# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 98339-100819

## Purpose

This chunk is part of AMD's generated DCN 4.1.0 register shift/mask header. It does not implement executable logic; it publishes C preprocessor constants that describe bit positions and bit masks for DisplayPort/PHY-style DPCSSYS CR1 raw always-on lane and supervisor registers. Runtime DCN401 display code uses these constants together with the matching offset header to issue field-accurate MMIO reads, writes, polling operations, and register-table initialization.

The range begins at an artificial chunk boundary in the middle of the `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC` register field list, then covers the complete `DPCSSYS_CR1_RAWAONLANE0_DIG_TX_RX_DCC_BYP_AC_CAP_IN` tail, full register-field families for `RAWAONLANE1`, `RAWAONLANE2`, `RAWAONLANE3`, and broadcast-style `RAWAONLANEX`, and then starts the `DPCSSYS_CR1_SUPX_DIG_*` supervisor/PLL field group. The line range ends at `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_OUT__BG_SUP_STATE_MASK`; the remaining `SUP_OVRD_OUT` masks continue in the next chunk.

## Important API Surface

There are no C functions, structs, enums, or storage objects in this chunk. The public API is the generated macro namespace:

- `DPCSSYS_CR1_RAWAONLANE*_...__<FIELD>__SHIFT` constants define the least-significant bit for a field in a 16-bit DPCSSYS lane register.
- `DPCSSYS_CR1_RAWAONLANE*_...__<FIELD>_MASK` constants define the field mask before shifting/extraction.
- `DPCSSYS_CR1_RAWAONLANEX_...` mirrors the per-lane field layout for a broadcast or lane-X access path, so consumers can program the same fields across a selected lane set without spelling lane 1, 2, or 3 individually.
- `DPCSSYS_CR1_SUPX_DIG_*__<FIELD>__SHIFT` and `_MASK` macros define supervisor/common-PLL fields for reference clock override, MPLLA/MPLLB override, SSC, fractional-N, charge-pump, prescaler, calibration, and supervisor-state override registers.

The dominant register groups in this slice are:

- Lane equalization, adaptation, and calibration: `DIG_AFE_ATT_IDAC_OFST`, `DIG_AFE_CTLE_IDAC_OFST`, `DIG_RX_ADPT_IQ`, `DIG_RX_ADAPT_FOM`, `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, `DIG_RX_ADPT_DFE_TAP1` through `TAP5`, `DIG_RX_ADAPT_DONE`, and `DIG_ADPT_CTL_0` through `DIG_ADPT_CTL_7`.
- DFE, slicer, and phase/reference levels: `DIG_DFE_*_VDAC_OFST`, `DIG_DFE_*_REF_LVL`, `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, `DIG_RX_IQ_PHASE_ADJUST`, `DIG_RX_SLICER_CTRL_EVEN`, and `DIG_RX_SLICER_CTRL_ODD`.
- Power, fast-path, and common-calibration status: `DIG_INIT_PWRUP_DONE`, `DIG_FAST_FLAGS`, `DIG_FAST_FLAGS_2`, `DIG_LANE_CMNCAL_MPLL_STATUS`, `DIG_LANE_CMNCAL_RCAL_STATUS`, and `DIG_MPLL_DISABLE`.
- Signal detect and receiver override/status: `DIG_TXRX_OVRD_IN`, `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_STATS`, `DIG_RX_OVRD_OUT_1`, `DIG_RX_OVRD_OUT_2`, `DIG_RX_OVRD_OUT_3`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, `DIG_RX_SIGDET_LF_CODE`, `DIG_SIGDET_OUT_OVRD`, and `DIG_SIGDET_OUT_IN`.
- DCC and analog calibration code paths: `DIG_RX_DCC_CAL_ICM_CODE_{0,1}`, `DIG_RX_DCC_CAL_IDF_CODE_{0,1}`, `DIG_RX_DCC_CAL_QCM_CODE_{0,1}`, `DIG_RX_DCC_CAL_QDF_CODE_{0,1}`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, `DIG_TX_DCC_CONFIG`, `DIG_TX_RX_DCC`, and `DIG_TX_RX_DCC_BYP_AC_CAP_IN`.
- Firmware/configuration and lane mode fields: `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_OVRD_IN`, `DIG_LANE_XCVR_MODE_IN`, and `DIG_RX_SIGDET_CONFIG`.
- Supervisor/common PLL fields: `DPCSSYS_CR1_SUPX_DIG_IDCODE_{LO,HI}`, `REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, `MPLLB_HDMI_CLK_OVRD_IN`, `MPLLA_OVRD_IN_0..5`, `MPLLB_OVRD_IN_0..5`, `MPLLA/MPLLB_SSC_PEAK_*`, `MPLLA/MPLLB_SSC_STEPSIZE_*`, `MPLLA/MPLLB_CP_OVRD_IN`, `MPLLA/MPLLB_CP_GS_OVRD_IN`, `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, and the start of `SUP_OVRD_OUT`.

## Field Semantics

The per-lane blocks describe low-level PHY state and overrides for the CR1 lane set:

- Adaptation readouts use compact `DATA`, `*_ADPT_VAL`, or tap-specific fields. Examples include 8-bit AFE/DFE offset fields, 7-bit IQ phase/adaptation fields, 10-bit VGA/CTLE values, and 12/13-bit DFE tap values.
- Status bits report training and calibration completion, such as `INIT_PWRUP_DONE`, `PH2_PWRUP_DONE`, `RX_ADAPT_DONE`, `LANE_CMNCAL_MPLL_DONE`, `LANE_CMNCAL_RCAL_DONE`, and signal-detect status/override outputs.
- Fast flag registers expose many one-bit skips or accelerated-calibration controls, including startup, AFE/DFE, bypass, reference-level, IQ, VCO, continuous adaptation, VPHUD/VREF, DCC, signal-detect, and RTUNE-related fast paths.
- DCC fields include RX DCC calibration code readouts, TX DCC bank addressing/data/continuous controls, TX/RX DCC configuration, and bypassed AC capacitor override/value fields.
- Lane mode and firmware configuration fields let firmware or driver flows select transceiver mode, adaptation behavior, and calibration behavior through raw lane registers.

The supervisor block shifts from per-lane analog state to common clocking/control:

- `REFCLK_OVRD_IN` selects or overrides reference clock paths.
- `MPLLA_*` and `MPLLB_*` blocks control common PLL enables, divider selection, VCO/fractional-N state, standby/calibration forcing, SSC configuration, fractional quotient/remainder/denominator fields, and charge pump settings.
- `SUP_OVRD_IN` and `SUP_OVRD_OUT` expose common supervisor override and acknowledge/state bits such as RTUNE request/ack, TX calibration code override, alternate reference-clock low-power selection, PLL state override, background lane/supervisor state override, and reference-clock acknowledgment.
- `PRESCALER_OVRD_IN` captures DCO range/fine-tune, MPLL reference dividers, and clock-detect enable/result fields.

## Control Flow

This header range has no local control flow. The effective runtime flow appears in consumers that combine:

1. A register offset, normally from `dcn_4_1_0_offset.h` or a related generated DPCS offset header.
2. One or more field constants from this `dcn_4_1_0_sh_mask.h` range.
3. AMD display register helpers/macros that pack a field value with `mask << shift`, write to MMIO, read and extract a field, or poll a status bit until hardware transitions.

For example, a PHY bring-up or link-training path may enable a lane/MPLL override, program divider or adaptation fields, wait for calibration done bits, then read signal-detect or adaptation result fields. The sequencing is not encoded here, but the names in this range define the legal bit positions that those flows depend on.

## State And Persistence

The macros are compile-time constants and do not persist state themselves. The state they describe is hardware state in DCN/DPCS MMIO registers:

- Per-lane state includes receiver adaptation coefficients, DFE/slicer/reference levels, power-up completion, calibration status, DCC calibration code, signal detect status, and lane transceiver mode.
- Override registers are persistent hardware latches until reset or until firmware/driver code writes a new value. Fields named `*_OVRD_EN`, `*_OVR_EN`, or `*_OVRD_VAL` are especially sensitive because enabling them can bypass hardware-autonomous behavior.
- Status and readout fields can be hardware-updated as PHY training, calibration, link power changes, or firmware microcode actions proceed.
- The `LANEX` group can affect multiple lanes through a broadcast path, so a single write using these definitions can intentionally or accidentally modify state wider than one lane.

Because this is a generated register contract, persistence concerns are mostly about pairing the right constants with the right silicon generation and avoiding stale values in driver sequences that cross suspend/resume, hotplug, link retraining, or DisplayPort/HDMI mode switches.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor. Functional dependencies are broader:

- Must be paired with the DCN 4.1.0 offset definitions for the same register names. The offset header supplies the address; this header supplies the bit layout.
- Integrates with AMD Display Core register helper macros used by DCN401 resource, link, PHY, GPIO, IRQ, and DMUB-adjacent code paths.
- Cross-generation generated headers under `include/asic_reg/dpcs/` expose similar `DPCSSYS_CR*_RAWAONLANE*` and `DPCSSYS_CR*_SUPX` names. Similarity is intentional but does not make the headers interchangeable; masks and offsets must match the ASIC generation and CR instance.
- Firmware-controlled fields such as `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, and fast-calibration flags are integration points with hardware firmware/microcontroller behavior. Driver writes can change how autonomous training or calibration proceeds.

## Risks

- The chunk begins and ends in the middle of generated register groups. Review or regeneration work must consider adjacent chunks before concluding that a register is incomplete or missing.
- A mask/shift typo can compile cleanly but misprogram hardware. This is higher risk than missing symbols because the generated names are all constants and many fields are same-width, so incorrect values may not be caught by type checking.
- Per-lane and `LANEX` broadcast names are visually similar. Accidentally using a broadcast macro or offset where a lane-specific access was intended can affect multiple lanes and create link instability.
- Fields with override enable bits can defeat hardware/firmware sequencing. Misuse of `OVRD_EN`, PLL force/calibration, RTUNE, DCC, or signal-detect override fields can cause bring-up failures, blank displays, hotplug flaps, or intermittent high-bit-rate link errors.
- Reserved masks are explicitly listed. Writes should preserve reserved bits unless the hardware programming guide requires otherwise; writing full literal register values through these masks may destabilize future stepping behavior.
- The supervisor MPLLA/MPLLB fields govern common clocking. Bad divider, SSC, fractional-N, charge-pump, or prescaler values can impact all lanes sharing the PLL, not just one link lane.
- Cross-generation copying from DPCS 3.x/4.2 or adjacent DCN headers is unsafe even when field names match, because offsets, CR instance numbering, reserved bits, or legal values may differ.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header, and hardware smoke tests:

- Compile DCN401/AMDGPU display code with this header and the matching `dcn_4_1_0_offset.h`; missing or renamed macros should fail at register-table expansion sites.
- Run a generated-header consistency check that every register field in this line range has a matching offset macro for the same generation and that every complete register block has both `__SHIFT` and `_MASK` definitions for each field.
- Compare the per-lane `RAWAONLANE1`, `RAWAONLANE2`, `RAWAONLANE3`, and `RAWAONLANEX` blocks mechanically. The repeated lane groups should have the same field layout except for the lane selector embedded in the macro name.
- Exercise display link bring-up on DCN401 hardware over DisplayPort and HDMI paths that require MPLLA/MPLLB, lane power-up, adaptation, DFE, DCC, signal detect, and SSC/fractional-N programming.
- Include suspend/resume, hotplug, link-rate change, lane-count change, and high-bit-rate link-training tests. These flows stress status polling, override lifetimes, and common PLL programming.
- Watch kernel display logs for training failures, HPD retry loops, AUX timeouts, signal-detect failures, and PHY calibration timeout messages after any regeneration or manual edit to this generated range.
