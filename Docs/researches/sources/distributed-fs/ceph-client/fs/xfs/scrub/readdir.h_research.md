# sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.h

## Purpose
`readdir.h` declares the scrub directory callback API and lock helper used by multiple scrub and repair modules.

## Important APIs, Types, And Functions
`xchk_dirent_fn` is the callback signature receiving scrub context, directory inode, data position, name, inode number, and private data. Declared functions are `xchk_dir_walk`, `xchk_dir_lookup`, and `xchk_dir_trylock_for_pptrs`.

## Control Flow
No standalone control flow exists. Callers provide a callback and private state to `xchk_dir_walk`, or use `xchk_dir_lookup` for exact name resolution.

## State And Persistence Behavior
The API itself is read-only. Lock helper calls mutate held lock state in the scrub context.

## Dependencies And Integration Points
It depends on XFS directory dataptr, name, inode, and scrub types. It is a central integration point for nlinks, parent scrub, parent repair, and orphanage code.

## Risks And Edge Cases
Callbacks must be prepared for synthesized dot entries in shortform directories and for names that have not yet been semantically validated. Callers must hold the required inode locks before walking or lookup.

## Test Signals
Callback consumers should test correct handling of dot, dotdot, invalid names, and early callback error termination.
