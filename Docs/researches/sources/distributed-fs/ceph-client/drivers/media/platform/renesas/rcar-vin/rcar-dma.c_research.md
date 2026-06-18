# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-dma.c

## Purpose
`rcar-dma.c` handles VIN register programming, crop/scale/compose hardware setup, vb2 queue operations, DMA-contiguous capture buffers, IRQ-driven frame completion, stream start/stop, channel routing, and runtime alpha updates.

## Important APIs, Types, And Functions
The private `struct rvin_buffer` wraps `vb2_v4l2_buffer`. Public sibling-file APIs are `rvin_dma_register()`, `rvin_dma_unregister()`, `rvin_start_streaming()`, `rvin_stop_streaming()`, `rvin_set_channel_routing()`, `rvin_set_alpha()`, `rvin_scaler_gen2()`, `rvin_scaler_gen3()`, and `rvin_crop_scale_comp()`. Core internal functions include `rvin_setup()`, `rvin_capture_start()`, `rvin_capture_stop()`, `rvin_irq()`, `rvin_mc_validate_format()`, `rvin_set_stream()`, `rvin_fill_hw_slot()`, and vb2 queue callbacks.

## Control Flow
Registration creates the `v4l2_device`, initializes locks/lists/hardware slots, configures a DMA-contiguous vb2 queue, and requests the VIN IRQ. On vb2 stream start, a scratch buffer is allocated and `rvin_start_streaming()` validates/enables the upstream media pipeline, resets sequence, fills three hardware slots from queued buffers or scratch memory, programs VIN registers, applies crop/scale/compose, and starts continuous capture. IRQ handling acknowledges status, emits frame-sync events on VSYNC, finds the completed hardware slot, timestamps and completes the vb2 buffer if present, increments sequence, and refills the slot. Stop repeatedly disables capture until hardware reports inactive, stops upstream streaming, disables interrupts, returns hardware buffers as error, frees scratch memory, and returns queued buffers.

## State And Persistence
State is in `struct rvin_dev`: active pixel format, crop/compose rectangles, media bus code, queued vb2 list, three hardware slots, scratch buffer DMA address, sequence, running flag, alpha, and cached CHSEL. `qlock` protects buffer/hardware/sequence/running fields. Register state is reprogrammed at stream start and modified dynamically for selection and alpha.

## Dependencies And Integration Points
The file depends on vb2 DMA-contiguous memory, V4L2 events, media pipeline helpers, upstream subdev stream APIs, runtime PM for CHSEL writes, and shared format helpers from `rcar-v4l2.c`. It is called by `rcar-core.c` during probe/remove and by `rcar-v4l2.c` through vb2/file operations.

## Risks
The scratch buffer hides underruns by dropping frames, so tests must watch sequence gaps and debug logs. Hardware buffer addresses must satisfy 128-byte alignment after compose offsets; violations trigger WARN and skipped slot update. Format validation is complex across interlaced/alternate fields, scaling, NV12 alignment, RAW formats, CSI vs parallel input, and Gen3/Gen4 limitations. In `rvin_start_streaming()`, `vin->running` is set after `rvin_capture_start()` even if `rvin_capture_start()` fails after upstream stream enable, so error-path behavior deserves scrutiny. Stop waits bounded retries and logs if hardware stays active.

## Test Signals
Exercise all supported pixel formats, RAW8/RAW10 paths, NV12 channel restrictions, scaling/no-scaling paths, compose offsets, interlaced and alternate fields, buffer underrun with scratch use, IRQ frame completion order, stream start validation failures, streamoff buffer return states, CHSEL writes under runtime PM, and alpha update while streaming for ARGB formats.
