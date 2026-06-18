# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/null.c

## Purpose
This file implements the synthetic `null` ublk target. It completes I/O without backing storage, while exercising normal completion, zero-copy, auto buffer registration, fallback registration failure, DMA alignment, and segment limit reporting.

## Important APIs, Types, and Functions
`ublk_null_tgt_init()` sets a 250 GiB device with basic, DMA, and segment params. `__setup_nop_io()` prepares `IORING_OP_NOP` with injected result and fixed-buffer flags. `null_queue_zc_io()` registers buffer, submits NOP, and unregisters. `null_queue_auto_zc_io()` submits a fixed-buffer NOP. `ublk_null_queue_io()` chooses normal, zc, or auto-zc behavior. `ublk_null_io_done()` aggregates CQEs. `ublk_null_buf_index()` can return an invalid index to force fallback.

## Control Flow
On normal non-zc I/O, the target immediately completes with requested byte count. On zero-copy paths, it queues io_uring NOP operations that inject a completion result and optionally wrap explicit buffer register/unregister commands. Completion ignores skipped successful register CQEs, records failures, and commits when all target SQEs are done.

## State and Persistence
No persistent data exists. Runtime state is per-I/O target counters and buffer indexes.

## Dependencies and Integration Points
It depends on io_uring NOP injected-result behavior, ublk params, target callbacks, and tests for zero-copy, auto buffer registration, safe stop, update size, balancing, and feature behavior.

## Risks
NOP fixed-buffer flags are guarded by local definitions in case headers lag kernel support. Auto-zc fallback intentionally returns invalid buffer indexes, so behavior depends on kernel fallback handling.

## Test Signals
Tests inspect sysfs DMA/segment limits, run fio over null devices, verify auto-zc fallback, check update-size and safe-stop, and trace per-thread I/O distribution.
