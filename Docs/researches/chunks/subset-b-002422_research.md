# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 87515-89938

## Scope And Purpose

This chunk covers a generated AMD GPU display register bitfield header for the DPCS 4.2.3 block. The file does not define executable code. It defines preprocessor constants for bit shifts and masks used to pack, update, and decode fields in DPCSSYS CR4 raw-lane registers. These registers are part of the AMD display PHY/link-encoder control surface used by the DCN 3.1.6 resource code through the matching `dpcs_4_2_3_offset.h` register-address header.

The covered range is source-tree aligned to the CR4 raw-lane section of the header. It starts in the middle of `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_3`, covers the rest of raw lane 0, covers a full raw lane 1 slice, and then covers the beginning of raw lane 2 through the first line of `DPCSSYS_CR4_RAWLANE2_DIG_FSM_FAST_RX_REFLVL_CAL`. Neighboring chunks are needed for the beginning of lane 0 and the rest of lane 2.

The macros describe low-level link/PHY behavior: PCS transmit and receive request/acknowledge handshakes, power states, link rates and widths, RX adaptation and equalization, TX/RX termination, loopback control, PMA overrides, per-lane FSM status, interrupt status and clear bits, and factory/ATE override paths. The constants are hardware contract data. Correctness depends on matching the ASIC register specification exactly.

## Important APIs, Types, And Macros

There are no C functions, structures, or callable APIs in this range. The important interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, generally within a 16-bit register payload in this chunk.
- Comment lines such as `//DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_RX_PCS_IN` group the following shift and mask constants under a register name.

The principal register families in this chunk are:

- `DPCSSYS_CR4_RAWLANE*_DIG_PCS_XF_*`: PCS transfer-interface fields for TX/RX input commands, override input, output acknowledge/status, lane number, ATE controls, RX equalization, phase-two calibration, and terminal control.
- `DPCSSYS_CR4_RAWLANE*_DIG_FSM_*`: per-lane FSM override, memory-address monitor, status monitor, fast calibration/adaptation bypass controls, common calibration status, lock state, DCC flags/status, OCLA controls, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE*_DIG_IRQ_CTL_*`: per-lane interrupt status, clear, and mask bits for reset, request, rate, power-state, adaptation, phase-two calibration, loopback, DCC-on-demand, and TX request/reset events.
- `DPCSSYS_CR4_RAWLANE*_DIG_PMA_XF_*`: PMA sideband and override fields for lane MPLL enable, supervisor state, TX/RX request/reset/data-enable controls, lane RTUNE, MPHY PWM/async controls, and RX adaptation output mapping.
- `DPCSSYS_CR4_RAWLANE*_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANE*_DIG_RX_CTL_*`: local TX/RX controller controls and status fields, including TX FSM timing, TX clock control, continuous DCC status, RX FSM enable, LOS mask timing, RX data-enable override timing, offcan/adapt continuous status, and UPCS OCLA data/clock enables.

Important field groups include:

- Link command fields: `RESET`, `REQ`, `ACK`, `RATE`, `WIDTH`, `PSTATE`, `LPD`, `MPLLB_SEL`, `MPLL_EN`, and `DETRX_REQ`.
- Override enable/value pairs: many registers use adjacent `_OVRD_VAL` and `_OVRD_EN` fields, for example reset/request, VCO/ref load values, TX beacon, loopback, data-enable, async data, PMA request/reset, and RX/TX termination.
- RX adaptation and equalization fields: `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `ADAPT_REQ`, `ADAPT_CONT`, `OFFCAN_CONT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `EQ_ATT_LVL`, `EQ_VGA1_GAIN`, `EQ_VGA2_GAIN`, `EQ_CTLE_BOOST`, `EQ_CTLE_POLE`, `EQ_DFE_TAP1`, and the RX EQ override registers.
- Calibration and FSM fields: `FSM_JMP_ADDR`, `FSM_JMP_EN`, `FSM_CMD_START`, `FSM_OVRD_EN`, `FSM_BREAK`, `STATE`, `CMD_RDY`, `ALU_OVFLW`, `WAIT_CNT_EQ0`, `FAST_RX_*`, `FAST_TX_*`, `CMNCAL_*`, `CR_REG_LOCK`, and `CR_MEM_LOCK`.
- Interrupt fields: status registers expose single-bit event indications, clear registers expose matching clear bits, and `IRQ_MASK`/`IRQ_MASK_2` expose mask fields for the same classes of events.

## Control Flow And Runtime Use

This header has no runtime control flow by itself. Its control path is compile-time macro expansion:

1. `dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. DC resource macros such as `DPCS_DCN31_REG_LIST(id)` populate static register-address tables for each link encoder instance.
3. Mask/shift list macros such as `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` populate static shift and mask tables.
4. Runtime display code uses the generated register tables through the AMD DC register helper layer, for example `REG_GET`, `REG_UPDATE`, and related macros, so field operations compile into address plus mask/shift read-modify-write sequences.

At runtime, these constants participate indirectly in link encoder and PHY operations. The driver can assert or deassert resets, request lane state changes, configure rate/width/power-state fields, enable MPLL or async paths, tune VCO/ref load values, poll `ACK` and FSM status fields, mask/clear IRQs, and read calibration/adaptation status. The actual sequencing logic lives in AMD display link encoder, resource, IRQ, and PHY code; this chunk supplies the bit layout those sequences depend on.

The chunk boundary matters for control-flow understanding. For raw lane 0, the first complete control group visible here begins at `RX_PCS_IN`, but the preceding `RX_OVRD_IN`, `RX_OVRD_IN_1`, and `RX_OVRD_IN_2` definitions begin before this range. For raw lane 2, the range ends before the FSM fast-calibration group is complete. The merge lane should reconcile neighboring chunks before describing complete CR4 raw-lane coverage.

## State And Persistence Behavior

The header defines immutable compile-time constants. It has no local state, allocation, locking, I/O, firmware messaging, or persistence behavior. The values persist only as compiled constants in the kernel object files that include the header through DCN 3.1.6 resource code.

The hardware registers described by these macros are stateful. Writes through the AMD DC register helper layer can change PHY/lane state, trigger request/acknowledge handshakes, enable override paths, mask interrupts, clear latched interrupt status, and alter calibration or adaptation behavior. Status fields such as `ACK`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `FSM_STATUS_MON`, calibration done bits, DCC status, and PMA acknowledge bits reflect hardware state rather than software-owned memory.

Several register categories have side-effect-prone semantics:

- Clear registers such as `*_IRQ_CLR` are likely write-one or write-value clear paths, so wrong masks can drop or fail to clear interrupts.
- Override enable fields can force hardware values away from firmware/FSM controlled behavior.
- FSM override fields can force command starts, jumps, and breaks.
- ATE override registers can bypass normal link training and production control paths.

Because this is a generated hardware-contract header, persistence risk is mostly source persistence: manual edits can permanently desynchronize checked-in constants from the ASIC specification or generated offset headers.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which supplies the corresponding register addresses such as the `ixDPCSSYS_CR4_RAWLANE*_...` definitions. The shift/mask macros in this file are useful only when paired with those addresses.

The primary source integration point found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes this header and the offset header. That file defines DPCS base segments for DCN 3.1.6 and builds static link encoder register, shift, and mask tables.

The macros also fit the broader AMD DC register abstraction:

- `reg_helper.h` supplies field access helpers used by display code.
- DCN link encoder headers define register and field list macros, including DPCS list composition.
- Runtime code in the display core operates on generated tables rather than spelling these CR4 raw-lane macros at every call site.

The covered CR4 raw-lane definitions are part of a repeated pattern across `CR0` through `CR4` and across `RAWLANE0` through later raw lanes. Consistency with adjacent generated DPCS versions such as `dpcs_4_2_2_*` and with other same-family `dpcs_4_2_3_*` chunks is an important integration signal.

## Risks And Edge Cases

Bit layout errors are high impact. A single wrong shift or mask can redirect a write to a reserved bit or to a neighboring control field, potentially causing link bring-up failures, bad DisplayPort/PHY state transitions, unstable RX adaptation, missed interrupts, or difficult-to-debug lane-specific failures.

The repeated lane pattern creates copy/paste and generation risks. Raw lanes 0, 1, and 2 have mostly parallel field definitions, but this chunk is not aligned to full lane boundaries. Automated validation should compare repeated field layouts while accounting for the partial first and last register groups in this range.

Reserved fields are explicitly defined. Driver writes must preserve reserved bits during read-modify-write operations. Using a full literal write instead of mask/shift helpers on these registers could modify reserved bits and violate hardware requirements.

Override and ATE fields are especially risky. Enabling `_OVRD_EN` fields without matching value fields, or leaving ATE override bits set after diagnostics, can force RX/TX reset, request, data-enable, adaptation, loopback, termination, MPLL, or async behavior outside the normal FSM sequence.

Interrupt status, clear, and mask definitions must remain paired. Mismatches between `*_IRQ`, `*_IRQ_CLR`, and `IRQ_MASK` fields can cause storms, lost events, or stuck status bits, especially for reset/request/rate/pstate/adaptation events that affect link state changes.

FSM override and status fields have debug or bring-up semantics. Incorrect use of `FSM_JMP_ADDR`, `FSM_CMD_START`, `FSM_OVRD_EN`, or `FSM_BREAK` can interrupt lane state machines. Status fields such as `WRMSK_DISABLED` and `RDMSK_DISABLED` need correct interpretation because they report whether the FSM is honoring memory/register masks.

The suffix values in this chunk use 16-bit-looking masks with an `L` suffix, while other generated DPCS headers sometimes use 32-bit-formatted masks. Consumers should treat them as unsigned register-field masks through the established helper macros rather than assuming a particular C integer width.

## Test Signals

Build coverage should include AMD display configurations that compile `dcn316_resource.c`, because that translation unit includes `dpcs_4_2_3_sh_mask.h` and instantiates the relevant DPCS mask/shift tables.

Static validation should check every `__SHIFT` and `_MASK` pair in the chunk for internal consistency: masks should align with shifts, non-reserved fields should not overlap within a register, and reserved masks should fill the unused bits indicated by the field list.

Generated-header validation should compare this file against the authoritative AMD register-generation source, if available, and against the matching `dpcs_4_2_3_offset.h` register list. The CR4 raw-lane register names in the mask header should have corresponding offset entries.

Lane-pattern validation should compare equivalent raw-lane 0, 1, and 2 registers after normalizing the lane number. Differences should be explained by the chunk boundary or by actual hardware deltas, not accidental text drift.

Runtime hardware test signals include successful display link bring-up on DCN 3.1.6 systems, stable DisplayPort rate/width changes, clean hotplug and IRQ handling, correct reset/request acknowledge polling, and absence of RX adaptation or equalization errors during link training.

Diagnostic tests that exercise PHY overrides, loopback, ATE paths, or fast calibration controls should verify that override enable bits are cleared after use and that normal FSM-controlled link operation resumes.

Because this chunk includes many interrupt clear/mask fields, regression tests should watch for stuck IRQ status, repeated IRQ firing after clear, and missing interrupt-driven link state transitions.
