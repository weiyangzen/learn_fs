# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro.h

## Purpose
Defines the central private interfaces for the Verisilicon Hantro VPU driver: hardware variants, V4L2/media-device function objects, per-device state, per-filehandle codec context, format descriptors, register helpers, decoded-buffer metadata, and exported helpers used by codec backends.

## Important APIs, Types, And Functions
Key types are `struct hantro_variant`, `struct hantro_dev`, `struct hantro_ctx`, `struct hantro_fmt`, `struct hantro_reg`, `struct hantro_decoded_buffer`, and `struct hantro_postproc_regs`. Inline helpers map V4L2/video objects to driver contexts, read/write encoder and decoder register windows, update masked register fields, fetch queued buffers, and select the decoder buffer address with or without postprocessing.

## Control Flow And State
`hantro_ctx` is the per-open state owner. It tracks encoder/decoder mode, sequence counters, negotiated source/destination/reference formats, controls, JPEG quality, bit depth, postprocessor need, selected codec ops, and a union of codec-specific hardware contexts. `hantro_dev` owns persistent device-wide resources: clocks, resets, mapped registers, V4L2/m2m/media devices, variant data, mutexes, IRQ lock, and watchdog work.

## Dependencies And Integration Points
The header binds Linux platform, V4L2, videobuf2 DMA-contig, media-controller, runtime codec headers from `hantro_hw.h`, and register IO primitives. Backend files include this header to share register helpers and buffer conventions.

## Risks And Test Signals
DMA addresses are truncated to 32 bits in `hantro_write_addr`, matching the driver mask; any future 64-bit DMA support must audit every caller. Postprocessor address selection changes decoded-buffer ownership, so regression tests should cover raw decode, postprocessed decode, and reference reuse. Compile coverage across enabled SoC variants is important because variant fields gate many optional paths.
