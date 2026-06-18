# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 24313-26724

## Scope

This chunk is a middle segment of the generated AMD DPCS 4.2.3 shift/mask header. It covers line 24313 through line 26724 and defines 1,220 `__SHIFT` macros and 975 `_MASK` macros across 233 visible register groups. The range begins with the tail masks for `DPCSSYS_CR1_SUP_DIG_PRESCALER_OVRD_IN`, then covers CR1 supervisor/common PLL, analog, RTUNE, lane 0, and the beginning of lane 1 register bitfields. It ends inside `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_3`, after the `TX_VCM_HOLD_TIME_17_15__SHIFT` definition and before that register's remaining mask definitions.

The content is declarative only. There are no C functions, structs, enums, runtime allocations, branches, loops, or local side effects. The exported surface is a set of preprocessor constants that describe bit positions and masks for DPCS CR1 memory-mapped or indexed hardware registers.

## Purpose

`dpcs_4_2_3_sh_mask.h` provides symbolic bitfield definitions for AMDGPU display code that targets the DPCS 4.2.3 register layout. Consumers combine these macros with companion register offsets from `dpcs_4_2_3_offset.h` and AMD display register helpers to compose, update, and decode PHY, PLL, lane, calibration, and debug registers without embedding raw bit numbers in driver logic.

This chunk focuses on CR1 display PHY resources:

- CR1 supervisor digital controls and readbacks for override outputs, MPLLA/MPLLB ASIC inputs, divided and HDMI clocks, global PHY reset/reference clock controls, lane-level settings, bandgap inputs, charge-pump settings, PLL power-control state/timers/calibration, SSC spread configuration, RTUNE configuration/status, and analog override readbacks.
- CR1 supervisor analog fields for prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous controls, PLL override/control/ATB fields, and reserved analog register surfaces.
- CR1 lane 0 digital/analog TX/RX controls, override inputs/outputs, power-state tables, power-up timers, DCC DAC controls, TX clock alignment, LBERT, RX statistics/match counters, and analog TX override/status fields.
- CR1 lane 1 digital ASIC override/control/readback fields and the beginning of its TX power-state and power-up timer fields.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace:

- `DPCSSYS_CR1_SUP_DIG_*`: supervisor/common digital fields, including `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `MPLLA_ASIC_IN_*`, `MPLLB_ASIC_IN_*`, divided/HDMI clock ASIC inputs, global `ASIC_IN`, level/bandgap/charge-pump ASIC inputs, PLL power-control registers, SSC spread type, RTUNE registers, analog override outputs, and analog status.
- `DPCSSYS_CR1_SUP_ANA_*`: supervisor analog fields for prescaler control, RTUNE control, bandgap controls and measurement switches, MPLLA/MPLLB misc/control/override/ATB registers, and reserved analog words.
- `DPCSSYS_CR1_LANE0_DIG_*`: lane 0 digital ASIC overrides, TX/RX override readbacks, lane ASIC inputs, TX power-state definitions, TX power-up timing, DCC bank/DAC controls, TX clock alignment, LBERT control, RX statistic/match/control/count registers, and digital-to-analog TX override/status outputs.
- `DPCSSYS_CR1_LANE0_ANA_*`: lane 0 analog TX controls for override measurement, power override, alternate/ATB buses, DCC DAC, DCC control, termination code, override clock, misc, and reserved fields.
- `DPCSSYS_CR1_LANE1_DIG_*`: lane 1 digital ASIC lane/TX/RX override controls, RX equalization inputs, ASIC input/output mirrors, OCLA enable bits, TX power-state definitions, and the beginning of TX power-up timers.

Most complete register groups follow the generated pair pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. Reserved fields are emitted as well, which lets consumers preserve, clear, or validate reserved bit ranges during read-modify-write sequences when the hardware specification allows it.

## Register Areas Covered

The supervisor digital section exposes common resources shared by the CR1 lanes. The MPLLA/MPLLB blocks define enable, standby, divider, multiplier, VCO frequency, fractional-N, SSC peak and step-size, HDMI/divided clock, and clock-sync fields. The PLL power-control sub-blocks add override controls, state/status readback, lane ownership/status, lock/stable timers, calibration fields, DAC range/input/output fields, and SSC spread type. These definitions are central to link-rate programming and PLL bring-up for DisplayPort or HDMI paths.

The supervisor analog section mirrors the common analog side. Prescaler, RTUNE, and bandgap fields control or observe reference-clock detection, resistor tuning, bias generation, and analog measurement paths. MPLLA/MPLLB analog misc, override, ATB, and control registers expose charge-pump, VCO, calibration, clock/reset, and test-bus selectors. Although this header does not encode access permissions, the naming separates configuration-like fields from `STAT`, `ACK`, `OUT`, and measurement readback fields.

Lane 0 receives the broadest coverage in this chunk. The digital lane ASIC override groups define TX/RX request, reset, pstate, rate, data-enable, clock, serial/loopback, signal-detect, VREF, termination, PWM, equalization, and lane-master handshakes. The TX power-control groups define P0, P0S, P1, and P2 state bitmaps for analog reference generation, VCM hold, analog/word clocks, reset, serial enable, digital clock, data enable, RX detect, VBOOST, and DCC compensation calibration. Power-up timer groups split timing values across several 16-bit words.

Lane 0 also includes debug and measurement-oriented surfaces: DCC bank address/data/control and DAC range/selection/ack/address fields, TX clock alignment, LBERT control, RX match and statistic counters, RX sample counts, calibration compare clock control, statistic stop, analog TX override outputs, termination-code override outputs, TX equalization override outputs, analog status, TX DCC DAC override outputs, and analog TX measurement/power/ATB/misc registers.

Lane 1 begins a corresponding lane-local surface. This slice covers its lane/TX/RX override inputs, RX equalization inputs, TX/RX ASIC inputs and outputs, CDR/VCO controls, OCLA enable bits, P0/P0S/P1/P2 TX power-state bitmaps, and the first TX power-up timing fields. The lane 1 timer group is incomplete in this chunk and continues in the next work item.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior appears only when AMD display code includes the generated header and uses the constants through register access helpers for MMIO or indexed CR register transactions.

The field names imply several hardware-controlled state machines and handshakes:

- Common PLL bring-up and clocking: MPLLA/MPLLB enable, divider, HDMI clock, VCO frequency, fractional-N, SSC, lock status, stable timers, calibration, DAC output, and power-control status fields describe PLL sequencing and readback.
- Supervisor analog readiness: bandgap, prescaler, RTUNE, reference-clock detect, calibration force, acknowledge, and measurement fields expose common analog setup that must be valid before lane traffic is reliable.
- Lane TX/RX sequencing: TX/RX request, reset, pstate, rate, data-enable, clock-enable, serial-enable, RX detect, signal-detect, adaptation-disable/request, termination, VREF, and CDR/VCO fields describe PHY lane mode changes and power transitions.
- Override workflows: repeated value plus `*_OVRD_EN` fields allow driver, firmware, validation, or recovery code to force hardware-facing values instead of using state-machine generated values.
- Measurement and debug: ATB/OCLA/LBERT, RX statistic counters, match masks, sample counts, DCC DAC control/readback, and analog status fields support hardware validation and fault isolation.

No software persistence is implemented here. Hardware register contents persist according to the ASIC reset, power, and clock domains. Fields named `*_STAT`, `*_STATUS`, `*_OUT`, `*_ACK`, `*_DONE`, or `*_ASIC_OUT` are readback-oriented by name, while `*_OVRD_IN`, `*_OVRD_EN`, `*_ASIC_IN`, timer, calibration, and config fields are control-oriented by name; actual read/write semantics must come from the hardware register database and driver access policy.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk pairs with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides the matching `ix...` and `mm...` register offsets for this shift/mask namespace.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`. That resource file builds DCN316 DPCS register, shift, and mask tables using `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`. This chunk contains many lower-level CR1 PHY fields beyond the small high-level link encoder tables, but all of them share the same generated DPCS 4.2.3 namespace available to display, PHY bring-up, diagnostics, and hardware validation code.

Related integration points include:

- AMD DCN316 link encoder resource initialization and register table generation.
- DCN31-style DIO link encoder helpers that consume DPCS register lists and shift/mask lists.
- HPO DP link encoder paths for RDPCS/DPCS register access patterns on DCN3.x hardware.
- DisplayPort and HDMI link training, link-rate changes, lane power-state changes, suspend/resume, hotplug recovery, RX detect, PLL lock, SSC programming, and debug/validation flows.
- Firmware-assisted or lab-only flows that force supervisor or lane override bits to recover or inspect PHY state.

## Risks

- Generated-header drift is the main risk. An incorrect shift or mask can silently write an adjacent analog, PLL, lane power, or override bit during a read-modify-write sequence.
- The chunk mixes shared supervisor resources with lane-local controls. A bug in MPLL, bandgap, RTUNE, prescaler, or reference-clock fields can affect all lanes served by CR1, while lane 0/1 mistakes can appear as lane-dependent failures.
- Override-enable fields are common. Setting an override value without its matching enable bit has no intended effect, while leaving an enable bit asserted after diagnostics or recovery can hold the PHY in a forced state across later link training or resume.
- Many fields are timing or calibration values split across multiple registers, such as SSC peak/step-size and TX power-up timing. Partial updates or inconsistent high/low halves can create unstable analog behavior.
- Status/readback fields and control fields are represented identically as macros. Consumers must know which registers are writable, read-only, sticky, clear-on-read, or reserved from the hardware specification.
- Reserved and broad full-width masks give C code little semantic protection. Values should come from generated tables, firmware contracts, or hardware-approved sequences rather than ad hoc driver calculations.
- This slice starts and ends at chunk boundaries inside register groups. Merge-time validation should account for the previous `PRESCALER_OVRD_IN` definitions and the next `LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_3` mask definitions before flagging missing pairs.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN316 targets that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static generation checks that every complete register in the full `dpcs_4_2_3_sh_mask.h` file has matching `__SHIFT` and `_MASK` definitions, with chunk-boundary exceptions for the tail of `PRESCALER_OVRD_IN` and the start of `LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_3`.
- Cross-check this header against the DPCS 4.2.3 register database and matching `dpcs_4_2_3_offset.h` register names.
- Grep or compile checks for DPCS fields consumed by `dcn316_resource.c`, DCN31 DIO link encoder tables, and HPO DP link encoder helpers.
- Hardware tests on DCN316/DPCS 4.2.3-class ASICs: DP and HDMI link training, link-rate changes, lane power-state transitions, hotplug, suspend/resume, RX detect, signal-detect behavior, PLL lock, SSC programming, RTUNE/bandgap readiness, and recovery after failed link training.
- Register readback during bring-up to confirm MPLL lock/status, RTUNE status, bandgap/reference-clock behavior, TX power-state transitions, DCC DAC acknowledgements, RX statistic counters, and cleanup of override-enable bits.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 24313-26724 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should cover the beginning of CR1 and the missing `DPCSSYS_CR1_SUP_DIG_PRESCALER_OVRD_IN` shifts and early masks. Later chunks should continue `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_3` and the rest of lane 1 plus later DPCS 4.2.3 register groups. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMD display PHY programming, not as handwritten runtime logic.
