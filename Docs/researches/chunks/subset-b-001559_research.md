# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 54983-57512

## Scope

This chunk covers lines 54983-57512 of the generated-style AMD DCE 12.0 register shift/mask header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable code. The chunk starts inside the `DSI1_DISP_DSI_DLN0_PHY_ERROR` macro family and ends at the first two definitions for `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_WIRELESS_DISPLAY_IDENTIFICATION`; the following endpoint registers continue in later lines.

The slice contains 2530 source lines, with 2053 `#define` lines and 411 register/address-block comments. Its exported interface is the set of globally visible register-field macros that AMDGPU display code combines with companion offset headers and MMIO/indexed-register access helpers.

## Purpose

The macros describe bit offsets and already-positioned masks for several DCE display, DisplayPort receiver, performance, and Azalia audio register blocks:

- Tail of DSI1 MIPI DSI control and status: lane-zero PHY error bits, low-power/high-speed timeout timers, PHY timing, EOT packet fields, generic escape triggering, MIPI BIST setup/status, error interrupt masks, DSI interrupt control, DSI clock state, FIFO state/control, TE handling, lane status, performance mode, readback count, and command-memory power control.
- `dce_dc_dprx_sd0_dispdec` and `dce_dc_dprx_sd1_dispdec`: two DisplayPort receiver stream decoder instances with stream enable, MSA/VBID decode, current-line and display-timer state, MSE saturation, pixel format, received/toggled stream status, line-number triggers, main and secondary deframing errors, VCPF phase state, majority-vote and pixel FIFO errors, SDP steering/data/errors, audio headers, FIFO errors, measured totals, BS counter, and MSE action handling.
- `dce_dc_dc_perfmon10_dispdec`: one display performance monitor instance with counter-control, event-selection, state, monitor-control, interrupt, and counter-value registers.
- `dce_dc_dc_zcalregs_dispdec`: impedance/calibration-related control, DFX, and fuse fields.
- Sparse VGA memory page address aliases for write/read page address blocks.
- `dce_dc_azdec`: Azalia HDA controller command/response rings, immediate command windows, DMA position buffer base, and wall-clock alias fields.
- `dce_dc_azstream0_azdec` through `dce_dc_azstream7_azdec`: eight Azalia output stream descriptor instances.
- `azf0stream0_streamind` through `azf0stream15_streamind`: sixteen indexed Azalia stream performance/latency and FIFO-size control blocks.
- Beginning of `azf0endpoint0_endpointind`: endpoint0 converter and pin-widget definitions, including format/channel control, digital converter state, supported formats/rates, GTC embedding/counter deltas, pin capabilities, unsolicited responses, pin sense, speaker/channel allocation, audio descriptors, multichannel enables, lipsync/HBR response fields, sink information strings, hot-plug/audio-enable control, configuration defaults, IEC 60958 channel-status override fields, LPIB snapshots, coding type, format-change notification, and wireless-display identification.

## Important Macro Families

Every field follows the generated naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in its final register position.
- If the hardware field itself is named `*_MASK`, the generated macro becomes `REGISTER__FIELD_MASK__SHIFT` plus `REGISTER__FIELD_MASK_MASK`; this awkward-looking double `MASK` form is intentional.

The DSI1 section exposes order-sensitive control fields. Timeout registers provide `LP_RX_TO`, `BTA_TO`, and `HS_TX_TO`; status registers pair timeout status bits with same-position clear bits. Error interrupt coverage spans readback ECC/CRC/incomplete-packet errors, error packets, interleave/TE aborts, D-PHY lane errors, timeout events, DMA/command FIFO underflows, display-engine FIFO overflow/underflow, per-lane HS FIFO overflows, LP FIFO overflow, and interleave-operation contention. `DSI_INTERRUPT_CTRL` uses repeated status/ack/mask triplets for command-mode DMA/DENG completion, video-mode done, error, software BTA done, and TE trigger. FIFO and lane status macros surface underflow/overflow, FIFO full/empty, packet counts, lane busy/ready/stop-state, and ULPS active flags.

The DPRX stream decoder blocks are nearly identical for `DPRX_SD0` and `DPRX_SD1`. They expose stream and packet decode state: MSA words, VBID, current line, timer snapshot/mode, MSE SAT values, force-update and active state, vertical parameter, pixel format, MSA received/toggled bits, line-number match interrupts, detailed main/secondary deframing errors, VCPF phase lock/error, majority-vote errors, pixel FIFO errors, SDP payload sizing and steering, SDP received levels/data/errors, audio header and FIFO error state, SDP control, measured vertical/horizontal totals, BS counter, and MSE active-action handling.

`DC_PERFMON10` mirrors the perfmon layout seen in other DCE chunks. It includes event selection, counted-value selectors, increment mode, hardware gating, count-off and restart controls, interrupt enable/status/ack, active state, interrupt type, counter-selection fields, counted-value type, stop selectors, packed counter state fields, perfmon report count and state, clock enable, and low/high counter-value readback.

The Azalia controller and stream descriptor macros describe HDA-like ring-buffer and stream state. `CORB_*` and `RIRB_*` cover write/read pointers, control, status, size, and base addresses. Immediate command windows include input/output data and indices plus status. `DMA_POSITION_*` and `WALL_CLOCK_COUNTER_ALIAS` expose DMA position and timing. Each `AZSTREAM0` through `AZSTREAM7` descriptor has the same control/status layout: stream reset/run, IOCE/FEIE/DEIE interrupt enables, descriptor error/FIFO-ready/status flags, traffic priority, stripe control, stream number, link position, cyclic buffer length, last valid index, FIFO size, format fields, BDL pointer lower/upper address, and link-position alias.

The indexed `AZF0STREAM0` through `AZF0STREAM15` blocks are compact and repeated: FIFO size allocation, latency counter reset/enable, worst-case latency, cumulative latency, and cumulative request count. These are likely selected through an indexed endpoint/stream register window rather than direct MMIO offsets.

The endpoint0 converter/pin section maps display-audio codec semantics. Converter fields cover audio widget capabilities, channel count, supported PCM size/rate and stream formats, converter sample format, channel/stream ID, digital converter enable/validity/category/copyright/non-audio/professional bits, stripe control, ramp rate, GTC embedding, and min/current/max GTC deltas. Pin fields cover pin widget capabilities, capabilities flags, unsolicited response tag/enable, pin-sense, output enable, speaker/channel allocation and HDMI/DP connection flags, audio descriptors 0-13, multichannel lane/channel enable/mute/channel IDs, lipsync/HBR responses, sink info bytes, hot-plug/audio-enabled flags, forced unsolicited response payloads, configuration default fields, IEC 60958 channel-status overrides, association info, digital output active state, LPIB snapshot/position/timer state, coding type, format-change reporting, and wireless-display identification.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The macro names are the ABI-like surface used by AMDGPU display code. Callers are expected to use matching register address macros from companion generated offset headers, then apply these field macros through register helpers or normal read/modify/write code.

This file is included directly by DCE 12.0 display components, including `display/dc/dce120/dce120_timing_generator.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/resource/dce120/dce120_resource.c`, DCE 12.0 GPIO factory/translation code, and `amdgpu/gmc_v9_0.c`. The macro names therefore need to remain stable for both display core code and low-level AMDGPU integration.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the fields:

1. Select a register instance by choosing the macro family, such as `DPRX_SD0` versus `DPRX_SD1`, `AZSTREAM0` through `AZSTREAM7`, or `AZF0STREAM0` through `AZF0STREAM15`.
2. Read a MMIO or indexed register through the matching offset/address macro.
3. Clear existing bits with `*_MASK`, shift new values with `*__SHIFT`, then write the combined value back.
4. For status and interrupt registers, read status bits and write ack/clear bits named `*_ACK`, `*_AK`, `*_CLR`, or `*_CLEAR` according to the hardware register semantics.
5. For FIFOs, rings, stream descriptors, and perfmon counters, poll or snapshot status/readback fields after enabling run or measurement fields.

The most sequencing-sensitive areas are DSI timeout/error clearing, DSI interrupt ack/mask handling, DSI clock and FIFO readiness, DPRX line-number/deframing/SDP error status, perfmon start/stop and interrupt ack, Azalia CORB/RIRB pointer/control updates, stream descriptor reset/run transitions, and endpoint format/audio-enable changes.

## State and Persistence

The header itself stores no software state and has no persistence. Its constants describe hardware state fields that persist in display-controller, receiver, performance-monitor, and audio registers until reset, power-management transitions, firmware/hardware updates, or driver writes change them.

Visible state domains include:

- DSI1 D-PHY lane error latches, timeout counters/status, packet/EOT control, BIST configuration and completion, interrupt status/masks/acks, clock ready/error state, DENG and command FIFO state, TE trigger/line state, lane stop/ULPS/ready/busy state, and command-memory power state.
- DPRX SD0/SD1 stream decode state, MSA/VBID snapshots, timer/current-line state, MSE saturation, stream-status toggles, deframing/majority-vote/pixel-FIFO/SDP/audio FIFO error latches, measured frame totals, and MSE action state.
- Perfmon10 configuration, event selection, active state, interrupt latches, and low/high counter values.
- ZCAL control/DFX/fuse state that can affect calibration behavior.
- Azalia controller ring state, immediate command status, DMA position base, wall-clock counter, stream descriptor run/reset/interrupt/error state, buffer positions, audio format, BDL pointers, latency counters, and endpoint codec/pin configuration.
- Endpoint0 display-audio pin state, including sink descriptors, hot-plug/audio-enabled state, unsolicited response behavior, IEC 60958 channel status overrides, LPIB snapshots, format-change state, and wireless display identification.

Several fields are full-width `0xFFFFFFFFL` values for data, address, counter, association, payload, and description registers. Others are single-bit status/enable/ack fields. Callers must preserve reserved bits and use the correct access width/path, especially for indexed Azalia endpoint and stream registers.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is useful only with the generated DCE 12.0 offset/address headers and AMDGPU display register access helpers. Its integration points are low-level and hardware-facing:

- DCE 12.0 display core code that includes `dce_12_0_sh_mask.h`.
- DSI command/video-mode, D-PHY, FIFO, timeout, BIST, and interrupt handling paths.
- DisplayPort receiver diagnostics or bring-up code that reads stream decoder MSA/VBID, line, SDP, audio, FIFO, and deframing fields.
- Display performance-monitor setup and counter collection paths.
- Calibration or bring-up code touching ZCAL fields.
- HDMI/DP audio code using Azalia HDA controller, stream descriptor, stream latency/FIFO, converter, pin-widget, channel allocation, sink info, lipsync, HBR, channel-status, and LPIB fields.
- Companion ASIC-generation data: the same endpoint and pin-control names appear in nearby ASIC families and offset headers, so this chunk must reconcile with per-ASIC offset files rather than standalone names.

Repeated instance prefixes are important integration signals. `DPRX_SD0`/`DPRX_SD1`, `AZSTREAM0`-`AZSTREAM7`, and `AZF0STREAM0`-`AZF0STREAM15` have parallel layouts; callers should select the instance explicitly instead of deriving names manually.

## Risks

The primary risk is silent hardware misprogramming. Any incorrect mask or shift compiles normally but can update the wrong register field, corrupt reserved bits, miss an interrupt ack, or leave status latches uncleared. These failures may present as display link instability, DSI command timeouts, missing TE/BTA completion, DisplayPort receiver decode errors, audio stream failures, or lost interrupts rather than a direct software fault.

Boundary risk exists for this chunk: it starts after the beginning of `DSI1_DISP_DSI_DLN0_PHY_ERROR` and ends before the complete wireless-display/remote-keepalive/audio-enable endpoint region. The final per-file reconciliation should merge adjacent chunks before treating the DSI PHY-error and endpoint0 sections as complete.

Generated names ending in `MASK_MASK` are easy to misread but represent legitimate fields named `*_MASK`. Renaming or simplifying them would break existing generated-code conventions and call sites.

Repeated register layouts increase copy/generation risk. A one-bit drift between `DPRX_SD0` and `DPRX_SD1`, between `AZSTREAM*` instances, or among `AZF0STREAM*` latency blocks would be hard to see in review and may only affect a subset of links or audio streams.

Status/ack/clear fields are especially sensitive. Some bits share the same shift and mask for status and clear/ack semantics, so drivers must know whether a write-one-to-clear, write-one-to-ack, or read-only access is required from the hardware spec. Blind read/modify/write can accidentally clear latched errors or acknowledge interrupts.

Audio fields combine HDA, HDMI/DP audio-infoframe-like, IEC 60958, and display hotplug semantics. Incorrect channel allocation, descriptor, format, stream ID, or channel-status fields can produce user-visible audio failures even when display modesetting succeeds.

## Test Signals

Useful validation signals for this chunk are mostly static and hardware-integration oriented:

- Build coverage for all DCE 12.0 translation units that include `dce_12_0_sh_mask.h`.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has a matching mask, masks align with their shifts, repeated instances have identical field layouts where expected, and no duplicate macro names collide.
- Diff or regeneration checks against the authoritative ASIC register database for DCE 12.0.
- DSI hardware smoke tests covering command mode, video mode, timeout/error clearing, TE events, BTA completion, FIFO underflow/overflow reporting, lane stop/ULPS state, and MIPI BIST done/status.
- DPRX receiver diagnostics that verify MSA/VBID decode, line-number triggers, measured totals, SDP reception/data/error paths, audio FIFO errors, deframing errors, and stream-status toggles on both SD0 and SD1.
- Perfmon tests that program `DC_PERFMON10`, start/stop counting, read low/high values, and exercise interrupt status/ack fields.
- Azalia/HDMI/DP audio tests that start and stop stream descriptors, verify CORB/RIRB and immediate command paths, check DMA/LPIB position snapshots, validate channel allocation and audio descriptors, test multichannel/HBR/lipsync paths, and confirm hot-plug/audio-enabled and unsolicited-response behavior.
- Register readback tests around full-width address/data/counter fields to catch truncation from signed or narrow intermediates.

## Cross-Chunk Notes

This is one interior slice of a 64798-line generated header. The final per-file document should reconcile this research with adjacent chunks for the beginning of the DSI1 PHY-error block before line 54983 and the continuation of endpoint0 remote-keepalive/audio-enable/status registers after line 57512.
