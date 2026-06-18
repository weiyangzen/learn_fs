# File Research: sources/block-storage/thin-provisioning-tools/src/copier/report.rs

This file implements `CopyProgress` adapters for copier operations.

`IgnoreProgress` is a no-op implementation used by tests or callers that do not need progress reporting. `ProgressReporter` wraps a shared `Report` and a mutex-protected `AccumulatedStats` structure. `update()` computes temporary progress including an in-flight batch, while `inc_stats()` commits completed batch stats into the accumulator.

Important behavior:
- Tracks total blocks, copied blocks, read errors, and write errors.
- Updates the report subtitle only when either error counter is nonzero.
- Uses `checked_div(...).unwrap_or(100)` so zero total blocks produce 100% progress.
- Designed for concurrent copier threads through `Arc<Report>` and `Mutex`.

Integration points:
- Depends on `crate::copier::{CopyProgress, CopyStats}`.
- Uses `crate::report::Report` for UI/progress display.
- Used by copier frontends to surface copy progress and error counts.

Risks and notes:
- Mutex poisoning is not recovered; `unwrap()` will panic after a prior panic inside the lock.
- Progress percentage truncates to integer percent and casts to `u8`.
