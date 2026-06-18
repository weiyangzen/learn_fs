# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_error.rs

## Purpose
This file defines typed errors for rebuild and snapshot rebuild operations using SNAFU. It is the common error vocabulary for job lifecycle, descriptor validation, I/O, task channels, frontend/backend liveness, nexus range locks, URI parsing, and snapshot URI setup.

## Important APIs, Types, And Functions
`RebuildError` includes job existence/lookup, copy buffer allocation, invalid ranges/maps, same bdev, bdev handle/open failures, read/write/verify I/O failures, state operation errors, pending-state conflicts, range lock/unlock failures, invalid URI, dropped frontend/backend, closed task channel, and wrapped `SnapshotRebuildError`. `SnapshotRebuildError` covers missing local bdev, missing remote URI, non-replica bdevs, and URI bdev open failure. `From<SnapshotRebuildError> for RebuildError` wraps snapshot errors.

## Control Flow
Other modules construct these variants through SNAFU contexts or direct errors. The variants carry enough source context for display strings and higher-level conversions through `VerboseError`.

## State, Persistence, And Dependencies
This file stores no state. It depends on `BdevError`, `CoreError`, SPDK descriptor/DMA errors, and `snafu`.

## Integration Points
Rebuild frontend methods, backend manager, descriptor I/O, task scheduling, nexus range locking, and snapshot rebuild builders all return these errors. RPC layers can map them through higher-level error conversion.

## Risks
`RebuildError` derives `Clone`, so embedded source errors must remain cloneable or the type contract changes. Some variants use generic errno-like meanings in display text but do not directly encode retryability. Snapshot errors are flattened under a single rebuild variant, so callers that need exact snapshot failure categories must inspect the source.

## Test Signals
Tests should assert important display strings, SNAFU source preservation, snapshot-to-rebuild conversion, clone compatibility after adding variants, and error mapping in callers that translate to tonic status or errno.
