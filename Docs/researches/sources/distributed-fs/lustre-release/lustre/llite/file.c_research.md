<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/file.c -->
# sources/distributed-fs/lustre-release/lustre/llite/file.c

## Purpose

`file.c` is the main Lustre llite VFS file-operation bridge. It connects Linux `struct file_operations` and `struct inode_operations` to Lustre metadata RPCs, CLIO data I/O, layout-lock management, HSM/PCC/FLR features, distributed flocking, group locks, FIEMAP, fallocate, project quota flags, and attribute refresh.

The file is also the coordination point for per-open client state. `struct ll_file_data` instances stored in `file->private_data` track open mode, cached MDS open handles, lease handles, group locks, readahead state, PCC state, designated FLR mirror, write-failure reporting, and lock-no-expand behavior.

## Important APIs, Types, And Functions

- `ll_file_open()` / `ll_file_release()`: VFS open and close handlers. They allocate/free `ll_file_data`, reuse or acquire MDS open handles, authorize statahead for directories, initialize encryption/PCC state, track open frequency, and close handles with `md_close`.
- `ll_prepare_close()` / `ll_close_inode_openhandle()` / `ll_md_close()` / `ll_md_real_close()`: close packing and open-handle lifecycle. Close can carry ordinary attributes or close-intent biases for layout split/merge/swap, HSM release, resync completion, and PCC attach.
- `ll_dom_finish_open()` and `ll_dir_finish_open()`: populate page or directory caches from inline data returned by open/read-on-open replies.
- `ll_merge_attr()` / `ll_merge_attr_try()` / `ll_merge_attr_nolock()`: merge MDT inode timestamps with OST object attributes, including encrypted-file lazy cleartext-size handling.
- `ll_io_init()` and `ll_file_io_generic()`: initialize and execute CLIO read/write operations, including direct I/O, parallel DIO, AIO, append, FLR mirror selection, range locks, no-lock mode, retry, and partial-I/O splitting.
- `ll_do_fast_read()` and `ll_do_tiny_write()`: fast paths that use existing page-cache state for small reads or already-dirty single-page writes.
- `ll_file_read_iter()` / `ll_file_write_iter()`: VFS iter I/O entry points, with PCC interception, hybrid buffered-to-DIO switching, unaligned-DIO segment looping, stats, and heat tracking.
- `ll_lov_setstripe_ea_info()`, `ll_lov_getstripe_ea_info()`, `ll_lov_setstripe()`, `ll_file_getstripe()`: set/get LOV layout and stripe extended attributes, including composite, DoM, foreign, encrypted, and erasure-coding checks.
- `ll_get_grouplock()` / `ll_put_grouplock()`: user-visible group-lock ioctls, layered over `cl_get_grouplock()` and serialized by inode group state.
- `ll_lease_open()`, `ll_file_set_lease()`, `ll_file_unlock_lease()`, `ll_lease_close_intent()`: lease acquisition/release and lease-backed layout/HSM/PCC operations.
- `ll_data_version()` / `ll_ioc_data_version()`: CLIO data-version queries used by userspace ioctls, HSM release, migration, layout swap, and resync.
- `ll_hsm_release()`, `ll_hsm_state_set()`, `ll_hsm_import()`, `ll_layout_restore()`: HSM release/import/state/restore handling.
- `ll_file_ioctl()`: large ioctl dispatcher for flags, stripe/layout, group locks, data versions, HSM, leases, ladvise, heat, PCC, project quota, and fallback OBD ioctls.
- `ll_file_flock()`: distributed POSIX/flock lock path via MDT LDLM flock enqueues, including asynchronous lock-manager callbacks.
- `ll_getattr_dentry()` / `ll_getattr()` / `ll_inode_permission()`: stat and permission hooks with statahead, revalidation, glimpse, striped-directory attr merging, foreign-symlink stat mode, root squash, and 32-bit inode encoding.
- `ll_layout_refresh()`, `ll_layout_conf()`, `ll_layout_lock_set()`, `ll_layout_intent()`, `ll_layout_write_intent()`: layout-lock fetch, application, generation tracking, retry, and write-intent signaling.

Key local helper structs include `split_param`, `pcc_param`, `swap_layouts_param`, and `ll_swap_stack`, all used to marshal biased close or layout-swap arguments.

## Control Flow

Open starts with intent state left by lookup/atomic-open when available. If no valid open intent is present, `ll_file_open()` synthesizes one from kernel flags, requests open-by-FID, optionally asks for an open lock when open-cache thresholds are exceeded, and retries after `ll_intent_file_open()` returns an MDS open result. Per-inode read/write/exec open handles are cached under `lli_och_mutex`; additional opens increment the matching usecount and get local `ll_file_data` without another close RPC. On errors, intent references and open handles are released carefully because close errors are rarely retried by applications.

Close reverses that state. `ll_file_release()` cleans up directory statahead, HSM copytool registration, PCC state, async write errors, and then calls `ll_md_close()`. `ll_md_close()` releases group locks and leases, consumes file-owned handles, decrements cached open-handle usecounts, and skips an MDS close only when a compatible cached OPEN lock remains. All close-intent variants eventually flow through `ll_close_inode_openhandle()`, which packs inode attributes, lazy size/block validity, data-modified HSM hints, lease handles, data versions, secondary FIDs, and operation-specific payloads before `md_close()`.

Read and write operations first offer the request to PCC. Reads then try fast page-cache reads before allocating a CL environment. Writes may switch to direct I/O by policy and may satisfy small dirty single-page writes through `ll_do_tiny_write()`. The generic CLIO loop initializes `CIT_READ` or `CIT_WRITE`, takes range locks for writes and direct reads unless a group lock is held, submits `cl_io_loop()`, waits/recycles synchronous DIO anchors, records bytes, handles partial I/O, and restarts for layout, mirror, or lock changes up to `RETRY_ATTEMPTS`.

Metadata operations are split between MDT and OST/CL layers. `ll_inode_revalidate()` fetches current metadata through an intent lock. `ll_getattr_dentry()` decides whether a glimpse is needed for size/blocks/mtime, lets PCC answer cached attrs, skips glimpse when MDT attributes are known authoritative, and otherwise calls `ll_glimpse_size()`. Non-regular and striped-directory attributes are merged by MDT directory stripe helpers.

Layout operations use LDLM layout locks. `ll_layout_refresh()` first checks cached layout generation, then under `lli_layout_mutex` either matches a local layout lock or sends an `IT_LAYOUT` intent. `ll_layout_lock_set()` fetches the layout LVB if absent, calls `ll_layout_conf()` to apply it to the CL object, waits/prunes on `-EBUSY`, and updates the inode layout generation when successful.

The ioctl dispatcher validates userspace buffers and privilege rules, then fans out to layout, lease, HSM, heat, PCC, project, flock, data-version, and fallback OBD control paths. Several ioctls intentionally reuse close-intent or lease paths so that metadata-server state transitions happen atomically with open-handle closure.

## State And Persistence Behavior

Most state is in memory: cached MDS open handles in `ll_inode_info`, per-file `ll_file_data`, CL object/layout state, LDLM locks, PCC attachment state, range-lock trees, heat counters, async write errors, and inode timestamps/blocks/size. Close RPCs persist file attributes, layout/HSM/PCC transitions, and data-modified flags back to the MDT. OST object state is changed through CLIO setattr/fallocate/fsync/data-version operations.

File size and block counts are deliberately lazy in several paths. `ll_prepare_close()` sends `OP_XVALID_LAZYSIZE`/`OP_XVALID_LAZYBLOCKS` when size/blocks are not authoritative. Encrypted files without keys report rounded sizes to userspace while preserving cleartext size in `lli_lazysize` for close. `AT_STATX_DONT_SYNC` can return lazy size/block fields without glimpse.

Layout state is persistent on the server but cached in the client via layout locks and CL object config. The client records `ll_layout_version` and refreshes it under layout-lock control. HSM state, archive IDs, data versions, and release/restore/import operations are persisted through MDT ioctls and biased close requests. Sessionless per-open flags such as no-lock, group-lock-held, lock-no-expand, and designated mirror are not persistent.

## Dependencies And Integration Points

`file.c` depends on llite internals, VVP/CLIO (`cl_io`, `cl_object`, `cl_lock`, `cl_page`), MDC/MDT metadata RPC helpers, LOV/LMV layout formats, LDLM locking, Linux VFS file/inode/stat/file-lock APIs, page cache helpers, encryption helpers, PCC hooks, HSM ioctl structures, Lustre OBD ioctl plumbing, and lprocfs stats.

Important cross-file integration includes `glimpse.c` for `ll_glimpse_size()` behavior, `lcommon_cl.c` for CL object initialization and OST setattr, `lcommon_misc.c` for group lock and OSC connect-flag update helpers, `llite_foreign.c`/`llite_foreign_symlink.c` for foreign fake symlink getattr mode and open/removal policy, and broader llite modules for directory, xattr, ACL, mmap, statahead, PCC, HSM, and layout callbacks.

## Risks And Edge Cases

- Open-handle caching is concurrency-sensitive. `lli_och_mutex`, per-mode usecounts, lease stealing, and error cleanup need to remain balanced or handles can leak, double-close, or skip required MDT close.
- Close errors are hard to recover from because VFS callers rarely retry `close()`. The implementation prioritizes local cleanup even when the close RPC fails.
- The generic I/O loop has many restart conditions: layout changes, FLR mirror retries, partial buffered I/O chunking, DIO/AIO completion, and append size refresh. Iterator state and range-lock release are high-risk areas.
- Hybrid I/O mutates `ki_flags` to direct I/O for large buffered requests. Pipe iterators, PCC attach, unaligned DIO, and older-server compatibility all have special handling.
- Attribute reporting is intentionally not strict POSIX atime behavior; Lustre avoids MDT RPCs on every read.
- Encrypted files without keys require rounded visible sizes and special close/getattr/seek/fiemap behavior.
- Foreign fake symlinks are regular files or directories presented as symlinks; callers must pass the `foreign` flag to `ll_getattr_dentry()` to avoid normal size/layout validation and to expose `S_IFLNK`.
- Several ioctl paths trust complex userspace structures after manual size checks. `LL_IOC_LADVISE`, lease unlock payloads, and FID2PATH variable buffers deserve fuzz coverage.
- Distributed flocking mixes kernel local locks and MDT LDLM locks. Async `lm_grant` callbacks, cancel races, and lockd owner comparison workarounds are subtle.
- Layout lock application can fail with `-EBUSY` while I/O is using the object; the prune/retry path must avoid stale layouts and deadlocks.

## Test Signals

Useful tests include open-cache reuse and close under read/write/exec modes; open-by-FID stale dentry retry; close-intent paths for HSM release, PCC attach, layout split/merge/swap, and resync done; encrypted open/getattr/close/seek behavior with and without keys; DoM read-on-open cache population; directory read-on-open cache population; fast-read fallback; tiny-write fallback; hybrid I/O switching thresholds; direct and unaligned vectored I/O; AIO/parallel-DIO completion; group-lock serialization and nonblocking behavior; lease set/get/unlock and broken-lease return modes; ladvise lockahead result mapping; stripe set/get including composite/DoM/foreign/EC layouts; FID2PATH for OST and encrypted names; fsync/flush async error propagation; flock sync/async/cancel paths; root-squash permission behavior; fallocate error mapping; layout refresh under revoked/blocked layout locks; and statx with `AT_STATX_DONT_SYNC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/file.c -->
