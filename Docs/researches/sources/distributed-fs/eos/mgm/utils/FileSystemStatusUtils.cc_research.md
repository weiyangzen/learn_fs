# sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.cc

## Purpose
Implements helpers for applying drain-completion/failure status and querying filesystem status by group.

## Important APIs, types, and functions
`ApplyDrainedStatus()` sets drain status to drained, clears drain counters, and when not shutting down marks the durable `configstatus` as `empty`. `ApplyFailedDrainStatus()` marks drain failed and records failed-job count. `FsidsinGroup()` returns fsids in a group matching active/drain status. `GetGroupFsStatus()` returns a map from fsid to active/drain statuses.

## Control flow
Each function locks `FsView::gFsView.ViewMutex`, resolves groups or ids through global views, reads or updates the target `FileSystem`, and logs missing groups or status changes.

## State and persistence behavior
`FileSystemUpdateBatch` applies local status and counter updates. `ApplyDrainedStatus()` also calls `StoreFsConfig(fs)` and sets durable `configstatus=empty` when MGM is not shutting down.

## Dependencies and integration points
Uses `FsView`, global `gOFS`, EOS logging, `FileSystemUpdateBatch`, `ActiveStatus`, and `DrainStatus`. It is used by drain workflows and group-selection logic.

## Risks and test signals
`FsidsinGroup()` accepts status parameters but currently compares against hard-coded `kOnline` and `kNoDrain`, ignoring the arguments. `ApplyDrainedStatus()` calls `StoreFsConfig(fs)` before `fs->applyBatch(batch)`, so tests should confirm durable status ordering is intentional. Tests should cover missing groups, null filesystem targets, shutdown versus non-shutdown drain completion, failed-drain counters, and argument-sensitive filtering.
