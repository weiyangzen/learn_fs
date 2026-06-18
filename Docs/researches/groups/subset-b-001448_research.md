# Research: subset-b-001448

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.c

## Purpose

`link_hwss_dio.c` implements the Display Input Output link hardware sequencing surface for legacy DIO-backed links. It adapts generic `struct link_hwss` operations to DIO link encoders and stream encoders for DP, HDMI, DVI, LVDS, audio packets, MST allocation tables, lane settings, and DP PHY test patterns.

## Important APIs, Types, And Functions

- `setup_dio_stream_encoder()` connects DIG back end to front end for non-RGB signals, enables the stream encoder, maps it to a link encoder, sets DIO pixels-per-cycle input mode, and enables FIFO.
- `reset_dio_stream_encoder()` reverses FIFO/input/stream enable state and disconnects DIG FE/BE for non-RGB signals.
- `setup_dio_stream_attribute()` programs DP, HDMI TMDS, DVI, or LVDS timing attributes and DP trace points.
- `enable_dio_dp_link_output()` and `disable_dio_link_output()` call link encoder output enable/disable functions for SST/MST DP.
- `set_dio_dp_link_test_pattern()`, `set_dio_dp_lane_settings()`, and `update_dio_stream_allocation_table()` forward DP training/test/MST table operations to the link encoder.
- Audio APIs route DP audio setup/enable/disable or HDMI audio setup/disable through `stream_enc->funcs`.
- `can_use_dio_link_hwss()` and `get_dio_link_hwss()` expose the static DIO HWSS vtable.

## Control Flow

The vtable maps generic link programming to per-resource function pointers. Most entry points first resolve `link_enc` from `pipe_ctx->link_res.dio_link_enc`; if `unify_link_enc_assignment` is disabled, they instead query `link_enc_cfg_get_link_enc(link)`. Null link encoders assert and return.

DP stream setup order is significant: connect DIG FE/BE, trace, enable stream, map stream to link, set input mode, then enable FIFO. Reset runs the reverse subset and records DP trace after disconnect. Attribute programming dispatches by signal type and uses DPCD caps for DP split SDP support.

## State And Persistence Behavior

The file does not persist data. It mutates hardware through function pointers and updates observable in-memory/link state indirectly through encoder programming. DP trace source-sequence calls record source-side milestones. Audio packet enable/disable changes stream encoder packet and mute state. MST allocation updates affect link encoder allocation tables but the owning software table is maintained by DPMS code.

## Dependencies And Integration Points

It depends on `core_types.h`, `link_hwss_dio.h`, `link_enc_cfg.h`, stream encoder and link encoder function tables, `dc_is_*_signal()` helpers, DP trace service hooks, and `struct pipe_ctx` resource assignments. `link_dpms.c`, DP training, and `get_link_hwss()` dispatch through this vtable for DIO links and DIO-based DPIA variants.

## Risks And Edge Cases

- The non-unified encoder path relies on `link_enc_cfg_get_link_enc()` being valid at the moment of programming.
- Some stream encoder function pointers are optional while others are called unconditionally, so resource construction must match signal type.
- DP trace calls assume `link_srv` is populated.
- Audio mute is always toggled even if DP audio enable is skipped, which is intended but sensitive to stream encoder implementation.
- Mapping stream to link uses `transmitter - TRANSMITTER_UNIPHY_A`; unexpected transmitter values would produce bad indices.

## Test Signals

Build tests catch vtable signature drift. Runtime coverage should include DIO DP SST/MST, HDMI/DVI/LVDS, unified and dynamic link encoder assignment, audio enable/disable, MST payload table updates, DP test patterns, and lane setting changes. DP trace events around DIG connect/disconnect, stream attribute setup, link PHY enable/disable, and audio transitions are useful observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.h

## Purpose

`link_hwss_dio.h` declares the DIO link hardware-sequencing interface used by generic link code and sibling HWSS variants. It exposes the DIO vtable getter, applicability check, stream setup/reset/attribute routines, DP link output and training helpers, audio helpers, and MST allocation update hook.

## Important APIs, Types, And Functions

The header declares `get_dio_link_hwss()`, `can_use_dio_link_hwss()`, `set_dio_throttled_vcp_size()`, `setup_dio_stream_encoder()`, `reset_dio_stream_encoder()`, `setup_dio_stream_attribute()`, `enable_dio_dp_link_output()`, `disable_dio_link_output()`, `set_dio_dp_link_test_pattern()`, `set_dio_dp_lane_settings()`, `setup_dio_audio_output()`, `enable_dio_audio_packet()`, `disable_dio_audio_packet()`, and `update_dio_stream_allocation_table()`. It depends on `link_hwss.h` and `link_service.h` for `struct link_hwss`, `struct dc_link`, `struct pipe_ctx`, `struct link_resource`, and DP lane/settings types.

## Control Flow

There is no runtime control flow. The declarations let the base DIO implementation and specialized wrappers share operations. Fixed-VS/PE retimer and DPIA variants call these helpers while overriding selected vtable extension functions.

## State And Persistence Behavior

The header stores no state. All state changes happen in `link_hwss_dio.c` through hardware function pointers and caller-owned `pipe_ctx`, `dc_link`, and `link_resource` objects.

## Dependencies And Integration Points

It is included by DIO HWSS consumers and retimer/DPIA specializations. Signature compatibility with `link_hwss.h` is important because the static vtable in the `.c` file assigns these routines to generic function-pointer slots.

## Risks And Edge Cases

Prototype drift breaks link service dispatch at build time. Because many functions take generic pointers, wrong signal/resource combinations will compile but fail at runtime. The header exposes low-level helpers directly, so specialized HWSS files must preserve DIO ordering assumptions when wrapping them.

## Test Signals

Kernel build coverage catches duplicate declarations, missing types, and signature mismatches. Runtime coverage is indirect through DIO DP/HDMI/DVI/LVDS link bring-up, MST allocation, audio, and training/test-pattern paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.c

## Purpose

`link_hwss_dio_fixed_vs_pe_retimer.c` specializes DIO DP hardware sequencing for external fixed voltage swing/pre-emphasis retimer paths. It reuses the normal DIO stream/audio/MST operations but overrides DP link output and test-pattern programming to emit vendor LTTPR/retimer configuration sequences over AUX/DDC.

## Important APIs, Types, And Functions

- `dp_dio_fixed_vs_pe_retimer_lane_cfg_to_hw_cfg()` maps current lane count to vendor DP type bytes, returning `0xF2` for four lanes and `0x12` otherwise.
- `dp_dio_fixed_vs_pe_retimer_exit_manual_automation()` writes a sequence of vendor register payloads through `configure_fixed_vs_pe_retimer()` to restore automation.
- `set_dio_fixed_vs_pe_retimer_dp_link_test_pattern_override()` handles 128b/132b retimer overrides for 80-bit custom and D102 patterns, including deprogramming old overrides.
- `set_dio_fixed_vs_pe_retimer_dp_link_test_pattern()` wraps the override path and falls back to `dp_set_phy_pattern`.
- `enable_dio_fixed_vs_pe_retimer_program_4lane_output()` writes five vendor payloads before four-lane output.
- `enable_dio_fixed_vs_pe_retimer_dp_link_output()` preprograms four-lane retimer state before normal DIO DP output.
- `requires_fixed_vs_pe_retimer_dio_link_hwss()` checks `link->chip_caps` for `AMD_EXT_DISPLAY_PATH_CAPS__DP_FIXED_VS_EN`.

## Control Flow

The static vtable is mostly the DIO vtable. Only `enable_dp_link_output` and `set_dp_link_test_pattern` are replaced. On link enable, four-lane settings trigger vendor retimer programming before the normal DIO PHY enable path. On test-pattern setup, the override path first gates on 128b/132b LTTPR support and non-null params, then either translates supported patterns into hardware pattern requests plus retimer writes or deprograms previous overrides and lets the caller fall back to the base link encoder pattern.

## State And Persistence Behavior

The file does not store private state. It changes retimer hardware state through repeated `link_srv->configure_fixed_vs_pe_retimer(link->ddc, data, len)` calls. It also depends on `link->current_test_pattern`, `pending_test_pattern` managed elsewhere, `cur_link_settings.lane_count`, and `dpcd_caps.lttpr_caps`.

## Dependencies And Integration Points

It includes `link_hwss_dio.h`, its own header, and `link_enc_cfg.h`. It integrates with DIO helpers, DP CTS/test-pattern code, DP training, and the link HWSS selector. The vendor payload transport is exposed by the DDC service through `link_srv`.

## Risks And Edge Cases

- Vendor byte sequences are opaque and order-sensitive.
- The lane configuration TODO notes missing USB-C orientation handling.
- Fallback pattern programming assumes a valid `link_enc`; unlike base DIO, the wrapper path does not assert-check after resolving it before fallback use.
- Override deprogramming is tied to `current_test_pattern` classifications; stale pattern state can leave retimer state mismatched.
- The 80-bit custom override only accepts a specific ten-byte pattern.

## Test Signals

Exercise DP 1.x and DP 2.x fixed-VS links, two-lane and four-lane modes, supported and unsupported PHY patterns, transitions from square/custom/D102 back to video, and link training retries. AUX/DDC transaction logs and DP trace entries after pattern setup and link PHY enable are primary diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.h

## Purpose

`link_hwss_dio_fixed_vs_pe_retimer.h` declares the DIO fixed-VS/PE retimer HWSS extension points and helper routines used by both DIO and HPO retimer variants.

## Important APIs, Types, And Functions

The header exposes `dp_dio_fixed_vs_pe_retimer_lane_cfg_to_hw_cfg()`, `dp_dio_fixed_vs_pe_retimer_exit_manual_automation()`, `enable_dio_fixed_vs_pe_retimer_program_4lane_output()`, `requires_fixed_vs_pe_retimer_dio_link_hwss()`, and `get_dio_fixed_vs_pe_retimer_link_hwss()`. It also declares `dp_dio_fixed_vs_pe_retimer_get_lttpr_write_address()`, but this declaration has no implementation in the reviewed `.c` file, so it is either implemented elsewhere in this source snapshot or is stale.

## Control Flow

The header has no executable flow. It allows the HPO fixed-VS/PE retimer implementation to reuse DIO retimer helpers for lane config, automation exit, and four-lane preprogramming.

## State And Persistence Behavior

No state is stored. Declared functions operate on `struct dc_link` and retimer hardware state through the link service.

## Dependencies And Integration Points

It includes `link_service.h` for `struct dc_link` and `struct link_hwss`. It is consumed by the DIO retimer implementation and `link_hwss_hpo_fixed_vs_pe_retimer_dp.c`.

## Risks And Edge Cases

The unimplemented or externally implemented `dp_dio_fixed_vs_pe_retimer_get_lttpr_write_address()` declaration is a maintenance risk if new callers expect it to link from this object. The header does not include `link_hwss.h` directly, so it relies on `link_service.h` to expose the needed incomplete types.

## Test Signals

Build/link tests catch missing definitions once a caller references every declaration. Runtime signals are fixed-VS link selection, retimer AUX write sequences, and successful test-pattern/training behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.c

## Purpose

`link_hwss_dpia.c` implements a DIO-style HWSS variant for USB4 DPIA endpoints. It reuses DIO stream/audio sequencing but customizes DP link output, test-pattern behavior, lane settings, and MST allocation updates for tunneled DP over DPIA.

## Important APIs, Types, And Functions

- `update_dpia_stream_allocation_table()` totals MST slots, calls `dc_process_dmub_set_mst_slots()` for the DPIA link index, logs previous slots, then optionally updates the DIO link encoder table.
- `set_dio_dpia_link_test_pattern()` only forwards `DP_TEST_PATTERN_VIDEO_MODE`; other patterns are ignored for DPIA.
- `set_dio_dpia_lane_settings()` is intentionally a no-op.
- `enable_dpia_link_output()` uses `enable_dpia_output()` when pre-training or unified assignment is enabled, passing DDC hardware instance, SST/MST DIG mode, and FEC readiness. Otherwise it falls back to `enable_dio_dp_link_output()`.
- `disable_dpia_link_output()` mirrors the enable path with `disable_dpia_output()` or normal DIO disable.
- `can_use_dpia_link_hwss()` requires flexible DIG mapping and either assignment support or a resolved DIO link encoder.

## Control Flow

The vtable extension block is initialized before base entries to match `link_hwss.h` layout. Stream encoder, attributes, and audio all dispatch to base DIO helpers. Link enable/disable resolve the link encoder according to `unify_link_enc_assignment`; if DPIA-specific encoder hooks exist, they are used, otherwise errors are logged or base DIO behavior is used depending on configuration.

## State And Persistence Behavior

The file mutates DMUB/DPIA MST slot state via `dc_process_dmub_set_mst_slots()`, link encoder output state, DIO stream encoder state through reused DIO helpers, and DP trace milestones. It does not own durable state; the software allocation table is owned by the caller and passed in.

## Dependencies And Integration Points

It depends on `link_hwss_dpia.h`, `link_hwss_dio.h`, `link_enc_cfg.h`, DIO link encoder functions, DMUB slot programming, and DP FEC decision service hooks. It is selected for USB4 DPIA links by generic HWSS selection and is used by DPMS MST/SST payload management.

## Risks And Edge Cases

- `status` and `prev_mst_slots_in_use` in `update_dpia_stream_allocation_table()` are static, which is unnecessary and could confuse concurrency analysis.
- Non-video test patterns are silently ignored for DPIA.
- Lane settings are a no-op, so training paths must not rely on source-side lane adjustment through this vtable.
- Missing `enable_dpia_output` or `disable_dpia_output` hooks only logs errors in DPIA mode.
- Slot total uses `uint8_t`; the valid DP MST slot range fits, but future expansion would need review.

## Test Signals

Use DPIA SST and MST bring-up, MST slot allocation/deallocation, FEC-ready combinations, unified and non-unified link encoder assignment, and pre-training enabled/disabled modes. DMUB MST slot logs, DP trace events, and USB4/DPIA HPD scenarios are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.h

## Purpose

`link_hwss_dpia.h` declares the DPIA HWSS vtable getter and applicability check, plus the DIG mode constants used when enabling tunneled SST or MST output.

## Important APIs, Types, And Functions

- `DIG_SST_MODE` is `0`; `DIG_MST_MODE` is `5`.
- `get_dpia_link_hwss()` returns the static DPIA `struct link_hwss`.
- `can_use_dpia_link_hwss()` checks whether a link/resource combination supports the DPIA sequencing path.

## Control Flow

There is no runtime flow in the header. The constants are consumed by `enable_dpia_link_output()` and `disable_dpia_link_output()` to tell the link encoder which DPIA output mode to program.

## State And Persistence Behavior

No state is held. The implementation changes DMUB slot state, DIO/DPIA encoder state, and trace state.

## Dependencies And Integration Points

It includes `link_hwss.h` and is part of the generic HWSS selection layer for USB4 DPIA links.

## Risks And Edge Cases

The DIG mode values are magic protocol constants; if encoder firmware expectations change, stale constants would break DPIA SST/MST selection. The header does not expose the no-op lane-setting behavior, so callers must rely on the vtable contract.

## Test Signals

Build coverage catches signature drift. Runtime validation should include USB4 DPIA SST/MST link enable/disable and MST payload table update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.c

## Purpose

`link_hwss_hpo_dp.c` implements link HWSS operations for HPO DP, the high-performance DP path used for 128b/132b DP 2.x style links. It programs HPO stream and link encoders, HPO-specific payload throttling, hblank symbol width, DP link PHY, MST allocation, and DP audio.

## Important APIs, Types, And Functions

- `set_hpo_dp_throttled_vcp_size()` programs VCP size on the HPO link encoder for a stream encoder instance.
- `set_hpo_dp_hblank_min_symbol_width()` derives hblank minimum symbol width from timing hblank, pixel clock, link bandwidth, and throttled VCP size.
- `setup_hpo_dp_stream_encoder()` enables an HPO stream encoder and maps it to an HPO link encoder.
- `reset_hpo_dp_stream_encoder()` disables the HPO stream encoder.
- `setup_hpo_dp_stream_attribute()` programs timing/colorimetry/DSC stream attributes and records a DP trace point.
- `enable_hpo_dp_link_output()` gates the symclk32 root clock on and enables link PHY using the legacy link encoder transmitter and HPD source.
- `disable_hpo_dp_link_output()` disables link, PHY, and clock gating.
- Static test-pattern and lane-setting helpers program HPO link test patterns and FFE.

## Control Flow

The vtable is HPO-specific for stream, link, audio, payload, and test operations. Enable flow checks `link_res->hpo_dp_link_enc`, turns on DCCG root clock gating if supported, and calls `enable_link_phy()`. Disable flow calls `link_disable()`, `disable_link_phy()`, and turns off the clock gate. The hblank helper guards division by checking effective DP bandwidth first.

## State And Persistence Behavior

The file mutates HPO stream encoder state, HPO link encoder state, DCCG clock gating state, audio packet state, and DP trace state. It relies on caller-owned `pipe_ctx->link_res` and `pipe_ctx->stream_res` assignments.

## Dependencies And Integration Points

It includes `dm_helpers.h`, `core_types.h`, `dccg.h`, and `clk_mgr.h`. DPMS payload code calls its vtable extensions for SST/MST 128b/132b allocation, throttled VCP, hblank symbol width, test patterns, and FFE.

## Risks And Edge Cases

- Missing HPO link encoder logs and returns, leaving higher layers responsible for failure handling.
- Hblank symbol width uses timing arithmetic with `pix_clk_100hz`; malformed timing can underflow hblank or divide badly if not validated.
- Lane settings use only `lane_settings[0].FFE_PRESET.raw`, assuming uniform FFE for the HPO encoder.
- `disable_hpo_dp_link_output()` indentation suggests nested operations but all are under the null check; functional behavior is still straightforward.

## Test Signals

Exercise DP 2.x SST and MST, DSC on HPO, VCP throttling, hblank symbol width updates, audio enable/disable, test patterns, FFE changes, and link output disable. Watch DCCG clock gate transitions and DP trace source sequence markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.h

## Purpose

`link_hwss_hpo_dp.h` declares the HPO DP HWSS interface for DP 2.x/HPO stream and link sequencing.

## Important APIs, Types, And Functions

The header declares throttled VCP, hblank minimum symbol width, stream encoder setup/reset/attribute, link output enable/disable, MST allocation update, audio setup/packet control, `get_hpo_dp_link_hwss()`, and `can_use_hpo_dp_link_hwss()`.

## Control Flow

The header has no runtime flow. It exposes routines assigned into the HPO DP `struct link_hwss` vtable and reused by the HPO fixed-VS/PE retimer specialization.

## State And Persistence Behavior

No state is stored. Implementations mutate HPO encoder, DCCG, audio, and trace state.

## Dependencies And Integration Points

It includes `link_hwss.h` and `link_service.h`. It is consumed by HPO DP implementation files and DPMS/HWSS selection code.

## Risks And Edge Cases

The prototype for `set_hpo_dp_hblank_min_symbol_width()` appears twice in the header. This is harmless in C because the declarations match, but it is a maintenance signal. As with DIO, most parameters are generic pointers, so type safety does not prevent mismatched resource usage.

## Test Signals

Build coverage catches signature drift. Runtime coverage comes from HPO DP SST/MST link enablement, payload allocation, audio, DSC PPS, test patterns, and FFE/lane-setting operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.c

## Purpose

`link_hwss_hpo_fixed_vs_pe_retimer_dp.c` specializes HPO DP sequencing for fixed voltage swing/pre-emphasis retimer paths. It reuses HPO DP stream/audio/payload operations and DIO retimer helpers while overriding HPO test-pattern, lane-setting, and link-output behavior for vendor retimer programming.

## Important APIs, Types, And Functions

- `dp_hpo_fixed_vs_pe_retimer_set_tx_ffe()` maps per-lane FFE preset levels and no-deemphasis/no-preshoot masks into vendor register bytes and writes them through `configure_fixed_vs_pe_retimer()`.
- `dp_hpo_fixed_vs_pe_retimer_program_override_test_pattern()` programs a vendor SQ128-style square pattern sequence.
- `dp_hpo_fixed_vs_pe_retimer_set_override_test_pattern()` gates on 128b/132b support, translates square patterns to PRBS31 on the HPO encoder, programs vendor overrides, or deprograms previous overrides.
- `set_hpo_fixed_vs_pe_retimer_dp_link_test_pattern()` wraps the override and sleeps 50 ms after most pattern changes for retimer lock.
- `set_hpo_fixed_vs_pe_retimer_dp_lane_settings()` avoids source FFE changes during PHY test patterns and directly programs retimer FFE for square-pattern overrides.
- `enable_hpo_fixed_vs_pe_retimer_dp_link_output()` preprograms four-lane fixed-VS state before normal HPO DP output.

## Control Flow

The vtable inherits most HPO DP operations. On test-pattern programming, square patterns are handled by setting a PRBS31 source pattern and then writing a vendor retimer square pattern sequence. Non-square patterns may deprogram older custom/square overrides before falling back to HPO link encoder test-pattern programming. Lane settings branch on `pending_test_pattern` to avoid conflicting with active PHY pattern output.

## State And Persistence Behavior

There is no private state. The file mutates retimer register state over AUX/DDC, HPO link encoder state, HPO stream/audio state through inherited functions, and trace state. Behavior depends on `link->cur_link_settings.lane_count`, `pending_test_pattern`, `current_test_pattern`, chip caps, and LTTPR DPCD capabilities.

## Dependencies And Integration Points

It includes `link_hwss_hpo_dp.h`, its own header, and `link_hwss_dio_fixed_vs_pe_retimer.h`. DP training/test code reaches it through the selected HWSS vtable when the link uses HPO DP and the fixed-VS external path capability is present.

## Risks And Edge Cases

- Vendor FFE and test-pattern byte tables are opaque, order-sensitive, and only lightly validated.
- FFE preset `level` indexes a 16-entry table; upstream validation must keep levels in range.
- Retimer lock delay is skipped only for TPS2 training mode; timing-sensitive monitors may need coverage around other transitions.
- The lane-setting logic intentionally does not update HPO source FFE during PHY patterns, which can surprise callers expecting uniform behavior.

## Test Signals

Test DP 2.x fixed-VS HPO links with two and four lanes, square PHY patterns, PRBS/custom transitions, TPS modes, FFE preset changes, and link-training retries. AUX write traces and 50 ms pattern-lock behavior are important diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.h

## Purpose

`link_hwss_hpo_fixed_vs_pe_retimer_dp.h` declares the HPO DP fixed-VS/PE retimer HWSS selector helpers.

## Important APIs, Types, And Functions

It exposes `requires_fixed_vs_pe_retimer_hpo_link_hwss()` and `get_hpo_fixed_vs_pe_retimer_dp_link_hwss()`. The implementation delegates the requirement check to the DIO fixed-VS helper and returns a static HPO retimer `struct link_hwss`.

## Control Flow

No runtime flow exists in the header. Callers use these declarations when selecting an HPO DP HWSS variant based on link chip capabilities.

## State And Persistence Behavior

No state is held. The implementation mutates retimer, HPO encoder, and trace state.

## Dependencies And Integration Points

It includes `link_service.h` for link and HWSS types. It is consumed by HWSS selection code and the implementation file.

## Risks And Edge Cases

The small interface hides the fact that the implementation depends on DIO fixed-VS helpers. If those helper semantics change, HPO retimer behavior changes too. Build coverage is the main guard for signature drift.

## Test Signals

HPO DP fixed-VS link selection, successful DP 2.x training, PHY pattern programming, and retimer AUX write logs validate this interface indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.c

## Purpose

`link_hwss_virtual.c` provides a minimal no-op link HWSS for virtual links. Virtual streams do not need physical stream/link encoder setup, attribute programming, or link-output disable sequencing.

## Important APIs, Types, And Functions

`virtual_setup_stream_encoder()`, `virtual_setup_stream_attribute()`, and `virtual_reset_stream_encoder()` explicitly ignore `pipe_ctx`. `virtual_disable_link_output()` ignores link/resource/signal. `get_virtual_link_hwss()` returns a static vtable containing only those base operations.

## Control Flow

All operations return immediately. The vtable omits optional extension callbacks and audio callbacks, so callers must only use operations valid for virtual links.

## State And Persistence Behavior

The file does not mutate hardware or persistent software state. It exists to satisfy generic sequencing contracts without programming physical resources.

## Dependencies And Integration Points

It includes `link_hwss_virtual.h`, which includes `core_types.h`. DPMS and HWSS selection can use this vtable for virtual signal paths, while DPMS also has early returns for virtual streams.

## Risks And Edge Cases

If a caller assumes optional vtable members exist for a virtual link, it will dereference null function pointers. The no-op behavior also means any required virtual metadata must be handled outside this HWSS layer.

## Test Signals

Virtual display enable/disable should complete without physical encoder programming, DPCD/AUX activity, or audio packet operations. Build coverage catches vtable layout drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.h

## Purpose

`link_hwss_virtual.h` declares the no-op virtual link HWSS interface.

## Important APIs, Types, And Functions

It declares `virtual_setup_stream_encoder()`, `virtual_setup_stream_attribute()`, `virtual_reset_stream_encoder()`, and `get_virtual_link_hwss()`.

## Control Flow

There is no runtime flow in the header. The declarations are used by the virtual implementation and by HPO FRL code, which reuses virtual stream encoder setup/reset while supplying HDMI FRL stream attributes.

## State And Persistence Behavior

The header stores no state; the implementation intentionally does not mutate hardware.

## Dependencies And Integration Points

It includes `core_types.h` for `struct pipe_ctx` and `struct link_hwss`. It is integrated into HWSS selection for virtual links and as shared no-op scaffolding for HPO FRL.

## Risks And Edge Cases

The interface is intentionally sparse. Callers must not expect link output enable, audio, payload, or DP extension callbacks from the virtual HWSS.

## Test Signals

Build coverage validates prototypes. Runtime tests should verify virtual streams and FRL users of these no-op helpers do not accidentally attempt physical DIO/HPO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.c

## Purpose

`link_detection.c` owns link and receiver detection state for AMD Display Core links. It classifies connected sink signal types, probes HPD/DDC/AUX/DPCD/EDID, manages local and remote sink objects, queries HDCP and dongle capabilities, verifies DP link capability, starts/stops MST topology management, and handles DPIA/USB4 detection quirks.

## Important APIs, Types, And Functions

- `link_detect()` is the public detection entry. It detects the local sink, verifies link capability, delegates MST topology discovery when needed, and resets MST topology on disconnect.
- `link_detect_connection_type()` determines physical, analog, eDP, DPIA, and HPD-based connection type without downstream MST enumeration.
- `detect_link_and_local_sink()` is the central local-sink state machine. It disconnects old sinks, detects signal/caps, creates `dc_sink`, reads EDID/MCCS/SCDC, applies panel patches, queries HDCP, initializes DP trace, and handles eDP panel config.
- `detect_dp()` handles native DP versus passive dongle detection, active branch classification, DPCD capability retrieval, and external bridge quirks.
- `verify_link_capability()` chooses destructive training-based verification or non-destructive reported/max capability assignment.
- `discover_dp_mst_topology()` and `link_reset_cur_dp_mst_topology()` start/stop DRM MST topology helpers and maintain DPIA DSC workaround flags.
- `link_add_remote_sink()` and `link_remove_remote_sink()` manage MST remote sink references and EDID parsing.
- `link_is_hdcp14()`, `link_is_hdcp22()`, `link_get_status()`, and `link_clear_dprx_states()` expose state managed here.

## Control Flow

Detection begins with connection type. Analog links ignore HPD and use an EDID-header DDC probe, falling back to DAC load detection. eDP powers the panel and waits for HPD readiness unless power sequencing is disabled. DPIA links query tunneled HPD state and pending HPD flags. Physical digital links use HPD state.

When a connection exists, the function chooses signal/transaction type by connector. HDMI/DVI/LVDS/RGB are I2C. eDP reads eDP caps and current link settings. DP waits for USB-C alt mode if needed, detects DPCD caps through AUX or passive dongle identity through I2C, applies external bridge and DPIA tunnel rules, and may enable USB4 bandwidth allocation mode. It then creates a local sink, reads EDID, handles no-EDID analog/DP failure modes, reads MCCS/SCDC, adjusts HDMI/DVI/RGB sink signal interpretation, queries HDCP, and initializes panel config for eDP.

After local sink detection, DP capability verification may destructively turn streams off and train at known limits, or non-destructively use reported/max caps for eDP, DPIA, MST, unavailable encoders, or debug skip modes. MST-capable DP sinks are delegated to the MST topology manager, causing `link_detect()` to return false for upper-layer local handling while the MST manager owns downstream enumeration.

## State And Persistence Behavior

The file mutates many in-memory link fields: `local_sink`, `remote_sinks[]`, `sink_count`, `type`, `dpcd_caps`, `dpcd_sink_count`, `cur_link_settings`, `reported_link_cap`, `verified_link_cap`, `hdcp_caps`, `aux_mode`, `link_state_valid`, `wa_flags`, `panel_config`, `psr_settings`, `replay_settings`, `dongle_max_pix_clk`, and `dprx_states`. It manages sink reference counts with `dc_sink_retain()` and `dc_sink_release()`. It does not write on-disk state.

## Dependencies And Integration Points

It integrates with DDC/AUX helpers, DPCD/capability parsers, HPD helpers, DP training, DP PHY, DPIA bandwidth, eDP panel control, DP trace, DM EDID/MCCS/MST helpers, clock manager power-state hooks, and hardware sequencing callbacks for eDP power and analog load detect. `link_factory.c` installs these functions into `link_service`.

## Risks And Edge Cases

- Sink reference handling is delicate when replacing a same-EDID sink, aborting EDID reads, or downstream SST branch unplug occurs.
- Destructive verification turns streams off and trains; it is gated by several debug/config/resource checks but can still be disruptive.
- Passive dongle detection relies on retrying I2C signatures and inferred max pixel clocks.
- USB-C alt-mode polling has a 200 ms timeout and may fail early HPD events.
- DP no-EDID behavior intentionally keeps fail-safe DP connected, while HDMI/DVI no-EDID aborts.
- DPIA MST DSC always-on workaround is vendor/device-specific and must be cleared on topology reset.

## Test Signals

Coverage should include HDMI/DVI/LVDS/RGB, analog with DDC and load detect, DP native SST, DP passive HDMI/DVI dongles, active dongles, SST branch unplug, MST branch connect/disconnect, eDP resume and OLED AUX settings, USB-C alt-mode delay, DPIA HPD and bandwidth allocation mode, EDID same/change, bad/no EDID, HDCP 1.4/2.2 capability queries, and destructive/non-destructive link verification. Logs under hotplug, EDID parser, DP trace, and MST topology are primary runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.h

## Purpose

`link_detection.h` declares the public link detection and sink-management interface installed into `struct link_service`.

## Important APIs, Types, And Functions

It declares `link_detect()`, `link_detect_connection_type()`, `link_add_remote_sink()`, `link_remove_remote_sink()`, `link_reset_cur_dp_mst_topology()`, `link_get_status()`, `link_is_hdcp14()`, `link_is_hdcp22()`, and `link_clear_dprx_states()`.

## Control Flow

The header has no runtime flow. The functions form the external entry points for local sink detection, MST remote sink management, connection-type probing, HDCP capability queries, and DPRX state clearing.

## State And Persistence Behavior

No state is held in the header. Implementations mutate `struct dc_link` sink, DPCD, HDCP, topology, and capability state and manage `struct dc_sink` references.

## Dependencies And Integration Points

It includes `link_service.h` for link, sink, status, and detection reason types. `link_factory.c` maps these declarations into `link_service` function pointers.

## Risks And Edge Cases

The API mixes queries with mutating operations. Callers must know that `link_detect()` and remote sink functions can allocate/release sinks and change topology state. HDCP helpers report cached capability state and depend on prior detection queries.

## Test Signals

Build coverage catches prototype drift. Runtime validation comes from hotplug, MST topology, remote sink add/remove, HDCP queries, and DPRX state clear paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_detection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c

## Purpose

`link_dpms.c` owns link-associated stream DPMS programming and link enable/disable sequencing. It bridges stream power state changes to signal-specific link protocols: DP/eDP training, MST/SST payload allocation, DSC programming, HDMI SCDC/retimer setup, LVDS/analog/virtual link output, audio, infoframes, USB4 bandwidth allocation, PSP stream config, and blank/unblank ordering.

## Important APIs, Types, And Functions

- Public blanking and state helpers: `link_blank_all_dp_displays()`, `link_blank_all_edp_displays()`, `link_blank_dp_stream()`, `link_set_all_streams_dpms_off_for_link()`, `link_resume()`, and `link_get_master_pipes_with_dpms_on()`.
- DSC APIs: `link_set_dsc_on_stream()`, `link_set_dsc_pps_packet()`, `link_set_dsc_enable()`, and `link_update_dsc_config()`.
- Payload APIs: `link_reduce_mst_payload()`, `link_increase_mst_payload()`, `allocate_mst_payload()`, `deallocate_mst_payload()`, `update_sst_payload()`, and `link_calculate_sst_avg_time_slots_per_mtp()`.
- Link enable/disable paths: `enable_link_dp()`, `enable_link_dp_mst()`, `enable_link_hdmi()`, `enable_link_lvds()`, `enable_link_analog()`, `enable_link_virtual()`, `enable_link()`, `disable_link_dp()`, and `disable_link()`.
- DPMS entries: `link_set_dpms_on()` and `link_set_dpms_off()`.
- Board support helpers program HDMI retimer/redriver I2C settings from VBIOS integrated info or defaults.

## Control Flow

`link_set_dpms_on()` validates it is called on the master pipe, resolves link encoder/HWSS, sets OTG mux, programs stream attributes, powers VPG, builds infoframes, handles seamless/eDP fast boot early returns, sets up DSC before link training, optionally sets panel replay, enables the signal-specific link, enables the stream, enables DSC on the sink and sends PPS, allocates USB4 bandwidth and DP payloads, unblanks, enables stream features, updates PSP, and enables audio.

`link_set_dpms_off()` performs the reverse at stream level: AV mute, audio disable, PSP update, blanking, USB4 deallocation, MST/SST payload deallocation, HDMI SCDC/retimer legacy setup, signal-specific stream/link disable ordering, ASSR disable, DSC disable, HPO mux reset, VPG powerdown, and eDP panel-mode state workaround.

DP link enable powers eDP when needed, optionally toggles MST mode, updates clocks for DP1.x, writes source OUI/cable ID, trains with retries and optional fallback, enables FEC for 8b/10b, and restores eDP AUX brightness/backlight settings. MST allocation uses DM helpers to update sideband payloads and local link encoder allocation tables. DP2 SST payload allocation writes DPCD VC payload registers and updates HPO allocation hardware.

## State And Persistence Behavior

The file mutates hardware state extensively and updates in-memory link/stream state: `link_status.link_active`, `cur_link_settings`, `mst_stream_alloc_table`, `dpia_bw_alloc_config`, `stream->dsc_packed_pps`, `stream->dpms_off`, panel mode, PSP stream config, audio state, AV mute, DPCD power/MST/FEC/DSC/hblank states, HDMI SCDC state, retimer/redriver I2C state, DCCG DSC clocks, VPG power, and OTG output mux. No on-disk persistence is used.

## Dependencies And Integration Points

It depends on HWSS selection, DPCD/DDC/HPD helpers, DP PHY/training/capability, eDP panel control, panel replay, DPIA bandwidth, DM MST helpers, resource and infoframe builders, DSC blocks, DCCG/clock manager, VPG, link validation bandwidth formulas, and PSP content-protection stream config. `link_factory.c` installs its public functions into `link_service`.

## Risks And Edge Cases

- The file acknowledges a boundary issue: DSC programming is done in link DPMS sequencing despite depending on front-end locks and OPTC state.
- MST allocation has many ordering requirements: source allocation table, sideband messages, ACT polling, and throttled VCP size must stay consistent.
- DP2 SST payload update returns `DC_OK` after logging some failures, so black-screen symptoms may be the only runtime signal.
- USB4 bandwidth allocation stores per-remote-sink requested bandwidth and adds overhead; stale remote sink indexes can misallocate.
- HDMI retimer/redriver programming depends on VBIOS tables and fixed default I2C addresses.
- DP link training failure is tolerated for SST in some cases but not MST.
- DPMS-on returns early if `stream->dpms_off` is true, so caller state must be coherent.

## Test Signals

Exercise DP/eDP SST, DP MST, DP2 128b/132b SST/MST, USB4 DPIA bandwidth allocation, DSC enable/disable and dynamic PPS update, FEC, hblank reduction, HDMI >340 MHz SCDC/retimer/redriver, DVI/LVDS/RGB/virtual paths, seamless boot, eDP fast boot, OLED/backlight AUX restore, link-training fallback/failure, MST payload increase/reduce, and DPMS off/on ordering. Logs under DP2 payload, MST, DSC, retimer/redriver, hotplug, and PSP update are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.h

## Purpose

`link_dpms.h` declares the link DPMS, blanking, payload, and DSC control API exposed through `struct link_service`.

## Important APIs, Types, And Functions

It declares `link_set_dpms_on()`, `link_set_dpms_off()`, `link_resume()`, DP/eDP blanking helpers, `link_set_all_streams_dpms_off_for_link()`, `link_get_master_pipes_with_dpms_on()`, MST payload increase/reduce, DSC PPS packet control, SST average slot calculation, DSC stream enable, DSC hardware enable, and DSC config update.

## Control Flow

There is no runtime flow in the header. The declarations divide DPMS operations into stream state transitions, global blanking helpers, MST bandwidth changes, and DSC operations.

## State And Persistence Behavior

The header stores no state. Implementations mutate hardware, DPCD, link status, payload tables, stream DSC PPS buffers, PSP stream config, and audio/blanking state.

## Dependencies And Integration Points

It includes `link_service.h`. `link_factory.c` assigns many of these functions into `link_service`, while other DC code can call the DSC and payload helpers directly.

## Risks And Edge Cases

The API exposes low-level operations that must be called in valid display commit contexts. `link_set_dpms_on()` expects master pipes and valid resources; payload/DSC helpers assume signal-specific prerequisites.

## Test Signals

Build coverage catches prototype drift. Runtime validation comes from DPMS on/off, blanking, MST payload changes, DSC PPS updates, and resume HPD filter programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_dpms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.c

## Purpose

`link_factory.c` constructs and destroys `struct link_service` and `struct dc_link` objects. It centralizes link service function-pointer wiring, BIOS/object-table based physical link construction, USB4 DPIA link construction, resource tracking, DDC/panel/link-encoder allocation, connector signal classification, and destruction cleanup.

## Important APIs, Types, And Functions

- `link_create_link_service()` allocates a `struct link_service` and fills all function pointers through category-specific constructors.
- `link_destroy_link_service()` frees the service.
- Constructor groups assign factory, detection, resource, validation, DPMS, DDC, DP capability, DP PHY/DPIA, IRQ, eDP panel control, panel replay, DP CTS, and DP trace functions.
- `link_create()` allocates a `dc_link` and calls `link_construct()`.
- `construct_phy()` builds physical connector links from BIOS connector/source objects, DDC, HPD, link encoder, panel control, device tags, external display path metadata, and HPD filters.
- `construct_dpia()` builds synthetic USB4 DPIA links with flexible DIG mapping and DPIA DDC service.
- `link_destroy()` calls `link_destruct()`, frees sinks/resources, and nulls the pointer.

## Control Flow

Service construction is simple allocation plus a fixed sequence of function-pointer category initializers. Physical link construction validates supported encoder or analog engine, reads connector caps, creates DDC, resolves HPD IRQs, creates a link encoder, maps connector IDs to signal types, creates panel control for eDP/LVDS, finds supported device tags, reads external display path channel mapping/chip caps, records forced fixed-VS drive settings, programs HPD filter, and initializes PSR/replay defaults. Failure jumps release partially created resources.

DPIA construction uses a dummy DisplayPort connector object, marks the endpoint as `DISPLAY_ENDPOINT_USB4_DPIA`, enables flexible DIG mapping, creates a DPIA DDC service without physical DDC, records the DPIA port index, and sets unsupported PSR/replay defaults.

## State And Persistence Behavior

The file initializes persistent in-memory link fields used throughout DC: IDs, endpoint type, connector signal, DDC service, HPD IRQ sources, link encoder, panel control, encoder/resource tracking arrays, channel mapping, chip caps, BIOS-forced drive settings, device tags, PSR/replay defaults, and DPIA preferred engine. Destruction releases DDC, panel control, link encoder, local/remote sinks, and resource-pool tracking entries. No on-disk state is written.

## Dependencies And Integration Points

It includes all link submodule headers, GPIO/BIOS/Atom firmware support, and resource-pool factory hooks. It is the integration point that turns standalone link submodule functions into the `dc->link_srv` service table used across detection, validation, DPMS, training, DDC, panel control, and diagnostics.

## Risks And Edge Cases

- Link construction has many partially initialized failure paths; cleanup must match allocation order.
- Physical construction assumes BIOS object tables provide coherent connector, encoder, HPD, and device-tag data.
- SmartMux restricts dual eDP creation in this path.
- External DP bridge handling rewrites connector signal to DP and follows nested source objects.
- Resource pool link encoder tracking is updated only for non-flexible physical encoders and must stay balanced on destruction.
- DPIA links intentionally omit physical link encoders and HPD IRQs, so downstream code must honor endpoint type.

## Test Signals

Build tests catch service signature drift. Runtime tests should cover service creation/destruction, physical HDMI/DP/eDP/LVDS/VGA/DVI links, external DP bridge links, unsupported encoder failure, panel control creation failure, HPD IRQ mapping, fixed-VS chip caps and BIOS drive settings, DPIA construction, and link destruction reference/resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.h

## Purpose

`link_factory.h` declares the basic link object lifecycle API.

## Important APIs, Types, And Functions

It exposes `link_create(const struct link_init_data *init_params)` and `link_destroy(struct dc_link **link)`. The service lifecycle functions are implemented in `link_factory.c` but not declared here in this snapshot, implying they are declared through another shared header or used with local visibility expectations.

## Control Flow

The header has no runtime flow. Callers use `link_create()` to allocate and construct physical or DPIA links and `link_destroy()` to destruct, free, and null a link pointer.

## State And Persistence Behavior

No state is stored in the header. The implementation allocates and releases `struct dc_link` objects and their nested DDC, panel, encoder, and sink resources.

## Dependencies And Integration Points

It includes `link_service.h` for lifecycle types. It is the public entry for DC resource-pool/link initialization code.

## Risks And Edge Cases

`link_destroy()` expects a valid pointer-to-pointer and does not advertise null tolerance. Creation failure returns null after partial cleanup. Callers must not use link fields after destruction because the pointer is explicitly nulled.

## Test Signals

Build coverage catches signature drift. Runtime tests should validate link create/destroy across physical and DPIA connectors, including failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_hwss_hpo_frl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_hwss_hpo_frl.c

## Purpose

`link_hwss_hpo_frl.c` implements the HWSS vtable for HPO FRL, the HDMI FRL high-performance output path. It reuses virtual no-op stream encoder setup/reset and supplies HDMI FRL stream attribute programming.

## Important APIs, Types, And Functions

- `setup_hpo_frl_stream_attribute()` counts ODM combine segments by walking `pipe_ctx->next_odm_pipe`, then calls `hdmi_frl_set_stream_attribute()` with stream timing, FRL borrow parameters, and ODM segment count.
- `can_use_hpo_frl_link_hwss()` checks for `link_res->hpo_frl_link_enc`.
- `get_hpo_frl_link_hwss()` returns the static HPO FRL vtable.

## Control Flow

The vtable maps setup/reset stream encoder to virtual no-ops and maps stream attribute setup to FRL-specific programming. There is no link output enable/disable function in this vtable; other hardware sequencing layers handle the link output path.

## State And Persistence Behavior

The implementation mutates HPO FRL stream encoder attribute registers through function pointers. It reads `stream->link->frl_link_settings.borrow_params` and pipe ODM topology but stores no private state.

## Dependencies And Integration Points

It includes `link_hwss_hpo_frl.h`, `core_types.h`, and `virtual/virtual_link_hwss.h`. It integrates with HDMI FRL stream setup for ODM-combined modes.

## Risks And Edge Cases

The ODM segment count depends on a correct `next_odm_pipe` chain. Missing `hpo_frl_stream_enc` or malformed FRL link settings would fail through function-pointer use. The vtable is sparse, so callers must not expect DP-style payload/audio/test-pattern operations here.

## Test Signals

Exercise HDMI FRL modes with and without ODM combine, verify stream attributes and borrow parameters, and validate HWSS selection only when an HPO FRL link encoder resource exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_hwss_hpo_frl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.c

## Purpose

`link_resource.c` provides small accessors for current link resources and a compact resource map used to preserve/reconcile HPO DP encoder availability across detection or validation operations.

## Important APIs, Types, And Functions

- `link_get_cur_link_res()` scans `dc->current_state->res_ctx.pipe_ctx[]` for a top-level pipe whose stream uses the requested link and copies its `pipe->link_res`.
- `link_get_cur_res_map()` builds a bit map of links whose receiver reports 128b/132b capability but whose current settings are not using 128b/132b, marking HPO DP link encoders as recyclable.
- `link_restore_res_map()` uses that recycle map and the resource pool HPO DP encoder count to remove excess 128b/132b verified capability by capping `verified_link_cap.link_rate` to HBR3.

## Control Flow

Current resource lookup zeroes the output and stops at the first matching top pipe. Resource map restore runs in two passes: first non-recycled links, then recycled links. Each pass consumes available HPO DP encoder count for links still verified at 128b/132b and downgrades links once the count is exhausted.

## State And Persistence Behavior

The functions mutate only caller-provided `link_resource`/map outputs and `link->verified_link_cap.link_rate` during restore. No persistent storage is used. The map encodes HPO DP recycle state using `LINK_RES_HPO_DP_REC_MAP__SHIFT` and mask constants.

## Dependencies And Integration Points

It includes `link_resource.h` and `protocols/link_dp_capability.h`. Link service exposes these accessors for detection, validation, and DPMS code needing current resources or HPO capability reconciliation.

## Risks And Edge Cases

- `link_get_cur_link_res()` returns zeroed resources if no current top pipe matches.
- Resource restore changes verified capabilities in place, which can affect later mode validation decisions.
- The two-pass policy prioritizes non-recycled links before recycled links; this is intentional but can alter which links retain DP2 capability under scarcity.
- Bit shifting assumes link indexes fit in the encoded map field.

## Test Signals

Test current resource lookup with active/inactive links, top and split pipes, DP HPO capability with fewer HPO encoders than capable links, recycled versus non-recycled links, and links disconnected during restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.h

## Purpose

`link_resource.h` declares link resource accessor helpers for current resources and HPO resource-map preservation.

## Important APIs, Types, And Functions

It declares `link_get_cur_res_map()`, `link_restore_res_map()`, and `link_get_cur_link_res()`.

## Control Flow

No runtime flow exists in the header. The declarations are assigned into `link_service` by `link_factory.c`.

## State And Persistence Behavior

No state is stored. The implementation reads current pipe contexts and mutates caller outputs plus verified link capabilities during resource-map restore.

## Dependencies And Integration Points

It includes `link_service.h` for `struct dc`, `struct dc_link`, and `struct link_resource`.

## Risks And Edge Cases

Callers must provide valid output pointers. The restore API mutates link verified caps, so it is not a pure restore of an external map and should be called only in the intended resource reconciliation phase.

## Test Signals

Build coverage catches signature drift. Runtime validation comes from HPO DP resource allocation and mode validation around multiple DP2-capable links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.c

## Purpose

`link_validation.c` owns link-level timing and bandwidth validation against dongle limits, DP receiver/link capabilities, USB4 DP tunnel budgets, and DP audio hblank requirements. It also exposes reusable bandwidth formulas.

## Important APIs, Types, And Functions

- `link_validate_mode_timing()` checks passive dongle pixel-clock limits, active dongle timing support, and DP link bandwidth.
- `dp_link_bandwidth_kbps()` computes effective DP bandwidth for 8b/10b and 128b/132b link settings, including FEC efficiency for 8b/10b when FEC should be enabled.
- `link_validate_dp_tunnel_bandwidth()` aggregates stream timing bandwidth by DPIA link and asks `link_dpia_validate_dp_tunnel_bandwidth()` to validate USB4 tunnel budgets.
- `dp_required_hblank_size_bytes()` calculates worst-case hblank bytes needed for DP audio SDP and main-link overhead for 8b/10b MST and 128b/132b.
- Static helpers validate active dongle encoding, color depth, 3D format, FRL/TMDS bandwidth, downstream-facing-port caps, VSC SDP requirements for YCbCr420, and audio layout overhead.

## Control Flow

Mode validation first permits virtual remote sinks for EDID override. It checks passive dongle pixel clock using TMDS output pixel clock adjusted for encoding and color depth. Active dongle validation branches by dongle type: simple DP-VGA/DVI require RGB, DP-HDMI converter checks extended caps, FRL/TMDS max bandwidth, and DFP capability extension fields. DP/eDP timings then require VSC SDP support for YCbCr420 unless virtual, always allow 640x480 fail-safe, enforce max uncompressed pixel rate unless DSC is enabled, and compare timing bandwidth against verified link bandwidth.

Tunnel validation iterates new context streams, filters DP/MST USB4/DPIA streams with bandwidth allocation enabled, groups required timing bandwidth by link, and validates all groups together. Audio hblank calculation derives audio layouts per line, rounds SDP symbol needs to lane mapping granularity, adds EOC/main-link overhead, and converts symbols to bytes by link encoding.

## State And Persistence Behavior

The file is mostly pure validation. It reads link DPCD/dongle caps, verified link caps, tunnel settings, stream timings, and audio params. It does not persist state or program hardware. Outputs are return statuses and calculated bandwidth/byte values.

## Dependencies And Integration Points

It includes `link_validation.h`, DP capability helpers, DPIA bandwidth helpers, and `resource.h`. DPMS uses `dp_link_bandwidth_kbps()` and `dp_required_hblank_size_bytes()` indirectly for payload/hblank decisions. Mode validation callers use `link_validate_mode_timing()` before committing modes.

## Risks And Edge Cases

- `dp_link_bandwidth_kbps()` multiplies/divides in an order that can lose precision and assumes link rates/lane counts are valid.
- The DP fail-safe 640x480 mode bypasses normal bandwidth checks.
- Some dongle DFP extension checks appear to test `support_rgb` for non-RGB encodings, matching current code but worth scrutiny.
- `link_validate_dp_tunnel_bandwidth()` iterates while `i < MAX_PIPES && i < stream_count` over `new_ctx->streams[]`, so stream array/count consistency matters.
- Audio hblank calculation assumes L-PCM, max one layout per SDP, four logical lanes, sixteen DSC slices worst case, and no SDP split.

## Test Signals

Test passive and active DP dongles, DP-HDMI FRL and TMDS converters, YCbCr420 VSC SDP support, DSC and max uncompressed pixel-rate caps, DP 8b/10b with and without FEC, DP 128b/132b, fail-safe 640x480, USB4 tunnel aggregation across multiple streams, and audio hblank for 2/6/8 channel audio at common sample rates. Return statuses `DC_EXCEED_DONGLE_CAP`, `DC_NO_DP_LINK_BANDWIDTH`, and `DC_FAIL_DP_TUNNEL_BW_VALIDATE` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.h

## Purpose

`link_validation.h` declares link timing, DP tunnel bandwidth, DP link bandwidth, and DP hblank audio bandwidth validation helpers.

## Important APIs, Types, And Functions

It declares `link_validate_mode_timing()`, `link_validate_dp_tunnel_bandwidth()`, `dp_link_bandwidth_kbps()`, and `dp_required_hblank_size_bytes()`.

## Control Flow

There is no runtime flow in the header. The declarations are installed into `link_service` by `link_factory.c` and used by validation and DPMS paths.

## State And Persistence Behavior

The header stores no state. Implementations are mostly read-only calculations over stream timing, link caps, tunnel settings, and audio parameters.

## Dependencies And Integration Points

It includes `link_service.h` for `dc`, `dc_state`, `dc_stream_state`, `dc_link`, timing, status, settings, and audio parameter types.

## Risks And Edge Cases

The exposed helpers are used both for rejecting modes and for programming-related calculations. Any formula change can alter visible mode lists, tunnel admission, MST/SST payload sizing, or hblank requirements.

## Test Signals

Build coverage catches prototype drift. Functional validation should compare bandwidth/status outputs for representative DP, eDP, DPIA, dongle, DSC, and audio hblank scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_validation.h -->
