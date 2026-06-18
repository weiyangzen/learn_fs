# sources/distributed-fs/ceph-client/fs/udf/udf_i.h

## Purpose
`udf_i.h` defines UDF in-core inode-private state and extent-position helper structures. It is the central contract for all UDF inode, allocation, directory, symlink, and truncation code.

## Important APIs, types, and functions
It defines `struct extent_position`, `struct udf_ext_cache`, and `struct udf_inode_info`, plus `UDF_I()` to recover the private inode from `struct inode`. Important fields include physical inode location, unique ID, extended attribute and allocation descriptor lengths, logical extent length, allocation goals, checkpoint/extra permissions, allocation type, extended-file-entry flags, stream directory fields, inline data pointer, metadata buffer tracking, extent cache, and extent-cache lock.

## Control flow
The header has no standalone control flow. Its comments define locking rules: regular file and symlink allocation information is protected by `i_data_sem` and inode mutex; extent mutations require write ownership and inode serialization. Directory protection is through inode mutex.

## State and persistence
Most fields mirror or cache persistent file-entry data: location, unique ID, allocation descriptors, inline data, timestamps, and extent lengths. Other fields are runtime-only allocation hints, caches, locks, and metadata buffer accounting.

## Dependencies and integration points
It is included by nearly every UDF C file. `super.c` initializes the structure in the slab constructor/allocator, `inode.c` populates it from disk, and `namei.c`, `partition.c`, `truncate.c`, and `symlink.c` rely on the layout and locking rules.

## Risks and test signals
Risks include violating allocation locking rules, stale cached extents after mutation, inconsistent `i_lenAlloc`/`i_lenExtents`, and inline data lifetime issues. Test signals include concurrent buffered writes/truncates, inline-to-block expansion, symlink reads during eviction, and metadata buffer dirty tracking under writeback.
