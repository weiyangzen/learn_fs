# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_1_sar2130p.h

Purpose: this header defines `dpu_sar2130p_cfg`, the DPU 9.1 hardware catalog for SAR2130P. It is structurally close to SM8550 and feeds the same KMS/RM/encoder/CRTC consumers.

Important data: capabilities include source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The catalog has six CTLs, four QSEED 3.3.2 VIG pipes, six DMA pipes, six LMs, four DSPPs, six normal pingpongs, two CWB pingpongs, four merge blocks, four DSC slices, WB2, and four display interfaces. `sar2130p_mdp` only exposes `DPU_CLK_CTRL_REG_DMA`, matching the 9.x generation.

Integration points: it uses `sm8550_vbif` and the same CWB/DSC topology mechanisms as SM8550. `sar2130p_perf_data` is consumed by performance checking and voting, but its `cdp_cfg` disables read/write CDP for both traffic classes, unlike adjacent catalogs. Interrupts integrate with the central DPU IRQ layer and physical encoder callbacks.

State and persistence: immutable catalog data only. The persistent behavior is the SoC-specific resource inventory and performance policy used during all atomic commits.

Risks: CDP disabled in the performance config is a notable behavioral difference; enabling it accidentally or copying another SoC config could change memory behavior. The catalog otherwise resembles SM8550, so subtle differences may be missed in review. QoS LUTs remain TODO/FIXME-marked.

Test signals: SAR2130P display bring-up, DSI/DP vblank and underrun IRQs, DSC paths, CWB/writeback, DMA cursor assignment, bandwidth votes with CDP disabled, and suspend/resume or idle-PC transitions.
