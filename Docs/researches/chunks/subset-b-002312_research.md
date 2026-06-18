# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 57196-59640

## Scope And Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.0 shift/mask header. It contains C preprocessor constants for hardware register bitfield packing and extraction, not executable code. The range belongs to the `DPCSSYS_CR2` register namespace and describes the always-on lane (`RAWAONLANE`) digital register fields for CR2 plus the start of the CR2 supervisor/common (`SUPX`) digital PLL and reference-clock fields.

The chunk starts in the tail of `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_LOS_MASK_CTL`, completes the remainder of lane 0's always-on RX/signal-detect block, repeats a full always-on register layout for lanes 1, 2, 3, and the lane-template-like `LANEX` namespace, then enters the common `DPCSSYS_CR2_SUPX_DIG_*` definitions. It provides 2,073 `#define` lines under 372 register-comment headings. The naming pattern is the generated public contract: each bitfield has a `__SHIFT` macro giving the low bit and a matching `_MASK` macro giving the encoded field mask.

## Register Groups Covered

- `DPCSSYS_CR2_RAWAONLANE0_DIG_*` tail: the range begins after the first two `RX_LOS_MASK_CTL` shift macros, so only the `RX_LOS_MASK_CNT_MASK` and reserved mask for that register are present in this chunk. It then covers lane 0 signal-detect filtering, statistics, RX PMA override outputs, RX signal-detect calibration/code fields, VREF generator enable, current/VREF calibration codes, RX DCC calibration code captures, TX DCC bank access, MPLL bandgap state delay control, signal-detect output override/input observation, firmware configuration words, lane transceiver-mode override/input, RX signal-detect filter counters, and TX DCC configuration.
- `DPCSSYS_CR2_RAWAONLANE1_DIG_*`, `RAWAONLANE2`, and `RAWAONLANE3`: each lane has a full repeated always-on set beginning with analog/RX adaptation telemetry and offsets, then DFE and slicer values, MPLLA/MPLLB coarse tuning, power-up-done status, adaptation outputs for ATT/VGA/CTLE/DFE taps, fast flag status banks, common calibration status, TX/RX disable overrides, loss-of-signal and signal-detect controls, RX PMA override outputs, signal-detect calibration, DCC calibration, firmware configuration, lane transceiver-mode fields, and TX DCC configuration.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*`: mirrors the same lane-local always-on layout using an `X` lane namespace. This usually acts as a generated generic or broadcast/template form alongside explicit lane numbers; consumers still need the matching address definitions to know whether this maps to an actual indirect lane selector, broadcast alias, or generated documentation alias.
- `DPCSSYS_CR2_SUPX_DIG_*` start: covers supervisor ID code low/high words, reference clock override fields, MPLLA/MPLLB divided clock and HDMI clock override fields, MPLLA main override words, MPLLA multiplier, MPLLA spread-spectrum enable/update controls, and the first MPLLA SSC peak word. The next chunk continues the SUPX PLL, ASIC-input, and analog supervisor register family.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The interface is the macro namespace consumed by AMDGPU register programming code:

- `DPCSSYS_CR2_RAWAONLANE<n>_DIG_<REG>__<FIELD>__SHIFT` gives the field's starting bit.
- `DPCSSYS_CR2_RAWAONLANE<n>_DIG_<REG>__<FIELD>_MASK` gives the mask for that field.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*` repeats the same shape for the generated lane-X alias/template.
- `DPCSSYS_CR2_SUPX_DIG_*` covers common CR2 supervisor fields shared by lanes, especially reference clock and MPLL control.
- `RESERVED_*` fields preserve the hardware register layout and must normally be left unchanged by read-modify-write code.

The header is intended to be used with the matching DPCS 4.2.0 register address header and AMDGPU display register access helpers. In typical usage, higher-level display/PHY code prepares a value by masking and shifting field values, writes it through an MMIO or indirect DPCS access path, or reads a register and decodes status with the corresponding mask and shift.

## Control Flow

This header has no runtime control flow. The implied hardware sequencing is visible in the field families:

- Override fields pair `*_OVRD_VAL` data with `*_OVRD_EN` enable bits. For RX PMA square wave/signal detect, VREF, termination, lane transceiver mode, TX/RX disable, and SUPX clock/PLL controls, the value field alone is not enough; software must intentionally assert the enable bit to take control away from normal hardware/ASIC signals.
- Status and observation fields such as `RX_VREFGEN_MASTER`, `RX_PMA_SQ_OUT`, `PH2_PWRUP_DONE`, `ADAPT_DONE`, `FAST_FLAGS`, `LANE_CMNCAL_*_STATUS`, and `SIGDET_OUT_IN` are intended for polling or diagnostics after hardware training, power sequencing, or calibration has been triggered elsewhere.
- Calibration code fields expose hardware-produced or firmware-provided values for signal detect, VREF/current generation, RX DCC I/Q common-mode and data-filter codes, and MPLL coarse tune. These are data surfaces for training/bring-up code, not algorithms themselves.
- The SUPX fields establish common reference-clock and PLL behavior before per-lane transmit/receive operation depends on those clocks. The chunk includes override controls for reference clock enable/source/range, bandgap, HDMI mode, divided clocks, HDMI clock dividers, MPLLA enable/divider/multiplier/fractional-N/spread-spectrum fields, and the first spread-spectrum peak register.

Because the range is generated and repetitive, lane identity is part of the control contract. A lane 2 mask may have the same numeric value as a lane 3 mask, but code should still use the macro matching the register address being accessed so static review and generated-address coupling remain correct.

## State And Persistence Behavior

The file itself persists no runtime state. It contributes compile-time constants. State affected by consumers is hardware register state in the CR2 display PHY/DPCS block:

- Lane-local RX adaptation and calibration state includes ATT/VGA/CTLE/DFE tap values, DFE even/odd data/error/bypass offsets, IQ phase adjustment, slicer controls, common calibration status, RX signal-detect thresholds/codes, LOS mask counters, and DCC calibration code fields.
- Lane control state includes TX/RX disable override bits, RX PMA square-wave/signal-detect/VREF/termination override fields, lane transceiver mode override, and TX DCC bank/configuration controls.
- Firmware-facing state appears in `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`, which expose 16-bit configuration or split adaptation/calibration fields for microcode or firmware-mediated PHY procedures.
- SUPX common state includes reference clock selection and range, bandgap enable, HDMI mode, MPLLA/MPLLB divided and HDMI clock overrides, MPLLA enable/standby/divider/multiplier/fractional-N/spread-spectrum controls, and SSC peak data.

Persistence is governed by hardware, not this header. Programmed register values can survive across portions of a mode-set, link training attempt, hotplug handling path, or suspend/resume sequence until overwritten, reset, or power-gated. Status fields may be transient or latched depending on the hardware register definition outside this header.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DPCS 4.2.0 register set:

- Matching register address definitions are required; this `_sh_mask` header only describes bit positions and masks.
- AMDGPU display code supplies the register read/write helpers, field packing helpers, locking, sequencing, polling, and timeout behavior.
- Link training and PHY bring-up code integrates with the lane always-on registers for RX adaptation results, DFE/CTLE/VGA state, signal detect, LOS masking, DCC calibration, lane mode selection, and TX/RX disable control.
- Power management and reset paths depend on the `INIT_PWRUP_DONE`, common calibration status, MPLL disable/state-delay, and SUPX reference-clock/PLL fields.
- Firmware or diagnostics paths may use the `FW_*` config registers, `FAST_FLAGS`, DCC bank address/data/control registers, signal-detect override/input registers, and ID code registers.
- The file is generated from ASIC register specifications. Manual edits risk diverging from the DPCS 4.2.0 hardware layout and should be validated against the generator/spec source.

Although this repository path starts with `sources/distributed-fs/ceph-client`, the file itself is an imported Linux AMDGPU display header. It has no direct Ceph filesystem integration.

## Risks And Edge Cases

- The chunk starts mid-register and ends mid-SUPX family. `RAWAONLANE0_DIG_RX_LOS_MASK_CTL` is incomplete at the beginning, and `DPCSSYS_CR2_SUPX_DIG_MPLLA_SSC_PEAK_1` is followed by more SUPX PLL fields in the next chunk. Merge-stage documentation should reconcile those boundaries.
- Reserved masks are emitted as named constants. Driver code should preserve reserved bits unless the hardware specification requires a particular write value.
- Override fields are easy to misuse. Leaving `*_OVRD_EN` asserted after debug or validation can pin RX termination, signal detect, TX/RX disable, PLL clocking, or lane mode away from normal hardware control.
- The repeated lane layout invites copy/paste mistakes. Numeric masks are often identical across `RAWAONLANE1`, `2`, `3`, and `X`, but the macro prefix must match the addressed register.
- Many fields are narrow but safety-critical. Unmasked values can spill into adjacent fields if callers shift raw values without applying `_MASK`; this is especially risky for thresholds, filter counters, DCC calibration codes, MPLL multipliers/dividers, fractional-N controls, and SSC fields.
- Status fields can be stale or timing-dependent. Polling `ADAPT_DONE`, calibration status, `PH2_PWRUP_DONE`, signal-detect inputs, or fast flags needs timeouts and reset/clear sequencing outside this header.
- The `LANEX` namespace requires caution. Without the matching address-map context, it should not be assumed to be interchangeable with a numbered lane address.

## Test Signals

Useful validation for this chunk is mostly compile-time, generated-header, and hardware-oriented:

- Build AMDGPU display translation units that include `dpcs_4_2_0_sh_mask.h` to catch macro spelling, duplicate definition, and include-guard issues.
- Generator consistency checks should verify every non-reserved field has matching `__SHIFT` and `_MASK` definitions, masks are contiguous where expected, and mask positions agree with shift/width metadata.
- Cross-lane checks should compare `RAWAONLANE1`, `RAWAONLANE2`, `RAWAONLANE3`, and `RAWAONLANEX` for expected repeated layouts while allowing lane-number namespace differences.
- Static checks around field packing should confirm caller values are masked before shifting and read-modify-write paths preserve reserved bits.
- Hardware regression coverage should include CR2 display link bring-up, hotplug, DisplayPort/HDMI training, high-bandwidth modes, suspend/resume, lane reset/retrain paths, and PLL/reference-clock transitions.
- Diagnostic validation should exercise RX signal-detect filtering and overrides, LOS mask timing, DCC bank access, RX DCC calibration code reads, adaptation/fast-flag observation, firmware config fields, and SUPX MPLLA/MPLLB override behavior.
- Runtime warning signals include blank displays after mode-set, link training failures, unstable high-rate links, repeated PHY retraining, stuck adaptation/calibration polling, incorrect signal-detect/LOS reporting, and HDMI/DP clocking problems after changes to these generated masks.
