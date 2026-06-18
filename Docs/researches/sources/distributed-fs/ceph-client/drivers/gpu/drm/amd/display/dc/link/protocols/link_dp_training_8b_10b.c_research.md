# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.c

Purpose: implements DisplayPort 8b/10b link-training policy and sequencing for native DP/DPRX and LTTPR paths. It derives AUX read intervals, decides training settings, chooses LTTPR mode, runs clock recovery, runs channel equalization, and drives the complete 8b/10b training loop.

Important APIs/functions: `decide_8b_10b_training_settings`, `dp_decide_8b_10b_lttpr_mode`, `perform_8b_10b_clock_recovery_sequence`, `perform_8b_10b_channel_equalization_sequence`, and `dp_perform_8b_10b_link_training`. Helper timing functions read `DP_TRAINING_AUX_RD_INTERVAL` or synthesize the 16 ms LTTPR default for old sinks. The early TPS2 helper implements an AMD external retimer interop sequence.

Control flow: settings are zeroed and filled from requested `dc_link_settings`, spread, FEC readiness, CR/EQ patterns, timing, DPCD lane mirrors, and LTTPR mode. Training programs link settings, optionally trains LTTPRs from farthest repeater toward the source, clears per-lane settings between repeater hops, then trains the final DPRX. CR loops until lock, max voltage swing, repeated unchanged requests, or `LINK_TRAINING_MAX_CR_RETRY`; EQ loops through bounded retry attempts and validates CR, channel EQ, symbol lock, and interlane alignment.

State/persistence: mutates `link_training_settings` lane settings each retry, reads `link->dpcd_caps`, `link->dc->caps/config/work_arounds`, and persistent `link->dp_ss_off`/`chip_caps`. It writes receiver and repeater DPCD link, pattern, and lane settings through shared DP PHY/DPCD helpers.

Dependencies/integration: depends on `link_dpcd`, `link_dp_phy`, and `link_dp_capability`. It is called by higher-level DP training selection and reused by the fixed VS/PE retimer path.

Risks: AUX failures abort; bad DPCD caps can select wrong timing/pattern; LTTPR mode selection depends on VBIOS and debug config; retry limits protect against infinite VS toggling but can fail marginal links. Early TPS2 is vendor-specific and sensitive to repeater count/address offsets.

Test signals: DP compliance/link-training logs, successful CR/EQ on 1/2/4 lane links, LTTPR transparent and non-transparent paths, old DPCD 1.1 LTTPR timing, max-VS failure returns, unplug/AUX error abort handling, and regression checks for early TPS2 retimer hardware.
