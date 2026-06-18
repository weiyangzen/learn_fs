# subset-b-001392 Research

Grouped research for AMD Display Core sources under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dp_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dp_types.h

## Purpose
`dc_dp_types.h` is the DisplayPort protocol contract layer for AMD DC. It defines DPCD register bitfield overlays, link-training enums, sink capability containers, compliance-test payloads, eDP PSR/ALPM/Panel Replay structures, DP tunneling over USB4 metadata, dongle capability models, and link-training trace state. It has no executable logic, but it is a critical ABI-like internal header because many parser, link-training, AUX, MST, DSC, PSR, and replay paths interpret raw DPCD bytes through these definitions.

## Important APIs, Types, And Data Contracts
The core link settings are `enum dc_lane_count`, `enum dc_link_rate`, `enum dc_link_spread`, `struct dc_link_settings`, and `struct dc_lane_settings`. These types encode legacy 8b/10b rates as DP multiplier values and UHBR rates directly in 10 Mbps units, so callers must not treat all enum values with one conversion rule. `struct dc_link_training_overrides` carries optional pointer overrides for swing, pre-emphasis, FFE, patterns, spread, MST, and FEC. The pointer-based design means the callee must check each override pointer before use.

DPCD byte overlays include `union dpcd_rev`, `union max_lane_count`, `union max_down_spread`, `union lane_status`, `union lane_align_status_updated`, `union dpcd_training_pattern`, and `union dpcd_training_lane`. These are used to map AUX reads/writes to bitfields for link training and HPD IRQ handling. `union hpd_irq_data` maps the 0x200-0x205 status block plus `LINK_SERVICE_IRQ_ESI0` into a seven-byte view.

Downstream and dongle support is modeled by `union dwnstream_portxcaps`, `union dp_downstream_port_present`, `enum dpcd_downstream_port_detailed_type`, `union hdmi_encoded_link_bw`, `union autonomous_mode_and_frl_link_status`, `struct dc_dongle_caps`, and `struct dc_dongle_dfp_cap_ext`. These feed DP-to-HDMI/DVI converter handling and FRL capability decisions.

DSC and FEC capabilities are represented by `union dpcd_fec_capability`, `union dp_fec_capability1`, `union dpcd_dsc_basic_capabilities`, `union dpcd_dsc_branch_decoder_capabilities`, and `struct dpcd_dsc_capabilities`. The DSC data is raw DPCD shaped and later decoded into `struct dsc_dec_dpcd_caps` from `dc_hw_types.h`.

Power and panel features are covered by `struct psr_caps`, `union edp_psr_dpcd_caps`, `struct edp_psr_info`, `union edp_alpm_caps`, Panel Replay unions, `struct dpcd_panel_replay_selective_update_info`, and sink extension caps. USB4 DP tunneling uses `struct dc_tunnel_settings`, `struct dpcd_usb4_dp_tunneling_info`, and register constants such as `DP_TUNNELING_CAPABILITIES`, `REQUESTED_BW`, and `DP_TUNNELING_STATUS`.

`struct dpcd_caps` is the aggregate sink/branch capability cache: it stores DPCD revision, lane/spread, eDP link rates, dongle and branch identity, FEC/DSC/LTTPR/adaptive-sync/USB4/replay/ALPM/HBlank expansion state, cable ID, and MSO-related fields.

## Control Flow And State
This header does not execute control flow. Its state is persisted by embedding its structures inside link objects, sink capability caches, training settings, and trace structures elsewhere in DC. State updates happen when AUX/DPCD readers fill the raw unions or decoded aggregates, and when link-training/replay/PSR code updates trace counters such as `struct dp_trace`.

## Dependencies And Integration Points
It includes `os_types.h` and `dc_ddc_types.h`, and it relies on DRM DP definitions when present while locally defining newer DPCD constants as compatibility fallbacks. Integration points include DP AUX handlers, link encoder training code, MST payload management, DSC policy, eDP PSR/Replay logic, USB4 DPIA bandwidth allocation, HDMI dongle probing, and compliance-test handlers.

## Risks
The largest risk is bitfield interpretation: C bitfield layout is compiler and endian sensitive, so this header assumes the kernel/compiler conventions used by AMD DC. Raw arrays are provided for many unions, which is safer when copying DPCD bytes but requires callers to avoid stale decoded fields. Link-rate enum semantics are mixed between legacy multipliers and UHBR absolute units. `struct dc_link_training_overrides` uses borrowed pointers whose lifetime is external. Several fallback register defines are temporary compatibility shims; mismatch with upstream DRM headers could cause duplicate or stale definitions.

## Test Signals
Good coverage comes from DP link-training success/failure across RBR/HBR/HBR2/HBR3/UHBR, HPD IRQ status decoding, MST payload activation, LTTPR repeater tests, DSC capability parsing, PSR/Panel Replay enablement, USB4 DPIA bandwidth allocation interrupts, DP-to-HDMI dongle probing, and compliance-test DPCD transactions. Static checks should also catch enum conversion errors and DPCD raw-size mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dsc.h

## Purpose
`dc_dsc.h` declares the public Display Stream Compression helper interface used by DC to parse DSC DPCD data, compute bandwidth ranges, select encoder configuration, and tune DSC policy for a timing. It is an interface header; implementation is elsewhere.

## Important APIs, Types, And Data Contracts
`struct dc_dsc_bw_range` reports min/max compressed bandwidth and target bpp in x16 fixed units plus uncompressed stream bandwidth. `struct display_stream_compressor` is the hardware/service object containing `dsc_funcs`, `dc_context`, and instance id. `struct dc_dsc_policy` captures policy choices such as slice preference, target bpp limits, forced DSC, and YCbCr422-simple handling. `struct dc_dsc_config_options` carries per-call overrides for slice height, target bpp cap, ODM h-slice, and force-DSC behavior.

The key functions are `dc_dsc_parse_dsc_dpcd`, `dc_dsc_compute_bandwidth_range`, `dc_dsc_compute_config`, `dc_dsc_stream_bandwidth_in_kbps`, `dc_dsc_stream_bandwidth_overhead_in_kbps`, `dc_dsc_get_policy_for_timing`, and policy setters for max target bpp, forced DSC, and stream overhead. Dump helpers expose decoder/encoder capabilities to logs.

## Control Flow And State
The header declares stateless computation functions plus global policy setters. The policy setters imply module-level mutable policy in the implementation, so tests must account for cross-test state and reset policy between cases. Compute flow is DPCD parse, policy/default option selection, bandwidth range calculation, then specific DSC config selection for target bandwidth and link encoding.

## Dependencies And Integration Points
It defines temporary DP extended DSC DPCD addresses and includes `dc_types.h`, using `struct dc`, `struct dc_crtc_timing`, `struct dc_dsc_config`, `struct dsc_dec_dpcd_caps`, and `enum dc_link_encoding_format`. It integrates with DP/eDP/HDMI FRL link validation, MST bandwidth calculation, timing validation, stream resource programming, and debug logging.

## Risks
Target bpp uses x16 fixed-point units while some policy fields are plain `uint32_t`, so unit confusion can over- or under-compress streams. Global policy setters can make behavior order-dependent. `dsc_min_slice_height_override` and slice granularity must remain aligned with hardware restrictions. HDMI FRL and DP overhead differ, making `is_dp` and link encoding selection important for bandwidth math.

## Test Signals
Use known DSC DPCD byte fixtures, eDP and DP sink variants, HDMI FRL DSC cases, MST hub branch throughput limits, min/max target bpp clamp tests, disabled-overhead policy tests, and mode validation for timings near link bandwidth boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.c

## Purpose
`dc_edid_parser.c` is a thin DMCU forwarding layer for EDID CEA and AMD VSDB parsing assistance. It does not parse EDID locally; it sends chunks to firmware and receives acknowledgements or parsed AMD VSDB frame-rate data when the DMCU supports the operations.

## Important APIs, Types, And Functions
`dc_edid_parser_send_cea` fetches `dc->res_pool->dmcu` and calls `dmcu->funcs->send_edid_cea` only when the DMCU exists, is initialized, and exposes that callback. `dc_edid_parser_recv_cea_ack` similarly forwards to `recv_edid_cea_ack`. `dc_edid_parser_recv_amd_vsdb` forwards to `recv_amd_vsdb` and returns version, minimum frame rate, and maximum frame rate through caller-provided pointers.

## Control Flow And State
Each function is guard-then-forward. Failure to find an initialized DMCU or required callback returns `false` without side effects. Persistent state, if any, lives in DMCU firmware and `dc->res_pool->dmcu`; this file only passes buffers and output pointers.

## Dependencies And Integration Points
It includes `dce/dce_dmcu.h` and `dc_edid_parser.h`. It integrates with EDID handling paths that need firmware assistance for CEA extension scanning or AMD vendor-specific data and with older DCE/DMCU platforms rather than DMUB-only paths.

## Risks
The code dereferences `dc->res_pool` and `dmcu->funcs` after only checking `dmcu`, so callers are expected to pass fully constructed `struct dc`. Input ranges `offset`, `total_length`, and `length` are not validated here; firmware callback implementations must enforce EDID bounds. Output pointer validity is caller-owned.

## Test Signals
Mock DMCU tests should cover no DMCU, uninitialized DMCU, missing callbacks, successful callback propagation, and callback failure propagation. EDID integration tests should verify CEA chunk offsets and AMD VSDB frame-rate values match known EDID fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.h

## Purpose
`dc_edid_parser.h` declares the DMCU-backed EDID parser forwarding API for sending CEA data and receiving parser acknowledgements or AMD VSDB data.

## Important APIs
The header exports `dc_edid_parser_send_cea`, `dc_edid_parser_recv_cea_ack`, and `dc_edid_parser_recv_amd_vsdb`. The APIs use `struct dc *` from `core_types.h`, integer offsets and lengths, mutable byte buffers, and output pointer parameters for acknowledgements and frame-rate data.

## Control Flow And State
There is no implementation in the header. State is external: the current DC resource pool must provide an initialized DMCU with matching function pointers. The API returns `bool` to indicate whether firmware communication succeeded.

## Dependencies And Integration Points
It includes `core_types.h` rather than the wider public `dc.h`, keeping the declaration tied to DC internals. EDID code and DMCU firmware service implementations are its primary integration points.

## Risks
The API exposes raw `uint8_t *data` without `const` for send operations, so ownership and mutation expectations are not explicit. Length and pointer validation are not expressible in the prototype and must be handled by callers/implementation.

## Test Signals
Compilation of EDID parser users, DMCU mock callback coverage, and EDID fixture tests using AMD VSDB blocks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_edid_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.c

## Purpose
`dc_fused_io.c` builds and executes fused write-poll-read I2C or AUX transactions through DMUB. The immediate use is HDCP atomic operations where the driver must write a register, poll for a condition, and then read data as one ordered firmware command sequence.

## Important APIs, Types, And Functions
`op_i2c_convert` converts a `mod_hdcp_atomic_op_i2c` into a `dmub_cmd_fused_request`, filling I2C location fields, DDC line, address, offset, length, and request buffer. `op_aux_convert` does the same for `mod_hdcp_atomic_op_aux`, marking the location as AUX and using AUX address/length fields.

`atomic_write_poll_read` prepares three `union dmub_rb_cmd` entries as `DMUB_CMD__FUSED_IO` requests with `multi_cmd_pending` set on the first two. It sets poll mask and poll timeout on the middle request, computes an overall timeout budget from a fixed 10 ms per request plus poll timeout and extra AUX transaction time, and calls `dm_helpers_execute_fused_io`. It returns success only if execution succeeds and the first request status is `FUSED_REQUEST_STATUS_SUCCESS`.

`dm_atomic_write_poll_read_i2c` and `dm_atomic_write_poll_read_aux` are the exported functions. They validate `link`, derive `ddc_line` from `link->ddc->ddc_pin->pin_data->en`, convert write/poll/read ops, execute the fused sequence, copy the response buffer into the read op, and return the result.

## Control Flow And State
The sequence is deterministic: validate link, convert three operations, set headers and timeout, execute through DMUB, copy read data, return success. State is transient in the stack-allocated command array and in DMUB firmware execution. No persistent driver state is updated here.

## Dependencies And Integration Points
It includes `dc_fused_io.h`, `dm_helpers.h`, and `gpio.h`, and relies on DMUB fused IO command definitions, HDCP atomic op structs from `mod_hdcp.h`, and link DDC/GPIO metadata. It integrates with HDCP authentication over DDC/I2C or DP AUX and with the DM helper execution path.

## Risks
Only `link` is checked before dereferencing `link->ddc`, `ddc_pin`, and `pin_data`, so malformed or partially initialized links can crash. Operation size is bounded by the DMUB request buffer, but `memcpy(read->data, commands[0].fused_io.request.buffer, read->size)` copies from command 0 rather than the read command slot; this is worth auditing because the read result would intuitively reside in `commands[2]`. `atomic_write_poll_read` checks only request 0 status, not poll/read statuses. AUX timeout scaling uses `length / 16`, which gives no extra timeout for 1-15 bytes and may under-budget small AUX reads.

## Test Signals
Unit tests with fake DMUB execution should verify command header fields, multi-command flags, request locations, timeout calculation, buffer copy source, oversized-op rejection, and failure propagation. Integration signals include HDCP 1.x/2.x authentication over native AUX and I2C-over-AUX, plus timeout/error injection in poll and read phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.h

## Purpose
`dc_fused_io.h` declares public fused IO helpers that execute atomic write-poll-read sequences over I2C or AUX for a `dc_link`.

## Important APIs
`dm_atomic_write_poll_read_i2c` accepts write, poll, and read `mod_hdcp_atomic_op_i2c` structures plus poll timeout and MSB mask. `dm_atomic_write_poll_read_aux` mirrors the same contract for AUX operations. Both return `bool` success and write read data into the mutable read operation structure.

## Control Flow And State
The header has no logic. The API contract implies callers allocate and retain operation buffers for the duration of the call, and the implementation sends the sequence to DMUB as a fused command.

## Dependencies And Integration Points
It includes `dc.h` and `mod_hdcp.h`, tying it to DC link objects and HDCP operation formats. HDCP authentication and DMUB IO execution are the main integration points.

## Risks
The API does not encode maximum buffer size, nullability of write/poll/read operations, or whether read data comes from I2C/AUX response semantics. Callers must provide a fully initialized link and DDC path.

## Test Signals
Compile coverage for HDCP users, static checks on nullability assumptions, and fake-DMUB tests for both exported functions are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_fused_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hdmi_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hdmi_types.h

## Purpose
`dc_hdmi_types.h` defines HDMI and DP-HDMI adapter register constants and SCDC byte overlays used by HDMI 2.0 link management, scrambling, clock detection, error counters, and DP dual-mode adapter probing.

## Important APIs And Types
Constants define DP adapter type-2 register offsets, ID, and TMDS clock limits. `struct dp_hdmi_dongle_signature_data` models the `"DP-HDMI ADAPTOR"` signature plus EOT byte. SCDC constants define address `0x54` and offsets for sink/source version, update flags, TMDS config, scrambler status, status flags, character error detection, test config, manufacturer OUI, and device ID.

The unions `hdmi_scdc_update_read_data`, `hdmi_scdc_status_flags_data`, `hdmi_scdc_ced_data`, `hdmi_scdc_manufacturer_OUI_data`, and `hdmi_scdc_device_id_data` overlay SCDC payload bytes with named fields.

## Control Flow And State
This is a declarative header. Runtime state is read from or written to HDMI SCDC registers by I2C/DDC helpers elsewhere. Error counters and lock bits are transient sink status data.

## Dependencies And Integration Points
It includes `os_types.h`. Integration points include HDMI 2.0 scrambling setup, TMDS clock validation, DP++ dongle detection, SCDC status polling, and HDMI diagnostics/error reporting.

## Risks
Bitfield overlays must match HDMI SCDC byte layout exactly. TMDS clock constants mix MHz and kHz naming, so callers must use the unit indicated by each macro. The CED union maps an 11-byte block with several partial-width fields; checksum and valid-bit interpretation should be validated against the spec.

## Test Signals
HDMI 2.0 4K60 modes requiring SCDC scrambling, DP-HDMI adapter detection, SCDC clock/channel lock polling, CED counter reads, and malformed/absent SCDC sink tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hdmi_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_helper.c

## Purpose
`dc_helper.c` implements low-level register helper routines used by DC register macros. It supports direct MMIO read/modify/write, indirect register access, register polling, optional DMUB offload/gathering of register sequences, and small utility helpers for DCE/DCN version naming and VRR support.

## Important APIs, Types, And Functions
`generic_reg_update_ex` builds a mask/value set from variadic field triples, then either queues a DMUB read-modify-write sequence when offload gathering is active or performs direct `dm_read_reg`/`dm_write_reg`. `generic_reg_set_ex` applies fields to a caller-provided register value and either queues burst writes or writes directly.

`generic_reg_get` through `generic_reg_get8` read one register and extract up to eight fields. Separate fixed-arity helpers are intentionally used instead of a pointer-heavy variadic get form, which the file comments call out as stack-corruption-prone.

`generic_reg_wait` polls a field until it equals a condition value, sleeping or delaying between tries. When DMUB gathering is active, it packs a `DMUB_CMD__REG_REG_WAIT` request instead. It asserts that total timeout is at most 3 seconds, logs long waits, warns on timeout, and breaks to debugger.

Indirect helpers are `generic_write_indirect_reg`, `generic_read_indirect_reg`, `generic_indirect_reg_get`, `generic_indirect_reg_update_ex`, `generic_indirect_reg_update_ex_sync`, and `generic_indirect_reg_get_sync`. They use index/data register pairs or CGS PCIE index access.

DMUB offload helpers include `reg_sequence_start_gather`, `reg_sequence_start_execute`, and `reg_sequence_wait_done`. Internal helpers pack read-modify-write, burst-write, and reg-wait DMUB commands and flush when buffers fill or command type/address changes.

`dce_version_to_string` maps known DCE/DCN version enums to display strings. `dc_supports_vrr` returns true for DCE versions at or above `DCE_VERSION_8_0`.

## Control Flow And State
The main state is `ctx->dmub_srv->reg_helper_offload`. `reg_sequence_start_gather` marks gathering active when DMUB offload is available and enabled. Subsequent register set/update/wait helpers append command data instead of touching MMIO directly. `reg_sequence_start_execute` clears gathering and submits the pending command based on command type. `reg_sequence_wait_done` waits for DMUB idle unless emulation is active.

For non-offload paths, register helpers synchronously read/write MMIO. DMUB offload can switch to burst-write mode after repeated same-address read-modify-write patterns, using `same_addr_count` and `should_burst_write`.

## Dependencies And Integration Points
It includes Linux delay/stdarg, `dm_services.h`, `dc.h`, `dc_dmub_srv.h`, and `reg_helper.h`. It integrates with nearly all DC hardware programming blocks through `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and indirect register macros. It depends on DMUB command definitions and `dc_wake_and_execute_dmub_cmd`.

## Risks
The variadic field APIs rely on exact argument ordering and integer promotion; mismatches can corrupt updates. DMUB gather sequencing is global per context, so nested or mismatched gather/execute calls can leave stale commands; the code asserts but still requires caller discipline. `generic_reg_set_ex` returns a `bool`-like result from `dmub_reg_value_burst_set_pack` in offload mode despite the function returning `uint32_t`, which callers should not treat as a readback value. Register waits can block up to the requested timeout and break to debugger on failure. Offloaded read-modify-write returns packed values rather than hardware states, so callers must not depend on readback semantics during offload.

## Test Signals
Register helper unit tests should cover mask composition, multi-field set/update, DMUB buffer flushing, burst-write transition, gather/execute/wait ordering, indirect access, timeout behavior, and version string mapping. Hardware integration signals include clean display bring-up, no hangs in register waits, correct DMUB idle handling, and stable behavior with `dmub_offload_enabled` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hw_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hw_types.h

## Purpose
`dc_hw_types.h` defines the hardware-facing data model for DC programming: plane addresses, surface formats, tiling/swizzle metadata, cursor state, gamma/CSC/color, CRTC timing, DSC, PSR context, DPCD-decoded capabilities, stream/link state fragments, writeback buffers, histogram control, and hardware context metadata. It is intended for virtual hardware layer programming and intentionally excludes higher-level logic-only types.

## Important APIs, Types, And Data Contracts
Memory and plane programming is represented by `union large_integer`, `struct dc_plane_address`, `struct dc_flip_addrs`, `struct plane_size`, `struct dc_plane_dcc_param`, `enum surface_pixel_format`, `enum dc_pixel_format`, tiling/swizzle enums, and `struct dc_tiling_info`. These structures carry GPU addresses, metadata addresses, VMID, TMZ, DCC const color, and GFX-version-specific tiling descriptions.

Cursor and color contracts include `struct dc_cursor_position`, `struct dc_cursor_mi_param`, `enum dc_cursor_color_format`, `struct dc_cursor_attributes`, `struct dpp_cursor_attributes`, `struct dc_gamma`, `struct dc_csc_transform`, `struct colorspace_transform`, color-space and dither enums, and histogram structures.

Timing and display output are modeled by `struct dc_crtc_timing`, `struct dc_crtc_timing_flags`, `struct dc_crtc_timing_adjust`, `enum dc_timing_standard`, `enum dc_color_depth`, `enum dc_pixel_encoding`, `enum dc_aspect_ratio`, and `enum scanning_type`. DSC timing fields embed `struct dc_dsc_config` and fixed bpp values.

Power, link, and platform context include `struct psr_context`, `struct dc_context`, `struct dsc_dec_dpcd_caps`, `struct hblank_expansion_dpcd_caps`, `struct dc_golden_table`, `enum dc_link_encoding_format`, display endpoint identifiers, panel/backlight enums, HDCP caps, MST allocation tables, PSR and Replay settings, panel config, DPIA bandwidth allocation, commit/create params, and validation params.

## Control Flow And State
The header has no functions, but many structures are persistent state containers embedded in `dc`, `dc_state`, `dc_link`, `dc_stream_state`, plane state, and hardware sequencer resources. `struct dc_gamma` includes a `kref`, so lifetime management is reference-counted. `struct dc_context` is a long-lived root object holding driver context, logger, BIOS/GPIO/DMUB services, ASIC IDs, register offsets, and firmware security/PSP context.

## Dependencies And Integration Points
It includes `os_types.h`, `fixed31_32.h`, and `signal_types.h`, and refers to many forward-declared DC objects. It is consumed by resource validation, hardware sequencers, link encoders, color management, cursor programming, writeback, PSR/Replay firmware paths, DSC, HDCP, MST, and DM/DC integration layers.

## Risks
Many enum values map directly to hardware register encodings; renumbering can silently break programming. Several structs contain raw GPU addresses and VMIDs, so stale or improperly synchronized state can cause memory faults. `struct dc_gamma` is large and reference-counted; incorrect retain/release can leak or use freed LUTs. Bitfields and unions are compact hardware contracts and need compiler layout consistency. Some comments document unit subtleties such as `pix_clk_100hz`, DSC bpp x16, luminance millinits, and DWB fixed-point formats.

## Test Signals
Validation should include plane format/tiling combinations, cursor attributes and movement, color/gamma programming, DSC timing validation, PSR/Replay entry/exit, MST allocation, writeback capture, HDCP cap reads, secure display CRC windows when enabled, and ASIC-version-specific tiling/swizzle cases. Compile-time coverage across DCN generations is important because many fields are conditionally consumed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_hw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane.h

## Purpose
`dc_plane.h` declares the public plane-state lifecycle and utility API for DC. It is the interface for creating, retaining, releasing, querying status, disabling DCC/tiling, and copying plane configuration.

## Important APIs
`dc_create_plane_state` allocates a new plane state for a `dc`. `dc_plane_state_retain` and `dc_plane_state_release` manage reference lifetime. `dc_plane_get_status` returns a `dc_plane_status` with requested update flags from `union dc_plane_status_update_flags`, currently address and histogram. `dc_plane_force_dcc_and_tiling_disable` mutates a plane state to disable DCC and optionally clear tiling. `dc_plane_copy_config` copies plane configuration from one state to another.

## Control Flow And State
The header contains no implementation. Plane state objects are persistent, reference-counted DC objects whose configuration is attached to streams through `dc_state` operations and committed later to hardware.

## Dependencies And Integration Points
It includes `dc_hw_types.h`, using plane address, format, tiling, and related hardware types. It integrates with DC state management, stream updates, resource validation, scaler programming, flip handling, and histogram/status queries.

## Risks
The API mutates shared plane state, so callers must respect retain/release and locking conventions. Disabling DCC/tiling can alter bandwidth and memory interpretation, so it should be used only for fallback or compatibility paths. Status update flags may trigger hardware reads in implementation and should be kept narrow.

## Test Signals
Plane lifecycle tests, attach/detach through `dc_state`, DCC/tiling fallback modes, flips with dirty rects, histogram status reads, and refcount leak checks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane_priv.h

## Purpose
`dc_plane_priv.h` declares internal plane-state helpers for construction, destruction, and pipe-mask lookup.

## Important APIs
`dc_plane_construct` initializes a `dc_plane_state` with a `dc_context`. `dc_plane_destruct` tears down owned resources. `dc_plane_get_pipe_mask` returns the pipe mask in a `dc_state` associated with a plane state.

## Control Flow And State
The header has no implementation. It separates private construction/destruction from public retain/release and gives internal code a way to inspect resource assignment state for a plane.

## Dependencies And Integration Points
It includes `dc_plane.h` and uses `struct dc_state`. Resource management, plane lifecycle implementation, and state validation consume these declarations.

## Risks
These functions are internal and can bypass public lifecycle expectations if misused. Pipe-mask lookup depends on a coherent `dc_state`; stale state could produce wrong resource masks.

## Test Signals
Plane creation/destruction tests, pipe assignment validation, SubVP/phantom plane interactions, and resource leak checks are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_plane_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.c

## Purpose
`dc_spl_translate.c` translates between DC pipe context structures and SPL scaler library input/output structures. It lets DC reuse SPL calculations while preserving DC-native structs for resource and hardware programming.

## Important APIs, Types, And Functions
Static helpers copy `rect` to/from `spl_rect`, map `scaling_taps` to/from `spl_taps`, convert SPL fixed-point ratio/init outputs to DC `fixed31_32`, and convert `dc_pixel_format` to `spl_pixel_format`.

`translate_SPL_in_params_from_pipe_ctx` fills `struct spl_in` from `struct pipe_ctx`. It chooses line-buffer partition callbacks based on `plane_state->ctx->dce_version`: DCN2, DCN3.2, DCN4.01/4.2, or DCN2 default. It maps plane clip/source/destination, stream source/destination, rotation, mirror, MPC slice count/index, ODM slice rect/index, output size including DSC hactive padding, scaler taps, EASF/debug settings, adaptive sharpening, linear-light scaling, cositing, transfer function, h/v active size, sharpness policy, fullscreen/HDR flags, and SDR white level.

`translate_SPL_out_params_to_pipe_ctx` copies SPL scaler program output back into `pipe_ctx->plane_res.scl_data`: recout, ratios, viewport, chroma viewport, taps, and scaler inits.

## Control Flow And State
Input translation is mostly field copying with policy branches for DCN generation and debug overrides. Output translation mutates the pipe context scaler data based on SPL results. No persistent storage is allocated here; state is transferred between caller-owned `pipe_ctx`, `spl_in`, and `spl_out`.

## Dependencies And Integration Points
It includes `dc_spl_translate.h`, DPP headers for generation-specific `dscl*_spl_calc_lb_num_partitions` callbacks, and uses resource helpers such as `resource_get_odm_slice_src_rect`, `resource_get_mpc_slice_count`, and `resource_get_mpc_slice_index`. It also calls `dm_helpers_is_hdr_on`. It integrates with scaler programming, adaptive sharpening, EASF, ODM/MPC slicing, and DC debug policy.

## Risks
The function assumes `pipe_ctx`, `plane_state`, `stream`, and stream timing/resource pointers are valid. Enum casts between DC and SPL types rely on aligned enum values; only pixel format has an invalid guard. Tap output adds one to SPL tap values, which is a subtle convention that can create off-by-one scaler programming if SPL changes. Fixed-point conversion right-shifts SPL fractional values by five bits; this must match SPL format. Debug override precedence can mask plane settings.

## Test Signals
Tests should compare translated SPL inputs/outputs for scaling, rotation, chroma formats, side-by-side 3D, ODM/MPC split cases, DSC padding, DCN2/DCN3.2/DCN4 callback selection, EASF force modes, adaptive sharpening modes, HDR detection, and tap/ratio fixed-point conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.h

## Purpose
`dc_spl_translate.h` declares the SPL/DC translation API used to map DC pipe context into SPL scaler input and SPL output back into DC scaler data.

## Important APIs
`translate_SPL_in_params_from_pipe_ctx` maps `struct pipe_ctx` into `struct spl_in`. `translate_SPL_out_params_to_pipe_ctx` maps `struct spl_out` into `pipe_ctx->plane_res.scl_data`.

## Control Flow And State
The header has no logic. Callers provide all storage; the implementation mutates the supplied `spl_in` or `pipe_ctx`.

## Dependencies And Integration Points
It includes `dc.h`, `resource.h`, and `dm_helpers.h`, tying it to internal pipe context/resource helpers and display manager HDR helpers. The scaler calculation path is the primary integration point.

## Risks
The API does not express nullability or required initialized subfields. It also exposes SPL types through DC headers, so SPL structure changes can require synchronized updates here.

## Test Signals
Compile coverage against SPL headers and scaler validation tests that exercise both translation directions are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stat.h

## Purpose
`dc_stat.h` declares lock-light status accessors for DMUB notifications and dataout. The file explicitly documents that these interfaces are called without DAL/DC locks and therefore may only access variables exclusively defined for this use.

## Important APIs
`dc_stat_get_dmub_notification` retrieves a `struct dmub_notification` from a `dc`. `dc_stat_get_dmub_dataout` retrieves a `uint32_t` dataout value.

## Control Flow And State
There is no implementation in this header. The state contract is important: implementation must avoid general DC state mutation or lock-dependent reads because callers use it outside the normal locking regime.

## Dependencies And Integration Points
It includes `dc.h` and `dmub/dmub_srv.h`, integrating with DMUB status reporting, interrupt paths, diagnostics, and display manager polling.

## Risks
Lockless access risks stale or torn reads unless the implementation uses dedicated atomic or otherwise safe storage. Expanding these APIs to touch broader DC state would violate the documented constraint.

## Test Signals
Concurrency tests, lockdep/static review, DMUB notification delivery tests, and interrupt/polling stress are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state.h

## Purpose
`dc_state.h` declares the public DC state lifecycle and stream/plane composition API. A `dc_state` is the transactional display configuration context used for validation and commit.

## Important APIs
Lifecycle functions include `dc_state_create`, `dc_state_copy`, `dc_state_create_copy`, `dc_state_copy_current`, `dc_state_create_current_copy`, `dc_state_construct`, `dc_state_destruct`, `dc_state_retain`, and `dc_state_release`.

Composition functions include `dc_state_add_stream`, `dc_state_remove_stream`, `dc_state_add_plane`, `dc_state_remove_plane`, `dc_state_rem_all_planes_for_stream`, `dc_state_add_all_planes_for_stream`, and `dc_state_get_stream_status`.

## Control Flow And State
The header defines the operations that build or mutate a proposed display state: create/copy current state, add streams, attach planes to streams, remove streams/planes, and query status. Persistent state lives in `struct dc_state` implementation fields, including resource contexts, stream statuses, and plane attachments. Reference management is explicit.

## Dependencies And Integration Points
It includes `inc/core_status.h` for `enum dc_status` and uses DC, stream, and plane state types. It integrates with atomic check/commit, resource validation, stream updates, plane updates, and current-state copying.

## Risks
State objects are shared and reference-counted; incorrect retain/release or mutation of current state can produce use-after-free or inconsistent commits. Add/remove functions must maintain stream status plane arrays and resource context consistency. Public callers must respect locking conventions enforced in implementation.

## Test Signals
Atomic commit validation, stream add/remove, plane attach/detach, state copy isolation, current state clone tests, refcount leak checks, and failed validation cleanup are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state_priv.h

## Purpose
`dc_state_priv.h` declares internal state helpers for stream lookup, SubVP/MALL classification, phantom stream/plane lifecycle, FAMS2 detection, and cursor-limit bookkeeping.

## Important APIs
Lookup and classification APIs include `dc_state_get_stream_from_id`, `dc_state_get_pipe_subvp_type`, `dc_state_get_stream_subvp_type`, and `dc_state_get_paired_subvp_stream`.

Phantom resource APIs include `dc_state_create_phantom_stream`, `dc_state_create_phantom_plane`, release functions, add/remove phantom stream and plane functions, bulk add/remove for phantom planes, `dc_state_remove_phantom_streams_and_planes`, and `dc_state_release_phantom_streams_and_planes`.

Feature/status helpers include `dc_state_is_fams2_in_use`, cursor/SubVP limit setters/getters, `dc_state_can_clear_stream_cursor_subvp_limit`, and `dc_state_is_subvp_in_use`.

## Control Flow And State
The header describes the internal flow for SubVP: create phantom stream/plane paired with a main stream/plane, add them to state with metadata, later remove and release them. Cursor-limit functions persist per-stream constraints in state so SubVP and hardware cursor support can coordinate. FAMS2 and SubVP detection inspect current resource assignments.

## Dependencies And Integration Points
It includes `dc_state.h` and `dc_stream.h`. It integrates with SubVP, MALL, FAMS2, resource validation, phantom pipe allocation, cursor programming constraints, and commit cleanup.

## Risks
Phantom resources have paired lifetimes with main resources; leaks or double releases can corrupt state. Removing phantom streams without releasing planes, or vice versa, can leave stale pointers in stream statuses. Cursor-limit flags are stateful constraints and must be cleared only when safe.

## Test Signals
SubVP enable/disable scenarios, phantom stream/plane allocation failures, cleanup after validation failure, cursor size limit transitions, FAMS2 state detection, and state copy/release stress are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_state_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream.h

## Purpose
`dc_stream.h` defines the DC stream state object and the public stream update/control API. A stream represents one display timing/output path with sink/link association, timing, color, info packets, audio, writeback, cursor, VRR/FreeSync, DSC, dynamic metadata, and commit/update state.

## Important APIs, Types, And Data Contracts
`struct dc_stream_state` is the central state container. It stores sink/link/link encoder, timing and timing adjustments, HDMI/DP info packets, DSC PPS, source/destination rectangles, audio info, HDR/dynamic metadata, transfer functions, color space, dither, view format, FreeSync/VRR flags, ABM level, context pointer, bit-depth/clamping, signal, DPMS, cursor attributes/position, kref, writeback info, boot optimization flags, stream id, test pattern, update flags, SubVP/phantom markers, luminance data, sharpening flags, DRR trigger mode, and update scratch.

`struct dc_stream_status` describes committed resource assignment: OTG, stream encoder, plane list/count, audio instance, timing sync group, ABM support, MALL/SubVP config, and FPO state. `struct dc_stream_update` is a pointer-based partial update descriptor for stream updates. `union stream_update_flags` tracks which stream properties changed.

Major APIs include stream comparison, `dc_update_planes_and_stream` and its prepare/execute/cleanup split, `dc_commit_updates_for_stream`, stream logging/current stream lookup, vblank counter and scanout position, DP SDP send, writeback add/remove/disable, DSC resource addition, dynamic metadata status/set, stream validation, stereo/sync trigger, surface update checking, stream create/copy/update signal, retain/release/status access, cursor check/set/program functions, VRR vmin/vmax adjustment, CRC functions, static-screen/dither/gamut/CSC helpers, 3DLUT allocation/release/init, pipe context lookup, DMUB dirty rect update, and cursor-limit queries.

## Control Flow And State
The stream update flow can be monolithic via `dc_update_planes_and_stream` or split into scratch init, locked prepare, unlocked execute, and locked cleanup. Stream objects are reference-counted with `kref`. Partial updates use pointer fields: a null pointer means no update for that property, while a non-null pointer supplies a new value. Committed resource status is retrieved through stream status helpers and current DC state.

## Dependencies And Integration Points
It includes `dc_types.h` and `grph_object_defs.h`, and it depends on many DC core types. It integrates with atomic commit, resource validation, hardware sequencing, link/MST/DSC code, color management, cursor programming, writeback, CRC/secure display, DMUB dirty rectangles, FreeSync/DRR, SubVP/MALL, and display manager state.

## Risks
The stream struct is broad and long-lived; partial updates must carefully distinguish null/no-change from pointer-to-new-value. Reference-count errors can leak or free active streams. Deprecated `sink` pointer should not be used by new code. Dynamic link encoder assignment must use volatile state rather than static link fields. Cursor and SubVP flags interact and can block power-saving paths. Writeback arrays are bounded by `MAX_DWB_PIPES`, and plane arrays by `MAX_SURFACES`.

## Test Signals
Atomic stream create/copy/release, stream update prepare/execute/cleanup, cursor set/program, VRR/DRR adjustments, DSC resource add, MST bandwidth update, dynamic metadata, writeback add/remove, CRC read/configure, 3DLUT lifecycle, SubVP/phantom stream interactions, and current-stream status queries are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream_priv.h

## Purpose
`dc_stream_priv.h` declares internal stream construction/destruction, stream ID assignment, and flickerless refresh-rate helper APIs.

## Important APIs
`dc_stream_construct` initializes a stream for a sink, `dc_stream_destruct` releases owned resources, and `dc_stream_assign_stream_id` assigns a unique stream id. Flickerless refresh helpers calculate maximum/minimum refresh rates from a starting point, test a refresh range for flicker risk, and compute maximum instant vtotal increase/decrease deltas for a stream.

## Control Flow And State
The header has no implementation. The flickerless helpers operate on `struct dc_stream_state`, likely using `luminance_data` and timing/DRR fields from the public stream struct. Construction/destruction underpins public create/copy/release.

## Dependencies And Integration Points
It includes `dc_stream.h`. It integrates with stream lifecycle implementation, DRR/Replay/flicker mitigation, luminance data, and SubVP/low-refresh behavior.

## Risks
These internal helpers can mutate or depend on stream internals outside the public API. Flickerless calculations are panel-data-sensitive; wrong luminance tables or timing units can produce visible flicker or overly conservative refresh limits.

## Test Signals
Stream lifecycle tests, unique ID assignment, luminance-table fixtures, gaming/static flicker criteria tests, and DRR vtotal transition tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_trace.h

## Purpose
`dc_trace.h` provides tracepoint wrapper macros for DC pipe state, DCE/DCN clock state, FPU reference tracking, and OPTC lock/unlock state.

## Important APIs
`TRACE_DC_PIPE_STATE` iterates over `dc->current_state->res_ctx.pipe_ctx` and emits `trace_amdgpu_dm_dc_pipe_state` for pipes with a plane state. `TRACE_DCE_CLOCK_STATE`, `TRACE_DCN_CLOCK_STATE`, `TRACE_DCN_FPU`, and `TRACE_OPTC_LOCK_UNLOCK_STATE` forward to corresponding `amdgpu_dm_trace.h` tracepoints.

## Control Flow And State
These are macros, so they execute in caller context. `TRACE_DC_PIPE_STATE` declares a local `pipe_ctx` pointer inside the loop, shadowing the macro parameter name, and reads current state/resource context. No persistent state is changed; trace buffers receive event data.

## Dependencies And Integration Points
It includes `amdgpu_dm_trace.h`. It integrates with Linux tracepoints, diagnostics, display state debugging, clock state logging, DCN FPU critical section tracing, and OPTC locking diagnostics.

## Risks
Macro arguments are not type-checked and can evaluate in surprising scopes. `TRACE_DC_PIPE_STATE` assumes `dc->current_state` is valid and that the caller has enough synchronization for diagnostic reads. Trace overhead depends on enabled tracepoints and call frequency.

## Test Signals
Build coverage with tracing enabled, tracepoint format validation, pipe-state trace during commits, clock state trace during clock changes, and FPU lock/unlock trace correlation are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_types.h

## Purpose
`dc_types.h` is the broad public type surface for AMD DC. It aggregates EDID/audio/timing/power/scaling/color/writeback/PSR/Replay/panel/USB4/backlight/validation/color-management types used by display manager and DC internals. It is a contract header rather than an implementation unit.

## Important APIs, Types, And Data Contracts
Environment and status enums include `enum dce_environment`, `enum dc_edid_status`, `enum act_return_status`, power states, connection types, validation modes, endpoint types, panel types, and backlight control types.

EDID/audio contracts include `struct dc_edid`, `struct dc_edid_caps`, `struct dc_cea_audio_mode`, `struct audio_mode`, `struct audio_info`, audio sample/speaker flags, info packet structs, and EDID read policy. Timing/mode contracts include `struct dc_mode_info`, `struct dc_mode_flags`, timing source enums, scaling transformations, 3D/stereo formats, content type, and writeback parameters.

PSR and Replay contracts include `struct psr_config`, `union dmcu_psr_level`, `struct psr_context`, `struct psr_settings`, Replay config/settings enums/unions, and panel config sections for power sequencing, brightness, PSR/Replay, ABM, eDP DSC, ILR, adaptive VariBright, and RIO.

Link and platform contracts include `struct dc_context`, ASIC IDs, clock config, DPCD-decoded DSC caps, golden table, GPU memory allocation type, link encoding format, endpoint id, link status, HDCP caps, MST stream allocation tables, DPIA bandwidth allocation, HPD enable selection, backlight params, validation DPIA set, and create/commit params.

Color-management contracts include CM2 GPU memory formats/layouts/sizes, transfer function sources, 3DLUT/shaper config, component settings, and legacy CM LUT enums.

## Control Flow And State
This header has no executable flow. Its structures are stored across DC context, stream state, link state, panel config, validation inputs, and display-manager-owned objects. Several fields are persistent knobs or status caches, such as `dc_context`, `psr_settings`, `replay_settings`, and `dc_panel_config`.

## Dependencies And Integration Points
It includes core low-level headers such as `os_types.h`, `fixed31_32.h`, `irq_types.h`, DDC/DP/HDMI/HW type headers, DAL graphics object definitions, and PSP content-protection types. It is included across DC, DM, link, resource, color, audio, writeback, PSR, Replay, and validation code.

## Risks
Because this is a wide shared contract, enum renumbering or struct layout changes can have broad compile and runtime impact. Many fields have implicit units: millinits, 100 Hz pixel clock precision, fixed-point formats, microhertz refresh, x16 DSC bpp, and bandwidth in kbps/Mbps/PBN. Some comments mark deprecated or temporary fields, such as stream `sink` use in other headers. Global context fields expose service pointers whose lifetime is owned elsewhere.

## Test Signals
Broad build coverage is essential. Runtime signals include EDID/audio parsing, timing validation, color and gamut updates, PSR/Replay state transitions, USB4 DPIA bandwidth allocation, backlight control by PWM/AUX, MST allocation, HDCP capability reads, validation mode variants, CM2 LUT programming, and power-source-dependent commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/Makefile

## Purpose
The DCCG Makefile adds Display Clock Generator objects for multiple DCN generations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled.

## Important Build Entries
It defines object groups for DCN20, DCN201, DCN21, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN401, and DCN42. Each group names one `dcn*_dccg.o`, prefixes it with `$(AMDDALPATH)/dc/dccg/<generation>/`, and appends the resulting path to `AMD_DISPLAY_FILES`.

## Control Flow And State
Build inclusion is controlled entirely by the `ifdef CONFIG_DRM_AMD_DC_FP` block. There is no runtime behavior. The Makefile contributes object paths to the larger AMD display build list.

## Dependencies And Integration Points
It depends on the parent AMD display build system defining `AMDDALPATH` and collecting `AMD_DISPLAY_FILES`. It integrates with Kconfig selection of DC floating-point support and generation-specific DCCG constructors used by resource creation.

## Risks
New DCCG source files must be added here or they will not build. Paths must match directory names. Conditional exclusion under `CONFIG_DRM_AMD_DC_FP` can hide missing compile coverage when FP DC is disabled.

## Test Signals
Kernel build tests with `CONFIG_DRM_AMD_DC_FP=y`, allmodconfig/allyesconfig coverage, and link checks for generation-specific DCCG create functions are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.c

## Purpose
`dcn20_dccg.c` implements the base DCN 2.0 Display Clock Generator object. It programs DPP DTOs, reference clock handling, FIFO error override, OTG add/drop pixel controls, initialization dividers, clock gating, memory low power, and object creation/destruction.

## Important APIs And Functions
`dccg2_update_dpp_dto` computes phase/modulo for a requested per-pipe DPP clock relative to `dccg->ref_dppclk`, writes `DPPCLK_DTO_PARAM[dpp_inst]`, enables/disables the corresponding DTO, clamps phase to 0xff, and records `pipe_dppclk_khz`.

`dccg2_get_dccg_ref_freq` reads `REFCLK_CNTL`, asserts if the refclk is enabled to a non-xtalin source, and reports the xtalin frequency. `dccg2_set_fifo_errdet_ovr_en` writes `DCCG_FIFO_ERRDET_OVR_EN`. `dccg2_otg_add_pixel` and `dccg2_otg_drop_pixel` clear both add/drop bits then pulse one bit for an OTG instance.

`dccg2_init` writes hardcoded 100 MHz-refclk divider/control values to microsecond/millisecond time base and dispclk change control, then clears `REFCLK_CNTL` if present. `dccg2_refclk_setup` clears refclk after hubbub init. `dccg2_is_s0i3_golden_init_wa_done` detects a BIOS marker in `MICROSECOND_TIME_BASE_DIV`. `dccg2_allow_clock_gating` writes gate disable registers to all zero or all ones. `dccg2_enable_memory_low_power` updates `DC_MEM_GLOBAL_PWR_REQ_DIS`.

`dccg2_create` allocates `struct dcn_dccg`, initializes base context/function table and register/shift/mask tables. `dcn_dccg_destroy` frees and nulls the object pointer.

## Control Flow And State
The object is a `struct dcn_dccg` wrapping `struct dccg`. Runtime state includes function-table dispatch, register tables, mask/shift tables, `ref_dppclk`, and per-pipe cached DPP clocks. Hardware state is changed through register helper macros.

## Dependencies And Integration Points
It includes Linux slab, `reg_helper.h`, `core_types.h`, and `dcn20_dccg.h`. It is called by resource creation for DCN2-family ASICs and by hardware sequencer clock programming paths.

## Risks
`dpp_inst` and `otg_inst` index arrays without local bounds checks; callers must validate pipe counts. Hardcoded init values assume a 100 MHz refclk unless overridden by later generations. `get_dccg_ref_freq` asserts on non-xtalin but still returns xtalin, so unsupported clocking may limp forward. Clock gating all-ones writes can disable broad DCCG gating and affect power. Phase/modulo rounding can overclock slightly and clamps at 0xff.

## Test Signals
Hardware bring-up on DCN2, per-pipe DPP clock programming, DTO disable when request is zero, OTG add/drop pixel behavior, S0i3 golden-init marker detection, clock-gating toggles, memory low-power toggles, and object create/destroy leak checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.h

## Purpose
`dcn20_dccg.h` defines the shared DCCG register/mask/shift table layout and DCN2 base API used by many later DCN DCCG variants.

## Important APIs, Types, And Macros
Register-list macros such as `DCCG_COMMON_REG_LIST_DCN_BASE`, `DCCG_REG_LIST_DCN2`, and mask/shift macros generate register tables for DPP DTO, refclk, dispclk change, OTG pixel rate, memory low power, and gate disable registers.

`DCCG_REG_FIELD_LIST` and generation extensions such as `DCCG3_REG_FIELD_LIST`, `DCCG31_REG_FIELD_LIST`, `DCCG314_REG_FIELD_LIST`, `DCCG32_REG_FIELD_LIST`, `DCCG35_REG_FIELD_LIST`, `DCCG401_REG_FIELD_LIST`, and `DCCG42_REG_FIELD_LIST` define a superset field table. `struct dccg_shift`, `struct dccg_mask`, and `struct dccg_registers` instantiate those field/register sets.

`struct dcn_dccg` embeds `struct dccg base` and points to register, shift, and mask tables. The header declares DCN2 functions for DPP DTO update, ref frequency, FIFO override, OTG pixel add/drop, init, refclk setup, clock gating, memory low power, S0i3 marker detection, object creation, and destruction.

## Control Flow And State
The header is declarative but drives runtime register access by shaping the tables consumed by `REG`, `FN`, and generation constructors. The superset register structure allows later generation code to share `struct dcn_dccg`.

## Dependencies And Integration Points
It includes `dccg.h` and is included by DCN201, DCN21, DCN30, DCN301, DCN302, DCN303, and other DCCG headers. Resource files provide concrete register lists and call create functions with generated tables.

## Risks
Macro-generated tables must match actual ASIC register definitions exactly. The shared superset struct can hide missing fields until runtime if a generation function accesses a zero/missing register. Array sizes use `MAX_PIPES` or fixed DPP count assumptions, so generation-specific pipe counts must align with list macros.

## Test Signals
Compile-time expansion for every DCN generation, register table sanity checks, hardware clock programming across generations, and static verification of field names against ASIC register headers are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn20/dcn20_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.c

## Purpose
`dcn201_dccg.c` implements the DCN 2.0.1 DCCG constructor and function table, reusing DCN2 behavior except for DPP DTO updates, which are intentionally a no-op because VBIOS handles that programming.

## Important APIs And Functions
`dccg201_update_dpp_dto` accepts the standard DCCG arguments but does nothing. `dccg201_funcs` reuses DCN2 refclk, FIFO override, OTG add/drop, init, refclk setup, clock gating, memory low power, and S0i3 marker helpers. `dccg201_create` allocates `struct dcn_dccg`, assigns context and the DCN201 function table, and stores register/shift/mask tables.

## Control Flow And State
Creation mirrors `dccg2_create`. Runtime dispatch through `base->funcs` changes only `update_dpp_dto`. The no-op does not update `pipe_dppclk_khz`, so any caller expecting cached DPP clock updates from this callback must account for DCN201 behavior.

## Dependencies And Integration Points
It includes `dcn201_dccg.h`, `dcn20/dcn20_dccg.h`, `reg_helper.h`, and `core_types.h`. It integrates with DCN201 resource creation and VBIOS-managed DPP clock programming.

## Risks
The no-op relies on VBIOS always programming DPP DTO correctly. Cached DPP clock state may remain stale compared with DCN2 behavior. Allocation failure is handled by `BREAK_TO_DEBUGGER` and null return, so resource creation must propagate failure.

## Test Signals
DCN201 hardware bring-up, DPP clock correctness after mode set, VBIOS interaction tests, and checks that no callers require `pipe_dppclk_khz` updates on DCN201 are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.h

## Purpose
`dcn201_dccg.h` declares the DCN 2.0.1 DCCG create function.

## Important APIs
`dccg201_create` takes a `dc_context` and generation-specific register, shift, and mask tables and returns a `struct dccg *`.

## Control Flow And State
There is no implementation in the header. It inherits the shared `struct dcn_dccg` shape from `dcn20_dccg.h`.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`. DCN201 resource construction code uses this declaration to instantiate the generation-specific DCCG.

## Risks
The header exposes only construction; destruction uses the shared `dcn_dccg_destroy`. Correct table selection is external.

## Test Signals
Compile/link coverage for DCN201 resources and constructor invocation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn201/dcn201_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.c

## Purpose
`dcn21_dccg.c` implements the DCN 2.1 DCCG variant. It customizes DPP DTO programming for DMCUB power-saving semantics and preserves an S0i3 golden-init workaround marker during initialization.

## Important APIs And Functions
`dccg21_update_dpp_dto` computes DTO modulo as `ref_dppclk / 10000` and phase as ceiling `req_dppclk / 10000`. If phase exceeds modulo it clamps to modulo to avoid corruption. If `req_dppclk` is zero, it sets phase to 10 and still enables the DTO to divide down unused pipe clock for power saving and to avoid hard hangs when accessing unused DPP registers. It writes phase/modulo and enables DTO when `ref_dppclk` is present, then records `pipe_dppclk_khz`.

`dccg21_init` checks `dccg2_is_s0i3_golden_init_wa_done`; if the BIOS marker is present, it skips `dccg2_init` so later BIOS golden init workaround logic can see the marker. Otherwise it calls DCN2 init.

`dccg21_funcs` reuses most DCN2 functions with the DCN21 DTO and init overrides. `dccg21_create` allocates and initializes the DCCG object and table pointers.

## Control Flow And State
Runtime state is the shared `struct dcn_dccg`, plus cached per-pipe DPP clocks. The key control branches are ref_dppclk availability, requested DPP clock zero/nonzero, phase clamp, and S0i3 marker detection.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, `dcn20/dcn20_dccg.h`, and `dcn21_dccg.h`. It integrates with DCN21 clock programming, DMCUB runtime clock lowering, BIOS golden init, and S0i3 resume paths.

## Risks
The modulo calculation can become zero if `ref_dppclk` is below 10 MHz, which would make phase clamping and register programming invalid; platform assumptions likely prevent this. The zero-request path intentionally leaves DTO enabled, which differs from DCN2. Skipping init on S0i3 marker relies on later BIOS logic to handle needed initialization.

## Test Signals
DCN21 mode sets, unused-pipe DPP access after DTO programming, DMCUB power-saving clock lowering, S0i3 resume with marker preserved, and phase/modulo boundary modes such as high-pixel-clock HDMI are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.h

## Purpose
`dcn21_dccg.h` declares the DCN 2.1 DCCG create function.

## Important APIs
`dccg21_create` accepts a context and register/shift/mask tables and returns a `struct dccg *`.

## Control Flow And State
The header has no logic. The concrete implementation uses the shared DCN2 object layout and DCN21-specific function table.

## Dependencies And Integration Points
It relies on forward-visible `struct dccg`, `struct dc_context`, `struct dccg_registers`, `struct dccg_shift`, and `struct dccg_mask` definitions from included resource context. DCN21 resource creation is the integration point.

## Risks
Because the header does not include `dcn20_dccg.h` directly, include order must provide the DCCG table struct declarations before use.

## Test Signals
Compile/link coverage for DCN21 resources and constructor use are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn21/dcn21_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.c

## Purpose
`dcn30_dccg.c` implements DCN 3.0 DCCG object creation. Functionally it reuses the DCN2 DCCG behavior while enabling DCN3 register table extensions through the constructor inputs.

## Important APIs And Functions
`dccg3_funcs` maps all operations to DCN2 implementations: DPP DTO update, refclk frequency, FIFO override, OTG add/drop, init, refclk setup, clock gating, memory low power, and S0i3 marker check. `dccg3_create` and `dccg30_create` both allocate `struct dcn_dccg`, initialize base context/function table, and store register/shift/mask pointers.

## Control Flow And State
Creation is allocation plus table/function pointer setup. Runtime behavior is inherited through the function table. There is no DCN3-specific register programming in this file beyond accepting DCN3 register tables.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, and `dcn30_dccg.h`. It integrates with DCN3 resource construction and DCCG register definitions for HDMI character clock and PHY symbol clocks.

## Risks
Using DCN2 functions on DCN3 assumes the register-table macros map all accessed fields compatibly. Separate `dccg3_create` and `dccg30_create` are equivalent, so callers must not infer behavior differences from the names. Allocation failure must be handled by resource construction.

## Test Signals
DCN3 display bring-up, DPP DTO programming, HDMI/DP clock behavior, clock gating, memory low power, and constructor coverage for both create names are expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.h

## Purpose
`dcn30_dccg.h` extends the DCN2 DCCG register and mask/shift lists for DCN3.0 and declares DCN3 create functions.

## Important APIs, Types, And Macros
`DCCG_REG_LIST_DCN30` extends `DCCG_REG_LIST_DCN2` with `HDMICHARCLK0_CLOCK_CNTL`, extra OTG pixel rate entries, and PHY A/B/C symbol clock control registers. `DCCG_MASK_SH_LIST_DCN3` extends DCN2 field mapping with HDMI character clock enable/source and PHY symbol force enable/source fields.

The header declares `dccg3_create` and `dccg30_create`.

## Control Flow And State
The macros are used by resource files to instantiate concrete register tables. There is no direct flow in the header.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`, sharing the object layout and base function declarations. It integrates with DCN3 resource initialization and hardware clock programming.

## Risks
The register list duplicates OTG entries already in `DCCG_REG_LIST_DCN2`, so correctness depends on macro expansion matching the intended generated table. Missing PHY D/E fields here reflects DCN3.0 hardware limits and must align with ASIC register headers.

## Test Signals
Compile-time macro expansion for DCN30 resources and runtime HDMI/DP clock programming on DCN3.0 are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn30/dcn30_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.c

## Purpose
`dcn301_dccg.c` implements the DCN 3.0.1 DCCG constructor and function table. It reuses DCN2 DCCG behavior with a reduced DCN301 register table defined in the header.

## Important APIs And Functions
`dccg301_funcs` points to DCN2 implementations for DPP DTO update, refclk frequency, FIFO override, OTG add/drop, init, refclk setup, clock gating, memory low power, and S0i3 marker detection. `dccg301_create` allocates `struct dcn_dccg`, sets context and function table, and stores register/shift/mask pointers.

## Control Flow And State
There is no custom runtime branch in this file. State is the shared DCCG object and register table pointers.

## Dependencies And Integration Points
It includes `reg_helper.h`, `core_types.h`, and `dcn301_dccg.h`. It integrates with DCN301 resource creation and common DCCG hardware sequencing.

## Risks
DCN301 header tables omit some fields used by inherited functions, notably OTG add/drop and several dispclk/memory-low-power fields depending on exact macro use. If a reused function accesses a register not present for a concrete ASIC table, `REG(...)` may be zero or invalid. Resource code must pass tables compatible with the function table actually used.

## Test Signals
DCN301 display bring-up, DPP DTO updates, init/refclk behavior, and any path calling OTG add/drop or memory low-power should be validated on hardware or register mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.h

## Purpose
`dcn301_dccg.h` defines the reduced DCN 3.0.1 DCCG register/mask list and declares its create function.

## Important APIs And Macros
`DCCG_REG_LIST_DCN301` includes DPP DTO control/params for DPP0-3, refclk, dispclk frequency change control, memory global power request, microsecond/millisecond time base, and two gate-disable registers. `DCCG_MASK_SH_LIST_DCN301` maps DPP DTO enable/DB fields, DTO phase/modulo, and refclk fields. `dccg301_create` is the constructor declaration.

## Control Flow And State
The macros shape generation-specific register tables consumed by the constructor and inherited DCN2 functions.

## Dependencies And Integration Points
It includes `dcn20/dcn20_dccg.h`. It integrates with DCN301 resource construction and shared DCCG helpers.

## Risks
The mask list is narrower than the register list and narrower than the inherited function table capabilities. Any call path using fields not listed for DCN301 must be avoided or backed by tables from another macro. DPP count is fixed to four in this list.

## Test Signals
Compile-time resource table construction, DPP DTO programming for four pipes, refclk init, and clock-gating/memory-low-power paths are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn302/dcn302_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn302/dcn302_dccg.h

## Purpose
`dcn302_dccg.h` defines DCN 3.0.2 DCCG register and mask/shift macros as a small extension of the common DCN base list.

## Important APIs And Macros
`DCCG_REG_LIST_DCN3_02` expands the common DCN base registers and adds `DPPCLK4_DTO_PARAM`. `DCCG_MASK_SH_LIST_DCN3_02` expands common base fields and adds DPP4 DTO enable and DB enable fields.

## Control Flow And State
The header is declarative; concrete resource files use the macros to build DCCG register tables.

## Dependencies And Integration Points
It includes `dcn30/dcn30_dccg.h`, inheriting DCN3/DCN2 DCCG declarations and register macro infrastructure. It integrates with DCN302 resource creation.

## Risks
This header declares no constructor of its own, so DCN302 likely uses a shared DCN3 constructor. The list supports DPP4 in addition to the four common base DPP DTOs but does not add full six-pipe DCN2 fields. Resource code must match pipe count and call paths.

## Test Signals
Compile coverage for DCN302 resources, DPP4 DTO programming, and normal DCCG init/refclk/gating paths are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn302/dcn302_dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn303/dcn303_dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn303/dcn303_dccg.h

## Purpose
`dcn303_dccg.h` defines a compact DCN 3.0.3 DCCG register and mask/shift list for a smaller pipe configuration.

## Important APIs And Macros
`DCCG_REG_LIST_DCN3_03` includes DPP DTO control/params for DPP0-1, refclk, dispclk frequency change control, and OTG pixel rate control for OTG0-1. `DCCG_MASK_SH_LIST_DCN3_03` maps DPP0-1 DTO enable/DB fields, DTO phase/modulo, refclk fields, dispclk change/error fields, and OTG0-1 add/drop pixel fields.

## Control Flow And State
There is no runtime logic in this header. It supplies concrete register-table macros consumed by DCN303 resource construction with a shared DCCG implementation.

## Dependencies And Integration Points
It includes `dcn30/dcn30_dccg.h`, sharing DCN3/DCN2 infrastructure. It integrates with DCN303 resource initialization and DCCG hardware sequencing.

## Risks
The table only covers two DPP/OTG instances. Any caller using indices above one with this table would access uninitialized register slots. The header has an SPDX line plus the standard MIT text; licensing is consistent but duplicated style differs from neighboring files.

## Test Signals
Compile coverage for DCN303 resources, two-pipe DPP DTO programming, OTG add/drop on OTG0-1, and no out-of-range DCCG calls on DCN303 are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn303/dcn303_dccg.h -->
