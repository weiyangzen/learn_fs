# sources/control-plane/mayastor/io-engine/src/rebuild/mod.rs

## Purpose
This is the rebuild module root. It declares the rebuild submodules, re-exports the public job/state/stats/map types, and holds shared constants and helpers.

## Important APIs, Types, And Functions
Public exports include `BdevRebuildJob`, `NexusRebuildJob`, `NexusRebuildJobStarter`, `RebuildJob`, `RebuildJobOptions`, `RebuildVerifyMode`, `RebuildMap`, `RebuildState`, `RebuildStats`, and `SnapshotRebuildJob`. `SEGMENT_TASKS` is the per-job concurrency count and `SEGMENT_SIZE` is derived from `SPDK_BDEV_LARGE_BUF_MAX_SIZE`. `WithinRange` validates nested ranges. `shutdown_snapshot_rebuilds` stops all snapshot rebuilds. `parse_url` maps URL parse errors into `RebuildError`.

## Control Flow
Most logic lives in child modules. The module-level shutdown helper collects forced stop receivers from all snapshot rebuild jobs and awaits them. `parse_url` is a small compatibility wrapper around `url::Url::parse`.

## State, Persistence, And Dependencies
No state is stored here beyond constants. It depends on SPDK constants, URL parsing, and child modules.

## Integration Points
Other io-engine code imports rebuild jobs and state from this module rather than individual submodules. Shutdown paths use `shutdown_snapshot_rebuilds` to drain outstanding snapshot copy work.

## Risks
`SEGMENT_TASKS` and `SEGMENT_SIZE` are global policy knobs; changing them affects memory use, concurrency, and copy granularity across all rebuild variants. `WithinRange` rejects empty ranges and overflow-prone ranges, so callers must use exclusive-end ranges correctly.

## Test Signals
Validate range containment edge cases, URL parse error mapping, snapshot rebuild shutdown behavior with running/stopped jobs, and exported API compatibility for downstream modules.
