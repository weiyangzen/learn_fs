# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSExtentsSupport.cpp

## Purpose

`AFSExtentsSupport.cpp` manages the Windows OpenAFS redirector's local file-cache extents for regular file FCBs. It maps file byte ranges to cache offsets, requests missing extents from the user-mode service, accepts extent-map replies, pins extents during read/write I/O, tracks dirty extents after writes, flushes dirty data back to the service, releases cache space under pressure, and trims extent state after truncation or failure.

The module is the bridge between file I/O paths (`AFSRead.cpp`, `AFSWrite.cpp`, close/cleanup/flush code) and the redirector/service communication protocol (`AFS_REQUEST_TYPE_REQUEST_FILE_EXTENTS` and `AFS_REQUEST_TYPE_RELEASE_FILE_EXTENTS`). It is also tightly coupled to `AFSFcbSupport.cpp`, which initializes the per-file extent lists, resources, dirty-list state, and completion events that this file assumes are present on `AFS_FILE_FCB` objects.

## Important APIs, Types, And State

- `AFSExtent` stores one cached byte range: `FileOffset`, `CacheOffset`, `Size`, `Flags`, `ActiveCount`, optional `MD5`, intrusive `Lists[AFS_NUM_EXTENT_LISTS]`, and a separate `DirtyList` link.
- `AFSFcb::Specific.File` supplies the extent skip lists, file lock, `ExtentsDirtyCount`, `ExtentCount`, `QueuedFlushCount`, `ExtentLength` in KB, and file metadata used in release/flush requests.
- `AFSNonPagedFcb::Specific.File` supplies synchronization and event state: `ExtentsResource`, `DirtyExtentsListLock`, `ExtentsRequestComplete`, `FlushEvent`, `QueuedFlushEvent`, `DirtyListHead`, `DirtyListTail`, `ExtentsRequestStatus`, and `ExtentsRequestAuthGroup`.
- `ExtentsMasks` and `AFS_NUM_EXTENT_LISTS` implement a small skip-list-like index. The base list is the full extent list; upper lists contain extents whose offsets satisfy coarser alignment masks.
- Request/release wire structures include `AFSRequestExtentsCB`, `AFSSetFileExtentsCB`, `AFSReleaseExtentsCB`, `AFSReleaseFileExtentsCB`, `AFSReleaseFileExtentsResultCB`, `AFSReleaseFileExtentsResultFileCB`, `AFSFileExtentCB`, and `AFSExtentFailureCB`.
- Public helpers declared in `AFSCommon.h` include `AFSExtentForOffset`, `AFSDoExtentsMapRegion`, `AFSRequestExtentsAsync`, `AFSWaitForExtentMapping`, `AFSProcessSetFileExtents`, `AFSProcessReleaseFileExtents`, `AFSProcessExtentFailure`, `AFSFlushExtents`, `AFSReleaseExtentsWithFlush`, `AFSReleaseCleanExtents`, `AFSMarkDirty`, `AFSTearDownFcbExtents`, `AFSDeleteFcbExtents`, `AFSTrimExtents`, active reference helpers, and dirty-list/byte-range helpers.

## Control Flow

Extent lookup is based on `AFSExtentForOffsetHint`, `AFSEntryForOffset`, `ExtentForOffsetInList`, `AFSExtentContains`, `ExtentFor`, and `NextExtent`. Callers must hold `ExtentsResource`; the code asserts that and then walks upper extent lists down to the base list to find the containing extent or nearest previous extent. `AFSDoExtentsMapRegion` uses those lookups plus adjacency checks to determine whether a requested byte range is fully mapped by contiguous extents.

Read and write paths call `AFSRequestExtentsAsync` when a range is missing. That function first checks any remembered service failure for the same auth group, checks whether the range is already mapped, aligns the request to `CacheBlockSize`, suppresses duplicate queued requests via `AFSIsExtentRequestQueued`, clears `ExtentsRequestComplete`, and sends an asynchronous `AFS_REQUEST_TYPE_REQUEST_FILE_EXTENTS`. If the service denies access for the current CCB auth group, it retries using `AFSRetrieveValidAuthGroup` when that yields a different group.

The service returns extent maps through `AFSProcessSetFileExtents`. This locates the volume by high FID index under `VolumeTreeLock`, references the volume, locates the object by low FID index under the volume object tree lock, references the object, and then either records a canceled extent request on service failure or calls `AFSProcessExtentsResult`. `AFSProcessExtentsResult` holds the file extent resource exclusive, walks the incoming extents in order, inserts new `AFSExtent` records into the base and skip lists, updates per-file and global extent counts/lengths, rejects overlap or size mismatches, trims newly supplied extents on insertion failure, and signals `ExtentsRequestComplete`.

Service-reported failures enter through `AFSProcessExtentFailure`. It validates the IOCTL buffer, resolves the FID to a live FCB, writes `ExtentsRequestStatus` and `ExtentsRequestAuthGroup`, and signals `ExtentsRequestComplete`. `AFSWaitForExtentMapping` waits up to one second on that event, returns stored failures for matching auth groups or the system process, and converts timeout into success so callers can retry/request again without treating the wait as a hard I/O error.

Extent release has multiple paths. `AFSProcessReleaseFileExtents` is the user-mode initiated IOCTL path: it validates buffers, either targets a specific FID or asks `AFSFindFcbToClean` for a candidate file, locks extents, builds a result structure, obtains a valid auth group, populates file metadata, and delegates actual removal to `AFSReleaseSpecifiedExtents`. That helper reports `UNKNOWN` for absent requested extents, `IN_USE` for active requested extents, skips active extents on release-all, removes dirty-list entries when needed, emits `DIRTY` and `RELEASE` flags, and frees released extents.

Driver-initiated cleanup uses `AFSTearDownFcbExtents`, `AFSDeleteFcbExtents`, `AFSFlushExtents`, `AFSReleaseExtentsWithFlush`, and `AFSReleaseCleanExtents`. Teardown releases as many inactive extents as it can and synchronously notifies the service. Delete removes local extents without a service release request. Flush repeatedly removes non-active dirty extents from the dirty list, marks them clean before sending to make concurrent writes re-dirty them, frees their local extent records, and synchronously sends dirty release batches. The release-with-flush and clean-release variants release inactive extents for cache-pressure and close paths, optionally retaining about 1 MB when handles remain open.

Writes call `AFSReferenceActiveExtents` before I/O, optionally `AFSSetupMD5Hash`, and then `AFSMarkDirty` after successful writeback to local cache. `AFSMarkDirty` inserts extents into the ordered dirty list, increments `ExtentsDirtyCount`, sets `AFS_EXTENT_DIRTY`, and can also dereference active extents as part of the write completion path. Plain reads use the active reference/dereference helpers to prevent release while cache pages are being consumed.

Truncation and error cleanup call `AFSTrimExtents` or `AFSTrimSpecifiedExtents`. `AFSTrimExtents` aligns a file size up to the cache block boundary, removes all extents at or beyond that aligned offset, removes dirty-list entries and decrements dirty counts, asserts inactive extents, frees records, and clears `ExtentsRequestStatus`. The specified variant removes only incoming result offsets, primarily after a failed extent-map insertion.

## State And Persistence Behavior

The file maintains volatile kernel-cache state, not durable AFS metadata. The persistent effects are indirect: dirty extent release requests carry file size and timestamp metadata plus dirty/cache/file offsets to the user-mode service, which owns the actual cache backing and server updates. Local extent records are allocated from nonpaged pool, are attached to FCBs, and are discarded on FCB teardown, deletion, cleanup, truncation, cache pressure, or service-directed release.

Important local state transitions include clean extent insertion, active pinning while I/O owns a range, dirty marking after writes, dirty-list removal during flush/release/trim, extent count and KB-length updates on allocation/free, global control-device `ExtentCount` and `ExtentsHeldLength` accounting, and `ExtentsHeldEvent` clear/set when global held extents cross zero. `ExtentsRequestStatus` is used as a one-shot remembered failure keyed by auth group and reset after it is delivered to a matching caller.

The code relies on `ExtentsResource` as the main extent-map lock and `DirtyExtentsListLock` for the dirty-list overlay. Some paths release `ExtentsResource` before synchronous `AFSProcessRequest` calls to avoid holding kernel locks across service round trips; by that point local extent records have already been detached/freed or the path depends on the active/dirty protections documented in the comments.

## Dependencies And Integration Points

- `AFSCommon.h`, `AFSRedirCommonStructs.h`, `AFSUserStructs.h`, and `AFSUserDefines.h` define FCB, extent, IOCTL, request, release, and flag structures.
- `AFSFcbSupport.cpp` initializes `ExtentsResource`, `DirtyExtentsListLock`, events, extent list heads, and dirty-list pointers.
- `AFSRead.cpp` and `AFSWrite.cpp` request/wait for mappings and pin/deref active extents; write also marks dirty and may generate MD5 hashes.
- `AFSDevControl.cpp` dispatches service IOCTLs to `AFSProcessSetFileExtents` and `AFSProcessReleaseFileExtents`.
- `AFSClose.cpp`, `AFSCleanup.cpp`, `AFSFlushBuffers.cpp`, `AFSGeneric.cpp`, `AFSFileInfo.cpp`, and `AFSWorker.cpp` flush, release, or trim extents during close, cleanup, purge, truncation, cache pressure, and worker processing.
- `AFSProcessRequest`, `AFSIsExtentRequestQueued`, `AFSRetrieveValidAuthGroup`, `AFSLocateHashEntry`, `AFSVolumeIncrement/Decrement`, and `AFSObjectInfoIncrement/Decrement` provide service communication and lifetime pinning.
- Cache access for MD5 can use `AFSLibCacheBaseAddress` for nonpersistent cache or `AFSReadCacheFile` for file-backed cache.

## Risks And Edge Cases

- The skip-list implementation is manual and intrusive. Any missed list removal, duplicate insertion, incorrect mask condition, or stale cursor can corrupt the extent index.
- Several functions require callers to hold `ExtentsResource`, and some require exclusive ownership; misuse from other modules can race free/insertion against read/write pinning.
- Active extents are protected only by `ActiveCount` discipline. Missed dereferences leak cache space; missed references allow release while I/O is still using the cache range.
- `AFSFlushExtents` clears `AFS_EXTENT_DIRTY` before the synchronous service request and frees the extent regardless of service status. The comments state the extent is considered released even on request failure, but this makes error reporting and cache coherency highly dependent on service semantics.
- Buffer-size calculations mix fixed header offsets, variable arrays, and `ExtentCount`; off-by-one or integer overflow bugs would affect kernel IOCTL safety.
- `AFSFindFcbToClean` walks volume/object lists while taking and releasing locks to avoid deadlock. It depends on volume/object references to keep nodes stable and skips open handles/queued flushes.
- `AFSTrimExtents` dereferences `FileSize` after a null check path; practical callers appear to pass a size, but the local code would be unsafe if `NULL` reached the `0 == FileSize->QuadPart` branch.
- Auth-group fallback and remembered failure handling are subtle: failures are delivered only to matching auth groups or system process paths, and status is reset after delivery.
- Optional `GEN_MD5` code allocates temporary buffers and reads cache contents while holding the extents resource shared; partial writes and allocation tag mismatch during free should be reviewed if MD5 is enabled.

## Test Signals

- Read/write tests where requested byte ranges are already fully mapped, partially mapped with a gap, and completely unmapped; assert aligned service requests and eventual mapping.
- Service reply tests for ordered extents, duplicate extents, overlapping extents, mismatched lengths, empty extent lists, and failure result statuses.
- Concurrent I/O and cache-pressure tests proving active extents return `IN_USE` or are skipped, and that dereference paths eventually allow release.
- Dirty write/flush tests checking dirty-list ordering, `ExtentsDirtyCount`, release flags, metadata fields, `FlushEvent`, `QueuedFlushEvent`, and re-dirty behavior during concurrent writes.
- Truncation tests covering exact cache-block boundaries and unaligned sizes, ensuring later extents and dirty-list entries are removed without touching earlier valid ranges.
- Service IOCTL fuzz tests for too-small input/output buffers, zero `ExtentCount`, unknown FIDs, missing FCBs, release-all requests, and output `IoStatus.Information`.
- Auth tests for access-denied retry with alternate auth group and remembered failure delivery to the same CCB auth group.
- Cache accounting tests for per-FCB `ExtentCount`/`ExtentLength`, control-device global `ExtentCount`/`ExtentsHeldLength`, and `ExtentsHeldEvent`.
