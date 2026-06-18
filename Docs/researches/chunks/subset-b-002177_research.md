# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 64578-66981

## Purpose

This chunk is a generated AMD DCN 4.1.0 register field shift/mask slice. It contains no executable C logic and defines no structs, enums, or functions. Its interface is a set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; display driver code combines them with matching register offsets and AMD Display Core register helpers to read, update, or write individual MMIO fields.

The requested range contains 2,165 `#define` entries: 1,093 shift macros, 1,080 mask macros, and several macro lines whose names are not ordinary shift/mask pairs. It also includes 225 register or address-block comments. The range starts at the mask half of `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, covers the rest of Azalia audio input endpoint 7 parameter/control fields, crosses several empty address-block markers for DSCC/DSC/DWB debug spaces, then defines a large `DPCSSYS_CR0` DisplayPort PHY/clock-system register block through the first six shift definitions of `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`. The end boundary is artificial: masks for that final register begin immediately after line 66981.

Although the source tree is a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a display or PHY register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field.

The main register families covered here are:

- `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `...SUPPORTED_SIZE_RATES`: HDMI/DP audio converter format capability and supported sample-rate/bit-depth fields for input endpoint 7.
- `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_*`: HDA/Azalia input pin widget capability and pin capability fields, including channel capability, amplifier flags, digital/power/LR-swap support, impedance and presence detection capability, HDMI/DP indication, VREF, EAPD, and pin type metadata.
- `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_*`: pin control, status, and response fields for unsolicited response tags/enables, input pin sense and presence detect, widget input enable, multichannel enable/mute/channel IDs for channels 0-7, HBR capability/enable, channel allocation, hot-plug audio enable/clock-gating status, forced unsolicited response payloads, default configuration descriptor fields, LPIB snapshot/timer values, input activity/channel-layout unsolicited-response enables, and audio infoframe channel count/allocation/validity.
- Address-block markers `dscc_dsccdebugind0`, `dscc_dscc_dispclk_debugind0`, `dsccif_dsccifdebugind`, `dsc_top_dsc_topdebugind`, `dwb_top_dwb_topdebugind`, and `dwbcp_dwbcpdebugind`: the requested lines only name these blocks; they do not define fields for them in this slice.
- `dpcssys_cr0_rdpcstxcrind`: begins the CR0 DisplayPort clock/PHY indirect block.
- `DPCSSYS_CR0_SUP_DIG_*`: supervisor digital registers for ID codes, reference clock and MPLL A/B div/HDMI clock overrides, MPLL A/B override input words, spread-spectrum peak and step-size programming, charge-pump and gain-stage override fields, supervisor/prescaler/level overrides, ASIC input readbacks, bandgap and charge-pump readbacks, PMA version ID, MPLL power-control status/timers/calibration/DAC readbacks, SSC spread type, clock/reset power-up timing, reference VPHUD, RTUNE configuration/status/set values/counters/calibration code, analog override outputs, analog status, bandgap override output, and MPLL PMIX override outputs.
- `DPCSSYS_CR0_SUP_ANA_*`: supervisor analog registers for prescaler, RTUNE, bandgap, switch power measurement, pre-regulator/vrefgen/probe controls, MPLL AB miscellaneous/override/ATB/vreg/outclk/lock/control/PMIX fields.
- `DPCSSYS_CR0_LANE0_DIG_ASIC_*`: lane 0 digital ASIC override and ASIC-facing input/output fields for lane, TX, and RX controls, including test-enable, reset, divider, data/clock enable, PLL clock selection, voltage swing/pre-emphasis, FFE, rate, TX power, termination, and RX detect/status style fields.
- `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state and power-up timing registers for P0/P0S/P1/P2, fast-wake and power-good timing, and DCC CR-bank/DAC control, range, select, acknowledge, and address fields.
- `DPCSSYS_CR0_LANE0_DIG_TX_CLK_ALIGN_TX_CTL_0` and `...TX_LBERT_CTL`: TX clock alignment and lane BERT/test controls.
- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: RX status/data-mask/pattern-match/sample-count/stat-counter controls for lane debug/stat collection, including match masks, sample-count done bits, stat counters 0-6, calibration comparator clock control, additional match controls, disable-sample-count, and stat-stop fields.
- `DPCSSYS_CR0_LANE0_DIG_ANA_*`: digital-to-analog TX override/status fields for TX analog clock/data/refgen/word clocks, MPLL clock enables, reset, serial enable, data rate, RX detect, override enables, termination code/source overrides, TX equalization control words, analog status readbacks, and the start of TX DCC DAC override output programming.

## Control Flow

This header slice has no local control flow. Runtime behavior comes from AMDGPU Display Core code that includes this generated header and companion offset headers:

1. DCN 4.1.0-specific display code includes `dcn/dcn_4_1_0_sh_mask.h` alongside `dcn/dcn_4_1_0_offset.h`.
2. Other DPCS-specific blocks use the separate `dpcs/dpcs_3_1_4_offset.h` and `dpcs/dpcs_3_1_4_sh_mask.h` headers for similar `DPCSSYS_CR0` names; this chunk embeds corresponding field masks in the DCN 4.1.0 mask header.
3. Register-list macros and helper tables token-paste register and field names into ASIC-specific `mask_sh` tables.
4. Hardware code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to shift/mask fields while programming audio endpoint state, DisplayPort PHY PLL/clock state, lane power, DCC/RTUNE calibration, equalization, and debug/status capture.

The macros do not encode sequencing rules. Consumers still need to follow hardware-defined order for audio endpoint programming, hot-plug response setup, MPLL power and lock sequencing, RTUNE/DCC calibration, lane power transitions, and analog override enable/disable.

## State And Persistence Behavior

This chunk stores no software state. It describes state that lives in DCN 4.1.0 display/audio/PHY hardware registers:

- Azalia endpoint 7 capability and control state, including supported audio formats/rates, pin capabilities, unsolicited response configuration, input pin sense, multichannel maps, HBR enablement, channel allocation, hot-plug/audio-enable state, default configuration values, LPIB snapshots, input status, and infoframe contents.
- DPCSSYS CR0 supervisor state for reference clocks, MPLL A/B overrides, spread-spectrum generation, charge-pump/gain settings, level and prescaler overrides, bandgap/vref generation, analog regulator/PMIX controls, PLL power/timer/calibration status, RTUNE set values and status, and ASIC input/readback state.
- Lane 0 TX/RX PHY state for ASIC override routing, TX power states and timers, DCC bank/DAC calibration, TX clock alignment, BERT/test enablement, RX pattern/stat counters, analog TX override controls, TX termination/equalization, RX-detect and calibration readbacks, and TX DCC DAC override control.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, link re-training, audio endpoint reprogramming, runtime power transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status/readback fields such as presence detect, clock-on state, input activity, MPLL power/lock status, RTUNE status, DCC acknowledge, RX sample-count done, stat counters, and analog status may be read-only, sticky, self-clearing, or only valid while the relevant clock/PHY/audio block is powered. This generated header does not distinguish read-only, write-one-to-clear, or side-effect fields.

## Dependencies And Integration Points

- The Azalia register names align with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies endpoint 7 indirect offsets such as `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`.
- The `DPCSSYS_CR0` register names correspond to the DPCS CR0 register map, with matching offsets visible in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` for examples such as `ixDPCSSYS_CR0_SUP_DIG_IDCODE_LO` and `ixDPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`.
- `dcn_4_1_0_sh_mask.h` is included by DCN 4.0.1/4.1-family display code such as `dmub/src/dmub_dcn401.c`, GPIO translation/factory code, the DCN401 clock manager, IRQ service, and resource construction.
- Azalia fields integrate with HDMI/DisplayPort audio paths that expose HDA codec widget/pin capabilities, program channel maps and infoframes, and respond to hot-plug or input activity events.
- DPCSSYS fields integrate with DisplayPort/HDMI link setup, PHY PLL programming, link training, lane power management, spread-spectrum clocking, calibration/RTUNE/DCC flows, analog bring-up, test/debug capture, and low-level status diagnostics.
- The generated masks are consumed indirectly through register helper tables. Many call sites do not reference every macro by name; they rely on ASIC-specific `mask_sh` structs and token-pasted `SF(...)`-style register-field macros.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly while selecting the wrong MMIO bits, corrupting neighboring fields, or silently leaving hardware unprogrammed.
- Generated-header and offset-header drift is the main integrity risk. Correct masks with stale offsets, or correct offsets with stale masks, can misprogram audio pins, PLLs, lane power, or analog override fields without obvious compile failures.
- Chunk boundaries are not semantic. The first line is only the mask for a `STREAM_FORMATS` group whose shift is in the previous line/chunk context, and the last line stops in the middle of `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`; its remaining shifts and all masks are in the following lines.
- Full-register writes are risky because many registers pack controls, enables, status/readback bits, reserved fields, override enables, high-bit validity flags, and done bits into the same 16- or 32-bit word. Read-modify-write helpers are expected unless hardware documentation calls for a full write.
- Audio endpoint fields affect user-visible HDMI/DP audio enumeration and playback. Wrong supported-rate, pin capability, HBR, channel allocation, infoframe-valid, or unsolicited-response masks can cause missing devices, incorrect channel layouts, hot-plug failures, or silent audio.
- Presence/hot-plug and unsolicited-response fields can be timing-sensitive. Forcing responses or enabling UR bits with the wrong tag/payload can create spurious HDA events or hide real plug/activity changes.
- PLL, clock, spread-spectrum, RTUNE, DCC, and analog override fields are hardware-sensitive. Incorrect values can cause link-training failure, unstable clocks, excessive jitter, broken HDMI/DP output, failed resume, or intermittent display blanking.
- Lane 0-only coverage can hide instance drift. Equivalent lane 1-3 or CR1/CR2/CR3 fields may live in adjacent chunks or companion DPCS headers; testing only lane 0 does not validate all physical lanes.
- Reserved fields appear throughout the DPCSSYS register groups. Accidentally writing non-reset values into reserved masks can produce undefined PHY behavior, especially around analog and calibration registers.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 display/audio behavior:

- Build AMDGPU display support with DCN 4.1.0 enabled. Missing, renamed, or malformed macros should fail in DCN401 DMUB, GPIO, clock-manager, IRQ, resource, or register-table code.
- Mechanically compare this slice against the authoritative DCN 4.1.0 register database and matching offset headers, allowing for the known artificial start and end boundaries.
- Check that complete register groups have matching `__SHIFT` and `_MASK` pairs and that partial groups are reconciled across adjacent chunks, especially `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`.
- Exercise HDMI/DP audio enumeration and playback through endpoint 7 style paths: supported sample rates/bit depths, multichannel channel IDs, channel allocation, HBR audio, infoframe validity, hot-plug audio enablement, and suspend/resume.
- Validate hot-plug and unsolicited-response behavior with rapid plug/unplug and activity changes, checking that HDA events are neither lost nor spuriously forced.
- Exercise DisplayPort/HDMI link bring-up, link retraining, low-power transitions, runtime PM, suspend/resume, and GPU reset while monitoring link stability, PLL lock, lane power state, and absence of display blanking.
- Run PHY/link diagnostics that read RTUNE, DCC, MPLL status, RX stat counters, sample-count done bits, analog status, and lane BERT/test fields where supported.
- Confirm reserved bits remain at hardware-expected values during register programming, especially in supervisor analog, PLL, lane analog override, termination, equalization, and DCC DAC controls.

## Cross-Chunk Notes

The previous chunk contains the `STREAM_FORMATS__SHIFT` definition immediately before this range and earlier Azalia input endpoint 7 converter control fields. The next chunk contains the remainder of `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT` plus following DPCSSYS lane 0 analog override groups. The final per-file research document should reconcile these adjacent chunks before making whole-file claims about complete Azalia endpoint 7 coverage or complete DPCSSYS CR0 lane/PHY coverage.
