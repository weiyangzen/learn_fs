# Research: subset-b-007660

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_changelog.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_changelog.c

## Purpose

`mdc_changelog.c` implements MDC-side delivery of Lustre MDT changelog records through per-MDT Linux character devices named from the connected MDT target. It bridges kernel llog changelog catalogs (`LLOG_CHANGELOG_REPL_CTXT`) to user space by opening the changelog catalog, prefetching records in a kernel thread, and exposing read, poll, seek, write-control, and ioctl operations on `/dev/changelog-*` devices. The file also manages global registration of changelog devices so multiple MDC OBDs or mount points that target the same MDT share one char device while preserving OBD references for teardown.

## Important APIs, Types, And Functions

Key state is split between `struct chlg_registered_dev` and `struct chlg_reader_state`. `chlg_registered_dev` owns the `cdev`, embedded `device`, global-list linkage, OBD list, and `kref` lifecycle for one target device. `chlg_reader_state` is per-open-file state: selected OBD, producer thread, error/EOF flags, start offset, wait queues, bounded record queue, llog cursor positions, ioctl flags, and user changelog filter mask. `struct chlg_rec_entry` stores one copied `struct changelog_rec` plus its variable name payload.

Public integration functions are `mdc_changelog_cdev_init()` and `mdc_changelog_cdev_finish()`, called from MDC setup/fini. They allocate or find a shared target device, allocate an IDR minor, initialize `device`/`cdev`, register file operations, link the OBD into `ced_obds`, and later remove that OBD and drop the device reference. The file exports global state declared in `mdc_internal.h`: `mdc_changelog_class`, `mdc_changelog_dev`, and `mdc_changelog_minor_idr`.

The main file operations are `chlg_open()`, `chlg_release()`, `chlg_read()`, `chlg_write()`, `chlg_llseek()`, `chlg_poll()`, and `chlg_ioctl()`. `chlg_ioctl()` handles `OBD_IOC_CHLG_POLL` flags and `OBD_IOC_CHANGELOG_FILTER`, the latter using `mdc_changelog_get_user_info()` to issue `MDS_GET_INFO` with `KEY_CHANGELOG_USER`.

## Control Flow

Open allocates `chlg_reader_state`, increments the registered-device kref, initializes queues and wait queues, and delays starting the producer. The first read or poll calls `chlg_start_thread()`, which spawns `chlg_load()`. The producer grabs a live OBD from the registered device list via `chlg_obd_get()`, opens and initializes the changelog catalog, and calls `llog_cat_process()` with `chlg_read_cat_process_cb()`. The callback validates `CHANGELOG_REC`, updates catalog/index cursors, skips old or masked records, waits while the local queue has `CDEV_CHLG_MAX_PREFETCH` entries, copies the variable-sized record, enqueues it under `crs_lock`, and wakes consumers.

Reads wait for queued records, EOF, or an error. They copy only whole records to user space, move consumed records to a temporary list, advance `crs_start_offset` to the next record index, wake the producer, free consumed entries, and update `file->f_pos`. Nonblocking reads return `-EAGAIN`, EOF, or a producer error when no record is queued. Seeking supports forward-only `SEEK_SET` and `SEEK_CUR` by updating `crs_start_offset` and discarding prefetched records below the new offset. Writes accept a compact control command, currently `clear:cl%u:%llu`, and send `KEY_CHANGELOG_CLEAR` through `obd_set_info_async()`.

If `CHANGELOG_FLAG_FOLLOW` is set, `chlg_load()` closes the current catalog, drops references, sleeps for one second, and reopens the catalog from the saved cursor until stopped. Release stops the thread, frees any queued records, and drops the registered-device reference.

## State And Persistence Behavior

Persistent changelog data lives on MDT llogs; this file does not persist records locally. It keeps only per-open cursors and a bounded in-memory queue. The reader offset is monotonic except initialization; backward seek is rejected. `chlg_clear()` persists progress for a changelog user by asking the MDT to clear records up to a supplied index. Registered-device state is global kernel state protected by `chlg_registered_dev_lock`; minor allocation is protected by `chlg_minor_lock` and the IDR.

Reference management is central: device lifetime uses `kref`, char-device release frees the allocated registered device and minor, OBD access is protected by `class_incref()`/`class_decref()`, and file release stops producer activity before freeing queue memory.

## Dependencies And Integration Points

The file depends on Linux char-device, device, IDR, kthread, poll, wait-queue, and copy-to/from-user APIs. Lustre dependencies include llog catalog APIs, `obd_set_info_async()`, changelog UAPI ioctls, `sptlrpc`/PTLRPC request capsules for `MDS_GET_INFO`, and MDC setup in `mdc_request.c`/`mdc_dev.c`. Naming integrates with Lustre OBD names using `get_target_name()` to convert an MDC OBD name into an MDT-level changelog device name.

## Risks

Concurrency risks center on global device teardown while files are open, producer blocking on a full queue, and OBD list mutation under the registered-device mutex. The code mostly mitigates these with krefs, OBD class refs, wait queues, and thread stop checks, but `mdc_changelog_cdev_finish()` assumes `chlg_registered_dev_find_by_obd()` returns a device and would dereference `NULL` if lifecycle accounting were violated. User record copying is whole-record only, so too-small buffers can make progress stall until a large enough read is issued. The filter mask uses `BIT(rec->cr.cr_type)`, so unexpected record type values would need to remain within the mask width.

## Test Signals

Useful tests are open/read/poll behavior on empty and populated changelogs, nonblocking reads, forward seek with prefetched records, follow mode across later records, `clear:clN:record` writes, filter ioctl behavior with server-provided masks, concurrent mounts sharing one target device, and teardown with open descriptors. Fault-injection signals include OBD disappearance while the producer runs, allocation failure for queued records, `copy_to_user()`/`copy_from_user()` failures, llog open/init/process errors, and minor exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_changelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_dev.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_dev.c

## Purpose

`mdc_dev.c` implements the CL/OSC-facing device, object, lock, IO, request-attribute, and device-type operations that let Metadata Client objects also serve Data-on-MDT file data. It reuses OSC infrastructure for pages, cache writeback, direct IO, fiemap, and common object handling, but maps locks and RPC metadata to MDT/FID semantics through LDLM IBITS locks carrying `MDS_INODELOCK_DOM`.

## Important APIs, Types, And Functions

The exported symbols used by other MDC files are `mdc_ldlm_blocking_ast()`, `mdc_ldlm_glimpse_ast()`, `mdc_fill_lvb()`, and the global `struct lu_device_type mdc_device_type`. The file defines CL operation tables: `mdc_lock_ops`, `mdc_lock_lockless_ops`, `mdc_io_ops`, `mdc_ops` (`cl_object_operations`), `mdc_object_ops` (`osc_object_operations`), `mdc_lu_obj_ops`, `mdc_lu_ops`, and `mdc_device_type_ops`.

Lock helpers include `mdc_lock_build_policy()` for DOM IBITS policy, `mdc_lock_build_einfo()` for LDLM enqueue callbacks, `mdc_dom_lock_match()` for local matching plus AST-data attachment and LVB caching, `mdc_dlmlock_at_pgoff()` for finding a whole-object DOM lock, `mdc_enqueue_send()` for synchronous/asynchronous LDLM enqueue, `mdc_enqueue_fini()` and `mdc_enqueue_interpret()` for reply completion, and `mdc_lock_upcall()`/`mdc_lock_granted()` for converting an LDLM result into an OSC lock state.

IO helpers include `mdc_io_setattr_start()` for truncate/fallocate against Data-on-MDT objects, `mdc_io_fsync_start()` for whole-object writeback and sync, `mdc_io_data_version_start()`/`end()` for asynchronous `MDS_GETATTR` data-version retrieval, and `mdc_io_read_ahead_prep()` for readahead under DOM locks. Object lifecycle helpers include `mdc_object_alloc()`, `mdc_object_init()`, `mdc_object_prune()`, `mdc_object_flush()`, and `mdc_object_fiemap()`.

## Control Flow

When a CL lock is initialized, `mdc_lock_init()` allocates an `osc_lock`, maps enqueue flags to LDLM flags, marks glimpse locks, builds LDLM enqueue info, attaches the MDC lock slice, optionally converts to lockless mode, and records reader/writer use based on IO type. `mdc_lock_enqueue()` rejects unsupported lockahead, handles test/glimpse shortcuts, waits for conflicting locks when needed, grants lockless locks locally, then builds a FID resource name and calls `mdc_enqueue_send()`.

`mdc_enqueue_send()` first tries local LDLM matching with `LDLM_FL_LVB_READY`, treating PR requests as PR|PW for sharing. If a valid lock is found and its AST data can be associated with the object, it invokes the upcall immediately. Otherwise it allocates an enqueue request, optionally cancels local DOM locks for write mode, handles old-server glimpse compatibility, requests an LVB, and calls `ldlm_cli_enqueue()`. Synchronous enqueues finish immediately through `mdc_enqueue_fini()`, while async enqueues store `osc_enqueue_args` and complete in `mdc_enqueue_interpret()`.

Blocking AST flow is handled by `mdc_ldlm_blocking_ast()`. A blocking callback sends async cancellation. A canceling callback creates an independent CL environment, calls `mdc_dlm_canceling()`, flushes or discards pages for the whole object, clears `l_ast_data`, and resets KMS to zero. LVB flow maps MDT `mdt_body` DOM size fields into `ost_lvb` with `mdc_fill_lvb()` for older servers, and `mdc_lock_lvb_update()` updates CL attributes and KMS once a lock is granted.

Device allocation creates an `osc_device`, binds the corresponding OBD found by name, and calls `mdc_setup()`. Device fini tears down procfs/PTLRPC/OSC precleanup, changelog cdevs, and llog context; final free asserts no modifying RPCs are in flight, finalizes CL, runs common OSC cleanup, and frees the `osc_device`.

## State And Persistence Behavior

Persistent metadata and Data-on-MDT data are remote; local state consists of LDLM locks, cached pages, OSC object attributes, LVB/KMS, and OBD/CL device structures. DOM locks are whole-object from the page-cache perspective. Losing a lock flushes dirty data for write mode, discards or selectively keeps clean pages depending on overlapping locks, clears AST data, and resets KMS so future reads refetch authoritative state. For truncate/fallocate, `mdc_io_setattr_start()` updates cached attributes when not lockless and sends an OSC-style punch/fallocate RPC using MDT object FID and a lock handle or server-lock flag.

## Dependencies And Integration Points

This file heavily depends on OSC CL infrastructure (`osc_lock`, `osc_object`, `osc_io`, page-gang lookup, cache writeback, punch/fallocate/fsync helpers), LDLM namespace and lock matching, PTLRPC request capsules, MDT/MDS opcodes, and CL environment APIs. It is the device-type implementation registered by `mdc_request.c` through `class_register_type(..., LUSTRE_MDC_NAME, &mdc_device_type)`. It also calls `mdc_setup()`, `mdc_changelog_cdev_finish()`, and `mdc_llog_finish()` for OBD-level lifecycle integration.

## Risks

The highest-risk areas are lock/cache coherence and lifecycle races. DOM locks use `l_ast_data` without owning object references in the DLM lock, so `mdc_object_prune()` must clear AST data before object destruction. Canceling locks may run during nested IO and therefore must use a fresh environment. Matched-lock paths must avoid associating one LDLM lock with the wrong OSC object; failed association drops the match. Data-version and setattr paths are asynchronous and rely on completion state in `osc_io`. Server-version compatibility for DOM LVBs and glimpse intents is another important compatibility risk.

## Test Signals

Coverage should include DOM read/write/truncate/fallocate/fsync/data-version/fiemap paths, lockless and locked IO, local lock match versus remote enqueue, glimpse on old and new servers, cancellation with dirty pages, object prune during active locks, KMS updates from LVB, and reconnect/teardown. Fault-injection hooks referenced in the file (`OBD_FAIL_MDC_GLIMPSE_DDOS`, `OBD_FAIL_LDLM_ENQUEUE_HANG`, `OBD_FAIL_OSC_CP_ENQ_RACE`, `OBD_FAIL_OSC_CP_CANCEL_RACE`) are direct test signals for race and error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_internal.h -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_internal.h

## Purpose

`mdc_internal.h` is the private interface for Lustre's Metadata Client implementation. It ties together request-packing helpers, lock/intents, reintegration operations, request/module setup, changelog char-device lifecycle, ACL unpacking, Data-on-MDT device hooks, and small inline helpers shared across `mdc_*.c` files.

## Important APIs, Types, And Functions

The header declares request packers implemented by `mdc_lib.c`: `mdc_pack_body()`, `mdc_swap_layouts_pack()`, `mdc_readdir_pack()`, `mdc_getattr_pack()`, `mdc_setattr_pack()`, `mdc_create_pack()`, `mdc_open_pack()`, security/encryption/SELinux packing helpers, unlink/link/rename/migrate packers, and `mdc_close_pack()`. These functions standardize how MDC fills `req_capsule` fields for MDS/MDT RPCs.

Lock and intent declarations include `mdc_set_lock_data()`, `mdc_null_inode()`, `mdc_intent_lock()`, `mdc_enqueue()`, `mdc_enqueue_async()`, `mdc_resource_cancel_unused_res()`, `mdc_resource_cancel_unused()`, `mdc_cancel_unused()`, `mdc_revalidate_lock()`, `mdc_intent_getattr_async()`, `mdc_batch_add()`, and `mdc_lock_match()`. Reint and request declarations include create/link/rename/setattr/unlink/file-resync operations, `mdc_fid_alloc()`, `mdc_setup()`, `mdc_llog_finish()`, open replay helpers, `mdc_save_lmm()`, `mdc_commit_open()`, and `mdc_replay_open()`.

Changelog declarations expose `MDC_CHANGELOG_DEV_COUNT`, `MDC_CHANGELOG_DEV_NAME`, `mdc_changelog_class`, `mdc_changelog_dev`, `mdc_changelog_minor_idr`, `mdc_changelog_cdev_init()`, and `mdc_changelog_cdev_finish()`. Data-on-MDT declarations expose `mdc_device_type`, LDLM AST callbacks, `mdc_fill_lvb()`, and `mdc_finish_enqueue()`.

Inline helpers are `mdc_prep_elc_req()` for early-lock-cancel request preparation, an ACL unpacking stub when POSIX ACLs are disabled, and `mdc_body2lvb()` for copying DOM size/time/block fields from `struct mdt_body` to `struct ost_lvb`. The header also defines default and maximum inline reply sizes for Data-on-MDT.

## Control Flow

The header itself has no runtime control flow, but it encodes cross-file layering. Request-building code flows from callers in `mdc_request.c`, `mdc_locks.c`, and `mdc_reint.c` into packers in `mdc_lib.c`. Lock and intent operations in `mdc_locks.c` call replay and request helpers from `mdc_request.c`, and Data-on-MDT device code in `mdc_dev.c` calls `mdc_finish_enqueue()` to share LDLM intent completion logic. Setup flows through `mdc_setup()` into llog/changelog/device initialization.

## State And Persistence Behavior

The header declares shared module-level changelog device state and the MDC LU device type, but does not define persistent storage. `mdc_body2lvb()` is stateful in the sense that it translates authoritative MDT reply body values into client lock value blocks used for cache coherence. The changelog device globals represent kernel registration state for all MDC changelog devices.

## Dependencies And Integration Points

The header includes `<lustre_mdc.h>` and assumes Lustre core types such as `struct req_capsule`, `struct md_op_data`, `struct ptlrpc_request`, `struct obd_export`, LDLM lock types, `struct lu_fid`, and `struct sptlrpc_sepol`. It is the internal ABI among MDC compilation units and connects MDC to LDLM, PTLRPC, OBD, LLOG, ACL, Data-on-MDT, and Linux device-class functionality.

## Risks

Because this header is the private contract, signature drift can silently break multiple source files. `mdc_prep_elc_req()` hardcodes `LUSTRE_MDS_VERSION` and MDS early-cancel behavior, so callers must use it only for compatible opcodes. `mdc_body2lvb()` asserts `OBD_MD_DOM_SIZE`, making missing DOM size data a hard failure in paths that expect it. Changelog minor count is tied to `LMV_MAX_STRIPE_COUNT`, so scaling or namespace changes must keep the user-visible char-device limit in mind.

## Test Signals

Build coverage is the primary signal for this file because it coordinates many prototypes. Runtime signals come indirectly from tests of metadata RPC packing, intent locking, reint operations, changelog char devices, ACL-enabled/disabled builds, and DOM LVB update paths. Configuration matrix tests should include `CONFIG_LUSTRE_FS_POSIX_ACL` on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_lib.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_lib.c

## Purpose

`mdc_lib.c` centralizes client-side packing of MDC request capsules for metadata RPCs. It translates Linux/VFS credentials, attributes, open flags, FIDs, names, security contexts, encryption contexts, SELinux policy data, layout payloads, close intents, and reint records into the wire structures consumed by MDT handlers.

## Important APIs, Types, And Functions

Generic body helpers are `__mdc_pack_body()` and `mdc_pack_body()`, which populate `struct mdt_body` with current credentials, capabilities, optional FID, EA size, flags, and project ID. `mdc_pack_name()` validates and copies single path components into request fields. Security helpers are `mdc_file_secctx_pack()`, `mdc_file_encctx_pack()`, and `mdc_file_sepol_pack()`.

Operation-specific packers include `mdc_readdir_pack()`, `mdc_create_pack()`, `mdc_open_pack()`, `mdc_setattr_pack()`, `mdc_unlink_pack()`, `mdc_link_pack()`, `mdc_rename_pack()`, `mdc_migrate_pack()`, `mdc_getattr_pack()`, `mdc_swap_layouts_pack()`, and `mdc_close_pack()`. Internal translators include `set_mrc_cr_flags()` for 64-bit create/open flags split into low/high wire fields, `mds_pack_open_flags()` for Linux open mode to MDS flags, `mdc_attr_pack()` for VFS `ia_valid`/extended validity to MDS setattr flags, `mdc_setattr_pack_rec()`, `mdc_ioepoch_pack()`, and `mdc_close_intent_pack()`.

## Control Flow

Most functions assume the caller has already selected a request format and set capsule field sizes. They fetch client-side fields with `req_capsule_client_get()`, fill fixed wire records, and copy optional variable payloads. Create/open packing writes `RMF_REC_REINT`, name, layout/default-LMV/symlink data, file security context, encryption context, and SELinux policy. Getattr packing writes `RMF_MDT_BODY`, optional name, FID pairs, cross-reference/namehash validity bits, and requested EA size. Readdir uses `mbo_size` and `mbo_nlink` as overloaded offset/size fields.

Setattr packing converts VFS attr flags, IDs, sizes, timestamps, blocks, project ID, and lazy-size/lazy-blocks indicators, then optionally copies or constructs LOV EA removal data. Close packing reuses setattr record packing, clears zero-atime updates to avoid old-server atime corruption, packs the open handle into `RMF_MDT_EPOCH`, and adds close-intent payloads for release, migration, layout split/swap, PCC attach, or resync completion.

## State And Persistence Behavior

This file does not retain state. Its outputs become persistent or replayable only after callers send requests and, where needed, save request buffers for replay. It uses current task credentials and capabilities at pack time, so packed records reflect the caller's security context. Project ID is written into the Lustre message when the project ID is valid and a PTLRPC request is present.

## Dependencies And Integration Points

Dependencies include Linux user namespace credential conversion, current umask/capability APIs, Lustre request capsules, MDT wire record definitions, LOV/LMV layout structures, security policy helpers, and CL object headers. It is used by `mdc_reint.c` for modifying metadata RPCs, `mdc_locks.c` for intent-open/create/getattr/getxattr/layout packing, and `mdc_request.c` for getattr, xattr, close, root, readdir, HSM, fsync, and ioctl-related requests.

## Risks

The main risks are mismatched capsule sizes, stale wire-format compatibility, and incorrect flag translation. Many functions rely on `LASSERT()` rather than recoverable errors for bad caller setup. `mdc_pack_name()` detects concurrent rename length mismatches but still copies the current string. `mdc_open_pack()` always includes `MDS_OPEN_DEFAULT_LMV`, so server-side interpretation must remain compatible. Close intent packing multiplexes several meanings through `struct close_data`; incorrect bias combinations would pack incompatible fields.

## Test Signals

Tests should validate wire records for create, mkdir with LMV, symlink/layout data, open with delayed create/PCC/default LMV, getattr by name/FID, setattr with mode/owner/size/lazy-size/project ID, xattr/security/encryption contexts, unlink/link/rename/migrate, close release/resync/swap/split/PCC, and readdir offset/size packing. Cross-version tests are important for atime clearing, flag high/low packing, and optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_locks.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_locks.c

## Purpose

`mdc_locks.c` implements MDC metadata LDLM lock acquisition, intent RPC packing/completion, lock revalidation, lock data association, replay-sensitive layout saving, and asynchronous intent/getattr or flock enqueue support. It is the bridge between high-level metadata operations (`lookup_intent`, `md_op_data`) and LDLM IBITS/FLOCK locking over MDT resources.

## Important APIs, Types, And Functions

Externally visible functions include `it_open_error()`, `mdc_set_lock_data()`, `mdc_lock_match()`, `mdc_cancel_unused()`, `mdc_null_inode()`, `mdc_save_lmm()`, `mdc_finish_enqueue()`, `mdc_enqueue()`, `mdc_enqueue_async()`, `mdc_revalidate_lock()`, `mdc_intent_lock()`, and `mdc_intent_getattr_async()`.

Internal request packers include `mdc_intent_open_pack()`, `mdc_intent_create_pack()`, `mdc_intent_getxattr_pack()`, `mdc_intent_getattr_pack()`, `mdc_intent_layout_pack()`, and `mdc_enqueue_pack()`. Shared orchestration is in `mdc_enqueue_base()`, with completion split between `mdc_finish_enqueue()` and `mdc_finish_intent_lock()`. Async helpers are `mdc_enqueue_async_interpret()` and `mdc_intent_getattr_async_interpret()`.

## Control Flow

`mdc_intent_lock()` first attempts local revalidation for sane child FIDs on lookup/getattr/readdir, allocates a new FID for create if needed, then delegates to `mdc_enqueue_base()`. `mdc_enqueue_base()` selects a lock policy from the intent: update for getattr/readdir/create, layout for layout intents, xattr for getxattr, lookup otherwise. It then packs the correct LDLM intent request, sets project ID and LDLM slot behavior, installs a DOM glimpse callback, and calls `ldlm_cli_enqueue()`.

Open/create packing performs early cancellation of conflicting parent update or child open/layout locks, obtains SELinux policy, marks replayable open requests, and reserves reply fields for MDT body, layout EA, ACL, security/encryption contexts, default LMV, and possible Data-on-MDT inline data. Getattr/getxattr/layout intents reserve only their required reply fields. When a server returns `-EINPROGRESS`, `mdc_enqueue_base()` retries while the import generation is unchanged; `-ERANGE` on old ACL buffers triggers a rebuild with maximum EA-size ACL capacity.

`mdc_finish_enqueue()` decodes LDLM reply disposition/status into the lookup intent, adjusts lock mode if the server granted a different mode, clears replay flags for failed/nonexecuted operations, extracts MDT body and layout data, saves layout EA into the request for replay when needed, installs layout LVB data on layout locks, and updates DOM LVBs for DOM locks. `mdc_finish_intent_lock()` converts disposition into VFS-visible references: it retains request refs for successful create/open phases, handles failed phases, and replaces duplicate locks with an existing matching one when possible.

## State And Persistence Behavior

Persistent state is remote MDT metadata; local state includes LDLM resources, inode association in `lr_lvb_inode`, `lookup_intent` disposition/status/lock handles, request replay flags, and saved EA buffers for recovery. `mdc_save_lmm()` can enlarge the request buffer and copy layout metadata so open/create/layout operations can be replayed correctly after recovery. Lock revalidation either validates an existing handle or searches the namespace for matching IBITS according to the intent.

## Dependencies And Integration Points

The file depends on LDLM locking, PTLRPC request capsules, Lustre intent/disposition definitions, MDC packers in `mdc_lib.c`, replay helpers in `mdc_request.c`, Data-on-MDT callbacks from `mdc_dev.c`, ACL sizing, SELinux policy helpers, and lprocfs counters. It is exported through `mdc_md_ops` in `mdc_request.c` as metadata enqueue, intent lock, async getattr, lock matching, and cancel-unused support.

## Risks

This is a high-risk concurrency and recovery file. Incorrect replay flag clearing could replay failed creates/opens or lose needed recovery data. ACL `-ERANGE` retry paths must free and rebuild requests without leaking locks. Infinite `-EINPROGRESS` retry depends on signal handling and import generation checks. Layout LVB installation allocates memory under completion flow and must avoid trusting blocked locks. `mdc_set_lock_data()` assumes any previous inode pointer is freeing when changed. Async completion must maintain lock references so failed lock cleanup and upcalls occur in a safe order.

## Test Signals

Important tests include lookup/getattr/open/create/readdir/getxattr/layout intents, local lock revalidation, duplicate lock replacement, open/create recovery replay, ACL large-reply retry, `-EINPROGRESS` retry and cross-eviction stop, DOM lock LVB update, layout lock LVB save/install, async flock enqueue, async getattr completion, and failure hooks such as `OBD_FAIL_MDC_GETATTR_ENQUEUE` and enqueue race failpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_reint.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_reint.c

## Purpose

`mdc_reint.c` implements MDC reintegration RPCs: metadata-modifying operations sent to MDTs through `MDS_REINT` or related reint formats. It covers setattr, create, unlink, link, rename/migrate, and file resync, plus shared early-lock-cancel helpers that gather local locks to cancel with a modifying request.

## Important APIs, Types, And Functions

The main public functions are `mdc_setattr()`, `mdc_create()`, `mdc_unlink()`, `mdc_link()`, `mdc_rename()`, `mdc_file_resync()`, `mdc_resource_cancel_unused_res()`, and `mdc_resource_cancel_unused()`. `mdc_reint()` is the shared synchronous send helper that sets the request import state, takes a modifying-RPC slot, queues the request, releases the slot, and validates that a successful reply contains `RMF_MDT_BODY`.

## Control Flow

Each operation computes a set of local LDLM locks to cancel early based on `md_op_data` flags and FIDs, allocates the operation-specific request format, sizes variable fields, optionally obtains SELinux policy data, prepares the request with `mdc_prep_elc_req()`, calls the corresponding packer from `mdc_lib.c`, sets reply sizes, and sends via `mdc_reint()`.

`mdc_setattr()` cancels update and sometimes lookup locks for the target FID, packs optional EA data and zero-length epoch/log-cookie fields, and treats `-ERESTARTSYS` as success after the RPC layer has handled recovery semantics. `mdc_create()` allocates a child FID if the caller did not, cancels parent update locks, packs name/EA/security/encryption data, and implements explicit retry for `-EINPROGRESS` by rebuilding the request as long as the import generation has not changed. Directory create replies with LMV EA are validated and saved into the request buffer for replay, then body LMV validity is cleared so initialization can be delayed to lookup.

`mdc_unlink()` cancels parent update locks and, for the child FID, either full inode locks or only ELC bits depending on dirty Data-on-MDT data. `mdc_link()` cancels update locks on source and parent. `mdc_rename()` cancels relevant source parent, target parent, source child lookup, and migration target ELC locks, selects migrate versus rename format, and routes BFL-capable renames to `MDS_IO_PORTAL` when supported. `mdc_file_resync()` packs `REINT_RESYNC`, optional mirror ID compatibility field, and a remote lease handle from the lease lock.

## State And Persistence Behavior

These operations mutate persistent MDT namespace, attributes, layout, and resync state. Locally, they consume modifying-RPC slots, may cancel local locks early, and return a held request pointer to callers for reply inspection and request lifecycle. Create can save reply LMV layout data for recovery replay. Resync includes lease-handle and mirror-ID state that affects persistent layout synchronization.

## Dependencies And Integration Points

The file depends on `mdc_lib.c` packers, LDLM resource cancellation, PTLRPC modifying-RPC slots, `mdc_fid_alloc()` from request setup, SELinux policy helpers, Lustre FID and request format definitions, and connection compatibility helpers such as `exp_connect_mirror_id_fix()`. It is wired into `mdc_md_ops` by `mdc_request.c`.

## Risks

The main risks are failure and retry semantics for modifying operations. Requests that return `-EINPROGRESS` must be rebuilt after dropping the old request, but only while the import generation is stable. Early lock cancellation must avoid canceling dirty DOM data incorrectly; unlink explicitly switches between full and ELC-only bits based on `CLI_DIRTY_DATA`. Several error paths allocate a request and policy object before packing, so leaks are possible if cleanup is missed. Rename portal selection is version/connection sensitive. `mdc_reint()` expects `RMF_MDT_BODY` on successful replies; format mismatches become `-EPROTO`.

## Test Signals

Tests should cover chmod/chown/truncate/setstripe setattr, create with caller-allocated and MDC-allocated FIDs, mkdir with LMV reply, create retry on `-EINPROGRESS`, unlink with dirty and clean DOM data, hard link, rename and migrate, resync with mirror ID compatibility, early-lock-cancel behavior with cancelset enabled/disabled, SELinux policy packing errors, and `-ERESTARTSYS` recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_reint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_request.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_request.c

## Purpose

`mdc_request.c` is the central MDC module implementation. It provides non-reint metadata RPCs, xattr operations, root and getattr lookup helpers, open/close replay management, directory page reads, statfs, HSM and quota ioctls, get_info/set_info dispatch, fsync/rmfid, import-event handling, FID allocation, llog setup, OBD/MD operation tables, changelog class allocation, and module init/exit.

## Important APIs, Types, And Functions

Major public or table-wired functions include `mdc_setup()`, `mdc_llog_finish()`, `mdc_fid_alloc()`, `mdc_set_open_replay_data()`, `mdc_replay_open()`, `mdc_commit_open()`, `mdc_save_lmm()` consumers, `mdc_create()`/reint functions through `mdc_md_ops`, and the `mdc_obd_ops`/`mdc_md_ops` tables. Internal functional areas include `mdc_get_root()`, `mdc_getattr()`/`mdc_getattr_name()`/`mdc_getattr_common()`, `mdc_xattr_common()` with `mdc_setxattr()`/`mdc_getxattr()`, `mdc_get_lustre_md()`, `mdc_close()`, directory read helpers (`mdc_getpage()`, `mdc_page_locate()`, `mdc_dirpage_add()`, `mdc_read_page()`), `mdc_statfs()`/async, ioctl helpers, `mdc_get_info()`/`mdc_set_info_async()`, `mdc_fsync()`, `mdc_rmfid()`, and `mdc_import_event()`.

## Control Flow

Startup runs `mdc_init()` as a late initcall: initializes libcfs, allocates the global changelog chrdev range, creates the changelog class, and registers the MDC OBD/MD type with `mdc_device_type`. Device setup later calls `mdc_setup()`, which runs common OSC setup, initializes tunables, sets Data-on-MDT defaults, registers cancel weighting and inode LVB ops, initializes changelog llog context, and registers the changelog char device.

Metadata reads use PTLRPC request capsules. `mdc_get_root()` sends `MDS_GET_ROOT`, optionally with a fileset, waits for a root FID, and checks subtree support after connect flags are known. `mdc_getattr()` and `mdc_getattr_name()` build getattrs, reserve layout/ACL/encryption fields, route plain getattr through the readpage portal to avoid modifying-RPC deadlocks, and retry with larger ACL buffers on `-ERANGE`. `mdc_xattr_common()` handles both `MDS_GETXATTR` and `MDS_REINT_SETXATTR`, packs names and values, sends SELinux policy data, and for modifying xattrs cancels local xattr locks early.

Open/close recovery is managed through `struct md_open_data`. Successful replayable opens get callback data and replay callbacks installed by `mdc_set_open_replay_data()`. `mdc_replay_open()` updates open handles in both live client handles and any already-built close request after a replay. `mdc_commit_open()` preserves committed open requests when needed for later close/eviction logic. `mdc_close()` selects close or close-intent format, may allocate volatile FIDs, packs lazy size/block updates if supported, fixes open replay state, sends through a modifying slot on the readpage portal, and handles committed-open `-ESTALE` as nonfatal.

Directory reads acquire a readdir intent lock, bind lock data to the inode, find a cached hash page, or issue `MDS_READPAGE` bulk RPCs. `mdc_getpage()` handles bulk sink setup, timeout resend with backoff, unwraps secure bulk data, and validates transferred bytes. Page helpers adapt LU page layout to native page size, add folios into the page cache by hash, and handle hash-collision edge cases.

Ioctl and info paths fan out to FID2PATH, HSM progress/state/request/copytool registration, quota, statfs, swap layouts, import recovery, active-state changes, and connection flags. HSM copytool messages are swabbed if needed and broadcast through kernelcomm; copytools are re-registered in a background thread on import active events. `mdc_import_event()` resets grants, flushes sequence clients, cleans LDLM/OSC state on invalidate, notifies observers, initializes grants/OCD-derived EA sizes, and triggers KUC re-registration after reconnect.

## State And Persistence Behavior

Persistent state lives on MDTs and llogs. Local MDC state includes import connection data, max/default MDS EA sizes, open replay records, close request references, directory page cache, LDLM namespace inode LVB pointers, changelog llog context, HSM copytool registrations, grant accounting, sequence client state, and global changelog chrdev registration. `mdc_get_info()`/`set_info_async()` also maintain local read-only flags and EA-size configuration. `mdc_rmfid()` submits batched FID removals asynchronously and copies per-FID result codes in its interpret callback.

## Dependencies And Integration Points

This file is the integration hub for Linux module/device APIs, PTLRPC, LDLM, OBD class operations, OSC common code, CL page cache helpers, Lustre llog, LMV/LOV metadata parsing, ACL/encryption/security contexts, quota, HSM kernelcomm, fid/seq allocation, and lprocfs. It registers the operation tables consumed by upper llite/LMV layers and delegates modifying namespace operations to `mdc_reint.c`, intent locking to `mdc_locks.c`, packing to `mdc_lib.c`, and device/DOM behavior to `mdc_dev.c`.

## Risks

The file has broad blast radius. Open/close replay uses multiple references and callbacks; incorrect ordering can leak requests, lose close handles, or replay stale creates. Directory hash page caching has explicit collision caveats. Bulk readdir resend must avoid infinite retry while preserving interruptibility. HSM ioctl paths copy user-derived variable data into request buffers and need size validation from upper layers. Import-event cleanup must coordinate LDLM namespace cleanup, OSC IO unplugging, grant reset, and observer notification. Module init error paths must unregister chrdev/class resources exactly once.

## Test Signals

High-value tests include root/fileset mount, getattr by FID/name with ACL `-ERANGE`, encrypted-file context fetch, getxattr/listxattr/setxattr edge cases, open replay through reconnect, close after committed open and `-ESTALE`, directory read cache and hash collision behavior, statfs old/new formats, FID2PATH partial `-EREMOTE`, HSM copytool registration/reregister/progress/state/request/data-version, quota iteration, swap layouts with early cancels, import event transitions, FID allocation after reconnect, module setup/fini, and changelog cdev integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/Makefile -->
# sources/distributed-fs/lustre-release/lustre/mdt/Makefile

## Purpose

This `Makefile` defines the Lustre Metadata Target (`mdt`) kernel module composition. It tells kbuild to build `mdt.o` as a module and lists the object files that make up the MDT implementation.

## Important APIs, Types, And Functions

There are no C APIs or runtime functions in this file. The important build variables are `obj-m += mdt.o`, which declares the module, and `mdt-objs`, which accumulates all object files linked into it. The object list includes handler, library, reintegration, xattr, recovery, open, identity, procfs, filesystem, size-on-MDS, LVB, HSM, MDS integration, IO, restripe, HSM coordinator/action/request/client/agent pieces, coordinator support, and batch support.

## Control Flow

Build control is linear kbuild variable evaluation. `mdt-objs` is initialized with core MDT objects and then extended over several lines with HSM and coordinator-related objects. If `CONFIG_GCOV_PROFILE_LUSTRE` is set, `GCOV_PROFILE := y` enables coverage instrumentation for the module.

## State And Persistence Behavior

The Makefile itself has no runtime state or persistence. It controls which source files become part of the MDT module binary. Changing the object list changes available runtime functionality and can introduce unresolved symbols or remove feature entry points.

## Dependencies And Integration Points

It integrates with the Linux kernel module build system and Lustre's build configuration. The object list is the build-time counterpart to source files under `lustre/mdt/`; those objects implement the server side that MDC client files in this subset talk to through MDS/MDT RPCs.

## Risks

The main risks are build omissions and instrumentation mismatch. Removing or misordering objects can break link-time symbol resolution or silently omit feature support. GCOV enablement depends on the `CONFIG_GCOV_PROFILE_LUSTRE` configuration and may affect build outputs and performance in test kernels.

## Test Signals

Signals are compile and link success for `mdt.o`, module load availability, and feature tests that exercise each listed component. Coverage builds should confirm `GCOV_PROFILE` is applied when `CONFIG_GCOV_PROFILE_LUSTRE` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/Makefile -->
