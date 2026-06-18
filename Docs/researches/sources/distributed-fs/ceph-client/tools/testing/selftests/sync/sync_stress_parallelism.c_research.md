# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_parallelism.c

## Purpose
Tests sw_sync as a two-thread sequencing primitive on one shared timeline. It verifies that alternating fence waits and timeline increments can serialize writes to a shared counter for many iterations.

## Important APIs, Types, And Functions
Implements `test_stress_two_threads_shared_timeline()` and `test_stress_two_threads_shared_timeline_thread()`. Shared state is `test_data_two_threads` with `iterations`, `timeline`, and `counter`.

## Control Flow
The main test creates one timeline, initializes the counter and iteration count (`1 << 16`), then starts two pthreads with ids 0 and 1. Each thread repeatedly creates a fence for `i * 2 + thread_id`, waits forever for that value to be reached, validates the shared counter equals the expected turn value, increments the counter, advances the timeline by one to release the other thread, and closes the fence. After both threads join, the main test checks the counter reached `iterations * 2`.

## State And Persistence
The shared counter is not protected by a mutex; the test relies entirely on timeline/fence ordering for visibility and serialization. Kernel state is the shared timeline and per-iteration fences.

## Dependencies And Integration Points
Depends on pthread scheduling, the sw_sync timeline increment semantics, and `sync_wait(..., -1)` blocking until a fence signals.

## Risks
Because the counter is ordinary shared memory without atomic or mutex access, the test assumes the synchronization through syscalls is enough for memory visibility on target architectures. Any missed timeline increment deadlocks both threads. The long iteration count makes it good at finding races but expensive when the kernel stalls.

## Test Signals
Expected signals are every wait completing, the counter always matching the expected turn, and final counter value exactly `131072`.
