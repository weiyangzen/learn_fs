# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 100128-102481

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for the `DPCSSYS_CR4` register block. It covers 2,354 lines and defines 2,141 preprocessor constants: 1,072 `__SHIFT` macros and 1,069 `_MASK` macros. The slight mismatch is expected for this sliced range because it starts inside `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` and ends inside `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN`.

The content is declarative only. It contains no functions, structs, enums, branches, loops, runtime variables, allocation, locking, or persistence code. Its public surface is a large set of C preprocessor constants that describe bit positions and bit masks for 16-bit internal DPCS registers.

## Purpose

The header gives AMDGPU display code symbolic names for DPCS 4.2.0 hardware register fields. Driver code can combine these `*_SHIFT` and `*_MASK` constants with companion register addresses from `dpcs_4_2_0_offset.h` and AMD register access helpers to build read-modify-write operations without hard-coding field locations.

This chunk specifically covers the CR4 lane-template area beginning after the lane override register, including ASIC-facing TX/RX override and input/output fields, TX/RX power control, TX DCC controls, TX clock alignment, RX VCO/CDR/adaptation/status controls, MPHY controls, analog override/status windows, analog TX/RX register fields, two raw memory identifiers, and the beginning of the `RAWLANEX_DIG_PCS_XF` TX/RX crossbar register family.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace. Most complete fields appear as a pair:

- `DPCSSYS_CR4_*__FIELD__SHIFT` gives the bit offset.
- `DPCSSYS_CR4_*__FIELD_MASK` gives the field mask, usually within a 16-bit register value.

Important macro families in this range:

- `DPCSSYS_CR4_LANEX_DIG_ASIC_*`: ASIC-facing lane, TX, RX, RX EQ, RX CDR/VCO, output, OCLA, and override fields. These expose request, acknowledgement, reset, rate, width, power state, data enable, loopback, beacon, DETRX, clock-ready, low-power detect, CDR tracking, RX alignment, RX VCO/ref load, RX EQ, TX pre/main/post cursor, async drive, VBOOST/IBOOST, and debug output fields.
- `DPCSSYS_CR4_LANEX_DIG_TX_PWRCTL_*`: TX power-state fields for P0, P0S, P1, and P2, TX power-up timing fields, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment control, and TX LBERT control.
- `DPCSSYS_CR4_LANEX_DIG_RX_PWRCTL_*`: RX power-state and power-up timing fields for P0/P0S/P1/P2 and power sequencing.
- `DPCSSYS_CR4_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, and status fields, including calibration request, clock/data selectors, FSM status, reference and VCO load values, low-frequency indication, and done/busy-style status.
- `DPCSSYS_CR4_LANEX_DIG_RX_CDR_*` and `RX_DPLL_*`: RX CDR control/status and DPLL frequency/bounds fields for lock tracking, SSC/filter configuration, frequency readback, and lock-related diagnostics.
- `DPCSSYS_CR4_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, ATT/VGA/CTLE/DFE tap status, data/error slicer offsets, slicer controls, DAC select controls, and CR-bank access fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_STAT_*`: RX statistic/match machinery, including data masks, match controls, statistic controls, sample count, statistic counters, calibration comparator clock control, match extensions, and stop control.
- `DPCSSYS_CR4_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock stable count fields.
- `DPCSSYS_CR4_LANEX_DIG_ANA_*`: digital views of analog TX/RX override outputs and controls, including TX termination code, TX EQ, RX control/power/VCO, RX calibration/DAC/AFE/CTLE/scope/slicer/IQ phase, analog status, MPHY override, signal detect, and TX DCC DAC override fields.
- `DPCSSYS_CR4_LANEX_ANA_*`: analog TX/RX register fields for TX override measurement, power override, alt bus, ATB, DCC DAC/control, termination code, override clock, miscellaneous TX registers, RX clock/CDR/deserializer/slicer/power/squelch/calibration/ATB/force/reserved registers.
- `DPCSSYS_CR4_RAWMEM_DIG_ROM_CMN0_B0_R0` and `DPCSSYS_CR4_RAWMEM_DIG_RAM_CMN0_B0_R0`: raw memory bitfield definitions for ROM and RAM access words.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_*`: beginning of raw lane PCS crossbar TX/RX override and input/output fields, covering TX reset/request/DETRX/VBOOST/IBOOST/beacon, TX pstate/LPD/width/rate/MPLL selection, TX acknowledgement and DETRX result, RX rate/width/pstate/LPD/adaptation/data enable/loopback/LOS threshold, RX VCO/ref load overrides, and the start of RX PCS input fields.

## Register Areas Covered

The ASIC override group maps values crossing between the ASIC control side and the lane digital/analog PHY. It provides paired value and override-enable bits for many controls, plus readback fields for acknowledgement and status. TX fields cover request, power state, link rate/width, MPLL B selection, data enable, main/pre/post cursor, async drive, HDMI mode, clock ready, detect-RX, inversion, low-power detect, DC coupling, extended FIFO, MPHY mode, reset, VBOOST, IBOOST, beacon, and TX enable/ack state. RX fields cover request, data enable, power state, link rate/width, RX reference/VCO load values, CDR VCO low-frequency state, CDR tracking and SSC, alignment, clock shift, disable, low-power detect, reset, RX DC coupling, RX LOS/LFPS thresholds, RX data/clock valid, RX EQ adaptation and force state, VCO/ref IQ calibration values, and RX output status.

The TX power-control group defines per-state parameters and wake-up timing. It includes coefficients and completion counters for TX P-states, explicit power-up timing slots, and DCC DAC programming fields. These are the bit definitions a driver or hardware bring-up path would use to tune TX low-power transitions, DCC calibration, and test modes.

The RX power, VCO, CDR, DPLL, and adaptation groups define the receive-side bring-up and calibration contract. They include RX P-state values, power-up timing, VCO calibration requests and status readbacks, CDR tracking/filter/frequency controls, DPLL frequency bounds, adaptation configuration registers, adaptation reset, equalizer/DFE tap status, slicer offsets, DAC control selection, and CR-bank indirection fields.

The RX statistic group exposes hardware match/count infrastructure. It defines masks, match controls, statistic controls, sample count, multiple statistic counter segments, calibration comparator clock control, additional match controls, and stop control. This is primarily diagnostic or validation-oriented rather than normal link-policy logic.

The analog/MPHY groups provide a digital register description for lower-level analog controls and observability. They include TX and RX analog override outputs, TX termination and EQ controls, RX analog power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ controls, analog status, MPHY override, signal-detect override, analog test bus controls, DCC controls, RX clock/CDR/deserializer/squelch/power/calibration, and reserved analog registers.

The raw memory and raw PCS crossbar section begins a lower-level view of the CR4 lane interface. The raw PCS TX/RX groups mirror many of the ASIC-facing concepts using explicit override-value and override-enable fields, plus PCS input/output status. This chunk ends before the RX PCS input group is complete.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior comes from the AMDGPU display driver code that selects these masks and from the DPCS hardware state machines that consume or expose the underlying register bits.

The field names imply these hardware state patterns:

- TX/RX request and acknowledgement handshakes: `REQ`, `RESET`, `ACK`, `TX_ACK`, `RX_ACK`, `EN_*`, and `*_OVRD_EN` fields describe state-machine requests, forced values, and observed completions.
- Link mode and power transitions: `PSTATE`, `RATE`, `WIDTH`, `LPD`, `DATA_EN`, `MPLLB_SEL`, `MPLL_EN`, TX/RX P-state registers, and power-up timing fields are the low-level representation of link rate/lane configuration and low-power entry/exit.
- Calibration and adaptation: VCO/ref load values, CDR controls, DPLL frequency fields, RX AFE/DFE adaptation controls, CTLE/VGA/DFE status, slicer offsets, TX DCC DAC controls, TX EQ cursor fields, and IQ phase fields expose calibration commands and readbacks.
- Debug, test, and manufacturing paths: OCLA, LBERT, RX statistic counters, ATB, scope, MPHY, analog override, raw memory, and CR-bank fields provide observability or forced settings that can bypass normal hardware sequencing.
- Interrupt-like status is not directly represented as a full IRQ block in this chunk, but status/ack/clear-style fields exist in several controller and calibration groups. The header does not encode access semantics such as write-one-to-clear; consumers must rely on the hardware spec and register helper conventions.

No software state is persisted here. Hardware register contents persist only according to ASIC reset, power-domain, firmware, and display-engine sequencing. Reserved fields are explicitly represented by masks and should be preserved by read-modify-write users.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.0 register database that generated this file and the companion `dpcs_4_2_0_offset.h` address map.

Within this source tree, `dpcs_4_2_0_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` together with `dpcs_4_2_0_offset.h`. The offset header maps the `DPCSSYS_CR4_LANEX_DIG_ASIC_*` window starting at internal addresses around `0x9000`, the TX power-control area around `0x9020`, RX power/VCO/CDR/adaptation/stat areas around `0x9040` through `0x9090`, analog lane areas after that, and the raw PCS crossbar fields in the CR4 raw-lane namespace.

Integration points visible from the names include AMD DC link encoder and PHY programming, DisplayPort/HDMI link training, lane rate/width changes, power-management and suspend/resume flows, TX/RX calibration, receiver equalization, DCC and VCO calibration, factory/ATE paths, debug capture through OCLA/LBERT/stat counters, and low-level PHY diagnostics using analog and raw crossbar registers.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target an adjacent hardware field during a register update.
- The chunk contains many override value bits adjacent to override enable bits. Setting a value without its enable bit has no intended effect; leaving an enable bit asserted after debug or test use can force hardware away from normal state-machine control.
- Several fields are calibration-sensitive: CDR, DPLL, VCO, DCC, TX EQ, RX adaptation, CTLE/VGA/DFE, slicer, and IQ phase values can destabilize link training or signal integrity if stale or misprogrammed.
- Reserved masks cover large bit ranges. Drivers should preserve reserved bits and avoid treating them as writable scratch space.
- The `LANEX` and `RAWLANEX` naming means this is a lane-template namespace, not a single obvious physical lane from the name alone. Consumers need the companion offset/addressing scheme to select the correct instance.
- The range starts and ends inside logical register groups. Merge/reconciliation should not assume `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` or `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` are fully described by this chunk alone.
- Many diagnostic and analog override fields are powerful enough to interfere with normal display operation, hotplug handling, and power sequencing if used outside controlled bring-up or validation paths.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.1 code that includes `dpcs_4_2_0_sh_mask.h` through `dcn31_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,072 shifts and 1,069 masks because the line range crosses group boundaries.
- Consistency checks against `dpcs_4_2_0_offset.h` so every complete register-family prefix in this chunk has a corresponding `ixDPCSSYS_CR4_*` address define.
- Generated-register comparison against adjacent DPCS versions or regenerated headers to catch accidental field-width, reserved-bit, suffix, or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.0: DisplayPort and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, TX/RX request-ack transitions, TX/RX calibration, DCC, VCO/CDR/DPLL behavior, RX adaptation/equalization, and link recovery.
- Debug/validation readbacks should show plausible transitions for TX/RX P-state programming, power-up timing, reset/request acknowledgements, VCO calibration status, CDR lock/frequency status, adaptation status, DFE/CTLE/VGA status, TX DCC acknowledgement, statistic counters, OCLA/LBERT signals, and raw PCS crossbar acknowledgements.

## Chunk Notes For Merge

This document intentionally covers only lines 100128-102481 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should include the CR4 supervisor/supply and the beginning of `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0`; later chunks should complete `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` and continue the raw lane register families. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.0 rather than handwritten driver logic, with `dcn31_resource.c` and the matching offset header as primary in-tree integration anchors.
