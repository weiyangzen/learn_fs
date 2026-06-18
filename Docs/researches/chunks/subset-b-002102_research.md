# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 33205-35422

## Purpose

This chunk is a generated DCN 3.5.1 shift/mask header segment for AMD display controller hardware. It contains C preprocessor constants only: every symbol describes a bit position (`__SHIFT`) or bit mask (`_MASK`) for a field in a 32-bit MMIO register. The companion address data lives in `dcn_3_5_1_offset.h`; consumers combine the address macros with these field macros through AMDGPU/DC register helper macros such as `FD`, `FN`, `REG_SET`, and related wrapper patterns.

The line range is centered on display link instance 4 and the shared DCIO/GPIO register block. It begins at the end of `AFMT4_AFMT_AUDIO_PACKET_CONTROL2`, covers the complete `AFMT4`, `DME4`, `DIG4`, and `DP4` field groups for audio, HDMI/TMDS, DisplayPort, metadata, and link training, then moves into UNIPHY lane mapping, DCIO reset/pattern/sync controls, generic/DDC/GENLK/HPD GPIO controls, power-sequencer backlight controls, pad strength, and the start of AUX analog control. It ends partway through `DC_GPIO_AUX_CTRL_1`; `DC_GPIO_AUX_CTRL_2` begins in the following chunk.

## Important macros and register fields

There are no functions, structs, or enums in this chunk. The important API surface is the macro naming contract:

- `REG__FIELD__SHIFT` gives the right shift needed to align a field to bit 0.
- `REG__FIELD_MASK` gives the field mask in register position.
- `regREG` and `regREG_BASE_IDX` are provided by the companion offset header, not by this file.

Major register families in this chunk:

- `AFMT4_*`: audio formatter fields for link/audio instance 4. This includes HDMI/DP audio infoframe payload fields (`AFMT_AUDIO_INFO0`, `AFMT_AUDIO_INFO1`), IEC 60958 channel status (`AFMT_60958_0`, `_1`, `_2`), audio CRC control/result, test ramp controls, audio status, audio packet control, audio infoframe source/update bits, audio source selection, and `AFMT_MEM_PWR` memory power controls.
- `DME4_*`: metadata engine controls for instance 4, including HUBP requestor selection, metadata engine enable, stream type, double-buffer pending/taken/clear/disable bits, missed-transmission status/clear, and DME memory power fields.
- `DIG4_*`: digital encoder instance 4 fields. Covered groups include front-end source/bypass routing, output CRC, test and random pattern generation, HDMI packet/control/status/ACR fields, HDMI generic packet controls for packets 0-14, HDMI double-buffer handshakes, AFMT clock gating status, back-end source/HPD selection, and TMDS control character, sync, DC-balance, and generated-control fields.
- `DP4_*`: DisplayPort instance 4 fields. This is the largest family in the chunk and includes DP link and video-stream control, DPHY training/scrambler/PRBS/CRC/8b10b controls, fast training status, HBR2 patterns, MSA timing/colorimetry/misc fields, secondary data packet enables and scheduling, DP audio M/N registers and readbacks, MST MSE rate/SAT/status fields, MSO controls, DSC enable mode, ALPM/AUX-less ALPM fields, and DPIA spare bits.
- `UNIPHYA_*`, `UNIPHYB_*`, `UNIPHYC_*`, `UNIPHYD_*`, `UNIPHYE_*`: physical transmitter lane controls. A/B/C expose lane invert and channel crossbar source fields; D/E expose channel crossbar source fields in this slice.
- `DCIO_*`, `DC_PINSTRAPS`, and `INTERCEPT_STATE`: shared DCIO controls for write-command delay, pinstrap audio/SMS/clock-bypass status, spare register bits, intercept state visibility, pattern generator enable/value, BL PWM frame-start display selection, GENLK/swaplock GSL pad controls, and soft resets for UNIPHY A-G, DSYNC A-G, and PWRSEQ0/1.
- `DC_GPIO_*`: shared GPIO register field definitions. This chunk covers generic GPIO mask/A/EN/Y, DDC1-DDC5 and DDCVGA mask/A/EN/Y controls, GENLK mask/A/EN/Y, HPD mask/A/EN/Y, PWRSEQ0/1 enable routing for backlight signals, pad strength registers, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, and the start of AUX/I2C analog tuning in `DC_GPIO_AUX_CTRL_0` and `DC_GPIO_AUX_CTRL_1`.

## Control flow and usage model

This header has no runtime control flow. Its control behavior comes from how callers use the generated constants:

1. DCN 3.5.1-specific source files include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Register abstraction macros expand a register/field pair into address, base-index, mask, and shift constants.
3. Callers encode values by masking and shifting field values into a 32-bit register value, often through `REG_SET`, `REG_UPDATE`, or lower-level `dm_read_reg`/`dm_write_reg` helpers.
4. Hardware samples the values through MMIO state, double-buffer handshakes, vertical update timing, HPD/DDC/AUX sideband logic, or link encoder control paths.

The instance suffixes are significant. `AFMT4`, `DME4`, `DIG4`, and `DP4` describe one link/encoder pipeline instance, so code that selects instance 4 must pair these masks with the matching `regAFMT4_*`, `regDME4_*`, `regDIG4_*`, and `regDP4_*` offsets. Using instance 4 masks with another instance's offset is usually layout-compatible for repeated blocks, but it breaks the generated symbol contract and risks subtle maintenance errors.

Several groups model explicit hardware sequencing:

- AFMT audio packet and 60958 updates require callers to program packed status/info fields and trigger update/ack bits at the right time.
- HDMI generic packet controls have send, continuous-send, line-reference, immediate-send, pending, line-number, and enable-double-buffer-pending fields. Callers must respect pending/taken/status fields before rewriting packet state.
- DP secondary packet controls similarly expose enable bits, line scheduling, send/pending/deadline-missed status, active/idle-send selection, and double-buffer disable fields.
- DME metadata and HDMI DB controls expose double-buffer pending/taken/clear/disable state; writes are meaningful only in relation to hardware's current update window.
- DCIO soft-reset and GPIO enable/mask fields directly gate physical or sideband blocks and should be ordered with link shutdown/startup paths rather than arbitrary display-state updates.

## State and persistence behavior

The macros do not store state. They describe persistent hardware state held in DCN 3.5.1 display registers after driver writes them.

The most externally visible state in this chunk includes:

- Audio state: channel status, audio infoframe fields, channel enable/layout selection, sample-send control, FIFO overflow status/ack, CRC test state, and AFMT memory power state.
- Metadata/packet state: DME and HDMI/DP double-buffer pending/taken flags, generic packet line scheduling, immediate-send pending bits, DP secondary data packet enables, and missed/deadline status bits.
- Link state: DP training pattern, scrambler, PRBS, CRC, M/N, MSA timing, MST slot allocation table, MSO stream enables, DSC mode, ALPM controls, and TMDS control/DC-balance settings.
- Physical routing state: DIG source selection, HPD selection, UNIPHY lane inversion/crossbar mapping, DCIO resets, DSYNC/UNIPHY reset bits, and AUX/DDC/HPD GPIO ownership and pad tuning.
- Panel/backlight related state: PWRSEQ0/1 backlight and variable-backlight OTG-vsync routing, plus BL PWM frame-start display selection.

Register contents are normally reset by GPU/display IP reset, runtime suspend/resume, ASIC reinitialization, modeset link reprogramming, or DMUB/DC resource rebuild. Some status fields, such as FIFO overflow, CRC done, DB taken, transmission missed, pending, and deadline-missed bits, are transient hardware observations. Some clear/ack fields are write-one style controls inferred from their names (`*_ACK`, `*_CLR`, `*_TAKEN_CLR`) and should not be treated as persistent configuration bits.

## Dependencies and integration points

- The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the matching `reg...` address macros. Spot checks show matching offsets such as `regAFMT4_AFMT_AUDIO_PACKET_CONTROL2`, `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`, `regDME4_DME_CONTROL`, `regDIG4_HDMI_CONTROL`, `regDP4_DP_SEC_CNTL`, `regDP4_DP_SEC_CNTL1` through `regDP4_DP_SEC_CNTL7`, `regDCIO_SOFT_RESET`, and `regDC_GPIO_DDC1_MASK`.
- DCN 3.5.1 users include `display/dmub/src/dmub_dcn351.c`, `display/dc/irq/dcn351/irq_service_dcn351.c`, and `display/dc/resource/dcn351/dcn351_resource.c`, which include the offset and shift/mask headers for register initialization and field extraction.
- The register helper API in the AMD display tree depends on exact generated names. Macros such as `FD(reg_field)`, `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `FN(reg, field)`, and resource/IRQ/DMUB tables all expect `REG__FIELD_MASK` and `REG__FIELD__SHIFT` spelling.
- HDMI, DP, AFMT, and DME fields integrate with the DC link encoder and stream encoder layers that program audio, infoframes, DSC/PPS packets, HDR/vendor metadata, MST stream allocation, link training, and sink timing.
- GPIO/DDC/AUX/HPD fields integrate with connector detection, AUX channel transactions, DDC I2C fallback, hotplug handling, panel power sequencing, and board-level pin routing.
- UNIPHY and DCIO soft reset fields sit below higher-level link-encoder resource selection; incorrect use can affect all connectors sharing that physical block, not just one stream.

## Risks and edge cases

- Generated-header drift: because these are generated constants, a single mask or shift typo will compile cleanly but corrupt hardware programming at runtime. Repeated instance blocks (`DP4`, `DIG4`, `AFMT4`) are especially vulnerable to copy/generation errors.
- Register/mask mismatch: instance 4 masks must be used with instance 4 offsets. Most repeated block layouts are likely identical, but relying on that manually can hide address-selection bugs.
- Packed-field overflow: many fields are narrow, for example 1-bit enables, 2-bit source selectors, 3-bit requestor/source IDs, 4-bit channel/status selectors, 6-bit DP SEC version or MST slot counts, 16-bit line/timing fields, 20-bit HDMI ACR CTS/N fields, and 24-bit audio M/N or CRC values. Callers must clamp or validate values before shifting.
- Reserved-bit writes: direct full-register writes can disturb undocumented bits. Read-modify-write or generated field update helpers are safer when the register contains status, reserved, or write-one-clear bits.
- Double-buffer sequencing: DME, HDMI, and DP packet controls expose pending/taken/clear/disable fields. Writing packet contents or enables without observing pending/taken state can produce stale metadata, missed packets, or packet updates on the wrong frame.
- Status/clear semantics: fields named `*_ACK`, `*_CLR`, `*_TAKEN_CLR`, `*_MISSED_CLR`, or `*_OVERFLOW_ACK` likely have write-one-to-clear behavior. Treating them as normal persistent bits can accidentally clear diagnostics or retrigger handshakes.
- Link-training sensitivity: DP DPHY training, scrambler, 8b10b, HBR2 pattern, PRBS, and symbol fields are timing-sensitive and can break link bring-up only on specific cables, retimers, docks, or sink revisions.
- Physical signal risk: GPIO, AUX, DDC, HPD, pad strength, slew, bias, resistor, and comparator selection fields affect electrical behavior. Incorrect values can cause intermittent hotplug, AUX/DDC failures, or board-specific regressions that are hard to reproduce in emulation.
- Power-management interactions: AFMT/DME memory power controls, ALPM/AUX-less ALPM controls, DCIO soft reset, and pad wake fields interact with suspend/resume and idle power. Bad sequencing can cause resume failures or excess power draw.

## Test signals

- Build coverage: compile AMDGPU/DC paths that include DCN 3.5.1 headers. Missing or misspelled generated symbols should fail at compile time when consumed by resource, IRQ, DMUB, link, audio, or GPIO code.
- Header consistency checks: compare `AFMT4`, `DME4`, `DIG4`, and `DP4` shift/mask values against neighboring instances in the same generated header and against the DCN 3.5.0/3.5.x headers where layouts are expected to match.
- Offset reconciliation: verify every field group used by code has a matching `reg...` and `reg..._BASE_IDX` in `dcn_3_5_1_offset.h`, especially packet-control, DP secondary-data, GPIO, and DCIO reset registers.
- Runtime register smoke tests on DCN 3.5.1 hardware: exercise modeset, hotplug, suspend/resume, and link retraining while tracing reads/writes for `DIG4`, `DP4`, `AFMT4`, `DME4`, DCIO, and GPIO registers.
- HDMI tests: validate audio playback, channel layout, IEC 60958 channel status, AVI/audio/infoframe updates, generic packet scheduling, ACR N/CTS behavior, AVMUTE, and TMDS output with HDMI sinks.
- DisplayPort tests: validate link training across rates/lanes, MST slot allocation, DSC/PPS secondary packets, audio M/N programming, MSA timing, ALPM entry/exit, CRC paths, and secondary packet send/deadline status.
- Connector-sideband tests: run HPD plug/unplug, AUX transactions, DDC EDID reads, DDCVGA paths if supported, and panel power sequencing across cold boot and resume.
- Negative diagnostics: intentionally monitor FIFO overflow, CRC done, DB pending/taken, metadata transmission missed, DP SEC deadline missed, and collision/audio-mute status to confirm ack/clear fields behave as expected.
