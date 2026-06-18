# sources/distributed-fs/ceph/src/client/Dentry.h

## Purpose
`Dentry.h` defines the client metadata-cache dentry object that links a parent `Dir` name to an optional `Inode`, tracks leases and ordering offsets, and participates in the LRU cache.

## Important APIs, Types, and Functions
`Dentry` derives from `LRUObject`. Constructor inserts into `Dir::dentries` and starts as a null dentry. `get()`/`put()` manage refs and LRU pinning. `link()` attaches an `InodeRef` and links into the inode dentry xlist. `unlink()` detaches the inode and updates null counts. `mark_primary()`, `detach()`, `make_path_string()`, `dump()`, and `print()` support cache maintenance and diagnostics. Fields include `lease_mds`, `lease_ttl`, `lease_gen`, `lease_seq`, `cap_shared_gen`, `alternate_name`, and `is_renaming`.

## Control Flow
Client lookup/readdir paths create dentries, link them to inode traces, touch or trim them through LRU, and unlink/detach them on invalidation or cache eviction. Directory inodes pin their parent dentry while `inode->dir` or `ll_ref` is held, preventing directory ancestry from disappearing unexpectedly.

## State and Persistence Behavior
Dentries are transient cache entries. Lease fields cache MDS dentry lease validity and sequencing. Offset supports readdir ordering. `alternate_name` carries encrypted long-name backing data when fscrypt name wrapping needs a separate MDS field.

## Dependencies and Integration Points
It depends on `Dir`, `Inode`, `InodeRef`, MDS types, xlist, and LRU. `Client` owns link/unlink/trim policy and lease updates. `DentryRef` supplies intrusive pointer ownership.

## Risks and Edge Cases
Refcount transitions must match LRU pin/unpin expectations: `ref==1` means cached only, `ref>1` pinned. `unlink()` assumes an inode is present and its xlist link is still attached. `detach()` only applies after inode unlink. Directory dentry pinning must mirror `Inode::open_dir()` and ll refs or leaks/asserts can result.

## Test Signals
Lookup/link/unlink cycles, negative dentry trimming, directory open/close pin accounting, rename invalidation, dentry lease hit/miss behavior, encrypted alternate-name path reconstruction, and LRU eviction.
