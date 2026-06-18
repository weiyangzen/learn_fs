## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-kernel.h

### Purpose
This is the central OrangeFS kernel header, defining core private structures, operation states, constants, inline helpers, cross-file declarations, global state, and service-operation flags.

### Important APIs, types, and functions
- Constants include default op/slot timeouts, request device name, protocol magic, max up/down sizes, and mount option bits.
- `enum orangefs_vfs_op_states` describes op lifecycle states: unknown, waiting, in progress, serviced, purged, and given up.
- `struct orangefs_kernel_op_s` contains op state, tag, shared-memory slot metadata, upcall/downcall payloads, completion, spinlock, attempts, and list node.
- `struct orangefs_inode_s`, `struct orangefs_sb_info_s`, `struct orangefs_stats`, `struct orangefs_cached_xattr`, and `struct orangefs_write_range` define per-inode, per-superblock, statistics, cached xattr, and dirty-range state.
- Inline helpers include `ORANGEFS_I()`, `ORANGEFS_SB()`, `orangefs_khandle_to_ino()`, `get_khandle_from_ino()`, `is_root_handle()`, `match_handle()`, `set_op_state_serviced()`, `set_op_state_purged()`, `fill_default_sys_attrs`, and `orangefs_set_timeout()`.
- It declares exported functions and globals across cache, module, waitqueue, superblock, inode, xattr, namei, device, file, utility, and operation service code.

### Control flow
Most OrangeFS source files include this header, allocate `orangefs_kernel_op_s` objects, fill upcalls, queue them through `service_operation()`, and inspect downcalls. State helpers drive operation transitions used by the device and waitqueue code. Inode and superblock helpers bridge VFS objects to OrangeFS private state.

### State and persistence behavior
The header defines runtime state layouts. Persistent server identity is represented by `orangefs_object_kref` stored in inodes and superblocks. Timeouts and mount flags drive local cache validity and interrupt behavior. Operation states are transient but central to daemon restart and cancellation semantics.

### Dependencies and integration points
Includes many Linux VFS, memory, mount, ACL, xattr, exportfs, and wait headers plus `orangefs-dev-proto.h`. It is the integration contract for all OrangeFS compilation units and must remain consistent with VFS API versions.

### Risks
Because this is a broad shared header, layout changes can affect slab usercopy ranges, ABI copies, waitqueue logic, and every subsystem. `set_op_state_purged()` has special cancellation behavior that frees a bufmap slot and releases the op; callers must not touch the op afterward. Timeout storage in `d_fsdata` casts jiffies through `void *`, which relies on pointer-sized storage.

### Test signals
Compile with sparse/lockdep and run module load/unload, daemon restart, cancellation, cache timeout, inode lookup, and xattr/ACL tests to cover the shared contracts.
