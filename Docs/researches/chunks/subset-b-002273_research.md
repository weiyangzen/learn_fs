# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 34158-36568

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header segment for the `DPCSSYS_CR2` register address block. It covers lines 34158 through 36568 and contains only preprocessor constants: 2,169 `#define` entries, with 1,086 `__SHIFT` definitions and 1,083 `_MASK` definitions across 243 register groups. The mismatch is expected for this chunk boundary: the range starts in the middle of `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2` after its shift definitions, and ends in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` before its remaining shifts and all masks.

The content is declarative register metadata. It defines no C functions, types, storage, structs, enums, executable statements, or local control flow. Runtime behavior appears only in consumers that include this generated header and use the constants to compose read-modify-write operations against DPCS/RDPCS hardware registers.

## Purpose

The purpose of this chunk is to expose symbolic bitfield locations for the DPCS CR2 supervisor and lane-control hardware. Each macro follows the generated AMD register naming convention:

- `<register>__<field>__SHIFT` gives the bit offset used to place or extract a field.
- `<register>__<field>_MASK` gives the already-shifted bit mask used to preserve, clear, or test the field.

The register areas covered here describe CR2 supervisor PLL programming, spread-spectrum clocking, analog override/status reporting, bandgap/reference-clock/RTUNE timing, lane 0 transmitter and receiver statistic controls, lane 0 analog TX override/status fields, lane 1 transmitter and receiver ASIC override inputs/outputs, lane 1 TX power-state sequencing, lane 1 RX power-state sequencing, and the beginning of lane 1 RX VCO calibration control.

## Exported API Surface

There are no callable APIs. The exported surface is the macro namespace itself, intended for AMDGPU display code that already knows the matching register addresses from companion generated headers.

Important macro families in this chunk include:

- `DPCSSYS_CR2_SUP_DIG_MPLLA_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_*`: MPLL A/B override, ASIC input, fractional-N divider, spread-spectrum peak/step, charge-pump, power-control, timer, calibration, status, and analog override-out fields.
- `DPCSSYS_CR2_SUP_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, `CLK_RST_*`, and `RTUNE_*`: supervisor-level control, analog calibration, reference-clock selection/detection, bandgap power sequencing, level override, resistor tuning request/status/set-value, and related timing counters.
- `DPCSSYS_CR2_SUP_ANA_*`: narrow analog-supervisor fields for prescaler, RTUNE, bandgap, and switch power-measurement control.
- `DPCSSYS_CR2_LANE0_DIG_ASIC_*`: lane 0 lane/TX/RX override inputs and ASIC input/output mirrors.
- `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power states, TX power-up timing, DCC CR-bank/DAC selection, TX clock alignment, and LBERT pattern/test controls.
- `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*`: lane 0 RX statistics match/control/counter registers, including masks, sample counters, comparator clocking, and statistic-stop control.
- `DPCSSYS_CR2_LANE0_DIG_ANA_*` and `DPCSSYS_CR2_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override/status definitions and direct analog TX measurement/power/ATB/DCC/termination/misc fields.
- `DPCSSYS_CR2_LANE1_DIG_ASIC_*`: lane 1 lane/TX/RX override inputs, equalizer override inputs, ASIC input mirrors, output mirrors, CDR/VCO ASIC inputs, and OCLA selection bits.
- `DPCSSYS_CR2_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX power states, TX power-up timing, DCC DAC control, TX clock alignment, and LBERT controls.
- `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX P0/P0S/P1/P2 power-state bitmaps and RX power-up timing.
- `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`: the beginning of lane 1 RX VCO calibration control fields; only the first five shift definitions are inside this chunk.

## Register Areas Covered

The supervisor MPLL sections define field positions for both MPLLA and MPLLB. The fields include enable, div5 clock enable, TX clock divider, override enable, V2I, standby, VCO frequency selection, calibration force, fractional-N enable, clock-sync override, multiplier, SSC enable/up-spread, PMIX enable, word-div2 enable, fractional configuration update, SSC peak, SSC step size, fractional quotient/remainder/denominator, charge-pump proportional/integral settings, and gear-shift charge-pump overrides. The corresponding ASIC input groups mirror many of the same semantic fields without the explicit override-enable pattern.

The supervisor power and analog sections expose state-machine controls and status for MPLL power control. The `MPLL_PWR_CTL_MPLL_OVRD` fields carry request-style controls such as `MPLL_EN`, `MPLL_STANDBY`, `MPLL_DIV5_CLK_EN`, `MPLL_DAC_RANGE`, `MPLL_WAIT_LOCK`, and `MPLL_DONE_ACK`. The `MPLL_PWR_CTL_STAT` fields expose observed state such as lock, calibration done, calibration fail, range, DAC outputs, clock-stable state, FSM state, VCO frequency status, clock-off status, and divider state. Timer/calibration groups define lock timers, generic MPLL timers, PCLK stable timers, DAC max range, calibration control, and analog DAC output fields.

The clock/reset and RTUNE sections provide field locations for bandgap power-up timing, reference-clock power-up timing, VPH/UD reference controls, RTUNE request/continuous/acknowledge behavior, RTUNE FSM status, set values and measured status for RX/TXDN/TXUP legs, RTUNE retry/interval counters, and TX calibration code. These fields are coordination points between digital control logic and analog calibration hardware.

The supervisor analog override-output sections define fields that report or drive analog-facing outputs for MPLLA/MPLLB, RTUNE, bandgap, PMIX, and analog status. They include fields for analog enable/standby/divider states, SSC/fractional settings, VCO/CP settings, RTUNE acknowledge, PLL state, bandgap lane/supervisor state, reference-clock acknowledgement, PMIX enables, and analog status bits such as PLL lock and calibration completion.

Lane 0 coverage is primarily TX and RX-stat oriented. Its ASIC override and ASIC input/output groups define TX driver controls, common-mode controls, FIR/equalization controls, main/pre/post cursor settings, termination, polarity, scrambling-related controls, RTUNE code fields, pattern data, and TX request/ack state. The lane 0 TX power-control groups define P0/P0S/P1/P2 state bitmaps and power-up/down delay fields for serial AFE, predrivers, data path, boost, DCC, and rate changes. The DCC groups expose a small indirect DAC/CR-bank command surface with address/data, range/control, select/request/update, and acknowledge fields.

Lane 0 RX-stat groups define programmable match and sampling machinery rather than RX bring-up. They include data-mask/load values, data-rate and clear controls, load/lock gating, pattern selection, counter increment policy, error/running/done/fail/valid state bits, state counters 0 through 6, comparator clock control, auxiliary match-control registers, and statistic stop control.

Lane 0 analog TX groups define the digital override-out fields for analog TX, including power state, AFE enable, predriver enable, driver enable, impedance enable, termination, DCC, boost, rate, inversion, common-mode controls, feed-forward equalization controls, DCC DAC overrides, and analog status. The direct `LANE0_ANA_TX_*` groups are narrow analog register bitfields for override measurement, power override, alternate bus, ATB selection, DCC DAC/control, termination code/control, override clock, miscellaneous analog fields, and reserved analog fields.

Lane 1 coverage repeats most lane 0 TX concepts and adds more RX bring-up material. Its ASIC override input groups include lane and TX controls plus RX analog controls: AFE/VREG/clock/deserializer/CDR enables, VCO reset/calibration/continuous calibration, channel rate/width, DETRX controls, adaptation mode, DFE enable, squelch detect, VCO mux, load/update fields, VGA and peaking controls, VCO buffer settings, CDR reference/VCO controls, EQ pre/post/current settings, and additional RX override register groups. Lane 1 ASIC input mirrors expose the same classes of fields as direct hardware inputs rather than override inputs.

Lane 1 TX power-control groups mirror lane 0 TX P-state and timing fields. Lane 1 RX power-control groups define RX P0/P0S/P1/P2 bitmaps for AFE, clock VREG, analog clock, deserializer, CDR, VCO frequency reset, VCO calibration reset, continuous calibration, and digital clock enable. RX timing groups define AFE/VREG/clock enable timing, fast enable bits, fast-start time, rate-change time, CDR enable time, deserializer enable time, and deserializer disable time. The final in-range register starts RX VCO calibration control by defining shift positions for fixed-count calibration, fixed-count enable, calibration-count shift, bounce count, and disabling bin hold.

## Control Flow And State Behavior

This header has no branches or local execution. It is a register-field map for hardware state machines. The field names nevertheless reveal the control surfaces that consumers must sequence carefully:

- MPLL programming is staged through override/ASIC input fields, fractional-N quotient/remainder/denominator fields, SSC peak/step fields, charge-pump fields, PMIX controls, timer fields, and power-control status fields.
- Supervisor bring-up coordinates bandgap, reference clock, prescaler, level, RTUNE, and PLL status. Request/acknowledge pairs such as `RTUNE_REQ`/`RTUNE_ACK`, state fields such as `MPLLA_STATE`, and lock/calibration status fields are intended for ordered writes followed by polling or readback.
- Lane TX bring-up is represented by P-state bitmaps and power-up timers. Consumers are expected to program timing/control values before requesting link/lane state changes.
- DCC DAC and CR-bank controls expose request/update/ack bits and address/data fields, implying an indirect register transaction protocol.
- RX-stat registers implement a small hardware measurement pipeline: program mask/match/control fields, clear or start the statistic engine, poll running/done/fail/valid bits, and read count registers.
- RX power-control and VCO calibration fields gate analog AFE/CDR/deserializer/VCO blocks and calibration behavior. Incorrect sequencing can produce link-training failures or unstable CDR lock.

No software persistence exists here. Register values persist only according to the GPU hardware power and reset domains. Some fields named `SPARE`, `RESERVED`, or full-width data/address fields may hold hardware- or firmware-defined values, but this chunk does not document a software storage contract.

## Dependencies And Integration Points

This header depends only on the C preprocessor and the include guard defined at the top of `dpcs_3_1_4_sh_mask.h`. It is normally consumed together with generated register-address headers for the same ASIC generation, plus AMD display helper macros that combine a register address, field mask, and shift.

Likely integration points are:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS/PHY code that programs DisplayPort and HDMI transmitter PLLs and lanes.
- Generated DPCS 3.1.4 address headers that define the actual CR2 register offsets corresponding to the field masks here.
- Link training and display clock programming paths that configure MPLLA/MPLLB, SSC, fractional-N dividers, PMIX, P-states, and TX/RX lane rate/width fields.
- Power-management and suspend/resume flows that toggle bandgap/reference-clock/MPLL/lane power states and then poll lock, stable, calibration, request/ack, or done fields.
- Diagnostics and validation paths that use lane RX-stat counters, LBERT controls, DCC DAC controls, analog status bits, and OCLA selection.
- Firmware or hardware ownership boundaries for analog/ASIC input and override-output surfaces. The `OVRD`, `ASIC_IN`, `ASIC_OUT`, and `ANA_*` names indicate that some fields are direct hardware inputs/outputs while others are software override controls.

## Risks

- Generated mask drift is the primary risk. A single incorrect shift or mask can silently write an adjacent analog/PLL/lane bit during read-modify-write operations.
- This chunk has partial boundary registers. Automated per-chunk analysis must not treat the missing `MPLLA_SSC_PEAK_2` shifts or the missing `RX_VCO_CAL_CTRL_0` masks as file-level defects; they are outside the requested line range.
- Many registers pair command and status semantics in nearby bits. Examples include request/ack, enable/state, calibration force/done/fail, timer programming/status, statistic clear/running/done/fail, and DCC request/ack. Consumer code must know which bits are writable, read-only, write-one-to-clear, or latched by hardware.
- PLL and analog override fields are high-impact. Bad values in fractional-N, SSC, charge-pump, VCO, PMIX, DCC, termination, common-mode, or EQ fields can break display link training or cause marginal signal integrity.
- Repeated lane and PLL macro families are vulnerable to copy-generation errors. MPLLA/MPLLB, lane 0/lane 1, override/ASIC input, and status/output groups use similar field names with different prefixes; consumers should avoid mixing prefixes when composing register writes.
- Reserved fields are explicitly named and masked in many registers. Using broad writes instead of mask-scoped writes risks modifying reserved bits with undocumented hardware behavior.
- Full-width or nearly full-width address/data fields, such as DCC CR-bank address/data and SSC/fractional payload fields, require caller-side range validation because the header only supplies bit placement.

## Test Signals

Useful validation for this chunk is mostly build-time, generated-header consistency, and hardware integration testing:

- C preprocessing and compilation of AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Generated-register validation against the authoritative DPCS 3.1.4 register database, including checks that matching `__SHIFT` and `_MASK` pairs exist across whole-register boundaries outside this chunk.
- Static checks that consumer code uses the CR2 lane and supervisor prefixes consistently, especially for MPLLA versus MPLLB and lane 0 versus lane 1 register families.
- Hardware smoke tests for DisplayPort and HDMI modes on ASICs using DPCS 3.1.4: hotplug, link training at multiple rates, spread-spectrum enable/disable, display mode changes, suspend/resume, and multi-lane configurations.
- Register readback tests around MPLL lock/calibration, RTUNE acknowledge/status, bandgap/reference-clock power-up, lane TX/RX P-state transitions, DCC request/ack, RX-stat done/fail/valid status, and RX VCO calibration behavior.
- Signal-integrity or compliance tests when changing any consumer of TX analog, EQ, DCC, termination, SSC, charge-pump, PMIX, or fractional-N fields.

## Chunk Notes For Merge

The merged per-file report should describe this file as a generated DPCS 3.1.4 bitfield map, not handwritten driver logic. This chunk is centered on CR2 supervisor and lane-control masks. It starts after the `MPLLA_SSC_PEAK_2` shift definitions and ends before the complete `LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` register definition, so adjacent chunks are needed to reconstruct complete field-pair accounting for those two boundary registers.
