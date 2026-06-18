# sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.cc

## Purpose

`InFlightTracker.cc` implements reporting and throttling calculations for the in-flight request tracker. The corresponding header handles most request accounting inline; this file formats per-user request state and computes stall delays when per-user or global thread limits are exceeded.

## Important APIs, Types, and Functions

- `InFlightTracker::PrintOut(bool monitoring)` emits a table of active users, thread counts, active sessions, limits, stall counts, stall time estimates, and overload status.
- `InFlightTracker::getStallTime(uid_t uid, size_t& limit)` estimates a bounded randomized stall delay based on active sessions and the relevant limit.
- `InFlightTracker::ShouldStall(uid_t uid, bool& saturated, size_t& threads_used)` checks per-user and global thread limits and returns a stall duration in seconds, or zero if the request should proceed.

## Control Flow

`PrintOut()` selects human-readable or monitoring-oriented table formats, snapshots current per-uid in-flight counts with `getInFlightUids()`, queries `Access::ThreadLimit()` and `Mapping::ActiveSessions()`, and classifies each uid as `pool-OL`, `user-OL`, `user-LIMIT`, or `user-OK`.

`ShouldStall()` first gets user and global limits with the non-enforcing/lookup form of `Access::ThreadLimit(..., false)`. If the per-user limit is greater than one and the uid's in-flight count exceeds it, the method increments stall accounting, marks `saturated` if the global pool is also over limit, and returns `getStallTime(uid, limit)`. If the user is not over limit but the global pool is over limit, it increments stalls for the uid and returns a stall time based on global active sessions. Otherwise it returns zero.

`getStallTime()` derives a base from `2.0 * sessions / limit`, clamps it to the range 1..60, picks a random value in that range, and returns half the base plus the random component.

## State and Persistence Behavior

The file updates in-memory stall counters through `incStalls(uid)` and reads in-memory request counts. There is no persistent state. Stall behavior depends on live process state in `eos::common::Mapping::ActiveSessions()` and `Access::ThreadLimit()`.

## Dependencies and Integration Points

The implementation integrates with MGM access policy (`mgm/access/Access.hh`), EOS identity/session mapping (`eos::common::Mapping`), random utility helpers (`common::getRandom`), and table formatting (`TableFormatterBase`, `TableData`, `TableCell`). It is used anywhere request admission needs to display or enforce in-flight request pressure.

## Risks and Edge Cases

- `threads_used` is set to `limit` rather than the actual current count, which may surprise callers expecting observed usage.
- Limit comparison uses `>` for stalling but `PrintOut()` labels `user-OL` at `>= limit`; behavior and status text differ at exactly the limit.
- `getStallTime()` returns at least one second even when the computed load is tiny and the caller has already decided stalling is required.
- Randomized stall time makes exact behavior harder to test unless the random helper is controllable.
- `PrintOut()` snapshots maps, but status values can change immediately after formatting because request accounting is concurrent.

## Test Signals

Tests should cover no-stall, user-limit stall, global-limit stall, combined saturation, stall counter increments, output status at below/near/at/above limits, and deterministic stall-time behavior with a mocked random source or bounded assertions.
