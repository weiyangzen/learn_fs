# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-h264.c

Purpose: implements the VDPU383 H.264 backend for RK3576-class RKVDEC hardware. It uses a newer link/function register split and a different global parameter packet from VDPU381.

Important APIs and functions: exported `rkvdec_vdpu383_h264_fmt_ops`; private helpers `set_field_order_cnt`, `set_dec_params`, `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, start/stop/run/try-control hooks, and private H.264 SPS/PPS/table/context structures.

Control flow: start validates SPS and allocates a coherent private table with CABAC data. Run builds H.264 reference lists, scaling data, hardware PPS, buffer indices, and RPS. Register configuration fills common fields, per-codec stream/stride/global length fields, reference/COLMV/payload addresses, RCB offset+size pairs, and auxiliary table base addresses. Decode is started by programming link timeout, IP enable, and decode-enable registers.

State and persistence: `ctx->priv` owns coherent auxiliary memory, reference-list storage, and a VDPU383 register image. Per-frame DPB POC and field flags are stored in the hardware PPS packet rather than the VDPU381 parameter registers. State is released on stream stop.

Dependencies and integration points: depends on V4L2 H.264 helpers, RKVDEC H.264 common code, RCB manager, CABAC table, `rkvdec-vdpu383-regs.h`, vb2 DMA-contig, and the VDPU383 variant table.

Risks: this path writes both reference base and payload-state base arrays, increasing address-programming surface. RCB register entries include size and address, so allocation-size bugs can affect hardware bounds. PPS fields are large packed bitfields, and helper functions manually enumerate all 16 DPB POC entries.

Test signals: H.264 decode on RK3576 hardware, field-picture and long-term-reference conformance, streams with scaling matrices and many DPB entries, link interrupt completion, timeout handling, and DMA/IOMMU fault monitoring.
