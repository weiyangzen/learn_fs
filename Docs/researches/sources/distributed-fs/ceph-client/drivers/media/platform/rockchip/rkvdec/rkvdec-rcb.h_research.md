# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.h

Purpose: declares the RKVDEC RCB sizing contract and public helper API used by variant setup and codec backends.

Important APIs and types: `enum rcb_axis` selects `PIC_WIDTH` or `PIC_HEIGHT`; `struct rcb_size_info` stores an 8-bit multiplier and axis. Exported declarations cover allocation, free, count, size, and DMA address lookup for buffers in `struct rkvdec_ctx`.

Control flow: variant descriptors define arrays of `struct rcb_size_info`; streaming start passes those arrays to `rkvdec_allocate_rcb`. Codec backends call the accessors while filling register images, then stop-streaming calls `rkvdec_free_rcb`.

State and persistence: the header owns no state. It defines the shape of size metadata and exposes access to context-owned volatile RCB allocations.

Dependencies and integration points: includes Linux integer types and forward-declares `struct rkvdec_ctx`. It bridges core variant tables in `rkvdec.c`, allocation implementation in `rkvdec-rcb.c`, and VDPU381/VDPU383 H.264/HEVC register setup.

Risks: there is no include guard in this header, so repeated inclusion relies on harmless duplicate declarations. The `u8` multiplier bounds the supported size multiplier, which is currently enough for local tables but is part of the ABI between variant data and allocation logic.

Test signals: compile coverage for all RKVDEC variants and successful stream start on VDPU38x paths indirectly validate this header.
