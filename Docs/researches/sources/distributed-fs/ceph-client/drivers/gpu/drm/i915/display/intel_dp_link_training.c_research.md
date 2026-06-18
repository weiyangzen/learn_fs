# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.c

## Purpose
Implements DisplayPort link training for i915 across classic 8b/10b links, UHBR 128b/132b links, eDP, DP MST, and LTTPR repeater topologies. It also exposes debugfs controls for forcing link rates, lane counts, failures, and retraining.

## Important APIs, types, and functions
- Capability/probe APIs: `intel_dp_read_dprx_caps()`, `intel_dp_init_lttpr_and_dprx_caps()`, `intel_dp_lttpr_transparent_mode_enabled()`.
- Training setup APIs: `intel_dp_link_training_set_mode()`, `intel_dp_link_training_set_bw()`, `intel_dp_program_link_training_pattern()`, `intel_dp_set_signal_levels()`, `intel_dp_get_adjust_train()`.
- Training lifecycle: `intel_dp_start_link_train()` and `intel_dp_stop_link_train()`.
- 8b/10b phases: `intel_dp_link_training_clock_recovery()`, `intel_dp_link_training_channel_equalization()`, `intel_dp_link_train_all_phys()`.
- UHBR phases: `intel_dp_128b132b_link_train()`, `intel_dp_128b132b_lane_eq()`, `intel_dp_128b132b_lane_cds()`, `intel_dp_128b132b_intra_hop()`, `intel_dp_128b132b_sdp_crc16()`.
- Fallback/debug: `intel_dp_schedule_fallback_link_training()`, link-parameter reduction helpers, and `intel_dp_link_training_debugfs_add()`.

## Control flow
Before training, `intel_dp_start_link_train()` blocks HPD handling, reinitializes LTTPR/DPRX capabilities, programs link mode and bandwidth, then chooses either UHBR or 8b/10b training. LTTPR discovery reads common caps, avoids unsafe probing on old AUX-timeout platforms, preserves mode on active links, switches repeaters to non-transparent mode when safe, and reads per-PHY caps.

For 8b/10b, training walks LTTPRs from downstream to upstream and then the DPRX. Each PHY performs clock recovery with TPS1, repeated link-status reads, sink adjust-request handling, same-voltage and max-swing escape conditions, and then channel equalization with TPS2/3/4 based on source/sink capability. After each PHY it disables that PHY's DPCD training pattern; after all PHYs it idles source training.

For UHBR, the code waits for intra-hop AUX to clear, performs the LANEx_EQ_DONE sequence with TPS1 then TPS2 and TX FFE preset updates under loop/deadline limits, then performs the LANEx_CDS_DONE sequence with TPS2_CDS until interlane align and symbol lock are complete. On failure it leaves the source in TPS2 before disabling DPCD training to avoid stuck transcoder states.

After training failure, sequential failure counts gate whether a userspace modeset retry is scheduled. Fallback first tries max eDP params when appropriate, then reduces link parameters while respecting forced debugfs rate/lane settings and avoiding unsupported UHBR to non-UHBR fallback. `intel_dp_stop_link_train()` marks the link active, disables source training, waits for UHBR intra-hop cleanup, unblocks HPD, and schedules link-check work unless long HPDs are ignored or repeated sequential failures occurred.

## State and persistence
State is kept in `struct intel_dp`: DPCD caps, LTTPR common/per-PHY caps, `train_set[4]`, active link status, selected link rate/lane count, max fallback limits, forced debugfs values, retrain-disabled flag, failure counters, HOBL failure state, and VRR link mode state. Sink-side DPCD persists link coding, lane count, link rate, downspread/MSA ignore, training pattern, and lane signal level requests during training.

## Dependencies and integration points
Depends heavily on DRM DP helper functions for DPCD caps, LTTPR, link status, adjust requests, UHBR status checks, and training delays. Source-side programming is delegated through function pointers in `intel_dp` and encoder callbacks. It is invoked from DDI and legacy DP enable paths and feeds MST, compliance tests, hotplug/link-check work, and debugfs.

## Risks
This file is high risk because link training touches timing, hardware sequencing, sink quirks, repeaters, and fallback policy. Infinite-loop prevention, partial AUX read/write failures, display-generation training pattern support, LTTPR transparent mode changes on active links, UHBR deadlines, and forced debugfs settings are all compatibility-sensitive. The code intentionally tolerates training failures in some CI long-HPD-ignore cases, which can hide real link issues if used outside that context.

## Test signals
Core signals are `lt_dbg` and `lt_err` messages showing requested and programmed signal levels, link status dumps, selected TPS pattern, pass/fail per PHY, fallback parameter changes, and retrain disablement. Debugfs files `i915_dp_force_link_rate`, `i915_dp_force_lane_count`, `i915_dp_force_link_training_failure`, `i915_dp_force_link_retrain`, max rate/lane files, and retrain-disabled status provide directed test hooks. Validation should cover SST, MST, eDP, LTTPR docks, UHBR, forced fallback, HPD retry behavior, and suspend/resume retraining.
