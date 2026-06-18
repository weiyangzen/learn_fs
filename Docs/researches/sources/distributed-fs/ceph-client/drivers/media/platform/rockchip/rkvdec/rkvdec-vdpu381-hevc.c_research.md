# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-hevc.c

Purpose: implements the VDPU381 HEVC stateless decode backend. It converts HEVC SPS/PPS/scaling/RPS/decode controls into VDPU381 parameter packets, private tables, reference-address registers, and common decode controls.

Important APIs and functions: exported `rkvdec_vdpu381_hevc_fmt_ops`; private functions `assemble_hw_pps`, `set_ref_valid`, `config_registers`, `rkvdec_write_regs`, `rkvdec_hevc_validate_sps`, `rkvdec_hevc_start`, `rkvdec_hevc_stop`, `rkvdec_hevc_run`, and `rkvdec_hevc_try_ctrl`. Key state types are `rkvdec_hevc_priv_tbl` and `rkvdec_hevc_ctx`.

Control flow: start validates 4:2:0 8-bit/10-bit SPS constraints and allocates a coherent table with CABAC data. Each run gathers V4L2 controls, assembles scaling lists and PPS/tile data, optionally assembles short/long-term RPS, fills VDPU381 register blocks, posts source/destination buffers, schedules the watchdog, and enables decode. Missing extended SPS RPS controls cause a rate-limited warning but do not stop decode on this variant.

State and persistence: `ctx->priv` owns coherent parameter/RPS/scaling/CABAC memory plus caches for scaling matrix and SPS short-term RPS controls. Current frame register images are rebuilt per job. Hardware state exists only while clocks and MMIO programming are active.

Dependencies and integration points: depends on V4L2 HEVC stateless controls, `rkvdec-hevc-common`, CABAC tables, RCB buffer accessors, vb2 DMA-contig, and `rkvdec-vdpu381-regs.h`. Selected by the RK3588 variant table.

Risks: missing RPS controls can produce wrong frames rather than an immediate error. Tile-column/row and bitfield packing must match hardware exactly. Reference validity is set through a switch with no default behavior for out-of-range IDs. DMA address and COLMV offsets must match the capture buffer layout from core format setup.

Test signals: HEVC conformance streams with tiles, scaling lists, short/long-term references, 8-bit and 10-bit Main profiles, resolution changes requiring format renegotiation, and stress runs checking timeout and IOMMU behavior.
