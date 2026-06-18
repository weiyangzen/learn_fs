# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-base.c

## Purpose
`microchip-isc-base.c` is the shared V4L2, media-controller, vb2, DMA, interrupt, control, and async-subdevice implementation for Microchip ISC and XISC capture devices. Product drivers provide format tables, register offsets, and hardware-specific callbacks while this file owns the capture device behavior.

## Important APIs, Types, and Functions
The vb2 path is implemented by `isc_queue_setup()`, `isc_buffer_prepare()`, `isc_start_streaming()`, `isc_stop_streaming()`, and `isc_buffer_queue()`. Format and media negotiation are handled by `isc_enum_fmt_vid_cap()`, `isc_try_fmt()`, `isc_set_fmt()`, `isc_link_validate()`, and `isc_find_format_by_code()`. Hardware programming is centralized in `isc_configure()`, `isc_set_pipeline()`, `isc_update_profile()`, `isc_crop_pfe()`, and `isc_start_dma()`. `microchip_isc_interrupt()` is exported for product drivers. Auto white balance uses `isc_set_histogram()`, `isc_awb_work()`, `isc_wb_update()`, and clustered V4L2 controls. Exported setup helpers include `microchip_isc_async_ops`, `microchip_isc_subdev_cleanup()`, `microchip_isc_pipeline_init()`, `isc_mc_init()`, `isc_mc_cleanup()`, and `microchip_isc_regmap_config`.

## Control Flow
Async completion initializes workqueues, mutexes, vb2 queues, controls, the video device, scaler links, and the media device. Opening the video node powers the bound subdevice and refreshes the active format. Media link validation reads the upstream subdevice format, validates it against supported ISC input formats, clamps dimensions, ensures capture dimensions match to prevent DMA overflow, decides whether direct dump is required, and activates the pipeline configuration. Streaming starts the media pipeline, starts the upstream subdevice, resumes runtime PM, programs PFE/RLP/DMA/pipeline/histogram registers, enables DMA-done interrupts, takes the first queued buffer, crops the PFE to the active frame, and starts DMA. The IRQ handler completes the current buffer, timestamps and sequences it, starts the next queued buffer, completes stop waiters, and schedules AWB work on histogram completion. Stop disables AWB, waits for frame completion, disables interrupts, releases runtime PM, stops the upstream subdevice, and returns outstanding buffers as errors.

## State and Persistence
`struct isc_device` holds all durable runtime state: active and trial V4L2 formats, active and trial pipeline configuration, current subdevice, DMA queue, current buffer, sequence number, stop flag, completion, AWB controls, histogram state, media device, scaler subdevice, and regmap fields for pipeline modules. Hardware register state is volatile and rebuilt on configure/start. There is no persistence across driver unload or power loss.

## Dependencies and Integration Points
The file depends on regmap MMIO, V4L2 controls/events/ioctls, media-controller graph APIs, async notifiers, vb2 DMA-contig, runtime PM, and product callbacks in `struct isc_device`. It integrates upstream with a single sensor/subdevice and internally with the scaler entity from `microchip-isc-scaler.c`.

## Risks and Edge Cases
The driver intentionally rejects frame-size mismatches at link validation because the PFE/DMA path could otherwise overrun buffers. Non-RAW sensors force direct dump because conversion pipeline stages require RAW Bayer input. AWB work races with frame DMA, so `awb_lock` and `awb_mutex` protect register updates and streaming-stop state; changes in this area must preserve that ordering. `isc_update_profile()` times out if no frame clocks the profile update. Error unwinding must return queued buffers to vb2 and keep media pipeline/runtime PM balanced.

## Test Signals
Exercise raw Bayer, YUV, RGB, and GREY input/output combinations; media link validation with mismatched sizes; vb2 streaming start/stop under queued and empty-buffer conditions; DMA-done interrupt sequencing; histogram/AWB auto and one-shot controls; runtime PM reference balance; and module builds for both SAMA5D2 ISC and SAMA7G5 XISC.
