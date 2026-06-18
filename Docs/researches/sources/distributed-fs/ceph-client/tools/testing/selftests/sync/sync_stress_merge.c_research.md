# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_merge.c

## Purpose
Stress-tests sync-file merging across many timelines by randomly generating thousands of sync points, merging them into one fence, and checking the final merged fence contains one outstanding point per touched timeline.

## Important APIs, Types, And Functions
Implements `test_merge_stress_random_merge()`. It uses `rand()`, `srand(time(NULL))`, arrays of 32 timelines and latest sync points, `sw_sync_fence_create()`, `sync_merge()`, `sync_fence_size()`, `sync_wait()`, and `sw_sync_timeline_inc()`.

## Control Flow
The test creates 32 timelines and an initial fence, then performs 32k iterations. Each iteration selects a random timeline and random sync point, tracks the maximum sync point seen for that timeline, creates a temporary fence, merges it into the aggregate fence, and destroys the old fds. After the loop it counts touched timelines, checks the aggregate fence size equals that count, advances each touched timeline to its tracked maximum while verifying the aggregate is still unsignaled before each increment, and finally expects the aggregate fence to signal.

## State And Persistence
Local arrays hold timeline fds and the latest required sync point per timeline. Kernel fence state is repeatedly replaced by a new merged fd, and only the latest aggregate survives each iteration.

## Dependencies And Integration Points
Depends on sw_sync merge coalescing by timeline and sync point, and on the helper layer reporting accurate fence sizes. It is the broadest merge coverage in the sync suite.

## Risks
The random seed makes exact coverage non-reproducible. Very large random sync points are passed directly to `sw_sync_timeline_inc()`, so integer range and cumulative counter behavior matter. The test may leak or mis-handle fds if a merge fails mid-loop, because the code continues to replace `fence` after each merge assertion point.

## Test Signals
Key signals are aggregate fence size equaling the number of timelines touched, aggregate wait timing out before all required increments, and successful wait after all timelines have advanced to their max sync point.
