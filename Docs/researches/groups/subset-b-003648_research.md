# subset-b-003648 Research

Grouped research report for DPU catalog, CRTC, encoder, IRQ, and performance sources. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_0_sm8350.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_0_sm8350.h

Purpose: this header is a static hardware catalog for the Qualcomm SM8350 DPU block, exporting `const struct dpu_mdss_cfg dpu_sm8350_cfg`. It describes MDSS version 7.0, block capabilities, register ranges, interrupts, display interfaces, compression, writeback, VBIF, and performance constraints. There is no executable control flow beyond static initialization; runtime behavior comes from DPU KMS/resource-manager code consuming these tables.

Important data: `sm8350_dpu_caps` advertises source split, dim layer, idle power collapse, 3D merge, 4096 max line width, eleven blend stages, and default pixel RAM. `sm8350_mdp` maps top-level clock controls for VIG, DMA, WB2, and REG_DMA. The file defines six CTLs, eight SSPPs (four VIG and four DMA, with DMA2/DMA3 cursor-capable), six layer mixers with three LM pairs, four DSPPs, six pingpongs, three 3D merge blocks, four DSC slices, one WB2 block, and four interfaces: DP0, DSI0, DSI1, and DP MST companion `intf_3`.

Integration points: the final `dpu_sm8350_cfg` binds common shared catalog objects such as `dpu_cdm_5_x`, `sdm845_vbif`, `sdm845_lm_sblk`, `sdm845_dspp_sblk`, `sc7280_pp_sblk`, and DSC sub-block descriptors. Interrupt fields use `DPU_IRQ_IDX()` and must match the IRQ map consumed by `dpu_core_irq` and physical encoder/CRTC handlers. Performance data feeds `dpu_core_perf.c` bandwidth checks and OPP/ICC votes.

State and persistence: the data is immutable kernel static storage. The persistent runtime effect is indirect: resource allocation, topology validation, clock/bandwidth voting, and interrupt registration use these constants for the lifetime of the driver instance.

Risks: incorrect base/length, `xin_id`, clock-control, IRQ, or pair mappings can silently misprogram hardware or hang commits. DSC entries intentionally share DCE base addresses with different sub-blocks; changing them without matching hardware documentation is high risk. The performance LUTs are marked FIXME/TODO, so QoS margins may be conservative or inaccurate.

Test signals: boot/probe on SM8350, DSI and DP modeset, dual-DSI, DP MST pairing, DSC-on modes, writeback through WB2, underrun absence, vblank and pingpong-done IRQ delivery, debugfs resource dumps, and bandwidth check coverage for high-resolution modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_0_sm8350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_2_sc7280.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_2_sc7280.h

Purpose: this header exports `dpu_sc7280_cfg`, the MDSS/DPU 7.2 catalog for SC7280. It is a smaller SoC description used by KMS discovery and resource reservation, not an executable module.

Important data: `sc7280_dpu_caps` sets seven blend stages, idle power collapse, dim layer, 3D merge, 2400 max line width, and default pixel RAM. The MDP table has clock controls for one VIG, three DMA pipes, and WB2. The hardware inventory includes four CTLs, one VIG SSPP, three DMA SSPPs, three LMs (`LM_0`, `LM_2`, `LM_3`), one DSPP, four pingpongs, one 3D merge block, one DSC hard-slice encoder, one WB2 block, and three interfaces: DP0, DSI0, and DP1.

Integration points: DPU core code consumes the catalog through `dpu_mdss_cfg` to allocate CTLs, LMs, DSPPs, pingpongs, and interfaces for `dpu_crtc.c` and `dpu_encoder.c`. Shared sub-block pointers include `dpu_vig_sblk_qseed3_3_0_rot_v2`, `dpu_dma_sblk`, `sc7180_lm_sblk`, `sdm845_dspp_sblk`, `sc7280_pp_sblk`, `dsc_sblk_0`, `dpu_cdm_5_x`, and `sdm845_vbif`. Performance data uses SC7180 QoS tables and is consumed by `dpu_core_perf_crtc_check()` and `dpu_core_perf_crtc_update()`.

State and persistence: all structures are static const. Runtime state such as assigned resources, enabled encoders, and bandwidth votes lives elsewhere; this file only constrains which resources exist and how they are addressed.

Risks: the single VIG/DSC and sparse LM numbering make topology and resource-reservation mistakes easy. Pingpong entries 0 and 1 have no merge block while 2 and 3 share `MERGE_3D_1`; incorrect assumptions about symmetric merge support can break wide modes. Bandwidth values are lower than flagship catalogs, so high-resolution or writeback paths should be checked carefully.

Test signals: SC7280 display probe, internal/eDP DP path, DSI command/video modes, DSC single-slice operation, WB2 writeback, max-linewidth rejection, CRTC LM-bound calculations for 2400-wide limits, underrun counters, and IRQ delivery for CTL start, pingpong done, vblank, tear, and WB done.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_7_2_sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_0_sc8280xp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_0_sc8280xp.h

Purpose: this header defines the DPU 8.0 SC8280XP catalog through `dpu_sc8280xp_cfg`. It describes a large laptop-class display block with many DP interfaces and multiple DSC engines.

Important data: capabilities include source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The catalog lists six CTLs, four VIG plus four DMA SSPPs, six paired LMs, four DSPPs, six pingpongs, three 3D merge blocks, and six DSC slices arranged as three DCE bases with paired sub-blocks. The interface table is the distinguishing feature: DP `intf_0`, DSI `intf_1`/`intf_2`, and DP `intf_3` through `intf_8`, with comments documenting MST pairings.

Integration points: resource-manager code uses the larger interface set to support multi-DP/MST topologies. `dpu_encoder_update_topology()` and `dpu_crtc_get_topology()` depend on DSC count, interface count, and 3D merge availability for LM/DSC allocation. Interrupt indices in CTL, pingpong, DSI tear, and interface entries are consumed by the central IRQ layer and physical encoders.

State and persistence: there is no mutable state. The catalog persists as read-only kernel data and determines hardware block availability for the device lifetime.

Risks: the many DP interface/controller mappings are easy to misroute, particularly MST companion comments. There is no WB entry in this catalog, so writeback assumptions copied from adjacent SoCs would be wrong. The performance section has TODO/FIXME notes for QoS table accuracy and shares some SC7180/SC8180X tables, making underrun and bandwidth validation important.

Test signals: boot and modeset on SC8280XP, all DP controller mappings, MST pairing, dual-DSI if present, DSC modes using more than four slices, high-resolution LM split, vblank/underrun IRQs across all interfaces, and bandwidth/clock validation near `max_bw_high`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_0_sc8280xp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_1_sm8450.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_1_sm8450.h

Purpose: this header exports `dpu_sm8450_cfg`, the DPU 8.1 catalog for SM8450. It is the runtime hardware contract used by DPU KMS, the resource manager, CRTC atomic checks, and encoder setup.

Important data: the file defines a 5120-linewidth DPU with source split, dim layer, idle PC, 3D merge, and eleven blend stages. It has six CTLs, four QSEED 3.3.1 VIG SSPPs, four DMA SSPPs with two cursor-capable pipes, six paired LMs, four DSPPs, six normal pingpongs plus two CWB pingpongs, four merge_3d blocks including the CWB merge, four DSC slices, one WB2 block, and four interfaces for DP0, DSI0, DSI1, and DP MST pairing.

Integration points: CWB pingpongs and `MERGE_3D_3` are used by concurrent writeback paths in `dpu_encoder_helper_phys_setup_cwb()` and clone-mode CRTC kickoff. The WB2 entry feeds writeback encoder setup and `intr_wb_done`; normal display paths consume pingpong done and interface vblank/underrun/tear IRQs. Performance data is used by `dpu_core_perf` with min prefill lines set to 35.

State and persistence: the file holds immutable catalog data. Runtime state is allocated by DRM atomic state, DPU global state, and encoder/CRTC private structures.

Risks: CWB resources sit in the pingpong and merge arrays, so count/order mismatches can break clone/writeback without affecting simple scanout. DSC entries share DCE bases and only the second DCE advertises native 4:2:x support. QoS LUT comments still note unresolved table differences.

Test signals: SM8450 probe, DSI/DP modeset, DSC with two engines, concurrent writeback clone mode, WB2 jobs, CWB mux programming, frame-done timers, pingpong done IRQs, bandwidth release after frame done, and high-resolution split-LM validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_1_sm8450.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_4_sa8775p.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_4_sa8775p.h

Purpose: this file provides `dpu_sa8775p_cfg`, the MDSS/DPU 8.4 catalog for SA8775P. It follows the high-end 8.x table layout while adding automotive-oriented interface mappings and CWB resources.

Important data: `sa8775p_dpu_caps` enables source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The inventory includes six CTLs, four QSEED 3.3.1 VIG pipes, four DMA pipes, six paired LMs, four DSPPs, eight pingpongs including two CWB pingpongs, four 3D merge blocks, six DSC slices, WB2, and a large interface set: DP0, DSI0, DSI1, DP1, plus additional DP MST companion interfaces `intf_6`, `intf_7`, and `intf_8`.

Integration points: DPU RM consumes the block counts and interface/controller pairs for multi-display reservations. CWB and WB2 resources integrate with writeback and clone-mode code in `dpu_encoder.c` and `dpu_crtc.c`. The performance config uses `sm6350_qos_linear_macrotile` for both linear and macrotile classes, SC7180 NRT QoS, `sdm845_vbif`, and min prefill lines of 35.

State and persistence: the catalog is immutable. It persists as hardware description data and does not manage runtime resources directly.

Risks: DP controller comments show multiple interfaces paired with controller 0 or 1 for MST; wrong controller IDs can surface as link bring-up or vblank failures only on specific ports. Safe LUT values differ from other 8.x/9.x catalogs, so underrun testing matters. As with similar catalogs, DSC shared-base definitions and CWB ordering are sensitive.

Test signals: SA8775P display probe, all DP/DSI outputs, MST combinations, DSC slice allocation, WB2/concurrent writeback, CWB mux enable/disable, interface underrun/vblank IRQs, pingpong done IRQs, and bandwidth validation under multi-display load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_8_4_sa8775p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_0_sm8550.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_0_sm8550.h

Purpose: this header exports `dpu_sm8550_cfg`, the DPU 9.0 catalog for SM8550. It describes a newer block generation with expanded DMA pipes, CWB support, and `sm8550_vbif`.

Important data: the SoC capabilities advertise 5120 max line width, source split, dim layer, idle PC, 3D merge, and eleven blend stages. Compared with 8.x catalogs, `sm8550_mdp` only lists `DPU_CLK_CTRL_REG_DMA`; individual SSPP/WB entries do not carry `clk_ctrl` assignments. The hardware inventory includes six CTLs, four QSEED 3.3.2 VIG pipes, six DMA pipes where DMA4/DMA5 are cursor capable, six LMs, four DSPPs, six regular pingpongs plus two CWB pingpongs, four merge blocks, four DSC slices, WB2, and four interfaces for DP0, DSI0, DSI1, and DP MST.

Integration points: the expanded DMA inventory affects plane assignment and cursor availability. `dpu_encoder.c` uses CWB pingpongs/merge for concurrent writeback and DSC counts for topology decisions. The catalog uses `sm8550_vbif`, so VBIF error clearing and traffic policy differ from earlier `sdm845_vbif` consumers.

State and persistence: all data is static const; dynamic resource state lives in DPU RM global state and DRM atomic state.

Risks: dropping per-pipe clock controls is a generation-specific behavior; backporting assumptions from 8.x can break clock gating. The QoS tables are still marked FIXME/TODO. CWB base addresses differ from SM8450/SA8775P, so copy-paste mistakes would break writeback.

Test signals: SM8550 probe, high-resolution DSI/DP modes, cursor pipes DMA4/DMA5, concurrent writeback, DSC two-engine modes, frame-done IRQ handling, VBIF error monitoring, and bandwidth/clock tests using `sm8550_vbif`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_0_sm8550.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_1_sar2130p.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_1_sar2130p.h

Purpose: this header defines `dpu_sar2130p_cfg`, the DPU 9.1 hardware catalog for SAR2130P. It is structurally close to SM8550 and feeds the same KMS/RM/encoder/CRTC consumers.

Important data: capabilities include source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The catalog has six CTLs, four QSEED 3.3.2 VIG pipes, six DMA pipes, six LMs, four DSPPs, six normal pingpongs, two CWB pingpongs, four merge blocks, four DSC slices, WB2, and four display interfaces. `sar2130p_mdp` only exposes `DPU_CLK_CTRL_REG_DMA`, matching the 9.x generation.

Integration points: it uses `sm8550_vbif` and the same CWB/DSC topology mechanisms as SM8550. `sar2130p_perf_data` is consumed by performance checking and voting, but its `cdp_cfg` disables read/write CDP for both traffic classes, unlike adjacent catalogs. Interrupts integrate with the central DPU IRQ layer and physical encoder callbacks.

State and persistence: immutable catalog data only. The persistent behavior is the SoC-specific resource inventory and performance policy used during all atomic commits.

Risks: CDP disabled in the performance config is a notable behavioral difference; enabling it accidentally or copying another SoC config could change memory behavior. The catalog otherwise resembles SM8550, so subtle differences may be missed in review. QoS LUTs remain TODO/FIXME-marked.

Test signals: SAR2130P display bring-up, DSI/DP vblank and underrun IRQs, DSC paths, CWB/writeback, DMA cursor assignment, bandwidth votes with CDP disabled, and suspend/resume or idle-PC transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_1_sar2130p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_2_x1e80100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_2_x1e80100.h

Purpose: this file exports `dpu_x1e80100_cfg`, the DPU 9.2 catalog for X1E80100. It is a large multi-display catalog, especially for DP outputs, and is consumed as immutable hardware description data.

Important data: it enables source split, dim layer, idle PC, 3D merge, 5120 max line width, and eleven blend stages. The file defines six CTLs, four QSEED 3.3.3 VIG pipes, six DMA pipes, six paired LMs, four DSPPs, eight pingpongs including CWB, four merge blocks, four DSC slices, WB2, and nine interfaces: DP0, DSI0, DSI1, DP MST companion `intf_3`, plus DP `intf_4` through `intf_8` with multiple controller IDs and MST pair comments.

Integration points: `dpu_encoder_update_topology()` depends on the DSC count and interface count for LM/DSC/CDM reservations. DP controller mappings connect to `msm_dp_*` helpers for wide bus, YUV420, and peripheral flush decisions. CWB and WB2 entries support writeback and clone-mode paths. The catalog uses `sm8550_vbif` and 9.x-style MDP clock control.

State and persistence: all structures are static const. Runtime resource state is maintained by DPU RM, CRTC state, and encoder private data.

Risks: interface/controller mapping is the highest-risk area because the SoC exposes many DP paths and MST pairings. VIG sub-blocks use QSEED 3.3.3, so reusing older feature assumptions may miss scaler behavior. QoS tables still include FIXME/TODO notes, and bandwidth tests should cover multi-monitor cases.

Test signals: X1E80100 probe, all DP connectors, MST pairings, DP YUV420/CDM path, DSI paths, DSC modes, concurrent writeback, CWB mux programming, vblank/underrun IRQs for all interfaces, and high-resolution multi-display bandwidth validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_9_2_x1e80100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_irq.h

Purpose: this header declares the DPU core interrupt API used by the MSM KMS integration and DPU submodules. It exposes lifecycle hooks, IRQ dispatch, status readback, callback registration, and debugfs setup.

Important APIs: `dpu_core_irq_preinstall()` prepares interrupt state before DRM IRQ install; `dpu_core_irq_uninstall()` tears it down. `dpu_core_irq()` is the top-level handler called through the MSM KMS IRQ path. `dpu_core_irq_read()` reads the status for a catalog/`DPU_IRQ_IDX()` interrupt index. `dpu_core_irq_register_callback()` and `dpu_core_irq_unregister_callback()` bind one callback and opaque argument to a specific DPU interrupt index. `dpu_debugfs_core_irq_init()` exposes debugfs state under a parent dentry.

Dependencies: the header includes `dpu_kms.h` and `dpu_hw_interrupts.h`, so callers operate on `struct dpu_kms`, `struct msm_kms`, and hardware interrupt abstractions. Catalog files provide interrupt indices for CTL start, pingpong done, interface underrun/vblank/tear, and writeback done; encoder and CRTC code register/wait on those indices.

State and persistence: the header itself has no state. The implementation likely stores callback arrays and enabled masks in the `dpu_kms`/hardware interrupt layer. Callback lifetime is important because physical encoder and CRTC objects may be enabled/disabled dynamically.

Risks: unregister/register mismatches can leave stale callback pointers reachable from IRQ context. IRQ indices must be validated against catalog bounds. `dpu_core_irq_read()` is used as a timeout fallback in encoder waits, so incorrect read semantics can hide missed interrupts or double-handle events.

Test signals: DRM IRQ install/uninstall during probe/remove, vblank enable/disable, encoder wait timeout paths, pingpong done and CTL start delivery, underrun reporting, writeback completion, debugfs IRQ status, and stress with rapid modeset/suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.c

Purpose: this implementation calculates, validates, aggregates, and applies DPU core performance requirements for active CRTCs. It converts plane and mode state into bandwidth and core-clock votes, then drives Linux interconnect (`icc_set_bw`) and OPP (`dev_pm_opp_set_rate`) APIs.

Important functions: `dpu_core_perf_adjusted_mode_clk()` applies catalog clock inefficiency factors. `_dpu_core_perf_calc_bw()` sums visible plane fetch bandwidth and applies bandwidth inefficiency. `_dpu_core_perf_calc_clk()` computes a mode-derived pixel rate and takes the max of plane clocks. `_dpu_core_perf_calc_crtc()` stores a CRTC's requested `bw_ctl`, `max_per_pipe_ib`, and `core_clk_rate`. `dpu_core_perf_aggregate()` sums bandwidth and maxes instantaneous bandwidth across enabled CRTCs of the same client type. `dpu_core_perf_crtc_check()` rejects real-time CRTC states exceeding `max_bw_high`. `dpu_core_perf_crtc_update()` updates bus votes before clock increases and updates clock after bus changes. `dpu_core_perf_crtc_release_bw()` releases bandwidth after pending frames drain. `dpu_core_perf_init()` stores catalog performance config and max clock.

Control flow: atomic check calculates new CRTC performance, aggregates active real-time clients, and enforces the high bandwidth threshold. Atomic flush/update compares old vs new votes; increases happen before kickoff, decreases after commit or disable. Bus bandwidth is divided across `kms->num_paths`. Clock rate is chosen as fixed, minimum, or max of active CRTC clocks depending on debug tuning mode.

State and persistence: `struct dpu_core_perf` stores current clock rate, maximum clock, catalog config, debug tune mode, bandwidth release flag, and fixed-mode overrides. Each `dpu_crtc` stores `cur_perf`; each `dpu_crtc_state` stores `new_perf`. `kms->bandwidth_ref` gates release behavior.

Dependencies and integration: depends on `dpu_crtc`, `dpu_plane_state`, `dpu_kms`, catalog `dpu_perf_cfg`, ICC paths, OPP, debugfs, and tracepoints. CRTC code calls check/update/release during atomic check, flush, complete, disable, and frame-done work.

Risks: aggregation uses enabled CRTCs and client type, so stale `enabled` or client classification can over/under vote. `icc_set_bw()` return values are ignored, currently leaving `ret` always zero. Fixed/minimum debug modes can mask real bandwidth bugs. Incorrect catalog inefficiency or min IB values lead to underruns or unnecessary power.

Test signals: atomic check rejection for excessive bandwidth, multi-CRTC aggregation, video-mode bandwidth reference behavior, command-mode bandwidth release after frame done, debugfs `perf_mode` changes, OPP rate transitions, ICC path votes, underrun counters, and suspend/resume with restored performance state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.h

Purpose: this header defines the DPU core performance data structures and function prototypes shared between CRTC, KMS initialization, and debugfs/performance code.

Important types: `struct dpu_core_perf_params` stores per-CRTC requested performance: maximum per-pipe instantaneous bandwidth, arbitrated bandwidth, and core clock rate. `struct dpu_core_perf_tune` stores the debug performance mode. `struct dpu_core_perf` holds the SoC-specific `dpu_perf_cfg`, current and maximum core clock, tuning state, bandwidth-release control, and fixed-mode clock/IB/AB overrides.

Important APIs: `dpu_core_perf_adjusted_mode_clk()` applies catalog clock scaling and is used by both performance checking and mode validation. `dpu_core_perf_crtc_check()` validates a proposed CRTC state. `dpu_core_perf_crtc_update()` applies bandwidth/clock changes. `dpu_core_perf_crtc_release_bw()` drops bandwidth when frame work drains. `dpu_core_perf_init()` binds catalog config and maximum clock during KMS setup. `dpu_core_perf_debugfs_init()` exposes tuning/debug entries when debugfs is enabled.

Dependencies and integration: includes Linux types, dcache, mutex, DRM CRTC definitions, and `dpu_hw_catalog.h`. `dpu_crtc.h` embeds `dpu_core_perf_params` in both live and atomic CRTC state. Catalog headers provide `dpu_perf_cfg` values used through this interface.

State and persistence: the structures persist inside `struct dpu_kms` and `struct dpu_crtc` for the lifetime of the device/CRTC. Atomic state copies carry proposed values across check/commit.

Risks: the header exposes debug writable fields indirectly through debugfs, so production behavior can be altered at runtime on debug builds. Type widths mix `u32` KBps votes with `u64` clocks/bandwidth; overflow and unit mismatches are key review points.

Test signals: compile coverage for all users, debugfs creation, KMS init using every catalog perf block, CRTC check/update/release call paths, and mode validation using adjusted clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.c

Purpose: this file implements the DPU DRM CRTC object. It coordinates atomic resource reservation, mixer/blend/color programming, performance updates, commit kickoff, vblank/CRC handling, frame-done processing, enable/disable, mode validation, and debugfs reporting.

Important functions: CRC helpers parse sources (`none`, `auto`/`lm`, `encoder`), set up LM or encoder MISR, collect CRCs after skipping initial frames, and integrate with DRM CRC entries. Blend helpers program per-plane stages, active SSPP bitmaps, alpha modes, LM output ROIs, and CTL/LM pending flush masks. Color helpers convert DRM CTM/gamma LUT state into DSPP PCC and GC programming. Atomic hooks include `dpu_crtc_atomic_check()`, `dpu_crtc_atomic_begin()`, `dpu_crtc_atomic_flush()`, `dpu_crtc_enable()`, and `dpu_crtc_disable()`.

Control flow: atomic check reserves LM/CTL/DSPP/CDM-related topology resources on modeset/color changes and SSPP plane resources on plane/zpos changes, computes LM bounds, marks dirtyfb requirements for command/self-refresh paths, increments bandwidth references, and calls `dpu_core_perf_crtc_check()`. Atomic begin programs pending trigger state, blend setup, and color blocks. Atomic flush captures vblank events, updates performance upward, flushes planes, and leaves final kickoff to `dpu_crtc_commit_kickoff()`. Kickoff validates encoders, handles clone-mode writeback ordering, prepares encoders, clears VBIF errors, triggers encoder kickoff, starts frame-done timers, and increments `frame_pending`. Completion updates performance downward and sends page-flip events.

State and persistence: `struct dpu_crtc` stores event pointers, vblank stats, enabled flag, frame-pending counter, frame-event pool/list, completion, locks, current performance, and SMMU transition state. `struct dpu_crtc_state` stores atomic resource assignments, LM bounds, proposed performance, CRC source, and frame-skip count. Frame events are pooled in `DPU_CRTC_FRAME_EVENT_SIZE` entries and processed on KMS event workers.

Dependencies and integration: deeply integrates with DRM atomic helpers, vblank, CRC, self-refresh, DPU RM, DPU planes, encoders, VBIF, CTL/LM/DSPP hardware ops, and `dpu_core_perf`. Encoder callbacks feed vblank and frame-done events back into this file.

Risks: resource allocation depends on topology inference; DSC, CWB clone mode, color management, and split interfaces can change LM/DSPP requirements. `dpu_crtc_get_intf_mode()` warns about locking ambiguity. Frame-event pool overflow is rate-limited but can lose completion events. Bandwidth refs must balance across check, kickoff, frame done, video mode, and disable paths. Gamma LUT allocation failure currently skips programming without failing commit.

Test signals: atomic modeset/plane/zpos/color changes, command and video mode display, self-refresh transitions, clone-mode concurrent writeback, DSC topology, CWB writeback ordering, CRC capture from LM and encoder, vblank enable/disable, frame-done timeout behavior, underrun absence, debugfs `status`/`state`, and high-resolution mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.h

Purpose: this header defines DPU's private CRTC structures, enums, inline helpers, and public CRTC APIs used by encoder, plane, KMS, and performance code.

Important types: `enum dpu_crtc_client_type` separates real-time scanout from non-real-time writeback. SMMU enums and `struct dpu_crtc_smmu_state_data` track attach/detach transitions. `enum dpu_crtc_crc_source` selects none, layer mixer, or encoder CRC/MISR. `struct dpu_crtc_mixer` binds LM, CTL, optional DSPP, and mixer operation mode for each virtual pipeline. `struct dpu_crtc_frame_event` packages encoder frame events for kthread work. `struct dpu_crtc` embeds `drm_crtc` and stores event, vblank, frame, lock, performance, and SMMU state. `struct dpu_crtc_state` extends `drm_crtc_state` with performance, resource assignments, LM bounds, and CRC state.

Important APIs: `dpu_crtc_frame_pending()`, `dpu_crtc_check_mode_changed()`, `dpu_crtc_vblank()`, `dpu_crtc_vblank_callback()`, `dpu_crtc_commit_kickoff()`, `dpu_crtc_complete_commit()`, `dpu_crtc_init()`, `dpu_crtc_get_intf_mode()`, `dpu_crtc_get_client_type()`, `dpu_crtc_frame_event_cb()`, and `dpu_crtc_get_num_lm()`.

Dependencies and integration: includes DRM CRTC, `dpu_kms.h`, and `dpu_core_perf.h`. Encoders call vblank/frame-event/commit helpers; performance code consumes CRTC state; planes are assigned through atomic resource logic.

State and persistence: live `dpu_crtc` objects persist with DRM device lifetime, while `dpu_crtc_state` is duplicated/destroyed through atomic helpers. Frame-event structures are statically cached to avoid IRQ-context allocation.

Risks: `dpu_crtc_get_client_type()` returns RT whenever `crtc->state` exists, otherwise NRT, which is simple but can be surprising for writeback-only paths. Fixed-size mixer/event arrays depend on constants such as `CRTC_DUAL_MIXERS` and `DPU_CRTC_FRAME_EVENT_SIZE`. SMMU transition fields are shared state that can poison plane flushes on errors.

Test signals: compile coverage across encoder/CRTC/perf users, atomic state duplication/reset/destroy, frame-event callback paths, RT/NRT classification, SMMU transition error handling, and CRC source changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.c

Purpose: this file implements DPU's virtual DRM encoder. A virtual encoder owns one logical display and coordinates one or more physical encoders, pingpong blocks, CTLs, DSC engines, CWB muxes, CDM blocks, interrupt waits, resource-control power states, frame-done timers, topology setup, writeback helpers, and debugfs status.

Important functions and flow: `dpu_encoder_init()` allocates the virtual encoder, initializes locks/timers/work, and calls `dpu_encoder_setup_display()` to create physical video, command, or writeback encoders for each tile. `dpu_encoder_update_topology()` reports interface, DSC, and CDM needs to CRTC resource reservation. `dpu_encoder_virt_atomic_mode_set()` maps resources reserved by RM into physical encoders: pingpongs, CTLs, DSCs, CWB muxes, and CDM. Atomic enable sets DSC/widebus state, enables slave then master phys encoders, enters resource-control kickoff state, and configures dither/vsync/audio helpers. Atomic disable waits for transfer completion, pre-stops resources, disables phys encoders, cancels frame timers, stops resources, and drops connector state.

Resource control: `dpu_encoder_resource_control()` is a state machine with OFF, PRE_OFF, ON, and IDLE states. Kickoff cancels delayed idle and enables runtime PM/IRQs as needed. Frame done schedules delayed idle when no more frames are pending. Pre-stop and stop transition toward OFF. Enter-idle disables IRQs or runtime resources depending on video/command mode and idle-PC support.

Commit and IRQ handling: `dpu_encoder_prepare_for_kickoff()` lets phys encoders wait for previous work, powers resources on, resets CTLs if needed, and programs DSC. `dpu_encoder_kickoff()` triggers flush/start through `_dpu_encoder_kickoff_phys()` and then post-kickoff hooks. `dpu_encoder_frame_done_callback()` clears busy bits, stops watchdog timers, calls resource-control frame done, and notifies CRTC. Vblank and underrun callbacks update counters, call CRTC vblank, and snapshot on first underrun. Timeout handlers snapshot once and notify CRTC error events.

State and persistence: `struct dpu_encoder_virt` stores the DRM encoder, phys encoder array, current master/slave, assigned hardware pointers, DSC/CWB masks, assigned CRTC/connector, locks, frame busy bits, timers, display info, idle-PC support, RC state, delayed work, topology, widebus flag, and current DSC config. Physical encoder state is initialized in `dpu_encoder_phys_init()`.

Dependencies and integration: integrates with DPU RM, KMS, core IRQ API, CRTC frame/vblank callbacks, `msm_dp`/`msm_dsi` helpers, writeback jobs, CDM, DSC, CWB, VBIF, hardware CTL/INTF/WB/PP ops, debugfs, and display snapshots.

Risks: RC state transitions mix normal context, IRQ context, timers, and delayed work; stale busy bits or unbalanced runtime PM can wedge display. Clone-mode CWB intentionally skips flush/start on writeback encoders, so ordering with real-time encoders is fragile. DSC topology is limited and assumes supported combinations. Timeout fallback can synthesize callbacks if IRQ status is already set, so IRQ read semantics matter. Several paths assume `cur_master` and `hw_pp` are valid after mode set.

Test signals: DSI command/video enable/disable, DP modes with widebus/YUV420/CDM, split display master/slave, DSC single/dual engine, concurrent writeback clone mode, writeback YUV jobs, vblank and underrun IRQs, frame-done timeout snapshots, idle power collapse enter/exit, suspend/resume restore, debugfs status, and rapid modeset stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.h

Purpose: this header declares the public DPU encoder interface shared with CRTC, KMS, writeback, physical encoder code, and DRM integration.

Important constants and types: frame-event bits define encoder-to-CRTC notifications for done, error, panel-dead, and idle. `IDLE_TIMEOUT` sets the delayed idle-power-collapse duration, and `MAX_H_TILES_PER_DISPLAY` bounds split displays. `struct msm_display_info` describes interface type, tile count, controller IDs per tile, command-mode flag, and TE/vsync source.

Important APIs: lifecycle and commit helpers include `dpu_encoder_init()`, `dpu_encoder_assign_crtc()`, `dpu_encoder_prepare_for_kickoff()`, `dpu_encoder_trigger_kickoff_pending()`, `dpu_encoder_kickoff()`, `dpu_encoder_start_frame_done_timer()`, and `dpu_encoder_virt_runtime_resume()`. Synchronization APIs include `dpu_encoder_wait_for_commit_done()` and `dpu_encoder_wait_for_tx_complete()`. Query helpers expose interface mode, line/vsync counts, clone masks, widebus, DSC, DSC merge, CRC count/values, and commit validity. Topology/writeback APIs include `dpu_encoder_update_topology()`, `dpu_encoder_needs_modeset()`, `dpu_encoder_prepare_wb_job()`, and `dpu_encoder_cleanup_wb_job()`.

Dependencies and integration: includes DRM CRTC and `dpu_hw_mdss.h`. CRTC code uses these declarations for vblank toggling, kickoff sequencing, frame timers, topology, CRC, and writeback clone mode. Physical encoder implementations provide the underlying mode-specific operations.

State and persistence: no state lives in the header. It defines contracts over state stored in `struct dpu_encoder_virt` and physical encoder structs in the C file.

Risks: the header exposes many functions that must be called in a specific order: assign CRTC, mode set/enable, prepare, kickoff, timer, wait, disable. Misordering can cause IRQ waits without resources, stale CRTC pointers, or missed frame done. Frame-event bits are shared ABI within the driver and must stay consistent with CRTC handling.

Test signals: compile coverage for all call sites, split DSI tile initialization, vblank enable/disable per CRTC, commit/tx waits, topology update during atomic check, widebus/DSC queries, CRC setup/collection, and writeback job prepare/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder.h -->
