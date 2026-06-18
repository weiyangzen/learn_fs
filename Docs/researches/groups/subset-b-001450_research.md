# subset-b-001450 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.c

Purpose: implements DisplayPort 8b/10b link-training policy and sequencing for native DP/DPRX and LTTPR paths. It derives AUX read intervals, decides training settings, chooses LTTPR mode, runs clock recovery, runs channel equalization, and drives the complete 8b/10b training loop.

Important APIs/functions: `decide_8b_10b_training_settings`, `dp_decide_8b_10b_lttpr_mode`, `perform_8b_10b_clock_recovery_sequence`, `perform_8b_10b_channel_equalization_sequence`, and `dp_perform_8b_10b_link_training`. Helper timing functions read `DP_TRAINING_AUX_RD_INTERVAL` or synthesize the 16 ms LTTPR default for old sinks. The early TPS2 helper implements an AMD external retimer interop sequence.

Control flow: settings are zeroed and filled from requested `dc_link_settings`, spread, FEC readiness, CR/EQ patterns, timing, DPCD lane mirrors, and LTTPR mode. Training programs link settings, optionally trains LTTPRs from farthest repeater toward the source, clears per-lane settings between repeater hops, then trains the final DPRX. CR loops until lock, max voltage swing, repeated unchanged requests, or `LINK_TRAINING_MAX_CR_RETRY`; EQ loops through bounded retry attempts and validates CR, channel EQ, symbol lock, and interlane alignment.

State/persistence: mutates `link_training_settings` lane settings each retry, reads `link->dpcd_caps`, `link->dc->caps/config/work_arounds`, and persistent `link->dp_ss_off`/`chip_caps`. It writes receiver and repeater DPCD link, pattern, and lane settings through shared DP PHY/DPCD helpers.

Dependencies/integration: depends on `link_dpcd`, `link_dp_phy`, and `link_dp_capability`. It is called by higher-level DP training selection and reused by the fixed VS/PE retimer path.

Risks: AUX failures abort; bad DPCD caps can select wrong timing/pattern; LTTPR mode selection depends on VBIOS and debug config; retry limits protect against infinite VS toggling but can fail marginal links. Early TPS2 is vendor-specific and sensitive to repeater count/address offsets.

Test signals: DP compliance/link-training logs, successful CR/EQ on 1/2/4 lane links, LTTPR transparent and non-transparent paths, old DPCD 1.1 LTTPR timing, max-VS failure returns, unplug/AUX error abort handling, and regression checks for early TPS2 retimer hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.h

Purpose: public interface for the 8b/10b DP link-training implementation. It defines retry limits and exposes the complete training sequence plus the individually callable CR/EQ phases.

Important APIs/types: `LINK_TRAINING_MAX_CR_RETRY` caps total CR attempts at 100; `LINK_TRAINING_MAX_RETRY_COUNT` caps repeated unchanged training requests at 5. Exports `dp_perform_8b_10b_link_training`, `perform_8b_10b_clock_recovery_sequence`, `perform_8b_10b_channel_equalization_sequence`, `dp_decide_8b_10b_lttpr_mode`, and `decide_8b_10b_training_settings`.

Control flow and integration: consumers include the core DP training path and vendor retimer path. The phase exports let alternate training implementations reuse the standard CR/EQ algorithms while surrounding them with custom setup.

State/persistence: no storage of its own; all state is supplied through `dc_link`, `link_resource`, `dc_link_settings`, and mutable `link_training_settings`.

Dependencies: includes `link_dp_training.h`, so callers must use the common DP training structures and result enums.

Risks: changing retry constants changes interop behavior for marginal sinks and MST hubs. Since CR/EQ phase functions are exported, their assumptions about initialized `lt_settings` must stay documented and stable.

Test signals: compile coverage of all callers, standard 8b/10b training success/failure, and retimer code that reuses the phase APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.c

Purpose: provides a deliberately minimal DP link-training path that skips AUX validation and only programs source hardware timing/patterns before returning success.

Important API: `dp_perform_link_training_skip_aux` computes normal training settings with `dp_decide_training_settings`, applies preferred overrides, programs the CR training pattern/lane settings, waits the CR interval, programs the EQ pattern/lane settings, waits the EQ interval, switches to video mode, logs success, and returns `true`.

Control flow: there are no DPCD link-setting writes, lane-status reads, sink adjustment requests, or failure classification. The function is linear and assumes the configured link will lock without feedback.

State/persistence: uses stack-local `link_training_settings`; applies `link->preferred_training_settings` as overrides. Hardware state is changed through `dp_set_hw_training_pattern`, `dp_set_hw_lane_settings`, and `dp_set_hw_test_pattern`.

Dependencies/integration: includes `link_dp_training_auxless.h` and `link_dp_phy.h`; it still relies on common DP training setting selection.

Risks: always reporting success can hide bad cables, wrong rates, disconnected sinks, or lane-setting mismatch. It is only appropriate for paths where AUX is intentionally unavailable or already bypassed by platform policy.

Test signals: verify callers only select this path for valid AUX-less scenarios, confirm video pattern is restored, and use hardware/link-status observation outside this function to catch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.h

Purpose: declares the AUX-less link-training entry point.

Important API: `dp_perform_link_training_skip_aux(struct dc_link *, const struct link_resource *, const struct dc_link_settings *)` returns a boolean success value after hardware-only training.

Control flow/state: the header does not define state; it relies on `link_dp_training.h` structures and common DP training configuration.

Dependencies/integration: included by code that wants to bypass normal AUX/DPCD status exchange. It is not a replacement for standard DP training when sink feedback is available.

Risks: the boolean API cannot expose detailed link-training failure classes, and the implementation reports success unconditionally once hardware programming completes.

Test signals: build coverage for selector code, plus platform tests proving this path is not accidentally used for normal DP/eDP links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_auxless.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.c

Purpose: implements DisplayPort link training for USB4 DPIA display endpoints. It adapts standard DP training to tunneled links by coordinating DPCD operations with DMUB/DPIA `SET_CONFIG` messages.

Important APIs/functions: `dpia_perform_link_training`, `dpia_training_abort`, `dpia_get_eq_aux_rd_interval`, and `dpia_set_tps_notification` are exported. Internal helpers configure the link, send `SET_CONFIG`, build VS/PE and link-mode payloads, translate DP training patterns to DPIA training stages, set/clear DPCD training patterns, and run CR/EQ in transparent or non-transparent LTTPR mode.

Control flow: `dpia_perform_link_training` decides LTTPR mode, configures channel coding/LTTPR mode/link settings/FEC, then trains hops from the DPTX-to-DPIA hop down to DPRX when non-transparent LTTPR mode is used. Each hop runs CR, EQ, and end-training. Transparent or no-LTTPR mode trains only DPRX and leaves most USB4 tunneling control to DPIA firmware. Successful training waits briefly and optionally checks link-loss status; aborts perform cleanup writes and `SET_CONFIG(SET_LINK=0)` unless consolidated training is enabled.

State/persistence: mutates `link_training_settings`, reads `link->dpcd_caps.lttpr_caps`, `link->is_hpd_pending`, debug/config flags, and `link->skip_fallback_on_link_loss`. It sends synchronous DMUB commands through `dm_helpers_dmub_set_config_sync` and writes DPCD link, lane, and pattern registers.

Dependencies/integration: integrates with `link_dp_dpia`, `link_hwss`, `dm_helpers`, `dmub_cmd`, `link_dpcd`, `link_dp_phy`, `link_dp_training_8b_10b`, `link_dp_capability`, and `dc_dmub_srv`. It depends on firmware ACK behavior for `SET_CONFIG`.

Risks: timing is sensitive, especially the 16 ms clock-sync delay during final-hop EQ. Non-transparent mode assumes DPTX-to-DPIA CR/EQ success based on message ACKs. HPD pending changes abort semantics. A bad repeater count or hop index can address wrong DPCD repeater windows.

Test signals: USB4 DP tunnel training for transparent/non-transparent LTTPR, DMUB `SET_CONFIG` ACK/NACK, sink unplug during configure/training, fallback after link-loss check, debug extended AUX interval, and compliance corner case using `skip_fallback_on_link_loss`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.h

Purpose: public interface for USB4 DPIA DP link training.

Important APIs/types: `DPIA_CLK_SYNC_DELAY` defines the approximate 16 ms wait for nine USB4 DP clock-sync packets. Exports `dpia_perform_link_training`, `dpia_training_abort`, `dpia_get_eq_aux_rd_interval`, and `dpia_set_tps_notification`.

Control flow/integration: callers use `dpia_perform_link_training` as the DPIA equivalent of normal DP training. Lower-level helpers are exposed so shared PHY/DPCD training code can request cleanup, timing, or TPS notification behavior when DPIA is involved.

State/persistence: no persistent state in the header; all state flows through `dc_link`, `link_resource`, `dc_link_settings`, and `link_training_settings`.

Dependencies: includes `link_dp_training.h` for training settings/result enums and common DP structures.

Risks: the API exposes hop-indexed operations; callers must pass DPRX/repeater offsets consistently with the implementation's hop model.

Test signals: compile coverage for DPIA callers, link-training abort cleanup, and correct propagation of `skip_video_pattern` even though the current implementation ignores it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_dpia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.c

Purpose: isolates the non-standard 8b/10b link-training sequence required by a vendor fixed VS/PE embedded retimer. It wraps standard DP training with retimer-specific DDC/AUX commands, lane-setting interception, and link-rate workarounds.

Important APIs/functions: `dp_perform_fixed_vs_pe_training_sequence` is the main entry; `dp_fixed_vs_pe_set_retimer_lane_settings` forces retimer VS/PE values; `dp_fixed_vs_pe_read_lane_adjust` queries retimer-reported DPRX lane adjustments. A private non-transparent path reuses standard `perform_8b_10b_*` phases after retimer setup.

Control flow: non-transparent LTTPR mode uses the common 8b/10b sequence with a minimum 16 ms CR interval and optional link-rate toggle before writing the real rate. Transparent/no-LTTPR mode resets retimer lane settings, enables intercept, writes spread/lane/rate DPCD, optionally toggles link rate when no LTTPR IEEE OUI is present, applies vendor DPMF and four-lane commands, disables intercept during first CR retry, then runs custom CR and EQ loops with retimer VS/PE updates before DPCD lane writes.

State/persistence: updates `link->vendor_specific_lttpr_link_rate_wa`, mutates `lt_settings`, and programs retimer state through `link_configure_fixed_vs_pe_retimer`/`link_query_fixed_vs_pe_retimer` on `link->ddc`. It writes normal DP DPCD fields through `core_link_write_dpcd` and shared training helpers.

Dependencies/integration: depends on `link_dp_training_8b_10b`, `link_dpcd`, `link_dp_phy`, `link_dp_capability`, and `link_ddc`. It is selected for specific retimer hardware while preserving common result enums.

Risks: magic vendor payloads, intercept toggling, delay tuning, and rate toggles are hardware-specific. AUX/DDC command failures are not always checked uniformly. Incorrect lane-count packing can misprogram per-lane settings.

Test signals: target retimer platforms with 1/2/4 lanes, no-OUI and OUI-present LTTPR caps, non-transparent mode, debug `fixed_vs_aux_delay_config_wa`, CR max retry, EQ failure classification, and retimer readback of DPRX requested VS/PE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.h

Purpose: declares the vendor fixed VS/PE retimer training interface.

Important APIs: `dp_perform_fixed_vs_pe_training_sequence` runs the special training sequence; `dp_fixed_vs_pe_set_retimer_lane_settings` packs requested DPCD lane settings into retimer VS/PE vendor commands; `dp_fixed_vs_pe_read_lane_adjust` converts retimer query bytes into per-lane `dpcd_training_lane` adjustments.

Control flow/state: callers supply initialized `link_training_settings`; this header itself stores no state. The implementation uses common DP training result enums and lane-count constants.

Dependencies/integration: includes `link_dp_training.h` and is consumed by DP training selector code and any PHY path that must talk to the fixed retimer.

Risks: exported helpers expose vendor-specific behavior through generic-looking lane structures, so callers must ensure the hardware really is this retimer before using them.

Test signals: build coverage on configurations with retimer support and hardware tests verifying helper packing/unpacking matches actual retimer registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_fixed_vs_pe_retimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.c

Purpose: centralizes low-level DPCD read/write access and enforces DisplayPort address partitioning constraints so AUX transactions do not illegally cross mandatory DPCD windows.

Important APIs/functions: exported `core_link_read_dpcd` and `core_link_write_dpcd` wrap `dm_helpers_dp_read_dpcd`/`dm_helpers_dp_write_dpcd`. Internal helpers define DPCD address ranges, detect intersections, compute the next partition size, extend reads that touch mandatory single-transaction blocks, and reduce extended replies back to the caller buffer.

Control flow: reads may be extended when the request intersects mandatory blocks such as LTTPR tunable PHY fields. The extended request is then partitioned into legal chunks, read sequentially, and reduced back to the requested subrange. Writes are partitioned only; they do not use mandatory block extension.

State/persistence: no persistent state. It observes `link->aux_access_disabled`; when AUX access is disabled, internal read/write helpers return `DC_OK` without touching hardware.

Dependencies/integration: includes DRM DP helper definitions, `dm_helpers`, `link_service`, and `dpcd_defs`. Nearly all DP training, eDP panel, and capability code depends on these wrappers.

Risks: the partition table must cover the full DPCD address space without gaps; otherwise `dpcd_get_next_partition_size` can loop forever. `dpcd_reduce_address_range` appears to copy from the caller buffer into the extended buffer before freeing, which is suspicious for reads and should be reviewed if read-extension bugs appear. Allocation failure only asserts.

Test signals: unit/static tests for partition boundaries, reads that span LTTPR/FEC windows, mandatory-block extension, AUX-disabled behavior, and error propagation from `dm_helpers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.h

Purpose: declares the common DPCD read/write wrappers used by link protocol code.

Important APIs: `core_link_read_dpcd(struct dc_link *, uint32_t address, uint8_t *data, uint32_t size)` and `core_link_write_dpcd(struct dc_link *, uint32_t address, const uint8_t *data, uint32_t size)` return `enum dc_status`.

Control flow/state: all behavior is implemented in the `.c` file; the header defines the dependency contract for callers that should use partition-aware DPCD access instead of raw helper calls.

Dependencies/integration: includes `link_service.h` and `dpcd_defs.h`. It is widely used by DP training, eDP panel control, and DPIA code.

Risks: consumers assume these calls handle partitioning and may pass ranges crossing repeater/FEC boundaries; bypassing this header risks spec-violating AUX transactions.

Test signals: compile coverage across link protocol modules and runtime DPCD transactions on sinks with LTTPRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.c

Purpose: manages eDP panel mode, backlight control, panel power sequencing, ILR optimization, PSR, Panel Replay, ALPM, ASSR, and related firmware context programming.

Important APIs/functions: panel mode is handled by `dp_get_panel_mode`/`dp_set_panel_mode`; AUX/nits backlight by `edp_set_backlight_level_nits`, `edp_get_backlight_level_nits`, `edp_backlight_enable_aux`, and `set_default_brightness_aux`; PWM/ABM backlight by `edp_set_backlight_level`, `edp_get_backlight_level`, and `edp_get_target_backlight_pwm`; power/timing by `edp_panel_backlight_power_on`, `edp_set_panel_power`, `edp_wait_for_t12`, `edp_receiver_ready_T9`, and `edp_receiver_ready_T7`; PSR by `edp_setup_psr`, `edp_set_psr_allow_active`, `edp_get_psr_state`, `edp_get_psr_residency`, and `edp_set_sink_vtotal_in_psr_active`; Replay by `edp_setup_freesync_replay`, `edp_set_replay_allow_active`, `edp_get_replay_state`, `edp_send_replay_cmd`, `edp_set_coasting_vtotal`, and residency/power helpers.

Control flow: mode selection checks external encoder branch IDs/names for special converter behavior before using eDP DPCD caps. Backlight paths choose VESA AUX, AMD AUX, OLED defaults, ABM, panel controller, or firmware depending on caps and control type. Power sequencing orders VDD, HPD wait, backlight, and RX power according to eDP direction. PSR setup clears sink config, fills DPCD PSR bits, enables ALPM/vtotal control when supported, builds a `psr_context` from stream/timing/link/ASIC state, then copies settings into DMUB PSR or DMCU. Replay follows a similar pattern with replay DPCD config, ALPM, and DMUB replay context.

State/persistence: updates `link->panel_mode`, `link->psr_settings`, `link->replay_settings`, `link->panel_cntl->stored_backlight_registers`, and DPCD registers. It reads `dc->current_state` pipe mappings and persistent debug/config/caps flags.

Dependencies/integration: uses `link_dpcd`, `link_dp_capability`, `dm_helpers`, ASIC IDs, `link_dp_phy`, DMUB PSR/Replay services, `abm`, resource helpers, and panel replay helpers. It crosses HWSS, DMCU, DMUB, ABM, panel controller, PSP, and current resource state boundaries.

Risks: many functions return success after partial behavior for DDS or unsupported paths. DPCD helper truthiness is easy to misread because `DC_OK` is zero. PSR/Replay setup is sensitive to panel instance lookup, stream timing, firmware availability, and ASIC-specific workarounds. Power sequencing delays are panel-specific and failures can cause blanking or hangs.

Test signals: eDP panel power-on/off sequencing, AUX and PWM backlight on OLED/non-OLED panels, ILR optimization decisions with BIOS-programmed rates, PSR v1/v2 enable/state/residency, FreeSync Replay/ALPM configuration, ASSR via PSP/DMUB, HPD-ready waits, and suspend/resume with stored backlight state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.h

Purpose: declares the eDP panel-control surface for link code and display core.

Important APIs: exposes panel mode, AUX/PWM backlight, PSR, Replay, ILR optimization, ALPM, power sequencing, receiver readiness, SmartMux support, and ASSR programming functions. Notable signatures include `edp_setup_psr`, `edp_setup_freesync_replay`, `edp_set_psr_allow_active`, `edp_set_replay_allow_active`, and `edp_set_panel_power`.

Control flow/state: the header groups functions that mutate `dc_link` panel, PSR, Replay, backlight, and DPCD state. Callers must provide valid stream/pipe context for PSR/Replay and hardware backlight operations.

Dependencies/integration: includes `link_service.h`, which supplies `dc_link`, stream, timing, and panel-related type visibility. Implementations integrate with HWSS, DPCD, ABM, DMCU/DMUB, and PSP.

Risks: this is a broad API with many feature-specific booleans; callers must understand whether a `true` return means feature configured, no-op success, or unsupported-but-not-fatal behavior.

Test signals: compile coverage from DC link, PSR, Replay, and backlight callers; runtime panel feature probes for every exported path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_edp_panel_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.c

Purpose: provides basic HPD state, enable/disable, filter programming, and GPIO-to-HPD-source discovery. It intentionally avoids higher-level detection policy.

Important APIs/functions: `link_get_hpd_state`, `link_enable_hpd`, `link_disable_hpd`, `link_enable_hpd_filter`, `program_hpd_filter`, `link_get_hpd_gpio`, and `get_hpd_line`.

Control flow: HPD state and enable/disable delegate to `link_enc->funcs` when a link encoder exists. Filter enable updates `link->is_hpd_filter_disabled` and programs per-signal connect/disconnect delays: HDMI/DVI get 500/100 ms, DP/MST get 80/0 ms, and eDP/LVDS/default skip filtering. GPIO discovery reads BIOS HPD info and GPIO pin info, creates an IRQ GPIO, maps IRQ source to `HPD_SOURCEID*`, and destroys the temporary GPIO.

State/persistence: mutates `link->is_hpd_filter_disabled`; otherwise it is a facade over encoder and GPIO-service state.

Dependencies/integration: depends on `gpio_service_interface`, `dc_bios`, link encoder function tables, and IRQ source definitions. `link_hpd.h` also declares DPIA HPD query, implemented elsewhere.

Risks: missing `link_enc` means false/no-op behavior; filter programming asserts in one disabled path. GPIO fallback is only used for DCE/DCN versions up to 4.01, so newer paths depend on encoder mapping.

Test signals: HPD high/low query, filter delay programming per connector type, BIOS GPIO mapping to HPD source IDs, no-link-encoder safety, and MST/SST switch behavior with DP filter timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.h

Purpose: declares basic HPD helpers for link protocol code.

Important APIs: `get_hpd_line`, `program_hpd_filter`, `dpia_query_hpd_status`, `link_get_hpd_state`, `link_get_hpd_gpio`, `link_enable_hpd`, `link_disable_hpd`, and `link_enable_hpd_filter`.

Control flow/state: this header exposes both encoder-backed HPD operations and BIOS/GPIO discovery helpers. `dpia_query_hpd_status` is declared here for USB4 tunnel HPD integration but is implemented outside this file pair.

Dependencies/integration: includes `link_service.h` for `dc_link`, BIOS, GPIO service, and HPD source types.

Risks: users may assume all declarations are implemented in `link_hpd.c`; DPIA HPD status is separate. Callers must handle `NULL` GPIO returns and unknown HPD source IDs.

Test signals: compile/link coverage for DPIA and non-DPIA HPD users plus connector-type HPD filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/Makefile

Purpose: contributes MMHUBBUB/MCIF writeback object files to the AMD display build.

Important build variables: `MMHUBBUB_DCN20`, `MMHUBBUB_DCN32`, `MMHUBBUB_DCN35`, and `MMHUBBUB_DCN42` name generation-specific objects. Each is expanded through `$(AMDDALPATH)/dc/mmhubbub/<generation>/` and appended to `AMD_DISPLAY_FILES`.

Control flow: DCN20, DCN32, and DCN35 are included only under `ifdef CONFIG_DRM_AMD_DC_FP`; DCN42 is appended outside that guard.

State/persistence: no runtime state; build state is the accumulated `AMD_DISPLAY_FILES` variable.

Dependencies/integration: depends on top-level AMD display Makefile variables and the object files produced by the generation folders.

Risks: the guard difference means DCN42 can be built in configurations where earlier MMHUBBUB generations are not. Missing object paths or inconsistent `CONFIG_DRM_AMD_DC_FP` assumptions will surface as build failures.

Test signals: kernel build matrix with and without `CONFIG_DRM_AMD_DC_FP`, and link coverage for DCN42 references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.c

Purpose: implements DCN2.0 MCIF writeback buffer manager programming for display writeback.

Important APIs/functions: `dcn20_mmhubbub_construct` installs `dcn20_mmhubbub_funcs`; exported helpers include `mmhubbub2_config_mcif_irq`, `mmhubbub2_enable_mcif`, `mmhubbub2_disable_mcif`, and `mcifwb2_dump_frame`. Private helpers program buffer addresses/pitches/sizes/warmup and arbitration/watermark registers.

Control flow: buffer configuration locks buffer manager state, writes four luma and chroma buffer addresses with high bits, zeros offsets, computes luma/chroma size from pitch and destination height, enables address fences, writes pitch, and sets warmup pitch. Arbitration writes time-per-pixel, four urgent watermarks, four p-state watermarks, max scaled time, slice size, and arbitration slice. IRQ configuration updates software/VCE interrupt enables. Enable/disable toggles `MCIF_WB_BUFMGR_ENABLE`.

State/persistence: stores context, instance, register, shift, and mask pointers in `struct dcn20_mmhubbub`; hardware register state persists in MCIF/WBIF blocks. `mcifwb2_dump_frame` locks buffers, copies luma/chroma memory, unlocks, and fills dump metadata.

Dependencies/integration: uses `reg_helper`, `resource`, `mcif_wb`, and the register/mask definitions in the header. Later DCN implementations reuse its enable/disable, IRQ, and dump helpers.

Risks: address macros assume 256-byte alignment and 40-bit split behavior. Buffer copy sizes trust pitch/height parameters. Watermark and arbitration values must match timing/QoS calculations.

Test signals: writeback capture across planar/packed formats, four-buffer cycling, IRQ enable/disable, overrun handling, dump-frame correctness, and register programming traces for address high/low fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h

Purpose: defines the DCN2.0 MMHUBBUB register map, field lists, object layout, and public helper prototypes.

Important APIs/types: `TO_DCN20_MMHUBBUB`, `MCIF_WB_COMMON_REG_LIST_DCN2_0`, `MCIF_WB_COMMON_MASK_SH_LIST_DCN2_0`, `MCIF_WB_REG_FIELD_LIST_DCN2_0`, and `MCIF_WB_REG_VARIABLE_LIST_DCN2_0` generate register/mask/shift structures. Defines `struct dcn20_mmhubbub_registers`, `mask`, `shift`, and `struct dcn20_mmhubbub`.

Control flow/integration: ASIC resource code provides concrete register lists and calls `dcn20_mmhubbub_construct`; function tables then expose MCIF operations through the generic `mcif_wb` base.

State/persistence: the object stores `mcif_wb` base plus const register/shift/mask pointers. Runtime hardware state is manipulated by functions in the `.c` file.

Dependencies: includes `mcif_wb` through the implementation and relies on register macro definitions such as `SRI`/`SF` from surrounding DCN resource code.

Risks: macro lists are long and tightly coupled to generated register headers. A missing field can break later code that conditionally checks masks, such as VCE slice interrupt support.

Test signals: compile-time construction for DCN2.0 resources, register list completeness, and writeback feature tests using every function pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn20/dcn20_mmhubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.c

Purpose: implements DCN3.2 MMHUBBUB/MCIF writeback behavior, reusing DCN2.0 helpers where compatible and adding memory warmup support.

Important APIs/functions: `dcn32_mmhubbub_construct` installs `dcn32_mmhubbub_funcs`. Private helpers `mmhubbub32_warmup_mcif`, `mmhubbub32_config_mcif_buf`, and `mmhubbub32_config_mcif_arb` override warmup, buffer, and arbitration behavior.

Control flow: warmup shifts base address/region/increment by 5 bits, enables warmup with software interrupt, waits for completion, acknowledges, then disables warmup. Buffer setup writes four luma/chroma address pairs and sizes/pitch but omits some DCN20 offset/warmup-pitch programming. Arbitration writes time-per-pixel, urgent watermarks through `MCIF_WB_WATERMARK`, p-state watermarks through `MCIF_WB_NB_PSTATE_LATENCY_WATERMARK`, max scaled time, slice size, and larger DCN32 arbitration units.

State/persistence: uses `struct dcn30_mmhubbub` base object with DCN32 register maps. Hardware state persists in MCIF and MMHUBBUB warmup registers.

Dependencies/integration: reuses `mmhubbub2_enable_mcif`, `disable`, `config_irq`, and `dump_frame`; depends on `dcn32_mmhubbub.h`, `dcn30_mmhubbub`, `reg_helper`, `resource`, and `mcif_wb`.

Risks: warmup waits can time out; address/increment units must match hardware. Changed watermark mask registers from DCN20 make copy/paste regressions likely. Reused DCN20 dump/IRQ helpers must remain field-compatible.

Test signals: memory warmup completion/timeout, writeback capture on DCN3.2, watermark programming, arbitration slice values, and function-table compatibility with generic `mcif_wb` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.h

Purpose: provides DCN3.2 MMHUBBUB register and mask/shift macro lists plus constructor declaration.

Important APIs/types: `MCIF_WB_COMMON_REG_LIST_DCN32` maps MCIF and MMHUBBUB registers using `SRI2`, including warmup registers. `MCIF_WB_COMMON_MASK_SH_LIST_DCN32` lists fields for buffer manager, watermarks, QoS, security, resolution, and warmup control. Exports `dcn32_mmhubbub_construct`.

Control flow/integration: resource code uses these macros to build typed register structures compatible with `struct dcn30_mmhubbub`, then constructor installs DCN32 function table.

State/persistence: header declares register metadata only. Runtime state lives in the `dcn30_mmhubbub` instance and hardware registers.

Dependencies: includes DCN20 and DCN30 MMHUBBUB headers to reuse base types and field lists.

Risks: DCN32 has a different register namespace for some watermarks and warmup fields; incorrect macro mapping can silently program wrong addresses.

Test signals: build coverage for DCN32 resource creation, warmup field programming, and writeback register access smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.c

Purpose: adapts the DCN3.2 MMHUBBUB implementation for DCN3.5 and adds fine-grain clock-gating control.

Important APIs/functions: `dcn35_mmhubbub_construct` delegates to `dcn32_mmhubbub_construct` with casts from DCN3.5 register/mask/shift structures to DCN3.0-compatible base structures. `dcn35_mmhubbub_set_fgcg` writes `MMHUBBUB_FGCG_REP_DIS` with the inverse of the requested enable state.

Control flow: construction is inherited; no new writeback buffer or arbitration function table is created. FGC gating is a direct register update through DCN3.5 typed register macros.

State/persistence: stores the same `dcn30_mmhubbub` base state as DCN32. FGC gating persists in `MMHUBBUB_CLOCK_CNTL`.

Dependencies/integration: includes `dcn35_mmhubbub.h` and `reg_helper`; depends on DCN32 compatibility for all MCIF operations.

Risks: the cast-based constructor assumes DCN3.5 register structures are layout-compatible with DCN3.0/DCN3.2 expectations plus appended fields. Misordered macro fields would break inherited operations.

Test signals: DCN3.5 writeback construction, inherited writeback capture, and toggling FGC gating while checking `MMHUBBUB_CLOCK_CNTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.h

Purpose: defines DCN3.5 MMHUBBUB register structures and FGC clock-gating API.

Important APIs/types: `MCIF_WB_REG_VARIABLE_LIST_DCN3_5` extends DCN3.0 variables with `MMHUBBUB_CLOCK_CNTL`; `MCIF_WB_COMMON_MASK_SH_LIST_DCN3_5` extends DCN32 fields with clock-control fields; `MCIF_WB_REG_FIELD_LIST_DCN3_5` wraps inherited fields and added clock fields. Defines DCN3.5 register/mask/shift structs and exports constructor plus `dcn35_mmhubbub_set_fgcg`.

Control flow/integration: resource code uses this header to instantiate a DCN3.5 MMHUBBUB object that reuses DCN32 functions while allowing generation-specific clock control.

State/persistence: metadata only; the associated runtime object is still `struct dcn30_mmhubbub`.

Dependencies: includes `mcif_wb` and DCN32 header.

Risks: the nested struct field-list macro differs from simple flat lists; consumers must use the matching DCN35 casts/macros. FGC disable polarity is inverted in implementation.

Test signals: compile-time register structure initialization and runtime FGC enable/disable register verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn35/dcn35_mmhubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c

Purpose: provides DCN4.2 MMHUBBUB fine-grain clock-gating control using the DCN3.5 register layout.

Important API: `dcn42_mmhubbub_set_fgcg(struct dcn30_mmhubbub *mcif_wb30, bool enabled)` writes `MMHUBBUB_CLOCK_CNTL.MMHUBBUB_FGCG_REP_DIS` to `!enabled`.

Control flow: the function is a single register update; there is no constructor or writeback behavior override in this file.

State/persistence: changes persistent hardware clock-control state. It relies on `mcif_wb30` carrying register pointers compatible with `dcn35_mmhubbub_registers`, shift, and mask structs.

Dependencies/integration: includes DCN35 and DCN42 headers plus `reg_helper`. It is used by DCN4.2 resource code when FGC gating must be toggled.

Risks: cast compatibility with DCN35 layout is assumed. The register field is disable-polarity, so incorrect boolean handling reverses the requested behavior.

Test signals: DCN4.2 clock-gating toggles, register readback, and display/writeback stability with FGC on and off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.h

Purpose: declares the DCN4.2 MMHUBBUB FGC clock-gating helper.

Important API: `dcn42_mmhubbub_set_fgcg(struct dcn30_mmhubbub *mcif_wb30, bool enabled)`.

Control flow/state: no state in the header; callers pass a DCN30-style MMHUBBUB object with DCN4.2/DCN35-compatible register metadata.

Dependencies/integration: includes `mcif_wb`, DCN32, and DCN35 MMHUBBUB headers so the implementation can reuse inherited types and register layout.

Risks: no constructor is declared here, so object setup must come from resource code or inherited constructors. Header guard is present but lacks a trailing double underscore convention, matching nearby DCN35 style.

Test signals: build coverage for DCN4.2 resource code and runtime FGC register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn42/dcn42_mmhubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/Makefile

Purpose: contributes generation-specific MPC object files to the AMD display build.

Important build variables: defines `MPC_DCN10`, `MPC_DCN20`, `MPC_DCN30`, `MPC_DCN32`, `MPC_DCN401`, and `MPC_DCN42`, expands each through `$(AMDDALPATH)/dc/mpc/<generation>/`, and appends them to `AMD_DISPLAY_FILES`.

Control flow: all MPC generation object additions are under `ifdef CONFIG_DRM_AMD_DC_FP`.

State/persistence: no runtime state; build state is the appended `AMD_DISPLAY_FILES` list.

Dependencies/integration: depends on the top-level AMD display Makefile providing `AMDDALPATH` and consuming `AMD_DISPLAY_FILES`.

Risks: missing generation object files or an incorrect config guard will break builds for affected ASIC families. Because all objects are behind FP, non-FP configurations must not reference these MPC implementations.

Test signals: kernel build matrix with `CONFIG_DRM_AMD_DC_FP` enabled/disabled and generation-specific resource link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.c

Purpose: implements the DCN1.0 Multiple Pipe/Plane Combiner (MPC/MPCC) base behavior for composing DPP planes into OPP outputs.

Important APIs/functions: `dcn10_mpc_construct` installs the DCN10 `mpc_funcs`. Key operations include `mpc1_insert_plane`, `mpc1_remove_mpcc`, `mpc1_mpc_init`, `mpc1_mpc_init_single_inst`, `mpc1_init_mpcc_list_from_hw`, `mpc1_set_bg_color`, `mpc1_update_stereo_mix`, `mpc1_read_mpcc_state`, `mpc1_cursor_lock`, and `mpc1_get_mpc_out_mux`.

Control flow: insertion validates MPCC availability, links the new MPCC into the in-memory tree above a requested node or at the bottom, programs top/bottom selectors, OPP ID, update-lock mapping, output mux, blending, stereo mix, and in-use mask. Removal unlinks top/middle/bottom nodes, updates mux/selectors/mode, clears hardware selectors, and clears in-memory `dpp_id`/`mpcc_bot`. Init disconnects every MPCC and output mux. Hardware reconstruction reads mux/top/bottom/OPP registers to rebuild `tree->opp_list`.

State/persistence: tracks `mpcc_in_use_mask`, `num_mpcc`, and `mpc->mpcc_array` linked-list state; persistent hardware state lives in MPCC selector/control/status and MUX registers.

Dependencies/integration: uses `reg_helper` and generic `mpc.h` types. DCN20 reuses many DCN10 tree functions while overriding blending, color, gamma, and idle behavior.

Risks: linked-list corruption can create cycles; assertions guard some but not all traversal cases. In-memory tree and hardware mux state must stay synchronized across insert/remove/resume. Background color writes target the bottommost MPCC.

Test signals: multi-plane composition ordering, insert/remove top/middle/bottom, resume reconstruction from hardware, idle wait/assert paths, stereo mix programming, cursor lock, and mux readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.h

Purpose: defines DCN1.0 MPC register lists, field metadata, object layout, and exported base MPCC tree operations.

Important APIs/types: `TO_DCN10_MPC`, `MPC_COMMON_REG_LIST_DCN1_0`, `MPC_OUT_MUX_COMMON_REG_LIST_DCN1_0`, `MPC_COMMON_REG_VARIABLE_LIST`, `MPC_COMMON_MASK_SH_LIST_DCN1_0`, and `MPC_REG_FIELD_LIST`. Defines `struct dcn_mpc_registers`, `dcn_mpc_shift`, `dcn_mpc_mask`, and `struct dcn10_mpc`.

Control flow/integration: resource code instantiates register/mask/shift data and calls `dcn10_mpc_construct`; later generations can reuse exported `mpc1_*` functions for tree management.

State/persistence: object state includes generic `struct mpc`, `mpcc_in_use_mask`, `num_mpcc`, and register metadata pointers.

Dependencies: includes `mpc.h`, which defines generic MPC/MPCC trees, blending config, stereo config, and function table contracts.

Risks: generation-specific derived structs often rely on DCN10 layout compatibility. Register array sizes must match `MAX_MPCC`/`MAX_OPP`, and callers must not use unavailable mux registers.

Test signals: compile-time register list generation, DCN10 construction, and reuse by DCN20+ implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn10/dcn10_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c

Purpose: extends the DCN10 MPC implementation for DCN2.0 with richer blending controls, output denorm/clamp, output CSC, output gamma LUT programming, MPCC disabled-state handling, and updated function table behavior.

Important APIs/functions: `dcn20_mpc_construct` installs `dcn20_mpc_funcs`. Exports include `mpc2_update_blending`, `mpc2_set_denorm`, `mpc2_set_denorm_clamp`, `mpc2_set_output_csc`, `mpc2_set_ocsc_default`, `mpc20_power_on_ogam_lut`, and `mpc2_set_output_gamma`. It reuses DCN10 insert/remove/init/cursor/mux/bg-color helpers.

Control flow: blending programs alpha, global gains, background BPC, bottom gain mode, and top/bottom gain registers. Denorm maps output color depth to hardware denorm mode and clamp registers. CSC selects the inactive A/B coefficient bank based on current mode, programs matrices, then flips mode for frame-boundary update. Gamma reads current RAM A/B/bypass state, powers OGAM memory, selects the alternate RAM, programs transfer-function regions and PWL data through sequenced register writes, applies the DEDCN20-305 workaround when needed, and switches OGAM mode.

State/persistence: tracks inherited `mpcc_in_use_mask`, `num_mpcc`, and `mpcc_array`; updates persistent MPCC control, gain, denorm, CSC, OGAM RAM, LUT, and status registers. `mpc2_read_mpcc_state` also reports gamma mode.

Dependencies/integration: includes `dcn20_mpc.h`, `reg_helper`, `dc`, `mem_input`, and color-management helper code from `dcn10_cm_common`. It is used by DCN2 resource construction and later derived MPC implementations.

Risks: double-buffered CSC/gamma bank selection must match current hardware status or visible glitches occur. Gamma programming assumes valid `pwl_params` and point counts. Workaround behavior depends on debug/workaround flags and OTG locking assumptions. Idle assertions differ from DCN10 because disabled state is explicit.

Test signals: plane blending with global/top/bottom gains, output CSC changes across color spaces, denorm/clamp by bit depth, gamma LUT enable/bypass/A-B switching, DEDCN20-305 workaround, MPCC idle/disabled assertions, and inherited tree insert/remove coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c -->
