# sources/distributed-fs/eos/mgm/drain/DrainTransferJob.cc

## Purpose
Implements a single file transfer used by drain, balance, repair, and related workflows. It selects a destination filesystem when needed, builds signed XRootD TPC source/destination URLs, executes the copy, handles ghosts/detached files, and updates metadata for zero-byte replica files.

## Important APIs and Functions
- `ContainerExists` checks whether a file parent container still exists.
- `ReportError` logs and marks the job failed.
- `DoIt` orchestrates metadata lookup, ghost/detached cleanup, destination selection, zero-size fast path, TPC preparation/execution, retry over sources, and final status.
- `GetFileInfo` prefetches file metadata and copies needed fields into `FileMdProto`.
- `BuildTpcSrc` selects a source replica or RAIN reconstruct path, builds source capability, and returns a root URL.
- `BuildTpcDst` snapshots target fs, builds destination capability and checksum parameters, and returns a root URL.
- `SelectDstFs` uses `GeoTreeEngine::placeNewReplicasOneGroup` with existing replicas/geotags and exclusions to pick a target.
- `DrainZeroSizeFile` updates namespace locations without data transfer.
- `GetInfo` formats requested monitoring tags.
- `UpdateMgmStats` maps app tag/status into MGM statistic counters.

## Control Flow
`DoIt` rejects pre-cancelled jobs, reads metadata, removes ghost or detached entries as successful cleanup, and then loops while alternate sources may be tried. If no forced target is set, it selects one. Replica zero-byte files skip TPC and directly adjust locations. Otherwise it builds source/destination URLs, prepares an XrdCl copy, runs it, and marks success on OK. Prepare/TPC failures log errors; cancellation and `EINPROGRESS` stop retrying.

## State and Persistence
The job mutates namespace replica locations for zero-size files and can trigger FST/MGM-side writes through signed TPC capabilities for non-empty files. Ghost/detached handling drops replicas. Runtime state includes source/target fsids, actual transfer source, tried sources, excluded destinations, RAIN flags, drop-source behavior, transfer progress, error string, and virtual identity for stats.

## Dependencies and Integration Points
Depends on global `gOFS`, `FsView`, `GeoTreeEngine`, `proc_fs_dropghosts`, XrdCl copy, EOS security capabilities via `SymKey`, layout helpers, string tokenization, namespace prefetching, and file metadata services. It is used by `DrainFs` and can also be configured for balance/fsck-like operations via constructor flags.

## Risks
- Error string construction in `BuildTpcDst` uses `err += caprc`, appending a character rather than decimal text.
- `DrainProgressHandler::JobProgress` divides by `bytesTotal` without zero guard.
- Detached-file handling drops all replicas when parent is missing; this is intended cleanup but high-impact if container lookup is transiently wrong.
- Source selection for replica layouts may choose source fs even if its snapshot status is unsuitable in the fallback path.
- RAIN reconstruction is attempted only once; transient failures become job failures.
- Capability construction and URL parameter correctness are security-critical and hard to unit test without integration coverage.

## Test Signals
Tests should cover ghost metadata exceptions, detached parent cleanup, destination placement failure, source retry/exclusion, RAIN reconstruct vs balance URL construction, checksum parameter padding, zero-size metadata update, cancellation, `EINPROGRESS`, and stats tag generation.
