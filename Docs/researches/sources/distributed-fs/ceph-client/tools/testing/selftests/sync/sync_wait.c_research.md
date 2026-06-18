# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_wait.c

## Purpose
Tests waiting on a merged fence built from three independent timelines. It ensures merged fence status tracks each component independently and only becomes fully signaled after all timelines have reached their target values.

## Important APIs, Types, And Functions
Implements `test_fence_multi_timeline_wait()`. It uses three sw_sync timelines, three fences, two `sync_merge()` calls, `sync_fence_count_with_status()`, `sync_wait()`, and timeline increments.

## Control Flow
The test creates timelines A, B, and C, creates a fence at value 5 on each, merges them into one fence, and checks that the merged fence has three active points. It verifies immediate wait times out, then increments each timeline by 5 in sequence and checks active/signaled counts transition from 2/1 to 1/2 to 0/3. A final wait with timeout 100 must succeed before all fds and timelines are destroyed.

## State And Persistence
Kernel state is distributed across three timeline counters and the merged fence fd. Local state records active/signaled counts for assertions.

## Dependencies And Integration Points
Builds on `sync.c` helpers and complements the single-timeline merge tests by validating independent timeline composition.

## Risks
The second `sync_merge()` overwrites `merged` without closing the first merged fd, so the test may leak one fd in the child process. Return values from timeline increments are not asserted in this file, meaning a failed increment would surface indirectly through count mismatches.

## Test Signals
Expected signals are three active components before increments, per-timeline count transitions after each increment, and a positive wait result once all three components are signaled.
