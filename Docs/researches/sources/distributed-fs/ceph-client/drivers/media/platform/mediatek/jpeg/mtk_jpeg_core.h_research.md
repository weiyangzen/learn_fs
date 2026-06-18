# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.h

## Purpose
This header defines the core data model and variant contract for the MediaTek JPEG V4L2 mem2mem driver. It is shared by the core, parser, and encode/decode hardware support files.

## Important APIs, Types, And Constants
Constants define driver name, format direction flags, min/max dimensions, default JPEG buffer size, hardware timeout, maximum EXIF size, and low-address alignment mask. `enum mtk_jpeg_ctx_state` models decode/encode context state (`INIT`, `RUNNING`, `SOURCE_CHANGE`). `struct mtk_jpeg_variant` is the OF-selected behavior table containing clocks, formats, vb2 ops, IRQ/reset/m2m/ioctl callbacks, queue defaults, multi-core flag, worker callback, and 34-bit DMA support.

`struct mtk_jpeg_src_buf` extends a vb2 buffer with frame number, list node, bitstream size, parsed decode parameters, and current context pointer. `struct mtk_jpeg_hw_param` captures active source/destination/context for a hardware component. `struct mtk_jpegenc_comp_dev` and `struct mtk_jpegdec_comp_dev` describe per-core encode/decode component devices with registers, clocks, IRQ, timeout work, hw state, and lock. `struct mtk_jpeg_dev` is the master device object. `struct mtk_jpeg_fmt`, `struct mtk_jpeg_q_data`, and `struct mtk_jpeg_ctx` describe formats, queue state, and per-open state.

## Control Flow And State
The header has no runtime control flow. It defines how control flow is parameterized: variant callbacks choose encode versus decode, single-core versus multi-core, and SoC-specific hardware behavior. State ownership is split between the master device, per-component hardware devices, per-file contexts, per-queue format data, and per-source buffers.

## Dependencies And Integration Points
The header depends on Linux clocks/interrupts and V4L2/vb2 headers, and includes `mtk_jpeg_dec_hw.h` for decode parameter types. It is consumed by `mtk_jpeg_core.c` and component hardware implementations, which must agree on `mtk_jpeg_hw_param`, component device layout, and variant callback semantics.

## Risks
Structure fields are concurrency-sensitive: `hw_state` and component parameters are protected by spinlocks, while queue/context fields are protected by the device mutex and m2m framework. The same `mtk_jpeg_src_buf` type is used for source buffers and, in multi-core code, to attach frame metadata to destination buffers, so buffer struct sizing and container assumptions must match queue setup. Adding formats or variants requires consistent updates to format flags, default fourccs, queue plane counts, and hardware helper support.

## Test Signals
Build all source files that include this header. Static review should verify all fields documented in variants are initialized by each OF match table. Runtime tests should validate context state transitions, multi-core component state accounting, and per-buffer decode parameter lifetime across qbuf, device run, IRQ, timeout, and streamoff.
