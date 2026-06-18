# sources/distributed-fs/ceph-client/lib/test_ref_tracker.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_ref_tracker.c` is a targeted self-test for the reference tracker infrastructure. It intentionally leaves references outstanding and attempts a double free to exercise diagnostic reporting. The source was read as a complete 116-line file.

## Important APIs, Types, and Functions

The file owns static `struct ref_tracker_dir ref_dir`, `tracker[20]`, a timer, and `test_ref_timer_done`. Macro `TRT_ALLOC` generates 19 noinline allocation wrapper functions so stack traces are distinct. Important routines are `alloctest_ref_tracker_free`, `test_ref_tracker_timer_func`, `test_ref_tracker_init`, and `test_ref_tracker_exit`.

## Control Flow

On load, the module initializes a tracker directory, starts a timer that allocates `tracker[0]` with `GFP_ATOMIC`, allocates `tracker[1]` through `tracker[19]` with distinct wrappers, frees trackers 2 through 19, attempts to free tracker 2 again, waits until the timer allocation completes, then exits the tracker directory while tracker 0 and tracker 1 remain allocated. This is expected to trigger ref-tracker warnings.

## State and Persistence Behavior

All tracker state is module-static and exists only during initialization. The test deliberately does not cleanly free all refs before `ref_tracker_dir_exit` because leak reporting is the behavior under test. The timer uses an atomic flag to synchronize completion with init.

## Dependencies and Integration Points

Direct includes are init, module, delay, ref_tracker, slab, and timer headers. Integration points are `ref_tracker_dir_init`, `ref_tracker_alloc`, `ref_tracker_free`, `ref_tracker_dir_exit`, timer callback context, `GFP_KERNEL`, and `GFP_ATOMIC`.

## Risks and Edge Cases

This module is designed to produce warnings, so a noisy load is expected. It depends on timer execution and uses polling with `msleep(1)`. Because it intentionally leaks tracked references into `ref_tracker_dir_exit`, it should not be treated like a normal pass/fail leak-free test.

## Test Signals

Expected signals are diagnostic warnings for the double free and for unfreed tracker 0 and 1. Module init returns `0`; the pass condition is that ref-tracker diagnostics appear and the module does not crash.
