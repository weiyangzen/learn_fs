# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 1-2433

## Purpose

This chunk is the opening slice of a generated AMD DPCS 3.1.4 register shift/mask header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for DisplayPort/PHY control-system registers under the `dpcssys_cr0_rdpcstxcrind` address block.

The range starts with the MIT license and include guard, then defines 2,158 `#define` lines: 1,099 `__SHIFT` macros and 1,075 `_MASK` macros. It covers the CR0 supervisor PLL/reference-clock/control families, RTUNE and bandgap/reference timing controls, lane 0 TX/status/analog controls, and the beginning of lane 1 TX/RX controls. The chunk ends mid-register at `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, with only its first three masks included; the remaining masks continue after line 2433.

Although this file is stored under a local `ceph-client` source mirror, it is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct MMIO accesses in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, clear, or update that field.

Major register families in this chunk:

- `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, MPLLA/MPLLB divider and HDMI-clock override registers, and `MPLLA/MPLLB_OVRD_IN_*`: reference clock selection, reference-clock range, bandgap enable, HDMI mode, MPLL enable, TX clock dividers, VCO frequency, standby, calibration, fractional-N controls, SSC peak/stepsize, fractional quotient/remainder/denominator, and charge-pump settings.
- `DPCSSYS_CR0_SUP_DIG_*_ASIC_IN*`: ASIC-driven versions of the MPLLA/MPLLB, divider, HDMI, supervisor, level, bandgap, and charge-pump control inputs. These mirror many override fields without the override-enable bits.
- `DPCSSYS_CR0_SUP_DIG_MPLLA/MPLLB_MPLL_PWR_CTL_*`: MPLL power-controller override, state/status, DAC max range, lock/stable timers, PCLK enable/disable timers, calibration override, analog DAC output, and SSC spread-type control.
- `DPCSSYS_CR0_SUP_DIG_CLK_RST_*` and `RTUNE_*`: bandgap/reference power-up timing, reference VPHUD, resistor-tuning configuration/status, RX/TX set values and status values, RTUNE timing counters, and TX calibration code.
- `DPCSSYS_CR0_SUP_DIG_ANA_*`: analog output controls and status for MPLLA/MPLLB clocks, resets, output enables, charge-pump values, RTUNE output, bandgap output, and PMIX overrides.
- `DPCSSYS_CR0_LANE0_*`: lane 0 lane-loopback controls, TX override input/output fields, ASIC TX inputs/outputs, RX status output, master-lane and digital-clock coordination fields, TX power-state P0/P0S/P1/P2 programming, TX power-up timing, DCC DAC/bank access, clock-alignment, LBERT control, RX statistic/match/counter controls, analog TX override/status, TX termination/equalization/DCC DAC controls, and reserved analog TX registers.
- `DPCSSYS_CR0_LANE1_*`: lane 1 lane-loopback controls, TX override input/output fields, RX override input/equalization fields, ASIC TX/RX inputs/outputs, RX CDR/VCO inputs, OCLA enable, TX power-state/timing/DCC/clock-align/LBERT controls, and the start of RX power-state P0.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU Display Core and hardware-sequencing code:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Register-helper macros and ASIC-specific tables combine matching offsets with these field masks and shifts.
3. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to program or read hardware bitfields.
4. The constants in this chunk determine which CR0 supervisor, PLL, lane TX/RX, analog, DCC, statistic, and diagnostic bits are touched during link bring-up, training, power-state transitions, PHY tuning, and diagnostics.

The macros do not encode programming order. Consumers must still follow hardware sequencing for reference-clock and bandgap bring-up, MPLL power and lock polling, RTUNE request/ack handshakes, lane power-state changes, TX/RX reset ordering, DCC DAC programming, analog equalization updates, statistic counter sampling, and status/acknowledge reads.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-backed DPCS state:

- Supervisor state includes reference-clock source/range, bandgap enable/state, prescaler controls, RTUNE request/ack/status, level controls, and reference/bandgap power-up timers.
- PLL state includes MPLLA/MPLLB enable, dividers, HDMI/div clocks, VCO and fractional-N settings, SSC parameters, charge-pump values, power-controller FSM state, lock status, calibration state, DAC values, and stable/lock timers.
- Lane TX state includes request/ack, data enable, P-state/rate/width, MPLL selection, main/pre/post cursor values, beacon, async drive, detect-RX request/result, clock-ready, reset, low-power disable, DC coupling, FIFO mode, MPHY mode, lane-master coordination, power-state programming, DCC DAC access, clock alignment, LBERT mode, analog TX controls, termination code, equalization pull/dir fields, DCC calibration, and analog status.
- Lane RX state in this range includes RX override/ASIC input fields for request, data enable, reset, polarity, P-state/rate/width, adaptation controls, CDR tracking/SSC, alignment, term controls, PWM and termination low-current controls, CDR/VCO load values, RX output status, and lane 1 RX P0 power-state fields at the boundary.
- Diagnostic state includes RX statistic sample/count/match controls for lane 0, DCC DAC acknowledge/address/data fields, LBERT pattern/error-trigger controls, and OCLA clock/data enables for lane 1.

Persistence is hardware-defined. Configuration fields generally survive until rewritten, reset, power-gated, suspend/resume reinitialized, or GPU reset. Status, acknowledgement, request, done, calibration, counter, and self-clearing fields may be transient, sticky, write-one-to-clear, read-only, or valid only while their clock/power domains are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` provides matching `ixDPCSSYS_*` register offsets for the field-bearing registers in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes both `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, making this slice part of the DCN 3.1.4 display resource/register interface.
- Shared AMD display register helpers included by the resource code, especially `reg_helper.h`, consume these generated masks and shifts through register-field tables and token-pasted field names.

Behaviorally, this chunk sits at the PHY/link integration boundary for DCN 3.1.4 display output. It supports register access for reference clocks, MPLL A/B programming, HDMI/DP clocking, lane TX/RX control, analog TX/RX tuning, DCC/RTUNE calibration, link-test diagnostics, and per-lane power sequencing.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while updating the wrong hardware bit.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the offset header, silicon documentation, and firmware or display-core assumptions.
- The chunk boundary is artificial. The final register, `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, is incomplete in this slice; the merge lane needs the following chunk before making full claims about lane 1 RX P0 power-state masks.
- Many fields are override pairs where a value bit is adjacent to an `*_OVRD_EN` bit. Confusing the two can leave hardware using ASIC defaults, force stale debug values, or unexpectedly override autonomous PHY control.
- PLL and clock fields are link-critical. Incorrect MPLL enable/divider/VCO/fractional/SSC/charge-pump masks can cause link-training failure, unstable clocks, HDMI timing errors, blank displays, or power-state hangs.
- Power-controller and timer masks affect sequencing. Bad lock/stable/PCLK/power-down timer fields can create resume-only failures, intermittent link bring-up, or calibration races.
- RTUNE and DCC calibration fields affect analog signal quality. Incorrect request/ack, set-value, DAC, range, selector, or calibration-control masks can produce poor eye margins, RX detect failures, or misleading calibration status.
- Lane TX/RX override and ASIC fields are repeated across lanes but not completely symmetric in this range. Testing only lane 0 could miss lane 1-specific RX override, CDR/VCO, OCLA, or RX power-state mistakes.
- Diagnostic fields such as statistics counters, LBERT, OCLA, and analog status are easy to treat as harmless, but bad masks can corrupt test setup or hide link-quality failures.
- Reserved-field masks are present throughout the chunk. Consumers should preserve reserved bits unless the hardware specification explicitly requires a value; this header does not describe reset values or side effects.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.1.4 display/link behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed DPCS macros should surface in resource/register-table construction around `dcn314_resource.c`.
- Cross-check this range against `dpcs_3_1_4_offset.h` so every field-bearing `DPCSSYS_CR0_*` register in the slice has the expected matching `ixDPCSSYS_CR0_*` offset.
- Mechanically verify paired `_MASK` and `__SHIFT` definitions for all complete registers in the range, while allowing the known boundary exception at `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`.
- Diff the slice against AMD's authoritative DPCS 3.1.4 register database or a trusted generated source. Repeated MPLLA/MPLLB and lane0/lane1 register families should match expected hardware schemas.
- Exercise display link bring-up across supported DP/HDMI modes, including high-rate modes, suspend/resume, hot replug, and GPU reset. Watch for link-training failures, blanking, PLL lock timeouts, and clock instability.
- Exercise lane power-state transitions P0/P0S/P1/P2, RX detect, low-power entry/exit, and reset sequencing on all available lanes.
- Run PHY tuning and calibration paths that touch RTUNE, DCC DAC, TX main/pre/post cursor, TX termination, equalization, CDR/VCO, and analog status fields. Expected signals are stable link margins and sane calibration acknowledgements.
- Use diagnostics where available: lane statistics counters, LBERT patterns/error injection, OCLA enable, analog status readback, and DCC DAC acknowledge/address/data paths.
- Monitor kernel logs and display-debug traces for AUX/link-training failures, PLL lock or calibration timeout messages, intermittent resume issues, lane-specific failures, and connector modes that only fail under HDMI mode or high data rates.

## Cross-Chunk Notes

This chunk owns the start of `dpcs_3_1_4_sh_mask.h`: license, include guard, the `dpcssys_cr0_rdpcstxcrind` address-block comment, all early CR0 supervisor/MPLL/RTUNE definitions, complete lane 0 TX/status/analog groups in this range, and the beginning of lane 1 TX/RX groups. It ends after `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0__RESERVED_1_MASK`; the following chunk must provide the rest of that register and later lane 1 RX power/control definitions before the final per-file report summarizes complete DPCS 3.1.4 coverage.
