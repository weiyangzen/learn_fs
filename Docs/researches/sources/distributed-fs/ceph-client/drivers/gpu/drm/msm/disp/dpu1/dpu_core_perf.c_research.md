# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.c

Purpose: this implementation calculates, validates, aggregates, and applies DPU core performance requirements for active CRTCs. It converts plane and mode state into bandwidth and core-clock votes, then drives Linux interconnect (`icc_set_bw`) and OPP (`dev_pm_opp_set_rate`) APIs.

Important functions: `dpu_core_perf_adjusted_mode_clk()` applies catalog clock inefficiency factors. `_dpu_core_perf_calc_bw()` sums visible plane fetch bandwidth and applies bandwidth inefficiency. `_dpu_core_perf_calc_clk()` computes a mode-derived pixel rate and takes the max of plane clocks. `_dpu_core_perf_calc_crtc()` stores a CRTC's requested `bw_ctl`, `max_per_pipe_ib`, and `core_clk_rate`. `dpu_core_perf_aggregate()` sums bandwidth and maxes instantaneous bandwidth across enabled CRTCs of the same client type. `dpu_core_perf_crtc_check()` rejects real-time CRTC states exceeding `max_bw_high`. `dpu_core_perf_crtc_update()` updates bus votes before clock increases and updates clock after bus changes. `dpu_core_perf_crtc_release_bw()` releases bandwidth after pending frames drain. `dpu_core_perf_init()` stores catalog performance config and max clock.

Control flow: atomic check calculates new CRTC performance, aggregates active real-time clients, and enforces the high bandwidth threshold. Atomic flush/update compares old vs new votes; increases happen before kickoff, decreases after commit or disable. Bus bandwidth is divided across `kms->num_paths`. Clock rate is chosen as fixed, minimum, or max of active CRTC clocks depending on debug tuning mode.

State and persistence: `struct dpu_core_perf` stores current clock rate, maximum clock, catalog config, debug tune mode, bandwidth release flag, and fixed-mode overrides. Each `dpu_crtc` stores `cur_perf`; each `dpu_crtc_state` stores `new_perf`. `kms->bandwidth_ref` gates release behavior.

Dependencies and integration: depends on `dpu_crtc`, `dpu_plane_state`, `dpu_kms`, catalog `dpu_perf_cfg`, ICC paths, OPP, debugfs, and tracepoints. CRTC code calls check/update/release during atomic check, flush, complete, disable, and frame-done work.

Risks: aggregation uses enabled CRTCs and client type, so stale `enabled` or client classification can over/under vote. `icc_set_bw()` return values are ignored, currently leaving `ret` always zero. Fixed/minimum debug modes can mask real bandwidth bugs. Incorrect catalog inefficiency or min IB values lead to underruns or unnecessary power.

Test signals: atomic check rejection for excessive bandwidth, multi-CRTC aggregation, video-mode bandwidth reference behavior, command-mode bandwidth release after frame done, debugfs `perf_mode` changes, OPP rate transitions, ICC path votes, underrun counters, and suspend/resume with restored performance state.
