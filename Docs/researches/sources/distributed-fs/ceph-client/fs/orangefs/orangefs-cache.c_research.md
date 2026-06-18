## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-cache.c

### Purpose
This file manages the slab cache for OrangeFS kernel operations and assigns unique operation tags used to match daemon downcalls to VFS waiters.

### Important APIs, types, and functions
- `op_cache_initialize()` creates a usercopy-aware `orangefs_op_cache` and initializes `next_tag_value`.
- `op_cache_finalize()` destroys the cache.
- `get_opname_string()` maps operation type constants to debug strings.
- `orangefs_new_tag()` increments the tag counter under a spinlock, skipping zero.
- `op_alloc()` allocates and initializes `struct orangefs_kernel_op_s`, sets type, tag, state, completion, list, lock, and current fsuid/fsgid in the upcall.
- `op_release()` frees the operation back to the slab.

### Control flow
Module init creates the slab before any operation can be allocated. Each VFS path calls `op_alloc(type)`, fills request-specific upcall fields, sends it through `service_operation()`, then calls `op_release()` when finished. The device write path uses the operation tag to locate the in-progress op and complete it.

### State and persistence behavior
Operation objects are transient. Tags are monotonically increasing runtime identifiers, reset at module load, and form the matching key for in-memory requests only.

### Dependencies and integration points
Depends on `orangefs_kernel_op_s` layout, protocol operation constants, current credentials, and debug logging. Used by every OrangeFS subsystem issuing upcalls.

### Risks
Tag uniqueness is only within a module lifetime and can wrap; the code resets zero to 100. Any op released while still reachable from request or hash lists would be catastrophic, so ownership conventions around cancellation and purge paths matter. Usercopy slab bounds must stay aligned with copied upcall fields.

### Test signals
Stress concurrent op allocation, tag wrap simulation, daemon downcall matching, cancellation/purge release paths, and slab init/finalize during module load failure unwinds.
