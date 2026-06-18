# Research: subset-b-007667

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_quota.c -->
# Research: sources/distributed-fs/lustre-release/lustre/osc/osc_quota.c

## Purpose
`osc_quota.c` implements the OSC-side quota signal cache and the OSC quotactl RPC path. It is not the quota authority. Instead, it records quota pressure returned by OST write replies and uses that cache to force subsequent I/O for affected quota IDs into synchronous/error-visible behavior. It also forwards quota control operations from the client-side OBD interface to the OST using PTLRPC capsules.

## Important APIs, Types, And Functions
The file exports `osc_quota_chkdq()`, `osc_quota_setdq()`, `osc_quota_setup()`, `osc_quota_cleanup()`, and `osc_quotactl()`. The main state is kept in `struct client_obd`: `cl_quota_exceeded_ids` is an xarray keyed by quota ID, storing a bitmask of quota types, `cl_quota_mutex` serializes cache updates, `cl_quota_last_xid` orders server reports, and `cl_root_squash` / `cl_root_prjquota` mirror OST flags.

`md_quota_flag()` maps `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA` to `OBD_MD_FL*QUOTA` valid bits. `fl_quota_flag()` maps the same quota types to `OBD_FL_NO_*QUOTA` flags in returned `obdo` state.

## Control Flow
`osc_quota_chkdq()` loops over `LL_MAXQUOTAS`, loads each caller-provided quota ID from the xarray, and returns `-EDQUOT` if the stored bitmask contains that quota type. Absence of an ID or absence of the relevant bit means the OSC can proceed without this local quota stop.

`osc_quota_setdq()` is called with the write reply XID, quota IDs, valid bits, and flags from the OST. It ignores replies without quota-valid bits and drops stale replies when a newer `cl_quota_last_xid` exists unless the server set `OBD_FL_NO_QUOTA_ALL`. Under `cl_quota_mutex`, it updates root squash flags, advances `cl_quota_last_xid`, then sets or clears per-type bits in `cl_quota_exceeded_ids`. A zero bitmask erases the xarray entry.

`osc_quotactl()` builds an `OST_QUOTACTL` request with `RQF_OST_QUOTACTL`, sizes the optional `RMF_OBD_QUOTA_ITER` server buffer only for `LUSTRE_Q_ITEROQUOTA`, copies the caller's `struct obd_quotactl` into the request, disables resend with `rq_no_resend`, waits synchronously, and copies back the server reply. Iteration replies allocate a `struct lquota_iter`, attach it to the caller-provided list pointer encoded in `qc_iter_list`, copy the iteration buffer, and zero returned iterator byte counts to indicate ownership transfer.

## State And Persistence
All state is volatile per-client memory. `osc_quota_setup()` initializes the mutex and xarray; `osc_quota_cleanup()` erases all xarray entries and destroys it. The xarray persists only for the OSC lifetime and is rebuilt from future OST replies after reconnect or remount. The file does not persist quota information to disk.

The XID ordering in `osc_quota_setdq()` is important because asynchronous OST replies can arrive out of order. The function still records some old negative quota reports to stay conservative, but it avoids allowing stale clears to remove a newer over-quota indication.

## Dependencies And Integration Points
The write-completion path in `osc_request.c` calls `osc_quota_setdq()` when an `OST_WRITE` reply carries quota valid bits. Higher-level OSC cache and write paths can call `osc_quota_chkdq()` before queuing work. `osc_quotactl()` depends on PTLRPC request allocation/packing, `req_capsule` field access, quota wire formats, and the `class_exp2cliimp()` import.

## Risks
The xarray key is only the numeric quota ID while the value encodes type bits. That is compact, but user/group/project IDs sharing the same integer share one xarray slot; bit handling must remain correct. `qc_iter_list` is passed through an integer field and cast back to a `struct list_head *`, so only trusted in-kernel callers should use that path. Stale reply handling is intentionally conservative, which can force synchronous behavior longer than strictly necessary after reordering.

## Test Signals
Useful tests are quota exhaustion and recovery cases covering user, group, and project quotas; out-of-order write reply simulation to verify stale clears do not remove newer over-quota state; `LUSTRE_Q_ITEROQUOTA` buffer handling; malformed or missing quotactl reply fields returning `-EPROTO`; and setup/cleanup leak checks for the xarray.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_request.c -->
# Research: sources/distributed-fs/lustre-release/lustre/osc/osc_request.c

## Purpose
`osc_request.c` is the main Lustre Object Storage Client request implementation. It translates OBD/OSC operations into OST PTLRPCs, manages asynchronous read/write BRW RPC construction and completion, integrates with LDLM locks, tracks OST grant accounting, handles checksums and encryption bounce pages, exposes statfs/getinfo/setinfo/iocontrol operations, and registers the OSC OBD type at module init.

## Important APIs, Types, And Functions
The file defines small async argument structures for setattr, fsync, ladvise, and BRW/grant use. Externally visible entry points include `osc_setattr_async()`, `osc_ladvise_base()`, `osc_punch_send()`, `osc_fallocate_base()`, `osc_sync_base()`, `osc_shrink_grant_to_target()`, `osc_schedule_grant_work()`, `osc_init_grant()`, `osc_build_rpc()`, `osc_send_empty_rpc()`, `osc_enqueue_base()`, `osc_match_base()`, `osc_set_info_async()`, `osc_reconnect()`, `osc_disconnect()`, `osc_ldlm_resource_invalidate()`, `osc_setup_common()`, `osc_setup()`, `osc_precleanup_common()`, and `osc_cleanup_common()`.

The central request helper is `osc_pack_req_body()`, which writes a wire `obdo` into `RMF_OST_BODY` and stores the project ID in the Lustre message. The central data path is `osc_build_rpc()` -> `osc_brw_prep_request()` -> PTLRPC send -> `brw_interpret()` -> `osc_brw_fini_request()`.

## Control Flow
Simple metadata/object operations allocate a PTLRPC request for a specific OST opcode, pack the request capsule, copy `obdo` fields, size the reply, send synchronously with `ptlrpc_queue_wait()` or asynchronously through a request set/`ptlrpcd`, and unpack `RMF_OST_BODY`. This pattern appears in getattr, setattr, create, punch, fallocate, sync, statfs, getinfo, and setinfo paths.

Destroy first gathers local LDLM locks for early cancellation with `osc_resource_get_unused()`, prepares an ELC destroy request, throttles the number of destroy RPCs through `cl_destroy_in_flight`, and sends it asynchronously. The destroy interpreter decrements the in-flight count and wakes waiters.

Grant flow is woven through all write and maintenance paths. `osc_announce_cached()` adds dirty/undirty/grant/lost-grant state to outgoing `obdo`s. `osc_update_grant()` consumes server returned grant. A delayed global work item walks `client_gtd.gtd_clients`, calls `osc_should_shrink_grant()`, and sends shrink requests in batches. `osc_init_grant()` initializes grant values from connect data and adjusts max pages per RPC to grant chunk alignment when `GRANT_PARAM` is negotiated.

For BRW RPCs, `osc_build_rpc()` receives a list of extents in `OES_RPC`, counts pages and grants, performs unaligned DIO copies, allocates the page pointer array and `obdo`, fills request attributes, sorts pages by object offset, calls `osc_brw_prep_request()`, attaches commit and interpret callbacks, moves pages and extents into async args, updates in-flight counters and histograms, and queues the request to `ptlrpcd`.

`osc_brw_prep_request()` chooses `OST_READ` or `OST_WRITE`, uses a request pool for writes when possible, handles encrypted writes by replacing plaintext folios with encrypted bounce folios, expands encrypted read ranges to encryption units, merges contiguous compatible pages into niobufs, chooses short I/O when small enough and supported, otherwise attaches a passive bulk descriptor, fills `obd_ioobj` and `niobuf_remote`, announces cached grant, optionally marks recovery resend and grant shrink, computes checksums for writes, requests checksums for reads, and stores all completion metadata in `osc_brw_async_args`.

`osc_brw_fini_request()` validates the OST reply, updates quota state from write replies, updates grant, unwraps protected bulk, verifies write checksums and per-niobuf return codes, copies short-read data, zero-fills short reads, verifies read checksums, decrypts encrypted read data when a key exists, and copies returned `obdo` attributes back to the caller's `obdo` on success. Recoverable checksum/security/server-progress errors return `-EAGAIN` or `-EINPROGRESS` for higher-level retry.

`brw_interpret()` restores bounce-page metadata, handles recoverable resend via `osc_brw_redo_request()`, updates object attributes and KMS/size on success, marks unstable write pages for sync, processes async writeback error state, finishes all extents, updates transferred counters and latency histograms, decrements in-flight counters, wakes cache waiters, and unplugs more OSC I/O.

LDLM integration starts by page-aligning extent policies. `osc_enqueue_base()` first tries to match an existing local lock; if none suffices, it packs and sends an LDLM enqueue, with async completion through `osc_enqueue_interpret()`. `osc_match_base()` performs local lock matching and updates cached LVB state. Import events clean grants, notify observers, invalidate LDLM resources and OSC objects, and initialize grant from OCD data.

## State And Persistence
Persistent storage updates are remote on OSTs; this file manages volatile client state. Important state includes request pool sizing (`osc_rq_pool`, `osc_pool_req_count`), in-flight read/write/direct counters, dirty/grant/reserved/lost-grant counters, async error forcing in `osc_async_rc`, delayed grant-shrink client lists, shrinker registration, lock AST data pointing to OSC objects, replayable PTLRPC request state, and request histograms.

The BRW path temporarily mutates `brw_page` offsets/counts for encryption-unit alignment and bounce folios. `osc_release_bounce_pages()` must restore those fields before completion propagates. Write persistence is observed through PTLRPC commit callbacks: `brw_commit()` decrements unstable pages when the server commits, or marks the request committed if the callback races before unstable accounting is set.

## Dependencies And Integration Points
This file is tightly coupled to PTLRPC (`ptlrpc_request_*`, `ptlrpcd_add_req()`, request sets, bulk descriptors), LDLM (`ldlm_*` lock matching/enqueue/cancel), CL/OSC object and extent layers (`cl_req_attr_set()`, `osc_extent_finish()`, `osc_io_unplug()`), quota code (`osc_quota_setdq()` and `osc_quotactl()`), llcrypt/Lustre encryption helpers, checksum helpers, lprocfs histograms, import recovery events, and kernel shrinker/debugfs/module registration.

The `osc_obd_ops` table is the public integration point for the OBD class. Module init allocates the shrinker, request pool, and grant work machinery before registering the `LUSTRE_OSC_NAME` type; exit reverses those resources.

## Risks
The BRW path has high concurrency and ownership complexity. Page arrays, extents, async args, request references, bounce pages, bulk descriptors, and unstable-page accounting must transfer exactly once across normal completion and resend. Error paths before queuing must finish extents and free `oa`/page arrays without touching request-owned resources. Checksum retry can mask transport corruption but can also create repeated resend pressure. Encrypted direct I/O temporarily edits folio mapping/index and depends on careful restoration.

Grant accounting is intentionally approximate under races, but underflow or stale lost-grant handling can affect write throttling. LDLM lock data attachment can fail if a matched lock already belongs to another OSC object. Import invalidation traverses namespace resources without taking references until it finds AST data, so callback and cleanup ordering are sensitive.

## Test Signals
Existing fail hooks named in the file are strong test anchors: `OBD_FAIL_OSC_BRW_PREP_REQ`, `OBD_FAIL_OSC_BRW_PREP_REQ2`, checksum send/receive corruption, `OBD_FAIL_OSC_MARK_COMPRESSED`, `OBD_FAIL_OSC_DELAY_IO`, LDLM enqueue/cancel race hooks, `OBD_FAIL_OSC_MATCH`, and `OBD_FAIL_OSC_SHUTDOWN`. Behavioral tests should cover short I/O reads/writes, encrypted buffered and direct I/O, checksum retry and dump behavior, grant shrink/reconnect, quota flag propagation, BRW resend after `-EINPROGRESS`, lock match/enqueue paths, statfs cache vs remote fetch, and setup/cleanup under connect/disconnect races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/osc_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/Makefile -->
# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/Makefile

## Purpose
This Makefile builds the Lustre `ptlrpc.o` kernel module. It composes the client/server PortalRPC core, security modules, llog networking, import/recovery machinery, network request scheduler pieces, LDLM object files, optional server target/nodemap code, optional GSS security subdirectory, and GCOV profiling flags.

## Important Build Variables
`obj-m += ptlrpc.o` declares the module. `ptlrpc_objs` lists core PTLRPC objects including `client.o`, `recover.o`, `connection.o`, `niobuf.o`, `pack_generic.o`, `service.o`, `pinger.o`, `import.o`, `ptlrpcd.o`, security implementations, NRS client pieces, `errno.o`, and `batch.o`.

`LDLM := ../ldlm/` and `TARGET := ../target/` are prefixes for imported object lists. The file includes `../ldlm/Makefile` unconditionally and `../target/Makefile` when `CONFIG_LUSTRE_FS_SERVER` is enabled. `nrs_server_objs` and `nodemap_objs` are appended only for server builds.

## Control Flow
The object list starts with always-built PTLRPC core files. It then imports LDLM objects through `$(patsubst %,$(LDLM)%,$(ldlm_objs))`, making LDLM part of the PTLRPC module link. In server configurations, it appends nodemap, server NRS, `pack_server.o`, `llog_server.o`, and target object files. `obj-$(CONFIG_LUSTRE_FS_GSS) += gss/` conditionally descends into the GSS security directory.

## State And Persistence
The Makefile does not maintain runtime state. Its effective state is build configuration: `CONFIG_LUSTRE_FS_SERVER`, `CONFIG_LUSTRE_FS_GSS`, and `CONFIG_GCOV_PROFILE_LUSTRE` change which objects and instrumentation are compiled. Because LDLM and optional target objects are folded into `ptlrpc.o`, symbol ownership and module init ordering are shaped by this file.

## Dependencies And Integration Points
This file integrates the PTLRPC directory with LDLM and target build fragments. `ccflags-y` adds include paths for `$(LUSTRE)/ldlm` and `$(LUSTRE)/target`, matching the cross-directory object linkage. Server builds depend on nodemap and target code being available and compatible with the PTLRPC module link.

## Risks
The unconditional LDLM include means errors or object list changes in the LDLM Makefile directly affect PTLRPC builds. Server conditional object additions can hide missing symbol problems until `CONFIG_LUSTRE_FS_SERVER` is enabled. Since `batch.o` is always included, client builds must compile its non-server fallback definitions correctly.

## Test Signals
Useful checks are client-only and server-enabled kernel builds, builds with `CONFIG_LUSTRE_FS_GSS`, builds with `CONFIG_GCOV_PROFILE_LUSTRE`, and link-time validation that imported LDLM/target object lists do not introduce duplicate objects or missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/batch.c -->
# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/batch.c

## Purpose
`batch.c` implements client-side batched metadata updates for Lustre. It groups multiple packed metadata update messages into one `MDS_BATCH` PTLRPC, sends the group inline or through a bulk transfer, dispatches per-subrequest callbacks from the batched reply, and can resend unfinished subrequests after server overflow.

## Important APIs, Types, And Functions
The public API is `cli_batch_create()`, `cli_batch_stop()`, `cli_batch_flush()`, and `cli_batch_add()`. Internally, `struct batch_update_head` tracks the export, owning `struct lu_batch`, update count, expected reply size, callback list, and update buffers. This file adds `struct batch_update_buffer` for allocated `batch_update_request` payloads, `struct batch_update_args` for PTLRPC async callback state, and `struct batch_work_resend` for deferred resend work.

Key helpers are `batch_prep_inline_update_req()`, `batch_prep_update_req()`, `batch_update_buffer_create()`, `batch_insert_update_callback()`, `batch_update_request_fini()`, `batch_update_interpret()`, `batch_send_update_req()`, `batch_update_request_add()`, and `cli_batch_resend_work()`.

## Control Flow
`cli_batch_create()` allocates a `cli_batch`, initializes flags and max count, and creates the first `batch_update_head` with a 4 KiB update buffer. `cli_batch_add()` creates a new head if the previous one was flushed, then calls `batch_update_request_add()`.

`batch_update_request_add()` repeatedly asks the caller-provided packer to encode an `md_op_item` into the current buffer. If the packer returns `-E2BIG`, it allocates a larger/new buffer sized from the packer's returned length and retries. On success it advances buffer offsets, increments request/update counts, accumulates reply size from `lm_repsize`, inserts the per-update callback, and auto-flushes if `lbt_max_count` is reached.

`batch_send_update_req()` converts the accumulated head into a PTLRPC request. `batch_prep_update_req()` chooses inline mode when there is one small buffer under `OUT_UPDATE_MAX_INLINE_SIZE`; otherwise it packs a header plus `but_update_buffer` descriptors and attaches a bulk descriptor with `ptlrpc_bulk_kiov_nopin_ops`. Non-read-only batches acquire a modification RPC slot. Synchronous batches call `ptlrpc_queue_wait()`, request-set batches add to the supplied set and check it, and default async batches go to `ptlrpcd`.

`batch_update_interpret()` releases the modification RPC slot, unpacks `RMF_BUT_REPLY`, validates `BUT_REPLY_MAGIC`, and calls `batch_update_request_fini()`. Finalization walks the callback list in request order, maps available embedded reply messages to callbacks, reports `-ECANCELED` for subrequests the server did not process, and schedules `cli_batch_resend_work()` when the enclosing RPC returned `-EOVERFLOW` and unfinished updates remain.

The resend worker creates a fresh head, copies or moves only unprocessed messages from the old buffers starting at `bwr_index`, splices callbacks to the new head, uses a conservative maximum reply size, sends the new request, and destroys the old head on success. On errors it finalizes both old and new heads with the error.

## State And Persistence
Batch state is transient and memory-resident. Buffers own packed subrequest bytes until the enclosing request completes or is resent. Callback objects carry caller data and interpreter functions and are freed after invocation. There is no disk persistence; durable effects are delegated to the MDS/MDT handlers that execute the embedded updates. Ordering is the insertion order in `buh_cb_list` and packed buffers.

## Dependencies And Integration Points
The file depends on PTLRPC request capsules, bulk descriptors, `ptlrpcd`, request sets, modification RPC slot accounting, Lustre message packing helpers, and batch wire structs such as `but_update_header`, `batch_update_request`, and `batch_update_reply`. It is paired with server-side batch handling in MDT/target code for `MDS_BATCH`. The Makefile builds `batch.o` into the PTLRPC module for both client and server-capable builds.

## Risks
The callback list and packed message stream must remain exactly aligned; any packer that reports an incorrect length or reply size can misroute subreply results. The overflow resend path transfers ownership of buffers and callbacks between heads, so cleanup ordering is delicate. In `batch_send_update_req()`, request-set handling calls `ptlrpc_check_set(env, bh->lbt_rqset)` and some callers pass `NULL` env elsewhere, so callback paths must tolerate the execution context used. Bulk buffer page counting is intentionally overestimated for partial first/last pages; changes there risk underallocating bulk fragments.

## Test Signals
Tests should cover inline vs bulk batch selection, read-only batches without modification slots, synchronous and asynchronous batches, request-set batches, packer `-E2BIG` growth, partial server replies, `-EOVERFLOW` resend from a nonzero subrequest index, callback return aggregation, and cleanup after allocation failures in buffer creation or resend work allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/batch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/client.c -->
# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/client.c

## Purpose
`client.c` implements the client-side PortalRPC core. It allocates and packs requests, manages bulk descriptors, assigns XIDs and bulk match bits, sends requests through imports, drives request-set state transitions, handles replies, timeouts, resends, adaptive timeouts, replay retention/commit cleanup, synchronous waits, and request reference/resource teardown.

## Important APIs, Types, And Functions
Major exported APIs include `ptlrpc_init_client()`, `ptlrpc_uuid_to_connection()`, `ptlrpc_prep_bulk_imp()`, `__ptlrpc_prep_bulk_page()`, `ptlrpc_free_bulk()`, `ptlrpc_at_set_req_timeout()`, `ptlrpc_at_get_net_latency()`, `ptlrpc_at_adj_net_latency()`, request cache/pool APIs, `ptlrpc_request_alloc()`, `ptlrpc_request_alloc_pool()`, `ptlrpc_request_alloc_pack()`, `ptlrpc_prep_set()`, `ptlrpc_set_add_req()`, `ptlrpc_check_set()`, `ptlrpc_set_wait()`, `ptlrpc_req_put()`, `ptlrpc_queue_wait()`, replay helpers, abort helpers, and XID helpers.

Important state lives in `struct ptlrpc_request`, `struct ptlrpc_request_set`, `struct obd_import`, `struct ptlrpc_bulk_desc`, and `struct ptlrpc_request_pool`. The file's static `request_cache` is the slab cache for requests, and `ptlrpc_last_xid` is the node-wide atomic XID counter.

## Control Flow
Request creation begins with `ptlrpc_request_alloc_internal()`, which allocates a request from the slab or optional pool, references the import, reconnects an idle import if needed, initializes a request capsule, and assigns the request format. `ptlrpc_request_pack()` obtains a security context, packs Lustre message buffers, initializes callbacks, portals, timeout, send state, opcode, and XID, and inserts the request into the import's unreplied list sorted by XID.

Bulk setup uses `ptlrpc_new_bulk()` to allocate a descriptor and bio_vec array, then `ptlrpc_prep_bulk_imp()` attaches it to a client request. `__ptlrpc_prep_bulk_page()` splits fragments across LNet MTU and `LNET_MAX_IOV` boundaries, growing `bd_md_count` and `bd_md_max_brw` as needed. `ptlrpc_free_bulk()` releases pool pages, import/export refs, fragment pins, and descriptor memory.

Request sets own caller references. `ptlrpc_set_add_req()` adds ordinary requests to `set_requests`, increments `set_remaining`, and sends immediately for producer sets. `ptlrpc_set_add_new_req()` queues ptlrpcd work on `set_new_requests` and wakes partner threads. `ptlrpc_queue_wait()` is the synchronous wrapper: allocate a set, add one referenced request, wait, destroy the set.

`ptlrpc_check_set()` is the main state machine. It sends NEW requests through `ptlrpc_send_new_req()`, delays requests when import recovery requires it, handles security-context waits, processes network errors/timeouts/resends, unregisters reply and bulk buffers, handles early replies and adaptive timeout updates, calls `after_reply()`, waits for bulk completion, moves to INTERPRET, invokes request interpreters, marks COMPLETE, removes requests from import sending/unreplied lists, decrements set/import counters, and produces more work for flow-controlled sets.

`after_reply()` unwraps and unpacks replies, handles truncated replies by resizing and resending when allowed, retries `-EINPROGRESS` unless disabled, records service statistics and adaptive timeout observations, validates reply type/status, triggers reconnect handling for recoverable errors, stores transnos, retains replayable requests, invokes commit callbacks for already committed requests, updates peer committed transno, and frees committed replay entries.

Timeout and resend logic is split across `ptlrpc_expire_one_request()`, `ptlrpc_expired_set()`, `ptlrpc_resend_req()`, and the resend branches in `ptlrpc_check_set()`. Expiration marks requests timed out, unregisters network buffers, optionally fails imports, and respects no-resend/recovery restrictions. Resends refresh security contexts, unregister old bulk, assign new match bits when appropriate, and call `ptl_send_rpc()` again.

Replay flow uses `ptlrpc_retain_replayable_request()` to keep transno-sorted replay requests, `ptlrpc_free_committed()` to prune replay and committed lists based on server committed transno/generation, and `ptlrpc_replay_req()` to reset a retained request for `LUSTRE_IMP_REPLAY` and queue it to ptlrpcd with `ptlrpc_replay_interpret()`.

## State And Persistence
The file manages volatile protocol state, but it is central to Lustre recovery semantics. Replay lists preserve enough request data in memory to replay committed-but-not-yet-confirmed operations after reconnect. XIDs are initialized from time or randomness and monotonically advanced in `PTLRPC_BULK_OPS_COUNT` increments so bulk match bits do not collide. Request phases (`NEW`, `RPC`, `BULK`, unregister phases, `INTERPRET`, `COMPLETE`) are the core lifecycle state.

Request buffers, reply buffers, security contexts, imports, bulk descriptors, request-set membership, unreplied/replay list entries, and pool ownership are all released in `__ptlrpc_free_req()` when the reference count reaches zero. Early reply buffers for large open RPCs can be freed before final request release to reduce memory pressure.

## Dependencies And Integration Points
`client.c` depends on LNet, Lustre import recovery, request capsules/layouts, SPTLRPC security, LDLM pool updates, lprocfs statistics, adaptive timeout helpers, ptlrpcd, and lower-level network send/unregister callbacks defined elsewhere. Higher layers such as OSC, MDC, MGC, LDLM, and batch code use these APIs for all client RPCs.

## Risks
This file is concurrency-sensitive. Request phase transitions depend on callback ordering from LNet and ptlrpcd. Returning a request to a pool before reply/bulk unlink completes can corrupt later users, which is why unregister phases are explicit. Replay list pruning must balance lock hold time against memory growth. XID/match-bit handling must remain collision-free across multi-bulk resends and old-server compatibility. Error paths in `ptlrpc_request_bufs_pack()` and request allocation must balance import references, security contexts, and pool ownership.

## Test Signals
Important tests include request allocation and pool fallback, bulk fragmentation at MTU and IOV boundaries, adaptive timeout/early reply behavior, import states NEW/CLOSED/INVALID/RECOVERY, no-resend vs resend timeouts, `-EINPROGRESS` retry, reply truncation resize, bulk failure after successful reply, replay retention and committed pruning, synchronous `ptlrpc_queue_wait()`, interruptible sets, flow-controlled producer sets, security context refresh waits, and fail hooks for long reply/bulk/request unlink and rounded XIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/connection.c -->
# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/connection.c

## Purpose
`connection.c` manages PTLRPC client connection objects keyed by LNet process identity and maintains per-CPU latency QoS requests used by PTLRPC. It provides connection lookup/creation/reference helpers and module-level initialization/finalization for the connection hash and CPU latency structures.

## Important APIs, Types, And Functions
The global connection table is `conn_hash`, an rhashtable keyed by `struct lnet_processid`. `cpus_latency_qos` is a per-CPU array of `struct cpu_latency_qos`. Public functions are `ptlrpc_connection_get()`, `ptlrpc_connection_addref()`, `ptlrpc_connection_init()`, and `ptlrpc_connection_fini()`.

`lnet_process_id_hash()` and `lnet_process_id_cmp()` avoid raw byte hashing because `struct lnet_processid` may contain unassigned bytes. `conn_hash_params` supplies key/head offsets plus custom hash and compare callbacks.

## Control Flow
`ptlrpc_connection_get()` normalizes the peer NID to its primary NID, looks up an existing connection, and increments its refcount if found. On miss, it allocates a new `struct ptlrpc_connection`, initializes peer and refcount, then inserts it with `rhashtable_lookup_get_insert_fast()`. If another thread inserted the same peer concurrently, the new allocation is freed and the existing object is referenced. Transient rhashtable resize errors `-ENOMEM` or `-EBUSY` sleep briefly and retry.

`ptlrpc_connection_addref()` atomically increments the refcount and returns the same object. `conn_exit()` is the rhashtable destroy callback and asserts that every remaining connection has zero references before freeing it.

`ptlrpc_connection_init()` allocates `cpus_latency_qos` for `nr_cpu_ids`, initializes each delayed work item, mutex, and default max time, then initializes `conn_hash`. `cpu_latency_work()` fires when a per-CPU QoS request deadline expires, clears the active request under the per-CPU mutex, and removes/frees the PM QoS request outside the lock. If the deadline has not arrived, it reschedules itself for the remaining jiffies.

`ptlrpc_connection_fini()` removes any active per-CPU PM QoS requests, cancels their delayed work, frees the per-CPU array, and destroys the connection hash with `conn_exit()`.

## State And Persistence
Connection state is volatile. Each connection stores peer process identity and an atomic refcount. The rhashtable provides process-wide sharing so imports to the same peer reuse a connection object. CPU latency QoS state is per CPU and includes a mutex, delayed work, active `dev_pm_qos_request`, deadline, and max timeout. No state is persisted across module unload.

## Dependencies And Integration Points
The file depends on Linux rhashtable, device PM QoS, LNet NID helpers, Lustre allocation/debug helpers, and `ptlrpc_internal.h`. `ptlrpc_uuid_to_connection()` in `client.c` resolves UUIDs to LNet peer/self IDs and calls `ptlrpc_connection_get()`. Import code holds and releases connection references around RPC communication.

## Risks
The CPU index calculation in `cpu_latency_work()` depends on pointer arithmetic over the allocated per-CPU array and must match the allocation type. Connection finalization asserts zero refs; leaked import references will trip `LASSERTF`. The insert path must tolerate rhashtable resizing and duplicate insertion races; unexpected errors currently cause the allocation to be freed and `NULL` returned.

## Test Signals
Tests should cover concurrent connection creation for the same peer, lookup after primary NID normalization, module init/fini with and without successful QoS allocation, active PM QoS cleanup on fini, rhashtable resize retry behavior, and leak detection by ensuring all connection references are dropped before `ptlrpc_connection_fini()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/connection.c -->
