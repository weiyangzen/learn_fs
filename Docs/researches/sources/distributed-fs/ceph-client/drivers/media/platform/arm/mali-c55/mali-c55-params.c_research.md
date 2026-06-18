# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-params.c

Purpose: Implements the Mali-C55 metadata-output video node that accepts userspace ISP parameter buffers and writes validated parameter blocks into the next frame's register context.

Important APIs/functions: Exports `mali_c55_params_write_config()`, `mali_c55_params_init_isp_config()`, registration and unregistration. Block handlers program sensor offset, AEXP histograms and weights, digital gain, AWB gains/config, mesh shading config, and mesh shading selection. It defines parameter block type metadata for V4L2 ISP validation.

Control flow: vb2 prepare validates buffer size and block layout using V4L2 ISP helpers after copying userspace content into an internal `kvmalloc` scratch buffer. Queued param buffers are listed. On ISP SOF path, `mali_c55_params_write_config()` pops one buffer, walks its blocks by size, dispatches to handlers, marks the buffer done, and leaves absent buffers as "reuse previous/default config". `mali_c55_params_init_isp_config()` programs windowing and safe defaults before first stream/config writes.

State and persistence: Params state stores video node, vb2 queue, lock, and queued scratch buffers. The actual hardware-facing state is the shared context register shadow in `mali_c55->context`.

Dependencies and integration: Uses V4L2 meta output, V4L2 ISP parameter validation, vb2 DMA-contig, media controller, runtime PM, ISP pipeline readiness, and register definitions.

Risks: AEXP histogram weights compute the last value/address but do not write the final register, which looks suspicious. Handlers trust prior validation for type/size. Config updates are frame-bound and silently skipped when no params buffer is queued.

Test signals: Meta format ioctls, malformed block rejection, each parameter block disable/enable behavior, per-frame buffer completion sequence, default config after no params, pipeline start synchronization with capture/stats, and register-write traces for AEXP/AWB/LSC.
