<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.h -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs.h

## Purpose
`v9fs.h` is the core 9p filesystem header defining session flags, cache modes, session state, inode wrapper state, and helper accessors.

## Important APIs, types, and functions
Key definitions are `enum p9_session_flags`, `enum p9_cache_shortcuts`, `enum p9_cache_bits`, `struct v9fs_session_info`, `struct v9fs_inode`, `V9FS_I`, and `v9fs_inode_cookie`.

## Control flow
The header has no primary control flow. Inline helpers recover the 9p inode wrapper and return an FS-Cache cookie when enabled.

## State and persistence
It defines runtime session state: mount options, access mode, protocol flags, cache mode, default ids, p9 client, session list linkage, rename semaphore, and lock retry timeout. Inode state tracks qid, netfs context, cache validity, and a mutex.

## Dependencies and integration points
It connects 9p VFS code to net/9p client types, transports, netfs, backing-dev support, and FS parser structures.

## Risks and test signals
Risks include flag bit overlap, cache shortcut interpretation, stale cache_validity handling, and assumptions about access mode masks. Test signals include compile coverage and mount/runtime tests for every cache/access/protocol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.h -->
