<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc -->
# sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc

## Purpose

`FsckEntry.cc` implements repair logic for one fsck finding on one file id. It gathers MGM metadata and FST-local metadata, classifies good and bad replicas or stripes, updates namespace metadata when safe, runs drain-transfer-style repair jobs, drops bad replicas, resyncs FST metadata, and reports success or failure to the fsck engine.

## Important APIs, Types, and Functions

The constructor maps `FsckErr` values to repair functions and creates a `DrainTransferJob` factory. Metadata collection is handled by `CollectMgmInfo()`, `CollectAllFstInfo()`, `CollectFstInfo()`, and `GetFstFmd()`. Repair paths are `Repair()`, `RepairMgmXsSzDiff()`, `RepairFstXsSzDiff()`, `RepairInconsistencies()`, `RepairReplicaInconsistencies()`, `RepairRainInconsistencies()`, and `RepairBestEffort()`. Post-actions are `ResyncFstMd()` and `NotifyOutcome()`.

## Control Flow

`Repair()` records MGM stats, fetches MGM metadata from QuarkDB, treats missing MGM metadata as an orphan/ghost cleanup, removes detached files, gathers FST info for all known locations plus the reported fsid, rejects tape-replica files, and dispatches either the reported repair operation or a priority sequence of MGM checksum/size, FST checksum/size, and consistency repairs. Replica checksum/size repairs compare MGM checksum/size, FST stored metadata, and disk stat size to select good and bad fsids. Consistency repairs diverge for replica layouts and RAIN layouts. RAIN logic handles unregistered, missing, differential, and stripe errors with registration, drop, or reconstruction jobs. Best-effort repair selects a reference replica, commits its checksum/size through verifystripe or test-mode mutation, then rebuilds enough replicas.

## State and Persistence Behavior

Each instance owns `mMgmFmd`, a map of FST file info, reported error, best-effort flag, repair dispatch map, repair factory, and QDB client. Persistent effects include namespace file metadata updates, replica location add/remove, dropped replicas, verifystripe checksum/size commits, drain-transfer repair copies, FST resync queries, MGM stat counters, and QuarkDB fsck-set removals through `NotifyOutcome()`.

## Dependencies and Integration Points

The implementation depends on global `gOFS`, `FsView`, namespace services and prefetchers, `MetadataFetcher`, XRootD client filesystem/stat/query APIs, drain transfer jobs, layout helpers, FST FMD parsing, MGM stats, and `proc_fs_dropghosts`.

## Risks and Edge Cases

Repair is destructive in several paths: `DropReplica()`, namespace location removal, detached file removal, and best-effort metadata commits. Best-effort can choose the largest available replica when no MGM match exists, which is operationally useful but risky. Many paths assume `mFsidErr` is non-empty. Network timeouts and missing FST metadata influence whether replicas are considered bad or unrepaired. RAIN over-replication and too many corrupt stripes require manual handling. Destructor removes the file id from the global tracker, so lifecycle ownership matters.

## Test Signals

Tests should cover missing MGM metadata orphan cleanup, detached file removal, tape-replica refusal, checksum/size match and mismatch matrices, unscanned replicas, zero-size no-disk case, replica under/over-replication, RAIN missing/unregistered/stripe errors, best-effort enabled/disabled paths, FST query timeout/error parsing, and `NotifyOutcome()` updates for stripe and diff-replica errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc -->
