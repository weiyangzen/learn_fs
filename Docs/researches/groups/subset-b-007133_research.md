# subset-b-007133 Research

Work item: subset-b-007133

Scope: GlusterFS POSIX storage translator inode/fd operations, inode handle declarations, io_uring optional fast path, metadata xattr persistence, memory/message IDs, and translator registration.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-fd-ops.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-fd-ops.c

## Purpose

This is the main inode and file-descriptor operation implementation for the GlusterFS `storage/posix` translator. It maps Gluster fops onto backend POSIX syscalls, converts Gluster loc/fd/inode state into backend GFID handle paths or raw file descriptors, fills pre/post `struct iatt` results, manages xdata responses, performs cloudsync/object-state maintenance hooks, and updates the separate ctime metadata xattr when enabled.

The file covers stat/setattr, fallocate/discard/zerofill, open/read/write/copy_file_range, statfs, flush/release/fsync, xattr operations, access/truncate/fstat, lock/lease stubs, readdir/readdirp, rchecksum, and inode forget cleanup. Its behavior is central to brick-side correctness because it is the syscall boundary for most data and metadata operations.

## Important APIs, Types, and Functions

Important helpers include `MAKE_INODE_HANDLE`, `MAKE_REAL_PATH`, and `MAKE_HANDLE_PATH` from the handle layer, `posix_fd_ctx_get`, `posix_pstat`, `posix_fdstat`, `posix_xattr_fill`, `posix_cs_maintenance`, `posix_set_ctime`, `posix_update_utime_in_mdata`, and `posix_update_ctime_in_mdata`.

Top-level fops implemented here include `posix_stat`, `posix_setattr`, `posix_fsetattr`, `posix_glfallocate`, `posix_discard`, `posix_zerofill`, `posix_seek`, `posix_opendir`, `posix_readlink`, `posix_truncate`, `posix_open`, `posix_readv`, `posix_writev`, `posix_copy_file_range`, `posix_statfs`, `posix_flush`, `posix_fsync`, `posix_setxattr`, `posix_getxattr`, `posix_fgetxattr`, `posix_fsetxattr`, `posix_removexattr`, `posix_fremovexattr`, `posix_fsyncdir`, `posix_xattrop`, `posix_fxattrop`, `posix_access`, `posix_ftruncate`, `posix_fstat`, lock/lease stubs, `posix_readdir`, `posix_readdirp`, `posix_rchecksum`, and `posix_forget`.

Private state used from `struct posix_private` includes the export base path, creation masks, forced create/directory modes, O_DIRECT policy, disk reserve/full flags, shared-brick statfs scaling, batch fsync queues, ctime enablement, gfid2path and pgfid behavior, FIPS rchecksum behavior, and byte counters. FD state is stored in `struct posix_fd`, which can hold either a backend fd or `DIR *`, flags, EOF offsets, list linkage for janitor cleanup, and a back-reference for deferred close.

## Control Flow

Most fops follow a common flow:

1. Validate frame/translator/loc/fd/private arguments.
2. Optionally switch fsuid/fsgid to the caller identity using `SET_FS_ID`.
3. Resolve a `loc_t` through `MAKE_INODE_HANDLE` or obtain a `struct posix_fd` from fd context.
4. Collect pre-operation state with `posix_pstat` or `posix_fdstat` when required.
5. Apply disk-space, cloudsync, internal-write, or atomic-write guards.
6. Run the backend syscall.
7. Collect post-operation state and update ctime metadata according to `frame->root->flags`.
8. Fill xdata dictionaries when requested.
9. Restore fs identity and unwind with `STACK_UNWIND_STRICT`.

Path operations use GFID handles except for absolute directory locs that can be safely mapped to the export path. FD operations rely on the fd context established by `posix_open` or `posix_opendir`. Directory release and file release do not close immediately; they enqueue `posix_fd` objects onto `ctx->janitor_fds`.

Read/write control flow has additional branches. `posix_readv` allocates an aligned iobuf, optionally runs cloudsync maintenance, issues `sys_pread`, updates the read counter, returns an iovec/iobref, then fstats and uses `ENOENT` as the EOF signal. `posix_writev` runs disk-reserve checks, internal-write checks, optional `GLUSTERFS_WRITE_IS_APPEND` or `GLUSTERFS_WRITE_UPDATE_ATOMIC` locking, pre-stats, cloudsync maintenance, an O_DIRECT-aware write loop, response xdata fill for fd counts/append state, post-stat, ctime update, optional fsync, and ENOSPC overwrite retry checks.

Xattr control flow is broad. `posix_setxattr` filters immutable internal keys such as GFID and volume ID, handles legacy ctime metadata seeding via `CTIME_MDATA_XDATA_KEY`, has a cloudsync upload-complete path that stores remote object metadata and truncates the local file, delegates normal key setting through `posix_handle_pair`, optionally syncs backend custom xattrs, and returns pre/post iatt details and ACL xdata. `posix_getxattr` and `posix_fgetxattr` synthesize several virtual xattrs before falling back to `lgetxattr`/`fgetxattr` or list traversal. `posix_common_removexattr` enforces disallowed keys and supports bulk removexattr through a dictionary walk.

Directory reads use `posix_fill_readdir` under `fd->lock` to protect shared anonymous directory offsets. It filters hidden Gluster paths, can skip directories, handles `DT_UNKNOWN` with `fstatat`, tracks EOF offset, and returns `gf_dirent_t` entries. `posix_readdirp_fill` then resolves per-entry stats and xattrs. `GET_ANCESTRY_DENTRY_KEY` redirects `posix_readdirp` into ancestry reconstruction.

## State and Persistence Behavior

Persistent backend effects are direct syscalls on files, directories, and xattrs: chmod/chown/utimes/ftruncate/fallocate/punch-hole/zero-fill/write/copy/fsync and xattr set/remove. The file also updates Gluster-specific metadata xattrs through `posix_set_ctime` and related functions, handles cloudsync object xattrs, and maintains virtual responses for pathinfo, node UUID, GFID-to-path, ancestry, ACLs, object signatures, fd counts, and checksums.

In-memory state includes fd contexts, inode contexts for xattrop and atomic-write locks, fd cleanup queues, inode mdata context pointers, byte counters, directory EOF offsets, and unlink-deferred flags. `posix_release` and `posix_forget` both may remove a renamed/unlinked backend file when its inode context says delayed unlink is pending.

## Dependencies and Integration Points

This file depends heavily on Gluster core APIs: dictionaries, iobuf/iobref pools, inode/fd contexts, loc/inode tables, logging/message IDs, locks, xdata keys, stack unwind macros, and POSIX syscall wrappers from `glusterfs/syscall.h`. It integrates with the handle layer (`posix_handle_path`, `posix_istat`, `posix_pstat`), ctime metadata (`posix-metadata.c`), cloudsync helpers (`posix_cs_*`), ACL helpers (`posix_pacl_get` and POSIX ACL xattrs), gfid2path/pgfid ancestry helpers, disk reserve checks, DHT migration xdata, shard atomic write expectations, AFR/WORM timestamp behavior, and the janitor thread for released fds.

## Risks

The largest correctness risks are errno/sign handling, lock lifetime, and feature parity. Several helpers return negative errno while syscalls use `-1` with `errno`; mistakes can leak wrong errors to clients. Atomic-write and xattrop locks must always unlock on every error branch. Xattr filtering is security-sensitive because GFID, volume ID, gfid2path, mdata, ACL, cloudsync, and marker xattrs have special semantics. Disk-reserve overwrite retry logic must avoid admitting real space-growing writes when the brick is full. `copy_file_range` performs one syscall and explicitly notes that short copies may need follow-up handling. `posix_set_ctime_cfr` delegates two-inode timestamp behavior and should be checked for source/destination fd/inode argument correctness. Readdir offset behavior is subtle because heal code relies on next-entry offsets. O_DIRECT write fallback copies into aligned buffers but still relies on aligned sizes/offsets accepted by the kernel.

## Test Signals

Useful tests include stat/setattr/fsetattr pre/post iatt validation; chmod/chown/utimes on files, directories, and symlinks; O_DIRECT aligned and unaligned read/write; append and `GLUSTERFS_WRITE_UPDATE_ATOMIC` behavior under concurrent writers; ENOSPC overwrite retries; fallocate/discard/zerofill with and without kernel support; cloudsync object status/repair xdata; xattr list/get/set/remove including protected keys, bulk remove, ACLs, pathinfo, node UUID, gfid2path, ancestry, and object signatures; readdir/readdirp offset resumption and `GF_READDIR_SKIP_DIRS`; rchecksum in FIPS and non-FIPS modes; deferred unlink on release/forget; and lock/lease fallback behavior when higher lock translators are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-fd-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-handle.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-handle.h

## Purpose

This header declares POSIX inode-handle path construction and ancestry APIs used by the storage translator to resolve Gluster GFIDs to backend paths. It also defines macros that convert a Gluster `loc_t` into either an export-root-relative real path or a handle path under the brick's internal GFID handle hierarchy.

## Important APIs, Types, and Functions

Key constants are `TRASH_DIR`, `UUID0_STR`, `POSIX_ANCESTRY_PATH`, and `POSIX_ANCESTRY_DENTRY`. `LOC_HAS_ABSPATH` and `LOC_IS_DIR` classify locs. `MAKE_REAL_PATH` prefixes `POSIX_BASE_PATH(this)` unless the constructed path would exceed `POSIX_PATH_MAX(this)`, in which case it falls back to an alloca buffer containing the path without a leading slash. `MAKE_HANDLE_PATH` calls `posix_handle_path`. `MAKE_INODE_HANDLE` is the main macro used by fops: it validates translator private state and GFID, prefers the real absolute path for directory locs with absolute paths, otherwise calls `posix_istat` and builds a GFID handle path unless the inode resolution returned `ELOOP`.

Declared functions are `posix_handle_path`, `posix_make_ancestryfromgfid`, `posix_handle_init`, and `posix_handle_trash_init`.

## Control Flow

The header's macros inline control flow into call sites. Most fops declare `op_ret`, call `MAKE_INODE_HANDLE`, then check whether it set `op_ret` to `-1`. This means callers must use the expected local variable names and must treat `errno` from the macro as authoritative. Ancestry reconstruction walks from a GFID handle to parents and optionally fills a path or `gf_dirent_t` list.

## State and Persistence Behavior

The header itself persists nothing, but its APIs define how persistent handle directories and trash/landfill layout are initialized and addressed. The path macros allocate temporary stack buffers with `alloca`; call sites must not retain those pointers beyond the current stack frame.

## Dependencies and Integration Points

It depends on `limits.h`, `sys/types.h`, `gf-dirent.h`, `posix_handle_path`, `posix_istat`, `posix_pstat`, translator private path macros, GFID helpers, and message ID `P_MSG_INODE_HANDLE_CREATE`. It is consumed throughout lookup, inode, fd, xattr, metadata, and ancestry code.

## Risks

The macro style is fragile because it mutates caller variables such as `op_ret` and `errno`, assumes local names, and uses stack allocation sized from paths. Path-length fallback behavior deserves review because it strips a leading slash instead of failing, relying on later handle or syscall behavior. Null GFIDs, missing private state during fini, stale handles, and symlink `ELOOP` handling are the main failure cases.

## Test Signals

Exercise absolute directory locs, non-directory GFID handle resolution, null GFID rejection, path-length boundary behavior, stale GFID handles, symlink loop handling, handle initialization, trash initialization, and ancestry path/dentry reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.c

## Purpose

This file provides an optional liburing-backed fast path for `readv`, `writev`, and `fsync` in the POSIX translator. When built with `HAVE_LIBURING` and successfully initialized, `posix_io_uring_on` replaces the translator fop table entries with asynchronous implementations; `posix_io_uring_off` restores the synchronous implementations.

## Important APIs, Types, and Functions

`struct posix_uring_ctx` carries the Gluster call frame, fd reference, backend fd, xdata reference, pre-operation iatt, operation code, fop-specific read/write/fsync arguments, and function pointers for SQE preparation and completion unwind. `posix_io_uring_ctx_init` allocates and initializes this context and captures prebuf for write/fsync. Completion functions are `posix_io_uring_readv_complete`, `posix_io_uring_writev_complete`, and `posix_io_uring_fsync_complete`. SQE preparers are `posix_prep_readv`, `posix_prep_writev`, and `posix_prep_fsync`. Runtime functions include `posix_io_uring_submit`, `posix_io_uring_thread`, `posix_io_uring_init`, `posix_io_uring_drain`, `posix_io_uring_fini`, `posix_io_uring_on`, and `posix_io_uring_off`.

## Control Flow

The on path initializes an io_uring queue with `POSIX_URING_MAX_ENTRIES`, initializes submission/completion mutexes, starts a `posix-iouring` completion thread, then patches `this->fops->readv`, `writev`, and `fsync`.

Each async fop allocates a context, fills operation-specific fields, and submits an SQE under `priv->sq_mutex`. The completion thread waits for CQEs under `priv->cq_mutex`, extracts the context pointer, treats a null context plus exit flag as shutdown, marks the CQE seen, then calls the context's unwind callback. Completion callbacks translate negative CQE results to op_errno, collect post-operation `posix_fdstat`, update counters, fill response xdata for writes, unwind the original frame, and release context resources.

Shutdown sets `uring_thread_exit`, submits a drain NOP with null data, joins the thread, exits the queue, and destroys mutexes. Without liburing, `posix_io_uring_on` logs build-time unavailability and returns `-1`.

## State and Persistence Behavior

Persistent storage effects are the same kernel read/write/fsync operations, but completion ordering and error reporting are mediated by io_uring. In-memory state lives in `struct posix_private`: `ring`, `sq_mutex`, `cq_mutex`, `uring_thread`, `uring_thread_exit`, `io_uring_capable`, and `io_uring_init_done`. Contexts hold fd and xdata references until completion.

## Dependencies and Integration Points

The file depends on `posix.h`, `posix-messages.h`, `posix-io-uring.h`, `posix-handle.h`, liburing, fd contexts, iobuf pools, `posix_fdstat`, `_fill_writev_xdata` from the synchronous implementation, and Gluster stack unwind macros. It mutates the active translator fop table, so it integrates directly with `posix.c` registration and runtime option/reconfigure code.

## Risks

Parity with the synchronous paths is the main risk. The async read/write/fsync paths do not run all synchronous checks visible in `posix-inode-fd-ops.c`, such as disk reserve checks, cloudsync maintenance, internal-write checks, ctime metadata updates, O_DIRECT alignment handling, atomic write locking, and durable xdata handling. `posix_io_uring_submit` fails immediately if no SQE is available and has a TODO to retry. Write contexts store caller iovec pointers without retaining an `iobref`, so lifetime must be guaranteed by the stack above. `posix_io_uring_drain` does not take the SQ mutex. Completion thread aborts on unexpected `io_uring_wait_cqe` errors. Fsync completion increments `write_value` by the fsync result, which is typically zero.

## Test Signals

Test build without liburing, init failure fallback, runtime on/off fop table restoration, read/write/fsync success and error propagation, EOF signaling, xdata append/fd-count response on async writes, fd/xdata/iobuf reference lifetime under delayed completion, queue-full `EAGAIN`, shutdown with in-flight operations, and parity against synchronous behavior for cloudsync, ctime, O_DIRECT, atomic writes, and disk-reserve scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.h

## Purpose

This header declares the public switch points for enabling and disabling the POSIX io_uring backend and, when liburing is available, exposes the normal `posix_readv` and `posix_writev` symbols needed to restore synchronous fops.

## Important APIs, Types, and Functions

`POSIX_URING_MAX_ENTRIES` sets the queue depth to 512. `posix_io_uring_on(xlator_t *this)` attempts initialization and fop-table replacement. `posix_io_uring_off(xlator_t *this)` restores synchronous fops and tears down io_uring state when active. Under `HAVE_LIBURING`, the header also declares the synchronous `posix_readv` and `posix_writev` prototypes used by `posix_io_uring_off`.

## Control Flow

The header is consumed by translator initialization/reconfiguration logic. Runtime code calls `posix_io_uring_on` when the option is enabled and `posix_io_uring_off` when disabled or during cleanup.

## State and Persistence Behavior

The header persists nothing. Its constants and declarations gate runtime in-memory queue state created in `posix-io-uring.c`.

## Dependencies and Integration Points

It depends on Gluster types such as `xlator_t`, `call_frame_t`, `fd_t`, `dict_t`, `iobref`, and `struct iovec` through included translation-unit context. It integrates with `posix.c` fop registration and `posix_private` io_uring fields.

## Risks

The conditional prototypes mean compile coverage must include both liburing and non-liburing builds. Queue depth is fixed here, so workloads with high concurrency can hit SQE exhaustion unless the implementation grows retry/backpressure behavior.

## Test Signals

Compile with and without `HAVE_LIBURING`, verify fop restore uses synchronous symbols, and validate queue-depth behavior around 512 submitted operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-io-uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-mem-types.h

## Purpose

This header defines the POSIX translator memory accounting type IDs used with Gluster's `GF_MALLOC`, `GF_CALLOC`, and related allocation tracking.

## Important APIs, Types, and Functions

`enum gf_posix_mem_types_` starts at `gf_common_mt_end + 1` and includes allocation buckets for `posix_fd`, generic chars, `posix_private`, trash paths, POSIX AIO control blocks, inode contexts, mdata attributes, io_uring contexts, disk xlator structures, and the terminal `gf_posix_mt_end`.

## Control Flow

There is no runtime flow in this file. The enum is included by POSIX sources so allocations can be tagged for memory accounting and leak diagnostics.

## State and Persistence Behavior

No persistent state is written. The enum affects in-memory accounting and observability.

## Dependencies and Integration Points

It includes `glusterfs/mem-types.h` and must remain consistent with `mem_acct_init` in the translator. Allocation sites in the researched files use `gf_posix_mt_posix_fd`, `gf_posix_mt_char`, `gf_posix_mt_mdata_attr`, and `gf_posix_mt_uring_ctx`.

## Risks

IDs must not collide with common memory types and should not be reordered casually because memory accounting reports and downstream assumptions may depend on stable names. New POSIX allocation families need matching enum entries and mem accounting initialization.

## Test Signals

Build with memory accounting enabled, run POSIX translator allocation-heavy paths, and inspect stated allocation buckets for fd, xattr buffer, metadata, and io_uring context usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-messages.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-messages.h

## Purpose

This header declares the POSIX translator's stable GLFS message IDs. These IDs are used throughout the POSIX implementation for structured logging and must be appended, not removed or reused.

## Important APIs, Types, and Functions

The file invokes `GLFS_MSGID(POSIX, ...)` with a long list of identifiers covering xattr failures, GFID handling, fd/path operations, IO failures, aio/io_uring availability, allocation/fallocate/zerofill/copy_file_range, metadata xattr operations, locks/leases, disk-space checks, initialization and option errors, and many other POSIX translator events. The newest researched identifier in the list is `P_MSG_POSIX_IO_URING`.

## Control Flow

There is no executable flow. Compile-time macro expansion creates message IDs in the POSIX component namespace. Call sites pass these IDs to `gf_msg`, `gf_msg_debug`, or related logging macros.

## State and Persistence Behavior

No runtime state or persistent data is modified. The persistent contract is semantic: message IDs must remain stable across versions so logs and tooling remain interpretable.

## Dependencies and Integration Points

It includes `glusterfs/glfs-message-id.h` and is included by POSIX implementation files. It integrates with admin/debug workflows, automated log parsing, support tooling, and test assertions that may look for specific message IDs.

## Risks

Removing, reordering for reuse, or repurposing IDs can break log compatibility. Misusing IDs at call sites can make operational triage misleading, especially where errno is significant.

## Test Signals

Compile after adding IDs, run representative POSIX failure paths, and verify structured logs show POSIX component IDs with the expected symbolic meaning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata-disk.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata-disk.h

## Purpose

This header defines the on-disk wire/storage layout for the POSIX translator's `trusted.glusterfs.mdata` timestamp xattr.

## Important APIs, Types, and Functions

`gf_timespec_disk_t` stores `tv_sec` and `tv_nsec` as `uint64_t`. `posix_mdata_disk_t` is packed and contains a `uint8_t version`, `uint64_t flags`, and disk-format ctime, mtime, and atime fields. Comments state the version must be bumped when adding members.

## Control Flow

There is no control flow. Conversion functions in `posix-metadata.c` serialize and deserialize this structure with big-endian conversions.

## State and Persistence Behavior

This is a persistent format. It is stored as the value of `GF_XATTR_MDATA_KEY` on backend files and must remain machine-independent. Packing avoids compiler padding in the xattr payload.

## Dependencies and Integration Points

It depends on fixed-width integer types through the includer environment. It is included by `posix-metadata.h` and used by metadata fetch/store and legacy lookup healing code.

## Risks

Changing field order, size, signedness, packing, or endian handling can corrupt or misread existing metadata xattrs. The `uint64_t` representation of time should be reviewed for platforms where `time_t` semantics differ.

## Test Signals

Round-trip mdata xattrs across little-endian and big-endian assumptions, verify packed size, verify version handling, and test upgrades from files without mdata xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata-disk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.c

## Purpose

This file implements GlusterFS POSIX ctime/mtime/atime metadata persistence using the `GF_XATTR_MDATA_KEY` xattr. It maintains an in-memory `posix_mdata_t` per inode, stores a portable disk format, supports legacy file healing when ctime is enabled after files already exist, and updates timestamps according to flags carried by the call frame.

## Important APIs, Types, and Functions

Serialization helpers are `posix_mdata_to_disk`, `posix_mdata_from_disk`, and `posix_mdata_iatt_from_disk`. Disk access is handled by `posix_fetch_mdata_xattr` and `posix_store_mdata_xattr`. Cache/read APIs are `__posix_get_mdata_xattr` and `posix_get_mdata_xattr`. Legacy creation/update is handled by `posix_set_mdata_xattr_legacy_files`. The central writer is `posix_set_mdata_xattr`, called by public update helpers `posix_update_utime_in_mdata`, `posix_update_ctime_in_mdata`, `posix_set_ctime`, `posix_set_parent_ctime`, and `posix_set_ctime_cfr`.

`posix_mdata_flag_t` determines which of ctime/mtime/atime should be updated. `posix_get_mdata_flag` decodes direct inode flags such as `MDATA_CTIME`, `MDATA_MTIME`, and `MDATA_ATIME`; `posix_get_parent_mdata_flag` decodes parent timestamp flags.

## Control Flow

Reads first look in inode context slot 1. If absent, they allocate `posix_mdata_t`, fetch `GF_XATTR_MDATA_KEY` from an fd, real path, or GFID handle path, convert from disk endian format, and cache it in the inode context when an inode is available. If the xattr is absent but a caller supplied `stbuf`, the read path treats this as legacy/no-mdata and returns success without overriding backend timestamps.

Writes take the inode lock, obtain or allocate cached metadata, optionally fetch current disk metadata, initialize new metadata for newly-created ctime-enabled files, update only the requested timestamp fields, and store the disk xattr. Non-utime updates retain the highest observed time for each requested field to reduce distributed race regressions. Explicit utime updates may set atime/mtime to caller-provided earlier or later values, while ctime is still only advanced. The updated metadata is copied into `stbuf` when provided.

Legacy healing uses `posix_set_mdata_xattr_legacy_files`: it either reuses existing cached/fetched metadata or initializes from a `struct mdata_iatt` received through xdata, compares incoming times with existing ones, keeps the larger value for each field, then stores the xattr.

`posix_set_ctime_cfr` handles `copy_file_range` as a two-inode operation: destination should get ctime/mtime updates, source should get atime updates when requested.

## State and Persistence Behavior

Persistent state is the packed `posix_mdata_disk_t` value stored in the backend xattr. In-memory state is a `posix_mdata_t *` stored in the inode context and freed by `posix_forget`. The code supports path-based, fd-based, and handle-path-based access. It logs occasional warnings for missing xattr support and explicit errors for failed mdata fetch/store.

## Dependencies and Integration Points

The file depends on `posix.h`, `posix-metadata.h`, `posix-handle.h`, POSIX syscall wrappers, endian helpers, inode context APIs, inode locks, frame root timestamp flags, and message IDs. It is called from setattr, fsetattr, open/opendir, read/write/truncate/ftruncate/fallocate/zerofill/copy_file_range, xattr remove, readdirp stat fill, checksum, and parent-entry operations.

## Risks

The metadata path is race-sensitive. It uses inode locks, but different clients/bricks can race through xattr updates, so monotonic comparison is used except for explicit utime. Error handling intentionally tolerates absent xattrs for legacy files, which can hide backend problems if op_errno classification is wrong. The code stores metadata on every update, which can be expensive and can amplify xattr failures. `posix_set_ctime_cfr` should be reviewed closely because source and destination arguments are easy to mix. Conversion uses unsigned 64-bit fields and assumes timestamps fit that representation. Inode-context allocation ownership must remain paired with `posix_forget`.

## Test Signals

Test xattr round-trip, missing xattr support, absent legacy mdata, lookup-triggered legacy healing, concurrent timestamp updates choosing the highest non-utime times, explicit utime to older and newer values, frame flag combinations for file and parent updates, fd-based and path-based updates, copy_file_range source/destination timestamp behavior, brick restart losing inode context and refetching from disk, and memory cleanup on forget.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.h

## Purpose

This header declares the in-memory metadata representation and public APIs for POSIX ctime metadata xattr handling.

## Important APIs, Types, and Functions

`posix_mdata_t` contains flags, ctime, mtime, atime, version, and explicit padding. `posix_mdata_flag_t` contains bitfields for ctime/mtime/atime update selection. Public APIs include locked and unlocked mdata reads, utime and ctime update helpers, direct file and parent ctime setters, copy_file_range timestamp setter, legacy-file xattr seeding, and disk-to-`mdata_iatt` conversion.

## Control Flow

Callers choose locked `posix_get_mdata_xattr` when they do not already hold the inode lock and `__posix_get_mdata_xattr` when they do. Mutating fops call one of the setter helpers after the backend syscall and post-stat. Lookup/setxattr legacy paths call `posix_set_mdata_xattr_legacy_files`.

## State and Persistence Behavior

The header defines in-memory state mirrored to `posix_mdata_disk_t` from `posix-metadata-disk.h`. `posix_mdata_t` is held in inode context and persisted to `GF_XATTR_MDATA_KEY` by implementation functions.

## Dependencies and Integration Points

It includes `posix-metadata-disk.h` and depends on Gluster types `xlator_t`, `inode_t`, `call_frame_t`, `struct iatt`, and `struct mdata_iatt`. The declarations are consumed by POSIX inode/fd, entry, lookup, and metadata code.

## Risks

Bitfield layout is only used in memory but should remain simple. Padding implies ABI/alignment awareness. Callers must respect lock expectations or risk races and deadlocks.

## Test Signals

Compile all call sites, verify locked/unlocked read use, validate timestamp update flags from frame root flags, and run memory-check tests around inode forget cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.c

## Purpose

This file registers the POSIX storage translator with GlusterFS. It binds the translator's fop table, callback table, dumpops, options, lifecycle hooks, memory accounting hook, identifier, and maintenance category.

## Important APIs, Types, and Functions

`dumpops` exposes `posix_priv` and `posix_inode`. `fops` maps Gluster operations to POSIX implementations including lookup, namespace operations, inode/fd operations, xattrs, locking stubs, checksum, allocation, discard, zerofill, ipc, seek, lease, put, and copy_file_range. `cbks` maps release, releasedir, and forget callbacks. `xlator_api` registers `posix_init`, `posix_fini`, `posix_notify`, `posix_reconfigure`, `mem_acct_init`, `posix_options`, identifier `"posix"`, and category `GF_MAINTAINED`.

## Control Flow

At translator load time, Gluster reads `xlator_api`, calls init/mem accounting, and installs the fop/callback tables. Runtime fops are dispatched through the table. Optional runtime code, such as io_uring enablement, can later patch entries like readv/writev/fsync.

## State and Persistence Behavior

This file itself has no persistence. It controls which implementation functions are reachable by the Gluster stack and therefore determines the persistent effects of all POSIX operations.

## Dependencies and Integration Points

It depends on `posix.h` for function declarations and private option declarations. It integrates with every POSIX source file that defines one of the registered functions and with the Gluster translator loader.

## Risks

Missing or incorrect fop mappings can silently disable functionality or route a request to the wrong implementation. New fops added elsewhere must be wired here. Since io_uring can mutate fop pointers after registration, restore paths must match this table. Lock and lease entries intentionally return ENOSYS unless higher translators are loaded, so volume graphs must include the proper feature translators.

## Test Signals

Build/link tests catch missing symbols. Runtime translator smoke tests should verify each registered fop reaches the intended implementation, init/fini/reconfigure hooks run, dumpops work, and io_uring on/off restores readv/writev/fsync mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.c -->
