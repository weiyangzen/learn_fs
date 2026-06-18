# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_fence.c

## Purpose
Tests basic fence wait and merge semantics on a single sw_sync timeline. It validates timeout behavior before a fence reaches its target value, signaling after enough timeline increments, and merged-fence behavior where the merged fence tracks the maximum sync point on one timeline.

## Important APIs, Types, And Functions
Implements `test_fence_one_timeline_wait()` and `test_fence_one_timeline_merge()`. Key calls are `sw_sync_timeline_create()`, `sw_sync_fence_create()`, `sw_sync_timeline_inc()`, `sync_wait()`, `sync_merge()`, and `sync_fence_count_with_status()`.

## Control Flow
The wait test creates a fence at value `5`, verifies immediate zero-timeout waits return timeout while the timeline is below 5, increments by `1` and then `4`, and expects readiness once the target is reached. It then increments further to ensure already-signaled fences remain waitable. The merge test creates fences at values 1, 2, and 3, merges them, verifies active counts, then advances the timeline one step at a time and checks the merged fence remains active until the last component has signaled.

## State And Persistence
The persistent state is in kernel timeline progression and fence fds. Local variables retain the merged fd chain and are closed at the end.

## Dependencies And Integration Points
Uses the sync helper ABI and is run by `sync_test.c`. It is a baseline for the later multi-timeline and stress tests.

## Risks
The merge test has repeated assertions against `a` where messages mention `b`, `c`, and `d`; this limits diagnostic precision and may miss per-fence count regressions before the later `d` checks. Failed intermediate `sync_merge()` calls could leak earlier fds or feed invalid fds into the next merge.

## Test Signals
Expected signals are `sync_wait(..., 0)` returning `0` for unsignaled fences, returning positive for signaled fences, active count dropping only as timeline values reach component sync points, and merged fence status becoming fully signaled at the maximum component value.
