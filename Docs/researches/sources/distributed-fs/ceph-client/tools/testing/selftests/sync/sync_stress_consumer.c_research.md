# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_stress_consumer.c

## Purpose
Implements a multi-producer/single-consumer stress test for sw_sync. It exercises large numbers of fence creations, waits, timeline increments, merges, and cross-thread coordination under file descriptor pressure.

## Important APIs, Types, And Functions
Important functions are `test_consumer_stress_multi_producer_single_consumer()`, `mpsc_producer_thread()`, `mpcs_consumer_thread()`, and `busy_wait_on_fence()`. Shared state lives in `test_data_mpsc` with iteration count, thread count, counter, a consumer timeline, producer timeline array, and a pthread mutex.

## Control Flow
The top-level test creates one consumer timeline and five producer timelines, initializes global shared state, starts five producer threads, and runs the consumer loop in the main thread. Producers repeatedly create fences on the consumer timeline and wait until the consumer releases each iteration, then increment a protected shared counter and advance their producer timeline. The consumer creates one fence per producer timeline for the current iteration, merges them into a single fence, waits until all producers have advanced, verifies the counter equals `threads * iteration`, and advances the consumer timeline to release producers for the next round.

## State And Persistence
State persists in global `test_data_mpsc` across all threads. The counter is protected by a mutex for increments but read by the consumer without taking the mutex after synchronization through producer fences. Kernel state includes six timelines and many transient fences/merged fences.

## Dependencies And Integration Points
Depends on pthreads, sync helper functions, and enough process file descriptors for many transient fences. The test runner isolates it in a child process.

## Risks
This test is sensitive to fd limits and scheduling. `busy_wait_on_fence()` repeatedly queries fence info and can be CPU-heavy. Some thread functions return integer values through a `void *` pthread signature cast, which is conventional in this test tree but not type-clean. The branch choosing wait mode uses `(iterations + id) % 8`, so with the current constants it varies by producer id rather than by loop iteration.

## Test Signals
Signals are no fence error status, producer waits completing, merged producer fences signaling each iteration, shared counter exactly matching the expected producer count, and no fd exhaustion during `1 << 12` iterations.
