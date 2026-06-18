# sources/distributed-fs/eos/mgm/convert/ConversionJob.cc

## Purpose
Implements execution of a file layout/location conversion. A job creates a temporary converted file via XRootD third-party copy, verifies the result and original checksum, then merges new physical locations back onto the original fid while preserving namespace identity.

## Important APIs and Functions
- `NewUrl` creates a root URL pointing at the MGM alias and manager port.
- `TpcProperties` configures XrdCl copy properties and timeout based on file size.
- `getDiskFsIdOfFile` selects a non-tape filesystem for tape GC notification.
- `ConversionJob::DoIt` orchestrates metadata lookup, destination CGI construction, TPC execution, result verification, merge, stats, tape GC notification, and callback cancellation.
- `HandleError` records status, increments failure stats, logs, stores timestamped error text, and cancels callback.
- `ConversionCGI` maps target layout/location/policy into EOS open parameters.
- `Merge` adds converted locations to the original file, asks FSTs to locally rename physical files from conversion fid to original fid, unlinks old non-tape locations, updates layout/ctime, updates quota, and resyncs new locations.

## Control Flow
`DoIt` rejects pre-cancelled jobs, marks running, reads original metadata under namespace lock, builds source and conversion destination URLs, excludes original/unlinked fsids from destination placement, runs XrdCl TPC, validates converted stripe count, re-reads the original checksum, aborts if it changed, and calls `Merge`. `Merge` first records converted locations on the original namespace object, then performs FST `local_rename` queries for each new location. On rename failure it removes newly added locations and restores quota accounting. On success it removes old non-tape locations, updates layout and optional ctime, then triggers resync for new locations.

## State and Persistence
The job mutates namespace metadata, physical FST file names, quota accounting, MGM stats, FST resync state, and optionally tape GC state. It uses the proc conversion path from `ConversionInfo` as the temporary destination. Status is held in an atomic enum and final errors in `mErrorString`.

## Dependencies and Integration Points
Heavily depends on `gOFS`, namespace locks and services, `FsView`, XrdCl copy/query APIs, EOS layout/checksum utilities, quota, tape GC, metadata prefetching, and connection pool helpers. `ConverterEngine` owns lifecycle and cleanup of the conversion proc file after the job finishes.

## Risks
- Merge spans namespace updates and remote FST renames without a single transaction; partial failure recovery removes metadata locations but cannot necessarily undo physical renames already completed.
- The original checksum comparison only detects checksum changes, not all metadata changes that could matter during conversion.
- `XrdOucErrInfo error` and `rootvid` in `DoIt` are unused after declaration.
- Callback success and failure both call `Cancel`, so callback semantics are not self-describing.
- Local rename timeout is fixed at 10 seconds, which may be fragile for slow FSTs.
- Quota removal happens before metadata retrieval in `Merge`; restoration paths exist for some failures but not every later failure.

## Test Signals
Test with fake namespace/FST services for TPC success, prepare failure, checksum drift, stripe mismatch, local rename failure after partial success, ctime update, quota restoration, tape file notification, and callback behavior. Integration tests require multi-FST EOS/XRootD setup.
