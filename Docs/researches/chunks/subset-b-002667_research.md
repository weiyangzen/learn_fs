# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 1-2461

## Purpose

This chunk is the opening portion of AMD's generated GC 9.4.2 shader/register field mask header. It provides C preprocessor constants for bitfield positions and masks used by the AMDGPU driver when composing, reading, and decoding 32-bit graphics core registers. The file begins with an MIT-style AMD copyright/license block and include guard `_gc_9_4_2_SH_MASK_HEADER`, then defines register field metadata for the `didtind`, `gc_cpdec`, and the beginning of `gc_cppdec` address blocks.

The content is declarative rather than executable: every register field is represented as a pair of constants named like `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. These constants are consumed by register access code elsewhere in the AMDGPU stack, normally together with companion register offset headers and helper macros that shift and mask values before MMIO/indirect register writes or after reads.

## Major Register Areas Covered

The `didtind` address block dominates the first half of the chunk. It describes dynamic power/throttling fields for shader and fixed-function graphics blocks: `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, and `DIDT_TCP_*`. The repeated register families cover DIDT enable/reset/clock override bits, high-power thresholds, tuning controls, stall delays, stall pattern programming, MPD scale factors, throttle release controls, EDC enable/status/overflow fields, rolling power delta values, stall event counters, PCC performance counters, and EDC thresholds. The same layout pattern appears across SQ, DB, TD, and TCP, which lets common power-management code apply similar programming sequences to multiple graphics subblocks while using block-specific register names.

The `gc_cpdec` address block starts the command processor decode/status portion. It defines fields for CPC/CPF status and busy/stalled state, GRBM free counts, private violation addresses, MEC controls/header dumps, scratch index/data access, CE/DE counters, broad CP stalled/busy/stat registers, instruction pointers, context/preemption state, ring read pointers, queue thresholds, queue availability, command index/data, ROQ/STQ/MEQ/CEQ status registers, and private violation address decoding. These fields are mostly diagnostics and control-plane visibility for the graphics command processor pipeline.

The `gc_cppdec` address block begins near the end of the chunk. It covers CP wait and synchronization controls, CPC interrupt information and address/PASID reporting, virtualization status, graphics error state, UTCL1 controls/errors, AQL status, ring buffer base/control/read/write pointer fields, interrupt control/status fields, device ID, pipe/ring priority counters and priorities, fatal error reporting, VMID selection, doorbell controls/ranges, ring active bits, and per-ring interrupt enable/status definitions. The chunk ends mid-definition at `CP_INT_STATUS_RING2__GENERIC1_INT_STAT__SHIFT`, so later chunks complete this register.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or callable APIs in this chunk. The exported interface is the macro namespace itself:

- `*_SHIFT` constants define the least-significant bit offset for a field.
- `*_MASK` constants define the unshifted 32-bit bitmask for the field's occupied bits.
- Register comments such as `//DIDT_SQ_CTRL0` and address block comments such as `// addressBlock: didtind` act as generated grouping metadata for readers and tooling.

Driver code commonly uses these constants through local AMD register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, read/modify/write helpers, and direct bitwise expressions. The macros therefore form part of the hardware ABI binding for GC 9.4.2; a wrong value can silently program the wrong hardware bit.

## Control Flow

This header has no runtime control flow. Its effective "flow" is compile-time inclusion:

1. A C source file includes the GC 9.4.2 register headers for offsets and masks.
2. Code selects a register field macro by ASIC generation and register name.
3. Compile-time constants are folded into register values used for MMIO or indirect register access.
4. Hardware state changes happen only in the including code that reads or writes the registers.

The repeated DIDT register families imply expected external control sequences: enable or reset DIDT/EDC, program thresholds, stall patterns, weights, scale factors, delays, and throttle policies, then observe status/counter/overflow fields. The CP register families imply external flows for ring setup, doorbell programming, interrupt enable/status handling, VMID selection, queue monitoring, preemption, and fault/error diagnosis.

## State and Persistence Behavior

The header itself stores no state and has no persistence behavior. The state described by its macros lives in GPU hardware registers:

- DIDT and EDC fields represent power-management configuration, live throttle/finite-state-machine state, rolling power deltas, stall counters, overflow counters, and performance counters.
- CP fields represent command processor queues, rings, read/write pointers, doorbell range/control state, VMID assignment, interrupt enable/status bits, privilege/fatal error state, UTCL1 error reporting, and busy/stall diagnostic state.

Persistence is hardware- and driver-lifecycle dependent. Values programmed through these masks can persist until reset, suspend/resume reinitialization, GPU reset, power-gating, or later driver writes. Because the file contains only field definitions, it does not enforce reset ordering, locking, cache coherency, or read-clear/write-one-to-clear semantics; those constraints must be handled by the caller and hardware documentation.

## Dependencies and Integration Points

This header depends only on the C preprocessor and its include guard. It is intended to be paired with nearby generated GC 9.4.2 headers that define register offsets, base indices, and default values. Integration points include:

- AMDGPU graphics IP initialization and power-management code that programs DIDT/EDC throttling fields.
- Command processor setup paths for ring buffer bases, ring sizes, read/write pointers, VMIDs, doorbells, and active state.
- Interrupt setup/handling code that enables and decodes `CP_INT_CNTL*` and `CP_INT_STATUS*` bits.
- Fault and hang diagnostics that decode busy, stalled, private violation, UTCL1, fatal error, and instruction-pointer registers.
- Virtualization/SRIOV or partitioned GPU paths that inspect CP virtualization status, PASID, VMID, and doorbell ranges.

The naming convention must remain synchronized with AMD's generated register database and with consumers that use token-pasting helper macros. Renaming a macro is an API break for driver code even if the numeric value is unchanged.

## Risks and Edge Cases

The main risk is register definition drift. If a mask or shift does not match GC 9.4.2 hardware, the driver can enable the wrong throttle behavior, fail to clear or report interrupts, corrupt ring pointer programming, misdecode a fault, or write reserved bits. These failures can appear as hangs, power-management instability, missed interrupts, or misleading diagnostics rather than immediate compile failures.

Several risks are specific to this kind of generated header:

- Repeated register layouts across SQ/DB/TD/TCP and ring0/ring1/ring2 make copy-generation errors easy to miss in review.
- Full-width masks such as `0xFFFFFFFFL` require callers to avoid unintended sign/width conversions on unusual build targets, although the kernel normally uses fixed-width register access types.
- Some fields are status/counter/overflow/error bits, while others are control bits; this file does not encode access type, side effects, write-one-to-clear behavior, or reset values.
- The chunk boundary stops in the middle of `CP_INT_STATUS_RING2`, so a partial analysis or generated report must not assume the register is complete here.
- Address block comments are not machine-enforced, so consumers must include the matching offset header and use the correct access path, especially for indirect DIDT registers versus normal CP registers.

## Test Signals

Useful validation signals are mostly compile-time and hardware-behavior oriented:

- Kernel builds that include GC 9.4.2 AMDGPU paths should compile without missing macro errors.
- Register helper unit/build checks should verify that representative `SHIFT` and `MASK` pairs round-trip through field set/get macros.
- Hardware bring-up or CI on GC 9.4.2 devices should confirm DIDT/EDC programming does not cause throttle stalls, power-limit regressions, or counter overflows outside expected workload behavior.
- Command processor tests should exercise ring setup, doorbells, write pointers, VMID programming, queue thresholds, interrupts, and hang/fault recovery.
- Diagnostic tests should compare decoded CP busy/stalled/status/error bits against known fault injection or firmware/hardware traces.
- Static checks can compare this generated header against the authoritative AMD register database to catch changed masks, missing fields, duplicated names, or incomplete per-ring/per-block families.
