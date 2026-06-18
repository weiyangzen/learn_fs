# sources/distributed-fs/ceph/src/client/Dir.h

## Purpose
`Dir.h` defines the small per-directory cache container owned by a directory inode.

## Important APIs, Types, and Functions
`Dir` stores `parent_inode`, an unordered map from names to `Dentry*`, `num_null_dentries`, and a `readdir_cache` vector. The constructor records the parent inode. `is_empty()` tests whether the dentry map is empty.

## Control Flow
`Inode::open_dir()` allocates `Dir` lazily for directory inodes. `Dentry` construction inserts into `dentries`, link/unlink updates null counts, and client readdir/cache paths use `readdir_cache` for ordered cached directory entries.

## State and Persistence Behavior
All state is volatile metadata cache. The MDS remains authoritative for directory contents, leases, and dirfrag mapping; this object holds the client-side materialized entries.

## Dependencies and Integration Points
It forward-declares `Dentry` and `Inode` and uses STL containers. `Client`, `Dentry`, and `Inode` coordinate its lifetime.

## Risks and Edge Cases
`parent_inode` is a raw pointer and must outlive the `Dir`. `num_null_dentries` must stay balanced with dentry link state. Readdir cache invalidation must track directory completeness and ordered flags in `Inode`.

## Test Signals
Directory open/close lifecycle, dentry map insert/erase accounting, null dentry counts, readdir cache invalidation, and cache trimming of empty dirs.
