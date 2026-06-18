# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.h

Purpose: defines the sun8i deinterlace register map, format constants, size limits, and core per-context/per-device state structures.

Important APIs and types: contains many `DEINTERLACE_*` register offsets and bit helpers for module enable, frame control, bypass, buffers, strides, formats, interrupts, thresholds, scaling coefficients, and sizes. Defines `struct deinterlace_ctx` and `struct deinterlace_dev`.

Control flow: the implementation uses these constants to program one deinterlace job and runtime initialization. Context and device structures are the bridge between file handles, M2M scheduling, vb2 buffers, and platform resources.

State and persistence: `deinterlace_ctx` persists per open file and tracks formats, flag buffers, previous buffer, field state, and aborting. `deinterlace_dev` persists per platform device and owns V4L2, video, M2M, MMIO, clocks, reset, and mutex state.

Dependencies and integration points: includes V4L2 device, mem2mem, videobuf2 V4L2/DMA-contig, and platform-device headers. It is private to `sun8i-di.c`.

Risks: register constants are numerous and mostly unvalidated at compile time. Min/max dimensions and NV12/NV21-only assumptions are baked into the implementation. Buffer address registers take full DMA addresses without high-register support, so platform DMA address width must match hardware capability.

Test signals: compile coverage plus hardware runs that exercise buffer addresses, field counters, writeback strides, and scaling coefficient registers.
