# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 10356-12776

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display, audio, clock-generation, Azalia codec, and display performance-monitor registers. It contains no executable C code; its public interface is a dense set of `#define` constants describing bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside MMIO registers.

The requested range contains 2,102 generated definitions. It starts inside the `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` field list, covers Azalia output stream descriptor instances 1 through 7, covers a large `DCCG` display clock generator block, covers display-clock dentist control, covers Azalia function/converter/pin/input codec node fields, and ends inside the `DC_PERFMON1_PERFCOUNTER_STATE` group. The range boundaries are artificial: `AZSTREAM1` begins in the previous chunk, and `DC_PERFMON1` continues in the next chunk.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The ABI-like surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- `AZSTREAM1_0` through `AZSTREAM7_0`: HDA output stream descriptor control/status, link position, cyclic buffer length, last valid index, FIFO size, stream format, buffer descriptor list lower/upper base address, and link-position alias fields. The control/status fields include stream reset/run, completion/FIFO/descriptor interrupt enables, stripe control, traffic priority, stream number, completion status, FIFO/descriptor error status, and FIFO ready.
- `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL`: pixel-clock resynchronization delay, enable, and status fields for PHY PLL paths.
- `DP_DTO_DBUF_EN`, `DP_DTO[0-3]_PHASE`, and `DP_DTO[0-3]_MODULO`: DisplayPort DTO double-buffer enables and per-stream phase/modulo values.
- `DSCCLK[0-3]_DTO_PARAM` and `DSCCLK_DTO_CTRL`: DSC clock DTO phase/modulo and per-DSC-clock enable/read-update controls.
- `DPPCLK[0-3]_DTO_PARAM`, `DPPCLK_DTO_CTRL`, and `DPPCLK_CTRL`: DPP clock DTO controls and DPP clock enable bits.
- `DPREFCLK_*`, `DISPCLK_*`, `SOCCLK_*`, `SYMCLK_*`, `DTBCLK_P_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, `HDMISTREAMCLK_CNTL`, `DPIA*`, and `PHY*SYMCLK_CLOCK_CNTL`: DCCG clock source selection, enable, frequency-change, clock-gating, fine-grain clock-gating repeat, and ref/symbol clock control fields.
- `DCCG_GATE_DISABLE_CNTL` through `DCCG_GATE_DISABLE_CNTL6`: root and leaf gate-disable bits for DISPCLK, SOCCLK, DPREFCLK, HDMICHARCLK, HDMISTREAMCLK, DPSTREAMCLK, DPPCLK, DSCCLK, DTBCLK, PHY symbol/ref clocks, and SYMCLK32 paths.
- `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, and `DCCG_AUDIO_DTO0/1_MODULE`: display audio DTO source selection and phase/module programming.
- `DCCG_VSYNC_*`: OTG vsync latch values, selectable vsync counter start/end events, counter run/clear, max count, interrupt enable/ack/status bits, and interrupt-trigger mode.
- `DCCG_PERFMON_CNTL` and `DCCG_PERFMON_CNTL2`: DCCG performance measurement controls including run, mode, OTG selection, event-count mode, monitor select, and MUX/debug source fields.
- `DENTIST_DISPCLK_CNTL`: display-clock dentist divider programming, change mode, and change-done fields.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: function group vendor/device ID, revision, node counts, power state, subsystem ID response, converter synchronization, reset, size/rate, stream format, and power-state capability fields.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, stream/channel ID, digital converter controls, stripe/ramp controls, widget capabilities, supported rates/formats, and audio descriptor-related fields.
- `AZALIA_F2_CODEC_PIN_*` and `AZALIA_F2_PIN_CONTROL_*`: output pin widget control, unsolicited response, pin sense, default configuration, speaker/channel allocation, downmix, ACP/audio descriptors, multichannel enables, lipsync, HBR, audio sink info, channel-status override, pin association, LPIB snapshot/readback, coding type, format changed status, wireless display ID, remote keepalive, and pin capability fields.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin control fields, including input converter format/stream/channel/digital control, input pin sense/default config, channel allocation, multichannel enables, HBR, LPIB snapshots, input status/control, infoframe, channel status, and capabilities.
- `DC_PERFMON0` and the start of `DC_PERFMON1`: display performance-counter event selection, counted-value selection/type, increment mode, hardware run/stop control, count-off selection, restart/interrupt/active bits, per-counter state readback, perfmon state/report count, count-off interrupt control/status/ack, counter-value interrupt status/ack bits, and low/high counter readback fields.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register, shift, and mask tables:

1. DCN42 driver code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. Resource and hardware-block headers use token-pasting macros such as `SR`, `SRI`, `DCCG_SF`, `DCCG_SFI`, `DCCG_SFII`, `SF`, and related register-list helpers to bind generic field names to generated DCN42 register-field constants.
3. Runtime objects receive register offsets plus field shift/mask tables during construction.
4. Shared AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to read, write, and update MMIO bitfields.

The macros in this chunk do not encode sequencing. Stream descriptor start/stop, HDA buffer programming, DCCG clock programming, DTO update timing, Azalia codec verbs, audio DTO setup, vsync counter use, and performance-counter sampling are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- HDA output stream state: run/reset controls, descriptor and FIFO errors, buffer-completion interrupts, FIFO ready, stream number, stream format, BDL base address, cyclic buffer length, last valid descriptor index, and link position.
- DCCG clock state: clock source selection, enables, DTO phase/modulo values, double-buffer update controls, divider settings, resync status, gate-disable overrides, soft resets, CAC status, time-base divisors, and test/debug mux selection.
- Audio clock state: audio DTO source selection plus phase/module values used to derive audio clocks from display timing or link/reference clocks.
- Azalia codec state: function/converter/pin capabilities and controls, ELD/audio descriptors, speaker and channel allocation, pin sense, stream/channel IDs, HBR and multichannel controls, channel-status overrides, LPIB snapshots, format-change status, and remote/wireless-display information.
- Performance-monitor state: event selection, counter run/stop controls, active state, interrupt enable/status/ack bits, selected counter states, count-off behavior, and readback values.

Persistence and side effects are hardware-defined. Configuration fields usually remain until modeset, stream disable, audio reconfiguration, suspend/resume, clock gating/power gating, GPU reset, or ASIC reset rewrites them. Status and interrupt fields can be latched, write-one-to-clear, self-clearing, or valid only while their block is powered and clocked. This file only provides bit positions and masks; it does not describe those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes both generated headers and builds DCN42 resource objects, including audio, AUX/I2C, DCCG, DIO, DSC, HPO, IRQ, and other display block tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.h` consumes many DCCG names from this range through `DCCG_MASK_SH_LIST_DCN42_COMMON`, including DPPCLK, DISPCLK frequency change, DP/HDMI stream clocks, SYMCLK32, OTG pixel-rate dividers, DTBCLK, audio DTO, dentist display clock, gate-disable, DSCCLK, and PHY symbol-clock fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn42/dcn42_dccg.c` programs those DCCG fields through the register/shift/mask tables created from this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the shared audio register and mask/shift lists for audio DTO and Azalia capability fields; DCN42 resource construction uses this style for audio object setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` uses audio register tables to enable/disable Azalia, configure audio stream format, program DTOs, and derive display audio timing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes this header for DMUB/DCN42 register initialization, although this specific chunk is more directly relevant to display clocking, audio, and perfmon fields than to the DMUB boot/reset fields near the top of that source.

Behaviorally, this range is an endpoint for HDMI/DP audio stream programming, display clock tree programming, DTO and clock-gating setup, Azalia codec verb exposure, and display/DCCG performance-monitor instrumentation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting only one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are missing the beginning of `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, and the final lines stop before the rest of `DC_PERFMON1`; adjacent chunk reports must be reconciled before making whole-block claims.
- HDA stream descriptors are DMA-facing. Bad masks for BDL base address, cyclic buffer length, last valid index, stream number, or run/reset can cause silent audio, underruns, descriptor errors, FIFO errors, or DMA to the wrong address.
- Link position and LPIB fields are used for synchronization. Incorrect masks can break audio position reporting, A/V sync, underrun diagnosis, and snapshot-based debug.
- DCCG clock controls are sequencing-sensitive. Incorrect enables, source selections, DTO values, or divider fields can produce blank display, bad link rates, unstable pixel clocks, stuck update-pending behavior, or clock-domain glitches during modeset.
- Gate-disable fields have power and stability implications. Wrong masks can leave clocks ungated and waste power, or gate clocks required by active pipes, DSC, DPP, HDMI, DP, PHY, or audio paths.
- Audio DTO source/phase/module fields must match signal type and timing. Mistakes can create HDMI/DP audio sample-rate drift, channel-status mismatch, or no audio only on specific display modes.
- Azalia codec capability and pin/control fields are externally visible to the OS audio stack. Wrong capability masks can advertise unsupported sample rates, channel counts, HBR support, speaker allocation, ELD/audio descriptors, or power states.
- Pin sense, unsolicited response, remote keepalive, and format-change status fields may be interrupt or status sensitive. Bad masks can produce stale connector/audio presence state or repeated/missed audio notifications.
- Performance-monitor interrupt status/ack fields are easy to misuse. Wrong masks can leave interrupts asserted, miss counter overflow/count-off events, or read the wrong high/low counter value.
- Repeated instance families are copy-sensitive. `AZSTREAM1-7`, DPPCLK/DP DTOs, OTG pixel-rate controls, PHY clocks, and `DC_PERFMON0/1` are structurally similar; a generator error can affect only one stream, pipe, PHY, or perfmon instance.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display/audio behavior:

- Build DCN42 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_dccg.h`, `dcn42_dccg.c`, `dce_audio.h`, `dce_audio.c`, and DMUB register initialization paths.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure every `_MASK` has the expected paired `__SHIFT` definition.
- Cross-check this shift/mask range against `dcn_4_2_0_offset.h` so every field register in the chunk has a corresponding register offset and base-index entry.
- Run static repeated-instance checks for `AZSTREAM1-7`, `PHYPLL[A-E]`, `DP_DTO0-3`, `OTG0-3`, `DPPCLK0-3`, `DSCCLK0-3`, `SYMCLK[A-E]`, and `DC_PERFMON0/1`, while allowing intentional per-instance prefixes and any documented per-instance omissions.
- Exercise HDMI and DP audio across common and edge sample rates, channel counts, HBR/non-HBR modes, suspend/resume, display hotplug, and modeset transitions. Expected signals are stable audio, correct stream/channel IDs, no FIFO/descriptor errors, correct position reporting, and matching channel/speaker allocation.
- Validate DCCG programming across display modes that change DISPCLK, DPPCLK, DSCCLK, DP stream clocks, HDMI stream clocks, PHY symbol clocks, and DTBCLK. Expected signals are successful modesets, stable pixel/link clocks, no stuck frequency-change done/update bits, and no underrun-like symptoms.
- Exercise DSC-enabled modes to cover DSCCLK DTO/gate fields that feed the compressor path.
- Verify clock-gating and power behavior with active/inactive pipes, DP/HDMI displays, and audio enabled/disabled. Expected signals include no display/audio regressions and expected power-state transitions.
- Use register dumps around audio DTO and Azalia node programming to confirm advertised capabilities, ELD/audio descriptors, pin sense, HBR, multichannel, and LPIB fields match the connected sink and active stream.
- Exercise `DC_PERFMON0` and `DC_PERFMON1` counter programming, readback, count-off interrupts, and ack paths. Expected signals are monotonic counter values for selected events, correct high/low readback, and clearable interrupt status.

## Cross-Chunk Notes

The previous chunk owns `AZSTREAM0_0` and the beginning of `AZSTREAM1_0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`. This chunk starts at the `FIFO_ERROR_INTERRUPT_ENABLE` shift for `AZSTREAM1_0`, so the full `AZSTREAM1` control/status field list must be reconstructed during merge. The next chunk continues after `DC_PERFMON1_PERFCOUNTER_STATE`; it should cover the remaining `DC_PERFMON1` fields and later register families. The final per-file research document should reconcile these boundaries before describing all DCN 4.2.0 HDA stream, DCCG, Azalia, or perfmon metadata.
