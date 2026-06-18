# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.c

Purpose: MMIO helper backend for Exynos3250-compatible JPEG hardware, also reused by Exynos5420 variant data. It programs reset, power, DMA issue counts, clock mode, raw input/output formats, dimensions, quant/Huffman table selectors, stride/offset, DMA addresses, coefficients, scaling, timer, interrupts, and start/restart.

Important APIs: `exynos3250_jpeg_reset()`, `exynos3250_jpeg_input_raw_fmt()`, `exynos3250_jpeg_output_raw_fmt()`, `exynos3250_jpeg_proc_mode()`, `exynos3250_jpeg_subsampling_mode()`, `exynos3250_jpeg_imgadr()`, `exynos3250_jpeg_stride()`, `exynos3250_jpeg_offset()`, `exynos3250_jpeg_dec_scaling_ratio()`, `exynos3250_jpeg_interrupts_enable()`, `exynos3250_jpeg_get_int_status()`, and `exynos3250_jpeg_compressed_size()`.

Control flow: `exynos3250_jpeg_device_run()` in `jpeg-core.c` resets and powers the block, configures DMA/clock/proc mode, then calls these helpers according to encode or decode mode. The IRQ path reads timer and JPEG interrupt status with these helpers, clears statuses, may restart after header interrupt, and reads compressed size/subsampling at completion.

State and persistence: no software-owned state. The helpers write volatile registers based on `s5p_jpeg_ctx` state supplied by the core.

Dependencies and integration: includes `jpeg-core.h`, `jpeg-regs.h`, and its public header. It maps V4L2 fourcc values to Exynos3250 register encodings for RGB/YUV packed and planar/semi-planar formats.

Risks: reset polls with fixed retry counts; failure is not returned to callers. Stride/offset calculations must match buffer layout and crop/downscale rules in the core. Unsupported fourcc falls through to zero encodings, relying on core format filtering.

Test signals: encode/decode for each Exynos3250 format, downscale ratios 1/2/4/8, crop offsets, RGB byte-swap variants, timer timeout handling, header interrupt restart, and Exynos5420 stream-error path.
