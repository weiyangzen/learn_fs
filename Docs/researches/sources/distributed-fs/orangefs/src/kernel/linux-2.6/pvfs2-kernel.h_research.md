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
