# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-rotate.h

Purpose: defines the sun8i DE2 rotation register map, hardware format constants, size limits, and per-context/per-device state structures.

Important APIs and constants: includes global control, interrupt, input/output format, size, pitch, address registers, burst/mode constants, hardware format codes, `ROTATE_SIZE`, min/max dimensions, `struct rotate_ctx`, and `struct rotate_dev`.

Control flow: `sun8i_rotate.c` uses these definitions to configure one M2M rotation job, process interrupts, and manage runtime PM resources.

State and persistence: `rotate_ctx` stores per-file source/destination formats, control handler, hflip/vflip/rotate controls. `rotate_dev` stores platform-wide V4L2/video/M2M objects, MMIO base, clocks, reset, and mutex.

Dependencies and integration points: includes V4L2 controls, device, mem2mem, videobuf2, DMA-contig, and platform-device headers.

Risks: high address registers are always written as zero in the implementation, so DMA address width is a hardware/platform assumption. Rotation constants map directly to `rotate / 90`; control validation must stay aligned with that.

Test signals: register programming through real rotation jobs, 90/180/270-degree geometry validation, and high-DMA-address platform testing if applicable.
