# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-hevc.c

Purpose: implements the VDPU383 HEVC backend. It prepares a VDPU383-specific combined SPS/PPS global packet, RPS/scaling/CABAC private tables, reference address registers, and link-block decode start sequence.

Important APIs and functions: exported `rkvdec_vdpu383_hevc_fmt_ops`; helpers `set_column_row`, `set_pps_ref_pic_poc`, `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, `rkvdec_hevc_validate_sps`, and start/stop/run/try-control hooks. Main state is `rkvdec_hevc_ctx` with a coherent `rkvdec_hevc_priv_tbl`.

Control flow: start validates HEVC SPS constraints and allocates private DMA memory with CABAC data. Run requires extended SPS long/short-term RPS controls when the SPS advertises those sets; unlike VDPU381, missing RPS returns `-EINVAL` to avoid IOMMU faults. It then assembles scaling, PPS/tile/POC data, RPS, register images, posts buffers, schedules the watchdog, and starts decode through VDPU383 link registers.

State and persistence: per-context caches track scaling matrix and short-term RPS data. Per-frame state includes current POC, reference POCs, valid-bit masks, tile dimensions, and DMA addresses. All state is volatile and released at stream stop.

Dependencies and integration points: depends on V4L2 HEVC stateless controls, RKVDEC HEVC common helpers, RCB accessors, VDPU383 register definitions, DMA-contig buffers, and core variant operations including VDPU383 matrix flattening.

Risks: tile dimension packing via paired 12-bit values is sensitive to HEVC PPS limits and hardware expectations. The loop over active DPB entries skips the final array slot by using `ARRAY_SIZE(dpb) - 1`, which should be validated against hardware/reference-list expectations. Missing RPS is intentionally fatal here due to observed IOMMU-fault risk.

Test signals: RK3576 HEVC conformance covering tiles, non-uniform tile spacing, Main/Main10, scaling matrices, short/long-term RPS, malformed/missing controls, and link interrupt/timeout behavior.
