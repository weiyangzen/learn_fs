# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c

## Purpose
Manages shared command queue state for Octeon hardware engines, especially PKO and DMA queues, using bootmem metadata and FPA-backed command buffers.

## Important APIs, Types, And Functions
The exported `__cvmx_cmd_queue_state_ptr` points at the `cvmx_cmd_queues` named bootmem block. Main APIs are `cvmx_cmd_queue_initialize()`, `cvmx_cmd_queue_shutdown()`, `cvmx_cmd_queue_length()`, and `cvmx_cmd_queue_buffer()`.

## Control Flow
Initialization creates or finds the global bootmem state, validates queue id/depth/pool/buffer size, detects compatible prior initialization, requires FPA to be enabled, allocates the first command buffer, and records its physical base. Shutdown refuses queues with pending commands, locks the queue, frees its buffer, and clears the base pointer. Length dispatches by queue class to PKO or NPEI doorbell CSRs.

## State, Persistence, And Dependencies
Queue state persists in bootmem and is shared across cores. Buffers come from FPA. Ordering uses `CVMX_SYNCWS`; hardware counters come from PKO/NPEI/PEXP CSRs.

## Integration Points
PKO configuration uses this module for every output queue. DMA length reporting reads NPEI queue counters.

## Risks
FPA must be initialized first. Length reporting for several engine types is stubbed as zero. PKO length reads have weak serialization around `CVMX_PKO_REG_READ_IDX`.

## Test Signals
Verify idempotent setup returns `ALREADY_SETUP`, invalid parameters fail, shutdown rejects non-empty queues, and PKO doorbell counts match queued commands.
