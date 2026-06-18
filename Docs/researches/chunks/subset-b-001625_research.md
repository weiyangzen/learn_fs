# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 37348-39691

## Purpose

This chunk is generated AMD DCN 2.0 register shift/mask metadata. It contains only C preprocessor constants; there are no functions, structs, variables, branches, allocation paths, or executable algorithms in this range. Each hardware field is represented by a bit-position macro ending in `__SHIFT` and a positioned mask macro ending in `_MASK`.

The covered hardware area is the connector-side display I/O path:

- The chunk begins in the tail of `DP_AUX0_AUX_INTERRUPT_CONTROL`, after the corresponding register comment and some earlier fields in the previous chunk.
- It then defines the remaining `DP_AUX0` AUX status, data, DPHY, GTC sync, and PHY wake fields.
- It defines full repeated AUX register field sets for `DP_AUX1` through `DP_AUX5`.
- It enters `DIG0`, the first digital front-end / stream-encoder instance, covering front-end selection, output CRC, test patterns, FIFO status, HDMI packet controls, HDMI audio control, generic packets, general control, audio-format/ISRC fields, double-buffer controls, metadata engine controls, MPEG infoframe payload fields, generic packet headers, and the first generic payload register.

The file is under a local `ceph-client` source mirror, but this path is AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, network storage protocols, or persistent filesystem data handling.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the same field.

Important macro families in this chunk:

- `DP_AUX0_AUX_INTERRUPT_CONTROL`: tail fields for AUX low-speed done interrupt/ack/mask and AUX GTC sync lock/error interrupt/ack/mask handling. The chunk begins after this register's first fields.
- `DP_AUXn_AUX_CONTROL` for `n=1..5`: AUX enable/reset/reset-done, low-speed read/update disable, HPD disconnect handling, mode detection, HPD selection, impedance calibration request, test mode, deglitch, and spare bits.
- `DP_AUXn_AUX_SW_CONTROL`: software AUX start delay, write byte count, and software go trigger.
- `DP_AUXn_AUX_ARB_CONTROL`: AUX register arbitration state, software request/done handshake, command-delay control, reset flag, and MCUI selection.
- `DP_AUXn_AUX_INTERRUPT_CONTROL`: software AUX done, low-speed done, GTC sync lock-done, and GTC sync error interrupt/status/ack/mask fields.
- `DP_AUXn_AUX_SW_STATUS`: software AUX transaction completion/request state, timeout state, RX timeout/overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start/sync/recovery flags, reply byte count, and arbitration status.
- `DP_AUXn_AUX_LS_STATUS`: low-speed AUX transaction completion/request, receive error flags, reply byte count, CP IRQ, update state, and update ack.
- `DP_AUXn_AUX_SW_DATA` and `DP_AUXn_AUX_LS_DATA`: indexed byte data windows for software and low-speed AUX transfers, including software read/write selection and autoincrement disable.
- `DP_AUXn_AUX_DPHY_TX_REF_CONTROL`, `TX_CONTROL`, `RX_CONTROL0`, and `RX_CONTROL1`: AUX physical-layer transmit reference selection/rate/divider, TX precharge timing, output-enable timing, mode-detect delay, RX start/receive windows, half-symbol/phase detection, transition filtering, below-threshold allowances, detection threshold, RX precharge skip, and timeout length/multiplier.
- `DP_AUXn_AUX_DPHY_TX_STATUS` and `RX_STATUS`: live TX active/state/half-symbol period and RX state/sync/half-symbol period readback.
- `DP_AUXn_AUX_GTC_SYNC_CONTROL`, `ERROR_CONTROL`, `CONTROLLER_STATUS`, and `STATUS`: AUX global-time-code sync enable and calibration/lock parameters, potential/definite error thresholds, lock acquisition timeout and retries, lock/error controller state, GTC sync transfer status, NACK, master request, and ack fields.
- `DP_AUXn_AUX_PHY_WAKE_CNTL`: PHY wake request, pending, priority, and ack bits.
- `DIG0_DIG_FE_CNTL`: stream-encoder source selection, stereo sync selection/gating, start, bypass/input-pixel selection, Dolby Vision enable/missed metadata status, front-end symbol-clock status, TMDS pixel encoding, and TMDS color format.
- `DIG0_DIG_OUTPUT_CRC_*`: digital output CRC enable, link/data selection, and result readback.
- `DIG0_DIG_CLOCK_PATTERN`, `DIG0_DIG_TEST_PATTERN`, and `DIG0_DIG_RANDOM_PATTERN_SEED`: test-pattern and random/static pattern controls for stream-encoder diagnostics.
- `DIG0_DIG_FIFO_STATUS`: FIFO error, overwrite level, error ack, calibrated/min/max/average levels, read clock source, calibration state, and recalculation/recompute triggers.
- `DIG0_HDMI_METADATA_PACKET_CONTROL`: HDMI metadata packet enable, line reference, missed status, and target line. This is relevant to dynamic metadata paths such as HDR/Dolby Vision-style metadata.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL0`, `2`, `3`, and `4`: generic packet send/continuous/line-reference controls and line-number programming for packet slots in this chunk.
- `DIG0_HDMI_CONTROL` and `DIG0_HDMI_STATUS`: HDMI keepout, data scrambling, clock-channel rate, null packet filling, packet-generator version, error ack/mask, deep-color enable/depth, AVMUTE status, packet errors, and HDMI error interrupt status.
- `DIG0_HDMI_AUDIO_PACKET_CONTROL`, `DIG0_HDMI_ACR_PACKET_CONTROL`, and `DIG0_AFMT_AUDIO_PACKET_CONTROL2`: HDMI audio packet cadence/delay, ACR send/source/auto-send/N-multiple/priority, AFMT audio layout override, channel enable, DP audio stream ID, HBR override, and 60958 override.
- `DIG0_HDMI_VBI_PACKET_CONTROL`, `DIG0_HDMI_INFOFRAME_CONTROL0/1`, `DIG0_HDMI_GC`, `DIG0_AFMT_MPEG_INFO0/1`, `DIG0_AFMT_GENERIC_HDR`, and `DIG0_AFMT_GENERIC_0`: HDMI null/GC/ISRC/ACP/infoframe/generic-packet send and line controls plus packet header/payload byte fields.
- `DIG0_AFMT_ISRC1_0` through `DIG0_AFMT_ISRC2_3`: ISRC status/continue/valid fields and 32 bytes of UPC/EAN/ISRC payload.
- `DIG0_HDMI_DB_CONTROL` and `DIG0_DME_CONTROL`: HDMI and metadata-engine double-buffer pending/taken/clear/lock/disable state and metadata engine requestor, enable, stream type, and double-buffer controls.

Several generated names repeat terms such as `MASK`, for example fields whose hardware names include mask bits and generated macro names ending in `_MASK`. This is expected in AMD register headers.

## Control Flow

This header chunk has no runtime control flow. Driver control flow is created by consumers that combine these masks and shifts with register offsets from `dcn_2_0_0_offset.h` and access helpers such as `REG_READ`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`.

Representative runtime use:

1. DCN20 resource setup includes `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`.
2. Register-list macros select instance-specific offsets for AUX engines, stream encoders, GPIO, IRQ, DMUB, clock, and display resources.
3. Field-list macros such as `DCN_AUX_MASK_SH_LIST` and stream-encoder `SE_*_MASK_SH_LIST` materialize shift/mask structs from names in this generated header.
4. Display Core code requests DPCD/EDID AUX transactions, link training, HPD-sensitive sideband operations, HDMI packet programming, stream start/stop, audio packet setup, metadata packet updates, CRC reads, or test-pattern output.
5. Hardware-specific code programs registers using these generated fields while polling done/status bits or writing ack/clear bits as needed.

Concrete local consumers include:

- `display/dc/resource/dcn20/dcn20_resource.c`, which includes this DCN 2.0 mask header and builds the six AUX engine register entries. Its `aux_engine_regs(id)` macro also stores `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK` in the AUX register table, showing direct use of this header's AUX control masks.
- `display/dc/dce/dce_aux.h`, where `DCN_AUX_MASK_SH_LIST` maps `DP_AUX0_AUX_CONTROL`, `DP_AUX0_AUX_ARB_CONTROL`, `DP_AUX0_AUX_SW_CONTROL`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_SW_STATUS`, `DP_AUX0_AUX_INTERRUPT_CONTROL`, and AUX DPHY RX timeout fields into per-AUX shift/mask structures. Instance-specific register addresses bind these generic DP_AUX0 field definitions to AUX engines 0 through 5.
- `display/dc/dce/dce_stream_encoder.h`, where stream-encoder field lists map `DIG0_HDMI_*`, `DIG0_AFMT_*`, `DIG0_DIG_FE_CNTL`, and related fields into the stream-encoder mask/shift structures used by DCE/DCN stream encoder code.
- `display/dmub/src/dmub_dcn20.c`, which includes the same offset and mask headers and uses generated field macros through `FD_MASK` and `FD_SHIFT` for DMUB service register definitions.
- Other DCN20 include points such as `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, and `amdgpu/gmc_v10_0.c`.

The hardware sequencing implied by the fields is significant even though the header does not encode it:

- AUX transactions require ownership/arbitration, request/go programming, data-window access, done polling, reply-byte counting, error status inspection, and interrupt/status ack.
- AUX DPHY and GTC sync fields affect link-side timing and synchronization behavior and must be programmed consistently with the link encoder and DP AUX protocol timing.
- HDMI and AFMT packet fields are latched into stream output, often through double-buffer pending/taken controls or frame/line scheduling.
- Status, ack, clear, reset, and missed/error bits must be handled according to hardware semantics that are not described by the macro values alone.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The represented state lives in DCN 2.0 display hardware registers and in caller-owned Display Core objects that cache register addresses, masks, and stream/AUX state.

Hardware state represented by this chunk includes:

- AUX engine state: enable/reset status, software transfer parameters, arbitration ownership, transaction done/request flags, reply byte counts, error flags, low-speed update state, interrupt status/masks/acks, indexed transfer data, DPHY TX/RX configuration and status, GTC sync configuration/status/error state, and PHY wake pending/ack state.
- Connector sideband state: HPD-disconnect reactions, AUX timeout windows, low-speed AUX update handling, CP IRQ indication, GTC sync lock/lock-lost/error signals, and PHY wake requests.
- Digital front-end state: selected stream source, stereo sync, start/bypass state, Dolby Vision enable and missed-metadata status, symbol-clock status, TMDS encoding/color format, output CRC enable/select/result, clock/static/random test pattern state, and FIFO calibration/error state.
- HDMI stream state: keepout mode, data scrambling, clock-channel rate, null-packet behavior, packet-generator version, deep color, packet errors, active AVMUTE, audio packet cadence, ACR behavior, VBI packet sends, infoframe sends, generic packet sends, line references, and general-control AVMUTE/packing phase.
- Audio-format and metadata state: AFMT channel enable/layout/HBR/60958 overrides, ISRC valid/status/payload bytes, MPEG infoframe bytes, generic packet header/payload bytes, HDMI double-buffer pending/taken/lock/disable state, and metadata engine enable/requestor/stream-type/double-buffer state.

Persistence is hardware-specific:

- Configuration fields such as AUX timing, HDMI packet controls, TMDS/deep-color settings, AFMT channel enable, generic packet bytes, and metadata-engine enable generally persist until explicitly rewritten, reset, power-gated, or restored during modeset/resume.
- Status fields such as AUX transaction errors, FIFO errors, HDMI packet errors, metadata missed status, pending/taken flags, and GTC sync controller status are live or sticky hardware state.
- Ack/clear/reset/go fields are action-oriented and may be self-clearing, edge-sensitive, or write-one-to-clear depending on the register specification.
- Indexed AUX and packet payload data windows expose transient transfer/payload staging state, not durable software storage.

The generated macros do not say whether a field is read-only, write-only, write-one-to-clear, self-clearing, latched on vblank, or double-buffered. Consumers must rely on Display Core sequencing and hardware documentation.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register contract and is meaningful together with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h`, which provides the matching `mm*` register offsets and base-index macros.
- Adjacent sections of `dcn_2_0_0_sh_mask.h`, because this range starts inside `DP_AUX0_AUX_INTERRUPT_CONTROL` and ends inside the DIG0 AFMT/generic packet region.
- DCN/DCE Display Core register-list and field-list macros, especially AUX and stream-encoder macros that turn these generated constants into typed shift/mask structs.
- Register helper infrastructure in AMDGPU Display Core and DMUB service code.

Primary integration points are:

- DP AUX and DPCD access: link training, EDID-over-AUX paths for DP/eDP, sideband transactions, AUX timeout/error handling, and HPD-disconnect-sensitive AUX cancellation.
- AUX low-speed/GTC sync paths: low-speed status/update handling, GTC sync lock/error interrupts, global-time-code synchronization, and link-side timing diagnostics.
- Power and wake sequencing: AUX PHY wake request/pending/ack handling and AUX reset/enable behavior around suspend/resume, HPD, and link bring-up.
- Stream encoder programming: source selection, stream start, stereo sync, TMDS encoding/color format, HDMI deep-color/scrambling/clock-channel control, Dolby Vision metadata enable, and HDMI packet-generation behavior.
- HDMI audio and metadata: audio packet timing, ACR generation, AFMT audio channel/layout/HBR controls, ISRC/MPEG/generic packet payload programming, metadata engine double-buffering, and HDMI general-control AVMUTE behavior.
- Diagnostics and validation: digital output CRC, test patterns, random patterns, FIFO status/calibration, HDMI packet error status, and metadata missed status.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong shift, wrong mask, stale generated value, or mismatch with `dcn_2_0_0_offset.h` can compile successfully while programming the wrong bit in display hardware.
- The chunk boundary is not semantic. It starts in the middle of `DP_AUX0_AUX_INTERRUPT_CONTROL`, so the full interrupt-control field set requires the previous chunk. It ends after `DIG0_AFMT_GENERIC_0`, while later generic packet payload registers and additional DIG instances continue outside this range.
- AUX instances are repetitive. `DP_AUX1` through `DP_AUX5` are near-identical macro families, and many consumers use `DP_AUX0` field names with instance-specific offsets. An instance mismatch can route a transaction to the wrong AUX engine or read the wrong connector's sideband status.
- AUX status/error handling is timing-sensitive. Timeout, overflow, HPD disconnect, invalid sync/start/stop, partial byte, NACK, CP IRQ, and reply-byte-count fields drive recovery decisions. Misinterpreting them can cause failed EDID/DPCD reads, link-training failures, or bad retry behavior.
- Ack and clear fields can have side effects. `*_ACK`, `*_CLEAR`, `*_RESET`, `*_GO`, `*_DONE_USING_AUX_REG`, and similar fields should not be touched by generic read-modify-write code unless the driver intends the side effect.
- DPHY timing masks are protocol-critical. Bad AUX precharge, start/receive window, timeout multiplier, detection threshold, or phase-detect settings can make AUX unreliable only on specific monitors, cables, bit rates, power states, or HPD timing windows.
- GTC sync fields are synchronization-critical. Incorrect lock acquisition, maintenance period, interval reset, threshold, retry, and ack handling can break synchronization or hide real link timing faults.
- HDMI packet scheduling is frame/line-sensitive. Wrong generic packet line, infoframe line, VBI packet send/continuous flags, or double-buffer handling can produce missing audio/infoframes, stale metadata, or compliance failures.
- HDMI deep color, scrambling, TMDS encoding, and clock-channel-rate fields affect sink interoperability. Incorrect settings can produce black screens, link errors, color format mismatches, or unstable HDMI 2.x-style operation.
- AFMT and audio packet fields are externally visible. Bad channel enable/layout, ACR source/N-multiple, HBR override, 60958 override, or packets-per-line settings can cause no audio, wrong channel mapping, dropouts, or sink audio-format rejection.
- Diagnostic and test-pattern fields can disturb normal output if left enabled. CRC, static/random test patterns, FIFO override/recalibration, and output test paths should be isolated to debug or validation flows.
- Full-byte payload fields are densely packed. Packet header/payload programming must preserve byte order and checksum expectations; masks alone do not validate HDMI/CEA packet semantics.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build AMDGPU/DC with DCN20 support enabled so missing or renamed masks fail in DCN20 resource, AUX, stream encoder, IRQ, GPIO, DMUB, and clock-manager paths.
- Static generated-header checks that every `__SHIFT` has a corresponding `_MASK`, masks align with shifts, and repeated `DP_AUX1` through `DP_AUX5` layouts remain consistent with `DP_AUX0` where hardware expects shared field layouts.
- Diff checks against the authoritative DCN 2.0 register database and `dcn_2_0_0_offset.h`, especially around this chunk's beginning and ending boundaries.
- DP/eDP AUX tests: EDID reads, DPCD reads/writes, link training, retry paths, HPD disconnect during AUX, timeout/overflow handling, CP IRQ handling, and suspend/resume or runtime power transitions.
- AUX PHY timing tests across varied displays, cables, and power states, watching for intermittent AUX timeout, invalid start/stop/sync, NACK, and reply-byte-count anomalies.
- GTC sync validation on hardware paths that use AUX GTC synchronization: lock acquisition, lock loss, error thresholds, retry behavior, and interrupt/ack delivery.
- HDMI modeset tests across TMDS encoding/color formats, deep-color depths, scrambling enabled/disabled paths, clock-channel-rate changes, and high-bandwidth modes.
- HDMI packet tests for AVI/audio/MPEG/generic/infoframe metadata, line scheduling, continuous/send behavior, checksums, ISRC payloads, and metadata missed status.
- HDMI audio tests for 2-channel and multichannel layouts, channel-enable masks, HBR, 60958 override behavior, ACR generation, and audio stability over modesets and hotplug cycles.
- Double-buffer tests that verify `HDMI_DB_*`, `VUPDATE_DB_*`, and `METADATA_DB_*` pending/taken/clear behavior drains as expected and does not expose stale or partially updated metadata.
- Diagnostic tests using DIG output CRC, test patterns, FIFO status/error ack, HDMI packet error status, and metadata missed status, with confirmation that debug features are disabled after use.

## Cross-Chunk Notes

This source slice starts after the `DP_AUX0_AUX_INTERRUPT_CONTROL` register comment and after some of that register's earlier fields. It should be merged with the previous chunk for a complete `DP_AUX0` interrupt-control description. It ends immediately after the first `DIG0_AFMT_GENERIC_0` payload byte register, so the final per-file report should merge later chunks before describing the full DIG0 generic packet payload space and additional digital stream-encoder instances.
