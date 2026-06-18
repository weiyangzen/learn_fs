# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-h264.c

Purpose: implements the VDPU381-specific stateless H.264 backend for RKVDEC. It translates V4L2 H.264 controls, DPB state, reference lists, scaling lists, and CABAC/RPS tables into the register and auxiliary-memory format expected by RK3588-class VDPU381 hardware.

Important APIs and functions: exported format ops are `rkvdec_vdpu381_h264_fmt_ops`. Internal helpers include `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, `rkvdec_h264_start`, `rkvdec_h264_stop`, `rkvdec_h264_run`, and `rkvdec_h264_try_ctrl`. Private structures define hardware SPS/PPS packets, `rkvdec_h264_priv_tbl`, and `rkvdec_h264_ctx`.

Control flow: start validates the active SPS and allocates a coherent private table containing CABAC tables. Run builds V4L2 P/B reference lists, assembles scaling list, PPS/SPS, reference buffer indices, and RPS, fills common/codec/address/high-POC register blocks, posts the mem2mem request, schedules a hardware-derived watchdog, then starts decode through `VDPU381_REG_DEC_E`.

State and persistence: per-stream state is `ctx->priv`, containing a coherent private table, reference-list cache, and a register image. Per-frame state is rewritten before each run. No persistent storage exists beyond DMA buffers and context lifetime.

Dependencies and integration points: depends on V4L2 H.264 helpers, vb2 DMA-contig addresses, RKVDEC H.264 common helpers, CABAC tables, RCB accessors, and VDPU381 register definitions. It is selected by `vdpu381_coded_fmts` in `rkvdec.c`.

Risks: the PPS packet uses PPS ID as an array index and assumes userspace-provided control values are validated by common helpers. Reference fallback to the current destination buffer hides unused DPB entries but makes address bugs hard to spot. RCB order must match hardware. Large dimensions rely on timeout and stride arithmetic staying in range.

Test signals: V4L2 stateless H.264 decode on RK3588, conformance clips covering IDR/P/B frames, long-term references, scaling matrices, field pictures, and high resolutions; watchdog timeout/error IRQ behavior; DMA/IOMMU fault absence.
