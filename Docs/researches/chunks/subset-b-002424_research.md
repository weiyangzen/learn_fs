# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 92391-94881

## Scope

This chunk is a late segment of the generated AMD DPCS 4.2.3 shift/mask header for the `DPCSSYS_CR4` register block. It covers line 92391 through line 94881 and defines 1,159 `__SHIFT` macros and 958 `_MASK` macros across 374 visible register groups. The unequal count is expected for this sliced range: it begins at the final mask for `DPCSSYS_CR4_RAWAONLANE1_DIG_ADPT_CTL_0`, includes complete repeated lane groups for lanes 2, 3, and X, and ends inside `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` before that register's remaining shifts and masks.

The content is declarative only. There are no C functions, structs, enums, variables, branches, loops, allocations, or local side effects. The public surface is a generated set of C preprocessor constants that describe bit positions and masks for 16-bit DPCS internal hardware registers.

## Purpose

`dpcs_4_2_3_sh_mask.h` gives AMDGPU display code symbolic names for the DPCS 4.2.3 register layout. Consumers combine these constants with matching offsets from `dpcs_4_2_3_offset.h` and AMD display register helpers to compose or decode register values without hard-coding bit numbers.

This chunk focuses on CR4 always-on lane and supervisor resources:

- The tail of `DPCSSYS_CR4_RAWAONLANE1_DIG_*`, including adaptation control words, MPLL disable, fast calibration flags, common calibration status, TX/RX disable overrides, RX loss/signal-detect filtering, RX override outputs, signal-detect calibration codes, RX/TX DCC calibration data, firmware config flags, and lane transceiver mode inputs.
- Full repeated `DPCSSYS_CR4_RAWAONLANE2_DIG_*`, `DPCSSYS_CR4_RAWAONLANE3_DIG_*`, and `DPCSSYS_CR4_RAWAONLANEX_DIG_*` field maps for RX adaptation, DFE/phase/reference offsets, MPLL coarse tuning, power-up done, fast flags, adaptation controls, signal-detect controls, DCC calibration, firmware config, and lane mode overrides.
- The start of `DPCSSYS_CR4_SUPX_DIG_*` and `DPCSSYS_CR4_SUPX_ANA_*`, covering supervisor ID fields, reference clock overrides, MPLLA/MPLLB divider and HDMI clock overrides, PLL override inputs, spread-spectrum clocking values, fractional-N fields, charge-pump controls, supervisor and prescaler overrides, ASIC input mirrors, bandgap inputs, analog prescaler/RTUNE/bandgap controls, and the beginning of MPLLA/MPLLB analog control fields.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace, where most complete fields follow `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Important macro families in this range:

- `DPCSSYS_CR4_RAWAONLANE{1,2,3,X}_DIG_ADPT_CTL_*`, `RX_ADPT_*`, `RX_ADAPT_DONE`, and `RX_ADAPT_FOM`: adaptation control and readback fields for AFE, CTLE, VGA, DFE taps, IQ phase, figure-of-merit, and completion state.
- `DPCSSYS_CR4_RAWAONLANE{2,3,X}_DIG_DFE_*`, `RX_PHSADJ_*`, and `RX_SLICER_CTRL_*`: per-lane DFE data/error/bypass/phase/reference adjustment and slicer controls.
- `DPCSSYS_CR4_RAWAONLANE{1,2,3,X}_DIG_FAST_FLAGS` and `FAST_FLAGS_2`: fast-path controls for RX startup, adaptation, AFE/DFE/bypass/reference/IQ/VCO calibration, TX common mode, RX power-up, continuous calibration/adaptation, DCC, VPHUD/VREF, TX RTUNE skip, and signal-detect calibration.
- `DPCSSYS_CR4_RAWAONLANE{1,2,3,X}_DIG_MPLL_DISABLE`, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `LANE_CMNCAL_MPLL_STATUS`, and `LANE_CMNCAL_RCAL_STATUS`: per-lane MPLL and common calibration control/status fields.
- `DPCSSYS_CR4_RAWAONLANE{1,2,3,X}_DIG_TXRX_OVRD_IN`, `RX_OVRD_OUT_*`, `SIGDET_OUT_OVRD`, `SIGDET_OUT_IN`, `RX_SIGDET_*`, and `RX_LOS_MASK_CTL`: override and status fields for TX/RX disable, RX squelch, VREF, termination, signal detect, loss masking, and PMA signal-detect filtering.
- `DPCSSYS_CR4_RAWAONLANE{1,2,3,X}_DIG_RX_DCC_CAL_*`, `TX_DCC_BANK_*`, and `TX_DCC_CONT`: RX DCC calibration code readbacks and TX DCC banked data/configuration controls.
- `DPCSSYS_CR4_SUPX_DIG_*`: common supervisor digital fields for reference clock, MPLLA/MPLLB clock generation, PLL override inputs, SSC peak and step size, fractional-N quotient/remainder/denominator, charge-pump controls, supervisor and prescaler overrides, level controls, debug, and ASIC-input mirrors.
- `DPCSSYS_CR4_SUPX_ANA_*`: supervisor analog fields for prescaler, RTUNE, bandgap/reference selection, ATB/measurement switches, MPLLA/MPLLB misc, override, ATB, and control registers.

Reserved bit ranges are emitted as macros alongside named fields. That gives consumers a way to preserve or validate reserved bits during read-modify-write sequences, but it does not encode access permissions.

## Register Areas Covered

The raw always-on lane sections are strongly repetitive. Lane 2, lane 3, and lane X each expose the same low-level RX adaptation and calibration surface: analog front-end IDAC offsets, CTLE/VGA/DFE adaptation values, odd/even DFE offsets, phase adjustment maps, RX IQ phase adjustment, MPLLA/MPLLB coarse tune values, initial power-up done state, fast calibration flags, adaptation control words, MPLL/RCAL common-calibration status, TX/RX disable overrides, RX loss and signal-detect filtering, RX squelch/VREF/termination/signal-detect override outputs, signal-detect calibration thresholds/codes, DCC calibration codes, and firmware configuration fields.

The lane X block maps the same register fields into a generic or broadcast-style lane window at offsets around `0x7000` in the companion offset header. That makes it important to distinguish lane-specific writes from generic-lane writes when reading driver code or register traces.

The supervisor digital section starts at `DPCSSYS_CR4_SUPX_DIG_IDCODE_LO` and maps common resources shared by CR4 lanes. It includes reference-clock and bandgap controls, divided and HDMI clock controls for both MPLLA and MPLLB, PLL enable/standby/divider/VCO/fractional-N/SSC override inputs, charge-pump proportional/integral settings, supervisor/prescaler/level override fields, and ASIC input mirrors that expose hardware-selected values back to software.

The supervisor analog section begins at `DPCSSYS_CR4_SUPX_ANA_PRESCALER_CTRL`. It exposes prescaler and RTUNE controls, bandgap/reference selectors, analog measurement switches, MPLLA and MPLLB misc controls, PLL override controls, ATB measurement selectors, and PLL control words. The chunk reaches only the first seven shift fields of `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD`; the rest of that register continues in the next chunk.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior appears only when AMD display code includes the generated header and uses these constants to read, write, or update DPCS registers.

The field names imply several hardware-controlled workflows:

- Per-lane RX adaptation and calibration: AFE, VGA, CTLE, DFE tap, IQ, VREF, VPHUD, signal-detect, DCC, and VCO-related flags and readbacks describe calibration/adaptation phases that must settle before link traffic is reliable.
- Lane power and mode transitions: `INIT_PWRUP_DONE`, TX/RX disable overrides, lane transceiver mode inputs, MPLL disable, MPLL common-calibration status, and RCAL status expose lane bring-up, shutdown, and common calibration sequencing.
- Signal-detect and loss handling: RX LOS mask counters, signal-detect HF/LF filter controls, thresholds, calibration codes, override output bits, and input readbacks describe how the PHY observes cable/signal state and filters transient loss indications.
- Common PLL and reference-clock programming: supervisor reference clock, bandgap, MPLLA/MPLLB divider, HDMI clock, VCO frequency, multiplier, fractional-N, SSC, charge-pump, and analog override fields describe shared clock generation and PLL tuning.
- Override and debug flows: repeated value plus `*_OVRD_EN` or `OVRD_*` fields let driver, firmware, validation, or recovery code force hardware-facing values instead of relying on normal state-machine outputs.

No software state is persisted here. Hardware register contents persist or reset according to ASIC reset, clock, and power domains. Field names such as `*_STATUS`, `*_DONE`, `*_IN`, `*_ASIC_IN`, `*_STATS`, and `*_OUT` suggest readback-oriented surfaces, while `*_OVRD_IN`, `*_OVRD_EN`, `*_CONFIG`, `*_CTL`, calibration code, and clock/PLL programming fields suggest control-oriented surfaces. Exact read/write, sticky, clear-on-read, and reserved-bit semantics must come from the hardware register database and driver access policy.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. The semantic dependency is the DPCS 4.2.3 register database that generated this file and the matching `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` address map. The companion offset header maps these lane windows to CR4 offsets such as lane 1 around `0x4100`, lane 2 around `0x4200`, lane 3 around `0x4300`, lane X around `0x7000`, and supervisor `SUPX` around `0x8000`.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`. That file builds DCN316 DPCS register, shift, and mask tables through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.

Related integration points include AMD DCN316 link encoder/resource initialization, DCN31-style DIO link encoder helpers, DisplayPort and HDMI link training, link-rate changes, lane-count and lane-power transitions, suspend/resume, hotplug recovery, PLL lock and SSC programming, RX signal-detect/loss handling, DCC and adaptation flows, and hardware validation paths that use override or ATB/debug fields.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can silently write an adjacent analog, PLL, calibration, or override bit during a read-modify-write sequence.
- The lane 2, lane 3, and lane X sections are highly repetitive. A generation error in one lane can create lane-asymmetric failures, while misuse of the lane X window can accidentally affect a generic or broadcast access path.
- The chunk mixes lane-local controls with shared supervisor resources. SUPX reference-clock, bandgap, prescaler, RTUNE, MPLLA, and MPLLB mistakes can affect all CR4 lanes rather than a single lane.
- Override-enable fields are common. Setting an override value without its enable bit may have no intended effect, while leaving an enable bit asserted after debug or recovery can hold the PHY outside normal hardware state-machine control.
- Several clock and PLL values are split across multiple 16-bit registers, including SSC peak/step-size and fractional-N quotient/remainder/denominator. Partial updates can leave transient or inconsistent PLL programming.
- Status, readback, control, and reserved fields are represented identically as macros. Consumer code must know register access permissions and side effects from the hardware spec.
- This slice starts and ends at chunk boundaries inside register groups. Merge-time validation should account for the previous chunk's `DPCSSYS_CR4_RAWAONLANE1_DIG_ADPT_CTL_0__VAL__SHIFT` and the next chunk's remaining `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` definitions before reporting missing shift/mask pairs.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN316 targets that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that every complete register group in the full `dpcs_4_2_3_sh_mask.h` file has matching `__SHIFT` and `_MASK` definitions, with chunk-boundary exceptions for `RAWAONLANE1_DIG_ADPT_CTL_0` and `SUPX_ANA_MPLLB_OVRD`.
- Cross-check register names and field widths against `dpcs_4_2_3_offset.h` and the authoritative DPCS 4.2.3 register database.
- Compare repeated lane 2, lane 3, and lane X field layouts for expected symmetry, while separately validating that their companion offsets target the intended lane or generic-lane window.
- Runtime hardware tests on DCN316/DPCS 4.2.3-class ASICs: DP and HDMI link training, link-rate changes, lane-count changes, hotplug, suspend/resume, low-power entry/exit, PLL lock, SSC programming, signal-detect/loss behavior, RX adaptation, DCC calibration, and recovery after failed link training.
- Register readback during bring-up should show expected transitions for `INIT_PWRUP_DONE`, MPLL/RCAL calibration status, RX adaptation done/FOM, signal-detect readbacks, DCC calibration values, supervisor reference/bandgap readiness, MPLLA/MPLLB ASIC input mirrors, and cleanup of override-enable bits.

## Chunk Notes For Merge

This document intentionally covers only lines 92391-94881 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should cover the beginning of CR4 and the missing `DPCSSYS_CR4_RAWAONLANE1_DIG_ADPT_CTL_0__VAL__SHIFT`. Later chunks should continue `DPCSSYS_CR4_SUPX_ANA_MPLLB_OVRD` and the rest of the CR4 supervisor analog and subsequent DPCS 4.2.3 register fields. The final merged per-file report should describe the whole file as a generated ASIC register bitfield map for AMD display PHY programming, not handwritten runtime logic.
