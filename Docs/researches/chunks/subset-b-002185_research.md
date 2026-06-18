# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h chunk subset-b-002185

## Scope

- Source: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`
- Lines: 83889-86300
- Chunk role: generated shift/mask metadata for DCN 4.1.0 DPCS PHY register fields. The chunk begins inside the `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` definition, then covers CR0 lane analog, raw-lane PCS/PMA/FSM/IRQ fields, and crosses at line 85052 into the `dpcssys_cr1_rdpcstxcrind` address block for CR1 supervisor PLL, RTUNE, bandgap, and clock/reset fields.

## Purpose

This header chunk defines C preprocessor constants used by AMDGPU DCN code to pack and unpack hardware register fields. Each register field is represented by a `__SHIFT` macro and a matching `__MASK` macro, normally with 16-bit masks such as `0x0001L`, `0x00FFL`, or `0xFFFFL`. These constants are not executable logic; they are the hardware/software ABI that lets register access helpers update only the intended bits.

The CR0 part describes one lane-side PHY control surface: analog RX ATB measurement, VDAC/CDR/VREG tuning, PCS transmit and receive handshakes, override paths, ATE/test overrides, RX equalization and phase calibration, raw-lane FSM acceleration/status, IRQ status/clear/mask registers, PMA lane/supervisor/TX/RX override paths, TX/RX control status, and master MPLL loop/test controls.

The CR1 part describes a supervisor/common PHY control surface: ID code registers, reference clock override, MPLLA/MPLLB divider and HDMI clock controls, MPLLA/MPLLB frequency/SSC/fractional-N/charge-pump overrides and ASIC inputs, supervisor override/ASIC state handshakes, level/bandgap controls, analog prescaler/RTUNE/VREF/MPLL analog controls, MPLLA/MPLLB power-control status/timers/calibration, clock reset timing, and RTUNE config/status/set-value fields.

## Important Definitions

- `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS*`, `DPCSSYS_CR0_LANEX_ANA_RX_VDAC_RANGE`, `DPCSSYS_CR0_LANEX_ANA_RX_CDR_VREG`, and `DPCSSYS_CR0_LANEX_ANA_RX_VREG_CTRL` expose analog RX measurement and tuning fields, including ATB muxes, VDAC ranges, CDR VCO/vreg controls, and reserved high byte masks.
- `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_*` and `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_RX_*` define PCS cross-interface input/output, override, data enable, reset/request, rate/width/pstate, loopback, beacon, async, RX adaptation, figure-of-merit, TX pre/main/post direction, lane number, equalization, termination, and PH2 calibration fields.
- `DPCSSYS_CR0_RAWLANEX_DIG_FSM_*` defines lane FSM override/status and fast-calibration enables. Notable fields include FSM jump/command/break controls, command-ready and ALU/wait status bits, fast startup/adapt/AFE/DFE/VCO/reflvl/IQ calibration enables, common calibration status, continuous calibration/adaptation gates, CR register/memory locks, TX DCC flags/status, OCLA enables, TX EQ update flag, common RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*` defines one-bit IRQ status and clear fields for RX reset/request/rate/pstate/adapt/PH2 calibration/loopback/DCC and TX reset/request events, plus `IRQ_MASK` and `IRQ_MASK_2` fields to gate those events.
- `DPCSSYS_CR0_RAWLANEX_DIG_PMA_XF_*` defines PMA cross-interface override/status fields for MPLLA/MPLLB lane enables, supervisor state, TX/RX request/reset/data-enable, beacon/async/clock-sync, serial/parallel loopback, RTUNE request/ack, MPHY PWM/termination overrides, RX IQ phase adjust map, and PMA input acks.
- `DPCSSYS_CR0_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANEX_DIG_RX_CTL_*` expose TX/RX FSM timing, clock/DCC/OCLA controls, loss-of-signal mask, RX data-enable override, off-can/adapt continuous status, and UPCS OCLA fields.
- `DPCSSYS_CR1_SUP_DIG_*` starts at the `dpcssys_cr1_rdpcstxcrind` address block and defines supervisor digital fields for IDCODE, reference clock override, MPLLA/MPLLB divider and HDMI clocks, PLL frequency/SSC/fractional-N and charge-pump programming, supervisor state/RTUNE/level overrides, ASIC input mirrors, PMA version ID, PLL power-control timers/status/calibration, clock/reset timing, and RTUNE config/status/set value.
- `DPCSSYS_CR1_SUP_ANA_*` defines analog supervisor fields for prescaler, RTUNE, bandgap, switch-power measurement, pre-regulator/VREF generation, MPLL AB miscellaneous controls, MPLL override/ATB, control-vreg, output-clock, lock, main PLL counters, PMIX, and related reserved fields.

## API and Type Surface

There are no functions, structs, enums, or runtime types in this range. The API is the macro naming contract:

- Register prefix: `DPCSSYS_CR0_...` or `DPCSSYS_CR1_...`.
- Field separator: `REGISTER__FIELD`.
- Bit position macro: `REGISTER__FIELD__SHIFT`.
- Bit mask macro: `REGISTER__FIELD_MASK`.

These macros are consumed by AMDGPU display register helpers and generated register tables elsewhere in the DCN driver. Typical call sites use the paired shift and mask to build read-modify-write values or to decode hardware state. The file must therefore remain synchronized with the matching address/header definitions for `dcn_4_1_0`.

## Control Flow

This chunk has no C control flow. The operational flow appears in the driver code that includes this header:

1. Driver code selects a DCN 4.1.0 register address from the matching address header.
2. A register access helper reads or prepares a register value.
3. The helper clears bits using a `__MASK` macro, shifts the caller-provided field value by the matching `__SHIFT`, and writes the resulting field value.
4. For status paths, the helper masks and shifts hardware values back into software-visible fields.

Hardware-level sequencing is implied by field names. Examples include reset/request/ack handshakes in PCS/PMA registers, IRQ status followed by `*_CLR`, fast calibration flags feeding raw-lane FSM behavior, and MPLLA/MPLLB power-control timers/status used around PLL enable, lock, calibration, and clock distribution.

## State and Persistence

The file itself persists no state. It describes hardware-backed state that can be latched in DCN PHY registers:

- Volatile status bits: IRQ status, `ACK`, `DONE`, `LOCK`, FSM state, DCC status, RTUNE status, adaptation/off-can status, and calibration status.
- Configuration bits: PLL dividers, fractional-N quotients/remainders/denominators, SSC peak/stepsize, charge-pump settings, vref/vswing/termination, power timing, fast-start options, and clock/reset control.
- Override enable/value pairs: many fields are paired as `*_OVRD_VAL` plus `*_OVRD_EN`, or as a value plus an `*_EN` bit. Writing an override-enable bit changes whether hardware uses a forced software value or its normal internal/ASIC-driven path.
- Reserved and `NC` masks: these document bit positions that should normally be preserved across read-modify-write operations. Accidentally writing reserved high-byte masks such as `0xFF00L`, `0xF000L`, or `0xFFFEL` can perturb undefined hardware behavior.

## Dependencies and Integration Points

- Depends on the generated DCN 4.1.0 register-address headers that provide the actual register offsets for the same `DPCSSYS_*` register names.
- Integrated by AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DCN register programming layers that use generated `*_sh_mask.h` files to map semantic field names to hardware bitfields.
- The CR0 raw-lane fields integrate with link bring-up, PHY calibration, DisplayPort/HDMI lane mode transitions, IRQ handling, ATE/test hooks, loopback paths, and RX/TX equalization logic.
- The CR1 supervisor fields integrate with common PLL and reference clock management shared across lanes, including MPLLA/MPLLB programming, spread-spectrum clocking, RTUNE, bandgap/reference generation, and power-up/down timing.
- Merge-time context is required for the first register in this chunk because lines 83889-83903 continue `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` from the previous chunk rather than starting at that register's first field.

## Risks

- Any shift/mask mismatch can corrupt adjacent PHY fields. This is especially risky for dense 16-bit registers that pack unrelated control, status, override-enable, and reserved bits into the same word.
- The many value/enable override pairs create a semantic risk: setting only the value or only the enable bit can leave hardware in normal mode or force stale values.
- IRQ and clear registers use similar names but different side effects. Confusing `*_IRQ`, `*_IRQ_CLR`, and `*_IRQ_MSK` fields can either miss events or accidentally acknowledge them.
- Status-like fields and writable control fields are mixed in adjacent blocks. Call sites should avoid assuming all fields under one prefix are safe to write.
- CR0 lane-specific and CR1 supervisor/common prefixes look similar but affect different hardware scopes. Using a CR1 common PLL/RTUNE field where lane-local behavior was intended can affect multiple lanes or clock consumers.
- Reserved masks are explicit and large in many registers. Code generation or manual updates must preserve reserved-field masks and avoid write-one patterns unless the hardware specification says otherwise.
- This header is generated hardware metadata; manual edits without regenerating from the authoritative register database can silently desynchronize DCN code from silicon documentation.

## Test Signals

- Build coverage: compile AMDGPU/DCN code with this header included; missing or renamed macros should fail at compile time in register programming tables or `REG_FIELD` uses.
- Static consistency checks: verify every field has a paired `__SHIFT` and `_MASK`, masks align with shifts and field widths, and no two non-reserved fields unintentionally overlap within a register.
- Hardware/link validation: DisplayPort and HDMI link bring-up across rates/widths/pstates should exercise PCS/PMA reset/request/ack, PLL programming, lane power, and TX/RX data enable fields.
- Interrupt validation: trigger RX/TX reset/request/rate/adapt/PH2/DCC events and verify status, mask, and clear behavior through the IRQ control fields.
- PHY calibration validation: observe RTUNE, DCC, VCO, VREF, AFE/DFE, IQ, continuous adaptation, and MPLL lock/status paths during warm boot, hotplug, link retrain, suspend/resume, and low-power transitions.
- Register dump comparison: compare programmed values against the DCN 4.1.0 hardware register specification, especially MPLLA/MPLLB fractional-N, SSC, charge-pump, power timer, bandgap, and reserved-bit behavior.
