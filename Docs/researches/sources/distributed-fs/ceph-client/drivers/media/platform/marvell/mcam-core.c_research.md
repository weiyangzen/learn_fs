# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.c

## Purpose
This file implements the shared Marvell CCIC camera core used by both Cafe and MMP platform wrappers. It owns V4L2 device behavior, async sensor binding, format negotiation, vb2 queue management, capture start/stop, frame interrupt processing, sensor clock control, power sequencing, and buffer handling across vmalloc, DMA-contiguous, and DMA scatter-gather modes.

## Important APIs, Types, And Functions
The exported platform-facing API is `mccic_register()`, `mccic_irq()`, `mccic_shutdown()`, `mccic_suspend()`, and `mccic_resume()`. Internal state is mostly `struct mcam_camera` from `mcam-core.h` plus `struct mcam_vb_buffer` and `struct mcam_dma_desc`. Format support is encoded in `mcam_formats[]`, mapping V4L2 fourccs to bytes-per-pixel, planar state, and media-bus codes.

Major internal functions include DMA setup/completion for vmalloc (`mcam_alloc_dma_bufs()`, `mcam_ctlr_dma_vmalloc()`, `mcam_frame_work()`), DMA-contig (`mcam_set_contig_buffer()`, `mcam_dma_contig_done()`), DMA-SG (`mcam_sg_next_buffer()`, `mcam_dma_sg_done()`, `mcam_sg_restart()`), hardware image configuration (`mcam_ctlr_image()`, `mcam_ctlr_configure()`), power and MIPI helpers, master clock `clk_ops`, vb2 callbacks, V4L2 ioctl handlers, file open/release, async notifier callbacks, and interrupt frame completion handling.

## Control Flow
`mccic_register()` validates or overrides the requested buffer mode, initializes mutex/state/default format, registers the async notifier, registers an `mclk` provider, and optionally preallocates vmalloc-mode coherent DMA buffers. When a sensor binds, `mccic_notify_bound()` resets/initializes the sensor, sets up vb2 according to buffer mode, clones the video-device template, and registers the video node.

Open powers the sensor and runtime PM, resets the camera, and marks hardware config needed. Format try/set delegates to the sensor pad format path, computes bytesperline/sizeimage, and marks controller configuration dirty. Streaming starts in `mcam_vb_start_streaming()`: if real buffers are not yet available for DMA modes it enters `S_BUFWAIT`; otherwise it resets counters and calls `mcam_read_setup()`. That function configures the sensor and controller if needed, enables or disables MIPI based on bus type, enables frame interrupts, sets `S_STREAMING`, and starts the controller unless SG restart is pending.

`mccic_irq()` is called by platform IRQ handlers with `dev_lock` held. It clears frame interrupts, records SOF bits, marks DMA active, stops the controller on SOF in SG mode, and completes frames only when EOF has a matching SOF. Completion updates sequence/frame counters and dispatches to the active buffer-mode completion callback. Stop streaming stops DMA with a long hardware settle wait and returns queued/active buffers as errors.

## State And Persistence
The core keeps a state machine (`S_NOTREADY`, `S_IDLE`, `S_FLAKED`, `S_STREAMING`, `S_BUFWAIT`), bit flags for valid frames, DMA active, config-needed, single-buffer fallback, SG restart, and SOF tracking, plus frame counters, vb2 buffer lists, active hardware buffers, default/current pix format, and current media-bus code. No state persists across module/device lifetime, but suspend/resume preserves logical streaming state and restarts if needed.

## Dependencies And Integration Points
The core depends on V4L2, V4L2 async, controls/events, vb2 memory backends, runtime PM, clock framework, and platform-supplied `mcam_camera` fields. Cafe and MMP wrappers supply register mapping, locks, device, chip ID, buffer mode, bus/MIPI parameters, IRQ calls, and optional platform power/DPHY callbacks. Sensor subdevices must support reset/init/power and pad format operations.

## Risks
The buffer-mode logic is complex. Vmalloc mode copies from internal coherent buffers in bottom-half work; DMA-contig reuses buffers when userspace underruns; SG mode must stop/restart the controller between frames and tracks `CF_SG_RESTART`. Frame completion relies on matching SOF/EOF bits; hardware that drops SOF or reports multiple frames can stress this logic. `mcam_ctlr_stop_dma()` uses a fixed 150 ms sleep and only logs if DMA remains active. Runtime PM is tied into the exported sensor clock, so clock consumers can power the controller unexpectedly. Error handling around `mcam_cam_configure()` adds return values and may mask which subdev operation failed.

## Test Signals
Build all vb2 backend combinations selected by Kconfig. Runtime coverage should exercise vmalloc, DMA-contig, and DMA-SG buffer modes; empty-buffer underrun behavior; SG restart after a later buffer arrives; format negotiation for packed, planar, RGB, and Bayer formats; read and streaming io modes; SOF/EOF interrupt ordering; stop streaming during active DMA; suspend/resume with open users and active streaming; and notifier bind/unbind. V4L2 compliance and stress streaming with low buffer counts are strong signals.
