# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_stats.rs

## Purpose
This file defines rebuild statistics and history record structures used by running jobs and post-completion reporting.

## Important APIs, Types, And Functions
`RebuildStats` records total/recovered/transferred/remaining blocks, percent progress, blocks per task, block size, total and active tasks, start time, partial flag, and optional end time. `Default` initializes zero counters and current start time. `HistoryRecord` stores child URI, source URI, final stats, final state, and end time, and derefs to `RebuildStats`.

## Control Flow
The backend manager computes `RebuildStats` from task counters and backend descriptors. `RebuildStates::set_final_stats` sets the end time. `RebuildJob::history_record` wraps final stats with URI/state metadata.

## State, Persistence, And Dependencies
These are in-memory data structures. They depend on `chrono` and `RebuildState`.

## Integration Points
RPC/status paths can expose these fields to control-plane clients. History records are lightweight extracts for completed jobs.

## Risks
`progress` is an integer percentage and may lose precision. Defaults use the current timestamp even for placeholder stats, which can be misleading if returned after backend failure. `HistoryRecord` hides `final_stats` from outside the crate except through deref.

## Test Signals
Validate stats calculations in the backend manager, final end-time assignment, default values, history record creation, and partial rebuild `is_partial` propagation.
