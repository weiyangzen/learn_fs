# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 44588-47203

## Purpose

This chunk is part of AMDGPU's generated DCE 12.0 register field mask header. It contains no executable C logic; it publishes compile-time bit layout constants for display-controller registers used by the Vega/DCE 12 display stack.

The range is centered on the final digital/DP instance and the first two DCIO ComboPHY instances:

- Tail of `DIG6` TMDS and digital-output fields, including TMDS feedback, stereo sync, sync-character patterns, TMDS control bits, DC balancer control, control-bit generator settings, lane enable, and AFMT audio-clock control.
- `DP6` DisplayPort stream/link fields, including link status, pixel format, MSA colorimetry and misc fields, video timing `M/N`, DPHY training/test/CRC/scrambler controls, secondary-data packet controls, audio `M/N` values, multi-stream transport allocation tables, and MSE status.
- `DCIO_UNIPHY0` and `DCIO_UNIPHY1` reserved macro-control ranges, represented as many full-width `RESERVED<n>` registers.
- `DC_COMBOPHYCMREGS0` and `DC_COMBOPHYCMREGS1` common PHY fields for fuses, lane power management, transmit common controls, lane resets, Z-calibration, and reserved-for-future-use registers.
- `DC_COMBOPHYTXREGS0` and `DC_COMBOPHYTXREGS1` per-lane transmit controls for lanes 0-3, including lane enable/ready, margin/de-emphasis, link-speed and PCS clock settings, boost, gang mode, and per-lane RFU registers.
- `DC_COMBOPHYPLLREGS0` plus the first part of `DC_COMBOPHYPLLREGS1`, covering frequency-control words, fractional/spread-spectrum controls, bandwidth tuning, calibration, loop controls, voltage-regulator configuration, observation, and DFT data for instance 0, then the same sequence through part of `VREG_CFG` for instance 1.

Each field is represented by paired macros. `REGISTER__FIELD__SHIFT` gives the low bit position, and `REGISTER__FIELD_MASK` gives the already-positioned mask. Driver code combines these masks with matching register-address macros from `dce_12_0_offset.h` and the display register helper macros that consume `FD(reg__field)` style names.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The macro namespace is the entire API surface.

The `DIG6_*` definitions describe the sixth digital stream encoder's TMDS/HDMI-oriented controls. Important groups include `DIG6_TMDS_CONTROL0_FEEDBACK`, `DIG6_TMDS_STEREOSYNC_CTL_SEL`, `DIG6_TMDS_SYNC_CHAR_PATTERN_0_1`, `DIG6_TMDS_SYNC_CHAR_PATTERN_2_3`, `DIG6_TMDS_CTL_BITS`, `DIG6_TMDS_DCBALANCER_CONTROL`, `DIG6_TMDS_CTL0_1_GEN_CNTL`, `DIG6_TMDS_CTL2_3_GEN_CNTL`, `DIG6_DIG_VERSION`, `DIG6_DIG_LANE_ENABLE`, and `DIG6_AFMT_CNTL`.

The `DP6_*` definitions describe a DisplayPort stream/link block for instance 6. Major register families are:

- Link and stream enable/status: `DP6_DP_LINK_CNTL`, `DP6_DP_CONFIG`, `DP6_DP_VID_STREAM_CNTL`, and `DP6_DP_STEER_FIFO`.
- Pixel and MSA programming: `DP6_DP_PIXEL_FORMAT`, `DP6_DP_MSA_COLORIMETRY`, `DP6_DP_MSA_MISC`, `DP6_DP_VID_TIMING`, `DP6_DP_VID_N`, `DP6_DP_VID_M`, `DP6_DP_LINK_FRAMING_CNTL`, and `DP6_DP_VID_MSA_VBID`.
- DPHY training and diagnostics: `DP6_DP_DPHY_CNTL`, `DP6_DP_DPHY_TRAINING_PATTERN_SEL`, `DP6_DP_DPHY_SYM0` through `SYM2`, `DP6_DP_DPHY_8B10B_CNTL`, `DP6_DP_DPHY_PRBS_CNTL`, `DP6_DP_DPHY_SCRAM_CNTL`, CRC enable/control/result/status registers, fast-training control/status, bit/serializer swap control, and HBR2 pattern control.
- Secondary-data, audio, and MST/MSE programming: `DP6_DP_SEC_CNTL`, `DP6_DP_SEC_CNTL1`, `DP6_DP_SEC_FRAMING1` through `FRAMING4`, audio `N` and `M` programming/readback, timestamp, packet control, `DP6_DP_MSE_RATE_CNTL`, SAT0/SAT1/SAT2 allocation fields, SAT update, link timing, misc control, and SAT status registers.

The `DCIO_UNIPHY0_*` and `DCIO_UNIPHY1_*` macro groups are intentionally repetitive: each `UNIPHY_MACRO_CNTL_RESERVED<n>` exposes a full-width `reserved<n>` field. These registers are part of the generated DCIO address space and may be used by firmware, diagnostics, or later hardware-specific code even when normal driver paths do not name individual fields.

The ComboPHY common register groups are mirrored for instances 0 and 1. `COMMON_FUSE1` through `COMMON_FUSE3` expose HDMI/LVDS/DP fuse and calibration fields such as impedance, pre-emphasis, margin, de-emphasis, spread-spectrum, FFE, and control-swing data. `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_LANE_RESETS`, and `COMMON_ZCALCODE_CTRL` expose PHY power sequencing, transmit mode, transmitter enable, per-lane reset, and impedance-calibration controls.

The ComboPHY TX register groups are also mirrored across instances and lanes. For each lane, `CMD_BUS_TX_CONTROL_LANE<n>` exposes `tx_en`, `tx_pg_en`, and `tx_rdy`; `MARGIN_DEEMPH_LANE<n>` exposes margin, de-emphasis, and margin-enable fields; `CMD_BUS_GLOBAL_FOR_TX_LANE<n>` exposes two-symbol mode, link speed, gang mode, max link rate, PCS frequency/clocking, PLL always-on, read-clock division, TX boost, and RON-code offset. The `TX_DISP_RFU0_LANE<n>` through `TX_DISP_RFU12_LANE<n>` registers are full-width RFU fields.

The ComboPHY PLL register groups define low-level PLL programming. `FREQ_CTRL0` and `FREQ_CTRL1` carry fractional and integer frequency-control words. `FREQ_CTRL2` carries denominator and slew fraction. `FREQ_CTRL3` exposes reference-clock division, VCO pre-division, fractional-N enable, SSC enable, FCW select, frequency jump, TDC resolution, and DPLL config bits. `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, and `VREG_CFG` expose bandwidth, calibration, loop, PRBS, phase, regulator, and analog tuning controls. Instance 0 continues through observe and DFT output fields inside this chunk; instance 1 is cut off inside `VREG_CFG`.

## Control Flow

This header range has no runtime control flow. It is preprocessor data. Runtime behavior appears only in consumers that pair these field constants with register addresses and register helper macros.

A typical display-driver flow is:

1. Select the DCE 12 register address from `dce_12_0_offset.h`, often through resource tables in the DCE 12 display code.
2. Use a generated mask/shift field such as `FD(DP6_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE)` or a direct mask/shift pair.
3. Read a register through display-service helpers such as `dm_read_reg_soc15()` or a higher-level `generic_reg_update_soc15()` wrapper.
4. Extract, clear, or insert the field using the generated shift/mask constants.
5. Write the updated value back when the target field is writable and the display engine/PHY sequencing permits it.

Control-sensitive hardware actions represented by this chunk include enabling DP video streams, deferring stream disable, resetting and monitoring DP steer/TU FIFOs, changing DP pixel encoding/depth/range, programming DP `M/N` timing, selecting training/test patterns, enabling/disabling scrambling or CRC capture, sending secondary/audio packets, updating MST allocation tables, enabling digital lanes and AFMT audio clocks, resetting PHY lanes, powering lanes, changing PHY link-speed/PCS/PLL settings, and overriding analog TX margin/de-emphasis. The macros themselves do not enforce sequencing or valid value ranges.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in display hardware registers.

The state represented here spans several layers:

- Stream-encoder state: TMDS control symbol generation, digital lane enables, AFMT audio clock enable/status, DP video stream enable/status, pixel encoding, MSA metadata, and VBID fields.
- Link-training and diagnostic state: DPHY training pattern selection, PRBS controls, scrambler seed/reset, CRC enable/masks/results, fast-training status, FIFO overflow flags and ACK bits, and MSE SAT status.
- Secondary-data and audio state: DP secondary packet enable/update scheduling, framing bytes, audio `N/M` programming and readbacks, timestamp, packet-line selection, and MST stream-allocation controls.
- PHY state: UNIPHY reserved register payloads, ComboPHY fuses, lane power management, common TX mode, lane resets, per-lane ready/enabled state, margin/de-emphasis/boost, link-speed hints, PCS clocking, PLL frequency words, spread-spectrum/fractional-N selection, calibration, loop/PRBS settings, regulator controls, observe selections, and DFT output.

Persistence depends on each hardware register's semantics. Some fields are latched programming values, some are live status bits, some are sticky diagnostic/status bits that require explicit ACK or clear fields, some are fuse/strap-derived read-only values, and some are reserved or RFU payloads. Values can be changed by the display driver, firmware/BIOS, hardware self-clearing behavior, link training, mode set, hotplug handling, suspend/resume, power-gating, or ASIC reset. This generated header does not encode read-only, write-one-to-clear, self-clearing, or sequencing rules.

## Dependencies And Integration Points

This chunk depends on the generated DCE 12 register-header ecosystem. The companion address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h`; this file supplies the field layout inside those addresses.

Direct include points for `dce_12_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_factory_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The display code includes both `dce_12_0_offset.h` and this mask header, then uses macros such as `FD(reg__field)`, `generic_reg_update_soc15()`, and `generic_reg_set_soc15()` to write packed register fields. `dce120_resource.c` also builds DCE 12 resource tables from generated `mm...` addresses and field metadata; these tables feed stream encoders, link encoders, timing generators, IRQ services, GPIO/AUX/I2C, and hardware sequencing code.

Although this repository path is under a local `ceph-client` source tree, the content of this chunk is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift can compile successfully while updating the wrong bit, failing to update the intended field, or corrupting adjacent fields during read-modify-write register updates.

High-risk display fields in this chunk include `DP6_DP_VID_STREAM_ENABLE`, deferred stream disable/status bits, DP pixel encoding/depth/range fields, MSA override fields, DP video timing `M/N` generation controls, DPHY training/test/scrambler/CRC controls, secondary-data packet controls, MST allocation table fields, and AFMT audio clock bits. Bad constants in these areas can produce blank displays, wrong color format or dynamic range, missing audio/infoframes, MST allocation failures, broken compliance test patterns, or incorrect CRC diagnostics.

PHY fields are especially sensitive. Lane enable/ready, lane power-management, lane reset, link-speed, PCS clock, PLL frequency-control, fractional-N/SSC, calibration, regulator, margin, de-emphasis, boost, and RON-code fields affect analog signaling. Incorrect values can cause failed link training, intermittent display dropouts, eye-margin failures, compliance failures, excess power, or hangs during mode set and resume.

The repeated instance/lane layout creates copy-generation risk. `DC_COMBOPHYTXREGS0` and `DC_COMBOPHYTXREGS1` repeat the same lane 0-3 pattern, and each lane has many similarly named RFU registers. An instance suffix or lane suffix mismatch would be hard to detect at compile time and might only fail on one physical transmitter or one lane configuration.

Reserved and RFU fields require conservative handling. Many `DCIO_UNIPHY*_UNIPHY_MACRO_CNTL_RESERVED<n>` and `TX_DISP_RFU<n>_LANE<m>` fields are full-width masks. Normal driver code should avoid inventing semantics for these fields unless backed by ASIC documentation or known golden-register programming.

This chunk has artificial line-boundary splits. It starts after the first `DIG6_TMDS_CONTROL0_FEEDBACK__TMDS_CONTROL0_FEEDBACK_SELECT__SHIFT` line and ends before the remaining masks for `DC_COMBOPHYPLLREGS1_VREG_CFG`. The final per-file merge should treat those as chunk boundaries, not source omissions.

## Test Signals

Useful validation is mostly compile-time plus display and hardware behavior:

- Kernel/driver builds for DCE 12/Vega display paths should compile all generated field names referenced by DCE 12 timing, IRQ, GPIO, resource, and hardware-sequencing code.
- Generated-register validation should compare every `*_MASK`/`*__SHIFT` pair in this range against AMD's register database and the adjacent address definitions in `dce_12_0_offset.h`.
- Display mode-set tests should exercise DP6 and DIG6 paths across HDMI/TMDS and DisplayPort outputs where hardware exposes those instances.
- DP link training, fast-training, HBR2 pattern, PRBS, scrambling, and CRC diagnostics should show expected bit transitions and stable link status.
- MST tests should verify MSE SAT programming, rate updates, link timing, and SAT status for multi-stream displays.
- Audio/infoframe tests should confirm AFMT clock enable/status, secondary packet scheduling, audio `N/M` programming, and packet framing are correct.
- Suspend/resume, hotplug, HPD IRQ, runtime power-management, and full modeset stress tests should not leave PHY lanes powered incorrectly, stuck in reset, or trained with bad margin/de-emphasis/PLL settings.
- Lab PHY/compliance tests should validate lane margin, de-emphasis, boost, SSC/fractional-N, PLL lock, and DFT/observe paths for both ComboPHY instances and all four lanes.

Regression symptoms from bad constants include blank or flickering display, wrong colors or quantization, DP link stuck at a lower rate, MST stream loss, missing HDMI/DP audio, repeated hotplug or link-training failures, CRC/test-pattern mismatches, PHY compliance failures, resume failures, or diagnostics showing activity on the wrong lane or PHY instance.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_sh_mask.h` define the preceding DCE 12 display register field families and the start of the `DIG6` TMDS block. Later chunks complete `DC_COMBOPHYPLLREGS1_VREG_CFG` and continue through subsequent DCE 12 register-mask families. The final per-file report should describe this source as one generated display hardware layout contract rather than as independent algorithmic code.
