# sources/control-plane/mayastor/io-engine/src/core/mod.rs

## Purpose
Acts as the main public facade for core SPDK/io-engine abstractions and shared error/status types.

## Important APIs, Types, and Functions
- Re-exports bdev, block device, descriptor, device event, environment, reactor, lock, share, snapshot, and runtime APIs.
- `VerboseError` formats an error chain.
- `CoreError` is the central Snafu error enum for bdev open, I/O dispatch/completion, sharing, reactor config, DMA, statistics, PTPL, snapshot, wipe, and crypto errors.
- `ToErrno` maps `CoreError` to POSIX errno values for API boundaries.
- `IoCompletionStatus`, `LvolFailure`, and `IoSubmissionFailure` normalize completion domains.
- `PAUSING` and `PAUSED` are global pause counters.
- `MayastorFeatures` and `MayastorBugFixes` expose feature/bugfix capability state.

## Control Flow and State
This file mostly defines contracts. `ToErrno` is used when control-plane or C-facing layers need errno-like errors. `IoCompletionStatus::from(NvmeStatus)` maps no-space/capacity-exceeded into `LvolError::NoSpace`; all other NVMe status values remain protocol-specific.

State is limited to exported atomics and feature structs initialized elsewhere.

## Dependencies and Integration Points
Every core consumer imports through this facade. It links `NvmfError`, SPDK status types, snapshot traits, share traits, and module visibility decisions.

## Risks and Test Signals
`CoreError` variants are user-visible through gRPC status mapping and logs, so changes have broad compatibility impact. Errno mappings must stay consistent with callers. Tests should verify error-to-errno mapping, no-space status conversion, re-export availability under feature flags, and error-chain formatting.
