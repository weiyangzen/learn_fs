# subset-b-001449 DP link protocol research

This grouped report covers the AMD display core DP/DDC protocol files assigned to `subset-b-001449`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.c

## Purpose
`link_ddc.c` implements generic display transport operations for DDC I2C, I2C-over-AUX, native AUX, fixed-VS retimer AUX access, and HDMI SCDC reads/writes. The file is intentionally protocol-level plumbing: it creates/destroys `ddc_service`, chunks I2C/AUX payloads, applies known dongle timing workarounds, dispatches raw AUX through DMUB or legacy DCE AUX, and exposes helpers used by DP capability detection, link training, HDMI scrambling setup, and low-level DPCD access.

## Important APIs, Types, And Functions
- `struct i2c_payloads` wraps a DAL `vector` of `struct i2c_payload`; `i2c_payloads_create/add/get/get_count/destroy` allocate, chunk, and release I2C command payloads.
- `link_create_ddc_service()` allocates a `ddc_service`, queries BIOS I2C GPIO data unless this is a DPIA link, and creates a GPIO DDC pin when available.
- `link_destroy_ddc_service()` tears down the GPIO DDC pin and frees the service.
- `set_ddc_transaction_type()`, `link_is_in_aux_transaction_mode()`, and `set_dongle_type()` update per-service transport policy.
- `link_get_aux_defer_delay()` applies generic and dongle-specific AUX defer delays; `defer_delay_converter_wa()` handles branch IDs/names for DP-VGA and DP-DVI converters.
- `link_query_ddc_data()` is the main read/write entry point. It chooses AUX payloads for AUX transaction modes and I2C command submission otherwise.
- `link_aux_transfer_raw()` dispatches to `dce_aux_transfer_dmub_raw()` when DMUB AUX is enabled or no DDC pin exists, otherwise to `dce_aux_transfer_raw()`.
- `link_aux_transfer_with_retries_no_mutex()` wraps `dce_aux_transfer_with_retries()` and is used for callers that already handle locking.
- `try_to_configure_aux_timeout()` programs AUX timeout through the DDC engine and applies the DCN 3.1 fixed-VS timeout workaround.
- `link_get_fixed_vs_pe_retimer_write_address()`, `link_get_fixed_vs_pe_retimer_read_address()`, `link_configure_fixed_vs_pe_retimer()`, and `link_query_fixed_vs_pe_retimer()` target vendor LTTPR/retimer address windows derived from `phy_repeater_cnt`.
- `write_scdc_data()` and `read_scdc_data()` access HDMI SCDC registers for source version, TMDS scrambling, and status reads.

## Control Flow
Construction begins from `ddc_service_construct()`: it records `link` and `ctx`, skips pin creation for DPIA or failed BIOS I2C info, otherwise builds a GPIO DDC object with BIOS line/engine metadata. DDC queries flow through `link_query_ddc_data()`. In AUX modes, it creates an `aux_payload`, writes the optional offset/address phase with `mot` held when a read follows, and reads back via `submit_aux_command()`, which slices transfers into `DEFAULT_AUX_MAX_DATA_SIZE` chunks. In native I2C mode, it builds write/read payload vectors in `EDID_SEGMENT_SIZE` chunks and sends one `i2c_command` through `dm_helpers_submit_i2c()`.

Fixed-VS retimer access calculates a vendor DPCD base from the encoded LTTPR count, then issues native AUX reads/writes at that address. SCDC setup first checks local sink panel patches and SCDC presence, reads sink version, optionally writes source version, then writes `TMDS_CONFIG` according to pixel clock and low-rate scrambling policy.

## State And Persistence
The file mutates persistent link/service state:
- `ddc_service->ddc_pin`, `ctx`, `link`, `transaction_type`, `dongle_type`, `flags`, and `wa`.
- `link->wa_flags.dp_keep_receiver_powered` is indirectly influenced by capability code that depends on DDC/AUX behavior.
- `link->dpcd_caps` fields drive defer delay and retimer address selection.
- `link->dpia` links are represented by a `ddc_service` with no GPIO DDC pin, routing raw AUX through DMUB.
- HDMI SCDC writes persist in the sink until the sink or link state changes.

## Dependencies And Integration Points
This file depends on DAL vectors, DCE AUX, GPIO/DDC services, BIOS I2C info, DPCD helpers, DM helper I2C submission, Atom firmware IDs, and HDMI SCDC constants. It is called by DP capability retrieval, DP training/DPCD helpers, HDMI link setup, and fixed-VS retimer code. `link_ddc.h` explicitly warns that `link_aux_transfer_with_retries_no_mutex()` requires external DM-side mutexing.

## Risks And Edge Cases
- `link_get_fixed_vs_pe_retimer_write_address()` returns a base address even when `phy_repeater_cnt` is invalid (`offset == 0xFF`), so callers depend on capability validation/workarounds.
- `try_to_configure_aux_timeout()` assumes a PHY endpoint before indexing `ddc_pin`; the early endpoint check prevents non-PHY access, but a malformed PHY link with no pin would be risky.
- AUX chunking changes `mot` only on the final chunk; regressions here can break EDID/I2C-over-AUX compliance.
- Converter delay workarounds compare branch names using the destination array size; mismatched string/padding behavior could miss a workaround.
- SCDC writes ignore return status, which is typical for best-effort HDMI setup but makes failures visible only through downstream behavior.

## Test Signals
Useful signals include EDID reads over I2C and I2C-over-AUX, AUX defer/retry behavior with DP-VGA/DVI/HDMI active converters, fixed-VS LTTPR retimer reads/writes, HDMI 2.0 SCDC scrambling at below/above 340 MHz, DPIA links with no GPIO DDC pin, and AUX timeout programming on DCN 3.1 fixed-VS platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.h

## Purpose
`link_ddc.h` declares the DDC/AUX/SCDC service API used by the display link layer. It provides constants for AUX defer and timeout workarounds, the EDID segment size, and the public entry points for DDC service lifecycle, I2C/AUX transactions, fixed-VS retimer access, HDMI SCDC, dongle metadata, and raw AUX transfer.

## Important APIs And Constants
- Constants: `AUX_POWER_UP_WA_DELAY`, `I2C_OVER_AUX_DEFER_WA_DELAY`, `DPVGA_DONGLE_AUX_DEFER_WA_DELAY`, `I2C_OVER_AUX_DEFER_WA_DELAY_1MS`, `LINK_AUX_DEFAULT_LTTPR_TIMEOUT_PERIOD`, `LINK_AUX_DEFAULT_TIMEOUT_PERIOD`, and `EDID_SEGMENT_SIZE`.
- Lifecycle: `link_create_ddc_service()`, `link_destroy_ddc_service()`.
- Mode/state helpers: `set_ddc_transaction_type()`, `link_get_aux_defer_delay()`, `link_is_in_aux_transaction_mode()`, `set_dongle_type()`, `get_ddc_pin()`.
- Transport helpers: `try_to_configure_aux_timeout()`, `link_query_ddc_data()`, `link_aux_transfer_with_retries_no_mutex()`, `link_aux_transfer_raw()`.
- Retimer helpers: `link_configure_fixed_vs_pe_retimer()`, `link_query_fixed_vs_pe_retimer()`, address calculators.
- HDMI helpers: `write_scdc_data()`, `read_scdc_data()`.

## Control Flow And Integration
The header is included by DP capability, DPCD, training, and HDMI setup code. It keeps the lower-level transport surface narrow: higher layers ask for DDC data or AUX transactions without embedding GPIO, BIOS, vector, or DCE AUX details. The comment on `link_aux_transfer_with_retries_no_mutex()` is an integration contract: DC-side users should usually go through DM DPCD helpers unless they already hold the required lock.

## State And Persistence
The header exposes APIs that mutate `struct ddc_service`, sink DPCD/SCDC state, DDC GPIO engine timeout settings, and `dc_link` retimer/dongle-dependent state. It does not define new structs beyond what `link_service.h` provides.

## Risks And Test Signals
Risk centers on callers respecting locking and transport mode selection. Tests should compile all users of the prototypes, exercise I2C and AUX transaction modes, validate timeout constants against training/capability paths, and confirm fixed-VS and SCDC declarations stay synchronized with `link_ddc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_ddc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.c

## Purpose
`link_dp_capability.c` is the DP capability discovery, normalization, policy, and verification hub. It reads DPCD capability blocks, source/sink/vendor IDs, dongle and PCON data, DSC/FEC/DP2 capability registers, LTTPR details, cable IDs, USB4 tunneling data, eDP panel capabilities, PSR/replay/ALPM support, and then computes reported, maximum, preferred, selected, and verified link settings. It also contains link-training fallback policy and pre-training verification loops.

## Important APIs, Types, And Functions
- `struct dp_lt_fallback_entry` and `dp_lt_fallbacks[]` encode the DP fallback order from highest to lowest bandwidth for DP2/max-bandwidth fallback.
- `fail_safe_link_settings` is RBR x1 with no downspread, used when verification fails.
- Capability predicates: `is_dp_active_dongle()`, `is_dp_branch_device()`, `dp_is_fec_supported()`, `dp_should_enable_fec()`, `dp_is_128b_132b_signal()`, `dp_is_lttpr_present()`, `dp_is_sink_present()`.
- LTTPR helpers: `dp_parse_lttpr_repeater_count()`, `dp_get_closest_lttpr_offset()`, `dp_retrieve_lttpr_cap()`, `dp_get_lttpr_count()`.
- Link rate helpers: `link_bw_kbps_from_raw_frl_link_rate_data()`, `link_dp_get_encoding_format()`, `mst_decide_link_encoding_format()`, `dp_get_max_link_enc_cap()`, `dp_get_max_link_cap()`, `dp_get_verified_link_cap()`.
- Link selection: `link_decide_link_settings()`, `edp_decide_link_settings()`, `decide_edp_link_settings_with_dsc()`, `decide_fallback_link_setting()`.
- Detection: `detect_dp_sink_caps()`, `detect_edp_sink_caps()`, `dp_overwrite_extended_receiver_cap()`, `read_is_mst_supported()`.
- Source writes: `dpcd_set_source_specific_data()`, `dpcd_write_cable_id_to_dprx()`.
- Verification: `dp_verify_link_cap_with_retries()` and internal `dp_verify_link_cap()` train candidate settings, detect link loss, and update tracing.
- eDP support: `edp_get_alpm_support()`.

## Control Flow
`detect_dp_sink_caps()` calls `retrieve_link_cap()`. That path first configures extended AUX timeout for possible LTTPR, retrieves LTTPR caps, wakes the AUX channel on failure, configures LTTPR transparent mode when present, writes source-specific DPCD data, then reads receiver capability blocks with retry and optional extended receiver caps. It validates lane count, reads vendor IDs, MST support, downstream port/dongle details, DSC/FEC data, DPRX feature enumeration, DP2 rates/fallback formats/FEC1, max pixel rate, VESA Panel Replay caps, USB4 tunneling info, and cable IDs.

`detect_edp_sink_caps()` builds on `retrieve_link_cap()` and then reads eDP link-rate tables, backlight capabilities, eDP revision, PSR caps, ALPM caps, panel replay info, OLED emission rate, DRR granularity, MSO support, and eDP general cap 2.

`dp_get_max_link_cap()` intersects encoder capability with sink `reported_link_cap`, cable ID, LTTPR capability, UHBR13.5 availability, and debug policy such as `disable_uhbr`. `link_decide_link_settings()` then chooses settings based on stream signal: preferred DP settings, MST verified cap, virtual defaults, eDP ILR/DSC-aware search, or regular DP minimum-bandwidth search.

`dp_verify_link_cap_with_retries()` initializes trace state, optionally applies a USB-C combo PHY reset workaround, then repeatedly calls `dp_verify_link_cap()`. The verifier enables PHY, performs link training, checks HPD IRQ link-loss status after nominal success, records fail counts, disables PHY, and falls back through `decide_fallback_link_setting()` until success or fail-safe settings.

## State And Persistence
The file is state-heavy. It writes:
- `link->dpcd_caps` including DPCD rev, MST, dongle caps, branch/sink IDs, FEC/DSC, 128b/132b rates, fallback formats, replay, ALPM, PSR, LTTPR, cable ID, USB4 tunneling, and eDP-specific fields.
- `link->reported_link_cap`, `verified_link_cap`, `preferred_link_setting`, `cur_link_settings` indirectly through verification/training.
- `link->wa_flags` for keep-receiver-powered, MOT segment reset, DPIA forced TBT3 mode, and other quirks.
- `link->dprx_states.cable_id_written` after writing cable ID downstream.
- `link->dpia_bw_alloc_config` is read to adjust LTTPR max link/lane caps when USB4 bandwidth allocation is active.
- Source DPCD registers such as OUI, device ID, min horizontal blanking, total LTTPR count, and cable attributes.

## Dependencies And Integration Points
This file integrates nearly every DP protocol layer: `link_ddc` for AUX timeouts and retimer support, `link_dpcd` for DPCD access, `link_dp_dpia` for USB4 tunnel data, `link_dp_phy` and `link_dp_training` for verification, IRQ handler parsing for post-train link-loss checks, panel control for eDP brightness defaults, link detection/validation, encoder resource selection, link encoder configuration, DMUB USB-C cable ID commands, and GPIO DDC for sink presence.

## Risks And Edge Cases
- Capability discovery depends on many best-effort DPCD reads; partial failures may leave zeroed fields that alter policy.
- DP2/UHBR capability intersection is subtle: encoder, sink, cable, LTTPR, bandwidth allocation, and debug flags all lower link caps.
- `decide_fallback_link_setting()` has separate legacy and DP2 fallback policies; infinite-loop prevention relies on updating `max->link_rate` on EQ failures.
- eDP ILR and DSC selection must not pick unsupported link-rate-set indexes.
- `read_is_mst_supported()` applies preferred training overrides, so raw MST capability and policy are deliberately coupled.
- Workarounds for Retina panels, PCON FRL status, TBT3 compatibility mode, fixed-VS LTTPR count, and USB-C combo PHY reset are hardware-specific and regression-prone.
- `dp_is_sink_present()` has GPIO behavior and a debugger break when no DDC pin exists; it should not be used blindly for DPIA/no-pin cases.

## Test Signals
High-value tests include DP 1.1/1.2/1.4 and DP2 sinks, MST docks, PCON HDMI 2.1 adapters with FRL status, active VGA/DVI/HDMI converters, eDP panels with supported link rate tables and DSC, LTTPR chains including invalid counts, USB4 DPIA links with bandwidth allocation, USB-C cable ID success/failure, FEC/DSC enable policy, `disable_uhbr` and preferred setting overrides, link-cap verification fallback, HPD link-loss after training, and sink-present GPIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.h

## Purpose
`link_dp_capability.h` defines the public DP capability and link-setting API for display core link code. It hides direct `dc_link` capability layout behind functions that detect caps, select link settings, query verified and maximum caps, classify encoding formats, handle LTTPR, evaluate FEC, and verify link capability through training.

## Important APIs
- Detection: `detect_dp_sink_caps()`, `detect_edp_sink_caps()`, `dp_overwrite_extended_receiver_cap()`, `read_is_mst_supported()`.
- Capability queries: `dp_get_max_link_cap()`, `dp_get_max_link_enc_cap()`, `dp_get_verified_link_cap()`, `dp_is_sink_present()`, `dp_is_lttpr_present()`, `dp_get_lttpr_count()`.
- Encoding and training selection: `link_dp_get_encoding_format()`, `mst_decide_link_encoding_format()`, `dp_decide_training_settings()`.
- Policy: `link_decide_link_settings()`, `edp_decide_link_settings()`, `decide_edp_link_settings_with_dsc()`, `decide_fallback_link_setting()`.
- Feature predicates: `dp_is_fec_supported()`, `dp_should_enable_fec()`, `dp_is_128b_132b_signal()`, `is_dp_active_dongle()`, `is_dp_branch_device()`.
- LTTPR/cable/source DPCD helpers: `dp_retrieve_lttpr_cap()`, `dp_parse_lttpr_repeater_count()`, `dp_get_closest_lttpr_offset()`, `dpcd_write_cable_id_to_dprx()`, `dpcd_set_source_specific_data()`.
- Verification and conversion: `dp_verify_link_cap_with_retries()`, `link_bw_kbps_from_raw_frl_link_rate_data()`, `edp_get_alpm_support()`.

## Control Flow And Integration
Most DP link bring-up code uses this header before training: detect sink caps, compute max/verified cap, decide stream link settings, and choose training settings. It includes only `link_service.h`, so it forms a stable interface between protocol code and higher-level link detection/validation/commit code.

## State And Persistence
The functions declared here operate on `dc_link`, `dc_stream_state`, `pipe_ctx`, `link_resource`, and `dc_link_settings`. They populate persistent link capability fields and select runtime training/link settings.

## Risks And Test Signals
The header is broad and cross-coupled with `link_dp_training.h`; signature drift can break multiple protocol modules. Compile coverage should include DP, eDP, MST, DPIA, FEC, DSC, LTTPR, and DP2/UHBR builds, plus call sites that rely on the exported fallback and verification policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.c

## Purpose
`link_dp_dpia.c` implements DP tunneling over USB4 DisplayPort-in-Adapter (DPIA) support that is not specific to bandwidth allocation. It reads USB4 tunneling DPCD registers, queries DPIA HPD state through DMUB, and derives stream tunnel settings from previously detected DPCD/DPIA bandwidth state.

## Important APIs
- `dpcd_get_tunneling_device_data()` reads tunneling support, adapter info, USB4 driver/router IDs, optional bandwidth capability/tunnel info, and topology ID into `link->dpcd_caps.usb4_dp_tun_info`.
- `dpia_query_hpd_status()` sends `DMUB_CMD__QUERY_HPD_STATE` with `AUX_CHANNEL_DPIA`, updates `link->hpd_status`, and returns the current HPD state.
- `link_decide_dp_tunnel_settings()` populates `struct dc_tunnel_settings` for DP SST/MST streams, including whether tunneling and DP bandwidth allocation should be used.

## Control Flow
Capability retrieval starts by reading three DPCD bytes at the DP tunneling support block. If DP tunneling is not advertised or a read fails, the function exits with the current status. If bandwidth allocation is advertised, it reads `USB4_DRIVER_BW_CAPABILITY` and `DP_IN_ADAPTER_TUNNEL_INFO`. It logs router/adapter IDs and then reads the USB4 topology ID byte array.

HPD query builds a DMUB ring-buffer command using the link enum ID as the DPIA instance. Success updates `link->hpd_status` from DMUB; failure logs and forces the link HPD state false.

Tunnel settings are decided only for DP SST/MST streams. The function copies bandwidth allocation identifiers and current `dpia_bw_alloc_config` values when both DPIA and connection manager bandwidth allocation are supported.

## State And Persistence
State written here includes `link->dpcd_caps.usb4_dp_tun_info`, `link->hpd_status`, and per-stream `dc_tunnel_settings`. It reads persistent `link->dpia_bw_alloc_config` values that are maintained by `link_dp_dpia_bw.c`.

## Dependencies And Integration Points
The file depends on DPCD helpers, DMUB command infrastructure, DM helpers, DP training headers, and link HWSS definitions. Capability data is consumed by `link_dp_capability.c`, bandwidth management, validation, and stream commit code that configures DP tunnels.

## Risks And Test Signals
Risk areas are stale or partial DPCD tunneling data after early `goto err`, DMUB HPD query failure forcing HPD low, instance numbering via `enum_id - ENUM_ID_1`, and consistency between DPCD bandwidth metadata and `dpia_bw_alloc_config`. Test with USB4 DPIA docks that support no tunneling, tunneling without BW allocation, full BW allocation, DMUB query failure, and MST tunnel settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.h

## Purpose
`link_dp_dpia.h` declares the USB4 DPIA tunneling interface: DPCD capability retrieval, HPD querying, and stream tunnel setting selection.

## Important APIs
- `dpcd_get_tunneling_device_data(struct dc_link *link)` updates link DPCD tunneling capability state.
- `dpia_query_hpd_status(struct dc_link *link)` returns true when the DPIA HPD state is high.
- `link_decide_dp_tunnel_settings(struct dc_stream_state *stream, struct dc_tunnel_settings *dp_tunnel_setting)` fills stream tunnel settings from link capability and allocation state.

## Control Flow And Integration
DP capability detection calls the DPCD retrieval function, HPD detection paths can query DMUB through `dpia_query_hpd_status()`, and stream validation/commit uses the tunnel settings decision helper. The header includes only `link_service.h`, keeping DPIA internals out of consumers.

## State, Risks, And Test Signals
The functions operate on `dc_link` and `dc_stream_state` state owned elsewhere. Risk is mainly that callers must only rely on tunnel settings after successful capability detection. Compile and runtime tests should cover USB4 DPIA links with and without bandwidth allocation and HPD state changes reported through DMUB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.c

## Purpose
`link_dp_dpia_bw.c` implements USB4 DPIA DisplayPort bandwidth allocation. It enables DPTX bandwidth allocation mode, reads allocation granularity and estimates, sends requested bandwidth values, handles tunneling IRQ status, resets state on unplug, calculates MST overhead, and validates aggregate DP tunnel bandwidth per USB4 router.

## Important APIs And Helpers
- `link_dp_is_bw_alloc_available()` gates allocation on DP tunneling, DPIA BW allocation support, and driver/connection-manager support.
- `reset_bw_alloc_struct()` clears `link->dpia_bw_alloc_config`, including per-remote-sink requested bandwidth.
- `get_bw_granularity()`, `get_estimated_bw()`, `get_non_reduced_max_link_rate()`, and `get_non_reduced_max_lane_count()` read DPCD bandwidth allocation fields.
- `retrieve_usb4_dp_bw_allocation_info()` resets and repopulates allocation state.
- `link_dpia_send_bw_alloc_request()` rounds a requested bandwidth to DPCD granularity, caps it to estimated bandwidth, stores `allocated_bw`, and writes `REQUESTED_BW`.
- `link_dpia_enable_usb4_dp_bw_alloc_mode()` writes `DPTX_BW_ALLOCATION_MODE_CONTROL`, reads allocation info, updates reported link cap from non-reduced fields, marks allocation enabled, and optionally sends a zero-allocation patch.
- `link_dp_dpia_handle_bw_alloc_status()` handles success/failure/capability/estimate changed bits and clears the DPCD tunneling status.
- `dpia_handle_usb4_bandwidth_allocation_for_link()` requests peak bandwidth or resets on unplug.
- `link_dp_dpia_allocate_usb4_bandwidth_for_stream()` refreshes estimate and requests stream bandwidth when available.
- `link_dpia_get_dp_overhead()` adds MST MTP overhead for 8b/10b MST branches.
- `link_dpia_validate_dp_tunnel_bandwidth()` aggregates per-router required/allocated/estimated bandwidth and validates requested bandwidth against available capacity.

## Control Flow
On plug or capability setup, callers enable BW allocation mode. The enable path writes mode/IRQ bits, resets and reads bandwidth state, updates reported link cap if non-reduced max link/lane fields are present, and may issue a zero request to release connection-manager preallocation. Stream allocation paths refresh estimated bandwidth, convert requested kbps to a DPCD register value using `bw_granularity`, round up to the next granularity, cap to `estimated_bw`, update `allocated_bw`, and write `REQUESTED_BW`.

At runtime, HPD IRQ handling reads `DP_TUNNELING_STATUS` and forwards bandwidth bits here. Failed requests trigger a request for the full estimated bandwidth. Changed granularity or estimate bits cause fresh reads. The status byte is then written back to clear the sink/adapter status.

Validation groups `dc_validation_dpia_set` entries by connection-manager/router ID. For each link it rounds required bandwidth up to tunnel granularity, adds MST overhead when needed, accumulates required and allocated bandwidth, tracks remaining and max estimated bandwidth, then checks whether required bandwidth fits either the single-DPIA estimate or the aggregate allocated-plus-remaining budget.

## State And Persistence
The owner state is `link->dpia_bw_alloc_config`: `bw_alloc_enabled`, verified/max/allocated/estimated bandwidth, granularity, overhead, non-reduced max link/lane, and remote sink requests. The file also updates `link->reported_link_cap` from USB4 non-reduced capabilities and clears DP tunneling status DPCD bits after IRQ handling.

## Dependencies And Integration Points
This file depends on DPCD helpers, DMUB service headers, USB4/DPIA DPCD definitions, `dc_validation_dpia_set`, `dc_tunnel_settings`, MST link types, and current link caps. It is called by DPIA capability setup, stream validation, HPD IRQ handling, plug/unplug handling, and MST bandwidth update paths.

## Risks And Edge Cases
- `link_dpia_send_bw_alloc_request()` has integer rounding/capping behavior; incorrect granularity creates over- or under-allocation.
- A zero `bw_granularity` aborts allocation but leaves previous state except for logs.
- Failed requests immediately ask for `estimated_bw`, which may be aggressive on congested routers.
- `link_dpia_validate_dp_tunnel_bandwidth()` breaks out on null data rather than reporting hard failure, so malformed sets can lead to partial validation.
- Router aggregation assumes `cm_id` is the right grouping key and relies on fixed `MAX_HOST_ROUTERS_NUM`.
- MST overhead is only added for 8b/10b MST branches.

## Test Signals
Test USB4 tunnel plug/unplug, enable mode DPCD writes, zero-allocation debug patch, allocation rounding for 0.25/0.5/1 Gbps granularities, allocation failure IRQ handling, estimated/granularity changed IRQs, MST overhead calculation, multi-DPIA same-router validation, different-router validation, and null/zero validation inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.h

## Purpose
`link_dp_dpia_bw.h` exposes USB4 DPIA DP bandwidth allocation APIs and the per-router aggregation structure used during validation.

## Important Types And APIs
- `enum bw_type` names estimated, allocated, and invalid host-router bandwidth categories.
- `struct usb4_router_validation_set` stores router grouping state: validity, connection-manager ID, DPIA count, required bandwidth, allocated bandwidth, estimated bandwidth, and remaining bandwidth.
- `link_dpia_enable_usb4_dp_bw_alloc_mode()` enables DPTX BW allocation mode and initializes link allocation state.
- `link_dp_dpia_allocate_usb4_bandwidth_for_stream()` sends per-stream allocation requests.
- `dpia_handle_usb4_bandwidth_allocation_for_link()` handles plug/unplug allocation behavior for a link.
- `link_dpia_get_dp_overhead()` computes DP tunneling overhead.
- `link_dp_dpia_handle_bw_alloc_status()` handles status bits from DP tunneling IRQ.
- `link_dpia_validate_dp_tunnel_bandwidth()` validates aggregate bandwidth requests.

## Control Flow And Integration
The header is used by HPD IRQ code, USB4 tunnel validation, and stream/link management code. It bridges DPCD-based allocation mechanics with higher-level `dc_validation_dpia_set` validation.

## State, Risks, And Test Signals
The APIs mutate `link->dpia_bw_alloc_config` and read tunnel settings. Risks include keeping declarations synchronized with DPCD status semantics and validation structures. Test signals include compile coverage for validation, HPD IRQ status dispatch, stream allocation, and plug/unplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_dpia_bw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.c

## Purpose
`link_dp_irq_handler.c` implements DP HPD short-pulse IRQ handling. It reads sink/service IRQ status, detects link loss, handles PSR and Panel Replay errors, dispatches automated test work, handles MST sideband readiness, processes USB4 tunneling bandwidth IRQs, and retrains links when needed.

## Important APIs And Functions
- `dp_parse_link_loss_status()` checks lane CR/channel-eq/symbol-lock and interlane alignment status, then verifies the sink is powered D0 before reporting link loss.
- `dp_handle_link_loss()` turns DPMS off for master pipes, optionally restores verified max settings, and turns DPMS back on to retrain/re-enable.
- `dp_read_hpd_rx_irq_data()` reads the correct DPCD IRQ/status block for pre-DP1.4 or DP1.4+ ESI layouts and fills `union hpd_irq_data`.
- `dp_should_allow_hpd_rx_irq()` gates IRQ handling on established link settings, branch devices, or active DPIA bandwidth allocation.
- `dp_handle_hpd_rx_irq()` is the top-level short-pulse handler.
- Internal PSR/replay handlers: `handle_hpd_irq_psr_sink()`, `handle_hpd_irq_vesa_replay_sink()`, `handle_hpd_irq_replay_sink()`.
- `dp_handle_tunneling_irq()` reads `DP_TUNNELING_STATUS`, forwards bandwidth allocation bits to `link_dp_dpia_handle_bw_alloc_status()`, and clears the DP tunneling service IRQ.

## Control Flow
Top-level IRQ handling logs the event, reads IRQ data, returns false on DPCD read failure, and first handles automated test IRQs by clearing the service bit and either deferring work or invoking `dc_link_dp_handle_automated_test()`. It then applies the allow gate, processes PSR errors early, processes Replay errors, reports/defer-handles MST upstream/downstream message readiness, checks link loss, dispatches USB4 tunneling IRQs, detects SST branch sink-count changes, and re-enables Replay when the earlier handler requested it.

Link-loss parsing scans lane nibbles based on `cur_link_settings.lane_count`, handles DP2 EQ/CDS interlane bits separately from legacy interlane alignment, and suppresses handling if the sink is not in D0. Link-loss recovery toggles DPMS for all active master pipes on the link.

PSR handling reads PSR configuration and error/status DPCD registers. CRC/RFB/VSC errors are acknowledged and PSR is disabled/re-enabled when active; active self-refresh without error returns handled to avoid treating the powered-down main link as loss. Replay handling has VESA Panel Replay and AMD FreeSync Replay paths, acknowledges error/status DPCD bits, increments desync counters, may disable Replay, and asks the top-level handler to re-enable it after link-status handling.

## State And Persistence
State changes include:
- `out_hpd_irq_dpcd_data`, `out_link_loss`, and `has_left_work` outputs.
- `link->skip_fallback_on_link_loss` for USB4 automated test workaround.
- `link->psr_settings` active toggles via `edp_set_psr_allow_active()`.
- `link->replay_settings` error status, desync fail count, active toggles, and re-enable state.
- `link->dpia_bw_alloc_config` through delegated bandwidth status handling.
- `link->dpcd_sink_count` comparison determines return status for downstream change detection.
- DPCD service/status bits are cleared for automated test and DP tunneling IRQs.

## Dependencies And Integration Points
This file depends on DPCD helpers, generic training helpers for lane status parsing, capability predicates, eDP panel control, Panel Replay APIs, DP trace, DPMS helpers, DM helpers, and DPIA bandwidth status handling. Higher-level detection and IRQ paths use the boolean return from `dp_handle_hpd_rx_irq()` to decide whether detection work is needed.

## Risks And Edge Cases
- Ordering is important: automated test is handled before the allow gate; PSR is handled before normal link-loss checks.
- DP 1.4+ ESI reads compact a larger block into legacy `union hpd_irq_data`; offset mistakes would misroute IRQ causes.
- `dp_read_hpd_rx_irq_data()` uses a static `retval`, which is unusual for a status local.
- Replay DPCD reads have retry only for one status register and best-effort behavior elsewhere.
- Link-loss DPMS toggling assumes current state pipes remain valid across off/on.
- Deferred handling must set `has_left_work` correctly or sideband/automated-test work can be dropped.

## Test Signals
Test HPD short pulses for automated test, MST upstream/downstream messages, SST branch sink count changes, PSR active/error states, VESA and FreeSync Replay error/desync states, DP2 128b/132b EQ/CDS alignment loss, legacy lane alignment loss, sink D3 suppression, USB4 tunneling bandwidth IRQ bits, deferred handling behavior, and DPMS retraining after link loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.h

## Purpose
`link_dp_irq_handler.h` declares the DP HPD RX IRQ and link-loss handling API used by link detection, training verification, and hotplug/event paths.

## Important APIs
- `dp_parse_link_loss_status()` evaluates IRQ lane/status data for link loss.
- `dp_should_allow_hpd_rx_irq()` gates handling based on link state, branch status, or bandwidth allocation.
- `dp_handle_link_loss()` performs DPMS off/on recovery.
- `dp_read_hpd_rx_irq_data()` reads and normalizes DPCD IRQ status into `union hpd_irq_data`.
- `dp_handle_hpd_rx_irq()` performs top-level short-pulse handling and reports detection/link-loss/deferred-work outcomes.

## Control Flow And Integration
The header is included by capability verification for post-training IRQ reads and by hotplug handling code for runtime short-pulse processing. It depends only on `link_service.h`.

## State, Risks, And Test Signals
The API mutates `dc_link` runtime state and returns multiple signals through booleans and output pointers. Tests should compile all call sites and exercise link-loss parsing, IRQ data reads for DPCD revisions, deferred handling, and USB4/branch allow-gate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.c

## Purpose
`link_dp_panel_replay.c` implements VESA Panel Replay setup and DMUB command wrappers, with a selector that delegates AMD FreeSync Replay setup to eDP panel control code. It programs replay-related DPCD registers, configures ALPM and frame skipping, sends replay context/settings to DMUB, toggles Replay active state, updates DMUB Replay state, sends general Replay commands, and queries Replay state by GPINT.

## Important APIs And Functions
- `dp_setup_replay()` selects VESA Panel Replay (`dp_setup_panel_replay()`) or FreeSync Replay (`edp_setup_freesync_replay()`).
- `dp_pr_get_panel_inst()` maps a link to a panel/OTG instance using either legacy eDP panel instance lookup or current pipe context.
- `dp_pr_enable()` sends `DMUB_CMD__PR_ENABLE`, optionally sets static-screen params for external DP, and updates `replay_allow_active`.
- `dp_pr_copy_settings()` finds the link pipe, builds `DMUB_CMD__PR_COPY_SETTINGS`, and passes AUX/DIG/DPP/OTG/DPPHY, line time, FEC/DSC flags, debug flags, selective-update granularity, DSC slice height, and main-link activity option.
- `dp_pr_update_state()` and `dp_pr_set_general_cmd()` wrap DMUB update/general commands.
- `dp_pr_get_state()` polls `DMUB_GPINT__GET_REPLAY_STATE` until a non-invalid state or retry exhaustion.
- Internal helpers calculate static frame count and static-screen triggers, clear/configure DPCD Panel Replay enable/config registers, and set ALPM/frame skipping.

## Control Flow
VESA setup first clears Panel Replay enable/config DPCD registers and returns false if Replay is unsupported, no replay resource exists, or no panel instance can be found. It builds a `replay_context` from DDC AUX channel, link encoder transmitter/preferred engine, timing generator instance, and computed line time. It sends settings to DMUB through `dp_pr_copy_settings()`; on success it programs DPCD Panel Replay enable bits. Embedded links enable CRC/error IRQs, selective update, and early transport; external links only set basic enable. It then programs ALPM config based on replay settings and enables frame skipping when supported.

DMUB wrappers all resolve `panel_inst`, populate a `union dmub_rb_cmd`, set PR command type/subtype and payload size, and wake/execute DMUB synchronously. State query uses GPINT with reply and retries up to 1000 times if DMUB reports `PR_STATE_INVALID`.

## State And Persistence
The file writes `link->replay_settings.replay_feature_enabled`, `link->replay_settings.replay_allow_active`, sink DPCD Panel Replay configuration, receiver ALPM configuration, frame skipping mode, DMUB Replay firmware state, and stream static-screen parameters. It reads current pipe topology, link encoder instances, FEC state, DSC timing flags, selective update caps, and replay debug/config flags.

## Dependencies And Integration Points
It depends on eDP panel control for FreeSync Replay and static panel instance behavior, DPCD helpers, DM helpers, DMUB Replay command definitions, current `dc_state` pipe resources, link encoder state, and stream timing. HPD IRQ handling calls `dp_pr_enable()` to recover Replay after errors.

## Risks And Edge Cases
- The code assumes `link->ddc->ddc_pin` and `link->link_enc` are valid during setup; DPIA or unusual links could violate that if routed incorrectly.
- `lineTimeInNs` uses integer math and divides by `pix_clk_100hz / 10`; invalid timing could divide by zero.
- `dp_pr_get_state()` can spin 1001 GPINT attempts, assert on persistent invalid state, and still return true.
- DMUB command calls do not inspect command completion status beyond transport helper return in some paths.
- Only DP SST/eDP is supported for panel instance lookup; MST is explicitly not handled.

## Test Signals
Test VESA Replay setup on embedded and external DP SST, unsupported Replay early return, missing replay resource, frame update command version 1 vs 2 panel instance mapping, DMUB copy settings payload fields, Replay enable/disable idempotence, ALPM AUXLESS config, frame skipping DPCD bit, DSC/FEC flag propagation, state query timeout behavior, and HPD replay error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.h

## Purpose
`link_dp_panel_replay.h` declares Panel Replay setup and DMUB control APIs for DP links.

## Important APIs
- `dp_setup_replay()` configures VESA Panel Replay or FreeSync Replay for a link/stream.
- `dp_pr_get_panel_inst()` maps a link to a panel instance.
- `dp_pr_enable()` toggles Replay active state.
- `dp_pr_copy_settings()` sends Replay context to DMUB.
- `dp_pr_update_state()` and `dp_pr_set_general_cmd()` issue DMUB PR commands.
- `dp_pr_get_state()` queries current Replay firmware state.

## Control Flow And Integration
The header is used by commit/setup paths and HPD IRQ recovery. It exposes DMUB command data types through the function signatures, so callers must include compatible DMUB definitions via `link_service.h` and related includes.

## State, Risks, And Test Signals
Functions mutate `link->replay_settings` and DMUB/sink Replay state. Tests should compile call sites for VESA and FreeSync Replay, verify panel instance resolution, and exercise enable/update/general/state command wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_panel_replay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.c

## Purpose
`link_dp_phy.c` is the DP PHY state bridge. It enables/disables main-link output, updates current link and lane settings, controls sink RX power state, programs hardware drive settings, mirrors lane settings to DPCD, and manages FEC ready/enable state around training.

## Important APIs
- `dpcd_write_rx_power_ctrl()` writes `DP_SET_POWER` D0/D3 unless synchronous link training is in progress.
- `dp_enable_link_phy()` stores `cur_link_settings`, enables DP link output through HWSS, then powers the sink receiver D0.
- `dp_disable_link_phy()` optionally powers the receiver D3, disables link output, clears `cur_link_settings`, and notifies clock manager of link-rate changes.
- `dp_set_hw_lane_settings()` programs HW lane settings through link HWSS, with LTTPR non-transparent skip logic for non-immediate downstream repeaters and fixed-VS exceptions.
- `dp_set_drive_settings()` programs HW settings, converts them to DPCD lane settings, and writes DPCD lane settings.
- `dp_set_fec_ready()` writes `DP_FEC_CONFIGURATION`, calls encoder `fec_set_ready`, and moves `link->fec_state` between not-ready and ready.
- `dp_set_fec_enable()` waits at least 7 us after training before enabling FEC in the encoder and updates `fec_state`.

## Control Flow
Training and verification call `dp_enable_link_phy()` before DPCD training operations. Lane setting updates flow from training decisions into `dp_set_hw_lane_settings()` and then to sink-visible DPCD through `dp_set_drive_settings()`. On disable, receiver power-down is skipped when a dongle workaround requires it, implicit eDP power control is skipped, or the link is disconnected. FEC is set ready before training when policy allows and enabled after successful training.

## State And Persistence
The file mutates `link->cur_link_settings`, `link->cur_lane_setting`, `link->fec_state`, sink `DP_SET_POWER`, sink `DP_FEC_CONFIGURATION`, hardware link output, hardware PHY lane drive, and clock-manager notification state.

## Dependencies And Integration Points
It depends on link HWSS, DPCD helpers, generic training helpers for DPCD lane conversion, capability FEC policy, clock manager, resource/link encoder selection, and Atom firmware chip caps. Training, verification, DPMS, and capability code all call into this file.

## Risks And Edge Cases
- `dpcd_write_rx_power_ctrl()` skips writes during sync link training; callers must account for receiver power state.
- Non-transparent LTTPR lane programming deliberately skips non-immediate downstream repeaters except fixed-VS/128b cases.
- FEC state transitions assume encoder callbacks exist and that DPCD writes succeed before hardware state changes.
- `dp_disable_link_phy()` clears `cur_link_settings`, which affects later HPD IRQ allow/link-loss logic.

## Test Signals
Test PHY enable/disable with receiver power D0/D3, keep-receiver-powered dongles, eDP implicit power skip, LTTPR non-transparent lane programming offsets, fixed-VS exceptions, FEC ready/enable/disable transitions, and clock-manager notification after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.h

## Purpose
`link_dp_phy.h` declares the DP PHY control interface for link output, lane drive settings, FEC control, and sink receiver power state.

## Important APIs
- `dp_enable_link_phy()` and `dp_disable_link_phy()` manage hardware link output and current link state.
- `dp_set_hw_lane_settings()` and `dp_set_drive_settings()` program per-lane PHY/DPCD settings.
- `dp_set_fec_ready()` and `dp_set_fec_enable()` manage FEC readiness and enablement around training.
- `dpcd_write_rx_power_ctrl()` writes sink receiver power state.

## Control Flow And Integration
Generic and specialized link training code include this header to prepare PHY output, send test/training patterns, apply lane settings, and transition FEC state. Capability verification also uses it while probing maximum link capability.

## State, Risks, And Test Signals
The APIs mutate `dc_link` current settings, lane settings, FEC state, hardware encoder state, and sink DPCD state. Tests should cover compile integration with training/capability modules and runtime behavior across DP, eDP, LTTPR, FEC, and disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.c

## Purpose
`link_dp_training.c` implements generic DP link training helpers and top-level training orchestration. It converts link settings into DPCD encodings, chooses training patterns, configures LTTPR and channel coding, reads lane status/adjust requests, applies overrides, dispatches specialized training sequences for 8b/10b, 128b/132b, DPIA, auxless, and fixed-VS retimer cases, exits training mode, transitions to video idle, handles post-link-training adjustment, traces results, and retries/falls back when training fails.

## Important APIs And Functions
- Logging/conversion: `dp_log_training_result()`, `dp_initialize_scrambling_data_symbols()`, `dp_training_pattern_to_dpcd_training_pattern()`, `dp_get_nibble_at_index()`, `get_dpcd_link_rate()`, `dp_translate_training_aux_read_interval()`.
- Status checks: `dp_get_cr_failure()`, `dp_is_max_vs_reached()`, `dp_is_cr_done()`, `dp_is_ch_eq_done()`, `dp_is_symbol_locked()`, `dp_is_interlane_aligned()`, `dp_check_interlane_aligned()`, `dp_check_link_loss_status()`.
- DPCD status read/write: `dp_get_lane_status_and_lane_adjust()`, `dpcd_set_training_pattern()`, `dpcd_set_link_settings()`, `dpcd_set_lane_settings()`, `dpcd_set_lt_pattern_and_lane_settings()`, `dpcd_configure_channel_coding()`.
- Training policy: `dp_get_lttpr_mode_override()`, `override_training_settings()`, `decide_cr_training_pattern()`, `decide_eq_training_pattern()`, `dp_decide_lttpr_mode()`, `dp_decide_lane_settings()`, `dp_decide_training_settings()`.
- LTTPR control: `configure_lttpr_mode_transparent()`, internal non-transparent configuration, `dpcd_configure_lttpr_mode()`, `repeater_training_done()`.
- Hardware pattern control: `start_clock_recovery_pattern_early()`, `dp_set_hw_test_pattern()`, `dp_set_hw_training_pattern()`.
- Top-level flows: `dp_perform_link_training()` and `perform_link_training_with_retries()`.

## Control Flow
`dp_perform_link_training()` first selects training settings by encoding, applies caller/debug/BIOS overrides, exits any previous training mode, configures LTTPR mode, prepares FEC for 8b/10b, writes channel coding, and then dispatches to fixed-VS 8b/10b, normal 8b/10b, or 128b/132b training. It exits training mode again, aborts DPIA training if necessary, optionally transitions to video idle, performs post-LT adjustment/link-loss checks, logs the result, and increments debug failure count on failure.

`perform_link_training_with_retries()` is the commit-time retry loop. It may preconfigure the stream encoder for 8b/10b SST, enables PHY for each attempt, honors sink power-up delay, sets eDP ASSR/panel mode, handles aux-disabled training, chooses legacy DPIA training or consolidated generic training, records trace counters, updates MST DPIA verified bandwidth after success, disables PHY between attempts, detects unplug after aborts, and either retries original settings or falls back to lower bandwidth while checking whether stream bandwidth still fits.

Lane-status reads use DPRX addresses or per-LTTPR repeater addresses depending on `offset`. Lane adjustment decisions convert DPCD requests to hardware lane settings, optionally maximize settings across lanes when per-lane settings are disallowed, and apply override values.

## State And Persistence
The file mutates `link_training_settings`, `link->dpcd_caps.lttpr_caps.mode` and LTTPR aux intervals, `link->cur_link_settings` and lane settings through PHY helpers, `link->fec_state`, DPCD training/link/lane/channel-coding registers, trace counters/timestamps, `link->ctx->dc->debug_data.ltFailCount`, `link->verified_link_cap` for DPIA MST fallback outcomes, and eDP panel mode/ASSR state.

## Dependencies And Integration Points
It integrates with specialized training modules (`8b_10b`, `128b_132b`, auxless, DPIA, fixed-VS retimer), DPCD helpers, DP trace, DP PHY, DP capability encoding/FEC policy, eDP panel control, link detection/validation, link encoder configuration, resources, and DM helpers for MST bandwidth updates.

## Risks And Edge Cases
- DPCD training operations must avoid non-LT AUX transactions while training mode is active; the top-level sequence documents this requirement.
- `dp_check_dpcd_reqeust_status()` only treats failed DPCD requests as abort-worthy for DPIA.
- LTTPR non-transparent mode handling differs for 8b/10b and 128b/132b and clears the DPTX-to-DPIA hop aux interval in some cases.
- Post-LT adjustment only applies when supported and TPS4 is not used.
- Retry/fallback logic tracks `is_link_bw_low` and `is_link_bw_min`; mistakes can train a link that cannot carry the stream or loop too long.
- Several paths rely on debug/preferred overrides and hardware workarounds, so capability and training state can diverge intentionally.

## Test Signals
Test 8b/10b and 128b/132b training, DPIA consolidated vs legacy training, aux-disabled path, fixed-VS retimer training, LTTPR transparent/non-transparent/no-LTTPR modes, training pattern DPCD encodings, link-rate-set eDP training, lane status/adjust parsing for DPRX and repeaters, post-LT adjust requests, link-loss check after video idle, FEC ready/enable, retry and fallback behavior, unplug aborts, MST DPIA bandwidth updates, and debug/preferred overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.h

## Purpose
`link_dp_training.h` declares the generic DP link training interface and shared helper APIs used by specialized training implementations, PHY control, capability verification, and commit-time training loops.

## Important APIs
- Top-level training: `perform_link_training_with_retries()`, `dp_perform_link_training()`.
- Hardware patterns: `dp_set_hw_training_pattern()`, `dp_set_hw_test_pattern()`, `start_clock_recovery_pattern_early()`.
- DPCD training writes: `dpcd_set_training_pattern()`, `dpcd_set_lane_settings()`, `dpcd_set_link_settings()`, `dpcd_set_lt_pattern_and_lane_settings()`.
- DPCD training reads: `dp_get_lane_status_and_lane_adjust()`.
- LTTPR/channel coding: `dpcd_configure_lttpr_mode()`, `configure_lttpr_mode_transparent()`, `dpcd_configure_channel_coding()`, `repeater_training_done()`.
- Decision helpers: `dp_decide_training_settings()`, `dp_decide_lane_settings()`, `decide_cr_training_pattern()`, `decide_eq_training_pattern()`, `dp_decide_lttpr_mode()`, `dp_get_lttpr_mode_override()`, `override_training_settings()`.
- Status helpers: `dp_check_link_loss_status()`, `dp_is_cr_done()`, `dp_is_ch_eq_done()`, `dp_is_symbol_locked()`, `dp_is_interlane_aligned()`, `is_repeater()`, `dp_is_max_vs_reached()`, `dp_get_cr_failure()`, `dp_check_interlane_aligned()`.
- Conversion/timing: `get_dpcd_link_rate()`, `dp_hw_to_dpcd_lane_settings()`, `dp_wait_for_training_aux_rd_interval()`, `dp_training_pattern_to_dpcd_training_pattern()`, `dp_initialize_scrambling_data_symbols()`, `dp_translate_training_aux_read_interval()`, `dp_get_nibble_at_index()`, `dp_get_eq_aux_rd_interval()`, `dp_check_dpcd_reqeust_status()`.

## Control Flow And Integration
Specialized modules include this header to share DPCD conversion, status parsing, lane-setting decisions, and top-level type definitions. Higher-level code calls the retry or single-training entry points, while capability verification uses training helpers to validate link caps.

## State, Risks, And Test Signals
These declarations touch most DP training state: `dc_link`, `link_resource`, `pipe_ctx`, `link_training_settings`, DPCD registers, PHY patterns, and trace state. Risks are broad API coupling and misspelled exported names such as `dp_check_dpcd_reqeust_status()` that must remain ABI/source-compatible. Test signals include compile coverage for all specialized training modules and runtime coverage for lane status, DPCD writes, LTTPR offsets, training retries, and encoding-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.c

## Purpose
`link_dp_training_128b_132b.c` implements DP2 128b/132b training policy and sequences. It handles TX FFE preset lane settings, channel EQ done polling, CDS done polling, 128b/132b AUX read intervals, DP2-specific failure statuses, and default training settings for UHBR links.

## Important APIs And Functions
- `dp_perform_128b_132b_link_training()` is the exported DP2 training sequence.
- `decide_128b_132b_training_settings()` initializes `link_training_settings` for DP2/UHBR training.
- `dp_decide_128b_132b_lttpr_mode()` chooses non-transparent mode when LTTPRs are present.
- Internal `dpcd_128b_132b_set_lane_settings()` writes all DPCD lane preset settings starting at `DP_TRAINING_LANE0_SET`.
- Internal `dpcd_128b_132b_get_aux_rd_interval()` reads and converts the DP2 AUX read interval register.
- Internal channel EQ and CDS sequence functions poll status and enforce loop/time limits.

## Control Flow
`dp_perform_128b_132b_link_training()` optionally falls back to legacy 8b/10b training when `debug.legacy_dp2_lt` is set. Otherwise it writes link settings, performs channel EQ, then performs CDS. Channel EQ sends TPS1 over main link, writes TPS1 to DPCD, reads AUX interval and lane adjust, decides FFE presets, switches hardware to TPS2, writes TPS2 plus lane settings in one AUX transaction, then loops until channel EQ is done, loop count is exceeded, `LT_FAILED_128b_132b` appears, or an AUX read aborts. It then waits for EQ interlane alignment until timeout or failure.

The CDS sequence writes the CDS training pattern and loops until symbol lock plus CDS interlane alignment, DP2 LT failure, timeout, or AUX abort.

`decide_128b_132b_training_settings()` sets downspread policy, CR/EQ/CDS patterns, EQ and CDS timing limits, loop count limit, disallows per-lane settings, chooses LTTPR mode, and initializes DPCD lane settings from default hardware settings.

## State And Persistence
The file mutates `link_training_settings` fields, DPCD link settings, DPCD training pattern/lane registers, hardware training pattern and lane settings through generic PHY helpers, and reads DPCD lane/status/adjust/aux-interval fields. It reads `link->dpcd_caps.lttpr_caps.phy_repeater_cnt` to size CDS wait time and choose LTTPR behavior.

## Dependencies And Integration Points
It depends on generic training helpers, legacy 8b/10b training for debug fallback, DPCD helpers, DP PHY programming, and capability predicates for LTTPR presence. It is dispatched by `dp_perform_link_training()` whenever the selected link settings use 128b/132b encoding.

## Risks And Edge Cases
- DP2 timing depends on DPCD AUX interval values that can be as large as 256 ms; timeout constants need to match spec and LTTPR depth.
- Initial default FFE preset settings are zero unless overrides or lane adjust requests change them.
- Channel EQ and CDS split status conditions; a sink that reports partial progress can run until loop/time limits.
- Debug `legacy_dp2_lt` intentionally uses 8b/10b logic on DP2 settings and should remain test-only.
- All lane settings are written as the full `dpcd_lane_settings` array, not just active lanes.

## Test Signals
Test UHBR10/UHBR13.5/UHBR20 training, channel EQ done, EQ interlane timeout, CDS done, CDS timeout, LT_FAILED handling, AUX abort handling, FFE preset adjustment loops, LTTPR and no-LTTPR wait limits, debug legacy path, and integration with generic fallback/retry handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.h

## Purpose
`link_dp_training_128b_132b.h` declares the DP2 128b/132b training entry points used by generic DP training code.

## Important APIs
- `dp_perform_128b_132b_link_training()` executes the DP2 training sequence for prepared `link_training_settings`.
- `decide_128b_132b_training_settings()` initializes DP2 training policy, patterns, timings, and LTTPR mode.
- `dp_decide_128b_132b_lttpr_mode()` chooses LTTPR mode for 128b/132b links.

## Control Flow And Integration
The header includes `link_dp_training.h` and is included by the generic training orchestrator. It keeps the DP2-specific implementation behind three functions while reusing shared training structures and helpers.

## State, Risks, And Test Signals
The APIs mutate training settings, DPCD training state, hardware pattern/lane state, and read `dc_link` DP2/LTTPR capability state. Tests should compile generic training with DP2 support and run UHBR training success/failure, LTTPR, and debug legacy fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.h -->
