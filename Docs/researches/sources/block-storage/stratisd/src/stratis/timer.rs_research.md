# File Research: sources/block-storage/stratisd/src/stratis/timer.rs

## Purpose

Runs periodic background checks for pool and filesystem usage.

## Main Types and Behavior

- `check_pool_and_fs` loops forever, calling engine pool and filesystem event processing with `None` to indicate timed checks rather than DM events.
- D-Bus builds send background signals for produced diffs.
- Min/non-D-Bus builds ignore returned diffs.
- Sleeps 10 seconds between checks.
- `run_timers` spawns the check loop and awaits it.

## Integration Points

Started by `stratis/run.rs` as one of the daemon’s long-running tasks.

## Notable Semantics

Because the spawned loop never normally returns, `run_timers` only exits on task failure or cancellation.
