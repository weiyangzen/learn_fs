# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.c

## Purpose
This file implements the V4L2 mem2mem core for MediaTek JPEG hardware. It supports single-core and multi-core encode/decode variants, exposes JPEG and raw YUV formats, parses JPEG headers for decode resolution and output format, manages vb2 multiplanar queues, controls runtime PM/clocks, dispatches work to hardware, handles interrupts/timeouts, and registers the platform driver for several MediaTek compatibles.

## Important APIs, Types, And Functions
Format tables `mtk_jpeg_enc_formats[]` and `mtk_jpeg_dec_formats[]` describe JPEG, NV12M, NV21M, YUYV, YVYU, YUV420M, and YUV422M support with sampling, alignment, plane count, and direction flags. Variant tables (`mt8173_jpeg_drvdata`, `mtk_jpeg_drvdata`, `mtk8195_jpegenc_drvdata`, `mtk8195_jpegdec_drvdata`) select formats, vb2 ops, mem2mem ops, ioctl ops, default queue formats, IRQ handlers, reset functions, worker functions, multi-core mode, and 34-bit support.

Key functions include format helpers `mtk_jpeg_enum_fmt()`, `mtk_jpeg_try_fmt_mplane()`, `mtk_jpeg_s_fmt_mplane()`, event/selection handlers, decode qbuf/header parsing, vb2 callbacks, single-core device runs `mtk_jpeg_enc_device_run()` / `mtk_jpeg_dec_device_run()`, multi-core workers `mtk_jpegenc_worker()` / `mtk_jpegdec_worker()`, IRQ handlers `mtk_jpeg_enc_irq()` / `mtk_jpeg_dec_irq()`, timeout work, queue initialization, file open/release, probe/remove, and PM hooks.

## Control Flow
Probe allocates `mtk_jpeg_dev`, stores OF match variant data, populates child platform devices, initializes either single-core MMIO/IRQ/clocks or multi-core waitqueue/workqueue state, registers V4L2, initializes the m2m device with variant ops, allocates/registers the video device, and enables runtime PM.

Open allocates `mtk_jpeg_ctx`, initializes work, done queue, file handle, m2m context, controls for encoder variants, and default queue formats. Userspace negotiates multiplanar output/capture formats. Decode output queueing parses the JPEG header with `mtk_jpeg_parse()`, stores per-source decode parameters, emits a source-change event on first valid header, updates queue data, and transitions the context state from `INIT` to `RUNNING` or `SOURCE_CHANGE`.

Single-core encode/decode `device_run()` obtains source/destination buffers, resumes runtime PM, schedules timeout work, resets hardware, writes source/destination/config registers, and starts the hardware. Decode refuses to run when a queued JPEG implies resolution/format change; it emits a source-change event and waits for userspace streamoff acknowledgment. IRQ handlers cancel timeout work, remove buffers, set payload sizes, mark buffer state done or error, finish the m2m job, and put runtime PM. Multi-core variants queue context work; workers select an idle component device under a hardware lock, wait on `hw_wq` if all cores are busy, program the selected component, and finish the scheduler job while completion is later handled by component hardware code through shared buffer metadata.

## State And Persistence
Device state includes mutex, hardware lock, V4L2/m2m/video objects, variant pointer, single-core register base and timeout work, multi-core component arrays, waitqueue, `hw_rdy`, and hardware index. Context state includes output/capture queue data, `MTK_JPEG_INIT/RUNNING/SOURCE_CHANGE`, encoder controls, work item, frame numbering, and encode done queue. Per-source buffers store bitstream size and parsed decode parameters. No state persists beyond open/device lifetime.

## Dependencies And Integration Points
The core depends on V4L2 mem2mem, vb2 DMA-contig, runtime PM, clock bulk APIs, OF platform population, MediaTek JPEG encode/decode hardware helpers, and the JPEG decode parser. It exposes `V4L2_CAP_STREAMING | V4L2_CAP_VIDEO_M2M_MPLANE` and handles source-change events required by stateful decode workflows.

## Risks
Stateful decode depends on userspace honoring source-change events and streamoff sequencing. `mtk_jpeg_buf_prepare()` can set JPEG capture payload to `sizeimage + MTK_JPEG_MAX_EXIF_SIZE` when EXIF is enabled, so queue size validation must stay consistent. Error paths in `device_run()` and workers must remove and complete exactly the buffers they acquired; otherwise m2m queues can hang or double-complete. Multi-core workers use retry loops and `hw_rdy` accounting; mismatched increment/decrement or interrupted waits can starve hardware. Timeout work assumes current context and buffers still exist. Runtime PM and clock cleanup differ between single-core bulk clocks and component-device clocks.

## Test Signals
Build all compatibles. Run V4L2 compliance for encoder and decoder nodes, including multiplanar queue setup, controls, crop/compose selection, event subscription, and encoder/decoder commands. Runtime tests should encode YUYV/NV12M/NV21M to JPEG, decode JPEG to YUV420M/YUV422M, handle resolution changes midstream, validate EXIF APP1 sizing, inject invalid JPEG headers, trigger hardware timeout, suspend/resume while jobs are queued, and stress multi-core encode/decode with parallel contexts.
