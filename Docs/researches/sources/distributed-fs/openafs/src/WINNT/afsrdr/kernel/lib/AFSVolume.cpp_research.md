# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolume.cpp

## Purpose
`AFSVolume.cpp` creates, caches, references, and removes `AFSVolumeCB` instances. It initializes root object and directory structures, retrieves volume metadata from the service, publishes real volumes in the global hash tree/list, tears down volume-owned state, and tracks references by reason.

## Important APIs, Types, And Functions
The exported routines are `AFSInitVolume`, `AFSRemoveVolume`, `AFSVolumeIncrement`, and `AFSVolumeDecrement`.

`AFSInitVolume` first retrieves `AFSVolumeInfoCB` for non-reserved cell entries, takes the global volume tree/list locks, checks for an existing volume by `AFSCreateHighIndex`, and returns it with an incremented reference and the volume lock held if found. Otherwise it allocates paged and nonpaged volume/object/directory structures, initializes resources and root metadata, copies service volume information, and inserts non-reserved volumes into `VolumeTree` and `VolumeListHead/Tail`.

`AFSRemoveVolume` requires zero references, removes the volume from global structures, tears down PIOCtl child state, releases service-held FIDs, deletes resources, frees nonpaged/paged root structures, and frees the VCB. The refcount helpers update total and per-reason counters with interlocked operations.

## Control Flow
Service metadata retrieval occurs before global locks to avoid blocking shared volume structures on communication. Race handling occurs under volume tree/list locks. Successful initialization, both hit and miss, returns with `VolumeLock` acquired exclusively. Removal performs unlinking before freeing resources.

## State And Persistence Behavior
State is the in-memory redirector volume cache: hash-tree/list linkage, root object info, root directory, root FCB pointer, service-provided `AFSVolumeInfoCB`, locks, and per-reason references. No disk state is written. The service remains authoritative for volume metadata and FID ownership.

## Dependencies And Integration Points
The file depends on redirector device extension volume structures, `AFSRetrieveVolumeInformation`, `AFSReleaseFid`, hash helpers, object/Fcb cleanup helpers, allocation callbacks, resources, and reference reason constants. It is used by name parsing, mount-point/root-volume construction, object lookup, and volume invalidation paths.

## Risks And Edge Cases
The returned-lock contract is easy to violate. Failure cleanup assumes certain resources have been initialized/acquired. Concurrent initialization intentionally performs redundant service calls. Reference reasons are unchecked array indexes. Removal must be synchronized against all outstanding name, object, worker, and mount-point references.

## Test Signals
Test global-root and real-volume initialization, concurrent same-volume initialization, service failures, allocation failures at each step, hash/list insertion/removal, returned lock release, reference reason counts and underflow assertions, PIOCtl cleanup, FID release, and head/tail/middle list removal.
