# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.c

Purpose: implements a V4L2 memory-to-memory driver for the Allwinner sun8i deinterlace unit with scaling support for NV12/NV21 input and output.

Important APIs and functions: module entry is `module_platform_driver(deinterlace_driver)`. Key paths include `deinterlace_device_run`, `deinterlace_irq`, `deinterlace_init`, V4L2 format ioctls, vb2 queue callbacks, `deinterlace_open`, `deinterlace_release`, platform probe/remove, and runtime resume/suspend.

Control flow: open allocates a per-file `deinterlace_ctx`, initializes default interlaced output and progressive capture formats, and creates a V4L2 M2M context. Streaming the output queue resumes PM and allocates two coherent flag buffers. The mem2mem scheduler runs only when at least one source and two destination buffers are ready. `device_run` programs input/output DMA addresses, line strides, format selection, previous-frame reference, scaling factors, neutral coefficients, field count, interrupts, and starts writeback. The IRQ handles writeback completion, marks each destination buffer done, alternates fields for a second pass when needed, stores the latest source as previous reference, completes the prior previous buffer, and finishes the M2M job.

State and persistence: per-context state includes source/destination formats, two flag buffers, previous source buffer, first/current field, and abort flag. Device state includes V4L2 device, video node, M2M scheduler, MMIO base, clocks, reset, and mutex. Hardware state is reinitialized on runtime resume and per job.

Dependencies and integration points: depends on V4L2 mem2mem core, videobuf2 DMA-contig, platform IRQ/MMIO resources, runtime PM, common clocks, reset, and coherent DMA. The compatible is `allwinner,sun8i-h3-deinterlace`.

Risks: two destination buffers are required for job readiness, reflecting field processing; userspace with too few capture buffers will stall. The previous-frame buffer is retained across jobs and must be returned on queue cleanup. Coefficient poll timeout result is ignored. Only NV12/NV21 are exposed. `kzalloc_obj` is used instead of the common `kzalloc(sizeof(*ctx), ...)`, so build environment support for that helper is assumed in this tree.

Test signals: v4l2-compliance for mem2mem ioctls, NV12/NV21 conversion/deinterlacing with two capture buffers, interlaced field order TB/BT, resize paths, abort/streamoff cleanup, runtime PM balancing, and IRQ writeback error handling.
