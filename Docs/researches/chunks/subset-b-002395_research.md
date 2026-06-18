# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 21873-24312

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header section. It contains preprocessor constants only: register field `__SHIFT` values and `MASK` values for DPCS CR0 lane-x digital/analog controls, CR0 raw-lane PCS/PMA/FSM/IRQ/TX/RX controls, and the start of the CR1 supervisor digital block. The companion address constants live in `dpcs_4_2_3_offset.h`; for example this chunk's `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0__*` fields pair with `ixDPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` at offset `0x9060`, and `DPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0__*` pairs with `ixDPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0` at offset `0x0007`.

The header is included by the DCN 3.1.6 resource implementation together with `dpcs_4_2_3_offset.h`, so these symbols are part of the AMD display driver's low-level register programming vocabulary for that ASIC generation.

## Purpose

The purpose of this line range is to provide named bit layout metadata for DPCS hardware registers. Driver code can use these macros to build read-modify-write values, decode hardware status, enable overrides, clear interrupt latches, and program PHY/PCS calibration knobs without open-coded bit positions.

The chunk is not business logic and has no direct behavior on its own. Its correctness matters because each constant encodes a hardware contract. A wrong mask or shift can silently write the wrong bit, corrupt adjacent fields, leave a reserved bit set, or misread a status/interrupt condition.

## Main Register Areas

### CR0 Lane-X RX CDR and DPLL

The chunk begins at the tail of `DPCSSYS_CR0_LANEX_DIG_RX_CDR_CDR_CTL_4`, carrying masks for SSC-on/off frequency and phase gain fields (`SSC_ON_FRUG0`, `SSC_ON_FRUG1`, `SSC_ON_PHUG0`, `SSC_ON_PHUG1`) plus a reserved high bit. It then defines:

- `DPCSSYS_CR0_LANEX_DIG_RX_CDR_STAT`: status fields for current phase/frequency update gain values (`PHUG_VALUE`, `FRUG_VALUE`).
- `DPCSSYS_CR0_LANEX_DIG_RX_DPLL_FREQ`: a 14-bit DPLL frequency value.
- `DPCSSYS_CR0_LANEX_DIG_RX_DPLL_FREQ_BOUND_0` and `_1`: upper/lower DPLL frequency bounds and a bound-enable bit.

These macros support clock-data recovery and digital PLL configuration/inspection for a receive lane. They are likely used during link training, spread-spectrum clock handling, and debug/diagnostic paths.

### CR0 RX Adaptation Control

The `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*` block defines a dense set of receiver adaptation controls and statuses:

- `ADPT_CFG_0` through `ADPT_CFG_9` configure adaptation timing, thresholds, step sizes, enable bits, slicer/TGG behavior, CTLE/VGA/ATT/DFE participation, and initial error values.
- `RST_ADPT_CFG` and `ADPT_RESET` provide per-subsystem adaptation reset controls, including ATT, VGA, CTLE boost/pole, DFE tap 1, and ASM1 reset.
- `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, and `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS` expose adaptation result codes and completion bits.
- `DFE_DATA_*_VDAC_OFST`, `DFE_ERROR_*_VDAC_OFST`, `RX_SLICER_CTRL_*`, and `ERROR_SLICER_LEVEL` expose or program even/odd VDAC offsets, slicer controls, and error slicer levels.
- `DAC_CTRL_SEL_1` through `_3`, `CR_BANK_ADDR`, and `CR_BANK_DATA` select DAC control sources and provide banked control/data access.

This is the most operationally significant part of the chunk. It names the fields used to start or tune receiver equalization/adaptation and to determine when adaptation has completed. Many fields are narrow multi-bit values packed into 16-bit register words, so correct masking before insertion is important.

### CR0 RX Statistics and Match Counters

The `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*` registers describe receive-side sampling/match/statistical counters:

- `LD_VAL_1` and `DATA_MSK` define load value and data mask fields.
- `MATCH_CTL0` through `MATCH_CTL5` define match patterns and match control options, including shadow load, match enable, pattern enable, pattern offset, valid-symbol enable, and sync-valid count.
- `STAT_CTL0`, `STAT_CTL1`, `STAT_CTL2`, and `STAT_STOP` define stat enable, reset, shadow-load, symbol/count mode, start/pause behavior, freeze-on-match, compare modes, and stop-on-match controls.
- `SMPL_CNT1` and `STAT_CNT_0` through `_6` expose sample/count accumulator fragments.
- `CAL_COMP_CLK_CTL` selects or enables calibration/comparison clock behavior.

These fields are integration points for diagnostic sampling, link bring-up analysis, and hardware-assisted validation of RX data patterns. Because the counter values are split across multiple registers, readers must assemble them consistently and account for shadow-load or freeze semantics.

### CR0 MPHY, Analog TX/RX Overrides, and Calibration

The chunk then defines MPHY and analog override/control/status fields for CR0 lane-x:

- `DPCSSYS_CR0_LANEX_DIG_MPHY_RX_PWM_CTL`, `MPHY_RX_TERM_LS_CTL`, and `MPHY_RX_ANA_PWM_CLK_STABLE_CNT` control MPHY low-speed/PWM receive behavior, termination, and clock-stability count.
- `DPCSSYS_CR0_LANEX_DIG_ANA_TX_OVRD_OUT`, TX termination code override registers, TX EQ override outputs `_0` through `_5`, and TX DCC DAC override outputs expose TX analog control handoff and equalization override state.
- `DPCSSYS_CR0_LANEX_DIG_ANA_RX_CTL_OVRD_OUT`, `ANA_RX_PWR_OVRD_OUT`, `ANA_RX_VCO_OVRD_OUT_*`, `ANA_RX_CAL`, `ANA_RX_DAC_CTRL*`, `ANA_RX_AFE_ATT_VGA`, `ANA_RX_AFE_CTLE`, `ANA_RX_SCOPE`, `ANA_RX_SLICER_CTRL`, IQ phase/sense/calibration controls, and analog-signal-change enable fields cover RX analog front-end control and calibration.
- `DPCSSYS_CR0_LANEX_DIG_ANA_STATUS_0` and `_1` expose analog status fields.
- Non-`DIG` lane analog registers such as `DPCSSYS_CR0_LANEX_ANA_TX_*` and `DPCSSYS_CR0_LANEX_ANA_RX_*` define direct analog TX/RX override, measurement, ATB, DCC, power, clock, slicer, squelch, calibration, and reserved fields.

The recurring `*_OVRD_*` and `*_EN` pattern indicates a muxed hardware-control model: firmware/hardware defaults can be replaced by explicitly programmed values when the corresponding override enable bit is asserted. Any driver sequence using these fields must preserve reserved bits and be careful about ordering because enabling an override before writing its value can transiently drive the PHY with stale settings.

### CR0 Raw-Lane PCS/PMA Crossbar and ATE

The `DPCSSYS_CR0_RAWLANEX_DIG_*` section covers lane-facing PCS/PMA interfaces and production/test hooks:

- `PCS_XF_TX_OVRD_IN`, `_IN_1`, `TX_PCS_IN`, `TX_OVRD_OUT`, and `TX_PCS_OUT` describe TX-side PCS override inputs and observed PCS outputs.
- `PCS_XF_RX_OVRD_IN` through `_3`, `RX_PCS_IN` through `_4`, `RX_OVRD_OUT`, `RX_PCS_OUT`, adaptation ACK/FOM, directed TX pre/main/post controls, lane number, reserved fields, ATE override inputs, RX EQ delta-IQ override input, and TX/RX termination control fields describe RX-side PCS interaction and test overrides.
- `PMA_XF_LANE_OVRD_IN/OUT`, `PMA_XF_SUP_OVRD_IN`, `PMA_XF_SUP_PMA_IN`, TX/RX PMA inputs/outputs, lane RTUNE control, MPHY override input/output, and RX adaptation override output define PMA-facing handoff state.
- Several `ATE_*` registers provide automated-test-equipment control points for RX/TX override paths.

These macros are integration points between the display driver's register programming layer and lower-level PHY state machines. They are also a risk area because many controls are intended for test or override modes rather than normal link operation.

### CR0 Raw-Lane FSM, IRQ, TX_CTL, and RX_CTL

The raw-lane digital block includes state-machine, interrupt, and control/status register fields:

- `FSM_FSM_OVRD_CTL`, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference/IQ calibration controls, fast supervisor/TX common-mode/RX detect controls, RX power-up/VCO wait/VCO calibration controls, common calibration MPLL/RCAL status, continuous calibration/adaptation/data/phase/AFE controls, fast flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, and RX IQ phase offset.
- `IRQ_CTL_*` registers expose RX reset/request/rate/P-state/adaptation request/adaptation disable IRQs and clear bits, lane transceiver mode IRQs, RX PH2 calibration request/disable IRQs and clear bits, RX-to-TX serial loopback IRQs, DCC on-demand, TX reset/request IRQs, and IRQ masks.
- `TX_CTL_*` registers define TX FSM/clock/DCC-continuous/OCLA/UPCS-OCLA control and status fields.
- `RX_CTL_*` registers define RX FSM, loss-of-signal masking, data-enable override, off-cancellation/adaptation continuous status, and UPCS OCLA fields.

This part of the header maps the observable and overrideable state-machine surface for the lane. Control flow is external to this file: the state machines are in hardware, while the driver writes or reads fields through register access helpers. Clear registers and mask registers are especially sensitive because they often have write-one-to-clear or interrupt-gating semantics in the hardware block.

### CR1 Supervisor Digital Block Start

Near the end of the chunk, an address-block marker switches to `dpcssys_cr1_rdpcstxcrind`. The chunk defines the first CR1 supervisor digital registers:

- `IDCODE_LO` and `IDCODE_HI` identify the block/revision.
- `REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN` define clock-selection and override fields for reference, divided, and HDMI clock paths.
- `MPLLA_OVRD_IN_0` through `_5`, `MPLLA_SSC_PEAK_1/_2`, `MPLLA_SSC_STEPSIZE_1/_2`, `MPLLA_CP_OVRD_IN`, and `MPLLA_CP_GS_OVRD_IN` define MPLLA enable/divider/VCO/calibration/fractional-N/SSC/charge-pump override fields.
- The same structure repeats for MPLLB through `MPLLB_CP_GS_OVRD_IN`.
- `SUP_OVRD_IN` and `PRESCALER_OVRD_IN` begin supervisor-level override and prescaler configuration, including RTUNE request/override, TX calibration code, alternate reference clock low-power selection, DCO range/fine-tune, ref-clock divisors, and clock-detect control/result.

This block is about common/supervisor resources rather than per-lane CR0 state. It is tied to PLL and reference-clock setup and must be synchronized with higher-level display clock and link encoder resource programming.

## APIs, Types, and Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The exported interface is the macro namespace:

- `DPCSSYS_*__FIELD__SHIFT` defines the bit position for a field.
- `DPCSSYS_*__FIELD_MASK` defines the already-shifted mask for that field.
- Register-name comments such as `//DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` group the macros for a single hardware register.
- Address-block comments identify logical register address spaces, including the transition from CR0 raw/lane registers to `dpcssys_cr1_rdpcstxcrind`.

The intended consumer pattern is to combine an offset macro from `dpcs_4_2_3_offset.h` with field masks/shifts from this header through the display driver's register access helpers and generated register tables.

## Control Flow

This file has no software control flow. There are no branches, loops, callbacks, locks, or error paths. Runtime control flow exists in code that includes this header and performs hardware register access. For this chunk, the implied hardware flows are:

1. Program or read CR0 RX CDR/DPLL and adaptation fields during lane bring-up or tuning.
2. Start/reset adaptation, poll `*_STATUS` completion bits, and read adaptation result codes.
3. Configure or sample RX statistics/match counters for diagnostics.
4. Apply analog/PCS/PMA override fields only when the relevant override-enable bits and hardware state allow it.
5. Observe or clear raw-lane FSM and IRQ state.
6. Program CR1 supervisor clock/MPLL/prescaler fields as part of common PHY/clock setup.

## State and Persistence

The macros are compile-time constants and do not hold state. The state represented by these names is hardware state in DPCS registers:

- Configuration state persists in the hardware register file until reset, power-gating, firmware/hardware ownership changes, or an explicit driver write.
- Status and counter state is produced by hardware and can be transient or latch-based.
- IRQ clear registers likely affect latched interrupt state, while mask registers gate subsequent interrupt reporting.
- Override-enable fields change ownership of a signal path and can persist across normal software operations until cleared or reset.

The header itself has no persistence, allocation, reference counting, or synchronization.

## Dependencies and Integration Points

Primary dependencies are architectural rather than code-level:

- `dpcs_4_2_3_offset.h` supplies the corresponding indexed register offsets.
- `dcn316_resource.c` includes both the offset and shift/mask headers for DCN 3.1.6 resource initialization.
- The AMD display register access layer supplies the actual read/write macros and typed register lists that consume these field definitions.
- Related generated headers for nearby ASIC revisions (`dpcs_4_2_0`, `dpcs_4_2_2`, `dpcs_3_1_4`, and `dcn_4_1_0`) contain similar register fields, which makes cross-version diffing useful when auditing hardware changes.
- Hardware/firmware sequencing outside this header determines whether a field is safe to write, read-only, write-one-to-clear, sticky, or reserved.

## Risks and Edge Cases

- Mask width differences: this DPCS 4.2.3 header uses many 16-bit-looking masks such as `0x03FFL`, while related generated files sometimes use zero-extended 32-bit masks. Consumers should treat the value, not textual width, as authoritative.
- Reserved fields are explicitly named and masked. Driver writes must avoid setting reserved bits unless hardware documentation says otherwise.
- Override fields are hazardous because asserting `*_OVRD_EN`, `*_EN`, or related mux controls can bypass hardware/firmware-managed PHY behavior.
- Split counters and multi-register values can tear if read without using shadow-load/freeze controls where required.
- Interrupt clear fields may be write-one-to-clear; a naive read-modify-write on clear registers can accidentally clear unrelated pending IRQs.
- PLL/SSC/fractional-N fields for MPLLA/MPLLB are clock-critical. Bad values can break link training, display output, or power behavior.
- Generated header drift is a real risk: offset and sh/mask headers must come from the same ASIC register database version.
- This chunk starts in the middle of `CDR_CDR_CTL_4` and ends in the middle of the CR1 supervisor block, so final per-file reconciliation should join neighboring chunks for complete register coverage.

## Test and Validation Signals

Useful validation for code using these macros includes:

- Build coverage for DCN 3.1.6 paths that include `dpcs_4_2_3_sh_mask.h` and `dpcs_4_2_3_offset.h`.
- Static checks that each used field has both `__SHIFT` and `_MASK` definitions and that the register offset exists in the matching offset header.
- Register programming tests or debug traces confirming that read-modify-write operations preserve reserved bits.
- Hardware bring-up signals: link training succeeds, lanes lock, DPLL/CDR status fields report plausible values, and RX adaptation status bits complete.
- IRQ tests verifying that mask and clear fields only affect intended lane events.
- Display validation on hardware using DCN 3.1.6 resources, including modes that exercise PLL/SSC/reference-clock selection and receiver adaptation.
- Cross-version comparison against `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_2_sh_mask.h` when diagnosing regressions, because many fields are expected to remain structurally similar across DPCS 4.2.x revisions.
