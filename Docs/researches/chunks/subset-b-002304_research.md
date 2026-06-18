# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h - subset-b-002304

## Scope

This chunk covers lines 38157-40592 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h`. The range is a generated AMD DPCS 4.2.0 register field header segment containing 2,086 `#define` macros across 351 register comment blocks. It starts in the tail of the `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` mask block, covers the remainder of RAWAON lane 1's late RX/DCC/firmware-control fields, full repeated RAWAON lane 2, lane 3, and lane X field layouts, then enters the CR1 SUPX common digital/analog PLL control area through the `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3` shift definitions.

## Purpose

The file is not executable logic. Its purpose is to publish the bit layout contract for DPCS 4.2.0 hardware registers to the AMD display driver. Each hardware field is represented by a `__SHIFT` macro and a matching `_MASK` macro, allowing driver code and register helper macros to construct, update, and decode packed register values without hard-coded bit positions.

This specific chunk describes two related areas:

- Per-lane RAWAON receiver/transmitter analog control and calibration fields for `DPCSSYS_CR1_RAWAONLANE*`.
- Shared `DPCSSYS_CR1_SUPX_*` digital and analog control fields for reference clocks, MPLLA/MPLLB programming, spread-spectrum clocking, prescaler, bandgap, RTUNE, and PLL analog controls.

The matching register-address side of this contract lives in `dpcs_4_2_0_offset.h`. For example, the covered chunk's offset companion maps `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_ADPT_IQ` to `0x4202`, `ixDPCSSYS_CR1_RAWAONLANEX_DIG_TX_DCC_CONFIG` to `0x7051`, `ixDPCSSYS_CR1_SUPX_DIG_IDCODE_LO` to `0x8000`, and `ixDPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3` to `0x804e`.

## Important Macro Groups

### RAWAON Lane 1 Tail

The first lines complete the lane 1 `DIG_RX_OVRD_OUT_2` mask group, then cover late lane 1 controls:

- `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_3` defines signal-detect low-frequency/high-frequency filter override values and enables.
- `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, and `DIG_RX_SIGDET_LF_CODE` define signal-detect calibration thresholds, enable bit, and 6-bit calibration tune codes.
- `DIG_RX_VREFGEN_EN`, `DIG_CAL_IOFF_CODE`, `DIG_CAL_ICONST_CODE`, and `DIG_CAL_VREFGEN_CODE` expose RX reference generator and calibration-code fields.
- `DIG_RX_DCC_CAL_*_CODE_{0,1}` expose 10-bit DCC calibration code fields for ICM, IDF, QCM, and QDF paths.
- `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG` define TX DCC table access/control fields.
- `DIG_MPLL_BG_CTL`, `DIG_SIGDET_OUT_OVRD`, `DIG_SIGDET_OUT_IN`, `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_*`, and `DIG_RX_SIGDET_CONFIG` expose firmware, lane-mode, signal-detect, and MPLL-background control/status fields.

### RAWAON Lane 2, Lane 3, and Lane X

The chunk includes 82 register blocks each for `DPCSSYS_CR1_RAWAONLANE2_DIG_*`, `DPCSSYS_CR1_RAWAONLANE3_DIG_*`, and `DPCSSYS_CR1_RAWAONLANEX_DIG_*`. These are structurally repeated lane definitions. The covered fields include:

- Front-end offset and adaptation measurements: `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `RX_ADPT_DFE_TAP5`, and `RX_ADAPT_DONE`.
- DFE and slicer calibration fields: `DFE_*_VDAC_OFST`, `DFE_*_REF_LVL`, `RX_PHSADJ_LIN`, `RX_PHSADJ_MAP`, `RX_IQ_PHASE_ADJUST`, `RX_SLICER_CTRL_EVEN`, and `RX_SLICER_CTRL_ODD`.
- Power-up and MPLL status/control: `INIT_PWRUP_DONE`, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `LANE_CMNCAL_MPLL_STATUS`, `MPLL_DISABLE`, `LANE_CMNCAL_RCAL_STATUS`, and `MPLL_BG_CTL`.
- Fast calibration flags: `FAST_FLAGS` and `FAST_FLAGS_2` contain many one-bit skip/fast-mode controls for RX adaptation, TX DCC calibration, RX DCC, VPHUD, VREF, signal detect, and continuous calibration paths.
- Manual override and observation fields: `TXRX_OVRD_IN`, `RX_LOS_MASK_CTL`, `RX_SIGDET_FILT_CTRL`, `STATS`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_OVRD_OUT_3`, `SIGDET_OUT_OVRD`, and `SIGDET_OUT_IN`.
- Firmware-owned or firmware-visible controls: `ADPT_CTL_0` through `ADPT_CTL_7`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`.

Lane X uses the same field model but the offset header places it at the `0x7000` lane-X indirect window rather than the lane 2/3 direct windows (`0x4200` and `0x4300`). This makes lane-X macros a generic or indexed lane access surface, while lane 2 and lane 3 are explicit lane instances.

### SUPX Digital Common Block

The `DPCSSYS_CR1_SUPX_DIG_*` section begins at `IDCODE_LO`/`IDCODE_HI` and then defines 60 register blocks for common digital control. Important groups include:

- Reference clock overrides: `REFCLK_OVRD_IN` has override value/enable pairs for digital, auxiliary, MPLL, HDMI, prescaler, and RX/TX reference-clock gating.
- MPLLA/MPLLB clock overrides: `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN` define divider and enable override fields.
- MPLLA/MPLLB programming: `MPLLA_OVRD_IN_0` through `_5`, `MPLLB_OVRD_IN_0` through `_5`, SSC peak/stepsize registers, and CP/CP_GS override fields expose fractional PLL, spread-spectrum, PMIX, divider, clock-enable, output-enable, reset, calibration, feedback clock, gearshift, standby, and charge-pump parameters.
- SUP, prescaler, and level overrides: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN` define common power, bandgap, RTUNE, prescaler, and level override controls.
- ASIC input mirrors: `MPLLA_ASIC_IN_*`, `MPLLB_ASIC_IN_*`, `*_DIV_CLK_ASIC_IN`, `*_HDMI_CLK_ASIC_IN`, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, and `*_CP*_ASIC_IN` define the bit layout of values driven by ASIC-level logic into the SUPX/PLL block.

The SUPX fields are mainly low-level hardware programming hooks. Many have value/enable override pairs, so using the value bit without the corresponding enable bit is not sufficient to affect hardware behavior.

### SUPX Analog Block

The `DPCSSYS_CR1_SUPX_ANA_*` portion covers 15 analog register blocks in this chunk:

- `ANA_PRESCALER_CTRL` and `ANA_RTUNE_CTRL` expose prescaler, measurement, fast-start, RTUNE ATB, DAC, mode, and regulator feedback controls.
- `ANA_BG1`, `ANA_BG2`, `ANA_BG3`, and `ANA_SWITCH_PWR_MEAS` expose bandgap/reference selection, temperature/power measurement, analog test bus, and switch controls.
- `ANA_MPLLA_MISC1`, `ANA_MPLLA_MISC2`, and `ANA_MPLLA_OVRD` expose MPLLA analog override, calibration, reset, gearshift, boost, lock, feedback-clock, and enable controls.
- `ANA_MPLLA_ATB1` through `ANA_MPLLA_ATB3` expose analog-test-bus measurement selection fields.
- `ANA_MPLLA_CTR1`, `ANA_MPLLA_CTR2`, and the beginning of `ANA_MPLLA_CTR3` expose PLL charge-pump, VREF, register, SPO, and internal-capacitor control fields.

The requested line range ends after `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3__RESERVED_15_8__SHIFT`. The `_MASK` macros for `MPLLA_CTR3` are immediately outside this chunk at lines 40593-40596, so this chunk is boundary-split in the middle of a register block.

## APIs, Types, and Functions

There are no C functions, enums, structs, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field's packed bit mask.
- Reserved-field masks such as `RESERVED_15_8_MASK` document the occupied but not semantically programmable parts of a 16-bit indirect register field layout.

The AMD display code consumes these definitions indirectly through table initialization and register helper macros. `dcn31_resource.c` includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, then builds `link_enc_regs`, `le_shift`, and `le_mask`. In the same resource file, `dcn31_link_encoder_create()` passes those tables into `dcn31_link_encoder_construct()`. The DPCS-specific table shape is declared in `display/dc/dio/dcn31/dcn31_dio_link_encoder.h` through `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(mask_sh)`.

This exact chunk's RAWAON and SUPX macros are not referenced by name in the display code searched under `drivers/gpu/drm/amd/display`. They are still part of the generated hardware register surface and may be used by bring-up, debug, firmware-directed sequences, or future code that accesses indirect CR registers via `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA`.

## Control Flow

The header itself has no control flow. The effective runtime flow around these definitions is:

1. A DCN31 resource file includes the generated offset and shift/mask headers for the ASIC generation.
2. Resource initialization creates static register, shift, and mask tables for link encoders.
3. Link encoder construction stores those tables in the encoder object.
4. Link encoder operations use register helper macros and the table entries to read, modify, and write hardware registers.
5. For indirect DPCS CR registers, software selects a CR address through the RDPCS CR address/data mechanism and uses these field masks/shifts to encode or decode the 16-bit payload.

The RAWAON/SUPX fields describe lane calibration and PLL state machines, but the sequencing of those machines is in hardware/firmware and in the link-encoder or PHY-control code outside this generated header.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The state they describe is hardware state:

- Lane adaptation and DFE values may represent live measured state, firmware-owned calibration state, or manually programmed override values.
- `*_DONE`, `*_STATUS`, `*_OUT_IN`, and `STATS` fields expose observable status bits.
- Override fields can persist in hardware registers until reset, power-gating, firmware reprogramming, or a driver write changes them.
- PLL, prescaler, RTUNE, and bandgap fields can affect link-clock stability and analog PHY behavior; wrong persistence across power transitions may lead to failed link training or unstable PHY output.

Because most masks are 16-bit-window masks with `0x0000FFFFL` or smaller values, callers must preserve reserved bits when doing read-modify-write sequences unless the hardware programming guide explicitly says otherwise.

## Dependencies and Integration Points

- `dpcs_4_2_0_offset.h` supplies the corresponding register offsets and indirect CR addresses.
- `dcn31_resource.c` is the direct integration point for this generated header in the DCN31 display stack.
- `dcn31_dio_link_encoder.h` defines the link encoder table macros that consume DPCS register/mask names for RDPCSTX-facing fields.
- `reg_helper.h` and AMD display register helper macros combine register offsets, masks, and shifts into typed register operations.
- The wider DPCS generated-header family (`dpcs_4_2_2_*`, `dpcs_4_2_3_*`, older `dpcs_3_*`) provides cross-generation layouts with similar naming. Those headers are useful for drift comparison, but mixing generations is risky because names may compile while bit layouts or offsets differ.

## Risks and Edge Cases

- Hardware contract drift is the main risk. A wrong mask, shift, or offset can silently program the wrong analog field.
- The chunk boundary splits `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3`: this document covers the shift macros, while the mask macros are in the following chunk. Any merge or reconciliation lane should join that register block before producing a final per-file report.
- Many fields are paired override value/enable bits. Tests or reviews should check both halves of any manual override sequence.
- RAWAON lane 2, lane 3, and lane X blocks are intentionally repetitive. Copy/paste or generation errors can produce a single-lane mismatch that is hard to notice in normal compilation.
- Several fields are analog calibration or PLL controls. Bad values can cause physical link failures, intermittent training errors, signal-detect false positives/negatives, clock instability, or display blanking.
- Reserved bits are explicitly defined. Blind writes of full 16-bit values can disturb reserved hardware state if firmware or hardware expects those bits preserved.

## Test Signals

Useful validation signals for changes touching this area include:

- Build coverage for DCN31 display code that includes `dpcs_4_2_0_sh_mask.h`, especially `dcn31_resource.c`.
- Compile-time failures from missing or renamed macros used by `DPCS_DCN31_MASK_SH_LIST`, `LINK_ENCODER_MASK_SH_LIST_DCN31`, or register helper initializers.
- Static comparison of each covered `__SHIFT`/`_MASK` pair: masks should line up with the documented shift and field width, and reserved masks should fill the unused bits in the 16-bit field window.
- Cross-check against `dpcs_4_2_0_offset.h` to ensure each register block in this chunk has an offset entry.
- Hardware or emulator smoke tests for DisplayPort/HDMI link training on DCN31 ASICs, including lane training, FEC readiness, PHY power transitions, DP Alt Mode, and PLL clock programming.
- Debug traces for signal detect, lane adaptation done bits, DCC calibration done/skip behavior, and MPLL lock/status when link bring-up fails.
