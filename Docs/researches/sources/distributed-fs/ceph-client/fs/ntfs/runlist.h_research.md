# sources/distributed-fs/ceph-client/fs/ntfs/runlist.h

## Purpose
`runlist.h` defines the NTFS in-memory runlist representation and declares runlist manipulation and mapping-pairs APIs.

## Important APIs and Types
`struct runlist_element` maps VCN ranges to LCN ranges. `struct runlist` wraps an array with an `rw_semaphore`, element count, and lookup hint. `ntfs_init_runlist()` initializes empty state. The header defines negative LCN sentinel values: `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_ENOMEM`, `LCN_EIO`, and `LCN_EINVAL`. It declares merge, decompress, lookup, build, truncate, sparse, compressed-size, insert-range, punch-hole, collapse-range, and realloc functions.

## Control Flow and State
The state contract is that `runlist->rl` is either null or a sorted, VCN-contiguous array ending in a zero-length terminator. Callers must use the embedded lock to serialize access. `count` tracks allocated/valid elements, while `rl_hint` can cache lookup position for other code.

## Dependencies and Integration
The header includes `volume.h` for volume geometry and exposes functions used by attributes, allocation, compression, MFT extension, and file range operations.

## Risks
Sentinel values are semantically overloaded as negative LCNs and error-like codes. Callers must distinguish holes/unmapped regions from true errors. The API documents no automatic locking; misuse can race runlist mutation. Ownership-transfer semantics of functions that free inputs are only in implementation comments, not visible in prototypes.

## Test Signals
Compile coverage plus focused runlist tests should verify initialization, lock usage by callers, sentinel interpretation, count maintenance, and API behavior for null or malformed runlists.
