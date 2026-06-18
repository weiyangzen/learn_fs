# sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.cc

## Purpose
Implements the MGM replication/creation tracker. It creates tag files for newly created files, removes them once the expected replica count is reached, periodically scans stale tracker entries, cleans abandoned atomic uploads, and optionally triggers layout/space conversion hooks on creation, injection, or access.

## Important APIs, types, and functions
`GetValidLocation()` selects the first non-zero, non-tape filesystem location. The constructor sets root identity and starts an assisted background thread. `Create()` makes a dated tracker directory and tag file. `Access()` checks conversion-on-access policy. `Commit()` removes the tag after replica count reaches layout stripe count and can trigger creation/injection conversion. `ConversionPolicy()` and `ConversionSizePolicy()` read space config. `Prefix()` maps file ctime to `mPath/YYYY/MM/DD/`. `getOptions()` reads default-space tracker config. `backgroundThread()` refreshes enable/conversion state and calls `Scan()`. `Scan()` lists tracker entries, reports status, removes completed/missing tags, cleans old empty directories, and deletes stale atomic target files.

## Control flow
On create, a tag file named by hex fid is stored under the date prefix. On commit, temporary atomic names are ignored; otherwise a file whose disk replica count matches its layout has its tag removed. Conversion hooks build a `/proc/user` file-convert command when configured policy and size filters allow it. The background thread waits for namespace boot, checks default-space `tracker` and `policy.conversion` settings, runs only on the master, and periodically scans the tracker tree.

## State and persistence behavior
Persistent state is represented by namespace tag files under `mPath`, their dated parent containers, and possible deletion of atomic upload files. Conversion jobs are submitted through `ProcCommand`. In-memory state is `mEnabled`, `mConversionEnabled`, root `mVid`, `mPath`, and the assisted thread.

## Dependencies and integration points
Uses global `gOFS`, `eosView`, `eosFileService`, `FsView::gFsView`, namespace locks, `ProcCommand`, `Resolver`, `Prefetcher`, layout helpers, and XRootD error/string types. It integrates with file creation/commit/access paths and default-space configuration.

## Risks and test signals
`Scan()` appends to `out` even when the tracker is disabled without checking `out` for null, which is risky for cleanup callers if disabled. Size-policy parsing uses `std::stol()` without local exception handling. `Access()` has a missing `break` after the `>` policy case, causing the default warning path to run too. Tests should cover disabled cleanup scans, malformed size policies, atomic-file cleanup, missing fids, replica-count thresholds with tape locations, conversion command formation, master-only background behavior, and tag directory cleanup age.
