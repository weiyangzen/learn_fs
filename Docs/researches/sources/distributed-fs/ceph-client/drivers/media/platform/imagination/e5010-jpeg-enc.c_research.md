# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.c

## Purpose
Implements a V4L2 mem2mem baseline JPEG encoder driver for Imagination E5010 hardware. It exposes YUV420/YUV422 semiplanar input formats, JPEG capture output, compression quality control, crop selection, vb2 queueing, JPEG header generation, IRQ completion, platform probe/remove, and runtime/system PM.

## Important APIs, Types, and Functions
Format table `e5010_formats[]` defines NV12/NV12M/NV21/NV21M/NV16/NV16M/NV61/NV61M output and JPEG capture. Ioctl handlers include querycap, enum/try/get/set format, enum framesizes, get/set selection, event subscription, and encoder command. Queue operations include `queue_init()`, `e5010_queue_setup()`, `e5010_buf_prepare()`, `e5010_buf_queue()`, `e5010_buf_finish()`, start/stop streaming, and `e5010_device_run()`. Control handling is via `V4L2_CID_JPEG_COMPRESSION_QUALITY`, `calculate_qp_tables()`, and `update_qp_tables()`. Platform entry points are `e5010_probe()` and `e5010_remove()`.

## Control Flow
Probe allocates/registers V4L2 and video devices, initializes mem2mem, maps `core` and `mmu` resources, requests IRQ, gets clock, enables runtime PM, and registers `/dev/video0`-style node. Open allocates `struct e5010_context`, creates mem2mem queues, initializes controls and default formats. Stream-on powers the device and calls `e5010_init_device()`. `e5010_device_run()` locks hardware, selects next src/dst buffers, copies metadata, updates QP tables when context or quality changed, computes crop offsets, programs DMA addresses and image parameters, sets output max size, and starts encoding. IRQ removes buffers, handles output-address error or picture done, marks EOS on last draining source buffer, sets capture payload to hardware output size plus header size, and finishes the mem2mem job. `e5010_buf_finish()` writes the JPEG header into the capture buffer after successful completion.

## State and Persistence
Device state in `struct e5010_dev` includes V4L2/mem2mem/video devices, MMIO bases, clock, mutex, hardware spinlock, and `last_context_run` for QP table caching. Per-file `struct e5010_context` holds output/capture queue data, crop, quality, QP tables, update flag, and control handler. No disk state exists.

## Dependencies and Integration Points
Uses V4L2 core, V4L2 mem2mem, vb2 DMA-contig, JPEG helper tables, media JPEG constants, runtime PM, platform OF matching (`img,e5010-jpeg-enc`), E5010 hardware helpers, and DMA API with a 32-bit mask.

## Risks
Capture header is written in `buf_finish()` after IRQ payload calculation, so capture buffers must be CPU-mapped and large enough for `HEADER_SIZE`. Crop adjustment logic contains suspicious corrections when crop exceeds bounds, and should be tested for right/bottom edge cases. The driver registers with fixed requested video nr 0, which can collide and fall back only if core permits. Runtime PM puts occur per queue stop and gets per queue start, so asymmetric stream-on/off order needs coverage. Error IRQ path can process both error and picture-done flags if both are set.

## Test Signals
`v4l2-compliance`, JPEG encode with each supported input format, quality control changes across contexts, crop tests for alignment and bounds, drain/EOS commands, output buffer too small error IRQ, streamoff during active job, suspend/resume with queued contexts, and JPEG header validation by decoding produced files.
