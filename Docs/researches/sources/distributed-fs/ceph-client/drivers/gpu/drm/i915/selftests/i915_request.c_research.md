# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_request.c

## Purpose
This file is the main request selftest suite. It validates mock request lifecycle and fence waiting, live request submission across engines, cancellation and reset behavior, breadcrumb signaling under concurrency, and performance characteristics of request dispatch, context switching, preemption, completion, and multi-engine throughput.

## Important APIs, Types, And Functions
- Public entries are `i915_request_mock_selftests()`, `i915_request_live_selftests()`, and `i915_request_perf_selftests()`.
- Mock tests include `igt_add_request()`, `igt_wait_request()`, `igt_fence_wait()`, `igt_request_rewind()`, and `mock_breadcrumbs_smoketest()`.
- Live tests include `live_nop_request()`, `live_empty_request()`, `live_all_engines()`, `live_sequential_engines()`, `live_parallel_engines()`, `live_cancel_request()`, and `live_breadcrumbs_smoketest()`.
- Cancellation helpers cover inactive, active, completed, and reset-backed non-preemptable requests.
- Perf helpers include timestamp/semaphore command emitters, `measure_*()` latency probes, `perf_request_latency()`, `perf_series_engines()`, and `perf_parallel_engines()`.
- Structs `smoketest`, `smoke_thread`, `parallel_thread`, `perf_stats`, `perf_series`, and `p_thread` hold per-run concurrency and measurement state.

## Control Flow
Mock tests create a mock GEM device, acquire runtime PM, and run basic request/fence scenarios. Breadcrumb smoke tests spawn kthread workers that allocate batches of requests across many contexts, gate submission through software fences, await DMA fences, and verify all request fences are signaled. Live tests iterate UABI engines, use `igt_live_test_begin/end` to enforce idle/reset invariants, create empty or recursive batches, submit requests concurrently or sequentially, and resolve recursive batches to let GPU execution finish. Cancellation tests use `igt_spinner` to create inactive/active/completed/hung requests and check fence errors and follow-up request progress. Perf tests pin contexts, disable heartbeats, pin RPS frequency, emit status-page timestamp commands, compute filtered cycle deltas, and print throughput/busy/runtime summaries.

## State And Persistence
The suite creates contexts, requests, fences, batches, VMAs, kthread workers, runtime PM wakerefs, QoS requests, and temporary engine property changes. State is expected to be fully released after each test. Some failure paths wedge the GT intentionally to avoid continued execution on corrupted or hung hardware. Perf tests temporarily disable c-states, heartbeat, and force high GPU frequency.

## Dependencies And Integration Points
The file depends on request, engine, context, ring, breadcrumb, scheduler, software fence, live-test, spinner, flush, mock GEM, runtime PM, and GT clock APIs. It integrates with all three selftest lanes: mock, live, and perf registries. It also relies on `i915_random` for randomized context/order coverage.

## Risks
This is high-blast-radius test code because it manipulates real engine queues, heartbeats, resets, and low-level ring commands. Kthread synchronization and reference handling must be exact to avoid leaked requests or dangling fences. Timing tests are sensitive to hardware generation, clock conversion, CPU latency, and engine wedging. Cancellation/reset tests intentionally exercise paths that can hang the GPU if arbitration or reset behavior regresses.

## Test Signals
Correctness signals include expected wait timeouts before submission, successful waits after submission, fence signaled bits, request completion state, preserved ordering across engines, cancelled fence error `-EINTR`, no unexpected GPU reset inside live sections, and clean flush after cancellation. Perf signals are printed latency, busy, runtime, and count summaries; fatal measurement failures wedge the GT and return errors.
