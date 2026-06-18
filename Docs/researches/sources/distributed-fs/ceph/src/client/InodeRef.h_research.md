# sources/distributed-fs/ceph/src/client/InodeRef.h

## Purpose
`InodeRef.h` defines the intrusive smart-pointer alias used to hold client inode refs.

## Important APIs, Types, and Functions
It forward-declares `Inode`, declares `intrusive_ptr_add_ref(Inode*)` and `intrusive_ptr_release(Inode*)`, and aliases `InodeRef` to `boost::intrusive_ptr<Inode>`.

## Control Flow
Any `InodeRef` increments/decrements the inode’s embedded refcount through functions implemented elsewhere. It is used in dentries, file handles, requests, snap dirs, roots, cwd, and many client helper results.

## State and Persistence Behavior
No state is persisted. The alias controls lifetime of in-memory inode cache records.

## Dependencies and Integration Points
It depends only on Boost intrusive pointer. `Client`, `Dentry`, `Fh`, `MetaRequest`, `Inode`, and `SnapRealm` all integrate this ownership model.

## Risks and Edge Cases
Raw `Inode*` and `InodeRef` are mixed heavily. Any raw pointer escaping without a corresponding ref can race trimming, while leaked refs keep cache and caps pinned.

## Test Signals
Inode trim with outstanding refs, low-level ll_get/ll_put behavior, file handle and dentry lifetime tests, and reconnect/unmount cache teardown.
