# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.h

Purpose: declares shared data structures and hardware helper prototypes for the STM32 DMA2D V4L2 mem2mem driver.

Important types and APIs: `enum dma2d_op_mode` models M2M, M2M with pixel format conversion, M2M blend, and register-to-memory modes. `enum dma2d_cmode` and `enum dma2d_alpha_mode` describe hardware color and alpha handling. `struct dma2d_fmt` maps V4L2 fourcc to depth and color mode. `struct dma2d_frame` stores dimensions, crop/offset fields, line offset, format, ARGB color, alpha mode, buffer size, and sequence. `struct dma2d_ctx` stores one file handle, source/capture/background frame configs, operation mode, controls, and colorimetry. `struct dma2d_dev` stores V4L2/video/m2m objects, locks, instance count, registers, clock, current context, and IRQ. The header declares `dma2d_start`, interrupt accessors, and foreground/background/output/common configuration helpers.

Control flow and integration: `dma2d.c` owns V4L2 policy and calls the prototypes implemented in `dma2d-hw.c`. Context and device structs are shared across queue callbacks, control callbacks, IRQ handling, and platform lifecycle.

State and risks: no standalone persistence. Risks are naming ambiguity between `cap` and `out`, unimplemented crop/background/blend fields becoming misleading API surface, and tight coupling between enum numeric values and hardware register encodings. Test signals are compile coverage for both source files, format negotiation tests that validate `size`, `line_offset`, and color mode, and IRQ/job scheduling tests that verify `dev->curr` lifetime.
