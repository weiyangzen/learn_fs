# subset-b-007862 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.c

## Purpose
`pvfs2-bufmap.c` implements the OrangeFS/PVFS2 shared-memory buffer map used to move file I/O data between VFS callers in the kernel and the user-space `pvfs2-client-core` daemon. The daemon passes a page-aligned userspace region through `PVFS_DEV_MAP`; this file pins those pages, slices them into descriptors, hands descriptor indices to file and directory paths, and provides copy helpers between mapped pages, user iovecs, kernel buffers, and page-cache pages.

## Important APIs, types, and functions
The public API exported through `pvfs2-bufmap.h` includes `pvfs_bufmap_initialize`, `pvfs_bufmap_finalize`, `pvfs_bufmap_get`, `pvfs_bufmap_put`, `readdir_index_get`, `readdir_index_put`, descriptor size queries, and the copy helpers. `struct slot_args` is a local adapter that lets normal I/O descriptors and fixed readdir descriptor indices use the same wait-and-claim logic. Global state includes descriptor sizing, `bufmap_init`, `bufmap_page_array`, `buffer_index_array`, `readdir_index_array`, `desc_array`, and wait queues for initialization and slot availability.

## Control flow
Initialization validates alignment, total size, descriptor size, and descriptor count from `struct PVFS_dev_map_desc`, allocates descriptor tracking arrays, pins user pages with `get_user_pages`, marks or flushes each page as needed, constructs `desc_array`, clears all descriptor usage bits, sets `bufmap_init`, and wakes callers blocked on `pvfs2_bufmap_init_waitq`. Finalization reverses this by clearing reserved status, releasing pinned pages, freeing arrays, and dropping `bufmap_init`.

`pvfs_bufmap_get` and `readdir_index_get` both call `wait_for_a_slot`. That function holds a read lock on `bufmap_init_sem`, scans the relevant slot bitmap under a spinlock, sleeps on an exclusive waitqueue entry when full, times out based on `slot_timeout_secs`, and returns `-EINTR` on signal. The copy helpers take the init read semaphore, then kmap one page at a time so highmem systems do not require permanently mapped pages.

## State and persistence behavior
All state is in-memory kernel module state tied to a live daemon mapping. There is no disk persistence. Descriptor usage is represented by integer arrays protected by spinlocks. Pinned pages persist until `pvfs_bufmap_finalize`, normally invoked when `/dev/pvfs2-req` closes. `pvfs_bufmap_size_query` and `pvfs_bufmap_shift_query` provide block-size signals to inode/superblock setup.

## Dependencies and integration points
This file depends on `pvfs2-kernel.h` for locking, timeouts, debug, kernel-version wrappers, and page helpers; on `pint-dev-shared.h` for the device map descriptor; and on `pvfs2-bufmap.h` for declarations. `devpvfs2-req.c` initializes/finalizes the map from device ioctls and close. `file.c` uses the descriptor copy helpers for read/write staging. `dir.c` uses the readdir index pool. `super.c` and inode setup query descriptor size for VFS block sizing.

## Risks and edge cases
Copy routines assume callers keep `size` within the descriptor capacity; most functions do not explicitly bound `buffer_index` or total bytes against `desc_array[buffer_index].array_count`. `get_bufmap_init` returns `0` both when uninitialized and when it cannot acquire the read semaphore, so callers must not treat it as a stable state transition. `pvfs_bufmap_initialize` failure after `bufmap_page_array` allocation may leave that array freed locally but not reset in all paths before descriptor cleanup. Long `slot_timeout_secs` values can make descriptor exhaustion look like a hang. AIO task-iovec copying maps remote task pages and then calls `copy_to_user` on a kmap address, a fragile kernel-version-sensitive path.

## Test signals
Useful tests exercise daemon restart with outstanding I/O, `PVFS_DEV_MAP` alignment/size failures, descriptor exhaustion and wakeup, signal interruption, timeout behavior, reads/writes spanning multiple pages, iovecs that split exactly on page boundaries, readdir descriptor reuse, and cleanup after daemon close. Kernel debug class `GOSSIP_BUFMAP_DEBUG` should show slot waits, descriptor acquisition, and copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.h

## Purpose
`pvfs2-bufmap.h` declares the kernel-side shared-memory buffer map contract used by OrangeFS I/O and directory paths. It exposes the descriptor layout and the operations that initialize the daemon-provided map, reserve descriptor indices, release them, and copy data between mapped pages and VFS/user buffers.

## Important APIs and types
`struct pvfs_bufmap_desc` stores the userspace base address, the array of pinned `struct page *`, a page count, and an unused list hook. The core lifecycle calls are `pvfs_bufmap_initialize`, `get_bufmap_init`, and `pvfs_bufmap_finalize`. Slot management is split between `pvfs_bufmap_get`/`pvfs_bufmap_put` for normal I/O and `readdir_index_get`/`readdir_index_put` for directory operations. Copy APIs cover user buffers, kernel buffers, user iovecs, kernel iovecs, page-cache pages, and AIO completion into another task when `HAVE_AIO_VFS_SUPPORT` is enabled.

## Control flow and integration
The header is included by `pvfs2-bufmap.c`, file I/O code, directory code, inode/superblock setup, and device request handling. Callers normally reserve a descriptor, copy write data into the mapped descriptor or receive read data from it, send an upcall to the daemon that references the descriptor index, wait for a downcall, and then release the descriptor.

## State and persistence behavior
The header itself has no state, but it exposes routines over module-global bufmap state in `pvfs2-bufmap.c`. That state is per-loaded-module and per-active-client mapping rather than persistent storage.

## Dependencies
The header depends on `pint-dev-shared.h` for `struct PVFS_dev_map_desc` and on kernel types already included by `pvfs2-kernel.h` in most users. The `__user`, `struct iovec`, `struct page`, and `struct task_struct` types reflect tight coupling to Linux VFS and memory-management APIs.

## Risks and test signals
The API accepts raw descriptor indices and byte sizes, so correctness depends on callers validating indices, sizes, and release-on-error paths. Test signals should include every declared copy direction, zero-length and page-boundary iovec cases, missing daemon mapping behavior, AIO-only build coverage, and lockstep `get`/`put` accounting under concurrent I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-cache.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-cache.c

## Purpose
`pvfs2-cache.c` owns slab-cache allocation for the main kernel objects used by the OrangeFS client module: upcall/downcall operations, device request buffers, private PVFS2 inode objects, and optional AIO `pvfs2_kiocb` objects. It also assigns monotonically increasing operation tags and tracks allocated PVFS2 inodes on a module-global list for final leak cleanup.

## Important APIs and functions
`op_cache_initialize` and `op_cache_finalize` create/destroy the `pvfs2_op_cache` and reset `next_tag_value` to 100. `op_alloc`, `op_alloc_trailer`, and `op_release` allocate operation objects, initialize wait queues and locks, assign operation type, tag, credentials, and trailer linger count, and return objects to the cache. `get_opname_string` maps operation IDs to debug names. `dev_req_cache_initialize`, `dev_req_alloc`, and related release/finalize routines manage buffers sized to `MAX_ALIGNED_DEV_REQ_DOWNSIZE`. `pvfs2_inode_cache_initialize`, `pvfs2_inode_alloc`, and `pvfs2_inode_release` manage `pvfs2_inode_t` plus embedded VFS inode construction. AIO builds add `kiocb_cache_initialize`, `kiocb_alloc`, and `kiocb_release`.

## Control flow
Module initialization creates caches in dependency order before device registration. Operation allocation zeroes the slab object, initializes list/lock/waitqueue fields, calls `pvfs2_op_initialize`, assigns a unique tag under `next_tag_value_lock`, records current fsuid/fsgid in the upcall, and sets linger count. Inode allocation uses a slab constructor to perform one-time VFS inode setup and xattr semaphore initialization, then runtime allocation clears PVFS-specific fields and appends the object to `pvfs2_inode_list`.

## State and persistence behavior
All state is volatile kernel memory. `next_tag_value` persists only while the module is loaded and wraps from zero back to 100. `pvfs2_inode_list` is a diagnostic/cleanup list, not a persistent cache lookup structure. Finalization forcibly frees unreleased PVFS2 inode objects if the list is not empty, which prevents a slab leak but can hide lifecycle bugs during unload.

## Dependencies and integration points
The file relies on `pvfs2-kernel.h` for object definitions, cache flags, credential compatibility, and operation IDs. `pvfs2-mod.c` calls the initialize/finalize routines. Almost every VFS helper calls `op_alloc` and `op_release`. `inode.c` and superblock code consume `pvfs2_inode_alloc/release` through inode allocation and destruction.

## Risks and edge cases
`dev_req_alloc` uses `memset(buffer, 0, sizeof(MAX_ALIGNED_DEV_REQ_DOWNSIZE))`; because the macro is an integer expression, `sizeof(...)` is the size of the expression type, not the requested buffer size, so most of the allocated buffer may not be zeroed. The inode finalize path frees unreleased inodes without coordinating with external holders if unload proceeds with live references. Operation tag wrap is handled only for the zero value; duplicate tags are possible over a very long module lifetime if old operations remain in progress across wrap. Cache destroy return handling is version-dependent and may not catch outstanding objects on newer kernels.

## Test signals
Tests should check module init error unwinding at every cache creation step, tag uniqueness under concurrent `op_alloc`, credentials in upcalls, trailer linger values for trailer operations, full zeroing of device request buffers, inode constructor initialization, unload with intentionally leaked inode references, and AIO cache behavior under `HAVE_AIO_VFS_SUPPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-dev-proto.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-dev-proto.h

## Purpose
`pvfs2-dev-proto.h` defines the ABI constants and small serialization helpers shared by the kernel module and the user-space client daemon for `/dev/pvfs2-req` upcalls and downcalls. It is the operation-number registry for the kernel-to-client protocol.

## Important APIs and types
The `PVFS2_VFS_OP_*` constants identify every request type: file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, readahead flush, mount/unmount, xattrs, parameter control, performance counters, cancellation, fsync, fskey, readdirplus, vector I/O, and feature negotiation. `PVFS2_FEATURE_READAHEAD` advertises readahead support. Name/debug array limits and readdir entry limits define fixed buffer sizes. `roundup4`, `roundup8`, `enc_string`, and `dec_string` provide alignment-aware in-place string encoding. `struct read_write_x` carries offset/length pairs for extended I/O.

## Control flow and integration
The protocol constants are written into `pvfs2_kernel_op_t.upcall.type` by VFS helpers and checked by the daemon and device request code when matching downcalls. `pvfs2-cache.c` uses the constants for debug names, `pvfs2-utils.c` switches on them to derive an fsid from an operation, and proc/sysctl handlers issue `PVFS2_VFS_OP_PARAM` and `PVFS2_VFS_OP_PERF_COUNT`.

## State and persistence behavior
This header carries no runtime state. Its values are persistent ABI: changing IDs, struct alignment assumptions, or maximum sizes requires matching daemon-side changes and compatibility handling.

## Dependencies
It includes `pvfs2.h`, `upcall.h`, `downcall.h`, and `quickhash.h`. Those headers define the bulk request/response payloads and hash-list links used by kernel request tracking.

## Risks and test signals
The string macros do not validate destination capacity or decode length, so callers must provide trusted protocol buffers. The comment requires multiples of 8 for 32/64-bit compatibility; tests should include mixed 32-bit userspace to 64-bit kernel ioctl/downcall paths. ABI tests should verify operation ID parity with the daemon, max readdir count limits, string alignment, and feature negotiation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-dev-proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-kernel.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-kernel.h

## Purpose
`pvfs2-kernel.h` is the central internal header for the OrangeFS Linux VFS kernel module. It gathers Linux compatibility includes, constants, object definitions, global declarations, operation-state macros, prototypes, and version-dependent wrappers used across the kernel client.

## Important APIs, types, and macros
Key data structures are `pvfs2_kernel_op_t`, `pvfs2_inode_t`, `pvfs2_sb_info_t`, `pvfs2_mount_options_t`, optional `pvfs2_kiocb`, and `pvfs2_opaque_handle_t`. Operation state is modeled with `OP_VFS_STATE_UNKNOWN`, `WAITING`, `INPROGR`, `SERVICED`, `PURGED`, and `INTERRUPTED`, with setters/testers used by waitqueue and device code. The header declares all cache, waitqueue, superblock, inode, xattr, namei, file, device, and utility functions used across compilation units. Request-list macros `add_op_to_request_list`, `add_priority_op_to_request_list`, `remove_op_from_request_list`, and `remove_op_from_htable_ops_in_progress` manipulate global queues. Mount option macros expose `intr`, `acl`, and `suid`; `fill_default_sys_attrs` translates VFS creation state into PVFS attributes.

## Control flow
Most VFS paths allocate a `pvfs2_kernel_op_t`, fill an upcall payload, and call `service_operation`. The header defines the flags controlling that call: interruptible, priority, cancellation, no semaphore, and async. Request macros place operations on `pvfs2_request_list`, wake the device waitqueue, and let device code move operations to `htable_ops_in_progress` while waiting for matching downcalls.

## State and persistence behavior
The header declares module-global synchronization and queues: `devreq_semaphore`, `request_semaphore`, `pvfs2_superblocks`, `pvfs2_request_list`, `pvfs2_request_list_waitq`, and `htable_ops_in_progress`. Private inode flags track dirty atime/mtime/ctime/mode and initialization in memory. Superblock state tracks fsid, root handle, mount options, device name, mount-pending state, and allocation counters. None of this is disk-persistent; server metadata is fetched and flushed through upcalls.

## Dependencies and integration points
The header bridges Linux VFS, memory management, sysctl/xattr/ACL variants, PVFS protocol headers, khandle helpers, debug maps, and device protocol definitions. It is included by nearly every file in this kernel module and therefore forms the compile-time compatibility layer for multiple Linux 2.4/2.6-era APIs.

## Risks and edge cases
Large macros perform list manipulation and locking inline, making lock ordering and side effects easy to miss. `remove_op_from_request_list` scans and deletes without changing the op state. Opaque-handle encode/decode is enabled by a preprocessor define and assumes fixed structure layout and endian conversion. The compatibility surface is broad, so build coverage across kernel feature combinations is essential. `is_root_handle` and `match_handle` allocate memory for debug strings in inline helpers, which can fail silently and adds allocation in paths that look like simple predicates.

## Test signals
High-value tests include request lifecycle state transitions, cancellation, daemon restart purge, mount option flag effects, inode private-data conversion via `PVFS2_I`, superblock list add/remove, 32-bit SMP inode size helpers, xattr handler signature variants, exportfs opaque-handle encode/decode, and build matrix coverage for supported kernel feature macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-mod.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-mod.c

## Purpose
`pvfs2-mod.c` is the load/unload entry point for the OrangeFS kernel module. It declares core globals, registers the VFS filesystem type, initializes caches, device communication, request tracking, fskey tracking, proc/sysctl controls, and tears all of them down on module exit.

## Important APIs and globals
Module parameters include `hash_table_size`, `module_parm_debug_mask`, `op_timeout_secs`, and `slot_timeout_secs`. Global synchronization and queues defined here include `devreq_semaphore`, `request_semaphore`, `htable_ops_in_progress`, `pvfs2_request_list`, `pvfs2_request_list_lock`, and `pvfs2_request_list_waitq`. `pvfs2_fs_type` binds the filesystem name `pvfs2` to mount/get_sb and kill_sb callbacks. `purge_inprogress_ops` marks active operations as purged after daemon shutdown.

## Control flow
`pvfs2_init` normalizes the module debug mask, builds the debug-help string, initializes optional backing-dev info, clamps negative timeouts to zero, creates all slab caches, initializes the device subsystem, initializes semaphores and the in-progress qhash table, initializes the fskey table, registers proc/sysctl entries, and finally registers the filesystem. Error labels unwind in reverse order. `pvfs2_exit` unregisters the filesystem and proc entries, finalizes fskey/device state, releases pending request-list ops, releases all qhash in-progress ops, destroys caches, finalizes qhash, destroys backing-dev info, and logs unload.

## State and persistence behavior
State is module-global and volatile. Operation hash buckets index in-progress operations by tag. The request list queues operations waiting for the daemon to read from `/dev/pvfs2-req`. Debug strings and masks persist until module unload or proc/ioctl changes.

## Dependencies and integration points
This file depends on cache routines in `pvfs2-cache.c`, proc routines in `pvfs2-proc.c`, fskey and mount helpers in `super.c`, device setup in `devpvfs2-req.c`, and debug conversion in `pvfs2-utils.c`. Device and waitqueue code depend on the globals defined here.

## Risks and edge cases
`purge_inprogress_ops` iterates `hash_table_size`, not the live `htable_ops_in_progress->table_size`; if qhash initialization adjusts size, iteration could diverge. Module exit releases in-progress operations without first synchronizing all possible waiters visible in this file, relying on teardown ordering elsewhere. Debug-help string construction manually tracks an index into a fixed 4096-byte buffer and checks individual keyword lengths, not total remaining capacity. Failure unwinding is dense and should be checked whenever a new subsystem is added.

## Test signals
Tests should cover module load with valid and invalid debug masks, negative timeout parameters, cache/device/qhash failure injection and unwind, filesystem registration failure, daemon-close purge waking waiters, module unload with queued and in-progress operations, and proc/sysctl availability after successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.c

## Purpose
`pvfs2-proc.c` implements the `/proc/sys/pvfs2` sysctl control plane. It exposes kernel debug strings, client debug strings, operation and slot timeouts, client cache tunables, performance counter settings, performance counter reads, and kernel-maintained cache statistics.

## Important APIs, tables, and handlers
`pvfs2_proc_initialize` registers the sysctl table and `pvfs2_proc_finalize` unregisters it. `pvfs2_proc_debug_mask_handler` handles `kernel-debug`, `client-debug`, and read-only `debug-help`. `pvfs2_param_proc_handler` handles integer get/set operations by sending `PVFS2_VFS_OP_PARAM` upcalls to the client. `pvfs2_pc_proc_handler` reads client performance counter strings through `PVFS2_VFS_OP_PERF_COUNT`. Static `pvfs2_param_extra` records bind sysctl files to client parameter operations and min/max ranges. `g_pvfs2_stats` backs read-only kernel stats.

## Control flow
Generic proc helpers first parse or format user data. Kernel debug writes are converted locally into `gossip_debug_mask` and canonicalized back into `kernel_debug_string`. Client debug and client parameter reads/writes allocate an operation, fill a parameter request, call `service_operation` interruptibly, consume the downcall, and release the operation. Performance-counter reads honor file offsets by copying a slice of the returned text buffer to userspace.

## State and persistence behavior
`client_debug_string`, `kernel_debug_string`, `debug_help_string`, timeout globals, and `g_pvfs2_stats` live in module memory. Client-side tunables are not stored locally; this file sends requests to the daemon and reports daemon responses. Sysctl registration state is tracked by `fs_table_header`.

## Dependencies and integration points
The file depends on Linux sysctl/proc APIs, debug mask maps and conversion functions from `pvfs2-utils.c`, operation allocation from `pvfs2-cache.c`, and `service_operation` from waitqueue code. It is initialized by `pvfs2-mod.c` after caches, qhash, and device state are ready.

## Risks and edge cases
The client-debug write path calls `op_release(new_op)` and then prints `new_op->downcall.resp.param.u.value64`, which is a use-after-free pattern. Many handlers require a live client daemon; without one, sysctl reads/writes may block until timeout or return service errors. The table contains repeated `CTL_NAME(15)` values under optional readahead entries, which may matter on older numbered sysctl kernels. `pvfs2_pc_proc_handler` trusts the daemon-provided string to be NUL-terminated within the response buffer before `strlen`.

## Test signals
Tests should exercise read/write of kernel-debug, client-debug, op/slot timeout minmax enforcement, each cache tunable, perf-counter partial reads with offsets, daemon-down behavior, module unload after sysctl registration, and the use-after-free site with slab debugging or KASAN-style instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.h

## Purpose
`pvfs2-proc.h` declares the proc/sysctl lifecycle hooks for the OrangeFS kernel module.

## Important APIs
`pvfs2_proc_initialize(void)` registers `/proc/sys/pvfs2` controls when `CONFIG_SYSCTL` support is compiled in. `pvfs2_proc_finalize(void)` unregisters that table. Both are implemented in `pvfs2-proc.c` and called by `pvfs2-mod.c` during module load/unload and error unwinding.

## Control flow, state, and integration
The header carries no state. It lets module initialization remain independent of the internal sysctl table definitions. The implementation internally tracks registration with a `struct ctl_table_header *`, making initialize/finalize idempotent around a non-NULL header.

## Dependencies and risks
There are no direct includes beyond the guard, so this header has a narrow dependency surface. The main risk is lifecycle ordering: callers must initialize operation caches and device request infrastructure before registering handlers that can issue client upcalls, and must unregister before destroying those dependencies.

## Test signals
Tests should verify successful registration on module load, cleanup on load failure after registration, cleanup on normal unload, and no exported proc entries when `CONFIG_SYSCTL` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-utils.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-utils.c

## Purpose
`pvfs2-utils.c` is the broad utility layer for OrangeFS VFS operations. It translates PVFS attributes to Linux inodes and back, sends getattr/setattr/xattr/create/remove/truncate/unmount/cancel operations to the daemon, handles exportfs opaque file handles, initializes/finalizes operation and inode private data, manages signal masks for interruptible waits, normalizes PVFS errors to Linux errno values, translates modes, and converts debug keyword strings to masks.

## Important APIs and functions
Metadata APIs include `fsid_of_op`, `copy_attributes_to_inode`, `pvfs2_inode_getattr`, `pvfs2_inode_setattr`, and `pvfs2_flush_inode`. Xattr APIs include `pvfs2_inode_getxattr`, `pvfs2_inode_setxattr`, `pvfs2_inode_removexattr`, and `pvfs2_inode_listxattr`, protected by each inode's `xattr_sem`. Namespace APIs include `pvfs2_create_entry`, internal file/dir/symlink creation helpers, `pvfs2_remove_entry`, and `pvfs2_truncate_inode`. Mount/control helpers include `pvfs2_unmount_sb`, `pvfs2_cancel_op_in_progress`, optional `pvfs2_flush_racache`, and exportfs helpers `pvfs2_fill_handle` and `pvfs2_sb_find_inode_handle`. Initialization helpers include `pvfs2_inode_initialize`, `pvfs2_inode_finalize`, `pvfs2_op_initialize`, and `pvfs2_make_bad_inode`.

## Control flow
Most functions allocate a `pvfs2_kernel_op_t`, fill the relevant `upcall.req.*` structure from inode, dentry, or superblock state, call `service_operation` with mount-dependent interruptibility, read `downcall.resp.*`, update VFS objects, and release the op. Attribute copying maps PVFS object types to VFS inode mode, operations tables, block sizing, timestamps, ownership, and symlink targets. Dirty inode flush snapshots and clears local dirty flags before issuing a setattr, reducing duplicate close-time flushes. Xattr listing may loop until the daemon returns `PVFS_ITERATE_END`.

## State and persistence behavior
The file updates in-memory inode fields and PVFS2 private inode flags, but persistent metadata lives on OrangeFS servers and changes only after successful daemon service operations. Xattr semaphores serialize per-inode xattr access. Opaque file handles encode enough metadata to reopen by handle without an immediate server getattr, trading freshness for export/openfh efficiency.

## Dependencies and integration points
This file depends on `pvfs2-kernel.h` for structures, request lifecycle, mount flags, and compatibility wrappers; `pvfs2-dev-proto.h` for operation IDs; `pvfs2-bufmap.h` for block-size queries; and khandle helpers for handle serialization/debugging. It is called by inode, dentry, namei, superblock, xattr, file, proc, and waitqueue-related paths.

## Risks and edge cases
Several debug paths allocate fixed-size handle strings in hot metadata functions. `copy_attributes_to_inode` computes `rounded_up_size` as `inode_size + (4096 - inode_size % 4096)`, which rounds exact 4096 multiples up by another page. `pvfs2_inode_getattr` allocates a debug buffer and can return early on invalid inode private data without freeing it. `snprintf` results for xattr keys are used as lengths without checking truncation beyond prior length checks. Reserved xattr filtering uses `strncmp(key, reserved, size)`, so a short key that prefixes a reserved key can be treated as reserved. `pvfs2_strtok` uses static parser state and is not reentrant, so concurrent debug mask parsing can race. Some exportfs code references debug fields that appear inconsistent with `pvfs2_opaque_handle_t` naming and should be build-checked under the relevant feature macros.

## Test signals
Tests should cover getattr/setattr for all object types, root sticky-bit behavior, suid mount option behavior, exact-page file sizes, dirty flag flushing under concurrent close, xattr get/set/list/remove including reserved keys and binary values, create/remove/truncate success and failure paths, unmount and cancellation upcalls, PVFS-to-errno mapping, debug mask parsing with `all`, `none`, comma/space lists and negation, exportfs handle round trips, and daemon-down timeout/interruption behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-utils.c -->
