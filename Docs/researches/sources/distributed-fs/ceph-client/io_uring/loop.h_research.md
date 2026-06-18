<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.h -->
# sources/distributed-fs/ceph-client/io_uring/loop.h

## Purpose
`loop.h` declares the io_uring loop-step interface. It defines the per-step parameters, callback result constants, a helper for detecting configured loop operations, and the `io_run_loop()` entry point.

## Important APIs, Types, and Functions
- `struct iou_loop_params` currently contains `cq_wait_idx`, a hint for the CQE index the loop should wait for.
- `IOU_LOOP_CONTINUE` and `IOU_LOOP_STOP` are valid loop-step return values.
- `io_has_loop_ops(ctx)` checks `ctx->loop_step` with `data_race()` because the enter path only needs a quick branch.
- `io_run_loop()` runs the loop under core locking.

## Control Flow
Callers use `io_has_loop_ops()` to decide whether to divert `io_uring_enter()` to loop mode. The loop implementation calls the configured `ctx->loop_step`, which fills `iou_loop_params` and returns continue or stop.

## State and Persistence Behavior
The header defines only transient step parameters. Persistent state is the function pointer in `io_ring_ctx`.

## Dependencies and Integration Points
It includes `io_uring_types.h` and is included by `io_uring.c` and `loop.c`. Any subsystem assigning `ctx->loop_step` must follow the return-value contract here.

## Risks and Edge Cases
- The unsynchronized helper is intentionally loose; the implementation must recheck the pointer under lock.
- `cq_wait_idx` is only a hint, so loop users must tolerate earlier wakeups.

## Test Signals
Build coverage and loop-mode runtime tests should verify the helper branch, valid stop/continue behavior, and early wake semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/loop.h -->
