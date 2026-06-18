# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 7219-9704

## Scope

This chunk is a generated AMD Display Core Next 3.1.4 register-field mask slice. It contains C preprocessor constants only: `_SHIFT` macros for field least-significant-bit positions, `_MASK` macros for raw 32-bit field masks, and comment markers that group those definitions by hardware register and address block. There are no C functions, structs, enums, variables, branches, loops, allocations, locks, or direct MMIO accesses in this range.

The requested range begins in the `AZF0INPUTENDPOINT7` HD-audio input endpoint pin definitions after the input-converter stream-format and supported-size/rate fields from the prior chunk. It then covers audio descriptor index registers, legacy VGA/MMHUBBUB register fields, HDA/Azalia immediate-command endpoint registers, a large DCCG display clock-generation and gating block, an Azalia F2 codec/output-pin/input-pin register surface, and ends at the first register of the DC perfmon0 block, `DC_PERFMON0_PERFCOUNTER_CNTL`. The following `DC_PERFMON0_PERFCOUNTER_CNTL2` group starts after the requested line boundary.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU display code and DCN 3.1.4 display hardware. Companion generated offset headers provide the register addresses; this mask header provides the field positions and masks that register helper macros use to pack values, extract readback fields, and perform read/modify/write operations without embedding numeric bit positions in functional code.

Major hardware areas represented here:

- `AZF0INPUTENDPOINT7` input pin metadata and controls for an HDA/Azalia input endpoint. These fields describe audio widget capabilities, pin capabilities, unsolicited responses, pin sense, widget enable state, multichannel enable/mute/channel IDs, HBR capability/enable, channel allocation, hot-plug audio state, configuration defaults, LPIB snapshots, input activity, infoframe state, and channel status.
- `azendpoint_descriptorind` audio descriptor registers `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`. Each descriptor exposes short audio descriptor fields such as channel count, sample-rate mask, byte slots, format code, bit-rate/code fields, and maximum bit rate for HDMI/DP audio capability advertisement.
- `dce_dc_mmhubbub_vga_dispdec[72..76]` and `dce_dc_mmhubbub_vga_dispdec` legacy VGA/MMHUBBUB fields. These include VGA memory page addressing, render/control state, sequencer reset/control, VGA modes, pitch and surface addresses, HDP/cache controls, per-pipe VGA controls, interrupt/status/clear fields, CRTC/attribute/graphics sequencer indexed ports, DAC access, source select, QoS, and test controls.
- HDA immediate command output/input endpoint register pairs for Azalia endpoint and input endpoint data/index access.
- `dce_dc_dccg_dccg_dispdec` display clock-generation fields. The chunk covers PHYPLL pixel-clock resync controls, DP DTO/DBUF enables, DSC/DPP/DTB/audio DTO parameters, clock gating/test toggles, gate-disable controls, stream-clock controls, global fine-grain clock-gating reporting, GTC DTO/current controls, millisecond/microsecond timebase dividers, display clock frequency-change controls, memory power requests, CAC/status, pixel-rate controls for OTG0-OTG3, symbol-clock controls/enables, DCCG soft reset, vsync latch/counter controls, HDMI/PHY stream clock controls, DMCUB clock control, and dentist DISPCLK control.
- `AZALIA_F2` codec root, function, converter, output pin, and input endpoint fields. These definitions expose HDA codec identity/capability data, function power/reset/synchronization controls, converter format/channel/digital-converter controls, widget capability/rate/format parameters, output pin connection/widget/unsolicited/pin-sense/configuration/default/speaker/channel-allocation/multichannel/LPIB/status/keepalive controls, input converter controls, and input pin activity/infoframe/channel-status/capability fields.
- The first `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` performance counter control register. `DC_PERFMON0_PERFCOUNTER_CNTL` selects the event, counted value, increment mode, hardware/run-enable behavior, restart/interrupt/off-mask behavior, active status, and counter control selection.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw mask within the 32-bit register.
- `// addressBlock: ...` comments identify the display hardware aperture for following definitions.
- `//<REGISTER>` comments group field definitions by MMIO register.

Important field families in this chunk:

- Azalia input endpoint pin fields include `AUDIO_WIDGET_CAPABILITIES`, `CAPABILITIES`, `UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, `WIDGET_CONTROL`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB`, `INPUT_STATUS_CONTROL`, `INFOFRAME`, and channel-status readbacks. These are the bit-level contract for input audio pin discovery, routing, event reporting, and stream status.
- Audio descriptor fields are repeated for descriptors 0 through 13. Each register carries `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, `DESCRIPTOR_BYTE_2`, `FORMAT_CODE`, `SUPPORTED_CODECS`, `DESCRIPTOR_BYTE_3`, and `MAX_BIT_RATE`, allowing the driver or firmware to expose sink audio capabilities through indexed descriptor storage.
- VGA fields cover stateful legacy display emulation. Key controls include render enable/stop status, graphics/address mode, chain/odd-even modes, host read/write select, surface pitch/address selection, memory base high/low, HDP enable/flush/invalidation, cache enable/flush/invalid flags, per-pipe VGA enable/mode/source control, interrupts, status clears, source select, and indexed VGA I/O register data paths.
- DCCG clocking fields are broad and timing-sensitive. The block includes pixel clock resync bypass/enable/status for PHYPLLA-E, stream clock source/enables, DP DTO phase/modulo controls, DSC/DPP/DTB/audio DTO phase/modulo and source controls, gate-disable fields for DISPCLK, DPPCLK, DSCCLK, DTO clocks, PHY/SYM clocks, HDMI character/stream clocks, DMCUBCLK, and fine-grain/CGTT clock-gating controls.
- DCCG timing counters and synchronization fields include GTC DTO increment/modulo/current, millisecond and microsecond time-base divisors, vsync latch values for OTG0-OTG5, vsync counter control/int control, and dentist DISPCLK divider controls. These fields feed timing correlation, firmware services, and clock-domain synchronization.
- DCCG power and reset fields include display clock frequency-change control, memory global power request control, DCCG soft-reset bits for clock slices, global fine-grain clock-gating reporting, CAC status, and clock-on-state or enable readbacks. These fields interact with runtime power management and safe clock transitions.
- Azalia F2 codec root/function fields expose vendor/device/revision/subordinate-node data, power states, subsystem ID response bytes, converter synchronization, function reset, group type, supported sample sizes/rates, stream formats, and power-state capability masks.
- Azalia F2 converter fields program HDA stream format and routing: stream type, sample base rate/multiple/divisor, bits per sample, channel count, channel/stream ID, digital-converter status bits, stripe control, ramp rate, GTC embedding, widget capabilities, supported sizes/rates, and stream format masks.
- Azalia F2 output pin fields cover widget enable, unsolicited response, pin sense, configuration defaults split across multiple byte-oriented registers, speaker allocation, channel allocation, down-mix inhibit, audio descriptor selection/data, multichannel pair and single-channel controls, lipsync, HBR, audio sink info index/data, channel-status overrides, association info, digital output status, LPIB snapshots, coding type, format-change notification/response, wireless-display identification, remote keepalive, and pin capability/readback data.
- Azalia F2 input endpoint fields mirror the input path: converter format/channel/digital-converter controls, widget capability/rate/format parameters, input pin widget and unsolicited-response controls, pin sense and configuration defaults, channel allocation, per-channel multichannel enable/mute/channel ID fields, HBR, LPIB, input activity/change unsolicited-response enables, infoframe validity/channel allocation, channel-status readbacks, and input pin capability masks.
- `DC_PERFMON0_PERFCOUNTER_CNTL` fields identify one hardware performance counter's event select, counted-value select, increment mode, hardware control select, run-enable mode, count-off start disable, restart enable, interrupt enable, off mask, active status, and counter-control select.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears only when AMDGPU Display Core, DMUB support code, or related generated register tables combine these macros with register offsets and MMIO helper APIs. A typical usage pattern is:

1. Select a DCN 3.1.4 register address from the companion generated offset table.
2. Use this chunk's `_SHIFT` and `_MASK` constants to pack or extract a field value.
3. Read, write, or update the register through display register helpers or firmware register tables.
4. Let display hardware retain configuration fields, update status fields, or consume side-effecting command/clear bits.

The state represented here is hardware register state rather than driver-owned memory:

- Persistent configuration fields include Azalia stream formats, channel/stream IDs, multichannel enable/mute/channel IDs, HBR enable, channel allocation, descriptor contents, VGA render/mode/cache/HDP/source selections, DCCG clock source and DTO parameters, clock gating disables, soft-reset controls, timebase dividers, function power state, converter synchronization, and perfmon event/control selects.
- Volatile readback/status fields include pin sense/presence, hot-plug audio enabled state, input activity, infoframe validity, LPIB and timer snapshots, VGA busy/stop/status/interrupt flags, cache/HDP flush-done state, clock-on/status bits, CAC status, vsync latches/counters, GTC current values, digital output status, format-changed state, and perfcounter active status.
- Side-effecting write fields include unsolicited-response force bits, VGA status clear and interrupt controls, cache/HDP flush or invalidation triggers, sequencer reset controls, DCCG soft-reset fields, frequency-change controls, vsync counter interrupt clears/masks, Azalia function reset, format-change acknowledgement/response fields, remote keepalive enable, LPIB snapshot lock, and perfcounter restart/interrupt enables.
- Indexed or indirect register paths need ordered access. VGA CRTC/attribute/graphics/sequencer index/data pairs and Azalia immediate-command index/data registers require callers to select an index before data access and to serialize against other users of the same indexed aperture.
- Clock and audio state are sequencing-sensitive. DCCG DTO parameters, stream-clock enables, gate disables, PHYPLL pixel-rate controls, audio DTO source/phase/module fields, and Azalia converter/pin controls must be coordinated with active links, stream enable/disable, audio packet programming, and power-gating transitions.

The masks do not encode ordering or locking requirements. Correct callers still need to hold the relevant display locks, respect register access domains, avoid touching clock-gated blocks prematurely, use update or reset sequencing where required, and avoid read/modify/write patterns that accidentally rewrite clear, force, reset, or trigger bits.

## Dependencies And Integration Points

This chunk is used with generated DCN 3.1.4 register headers and the AMD display register abstraction:

- `display/dmub/src/dmub_dcn314.c` includes both `dcn/dcn_3_1_4_offset.h` and this `dcn/dcn_3_1_4_sh_mask.h`, then builds DCN 3.1 register tables with field masks and shifts. This confirms the header participates in table-driven register access for DCN 3.1.4 DMUB support.
- Companion generated offset/address headers provide the `reg...` values that pair with these `_SHIFT` and `_MASK` macros.
- AMDGPU Display Core register helper macros consume field names through generated tables for `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and similar access patterns.
- Display audio and HDMI/DP audio code depends on the Azalia F0/F2 codec, converter, pin, descriptor, channel-allocation, HBR, LPIB, infoframe, channel-status, and sink-info definitions to program audio routing and expose HDA codec capabilities.
- Hot-plug and unsolicited-response handling integrates with pin sense, presence-detect, unsolicited-response tag/enable/force, format-changed, input-activity, and keepalive fields.
- Legacy VGA support and early boot/framebuffer handoff paths depend on the VGA render, memory, surface, pitch, source-select, indexed I/O, DAC, cache, HDP, status, and interrupt fields.
- Display clock management depends on DCCG fields for stream clocks, DTOs, pixel-rate divisions, PHYPLL resync, clock gating, soft reset, timebase generation, vsync latching/counters, dentist DISPCLK control, DMCUBCLK control, and audio clock DTO generation.
- Runtime power management and suspend/resume paths integrate with DCCG clock-on states, gate-disable controls, soft resets, memory power requests, frequency-change state, and Azalia power/reset fields.
- Diagnostics and performance tooling can use the DC perfmon0 counter control fields, DCCG CAC/status fields, clock status readbacks, VGA status, LPIB snapshots, and audio infoframe/channel-status readbacks.
- The related enum headers, such as `soc21_enum.h` and older generation enum headers, document semantic values for several Azalia F2 fields. This mask header only provides bit positions and masks, not the named field values.

Because these are generated macros, missing macro names generally fail at compile time only where referenced. Incorrect numeric masks or shifts can compile cleanly and then misprogram display hardware at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.4 register specification is the primary risk. A wrong shift or mask can write the wrong bit in clock, VGA, audio, or perfmon hardware, causing display audio failures, clock instability, legacy VGA breakage, or invalid performance counter results.
- The chunk contains several repetitive blocks. Audio descriptors 0-13, multichannel controls, per-channel enable registers, and repeated DCCG pixel-rate/DTO controls are vulnerable to copy-generation or prefix mistakes that still compile if the wrong macro name exists.
- The range starts and ends mid-topic. It begins after prior `AZF0INPUTENDPOINT7` input-converter fields and ends after `DC_PERFMON0_PERFCOUNTER_CNTL`, before `DC_PERFMON0_PERFCOUNTER_CNTL2`. The merge lane must combine adjacent chunks for a complete per-file picture.
- Side-effecting fields require care with read/modify/write helpers. Unsolicited-response force, reset, clear, flush, invalidate, interrupt clear, status clear, restart, and snapshot lock fields should not be accidentally rewritten while changing adjacent configuration bits.
- Clock-generation fields are highly timing-sensitive. Bad DTO phase/modulo, pixel-rate divider, stream-clock source, gate-disable, soft-reset, or dentist DISPCLK values can break active display pipes or audio clocking in ways that are not caught by compile-time checks.
- Audio routing fields must match the active connector, stream, and sink. Incorrect stream format, channel count, channel allocation, HBR, audio descriptor, infoframe, LPIB, or channel-status values can produce silent audio, malformed HDMI/DP audio metadata, or unstable hot-plug behavior despite normal video output.
- Indexed VGA and HDA immediate-command accesses can be corrupted by interleaving. Callers need serialization around index/data register pairs or descriptor-indirect paths.
- Legacy VGA fields interact with boot firmware state and framebuffer handoff. Incorrect render stop, memory mapping, surface address, cache/HDP invalidation, or source selection can disrupt console takeover or low-level modesetting.
- Full-width or wide fields such as descriptor data, LPIB snapshots, channel status, GTC/current counters, DTO phase/modulo values, surface addresses, and perfcounter event fields provide no type or range checking here. Callers must validate units and ranges before packing values.
- Power and reset state can make readbacks unreliable. Clock-on, busy, reset, and gate states must be sequenced before trusting DCCG, VGA, or Azalia status bits.

## Test Signals

Useful validation signals for this chunk are mostly generated-header checks plus hardware-facing display/audio behavior:

- Build AMDGPU with DCN 3.1.4 and DMUB support enabled and confirm all referenced generated field names resolve.
- Run generated-header consistency checks that every in-scope field has the expected `_SHIFT`/`_MASK` pair, masks fit within 32 bits, and fields do not overlap unexpectedly within each register.
- Compare the generated values against the authoritative DCN 3.1.4 register specification, with special attention to repeated descriptor, multichannel, DCCG DTO, and gate-disable blocks.
- Exercise HDMI and DisplayPort audio playback across common formats, channel counts, sample rates, HBR modes, and hot-plug cycles; verify audio descriptors, channel allocation, infoframes, channel status, LPIB snapshots, and converter stream IDs behave as expected.
- Test audio input/status paths where hardware exposes them, checking input activity, channel layout, input infoframe validity, channel status readbacks, unsolicited-response enables, and pin-sense/presence behavior.
- Validate Azalia codec enumeration and power transitions by checking vendor/device/revision/subordinate-node responses, power state handling, function reset, converter synchronization, and supported size/rate/format fields.
- Exercise legacy VGA handoff and console/modeset transitions, validating VGA render control, source selection, surface address/pitch, indexed CRTC/attribute/graphics/sequencer access, cache/HDP flush/invalidate behavior, and VGA interrupt/status clear behavior.
- Run display modesets over all relevant DCN 3.1.4 pipes while observing DCCG clock source, DTO phase/modulo, pixel-rate controls, PHYPLL resync status, stream-clock enables, and clock gating state.
- Test suspend/resume and runtime power-management transitions that toggle DCCG soft reset, gate-disable fields, DMCUBCLK, DISPCLK frequency-change controls, memory power requests, and Azalia power states.
- Validate vsync/GTC/timebase behavior by checking millisecond/microsecond dividers, GTC DTO/current values, vsync latch values for OTG0-OTG5, and vsync counter interrupt mask/type/status behavior.
- Use display diagnostics or perf tooling to program `DC_PERFMON0_PERFCOUNTER_CNTL`, select events, start/restart counting, enable interrupts where supported, and confirm active status and counted behavior match expectations.

## Chunk-Specific Summary

Lines 7219-9704 define a dense DCN 3.1.4 register-field mask surface, not executable logic. The chunk's most important responsibilities are HDA/Azalia F0 input endpoint pin status, indexed audio descriptors, legacy VGA/MMHUBBUB controls, HDA immediate command endpoints, DCCG clock/DTO/gating/timebase/reset controls, Azalia F2 codec/output/input endpoint fields, and the first DC perfmon0 control register. Correctness depends on exact generated masks and shifts, instance-correct macro use, careful handling of indexed and side-effecting registers, and hardware tests that cover display audio, hot-plug, VGA handoff, DCCG clock sequencing, power transitions, timing counters, and perfmon operation.
