<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c

## Purpose

`hw/cdma_hw.c` provides the generation-specialized hardware implementation of CDMA operations included into each `host1x0N.c` build unit. It programs channel DMA registers, handles channel stop/freeze/resume, initializes timeout work, and implements timeout-specific MLOCK cleanup.

## Important APIs, Types, And Functions

- `push_buffer_init()` writes the RESTART opcode at the end of the pushbuffer.
- `cdma_start()`, `cdma_flush()`, and `cdma_stop()` program DMASTART/DMAPUT/DMAEND/DMACTRL and wait for queue drain.
- `cdma_timeout_restart()` restores DMAGET from a timeout recovery address and restarts DMA.
- `cdma_freeze()` stops command processing, stops CDMA, tears down the channel, and marks the CDMA torn down.
- `cdma_resume()` clears command-processor stop and restarts from a selected GET pointer.
- `cdma_timeout_handler()` dumps debug state, checks whether the syncpoint really timed out, freezes hardware, releases MLOCK if needed, and repairs the sync queue.

## Control Flow

Generic `cdma.c` calls these operations through `host1x_cdma_ops`. Start programs the circular pushbuffer base/end and initializes GET to PUT before enabling DMA. Stop waits for an empty sync queue before asserting DMASTOP. Timeout handling first freezes the command processor for a clean snapshot, verifies the syncpoint threshold is still incomplete, freezes/tears down the channel, releases any held MLOCK on Tegra234 classes, then delegates job-queue repair to `host1x_cdma_update_sync_queue()`.

## State And Persistence Behavior

Hardware state includes DMA pointers, DMACTRL, command-processor stop bits, channel teardown state, and common MLOCK registers on HW8. Software state mutates `cdma->running`, `cdma->torndown`, `last_pos`, and timeout initialization/client fields.

## Dependencies And Integration Points

This file relies on register macros supplied by the including generation hardware header and on `HOST1X_HW` for conditional code. It integrates with `cdma.c`, `debug.c`, syncpoint APIs, and channel timeout policy.

## Risks And Test Signals

Register offsets differ substantially before and after HW6; inclusion with the wrong hardware header would corrupt registers. Timeout MLOCK release is implemented only for specific Tegra234 engine classes and warns for unknown classes. Tests should cover start/flush/stop, timeout recovery, channel teardown/resume, 64-bit DMA register programming on HW6+, and class-specific MLOCK release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/cdma_hw.c -->
