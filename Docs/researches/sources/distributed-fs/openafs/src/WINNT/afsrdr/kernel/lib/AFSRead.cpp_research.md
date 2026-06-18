# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSRead.cpp

## Purpose
`AFSRead.cpp` implements read dispatch for ordinary files, pioctl nodes, and special share/pipe nodes in the OpenAFS redirector library. It selects between Windows Cache Manager reads, noncached local-cache extent reads, direct user-service reads, pioctl reads, and pipe reads while enforcing shutdown, lock, EOF, deletion, invalidation, and resource synchronization rules.

## Important APIs, Types, And Functions
Public functions are `AFSRead`, `AFSCommonRead`, `AFSIOCtlRead`, and `AFSShareRead`; static helpers are `AFSCachedRead`, `AFSNonCachedRead`, and `AFSNonCachedReadDirect`.

`AFSCommonRead` is the policy gate: it pins the `FILE_OBJECT`, rejects shutdown and invalid FCBs, routes `AFS_IOCTL_FCB` and `AFS_SPECIAL_SHARE_FCB`, checks cache readiness, handles zero-length and MDL-complete requests, validates byte-range locks, rejects deleted/invalid objects, applies EOF truncation, initializes cache maps, handles cached MDL reads, and then delegates to cached or noncached helpers.

`AFSCachedRead` calls `CcCopyRead` over the system buffer/MDL chain. `AFSNonCachedRead` requests and waits for extents, builds IO runs against the cache file, queues gathered reads, waits for completion, and releases active extents. `AFSNonCachedReadDirect` sends `AFS_REQUEST_TYPE_PROCESS_READ_FILE` with an `AFSFileIOCB`. `AFSIOCtlRead` sends `AFS_REQUEST_TYPE_PIOCTL_READ`; `AFSShareRead` sends `AFS_REQUEST_TYPE_PIPE_READ`.

## Control Flow
Ordinary reads pass common validation before data movement. Cached reads retain section-object synchronization and use `CcCopyRead` or `CcMdlRead`. Noncached reads release file resources before issuing service/cache-file IO, then complete in the helper. Persistent-cache noncached reads loop until extents are mapped, re-requesting after `ExtentRequestTimeCount`. Direct-service reads bypass extents when `AFS_DEVICE_FLAG_DIRECT_SERVICE_IO` is set.

## State And Persistence Behavior
The code updates IRP status/information, synchronous `CurrentByteOffset`, cache-map state, active extent references, extent wait state, and optional extent release/flush behavior. Persistent-cache reads consume the local cache file through extents; nonpersistent-cache reads use `AFSProcessExtentRun`; direct reads rely on the user-mode service to fill the mapped buffer. It does not modify file contents.

## Dependencies And Integration Points
Dependencies include Cache Manager (`CcInitializeCacheMap`, `CcCopyRead`, `CcMdlRead`, `CcMdlReadComplete`), MDL/user-buffer mapping, FSRTL byte-range locks, FCB/CCB/object-info structures, extent APIs (`AFSRequestExtentsAsync`, `AFSDoExtentsMapRegion`, `AFSWaitForExtentMapping`, `AFSGetExtents`, `AFSSetupIoRun`, active extent refcounting), cache-file references, `AFSQueueStartIos`, `AFSProcessRequest`, and service buffer mapping helpers.

## Risks And Edge Cases
IRP completion ownership is delicate because some paths complete in helpers while early failures complete in `AFSCommonRead`. EOF arithmetic and `ULONG` casts deserve boundary tests. Holding resources across extent waits or cache-file IO would deadlock, so the release-before-noncached-IO contract is important. Active extents must be dereferenced on every failure path. Direct-service reads expose kernel buffer/MDL metadata through the service contract and depend on correct service behavior.

## Test Signals
Test cached, MDL, noncached extent, nonpersistent-cache, and direct-service reads; zero length; EOF and beyond EOF; byte-range lock conflicts; deletion/invalid flags; shutdown; cache-file unavailable; extent request/wait failures; IO-run allocation and gathered IO failures; current-byte-offset updates; pioctl reads; and special-share pipe reads including `STATUS_BUFFER_OVERFLOW`.
