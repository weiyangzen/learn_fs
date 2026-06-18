# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_sw_fence.c

## Purpose
This file tests the i915 software fence primitive. It validates completion, dependency graphs, cycle detection, chains, many-to-one and one-to-many relationships, cross-workqueue signaling, timed fences, and wrapping of DMA fences with optional timeout behavior.

## Important APIs, Types, And Functions
- `alloc_fence()`, `free_fence()`, and `fence_notify()` create and destroy test fences while leaving memory ownership to the caller.
- Dependency tests include `test_self()`, `test_dag()`, `test_AB()`, `test_ABC()`, `test_AB_C()`, `test_C_AB()`, and `test_chain()`.
- `task_ipc` and `test_ipc()` validate use as an inter-thread synchronization primitive.
- `test_timer()` validates `timed_fence`.
- `alloc_dma_fence()`, `wrap_dma_fence()`, and `test_dma_fence()` test software fence waits on external DMA fences.
- `i915_sw_fence_mock_selftests()` registers all tests as mock subtests.

## Control Flow
Tests create fences, add await relationships with `i915_sw_fence_await_sw_fence_gfp()` or `i915_sw_fence_await_dma_fence()`, commit fences in controlled order, and inspect `i915_sw_fence_done()`. DAG tests intentionally try recursive and cyclic dependencies when DAG checking is enabled. IPC queues a work item that waits on one fence, updates a value, and commits another. Timer and DMA tests wait for delayed completion and then verify early/late signaling semantics.

## State And Persistence
All state is heap-allocated fence objects, DMA fences, workqueue/work structs, and timed fence timers. State is transient and freed at the end of each test. DMA fence tests signal the DMA fence on all failure paths to unblock wrappers.

## Dependencies And Integration Points
It depends on the i915 software fence implementation, Linux DMA fences, workqueues, completions, timers/jiffies, and the selftest subtest runner. The mock request tests also rely on software fences, making this file foundational for higher-level request coverage.

## Risks
Reference and notification ordering are critical: freeing before dependency completion would corrupt waiters. Some timing checks tolerate oversleep by skipping late timeout validation. DAG checks are conditional on `CONFIG_DRM_I915_SW_FENCE_CHECK_DAG`, so cycle coverage can be absent in some builds.

## Test Signals
Expected signals are early-not-done and later-done states, cycle insertion returning `-EINVAL`, ordered propagation through chains, worker value update only after input fence commit, timer not firing before target jiffies, and DMA timeout/non-timeout wrappers completing at the right events.
