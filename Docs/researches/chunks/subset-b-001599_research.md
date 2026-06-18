# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 44706-47394

Chunk: `subset-b-001599`
Covered source range: lines 44706-47394 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h`

## Purpose

This chunk is part of the generated AMD DCN 1.0 register shift/mask header. It contains no executable driver code; it exports C preprocessor constants that describe bit positions and positioned masks for display PHY, legacy VGA, and Azalia/HD-audio indexed registers.

The range begins at the tail of the `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3` block, then covers complete mask groups for COMBOPHY PLL instance 2, UNIPHY3 reserved registers, COMBOPHY common/TX/PLL instance 3, ZCAL, legacy VGA sequencer/CRT/graphics/attribute indexed registers, Azalia F2 output codec and pin blocks, audio descriptors, sink-info fields, Azalia CRC result blocks, and the beginning of the Azalia F2 input endpoint block. It ends after the `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR__HBR_ENABLE__SHIFT` macro, before the matching HBR masks and later input-pin fields.

Every field follows the generated naming contract:

- `REGISTER__FIELD__SHIFT` is the field's least-significant bit position.
- `REGISTER__FIELD_MASK` is the already-positioned mask for that field.

The companion `dcn_1_0_offset.h` header provides the matching `mm*` and `ix*` register offsets. This file provides the per-register field layout used by AMDGPU Display Core register helpers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this slice. The exported API is the macro namespace itself. This chunk contains 2,063 `#define` directives, 19 address-block comments, and 499 register comments in the requested range.

Major macro families:

- `DC_COMBOPHYTXREGS2_*`: the chunk starts in the final instance-2 lane-3 TX tuning/control area. `CMD_BUS_GLOBAL_FOR_TX_LANE3` defines link-speed, lane-gang, PCS clock, PLL always-on, boost, and RON offset fields. `TX_DISP_RFU0_LANE3` through `TX_DISP_RFU12_LANE3` expose full-width reserved-for-future-use payloads.
- `DC_COMBOPHYPLLREGS2_*`: PLL instance 2 frequency-control, bandwidth, calibration, loop, regulator, observation, DFT, and wrapper-control fields. These include fractional/integer frequency words, denominator/slew values, refclk/VCO/divider and spread-spectrum controls, loop bandwidth parameters, calibration disables/ratios, feedback and clock selection controls, regulator configuration, lock-detection observation state, digital observation selectors, and full-width DFT data.
- `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0..159`: a large reserved UNIPHY3 macro-control aperture. Each register exposes a single full-width `UNIPHY_MACRO_CNTL_RESERVED` field with shift `0x0` and mask `0xFFFFFFFFL`.
- `DC_COMBOPHYCMREGS3_COMMON_*`: common instance-3 display PHY fields. Fuse registers expose validity and impedance/current/override state; `COMMON_MAR_DEEMPH_NOM` carries nominal margin/de-emphasis values; `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, and `COMMON_ZCALCODE_CTRL` cover lane power, common TX, TMDS/DP mode, resets, and impedance calibration code controls. `COMMON_DISP_RFU1..7` are full-width reserved display registers.
- `DC_COMBOPHYTXREGS3_*`: per-lane TX controls for lanes 0-3. Each lane has `CMD_BUS_TX_CONTROL_LANE<n>` for power/power-gate/ready bits, `MARGIN_DEEMPH_LANE<n>` for margin and de-emphasis selection, `CMD_BUS_GLOBAL_FOR_TX_LANE<n>` for link/PCS/boost/global lane settings, and `TX_DISP_RFU0..12_LANE<n>` reserved payloads.
- `DC_COMBOPHYPLLREGS3_*`: the instance-3 copy of the PLL frequency, bandwidth, calibration, loop, regulator, observation, DFT, and wrapper-control layout used for instance 2.
- `ZCAL_MACRO_CNTL_RESERVED0..4`, `COMP_EN_CTL`, `COMP_EN_DFX`, and `ZCAL_FUSES`: Z-calibration reserved registers plus comparator-enable and fuse-derived calibration fields. These drive or report impedance/reference calibration behavior shared by the display PHY.
- `SEQ00..SEQ04`, `CRT00..CRT22`, `GRA00..GRA08`, and `ATTR00..ATTR14`: legacy VGA indexed register fields for sequencer reset/clock/map/font/memory mode, CRT timing/cursor/display-start/sync/overflow/underline/mode-control fields, graphics controller set/reset/plane/rotate/mode/misc/compare/mask fields, and attribute controller palette/mode/overscan/plane/pel-pan/color-select fields.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, stream/channel ID, digital converter status/control, stripe, ramp rate, GTC embedding, audio widget capabilities, supported size/rates, and stream-format fields.
- `AZALIA_F2_CODEC_PIN_*`: output pin controls and parameters, including connection-list response, widget control, unsolicited response, pin sense, default configuration words, speaker/channel allocation, down-mix info, audio descriptor selection/data, multichannel enable groups and individual channels, lip-sync, HBR, sink-info selection, codec channel-status overrides, pin association, digital output status, LPIB snapshots, coding type, format-change reporting, wireless display identification, remote keepalive, pin widget capabilities, pin capabilities, and connection-list length.
- `AUDIO_DESCRIPTOR0..13`: audio descriptor slots with maximum-channel count, sample-rate mask, and PCM/compressed coding-type capability bits.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, `PORTID1`, and `SINK_DESCRIPTION0..17`: sink identity and description words for the Azalia endpoint sink-info block.
- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7`: full-width 32-bit CRC result fields for input and output/general Azalia diagnostic paths.
- `AZALIA_F2_CODEC_INPUT_CONVERTER_*` and `AZALIA_F2_CODEC_INPUT_PIN_*`: the beginning of the F2 input endpoint converter and input-pin field layout. This includes input converter format, stream/channel ID, digital converter state, input widget capabilities, supported sizes/rates, input pin widget control, unsolicited response, pin sense, default configuration, channel allocation, even-numbered multichannel enables 0/2/4/6, and the first two HBR shift fields. The HBR masks and subsequent odd-channel/input status fields are outside this chunk.

## Control Flow

This header slice has no runtime control flow. It is a linear sequence of `#define` directives inside the larger DCN 1.0 include guard.

Effective runtime flow appears in consumers that:

1. choose a register offset from `dcn_1_0_offset.h`, such as `mmDC_COMBOPHYPLLREGS3_FREQ_CTRL0`, `mmCOMP_EN_CTL`, `ixSEQ00`, `ixCRT00`, `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`, `ixAUDIO_DESCRIPTOR0`, or `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`;
2. access the corresponding MMIO register directly or through the correct indexed-register window for VGA/Azalia endpoint blocks;
3. extract fields with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert fields using the same pair;
4. write back only when the hardware register is writable and the caller is in the correct display, PHY, VGA, or HD-audio programming sequence.

The macros do not encode sequencing. External code must handle PLL programming order, calibration enable/polling, lane reset release, link training, display audio stream setup, unsolicited-response delivery, LPIB snapshot locking, CRC latch semantics, and legacy VGA indexed-register access rules.

## State And Persistence Behavior

The header has no mutable software state and persists only as compiled constants.

The fields describe hardware state in DCN 1.0 display PHY, ZCAL, VGA compatibility, and Azalia display-audio blocks. Important hardware state represented here includes:

- COMBOPHY PLL frequency, bandwidth, loop, calibration, regulator, lock-observation, and DFT/debug state for PHY instances 2 and 3;
- UNIPHY3 reserved macro-control state, retained in the generated map for register database completeness;
- COMBOPHY instance-3 fuse, impedance, lane power, common TX, TMDS/DP mode, reset, ZCAL code, lane TX power, margin, de-emphasis, PCS, boost, and reserved lane state;
- ZCAL comparator enable, DFX, and fuse-derived calibration values;
- legacy VGA sequencer, CRT controller, graphics controller, and attribute controller indexed state used by compatibility display paths;
- Azalia F2 output converter and pin state, including audio format, channel/stream IDs, digital converter status, pin sense, unsolicited-response state, sink capability data, channel allocation, multichannel/HBR controls, LPIB snapshots, coding type, format-change status, and remote keepalive;
- Azalia sink identity/description and audio descriptor payloads;
- full-width Azalia input/output CRC result snapshots;
- partial Azalia F2 input converter/input-pin state at the end of the slice.

Persistence depends on register class. Some fields are read-only capability/status values, some are writable controls, some are debug selector/readback values, and some are reserved or fuse-derived. Values may be reset or reinitialized by display modeset, link retraining, audio stream setup/teardown, hot-plug handling, runtime power management, suspend/resume, GPU reset, display core reset, firmware/BIOS initialization, or full device power loss.

## Dependencies And Integration Points

The direct generated companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Examples of matching offsets in that companion header include:

- `mmDCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0`
- `mmDC_COMBOPHYCMREGS3_COMMON_FUSE1`
- `mmDC_COMBOPHYTXREGS3_CMD_BUS_TX_CONTROL_LANE0`
- `mmDC_COMBOPHYPLLREGS3_FREQ_CTRL0`
- `mmCOMP_EN_CTL`
- `mmZCAL_FUSES`
- `ixSEQ00`
- `ixCRT00`
- `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`
- `ixAUDIO_DESCRIPTOR0`
- `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`

The local DCN 1.0 resource code includes both the offset and mask headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`. The broader integration point is AMDGPU Display Core for Vega/DCN 1.0 hardware, where generated register constants feed register-helper macros and hardware block constructors.

Functional integration areas include:

- display PHY and link encoder paths that program COMBOPHY PLLs, lane power, resets, TX margin/de-emphasis, boost, and PCS behavior for DisplayPort/HDMI/DVI signaling;
- ASIC initialization, power management, and resume paths that preserve or restore PHY, ZCAL, and reserved register state;
- debug and validation paths that use observation, DFT, lock, ZCAL, and CRC readback fields;
- legacy VGA compatibility paths that access indexed sequencer/CRT/graphics/attribute registers;
- display audio and HDA/Azalia paths that expose GPU HDMI/DP audio converter/pin capabilities, sink descriptions, audio descriptors, channel allocation, HBR support, hot-plug/pin-sense events, and stream-position snapshots.

Although the repository root is named `ceph-client`, this chunk is AMDGPU kernel display-driver register metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. Incorrect masks or shifts compile cleanly but can read the wrong bit, fail to update the intended field, or corrupt adjacent fields in packed hardware registers.

This range is highly repetitive. COMBOPHY instance 2 and 3 PLL layouts should remain structurally aligned where the hardware database says they match; TX lane 0-3 layouts must preserve lane numbers; Azalia multichannel fields repeat by channel; VGA indexed registers reuse short historical register names. A generated prefix, instance, channel, or lane mismatch can look plausible in review while targeting the wrong hardware path.

Reserved and RFU fields require caution. `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED*`, COMBOPHY `*_RFU*`, `ZCAL_MACRO_CNTL_RESERVED*`, and similar full-width masks exist for register-map completeness, not as permission for arbitrary writes. Writing undocumented/reserved apertures can affect board-specific or ASIC-internal behavior.

PHY and PLL fields are timing and board dependent. Bad frequency-control, loop-bandwidth, regulator, calibration, impedance, margin, de-emphasis, reset, or lane-power values can cause link-training failures, black screens, intermittent DisplayPort/HDMI instability, high error rates, or suspend/resume regressions without obvious software exceptions.

Legacy VGA fields are narrow indexed registers represented in a 32-bit macro namespace. Callers must respect VGA indexed-register addressing and historical side effects; treating these as ordinary flat 32-bit display registers can corrupt timing, cursor, blanking, graphics mode, or palette/attribute state.

Azalia output and input fields are externally visible through the audio stack. Wrong format, stream ID, channel allocation, HBR, descriptor, sink-info, pin-sense, or unsolicited-response masks can produce missing HDMI/DP audio devices, wrong channel layouts, bad sample-rate/coding advertisements, spurious hot-plug events, failed HBR audio, or unstable playback-position reporting.

CRC fields are full-width diagnostic readbacks. They should be treated as result snapshots, not bitfield controls, despite following the same generated mask/shift naming pattern.

The chunk boundaries are partial. The first line is a single tail mask for `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3`; the rest of that register is in the previous chunk. The final two macros start `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`; its masks and following input-pin fields are in the next chunk.

## Test Signals

Useful validation signals include:

- kernel build coverage for DCN 1.0/Vega display paths that include `dcn_1_0_sh_mask.h`;
- generated-header consistency checks that each `REGISTER__FIELD_MASK` has the matching `REGISTER__FIELD__SHIFT`, with this chunk's first and last boundary splits reconciled at file-merge time;
- diffs against the authoritative DCN 1.0 register database for COMBOPHY, UNIPHY3, ZCAL, VGA, and Azalia blocks;
- cross-checks that every mask macro is paired with the expected offset name in `dcn_1_0_offset.h`;
- instance and lane consistency checks comparing `DC_COMBOPHYPLLREGS2` with `DC_COMBOPHYPLLREGS3`, lane 0-3 TX layouts in `DC_COMBOPHYTXREGS3`, and repeated Azalia multichannel field shapes;
- hardware modeset and link-training tests across ports that exercise PHY instances 2 and 3, including DisplayPort and HDMI/DVI where available;
- PLL and ZCAL validation that verifies requested clocks, lock/observation fields, calibration behavior, impedance calibration, and stable link output after suspend/resume and runtime power transitions;
- legacy VGA smoke tests for early console, mode switching, cursor, blanking, palette/attribute behavior, and resume on DCN 1.0 hardware or emulation;
- HDMI/DisplayPort audio tests across stereo, multichannel, compressed formats, HBR, sample-rate changes, stream enable/disable cycles, and sink re-enumeration;
- hot-plug and pin-sense tests that verify unsolicited response tags/enables, presence-detect state, audio device creation/removal, and sink capability refresh;
- ELD/sink-capability checks that confirm `AUDIO_DESCRIPTOR*`, manufacturer/product IDs, port IDs, sink descriptions, speaker allocation, and channel allocation decode as expected;
- LPIB snapshot and playback-position tests under wraparound and stream restarts;
- CRC diagnostic tests that read `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channels under known audio/display traffic.

Regression symptoms from bad constants include missing or unstable display links, link-training failures isolated to a PHY instance or lane, black screens after resume, wrong VGA compatibility output, missing HDMI/DP audio, incorrect advertised audio capabilities, wrong channel mapping, HBR failures, spurious or missing hot-plug events, incorrect LPIB/timer snapshots, and CRC diagnostics changing on the wrong channel.

## Cross-Chunk Notes

This is a middle slice of a much larger generated header. The final per-file research document should merge this with adjacent chunks before making whole-file claims. Specifically:

- `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3` starts before line 44706.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR` continues after line 47394.
- Later chunks are needed for the rest of the F2 input endpoint input-pin fields and the file guard tail.
