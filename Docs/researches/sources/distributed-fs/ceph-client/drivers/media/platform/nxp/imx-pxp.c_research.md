# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.c

## Purpose
`imx-pxp.c` is a V4L2 memory-to-memory driver for the i.MX Pixel Pipeline hardware. It exposes scaling, color-space conversion, rotation, horizontal and vertical flip, and alpha-component output as a `/dev/video*` mem2mem device backed by contiguous DMA buffers.

## Important APIs, Types, and Functions
The core device state is split between `struct pxp_dev`, which owns the V4L2 device, video node, regmap, clock, interrupt lock, and `v4l2_m2m_dev`, and `struct pxp_ctx`, which tracks one open file handle, controls, queue formats, colorimetry, rotation, flip mode, and abort state. Queue state lives in `struct pxp_q_data`, and pixel format capabilities are listed in `formats[]`.

Important helpers include `find_format()`, `get_q_data()`, `pxp_read()`, `pxp_write()`, `pxp_v4l2_pix_fmt_to_ps_format()`, `pxp_v4l2_pix_fmt_to_out_format()`, and `pxp_v4l2_pix_fmt_is_yuv()`. `pxp_setup_csc()` programs CSC1 and CSC2 coefficients for YUV-to-RGB and RGB-to-YUV conversions across BT.601, Rec.709, BT.2020, and SMPTE 240M limited/full range choices. SoC-specific data-path setup is provided by `pxp_imx6ull_data_path_ctrl0()` and `pxp_imx7d_data_path_ctrl0()`. Runtime operation flows through `pxp_start()`, `pxp_device_run()`, `pxp_irq_handler()`, and `pxp_job_finish()`.

The V4L2 surface is implemented by `pxp_ioctl_ops`, `pxp_fops`, `pxp_qops`, and `m2m_ops`. Controls are `V4L2_CID_HFLIP`, `V4L2_CID_VFLIP`, `V4L2_CID_ROTATE`, and `V4L2_CID_ALPHA_COMPONENT`. Probe/remove are handled by `pxp_probe()` and `pxp_remove()` with OF compatibles `fsl,imx6ull-pxp` and `fsl,imx7d-pxp`.

## Control Flow
Probe allocates `pxp_dev`, reads platform match data, gets the `axi` clock, maps MMIO through regmap, requests the IRQ, enables the clock, performs `pxp_soft_reset()`, registers the V4L2 device, initializes the mem2mem core, and registers the video node. With media controller support enabled, it also creates and registers the media device entity for a video pixel formatter.

On open, the driver allocates a per-file `pxp_ctx`, creates the control handler, initializes default 640x480 formats, and creates the mem2mem context with `queue_init()`. Userspace negotiates output and capture formats through try/set ioctls. Width and height are clamped to 8-pixel aligned 8..4096 ranges, bytes-per-line and sizeimage are derived from format depth, and capture colorimetry is either inherited from source when no CSC is possible or mapped to defaults for conversion.

When both queues have buffers, `pxp_device_run()` selects the next source and destination buffers and calls `pxp_start()`. `pxp_start()` obtains DMA addresses, propagates timestamps and buffer flags, computes rotation-adjusted output geometry, configures planar and semiplanar buffer offsets, computes decimation and scale factors, writes output, processed-surface, background, color key, CSC, LUT, data-path, interrupt, and control registers, then starts the hardware. `pxp_irq_handler()` clears the completion interrupt and calls `pxp_job_finish()`, which returns both buffers as done and completes the mem2mem job.

## State and Persistence
Persistent kernel-visible state is in the V4L2 device registration and per-open contexts; all image-processing state is volatile per job and programmed into PXP registers. Buffer sequence counters live in `pxp_q_data` and reset at stream start. Register state is not restored across power loss beyond probe reset and per-job programming. The driver uses `dev_mutex` around file and queue operations and `irqlock` around buffer completion.

## Dependencies and Integration Points
The driver depends on V4L2 mem2mem, videobuf2 DMA-contig, media controller support when configured, regmap MMIO, platform OF matching, an `axi` clock, and an IRQ. It integrates with the register definitions in `imx-pxp.h` and accepts only DMA-contiguous MMAP or DMABUF buffers. Pixel formats map V4L2 FourCC values to PXP processed-surface and output format fields.

## Risks and Edge Cases
`pxp_device_run()` ignores the return value from `pxp_start()`, so a DMA address failure can leave a mem2mem job without explicit error completion. Scaling calculations divide by `dst_width - 1` and `dst_height - 1` in non-decimated paths, but the enforced minimum size makes zero divisors unlikely. Capture and output format capabilities are asymmetric for some FourCCs, so tests must cover both queues. CSC coefficients cover common colorimetry but not arbitrary YCbCr-to-YCbCr or RGB range conversions. Remove resets and clocks off the device but does not coordinate with active users beyond normal device unregister behavior.

## Test Signals
Useful validation includes probing both i.MX6ULL and i.MX7D compatibles, successful soft reset and version read, `v4l2-compliance` mem2mem coverage, format enumeration for capture/output-only asymmetries, streaming with RGB, packed YUV, semiplanar YUV, and planar YUV formats, rotation 90/270 geometry swaps, flip controls, alpha output, full and limited range CSC conversions, interrupt completion, queue stop returning pending buffers with error, and media-controller registration when enabled.
