# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.c

## Purpose
`imx-vdoa.c` implements the i.MX6 Video Data Order Adapter helper used by CODA workflows that need hardware-assisted video data reordering, especially tiled or VPU-oriented source layout into linear V4L2 capture formats. It is a platform driver plus exported helper API for clients that create a VDOA context, configure dimensions and output format, submit one DMA transfer, and wait for completion.

## Important APIs, Types, and Functions
The exported API is `vdoa_context_create`, `vdoa_context_configure`, `vdoa_device_run`, `vdoa_wait_for_completion`, and `vdoa_context_destroy`. Internal state is split between `struct vdoa_data` for device-wide MMIO, clock, and current context, `struct vdoa_ctx` for per-client completion and job counters, and `struct vdoa_q_data` for source/destination geometry. `vdoa_probe` binds the DT node, sets a 32-bit DMA mask, maps registers, acquires the clock, and installs the threaded IRQ.

## Control Flow
Clients allocate and configure a context, then call `vdoa_device_run(ctx, dst, src)`. The function serializes with an existing `curr_ctx` by waiting for it, stores the new context, reinitializes completion, programs control, frame size, input/output base addresses, strides, chroma offsets, and enables transfer/error interrupts before writing `VDOASRR_START`. The IRQ disables interrupts, acknowledges `VDOAIST`, logs transfer errors or spurious interrupts, increments `completed_job`, and completes the waiter.

## State and Persistence
Device state is transient and MMIO-backed. `curr_ctx` serializes one in-flight transfer; `submitted_job` and `completed_job` guard completion waits. Context creation enables the VDOA clock and destruction waits for an active transfer before disabling the clock and freeing memory.

## Dependencies and Integration
The driver depends on platform resources, DT compatible `fsl,imx6q-vdoa`, `clk`, `dma-mapping`, completions, IRQ threading, and V4L2 pixel format constants. It integrates with CODA through `imx-vdoa.h` exports and with the kernel device model through `module_platform_driver`.

## Risks and Test Signals
Risks include weak global serialization with no explicit lock around `curr_ctx`, fixed 300 ms timeout, 32-bit DMA address truncation into `u32`, strict width/height multiple-of-16 validation, and limited format validation despite an NV21 branch in run setup. Test with concurrent context users, timeout/error IRQ injection, NV12 and YUYV transfers, invalid dimensions, stream teardown during transfer, and runtime module unload.
