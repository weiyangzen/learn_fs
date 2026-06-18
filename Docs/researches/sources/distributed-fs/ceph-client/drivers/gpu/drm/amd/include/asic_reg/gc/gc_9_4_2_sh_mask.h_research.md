# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002667`: lines 1-2461, `Docs/researches/chunks/subset-b-002667_research.md`
- `subset-b-002668`: lines 2462-4871, `Docs/researches/chunks/subset-b-002668_research.md`
- `subset-b-002669`: lines 4872-7289, `Docs/researches/chunks/subset-b-002669_research.md`
- `subset-b-002670`: lines 7290-9799, `Docs/researches/chunks/subset-b-002670_research.md`
- `subset-b-002671`: lines 9800-12226, `Docs/researches/chunks/subset-b-002671_research.md`
- `subset-b-002672`: lines 12227-14836, `Docs/researches/chunks/subset-b-002672_research.md`
- `subset-b-002673`: lines 14837-17355, `Docs/researches/chunks/subset-b-002673_research.md`
- `subset-b-002674`: lines 17356-19701, `Docs/researches/chunks/subset-b-002674_research.md`
- `subset-b-002675`: lines 19702-22065, `Docs/researches/chunks/subset-b-002675_research.md`
- `subset-b-002676`: lines 22066-24623, `Docs/researches/chunks/subset-b-002676_research.md`
- `subset-b-002677`: lines 24624-27042, `Docs/researches/chunks/subset-b-002677_research.md`
- `subset-b-002678`: lines 27043-29425, `Docs/researches/chunks/subset-b-002678_research.md`
- `subset-b-002679`: lines 29426-31946, `Docs/researches/chunks/subset-b-002679_research.md`
- `subset-b-002680`: lines 31947-33003, `Docs/researches/chunks/subset-b-002680_research.md`

## Chunk Research

### subset-b-002667: lines 1-2461

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

### subset-b-002668: lines 2462-4871

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 2462-4871

## Scope And Purpose

This chunk is a declarative register-field map for the AMD GC 9.4.2 graphics IP block, used by the Aldebaran-era amdgpu/KFD driver code. It contains only preprocessor constants: each hardware register field is represented as a `__SHIFT` macro and a matching `_MASK` macro. Runtime code combines these names through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` from `amdgpu.h`, which token-paste `REG__FIELD__SHIFT` and `REG__FIELD_MASK`.

The slice begins in the middle of `CP_INT_STATUS_RING2` and ends in the first three shift macros of `GCEA_ADDRDEC_MISC_CFG`, so both boundaries depend on neighboring chunks for complete per-register coverage. Within the slice, the main areas are command processor interrupt/control state, command processor queue/HQD state, DIDT indirection registers, and GCEA DRAM/effective-address routing controls.

## Important APIs, Types, And Register Groups

There are no C functions or types in this chunk. The important API surface is the macro naming contract:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
- `REG_SET_FIELD(orig, reg, field, val)` clears the mask and inserts `val << shift`.
- `REG_GET_FIELD(value, reg, field)` extracts `(value & mask) >> shift`.

Major register groups covered here:

- `CP_*_F32_INTERRUPT`, `CP_MEC*_F32_INTERRUPT`, and `CP_MEC*_F32_INT_DIS`: command processor F32, MEC, ECC, GPF, queue-message, wave-restore, SUA-violation, and fatal-EDC interrupt bit definitions.
- `CP_ME{1,2}_PIPE{0..3}_INT_CNTL`, matching `*_INT_STATUS`, and `CP_ME{1,2}_INT_STAT_DEBUG`: compute pipe interrupt enable, latched status, and debug-assertion fields for query-status, dequeue, ECC, GPF, WRM timeout, privileged access, opcode, timestamp, reserved-bit, and generic interrupt causes.
- `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME*`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, and `CP_PQ_STATUS`: control bits for command-processor power, memory sleep/deep sleep, context handling, VMID reset/preempt/status, and packet-queue status.
- `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CP_CPC_IC_*`, `CP_CPC_GFX_CNTL`: command processor controller interrupt, instruction-cache, and graphics-control fields.
- `CP_RB_DOORBELL_CONTROL_SCH_{0..7}`, `CP_RB_DOORBELL_CLEAR`, `CP_RB_STATUS`: scheduler ring-buffer doorbell offsets, enable/hit/update bits, and doorbell clear masks.
- `CPF/CPG/CPC/DC_*_CNT`, `CP_*_DSM_CNTL*`, and `CP_EDC_FUE_CNTL`: EDC counters, dynamic/static memory/error injection controls, and fatal uncorrectable error masking/flagging.
- `CP_GFX_MQD_*`, `CP_MQD_*`, `CP_HQD_*`: memory queue descriptor and hardware queue descriptor fields for VMID, privilege, execution disable, cache policy, queue activation, pipe/queue priority, quantum, PQ/IB/EOP base addresses, read/write pointers, doorbell control, dequeue requests, offload, scheduler/status/control, context-save addresses, GDS resource state, AQL control, and HQD error causes.
- `DIDT_IND_INDEX`, `DIDT_IND_DATA`, `DIDT_INDEX_AUTO_INCR_EN`: indirect register selector/data/autoincrement fields for dynamic instruction/dynamic throttling tables.
- `GCEA_DRAM_*`: graphics client effective-address DRAM read/write client-to-group mappings, group-to-VC mappings, lazy thresholds, CAM depth/reorder controls, page-burst limits, priority aging/queueing/fixed/urgency coefficients, and quantum thresholds.
- `GCEA_ADDRNORM_*`, `GCEA_ADDRNORMDRAM/GMI_*`, `GCEA_ADDRDEC_BANK_CFG`, and the start of `GCEA_ADDRDEC_MISC_CFG`: address range validity, legacy MMIO hole handling, interleave topology, base/limit/offset values, DRAM/GMI hole controls, NP2 channel sizing, and bank/channel/chip-select decode knobs.

## Control Flow And Runtime Behavior

This header has no executable control flow. Control flow appears in consumers that:

1. Include `gc_9_4_2_offset.h` for register addresses and this `gc_9_4_2_sh_mask.h` file for field layout.
2. Build register values with `REG_SET_FIELD()` or direct mask/shift operations.
3. Access hardware through MMIO helpers such as `RREG32`, `WREG32`, `WREG32_RLC`, `SOC15_REG_OFFSET`, and RLC-mediated register access.

For this exact ASIC generation, `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` include this header directly. The broader amdgpu/KFD queue code uses the same `CP_HQD_*` and `CP_HQD_PQ_*` field names to initialize MQDs, program doorbell offsets, activate queues, issue dequeue requests, and poll for queue teardown. Interrupt setup paths use `CP_ME1_PIPE*_INT_CNTL`/status fields to enable and classify compute pipe events. RAS paths use nearby GCEA and CP EDC status/counter fields to identify and clear error state.

## State And Persistence Behavior

The state represented by these macros is hardware state, not software-owned persistence:

- Interrupt enable/status fields persist in MMIO registers until hardware or driver writes update or clear them.
- MQD/HQD fields describe queue identity and lifecycle state: active bit, VMID, queue priority, PQ/IB/EOP base addresses, read/write pointers, doorbell routing, dequeue requests, context-save addresses, AQL controls, and error flags.
- EDC and FUE fields expose persistent hardware error counters, injection configuration, and fatal-error flags until counters/status are cleared or reset.
- GCEA DRAM and address-normalization fields affect address routing, interleaving, DRAM/GMI hole behavior, client priority, and reorder behavior while programmed.
- Power, memory sleep, soft-reset-adjacent, and VMID controls affect hardware engine state across runtime transitions, reset, suspend/resume, and queue preemption.

The header itself stores no values. Its correctness determines whether software writes the intended hardware bits.

## Dependencies And Integration Points

Primary dependencies are:

- Companion generated files such as `gc_9_4_2_offset.h`, which define the `reg...` addresses referenced by consumers.
- `amdgpu.h` field helpers that depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings.
- SOC15 access helpers and register entry macros, including `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD`.
- GFX 9.4.2 amdgpu implementation code in `gfx_v9_4_2.c`, including golden settings, RAS/EDC counter handling, GCEA error handling, and GC programming paths.
- Aldebaran KFD integration in `amdgpu_amdkfd_aldebaran.c`, which includes this ASIC register layout for KFD/debug interaction with GC hardware.
- Common KFD MQD/HQD management code for GFX generations, which relies on `CP_HQD_*` masks and shifts when constructing queue descriptors and programming active queues.

The source-tree alignment is important: this is GPU driver hardware metadata inside the vendored Ceph-client Linux tree, not Ceph filesystem logic.

## Risks And Edge Cases

- Off-by-one or stale mask/shift values can silently corrupt unrelated bits in privileged MMIO registers, causing hangs, lost interrupts, incorrect queue scheduling, bad VMID assignment, or broken RAS reporting.
- The chunk starts and ends mid-register. Any generated report for only this slice must not claim complete coverage for `CP_INT_STATUS_RING2` or `GCEA_ADDRDEC_MISC_CFG`.
- Many pipe and queue registers are repeated with identical layouts. Copy/paste or generation drift between `CP_ME1`/`CP_ME2`, pipe indices, and status/control variants can leave one queue path misprogrammed while others work.
- Address-bearing fields have alignment encoded in their low-bit shifts and masks, for example base-address fields shifted by 2, 3, or 12 bits. Misinterpreting these as byte-granular values can produce invalid queue, EOP, IB, or address-normalization programming.
- Doorbell fields combine enable, mode, source, hit, and large offset fields. Incorrect masking can route doorbells to the wrong queue or leave queues unresponsive.
- EDC/FUE and DSM injection controls are diagnostic and fault-handling sensitive; accidentally enabling injection or masking fatal errors would make test and production behavior diverge.
- GCEA address-normalization and address-decode fields control memory fabric routing. Bad base/limit/interleave/hole settings risk memory access failures that surface far from the write site.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for files that include `gc_9_4_2_sh_mask.h`, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, catches missing or renamed macros.
- Queue lifecycle tests should exercise MQD/HQD load, active polling, doorbell update, dequeue/destroy, read/write pointer reporting, IB execution, and EOP event handling.
- KFD compute tests should cover user queues, kernel queues, VMID assignment, priority/quantum settings, and debug trap/watchpoint flows on Aldebaran/GC 9.4.2 hardware.
- Interrupt tests should confirm CP/MEC/CPC interrupt enable and status bits produce expected IRQ handling for dequeue, timestamp, ECC, GPF, opcode, privileged register/instruction, and reserved-bit conditions.
- RAS tests should inject or observe EDC/FUE events and verify counters, first-occurrence fields, clear paths, and fatal masking behavior.
- Suspend/resume, GPU reset, and preemption tests should verify that persistent HQD, VMID, doorbell, and error state is reprogrammed or cleared correctly.
- Performance and stress tests that vary memory traffic are the practical signal for GCEA priority, CAM, page-burst, and address-normalization programming regressions.

### subset-b-002669: lines 4872-7289

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 4872-7289

## Purpose

This chunk is a generated ASIC register field header for the AMD GC 9.4.2 graphics block. It does not contain executable C logic; it defines `__SHIFT` and `_MASK` constants that describe bit layouts for memory-address decode, graphics-cache/power-control, error-detection, performance-counter, and GDS/GDSP registers. Driver code combines these constants with the matching register offsets from `gc_9_4_2_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`.

The slice contains 2,418 source lines, 2,171 `#define` entries, and 236 register/comment block markers. It starts in the middle of `GCEA_ADDRDEC_MISC_CFG`, then covers complete groups for GCEA address decoding and IO scheduling, GCEA perf/EDC/DSM control, GC CAC/DIDT/throttling/EDC, GDS protection and counters, and the beginning of per-VMID GDS/GWS/OA partition registers.

## Important Register Groups And Fields

The `GCEA_ADDRDEC*` section describes the graphics engine address decoder. `GCEA_ADDRDECDRAM_HARVEST_ENABLE` and `GCEA_ADDRDECGMI_HARVEST_ENABLE` provide force-enable/value bits for harvested address bits `B3` through `B5`. The repeated `GCEA_ADDRDEC{0,1,2}_...` groups define three decoder instances, each with base address registers for primary chip-selects `CS0` through `CS3` and secondary chip-selects `SECCS0` through `SECCS3`, address masks for `CS01`/`CS23` and secondary pairs, and detailed address mapping fields. Those mapping fields include bank group count, row/column layout, bank selectors, channel-bit selectors, column selectors `COL0` through `COL15`, row-major selectors, and row-MSB inversion controls. The matching offset header maps these fields to registers around `regGCEA_ADDRDEC0_BASE_ADDR_CS0` at `0x0a5f`, through `regGCEA_ADDRDEC2_RM_SEL_SECCS23` at `0x0aac`.

`GCEA_ADDRNORM*` and `GCEA_IO_*` define normalization and client arbitration controls. The IO maps assign read/write clients to groups (`GCEA_IO_RD_CLI2GRP_MAP0/1`, `GCEA_IO_WR_CLI2GRP_MAP0/1`), define combine-flush behavior, group burst sizing, read/write priority aging, queueing, fixed priority, urgency, urgency masks, and quantum settings for priorities 1 through 3. These constants represent low-level memory-system scheduling policy rather than normal kernel data structures.

The GCEA perf/EDC/DSM region includes `GCEA_MISC`, `GCEA_LATENCY_SAMPLING`, performance counter low/high result registers, counter configuration registers, result control, EDC counters (`GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, `GCEA_EDC_CNT3`), DSM controls, crossbar credit and max-burst knobs, probe controls/map, error status, DRAM-bank arbitration, and address-decoder select. These fields are diagnostic and reliability surfaces: they count or configure hardware events, expose ECC/EDC state, and control built-in scan/debug modes.

`GCEA_CGTT_CLK_CTRL` belongs to the power-decode address block and exposes clock-gating control/status style bits for the GCEA area. It is separate from the main base-index-0 GC register ranges; the matching offset header marks it with base index 1.

The `GC_CAC*`, `GC_DIDT*`, `GC_THROTTLE*`, and `GC_EDC*` section describes compute activity counting, dynamic current/power management, throttling, and graphics-core error detection. Important fields include CAC aggregation controls, CAC indirect index/data access, DIDT enables and weights, throttle pattern/program step controls, power-brake fields, EDC status/overflow/threshold controls, and rolling power delta reporting. `gfx_v9_4_2_set_power_brake_sequence()` directly uses `GC_THROTTLE_CTRL1__PWRBRK_STALL_EN_*` through `REG_SET_FIELD(tmp, GC_THROTTLE_CTRL1, PWRBRK_STALL_EN, 1)` before writing `regGC_THROTTLE_CTRL1`.

The `GDS_*` section covers Global Data Share configuration, status, protection faults, virtual-memory protection faults, EDC counters, DSM controls, and a work-distributor GDS CSB register. `GDS_CONFIG` describes capacity/layout knobs; `GDS_CNTL_STATUS` includes status and control bits; `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` expose fault address/status fields; and `GDS_EDC_*` registers track EDC events across GDS, GRBM, OA, PHY, and pipe paths.

The `gc_gdspdec` part begins the per-VMID partition table. `GDS_VMID0_BASE` through `GDS_VMID15_BASE` expose 16-bit base fields, paired `GDS_VMID0_SIZE` through `GDS_VMID15_SIZE` expose 17-bit sizes, and `GDS_GWS_VMID0` through `GDS_GWS_VMID15` pack a 6-bit GWS base with a size field at bit 16. The chunk ends at `GDS_OA_VMID9`; the remaining OA VMID masks continue after this slice. Other GFX generations use the same register pattern in init and command-submission paths, so these constants define the ABI between KFD/AMDGPU queue setup and hardware VMID-local GDS/GWS/OA allocation.

## APIs, Types, And Integration Points

There are no functions, structs, enums, or storage objects in this chunk. The public interface is the macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the raw 32-bit register value.
- Register addresses are intentionally not in this file; they come from `gc_9_4_2_offset.h` as `reg<REGISTER>` constants and `reg<REGISTER>_BASE_IDX`.

The principal consumer is `drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which includes both `gc/gc_9_4_2_offset.h` and this header. The AMDGPU SOC15 register helpers combine the offset constants with these masks. `REG_SET_FIELD` depends on exact macro spelling, so a field rename or mask mismatch is a compile-time or silent hardware-programming risk depending on which macro is affected.

Cross-version integration is also important. Similar macro groups appear in `gc_9_0_sh_mask.h`, `gc_9_2_1_sh_mask.h`, `gc_9_4_3_sh_mask.h`, and later GC 10/11 headers, but fields are not perfectly identical. For example, the GC 9.4.2 `GC_THROTTLE_CTRL1` layout contains `PATTERN_EXTEND_*`, `FP_PATTERN_CLAMP_EN`, and `PWRBRK_STALL_EN`, while some later headers use different power-brake program-min/max fields. Version-specific source must include the matching header pair.

## Control Flow And State

This header has no runtime control flow. Its constants are consumed by control flow in AMDGPU initialization, RAS, power management, debug, and queue/GDS setup paths. The typical sequence is:

1. Driver code selects the target SOC15 block/instance and, when needed, a shader/SE/VMID context.
2. Code reads or initializes a 32-bit register value.
3. `REG_SET_FIELD` or explicit shift/mask arithmetic inserts one of these field values.
4. `WREG32_SOC15`/`WREG32` writes the resulting register value to the GC block.

State is persistent in hardware registers rather than kernel-owned data. Address-decoder, arbitration, throttle, and GDS partition settings survive as device register state until reset, reinitialization, suspend/resume restoration, or another write changes them. Counter registers and fault/status registers reflect mutable hardware state and may be clear-on-write or latch-like depending on the hardware contract, which is not encoded in this header.

## Dependencies

The masks depend on the GC 9.4.2 register specification and must remain synchronized with:

- `gc_9_4_2_offset.h`, which supplies the register addresses and base indices for the same symbolic names.
- AMDGPU SOC15 register access helpers in the driver (`SOC15_REG_OFFSET`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_SOC15_OFFSET`).
- Field helper macros such as `REG_SET_FIELD`, which derive the shift and mask macro names from the register and field tokens.
- Firmware and hardware initialization expectations for GCEA, CAC/DIDT, EDC, and GDS blocks.

The file is independent of Ceph or distributed-filesystem logic despite residing under the repository's source mirror. It is part of the imported AMD Linux DRM driver tree.

## Risks

The main risk is silent hardware misprogramming. A wrong shift or mask can write a neighboring bitfield while leaving C compilation successful. The highest-risk groups are address decode (`GCEA_ADDRDEC*`), throttling/power brake (`GC_THROTTLE*`), and per-VMID GDS partitioning (`GDS_VMID*`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`) because they affect memory routing, power throttling behavior, and process/queue resource isolation.

The repeated register families are easy to update inconsistently. `GCEA_ADDRDEC0`, `GCEA_ADDRDEC1`, and `GCEA_ADDRDEC2` have nearly identical field layouts; a generator or manual patch that changes only one instance would create hard-to-debug ASIC-specific behavior. The same applies to the 16 VMID base/size/GWS/OA families.

Generated-header skew is another risk. If `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h` come from different hardware-description revisions, field updates may be paired with the wrong register addresses. Because the driver often builds register names from tokens, this can appear as correct source-level code while targeting an incorrect raw register or bit range.

The chunk boundary itself is a documentation risk: it starts after the first `GCEA_ADDRDEC_MISC_CFG` field definitions and ends before all `GDS_OA_VMID*` registers are listed. Any final per-file research should reconcile this chunk with adjacent chunks before claiming a complete register inventory.

## Test Signals

Useful build-time signals are successful compilation of GC 9.4.2 AMDGPU code and absence of `REG_SET_FIELD` macro-expansion failures for fields such as `GC_THROTTLE_CTRL1.PWRBRK_STALL_EN`, `GDS_GWS_VMID0.SIZE`, and GDS/GCEA EDC counters. A header-name or field-name mismatch should fail compilation where a field is used directly.

Runtime validation requires hardware or emulator coverage. Signals include successful GC 9.4.2 device initialization, stable suspend/resume, no GDS/GWS allocation faults under KFD/compute workloads, correct RAS/EDC counter reads for GDS and GCEA registers, and no unexpected GCEA address decode, GDS protection, or VM protection fault reports. For power-brake coverage, the `gfx_v9_4_2_set_power_brake_sequence()` path should program `regGC_THROTTLE_CTRL`, `regGC_THROTTLE_CTRL1`, and the CAC indirect power-brake stall pattern without register-access faults.

### subset-b-002670: lines 7290-9799

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 7290-9799

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.4.2 shader/mask register header. The covered range starts in the `GDS_OA_VMID9`/`GDS_OA_VMID10` area and continues through most of `SPI_BARYC_CNTL`, stopping at `SPI_BARYC_CNTL__POS_FLOAT_ULC_MASK`. The next line in the source file defines `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK`, so this chunk ends one line before the `SPI_BARYC_CNTL` family is fully complete.

The major register groups in this range are:

- GDS ordered-append VMID masks, GWS reset bits, ordered-append reset masks, GDS enhancement flags, and GDS context-switch counters.
- The start of `addressBlock: gc_gfxdec0`, including depth-buffer, stencil-buffer, HTILE, depth bounds, depth clear, and depth/stencil read/write base fields.
- Screen, window, generic, clip-rect, and viewport scissor fields, plus viewport depth range registers.
- Color-buffer target/shader masks and blend constant channels.
- Primitive assembler and scan-converter state such as raster config, tile steering, edge rules, hardware screen offsets, and grid fields.
- Command processor context selectors for perfmon context, pipe id, ring id, and VMID.
- Viewport transform registers, user clip-plane registers, programmable near clip Z, and pixel-shader input interpolation control.

The file is a generated hardware register bitfield map. This chunk defines C preprocessor constants only: there are no functions, structs, variables, persistence objects, or executable branches in the header itself.

## Purpose

The purpose of this header range is to provide the bit-level ABI between GC 9.4.2 hardware registers and AMDGPU/KFD code that composes or decodes register values. Each field is represented in the usual generated form:

- `<REGISTER>__<FIELD>__SHIFT`, giving the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, giving the 32-bit field mask.

The paired `gc_9_4_2_offset.h` file supplies register addresses such as `regGDS_GWS_RESET0`, `regDB_RENDER_CONTROL`, `regDB_Z_INFO`, `regPA_SC_VPORT_SCISSOR_0_TL`, and `regSPI_PS_INPUT_CNTL_0`; this header supplies the corresponding field layouts. Consumers combine these constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and packet-building code that writes context registers through command processor packets.

## Important Macro Families

### GDS VMID, Reset, and Context-Switch State

The chunk begins with ordered-append VMID masks for `GDS_OA_VMID9` through `GDS_OA_VMID15`, where the low 16 bits are a VMID-specific mask and the high 16 bits are marked unused. It then defines two 32-bit GWS reset banks:

- `GDS_GWS_RESET0__RESOURCE0_RESET` through `RESOURCE31_RESET`.
- `GDS_GWS_RESET1__RESOURCE32_RESET` through `RESOURCE63_RESET`.

`GDS_GWS_RESOURCE_RESET` provides a single-resource reset command style field with `RESET` plus an 8-bit `RESOURCE_ID`. `GDS_OA_RESET_MASK` and `GDS_OA_RESET` define reset selection for ordered-append resources by ME/pipe, including ME0 graphics/pixel/vertex/compute/geometry reset bits and ME1/ME2 pipe reset bits.

`GDS_ENHANCE` contains miscellaneous and control flags for GDS behavior, including auto-increment index, CGPG restore, read-buffer tag miss handling, GDSA/GDSO clock-gating disables, WD GDS CSB override, GDS clock enhance disable, DS memory clock gate disable, and unused high bits. `GDS_OA_CGPG_RESTORE` exposes ordered-append backup counters and `GDS_CS_CTXSW_STATUS` / `GDS_GFX_CTXSW_STATUS` expose context-save state such as `BUSY`, `GFX_OPCODE`, and `OA_STATE`.

The numerous `GDS_*_CTXSW_CNT*` registers share a simple layout: `UPDN` in bits 0-15 and `PTR` in bits 16-31. Covered variants exist for CS, VS, PS0 through PS7, and GS, with four counters per stage. These fields support GDS context-save/restore bookkeeping around graphics or compute context switches.

### Depth, Stencil, HTILE, and Render Override

The `gc_gfxdec0` section starts with DB register fields:

- `DB_RENDER_CONTROL` controls depth/stencil copy, resolve, decompress, resummarize, and tile-surface enable modes.
- `DB_COUNT_CONTROL` selects sample/rate behavior, Z-pass increment mode, perfect-Z-pass counting, and disabled sample detection.
- `DB_DEPTH_VIEW` defines slice start/max.
- `DB_RENDER_OVERRIDE` and `DB_RENDER_OVERRIDE2` carry force/disable/override controls for Z, stencil, HiZ, HiS, compression, sample counts, quad export, centroids, conservative Z export, decompression, and late-Z behavior.
- `DB_HTILE_DATA_BASE` and `_HI`, `DB_Z_READ_BASE`, `DB_Z_WRITE_BASE`, `DB_STENCIL_READ_BASE`, and `DB_STENCIL_WRITE_BASE` define low/high address fragments for depth/stencil and HTILE surfaces.
- `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_Z_INFO2`, and `DB_STENCIL_INFO2` define format, tiling, swizzle, compression, clear, metadata, TC compatibility, and related surface interpretation bits.
- `DB_DEPTH_SIZE`, `DB_DEPTH_BOUNDS_MIN`, `DB_DEPTH_BOUNDS_MAX`, `DB_STENCIL_CLEAR`, `DB_DEPTH_CLEAR`, and `DB_DFSM_CONTROL` define size, clear values, bounds, and depth/stencil state-machine control.

These fields are render-context state. They are normally programmed by command submissions or clear-state initialization, not by ordinary CPU-side persistent storage.

### Scissor, Clip, Raster, and Viewport State

The PA/SC portion defines many coordinate-packed registers:

- `PA_SC_SCREEN_SCISSOR_TL/BR`, `PA_SC_WINDOW_SCISSOR_TL/BR`, `PA_SC_GENERIC_SCISSOR_TL/BR`, and `PA_SC_VPORT_SCISSOR_0..15_TL/BR` use `TL_X`, `TL_Y`, `BR_X`, and `BR_Y` fields, with top-left registers also carrying a `WINDOW_OFFSET_DISABLE` bit where applicable.
- `PA_SC_WINDOW_OFFSET` and `PA_SU_HARDWARE_SCREEN_OFFSET` define signed or packed X/Y offsets.
- `PA_SC_CLIPRECT_0..3_TL/BR` and `PA_SC_CLIPRECT_RULE` define four clip rectangles and a 16-bit rule mask.
- `PA_SC_EDGERULE` packs `ER_TRI`, `ER_POINT`, `ER_RECT`, and four line edge-rule fields.
- `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15` provide full 32-bit min/max depth values for each viewport.
- `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE` describe raster pipe/bank mappings, shader-engine pairing, screen extent control, and tile steering override.
- `PA_SC_RIGHT_VERT_GRID`, `PA_SC_LEFT_VERT_GRID`, and `PA_SC_HORIZ_GRID` provide grid-offset and grid-count fields used by scan-converter setup.

These fields determine clipping, viewport extent, rasterization placement, and tile-to-pipe routing. The clearstate tables in this tree contain reset-like values for many of these names, for example `PA_SC_VPORT_SCISSOR_0_TL` through `PA_SC_VPORT_SCISSOR_15_BR` and default viewport Z min/max values in `clearstate_gfx10.h` and neighboring generation clearstate headers.

### Color Buffer Masks, Blend Constants, and CP Context Selectors

`CB_TARGET_MASK` and `CB_SHADER_MASK` expose four-bit channel write masks for up to eight MRTs. `CB_BLEND_RED`, `CB_BLEND_GREEN`, `CB_BLEND_BLUE`, and `CB_BLEND_ALPHA` define full-register blend constant values. `CB_DCC_CONTROL` controls DCC overwrite-combiner, independent block size, max compressed block size, max uncompressed block size, and related compatibility/control flags.

`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` define context selector fields used by CP-visible state. They are narrow registers, but wrong values can associate render or perfmon state with the wrong pipe, ring, or VMID.

### Viewport Transform and User Clip Planes

The `PA_CL_VPORT_*` families define viewport transform scale and offset registers for X, Y, and Z over viewport indices 0 through 15. Each is represented as a full 32-bit `DATA` field. The chunk also defines six user clip planes, `PA_CL_UCP_0_*` through `PA_CL_UCP_5_*`, with X/Y/Z/W components as full 32-bit fields, plus `PA_CL_PROG_NEAR_CLIP_Z`.

These are shader/raster interface state registers. Their bitfields are intentionally simple because they transport float or raw 32-bit payloads rather than sub-bit control fields.

### SPI Pixel-Shader Input and Interpolation State

`SPI_PS_INPUT_CNTL_0` through `SPI_PS_INPUT_CNTL_31` define pixel-shader input mapping and interpolation behavior. Inputs 0-19 include fields for `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PT_SPRITE_TEX`, `FP16_INTERP_MODE`, default attribute-1 behavior, and attribute validity. Inputs 20-31 have a related but slightly smaller layout that omits `ROTATE_PC_PTR` and `PT_SPRITE_TEX`, retaining offset/default/flat/dup/FP16/default-attr/valid bits. This split is easy to miss because the names are mechanically similar.

`SPI_VS_OUT_CONFIG` provides vertex-shader export count and half-pack control. `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` share fields for perspective, linear, pull-model, line stipple, position, front-face, ancillary, sample coverage, and fixed-point position inputs. `SPI_INTERP_CONTROL_0` controls flat shading, point-sprite enable, X/Y/Z/W point-sprite override selectors, and top-origin selection. `SPI_PS_IN_CONTROL` provides the number of interpolators, offchip parameter enable, late parameter-cache deallocation, and barycentric optimization disable. `SPI_BARYC_CNTL` starts at the end of the chunk and covers perspective/linear center and centroid controls, position float location, position upper-left-corner handling, and the shift for `FRONT_FACE_ALL_BITS`; its final mask line is outside this chunk.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It affects compiled driver behavior by determining how code and packet builders pack or unpack 32-bit MMIO/context-register values.

The state represented here lives in GPU hardware context registers and command-stream state, not in the header. Some fields are ordinary persistent context state, such as scissor rectangles, viewport transforms, depth/stencil formats, blend constants, and PS interpolation controls. Others are command-like or reset/control fields, especially GDS/GWS reset bits, `GDS_GWS_RESOURCE_RESET__RESET`, and `GDS_OA_RESET__RESET`.

The DB, PA/SC, PA/CL, CB, and SPI fields are generally part of graphics context state that can be saved/restored by CP/RLC mechanisms or reset through clearstate programming. GDS context-switch counters and status fields are hardware bookkeeping for context save/restore. The macros do not describe sequencing, hazards, polling, or write-one-to-clear behavior; those rules have to come from the hardware specification and the driver paths that program the registers.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `gc_9_4_2_offset.h` supplies the register numbers and base indices for the names in this mask header.
- `gc_9_4_2_default.h` supplies reset/default values where generated defaults exist.
- AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_RLC`, and CP packet builders consume the `__SHIFT` and `_MASK` names.

Observed integration in this tree includes:

- `amdgpu/gfx_v9_4_2.c`, which includes `gc/gc_9_4_2_offset.h` and `gc/gc_9_4_2_sh_mask.h` for Aldebaran/GC 9.4.2 graphics support, golden settings, compute initialization, RAS/error paths, and register access.
- `amdgpu/amdgpu_amdkfd_aldebaran.c`, which also includes the GC 9.4.2 offset and mask headers for KFD-to-KGD debug, trap, watchpoint, queue, VMID, and wave-control integration.
- Clearstate tables such as `amdgpu/clearstate_gfx10.h` and nearby generation tables, which show the same class of DB, PA/SC, viewport, and SPI context registers being reset to known render-state values.
- Userspace graphics drivers and kernel command submission paths, which program many DB/CB/PA/SPI context registers through PM4 packets rather than direct CPU MMIO.

The register names are cross-generation familiar, but the exact field layout is generation-specific. In particular, the SPI input control layout differs across GC generations and even within this chunk between inputs 0-19 and 20-31.

## Risks

- Bitfield drift is high impact. A wrong mask or shift in DB, PA/SC, CB, or SPI state can cause incorrect depth/stencil tests, invalid clears, broken compression metadata, wrong scissor/viewport clipping, missing color channels, or bad pixel-shader interpolation.
- GDS reset fields are dense and mechanically repetitive. Off-by-one resource reset masks in `GDS_GWS_RESET0/1` could reset the wrong GWS resource, while wrong ordered-append pipe reset bits could disturb another ME or pipe.
- Context-switch counters all share `UPDN` and `PTR` layouts; incorrectly treating them as independent semantic counters rather than context-save bookkeeping can mislead diagnostics.
- DB surface address and metadata fields must match memory layout, tiling, swizzle, compression, and HTILE/DCC state. Bad values can produce GPU faults, corrupted depth/stencil data, or hangs.
- Scissor and viewport fields are signed/packed coordinate state. Mispacking top-left, bottom-right, or offset-disable bits can silently clip all rendering or allow rendering outside intended bounds.
- `PA_SC_RASTER_CONFIG` and tile steering fields encode topology-sensitive routing. Incorrect values can misroute work across raster pipes or shader engines.
- `SPI_PS_INPUT_CNTL_*` is split into two layouts. Applying the input 0-19 masks to input 20-31, or assuming `ROTATE_PC_PTR`/`PT_SPRITE_TEX` exist everywhere, can corrupt interpolation setup.
- This chunk ends before `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK`; the merge/reconciliation lane should join it with the next chunk so the final per-file report does not imply the `SPI_BARYC_CNTL` family is complete here.

## Test and Validation Signals

Useful validation is mostly build, bring-up, and graphics conformance coverage:

- Build AMDGPU and KFD code with GC 9.4.2 support enabled; this catches missing or renamed generated macros included by `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`.
- Run graphics render tests that exercise depth/stencil formats, depth bounds, clears, resolves, HTILE metadata, compression/decompression, and stencil front/back reference/mask behavior.
- Run scissor, viewport, clip rectangle, user clip plane, programmable near clip, and viewport-depth-range tests across all 16 viewport slots.
- Run MRT color-mask and blend-constant tests to validate `CB_TARGET_MASK`, `CB_SHADER_MASK`, and `CB_BLEND_*` packing.
- Run pixel-shader interpolation tests covering flat shade, perspective/linear center/sample/centroid, pull model, point sprites, FP16 interpolation, default attributes, front-face, sample coverage, and position inputs.
- Exercise suspend/resume, GPU reset, preemption, and queue context-switch workloads to validate GDS context-switch status/counter behavior and GWS/OA reset sequencing.
- Compare generated `gc_9_4_2_*` headers against AMD's source register database or upstream-generated headers when refreshing this file; repeated families should be checked with scripts because visual review is error-prone.

### subset-b-002671: lines 9800-12226

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 9800-12226

## Scope

This chunk is a generated AMD GC 9.4.2 shader/header mask slice. It contains 2,168 `#define` constants under 259 register-name comment groups. The range starts immediately after the `SPI_BARYC_CNTL` comment from the previous chunk, so it only contains the `FRONT_FACE_ALL_BITS_MASK` field for that register. It ends inside `CB_COLOR5_INFO`, after the `SIMPLE_FLOAT_MASK` field; the rest of `CB_COLOR5_INFO` and later color-target registers are in the next chunk.

There are no functions, structs, enums, variables, locks, allocation paths, or executable statements here. The file is compile-time hardware metadata: each `__SHIFT` and `_MASK` macro describes a bitfield in a GC 9.4.2 MMIO register.

The covered register families are:

- SPI export and shader-interface fields, including front-face barycentric handling, temporary ring sizing, position/Z/color export formats.
- SX pixel export, downconversion, blend epsilon, blend optimization disable, and per-MRT blend optimization fields.
- CB blend control for MRT0 through MRT7 and CB color buffer state for targets 0 through part of 5.
- DB depth/stencil, EQAA, shader depth interaction, HTILE, alpha-to-mask, and stencil-result compare/preload controls.
- PA clipper, setup, scan converter, rasterization, antialiasing sample locations/masks, binner, conservative rasterization, stereo, line/point, viewport transform, NaN/Inf, primitive filtering, and NGG-facing controls.
- VGT draw initiation, DMA/index draw state, tessellation, geometry shader, streamout, primitive ID, shader-stage enable, ring sizing, and vertex reuse/deallocation controls.
- Small copy-state and command-style payload registers such as `CS_COPY_STATE`, `GFX_COPY_STATE`, `VGT_IMMED_DATA`, and event initiators.

## Purpose

The purpose of this header segment is to expose the bit layout of GC 9.4.2 graphics pipeline registers to AMDGPU driver code. The paired offset header provides register addresses; this mask header provides field offsets and masks used to compose and decode 32-bit register values.

The generated API pattern is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

Consumers normally reach these macros through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `WREG32_SOC15()`, `RREG32_SOC15()`, packet-building code, or local read-modify-write helpers. Correctness depends on these symbolic names matching the ASIC register database for GC 9.4.2.

## Important Macro Families

### SPI And SX Export State

The SPI section defines fields for shader output formats and scratch/ring sizing. `SPI_TMPRING_SIZE` packs wave count and wave size. `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` encode position, depth, and up to eight color export formats. The leading `SPI_BARYC_CNTL__FRONT_FACE_ALL_BITS_MASK` is a boundary fragment from the prior register group.

The SX section controls pixel shader export conversion and blend optimization. `SX_PS_DOWNCONVERT` and `SX_BLEND_OPT_EPSILON` have repeated 4-bit fields for MRT0 through MRT7. `SX_BLEND_OPT_CONTROL` disables color/alpha optimizations per MRT and has a global `PIXEN_ZERO_OPT_DISABLE` bit. `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` each define color and alpha source/destination optimization selectors and combine functions.

### CB Blend And Color Target State

`CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define the per-render-target blend contract: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate alpha enable, blend enable, and ROP3 disable. These macros are central to translating API blend state into hardware register values.

The later CB color target section covers complete target descriptors for MRT0 through MRT4 and the beginning of MRT5. Repeated fields include:

- `CB_COLORn_BASE` and `CB_COLORn_BASE_EXT`, which hold 256-byte-aligned base address pieces.
- `CB_COLORn_ATTRIB2`, with mip0 height, mip0 width, and max mip.
- `CB_COLORn_VIEW`, with slice start, slice max, and mip level.
- `CB_COLORn_INFO`, with endian, format, number type, component swap, fast clear, compression, blend clamp/bypass, simple float, round mode, blend optimization hints, FMASK compression flags, DCC enable, and CMASK address type.
- `CB_COLORn_ATTRIB`, with mip0 depth, metadata linear flag, sample/fragment counts, force alpha, color/FMASK swizzle modes, resource type, RB alignment, and pipe alignment.
- `CB_COLORn_DCC_CONTROL`, with overwrite-combiner, compressed/uncompressed block sizing, color transform, independent 64B blocks, lossy precision, and constant encode controls.
- `CB_COLORn_CMASK`, `FMASK`, clear words, and DCC base/base-ext registers.

Because the chunk stops inside `CB_COLOR5_INFO`, later merge work must combine the next chunk before making complete claims about target 5 and targets 6-7.

### DB Depth, Stencil, And Sample State

`DB_DEPTH_CONTROL` exposes stencil enable, Z enable/write, depth-bounds enable, Z compare function, backface enable, front/back stencil functions, and color-write behavior on depth pass/fail. `DB_EQAA` describes sample counts, anchor samples, alpha-to-mask sample count, high-quality intersections, interpolation choices, over-rasterization amount, and post-Z over-rasterization enable. `DB_SHADER_CONTROL` connects pixel shader behavior to depth/stencil processing through Z export, stencil exports, Z ordering, kill/coverage/mask export, hierarchical execution, alpha-to-mask disable, depth-before-shader, conservative Z export, primitive ordered pixel shader, and overlap controls.

`DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK` describe depth metadata, stencil-result compare inputs, preload window coordinates, and alpha-to-mask offsets. These are passive bitfield definitions, but the hardware behavior is stateful once programmed.

### PA Clipper, Setup, Scan Converter, And Rasterizer State

The PA groups are broad pipeline state for clip, setup, scan conversion, rasterization, multisampling, and binning. `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and the guard-band adjustment registers define user clip/cull planes, viewport transform behavior, vertex shader output sideband usage, NaN/Inf handling, and guard-band clip/discard parameters.

Setup/raster state includes `PA_SU_SC_MODE_CNTL`, line stipple controls, primitive/small-primitive filtering, object/primitive ID controls, NGG-related clipper state, over-rasterization behavior, stereo routing, point and line sizes, polygon offset scale/offset/clamp, and vertex quantization/rounding. `PA_SC_MODE_CNTL_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` control scan conversion, scissor/MSAA behavior, tile/supertile walk order, multi-GPU or multi-SE discard behavior, EOV forcing, out-of-order primitive handling, shader quad realignment, binning dimensions/state counts, conservative rasterization uncertainty rules, and NGG deallocation limits.

The antialiasing section is highly regular. `PA_SC_AA_CONFIG` defines sample exposure and coverage selection. Sixteen `PA_SC_AA_SAMPLE_LOCS_PIXEL_*_*` registers pack 4-bit X/Y locations for samples 0 through 15 across four pixel positions. `PA_SC_AA_MASK_X0Y0_X1Y0` and `PA_SC_AA_MASK_X0Y1_X1Y1` pack coverage masks for the same pixel quadrants. `PA_SC_CENTROID_PRIORITY_0/1` define centroid priority distances 0 through 15.

### VGT Draw, Tessellation, Geometry, And Streamout State

The VGT groups define draw setup and shader-stage plumbing. `VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DMA_NUM_INSTANCES`, and `VGT_DMA_EVENT_INITIATOR` describe indexed draw DMA base/size/type, instance count, and event signaling. `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, and `VGT_DISPATCH_DRAW_INDEX` describe draw source/mode, immediate payload, event address/type, payload enablement, and dispatch draw matching.

Tessellation and geometry-stage fields include `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, min/max tessellation level, reuse depth, group primitive/vector controls, GS mode, GS on-chip control, per-ES/GS/VS ratios, GSVS ring offsets/item sizes, GS output primitive types, LS/HS config, GS vertex item sizes, tessellation distribution, shader-stage enablement, and tessellator-factor parameters. These fields are integration points between compiler-selected pipeline state and command submission.

Streamout and primitive state includes `VGT_STRMOUT_BUFFER_SIZE_*`, vertex stride, buffer offset, opaque draw offset/filled-size/stride, `VGT_STRMOUT_CONFIG`, `VGT_STRMOUT_BUFFER_CONFIG`, primitive ID enable/reset, GS instance count, primitive reuse disable, vertex count enable, vertex reuse depth, and output deallocation distance.

## Control Flow

There is no direct control flow in this header. Runtime flow is supplied by driver code that includes this generated file:

1. Code selects the GC 9.4.2 register address from the matching offset header.
2. It builds a register value by shifting field values by `__SHIFT` and constraining them with `_MASK`, usually through helper macros.
3. It writes the value through MMIO or command packets, or reads a register and decodes fields using the matching mask/shift pair.
4. Sequencing, synchronization, cache flushing, command submission, polling, and error handling live outside this header.

Typical higher-level flows include graphics pipeline state emission for draws, render-target setup, blend/depth/stencil programming, MSAA sample programming, tessellation/geometry/NGG setup, streamout setup, and indexed draw DMA/event setup.

## State And Persistence Behavior

The macros themselves hold no software state. They describe hardware register state that persists until overwritten, reset, power-gated/reinitialized, or restored by firmware/driver resume paths.

Most fields in this chunk are context or pipeline state. Once programmed, blend, color target, depth/stencil, rasterizer, sample-location, tessellation, streamout, and draw-control values affect subsequent graphics work submitted to the GPU. Address-bearing CB fields (`BASE`, `BASE_EXT`, `CMASK`, `FMASK`, `DCC_BASE`, and their extension registers) refer to GPU memory in 256-byte units and therefore must match the driver's memory manager, tiling, metadata, compression, and synchronization state.

Some registers are command-like rather than durable configuration, such as draw initiators, event initiators, dispatch draw index matching, copy-state source IDs, and preload/clear controls. These require surrounding driver sequencing to avoid stale state, partial updates, or writes in the wrong pipeline phase.

## Dependencies And Integration Points

This chunk must remain synchronized with the generated GC 9.4.2 register database and the matching address definitions, especially `gc_9_4_2_offset.h`. It is consumed by AMDGPU graphics, display interop, command submission, shader compiler state emission, KFD/compute-adjacent setup where graphics state is shared, render-target compression/metadata code, reset/suspend/resume paths, and debug or register-dump tooling.

The source path is under a `ceph-client` mirror, but this file is AMD GPU driver hardware metadata. It has no Ceph protocol behavior, filesystem data path, distributed consistency, network I/O, or persistent storage semantics beyond the GPU-memory addresses programmed into CB metadata registers.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can corrupt GPU MMIO state.
- The chunk has incomplete boundary register groups: `SPI_BARYC_CNTL` is only represented by one trailing mask, and `CB_COLOR5_INFO` is only partially present.
- Repeated MRT and color-target groups are easy to copy or index incorrectly. Target-specific names must match the register address selected by the caller.
- Address fields are split across low and extension registers and use 256-byte units. Incorrect alignment, truncation, or extension handling can send CB/CMASK/FMASK/DCC traffic to the wrong GPU memory.
- Many fields interact across blocks: color export formats must match CB formats and blend controls; MSAA/EQAA sample counts must match AA sample locations, masks, DB state, and color/depth target attributes; tessellation/GS/NGG settings must match shader-stage enablement and compiler output.
- Some masks cover reserved or legacy-named fields such as `RESERVED_*` in `VGT_GS_MODE` and `SPRITE_EN_R6XX` in `VGT_DRAW_INITIATOR`. Driver code should avoid assuming semantic safety from the names alone.
- Command-like fields and enable/clear/event fields need hardware-specific ordering outside this header. Treating them as ordinary cached state can cause missed events, wrong draws, or inconsistent profiling/debug observations.

## Test Signals

Useful validation is mostly integration-level rather than unit-level:

- Kernel build coverage for all GC 9.4.2 AMDGPU users, catching renamed or missing macros.
- Register helper tests or static checks that `REG_SET_FIELD()` and `REG_GET_FIELD()` round-trip important fields without overlapping unrelated bits.
- GPU graphics CTS/dEQP/Piglit coverage for blending, depth/stencil, alpha-to-mask, MSAA/EQAA sample locations, conservative rasterization, tessellation, geometry shader, NGG, streamout, primitive ID, and indexed draw paths.
- Render-target compression and metadata tests that exercise DCC/CMASK/FMASK base, clear-word, format, sample, fragment, alignment, and swizzle fields.
- Suspend/resume, reset, and context-switch testing to ensure programmed pipeline state is restored or invalidated correctly.
- Register dumps on GC 9.4.2 hardware compared against known-good programming sequences for color/depth/rasterizer/VGT state.

### subset-b-002672: lines 12227-14836

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 12227-14836

## Purpose

This chunk is generated AMD GPU register metadata for the GC 9.4.2 graphics core, used by the Linux AMDGPU driver path carried in this source tree. It defines symbolic bit positions and masks for hardware registers; it does not implement executable logic. The macros let GC 9.4.2 consumers build or decode 32-bit register values through `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 MMIO helpers, and packet-emission code without open-coded hex bit layouts.

The range starts at the tail of color-buffer target 5 state, completes color-buffer targets 6 and 7, then crosses several hardware decode blocks:

- `gc_gfxudec`: command processor EOP/fence/writeback, streamout and pipeline-stat counters, scratch registers, append/atomic preop registers, CP DMA, coherency, CE/IB/ST buffers, indirect draw/dispatch/index pointers, GDS backup, sample status, RLC GPM perf counters, GRBM indexing, VGT draw state, PA screen/trap state, SQ thread trace, SQC cache controls, DB counters, GDS direct/atomic/resource/OA registers, and SPI configuration.
- `gc_grbmdec`: GRBM status, reset, clock/power, read/write error, interrupt, trap, fence, scratch, and async VF violation fields.
- `gc_hypdec`: CP/RLC microcode RAM access, GRBM saved-register/CAM access, RLC GPU IOV virtualization, doorbell, timer, semaphore, scheduler, interrupt, SDMA save/restore status, and SDMA VM busy fields.
- `gc_padec`: the beginning of PA/VGT frontend decode, including DMA FIFO depths, cache invalidation, streamout delay, FIFO depths, IA status, and VGT status.

## Important APIs, Types, And Data

There are no C functions, structs, enums, variables, locks, or allocation APIs in this range. The public surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `REGISTER__FIELD_MASK` gives the field's 32-bit mask before shifting.
- Address-block comments such as `gc_gfxudec`, `gc_grbmdec`, `gc_hypdec`, and `gc_padec` identify hardware decode domains, not C namespaces.
- Full-width fields such as `SCRATCH_REG*__SCRATCH_REG*_MASK`, `CP_*_DATA_*`, `GDS_*_DATA`, `SQ_THREAD_TRACE_CNTR__CNTR_MASK`, and `GRBM_NOWHERE__DATA_MASK` expose whole register words.

Important register families in this chunk include:

- Color buffer target state for slots 5-7: `CB_COLOR{5,6,7}_INFO`, `ATTRIB`, `ATTRIB2`, `VIEW`, base/base-ext, CMASK, FMASK, clear words, DCC base, and `DCC_CONTROL`. These encode render target base addresses, mip dimensions, array slice/mip views, format/number type/component swap, fast clear/compression/DCC controls, sample/fragment counts, swizzle modes, resource type, and alignment flags.
- CP writeback and pipeline statistics: `CP_EOP_DONE_*`, `CP_EOP_LAST_FENCE_*`, `CP_STREAM_OUT_ADDR_*`, `CP_NUM_PRIM_*`, `CP_VGT_*COUNT*`, `CP_PA_*COUNT*`, `CP_SC_PSINVOC_COUNT*`, `CP_PIPE_STATS_*`, and `CP_STREAM_OUT_CONTROL`. These describe address, data, cache-policy, and counter layouts for EOP events, fences, streamout, and graphics pipeline accounting.
- CP scratch, append, atomic, semaphore, DMA, and coherency controls: `SCRATCH_REG0..7`, obsolete `SCRATCH_UMSK/ADDR`, `CP_APPEND_*`, `CP_*ATOMIC*PREOP*`, `CP_SIG_SEM_*`, `CP_WAIT_SEM_*`, `CP_WAIT_REG_MEM_TIMEOUT`, `CP_DMA_{PFP,ME}_*`, `CP_DMA_CNTL`, `CP_DMA_READ_TAGS`, `CP_COHER_*`, and `CP_ME_COHER_*`.
- Command-buffer and indirect-execution state: `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_SCRATCH_INDEX/DATA`, `CP_RB_OFFSET`, CE/IB2/ST base/offset/buffer-size registers, `CP_EOP_DONE_EVENT_CNTL`, `CP_EOP_DONE_DATA_CNTL`, completion status, predication visibility, metadata base addresses, indirect draw/dispatch pointers, index base/type, GDS backup, and `CP_SAMPLE_STATUS`.
- Frontend VGT/PA/WD state: `GRBM_GFX_INDEX`, `VGT_GSVS_RING_SIZE`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, streamout filled sizes, index range/offset/count/instance controls, tessellation factor memory/ring sizing, WD buffer bases, `IA_MULTI_VGT_PARAM`, line stipple/screen extent/trap screen registers, and the later `gc_padec` FIFO/status/cache invalidation registers.
- SQ/SQC trace and cache controls: `SQ_THREAD_TRACE_BASE/SIZE/MASK/TOKEN_MASK/PERF_MASK/CTRL/MODE/BASE2/TOKEN_MASK2/WPTR/STATUS/HIWATER/CNTR/USERDATA_*`, plus `SQC_CACHES` and `SQC_WRITEBACK`.
- DB/GDS/SPI support: DB occlusion and z-pass counters, direct GDS read/write/burst registers, GDS atomic operand/result/register windows, GWS resource controls, ordered-append controls, `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, and `SPI_WAVE_LIMIT_CNTL`.
- GRBM status and controls: `GRBM_STATUS`, `GRBM_STATUS2`, per-SE `GRBM_STATUS_SE0..SE3`, `GRBM_SOFT_RESET`, `GRBM_GFX_CLKEN_CNTL`, wait-idle clocks, read/write error decoders, interrupt enable, trap programming, power controls, UTCL2 invalidation ranges, fence ranges, scratch registers, and async VF violation reporting.
- Hypervisor and RLC IOV state: CP PFP/ME/CE/MEC and RLC GPM microcode address/data registers, saved-register select/data registers, GRBM CAM remap registers, VF enable/mask/doorbell status set/clear, RLC timers, hypervisor semaphores, RLC clock controls, IOV scheduler/config/status registers, active function ID, IOV interrupt state, scratch and ucode windows, F32 control/reset, virtual reset requests, RLC responses, and SDMA0-7 preempt/save/restore plus VM busy status.

## Control Flow

This header chunk has no runtime branches or call graph. Its only direct execution effect is C preprocessing: consumers include the header and compile the constants into register read-modify-write operations, packet payloads, or debug/status decoders.

Typical runtime use follows this pattern:

1. A GC 9.4.2-specific source such as `gfx_v9_4_2.c` or `amdgpu_amdkfd_aldebaran.c` includes both `gc_9_4_2_offset.h` and this `gc_9_4_2_sh_mask.h`.
2. Driver code selects an offset macro from the matching offset header and reads or writes the hardware register via SOC15 helpers such as `RREG32_SOC15`/`WREG32_SOC15`, or emits a PM4 packet that carries the same field layout.
3. Field helpers use the `__SHIFT`/`_MASK` pair to pack a field value into a 32-bit register word or extract a status field from a readback.

Representative downstream flows in the tree include GFX idle checks that read `GRBM_STATUS2` and test `RLC_BUSY`, cache flush/invalidate packet paths that emit `CP_COHER_CNTL` action bits, golden-setting paths that program `VGT_CACHE_INVALIDATION`, and RLC IOV firmware paths in later GFX files that write `RLC_GPU_IOV_UCODE_ADDR`, `RLC_GPU_IOV_UCODE_DATA`, and `RLC_GPU_IOV_F32_CNTL`. The GC 9.4.2 macro names here are the generation-specific definitions such consumers rely on.

## State And Persistence Behavior

The macros are stateless compile-time constants. All state described here is hardware state in the GPU or packet-visible command processor state.

The range describes several persistence classes:

- Context/render state that persists until reprogrammed by command streams, clear state, context restore, reset, or power transitions: color-buffer target state, VGT draw parameters, PA screen/trap controls, SPI limits, and tessellation/WD buffer bases.
- Command processor and synchronization state: EOP done addresses/data, last fence registers, append/fence registers, semaphore address/control fields, wait timeouts, CP DMA source/destination/command state, scratch registers, CE/IB/ST buffer windows, completion status, and predication/sample-status bits.
- Cache and coherency state: `CP_COHER_*`, `CP_ME_COHER_*`, `SQC_CACHES`, `SQC_WRITEBACK`, and `VGT_CACHE_INVALIDATION` define fields that trigger or observe cache writeback/invalidation and ordering operations.
- Status and diagnostic state: GRBM global/per-SE busy bits, read/write error fields, interrupt/trap registers, DB counters, GDS counters, SQ thread trace status/write pointer/counters, IA/VGT busy status, and SDMA save/restore/preempt state.
- Virtualization and firmware state: hypervisor CP/RLC ucode windows, saved-register and CAM remap data, RLC GPU IOV VF enable/mask/scheduler/doorbell/interrupt/reset status, active function IDs, semaphores, and VM busy masks.

Some fields are likely sticky, write-one-to-clear, clear-on-read, or command-triggering according to the hardware spec. This header does not encode those semantics. Consumers must know whether a register is safe to read, must be polled, or must be written only during quiescent/reset/firmware-load windows.

## Dependencies

This chunk depends on the generated AMD ASIC register ecosystem:

- `gc_9_4_2_offset.h` supplies matching register offsets. These masks are incomplete and unsafe without the corresponding offsets.
- Other GC 9.4.2 generated headers provide defaults and adjacent register ranges not covered by this line chunk.
- AMDGPU's SOC15 register helpers, PM4 packet emission helpers, and field helpers provide the operators that combine these constants with MMIO reads/writes or command packets.
- `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` include this header directly for Aldebaran/GC 9.4.2 behavior.
- Shared AMDGPU definitions such as `soc15d.h` expose packet-level equivalents for some `CP_COHER_CNTL` bits; the register-mask values here must remain consistent with those command packet definitions where hardware reuses the same bit layout.

The data is a hardware ABI. It must stay synchronized with AMD's GC 9.4.2 register specification and with sibling generated files. Similar macro names exist in GC 9.1, 9.4.3, 10.x, 11.x, and 12.x headers, but fields can move or change width across generations.

## Integration Points

Primary integration points are:

- AMDGPU GFX 9.4.2 initialization, reset, idle, golden-setting, and command submission paths that include the GC 9.4.2 offset/mask pair.
- KFD/Aldebaran compute integration, where GC 9.4.2 register fields may be used for queue, VMID, debug, and performance/debug state.
- Render backend setup and context restore for color-buffer slots 5-7, including DCC, CMASK, FMASK, fast clear, sample count, resource type, swizzle mode, and base address programming.
- PM4 packet generation for EOP writebacks, fences, acquire-mem/coherency operations, CP DMA copies, semaphore waits/signals, streamout/stat counters, and indirect draw/dispatch/index state.
- Idle and hang diagnostics that decode `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS_SE*`, `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, `CP_*_COMPLETION_STATUS`, `CP_SAMPLE_STATUS`, and read/write error fields.
- SQ thread trace and profiling tooling that programs trace buffers, masks CUs/SHs/SIMDs/VMIDs/shader stages, checks full/busy/new-buffer/error status, and reads trace counters/userdata.
- SR-IOV and GPU virtualization flows that manipulate RLC GPU IOV VF enable/mask/status, doorbell set/clear, scheduler slots, active function IDs, per-SDMA save/restore state, and virtual reset requests.
- GDS/GWS/OA users that access GDS memory windows, atomics, resource counters, ordered append rings, and backup state.

## Risks

- Incorrect shifts or masks silently produce valid C code that targets the wrong hardware bits. In this chunk that can corrupt render-target metadata, fence addresses, DMA commands, cache invalidation policy, VMID/queue selection, trace programming, or virtualization state.
- The chunk mixes ordinary context state with control, status, reset, interrupt, trap, firmware, and hypervisor registers. Treating all fields as normal read-modify-write state is unsafe.
- Several address fields are split low/high and use alignment shifts, for example CP EOP/streamout/append/pipe-stat addresses and CB/GDS/WD base registers. Packing unaligned or incorrectly shifted addresses can redirect GPU writes or DMA.
- Coherency fields have system-wide effects. Misprogrammed `CP_COHER_CNTL`, `CP_ME_COHER_CNTL`, `SQC_CACHES`, or `VGT_CACHE_INVALIDATION` bits can leave stale shader, texture, color/depth, or memory-controller state visible to later work.
- `GRBM_SOFT_RESET`, `RLC_GPU_IOV_F32_RESET`, `RLC_GPU_IOV_VIRT_RESET_REQ`, interrupt force/disable, doorbell set/clear, and hypervisor semaphore fields are destructive or control-plane oriented. They should be used only in the intended reset/IOV/firmware sequences.
- Status fields such as GRBM busy bits, read/write errors, CP completion state, SQ trace status, GDS completion/resource state, and SDMA save/restore bits can be transient or sticky; tests must account for polling and clear behavior from the hardware spec.
- Cross-generation reuse is risky. GC 9.4.2 shares many names with GC 9.1 and GC 9.4.3, but field positions and register availability are not guaranteed identical.
- Because this file is generated register metadata, manual edits are high risk and should normally be replaced by regenerating the AMD register headers from the authoritative source.

## Test Signals

Useful validation signals include:

- Compile coverage for GC 9.4.2 include users, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, with `REG_GET_FIELD` and `REG_SET_FIELD` expressions resolving against this header and `gc_9_4_2_offset.h`.
- Static consistency checks that every register represented in this chunk has a matching offset in `gc_9_4_2_offset.h` and, where applicable, a matching default/generated entry elsewhere in the ASIC register set.
- Boot and GFX initialization on Aldebaran/GC 9.4.2 hardware or emulation, confirming golden settings, context state, color-buffer clear state, GRBM idle polling, and reset flows complete without invalid-register warnings.
- Ring tests that exercise EOP writebacks/fences, CP DMA, acquire-mem cache invalidation, wait/signal semaphore, indirect draw/dispatch, index buffer setup, and streamout/pipeline-stat writes.
- Render and compute workloads that stress color targets 5-7, DCC/CMASK/FMASK, multisampling, fast clear, tessellation, streamout, line stipple/screen extents, GDS atomics, GWS resources, and ordered append.
- SQ thread trace/profiling tests that allocate a trace buffer, program mask/token/perf/mode fields, validate wrap/interrupt/full/error status, and decode the resulting trace stream.
- Virtualization/SR-IOV tests that load RLC IOV firmware, toggle VF enable/masks, process doorbell status set/clear, issue VF/PF reset requests, and observe per-SDMA preempt/save/restore and VM busy status.
- Suspend/resume, GPU reset, and RAS/hang-diagnostic runs that verify GRBM status/error fields, soft reset bits, RLC clock controls, microcode windows, and scratch/fence registers are restored or cleared in the expected sequence.

### subset-b-002673: lines 14837-17355

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 14837-17355

## Scope

This chunk covers lines 14837-17355 of the generated AMD GC 9.4.2 shader/register mask header. It contains 2,142 `#define` entries across 372 register names. The slice starts with the final `VGT_CNTL_STATUS__VGT_PRIMGEN_BUSY_MASK` bit from the preceding VGT status register, then covers WD/IA/VGT/PA front-end and primitive assembly controls, PA scanner/clipper/binning controls, UTCL1 policy/status fields, and a large performance-counter data/select register span.

The chunk crosses two visible address-block regions:

- Before line 15457, the register groups describe graphics front-end and PA/VGT/WD/IA controls, including UTCL1 policy, primitive/DMA controls, PA clip/scanner enhancement, binner event controls, FIFO sizing, and tile steering.
- From `// addressBlock: gc_perfddec` at line 15457 through line 16043, it defines performance-counter data register masks for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB/DB, RLC, and RMI blocks.
- From `// addressBlock: gc_perfsdec` at line 16045 to the end of this chunk, it defines performance-counter selector, global control, latency-stat selector, draw-window, GRBM busy-mask, SQ/SPI binning, texture/cache, color-buffer filter, and counter-mode fields.

This is a generated register metadata header, not executable driver logic. The public surface is the set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed with matching GC 9.4.2 register offsets.

## Purpose

`gc_9_4_2_sh_mask.h` supplies bit positions and masks for AMDGCN/SOC15 GC 9.4.2 hardware registers, used by the Aldebaran graphics and KFD paths. This chunk's purpose is to let runtime code safely build and decode 32-bit register values for:

- Work distributor (`WD_*`) busy state, draw quality-of-service, UTCL1 policy/status, buffer resource sizing, and performance counters.
- Input assembler (`IA_*`) UTCL1 policy/status and performance-counter selects.
- Vertex geometry/tessellation (`VGT_*`) system configuration, max wave IDs, DMA primitive/control parameters, LS/HS config, and performance-counter selects.
- Primitive assembler/clipper/scanner (`PA_*`) clipper and scanner enhancement, binner events, FIFO sizing, UTCL1 controls, scanner out-of-order behavior, DSM/tile steering, and PA SU/SC performance counters.
- Command processor (`CP*`, `CPF`, `CPG`, `CPC`) performance counters, latency-stat selectors, draw object/window registers, and `CP_PERFMON_CNTL`.
- Global register bus manager (`GRBM*`) performance counters and user-defined busy/clean masks.
- Shader processor/input (`SPI`), shader queue (`SQ`), shader export (`SX`), global data share (`GDS`), texture address/data/cache (`TA`, `TD`, `TCP`, `TCC`, `TCA`), color buffer (`CB`), depth buffer (`DB`), runlist controller (`RLC`), and RMI performance-counter data/select registers.

The constants remove raw bit numbers from consumers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, golden-register programming, perf-event setup, debug register dumps, and low-level MMIO read/modify/write paths.

## Important API Surface

There are no structs, enums, functions, or inline helpers in this chunk. The API consists entirely of preprocessor macros. Important families are:

- `WD_CNTL_STATUS`, `WD_QOS`, `WD_UTCL1_CNTL`, and `WD_UTCL1_STATUS` expose WD busy bits, draw-stall control, UTCL1 retry/drop/bypass/invalidate/fragment/snoop policy, and fault/retry/PRT status plus UTCL1 IDs.
- `IA_UTCL1_CNTL` and `IA_UTCL1_STATUS` mirror the WD UTCL1 policy/status layout for input assembler traffic.
- `CC_GC_PRIM_CONFIG` and `GC_USER_PRIM_CONFIG` describe inactive IA and VGT/PA blocks, while `CC_GC_SHADER_ARRAY_CONFIG` and `GC_USER_SHADER_ARRAY_CONFIG` expose inactive CU masks. These are topology/configuration masks that must align with the companion offset header and ASIC harvesting rules.
- `VGT_SYS_CONFIG`, `VGT_VS_MAX_WAVE_ID`, `VGT_GS_MAX_WAVE_ID`, `VGT_DMA_PRIMITIVE_TYPE`, `VGT_DMA_CONTROL`, and `VGT_DMA_LS_HS_CONFIG` define primitive processing, DMA draw grouping, EOP/EOI switching, instance optimization, and tessellation input control fields.
- `WD_BUF_RESOURCE_1` and `WD_BUF_RESOURCE_2` split position, index, parameter, address-mode, and sideband buffer sizes across field ranges.
- `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_DEPTH_CNTL`, trap-screen locks, force-EOV counters, binner event controls, binner timeout/perf controls, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, FIFO size registers, and `PA_SC_TILE_STEERING_CREST_OVERRIDE` cover front-end raster/clip/scanner behavior. Many fields are enable/disable or workaround-style bits, including out-of-order PA/SC guidance, PBB/binning, line-stipple reset, VPZ event routing, shader profiling, FDCE enhancements, clock-gating disables, and ECO spares.
- `PA_UTCL1_CNTL1` and `PA_UTCL1_CNTL2` include page-fragment, prefetch, invalidation, request-discard, stall, sparse, VMID/RDWR perf-event, and fragment-forcing controls for PA-side translation traffic.
- `CPG/CPC/CPF/GRBM/WD/IA/VGT/PA_SU/PA_SC/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB/RLC/RMI_PERFCOUNTER*_LO/HI` in `gc_perfddec` are performance counter data registers. Most low/high halves expose a single full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` field, with notable 16-bit high-half masks for `PA_SU_PERFCOUNTER*_HI`.
- `*_PERFCOUNTER*_SELECT` in `gc_perfsdec` provide event-selection and counter-mode controls. Common fields include `PERF_SEL` or `CNTR_SEL*`, paired event selectors, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE`; block-specific selectors add masks such as SQ SQC bank/client/SIMD masks and GRBM user-defined busy masks.
- `CP_PERFMON_CNTL` defines global perfmon and SPM perfmon states, enable mode, and sample-enable fields.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` select texture-cache counter windows, with `ALWAYS` and `ENABLE` bits.
- `CPF/CPG/CPC_LATENCY_STATS_SELECT` and the corresponding data registers define latency-stat index, clear, enable, and data fields.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe draw-window/object filtering for CP-side measurement.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` add SQ counter enable, trace, halt, SIMD/mode, thread-trace, SQG event, and reset controls beyond the repeated SQ select registers.
- `SPI_PERFCOUNTER_BINS` defines four min/max bin ranges packed into a 32-bit register.
- `VGT_PERFCOUNTER_SEID_MASK` scopes VGT performance counting by shader-engine ID.
- `CB_PERFCOUNTER_FILTER` gates CB performance events by operation, format, clear, MRT, sample count, and fragment count.
- The chunk ends inside `CB_PERFCOUNTER3_SELECT`: it includes `PERF_SEL__SHIFT`, `PERF_MODE__SHIFT`, and `PERF_SEL_MASK`, but the matching `PERF_MODE_MASK` is outside this chunk.

## Control Flow

The header itself has no runtime control flow. Driver control flow around these masks usually follows this pattern:

1. Include the GC 9.4.2 offset header and this mask header.
2. Choose the register address macro from `gc_9_4_2_offset.h`.
3. Compose, update, or decode the register value with `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, often through field helpers.
4. Apply the value through SOC15/MMIO helpers, packet programming, golden-register setup, KFD debug paths, performance-monitor configuration, or debug dump decoding.

Direct local include points are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which owns Aldebaran GC 9.4.2 graphics setup, golden settings, reset, RAS, shader init, and performance-related flows, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c`, which uses the same generated masks for KFD/debug register value construction.

The visible chunk implies several table-driven or indexed runtime flows even though no loops are present here:

- Performance monitor setup iterates over low/high counter registers and paired selector registers for each IP block.
- SQ exposes 16 repeated `SQ_PERFCOUNTER*_SELECT` families and separate counter control/mask registers; consumers must program the select and mode fields consistently with the counter data slot being read.
- GRBM select registers pack a `PERF_SEL` field plus many user-defined busy/clean masks; consumers can construct aggregate busy views by choosing which sub-block busy signals participate.
- PA scanner/binning controls are usually programmed during ASIC initialization or golden-setting application, not per draw, because they affect pipeline scheduling, binning, out-of-order behavior, and hardware workarounds.
- UTCL1 controls/status fields are consumed by memory-translation setup and diagnostic paths; status fields are read/decoded, while control fields are written with preserved reserved bits.

## State and Persistence

The macros are compile-time constants and hold no state. The registers they describe are persistent GPU hardware state until changed by the driver, firmware, reset, suspend/resume, power transition, or context restoration path.

PA/SC/VGT/WD/IA control registers affect long-lived pipeline behavior. Examples include inactive block masks, primitive/DMA switching policy, PA scanner enhancement/workaround bits, binning controls, FIFO sizes, tile steering, and draw-stall control. Incorrect values can persist beyond a single command submission and affect all graphics or compute work using the same GC instance.

UTCL1 fields in WD, IA, and PA affect memory-translation behavior for front-end/scanner traffic. Retry timers, bypass/drop modes, invalidation bits, force-snoop policy, VMID reset mode, sparse behavior, page-fragment forcing, and request-discard behavior can alter fault reporting and translation performance until reprogrammed.

Performance-counter data registers are read-only or counter-like hardware state in normal usage. Selector and control registers persist the active event mux, SPM mode, counter mode, mask/window/filter policy, trace enable, halt state, and sample enable. If perf setup fails to restore selectors, later profiling sessions or debug reads can observe stale event routing.

The PA binner and scanner fields contain many enable/disable and ECO spare bits. These are typically validated as ASIC-specific golden settings or workaround state; persistence matters across reset, power-gating, and multi-die initialization because GC 9.4.2/Aldebaran has die-specific setup paths.

## Dependencies and Integration Points

- The masks depend on the generated GC 9.4.2 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h`.
- The header guard and generated constants are used by AMDGPU code through ordinary C preprocessing. There is no runtime library dependency inside the header itself.
- `gfx_v9_4_2.c` includes this header with the companion offset header for Aldebaran graphics initialization and register programming. Its golden-setting arrays use generated register offsets; related field-level call sites in this driver family rely on `*_sh_mask.h` names remaining exact.
- `amdgpu_amdkfd_aldebaran.c` includes this header for KFD/debug register value construction using field helpers such as `REG_SET_FIELD`.
- SOC15 register helpers, MMIO accessors, RAS paths, KFD debug controls, perfmon/perf-event code, register dump tooling, and reset/suspend/resume flows are the likely integration surfaces for this chunk.
- Cross-ASIC generated headers under `include/asic_reg/gc/` and older `gca/` headers expose similar macro families. That makes this chunk part of a generated ABI-like source surface: names and bit layouts are expected by existing common AMDGPU code and by ASIC-specific programming tables.

## Risks

- Generated bitfield drift is the main risk. A wrong shift or mask silently programs the wrong hardware bit, and most consumers will still compile because these are untyped numeric macros.
- The range begins and ends mid-context. Line 14837 is only the final `VGT_CNTL_STATUS` mask from a previous register group, and line 17355 cuts off inside `CB_PERFCOUNTER3_SELECT`. Merge/reconciliation must combine adjacent chunks before claiming complete per-file coverage.
- Reserved and ECO spare fields are exposed as ordinary masks. Callers must know which bits are safe to write for GC 9.4.2 stepping and preserve reserved bits during read/modify/write.
- PA scanner/binning/enhancement fields have high hardware-behavior risk. Fields that disable resets, alter out-of-order threshold switching, bypass PBB/binning, flush on transitions, or change line-stipple/VPZ behavior can cause rendering corruption, hangs, or performance regressions if applied to the wrong ASIC revision.
- UTCL1 policy fields can affect fault visibility and recovery. Misprogrammed bypass, drop, invalidation, retry, page-fragment, sparse, prefetch, VMID, or force-snoop controls can produce hidden faults, false fault attribution, or unstable memory accesses.
- Performance counter select/data families are repetitive. Copy/paste or index mistakes can read one block's counter while selecting another block's event, especially around paired `*_SELECT`/`*_SELECT1` registers and low/high data halves.
- Some high-half counter masks are narrower than the common full-width pattern, notably the PA SU high halves. Generic decoding code must not assume every `*_HI` mask is `0xffffffff`.
- GRBM busy mask fields have names ending in `_MASK_MASK` because the field name itself includes `MASK`; this can be easy to misuse in scripts or generated field helper lookups.
- The chunk exposes filter/windowing registers for perfmon. Stale filters, window selectors, draw-window controls, or sample-enable state can make performance measurements misleading even when counters increment.

## Test Signals

- Build coverage: compiling AMDGPU with `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` catches missing macros, duplicate definitions, syntax problems, and include-order issues.
- Header generation validation: compare lines 14837-17355 against the GC 9.4.2 source register database and `gc_9_4_2_offset.h`, verifying each `__SHIFT` has the expected mask, width, and register association.
- Adjacent-chunk merge validation: ensure `VGT_CNTL_STATUS` is completed from the prior chunk and `CB_PERFCOUNTER3_SELECT__PERF_MODE_MASK` is collected from the following chunk before writing the final per-file research report.
- Golden-register and init smoke tests: boot and reset Aldebaran/GC 9.4.2 hardware while checking dmesg for golden-setting failures, RAS initialization issues, GPU hangs, or graphics pipeline instability.
- UTCL1 diagnostics: exercise VM fault, retry/XNACK, PRT, sparse, and invalidation scenarios, then decode `WD_UTCL1_STATUS`, `IA_UTCL1_STATUS`, `PA_CL_CNTL_STATUS`, `PA_UTCL1_CNTL1`, and `PA_UTCL1_CNTL2` with these masks.
- Perfmon validation: program representative CP/GRBM/WD/IA/VGT/PA/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB/RLC/RMI counters, confirm selectors route the expected events, and verify low/high counter reads match known workloads.
- Counter filter/window tests: validate CP draw-window controls, CPF/CPG texture-cache windows, latency-stat selectors, SQ counter masks, SPI bins, VGT SEID masks, and CB filters against controlled workloads.
- Register-dump validation: decode known-good GC 9.4.2 register dumps and compare field names/values for PA scanner controls, UTCL1 controls/status, perf data registers, selector registers, and CB filter fields.

### subset-b-002674: lines 17356-19701

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 17356-19701

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.4.2 register mask header. The range starts with the final mask for `CB_PERFCOUNTER3_SELECT`, then covers complete register bitfield definitions for DB, RLC SPM/perfmon, RLC GPU IOV performance-counter access, RMI performance counters, and the first large portion of the `gc_pwrdec` power/clock-control block. It ends inside the `CGTT_SX_CLK_CTRL4` field list; the rest of that register belongs to the next chunk.

The file is declarative only. It defines C preprocessor constants for hardware register fields and does not contain functions, structs, variables, executable statements, or local storage.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU code when programming GC 9.4.2 MMIO registers. Each field is represented in the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask used to isolate or compose the field.

Driver code combines these macros with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`. The matching `gc_9_4_2_offset.h` header provides the register addresses, while this file provides the field encodings for those addresses.

## Important Macro Families

### DB, RLC, and RMI Performance Counters

The chunk begins in the performance counter selector area. `DB_PERFCOUNTER0_SELECT` through `DB_PERFCOUNTER3_SELECT` expose the depth-buffer block's event selection and mode fields. Counters 0 and 1 include paired secondary select registers (`DB_PERFCOUNTER0_SELECT1` and `DB_PERFCOUNTER1_SELECT1`) with `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. The regular layout uses 10-bit event selectors, a 4-bit `CNTR_MODE` field where present, and upper-nibble performance mode fields.

`RLC_PERFCOUNTER0_SELECT` and `RLC_PERFCOUNTER1_SELECT` provide the same style of event selector and mode fields for the RLC block. `RLC_PERFMON_CLK_CNTL_UCODE`, `RLC_PERFMON_CLK_CNTL`, and `RLC_PERFMON_CNTL` configure RLC perfmon clock behavior and global perfmon enables/resets, including `PERFMON_STATE`, `PERFMON_ENABLE_MODE`, `PERFMON_ENABLE`, `PERFMON_RESET`, `PERFCOUNTER_RESET`, and `PERFCOUNTER_ENABLE`.

`RMI_PERFCOUNTER0_SELECT` through `RMI_PERFCOUNTER3_SELECT` and `RMI_PERF_COUNTER_CNTL` define event selection for the render memory interface. Counters 0 and 2 have secondary select registers; the control register exposes counter enable, select enable, and counter reset bits.

### RLC Streaming Performance Monitor

The `RLC_SPM_*` section describes RLC-managed streaming performance monitor state. `RLC_SPM_PERFMON_CNTL` contains ring mode and sample interval fields. `RLC_SPM_PERFMON_RING_BASE_LO`, `RLC_SPM_PERFMON_RING_BASE_HI`, and `RLC_SPM_PERFMON_RING_SIZE` describe the output ring buffer location and size. `RLC_SPM_RING_RDPTR` exposes the ring read pointer.

`RLC_SPM_PERFMON_SEGMENT_SIZE`, `RLC_SPM_PERFMON_SEGMENT_SIZE_CORE1`, and `RLC_SPM_SEGMENT_THRESHOLD` divide sampled data into global and shader-engine segments. The line-count fields cover global, SE0, SE1, SE2, and core1 SE3/SE4/SE5 streams, so consumers must account for the multi-SE topology described by GC 9.4.2.

`RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` are indirect selector windows for programming per-shader-engine and global mux selection data. The sample-delay registers cover many GC blocks: CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI. Each uses an 8-bit `PERFMON_SAMPLE_DELAY` field plus reserved upper bits. `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` gives a maximum delay field.

### RLC GPU IOV Performance Counter Window

`RLC_GPU_IOV_PERF_CNT_CNTL`, `RLC_GPU_IOV_PERF_CNT_WR_ADDR`, `RLC_GPU_IOV_PERF_CNT_WR_DATA`, `RLC_GPU_IOV_PERF_CNT_RD_ADDR`, and `RLC_GPU_IOV_PERF_CNT_RD_DATA` define a virtualization-aware indirect access path for performance counter state. The control register contains fields for counter ID, register offset, operation type, reset trigger, read-valid status, read count, instance ID, `GRBM_GFX_INDEX`, and an `UNMAPPED` flag. The address/data registers hold 32-bit write and read payloads.

These fields are part of the PF/VF performance monitoring path rather than ordinary graphics dispatch setup. Correct use depends on RLC/IOV sequencing and privilege context.

### Power Decode and Clock-Gating Controls

The chunk enters `addressBlock: gc_pwrdec` after the RMI performance counter definitions. `CGTS_SM_CTRL_REG` exposes coarse-grain tree shader controls for block ID, register ID, read/write enable, instance index, broadcast, forced clock gating, and forced light sleep. `CGTS_RD_CTRL_REG` and `CGTS_RD_REG` provide a readback path for clock-gating/power-control state.

`CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`, `CGTS_TCC_DISABLE2`, and `CGTS_USER_TCC_DISABLE2` define TCC disable masks for the first and extended TCC groups. These fields are topology-sensitive because they can hide cache blocks from the active graphics configuration.

The largest portion of the chunk is the generated per-CU `CGTS_CU*_..._CTRL_REG` set for CU0 through CU15:

- `CGTS_CU*_SP0_CTRL_REG` and `CGTS_CU*_SP1_CTRL_REG` define SP lane groups (`SP00`, `SP01`, `SP10`, `SP11`) and their `OVERRIDE`, `BUSY_OVERRIDE`, `LS_OVERRIDE`, and `SIMDBUSY_OVERRIDE` fields.
- `CGTS_CU*_LDS_SQ_CTRL_REG` defines LDS and SQ gating/light-sleep override fields.
- `CGTS_CU*_TA_SQC_CTRL_REG` defines TA and, for several CUs, SQC gating/light-sleep override fields. Some CU entries expose only TA fields, so consumers cannot assume every repeated register has identical field coverage.
- `CGTS_CU*_TCPI_CTRL_REG` defines TCPI gating/light-sleep override fields plus reserved upper bits for CUs 0 through 15.

The ending portion covers block-level clock-gating timing controls: `CGTT_SPI_PS_CLK_CTRL`, `CGTT_SPIS_CLK_CTRL`, `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SC_CLK_CTRL0..2`, and `CGTT_SQG_CLK_CTRL`. These use common fields such as `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, and `SOFT_OVERRIDE*`, with block-specific `DIV_ID` or reserved fields where applicable.

`SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` define `FORCE_CU_ON_SH0` and `FORCE_CU_ON_SH1` masks, allowing shader-array scoped forcing of SQ subunit clocks. `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` define min/max power, phase offset, max power delta, short-term interval size, long-term interval ratio, and reference-clock selection for SQ power ramp/throttle behavior.

The chunk ends in `CGTT_SX_CLK_CTRL0..4`. It contains complete definitions for controls 0 through 3 and the beginning of control 4. These registers follow the same delay/hysteresis plus soft-stall/soft-override pattern used by other `CGTT_*_CLK_CTRL` registers.

## APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The effective API surface is the generated macro namespace consumed by AMDGPU C code. The important contract is name stability and exact bitfield encoding for GC 9.4.2:

- Register address macros come from the sibling offset header.
- Field shift/mask macros come from this header.
- Default/reset values, when generated, come from the sibling default header.
- Driver code relies on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spelling used by AMD's SOC15 register helper macros.

## Control Flow

This header has no runtime control flow. It influences control flow indirectly because compile-time macros determine which bits AMDGPU writes or reads when enabling performance counters, programming RLC SPM, using the RLC GPU IOV perf-counter window, changing TCC/CU availability masks, or enabling/disabling clock and light-sleep controls.

Hardware-side sequencing is not encoded here. For example, RLC SPM ring and muxsel programming requires owning code to set base/size/segment fields, program selector windows, manage sample intervals and delays, and read ring pointers in a valid order. Similarly, `RLC_GPU_IOV_PERF_CNT_CNTL` read-valid and reset fields require the surrounding IOV code to perform proper polling and timeout handling.

## State and Persistence Behavior

The header itself persists no state. The fields describe persistent or latched state inside GC 9.4.2 hardware until reset, firmware reinitialization, suspend/resume restoration, or explicit driver writes.

Important hardware state represented by this chunk includes DB/RLC/RMI performance event selection, RLC perfmon enables/resets, SPM ring buffer addresses and size, SPM segment sizes and thresholds, per-block SPM sample delays, SPM mux selector RAM access, RLC GPU IOV performance-counter indirect access state, TCC disable masks, per-CU power-gating/light-sleep overrides, shader-array force-on masks, SQ power throttle parameters, and block-level CGTT delay/hysteresis/override state.

Some fields are configuration bits, some are command/reset triggers, and some are readback/status bits. Examples include `PERFMON_RESET`, `PERFCOUNTER_RESET`, `PERF_CNT_RESET`, and `PERF_CNT_READ_VALID`. Treating trigger or status fields as ordinary persistent configuration can leave counters stale, cause incomplete reads, or desynchronize performance monitor setup.

## Dependencies and Integration Points

This chunk depends on generated AMD register-header conventions and is meaningful only with the matching GC 9.4.2 register-address header. It is typically included through AMDGPU GFX 9.4.x code paths that configure graphics, compute, power, and profiling behavior.

Important integration points in the source tree include:

- GFX 9.4.x AMDGPU initialization and reset code, which includes GC register headers and programs RLC, clock-gating, and golden-register state.
- Performance/profiling paths that configure DB, RLC, RMI, and SPM event selection, sample timing, ring buffers, and mux selection.
- SR-IOV or partition-aware paths that use `RLC_GPU_IOV_PERF_CNT_*` fields to access virtualized performance counter state.
- Power-management and clock-gating code that coordinates `CGTS_*`, `CGTT_*`, SQ force-on, and SQ throttle fields with SMU/RLC firmware policy.
- Topology/harvest handling that must keep `CGTS_TCC_DISABLE*` and `CGTS_USER_TCC_DISABLE*` values consistent with actual cache availability.

Cross-generation similarity is high, but these masks should not be reused across other GC versions. Similar register names in GC 9.4.3, GC 10, or GC 11 headers can differ in reserved fields, instance counts, or field widths.

## Risks

- Bitfield drift is high impact. An incorrect shift or mask can write unrelated MMIO fields and cause hangs, bad performance data, broken power gating, or invalid topology exposure.
- The repeated per-CU `CGTS_CU*` families are mechanically similar but not perfectly identical. Some `TA_SQC` registers omit SQC fields, and generated consumers must not assume all CU registers have the same subfields.
- SPM fields combine memory-backed ring configuration, selector-window programming, sample timing, and read pointers. Missing sequencing, alignment, or polling rules can corrupt samples or stall profiling flows.
- `RLC_GPU_IOV_PERF_CNT_*` fields are privilege- and virtualization-sensitive. Incorrect instance, `GRBM_GFX_INDEX`, operation type, or reset/read-valid handling can return stale data or cross the wrong VF/PF context.
- TCC disable and user-disable masks are topology-sensitive. Wrong values can expose disabled cache slices or hide valid ones.
- Clock-gating and light-sleep overrides affect power, performance, and stability. Forcing clocks on/off or overriding busy/light-sleep signals without SMU/RLC coordination can cause power regressions or hardware hangs.
- SQ power throttle fields are validated by field widths in some power-management code. Values outside the encoded ranges can silently truncate if consumers fail to range-check before shifting.
- This chunk starts after the `CB_PERFCOUNTER3_SELECT` family has begun and ends inside `CGTT_SX_CLK_CTRL4`, so adjacent chunks must be consulted for complete family-level documentation.

## Test and Validation Signals

Useful validation is mostly build-time and hardware-integration based:

- Build AMDGPU with GC 9.4.2 support enabled to catch missing, renamed, or conflicting macros.
- Exercise GFX 9.4.x initialization, reset, suspend/resume, and clock-gating toggles to verify `CGTS_*`, `CGTT_*`, SQ force-on, and SQ throttle fields remain consistent with firmware policy.
- Run performance counter tests for DB, RLC, and RMI event selection, including counters with secondary select registers and counters with only primary selection fields.
- Validate RLC SPM setup by checking ring base/size programming, segment size and threshold programming, per-block sample delays, mux selector writes, read pointer updates, and sample data integrity.
- Test SR-IOV/per-partition profiling flows that use `RLC_GPU_IOV_PERF_CNT_*`, especially reset, read-valid polling, instance selection, and `GRBM_GFX_INDEX` handling.
- Validate topology-sensitive TCC disable masks on harvested and fully enabled parts.
- Use power and stability tests to catch regressions from clock-gating overrides: idle power, load power, resume from low-power states, heavy graphics/compute load, and reset recovery.

## Unresolved Cross-Chunk References

The first line is the final `CB_PERFCOUNTER3_SELECT__PERF_MODE_MASK` definition, so the complete CB counter selector family is in the previous chunk. The final lines begin `CGTT_SX_CLK_CTRL4` but do not include its complete mask list; the following chunk must provide the rest of that register and subsequent power-control definitions.

### subset-b-002675: lines 19702-22065

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 19702-22065

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core. It contains C preprocessor constants that define bit shifts and bit masks for hardware register fields. The definitions are not executable code; they are the symbolic contract used by AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_KIQ`, and SOC15 offset wrappers to read, compose, and update 32-bit graphics-core registers without open-coding bit positions.

The range starts in the middle of `CGTT_SX_CLK_CTRL4`, covers multiple clock-gating and clock-throttling control registers, then crosses into the `gc_rbdec` address block for depth buffer, render backend, graphics backend, tile/macro-tile, color buffer, and DCC controls. It then enters the `gc_rlcpdec` address block for RLC control, status, safe-mode handshakes, timers, load balancing, clock-gating/power-gating controls, and RLC SERDES access fields. The chunk ends partway through `RLC_SERDES_WR_CTRL`, so the following chunk owns the remaining fields for that register.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or runtime variables in this chunk. The API surface is a large set of macros following the generated AMD ASIC register naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit index of a field.
- `REGISTER__FIELD_MASK` gives the unshifted mask for the field in a 32-bit register word.
- Full-register fields use masks such as `0xFFFFFFFFL`, for example timer values, CU masks, clock counters, and SERDES read data.
- Comments such as `// addressBlock: gc_rbdec` and `// addressBlock: gc_rlcpdec` mark hardware register decode blocks, not C namespaces.

The first group covers CGTT clock-gating and clock-throttling controls for graphics sub-blocks:

- `CGTT_SX_CLK_CTRL4`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_TCP_TCR_CLK_CTRL`, `CGTT_TCI_TCR_CLK_CTRL`, `TCX_CGTT_SCLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL2`, `TCC_CGTT_SCLK_CTRL3`, `TCA_CGTT_SCLK_CTRL`, `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, `CGTT_RLC_CLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, and `GRBM_CGTT_CLK_CNTL`.
- Common fields include `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `SOFT_OVERRIDE_DYN`, `SOFT_OVERRIDE_REG`, `SOFT_OVERRIDE_PERFMON`, and block-specific bits such as `MGLS_OVERRIDE`, `TCC_LS_ENABLE`, `BLK_CLKEN_MASK`, and `SOFT_OVERRIDE_DIDT_REG`.
- `RLC_GFX_RM_CNTL` is a small register with `RLC_GFX_RM_VALID`, used to represent validity of RLC graphics resource-management state.

The `gc_rbdec` group covers DB/RB/GB/CB rendering backend configuration:

- Depth buffer debug and cache/control registers: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, `DB_EXCEPTION_CONTROL`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, `DB_RMI_CACHE_POLICY`, `DB_DFSM_CONFIG`, `DB_DFSM_WATERMARK`, `DB_DFSM_TILES_IN_FLIGHT`, `DB_DFSM_PRIMS_IN_FLIGHT`, `DB_DFSM_WATCHDOG`, `DB_DFSM_FLUSH_ENABLE`, and `DB_DFSM_FLUSH_AUX_EVENT`.
- Render backend redundancy and disable masks: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GC_USER_RB_REDUNDANCY`, and `GC_USER_RB_BACKEND_DISABLE`.
- Graphics backend topology registers: `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, and `CC_RB_DAISY_CHAIN`. These describe pipe count, interleave size, bank count, shader-engine count, RBs per SE, compressed-fragment capacity, packed pipes, and related topology fields.
- Tile and macro-tile modes: `GB_TILE_MODE0` through `GB_TILE_MODE31` define `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE`, and `SAMPLE_SPLIT`; `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`.
- Color buffer and DCC controls: `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG` describe blend/fast-clear behavior, cache tag and FIFO sizing, memory arbitration weights, NACK handling, clock-gating bypasses, DCC overwrite-combiner behavior, and DCC cache sizing.

The `gc_rlcpdec` group covers RLC microcontroller, timer, load-balancing, clock-counting, and power-management state:

- Core RLC control/status: `RLC_CNTL`, `RLC_STAT`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_INT_STAT`, and `RLC_UCODE_CNTL`.
- RLC memory sleep and clock counters: `RLC_MEM_SLP_CNTL`, `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_LSB/MSB`, `RLC_CLK_COUNT_REFCLK_LSB/MSB`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`.
- GPM timers and threads: `RLC_GPM_TIMER_INT_0` through `RLC_GPM_TIMER_INT_3`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_CP_DMA_COMPLETE_T0`, `RLC_GPM_CP_DMA_COMPLETE_T1`, and `RLC_GPM_STAT`.
- Load balancing and dynamic CU power gating: `RLC_LB_CNTR_MAX`, `RLC_LB_CNTL`, `RLC_LB_CNTR_INIT`, `RLC_LOAD_BALANCE_CNTR`, `RLC_PG_DELAY_2`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_LB_PARAMS`, `RLC_THREAD1_DELAY`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, and `RLC_AUTO_PG_CTRL`.
- Clock-gating policy: `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` define memory-gating intervals, override bits for MGCG/CGCG/CGLS/MGLS/FGCG, idle thresholds, sleep modes, and CGCG ramp timing.
- RLC SERDES access: `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_NONCU_MASTER_BUSY_1`, `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, and the beginning of `RLC_SERDES_WR_CTRL`.

## Control Flow

This header chunk has no runtime control flow. Its effect is entirely through preprocessing and compilation: consumers include the GC 9.4.2 register headers, then use the macros to construct register values or extract field values during device initialization, power management, debug, reset, and status reporting.

Typical consumer flow is:

1. Select the GC 9.4.2 offset and mask headers for devices whose `amdgpu_ip_version(adev, GC_HWIP, 0)` is `IP_VERSION(9, 4, 2)`.
2. Read a 32-bit register through a SOC15 accessor, or start from a known golden/default value.
3. Use these `__SHIFT` and `_MASK` constants directly or through `REG_GET_FIELD`/`REG_SET_FIELD`.
4. Write the updated register back, or cache decoded topology/status values in driver state.

Visible consumers in the surrounding AMDGPU tree show these patterns. `gfx_v9_0.c` handles the GC 9.4.2 case by reading `mmGB_ADDR_CONFIG`, applying a GC 9.4.2 topology value, and decoding fields such as `NUM_PIPES`, `NUM_BANKS`, `MAX_COMPRESSED_FRAGS`, `NUM_RB_PER_SE`, `NUM_SHADER_ENGINES`, and `PIPE_INTERLEAVE_SIZE` into `adev->gfx.config`. The same file programs and queries RLC CGCG/CGLS state with `RLC_CGTT_MGCG_OVERRIDE__GFXIP_CGCG_OVERRIDE_MASK`, `RLC_CGTT_MGCG_OVERRIDE__GFXIP_CGLS_OVERRIDE_MASK`, `RLC_CGCG_CGLS_CTRL__CGCG_GFX_IDLE_THRESHOLD__SHIFT`, `RLC_CGCG_CGLS_CTRL__CGCG_EN_MASK`, and `RLC_CGCG_CGLS_CTRL__CGLS_EN_MASK`. It also reads `DB_DEBUG2` into `adev->gfx.config.db_debug2` for relevant ASICs.

The line range itself is purely declarative, but the implied runtime sequencing is important for several register families. RLC safe-mode and clock-gating updates must be sequenced so the RLC is in a stable state before changing CGTT/MGCG/CGCG bits. GB address configuration must be decoded before surface tiling and backend layout decisions depend on it. DB/CB debug and cache controls must be programmed consistently with golden settings and hardware workarounds before rendering workloads rely on compression, fast clear, HTILE, DCC, or cache arbitration behavior.

## State And Persistence Behavior

The macros do not store state. The state they describe lives in hardware registers or in driver fields populated from those registers.

State categories in this chunk include:

- Persistent hardware configuration until reset, power transition, or explicit reprogramming: most `CGTT_*`, `*_CGTT_*`, `DB_*`, `CB_*`, `GB_ADDR_CONFIG`, `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, `RLC_MEM_SLP_CNTL`, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_PG_*`, and `RLC_AUTO_PG_CTRL` fields.
- Driver-cached topology: fields decoded from `GB_ADDR_CONFIG` become `adev->gfx.config.gb_addr_config` and `adev->gfx.config.gb_addr_config_fields`, which persist in memory for later GFX setup and resource decisions.
- Status and observation state: `RLC_STAT`, `RLC_GPM_TIMER_STAT`, `RLC_SERDES_NONCU_MASTER_BUSY_1`, `RLC_INT_STAT`, `RLC_CLK_COUNT_STAT`, `RLC_GPM_STAT`, `RLC_DYN_PG_STATUS`, `RLC_CU_STATUS`, `DB_DFSM_TILES_IN_FLIGHT`, `DB_DFSM_PRIMS_IN_FLIGHT`, and SERDES read data expose transient hardware status.
- Command or handshake state: `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPM_THREAD_RESET`, `RLC_JUMP_TABLE_RESTORE`, `RLC_DYN_PG_REQUEST`, and `RLC_SERDES_WR_CTRL` are intended to drive hardware-side actions or select a read/write transaction.
- Counters and timestamps: RLC reference-clock, GPU-clock, GFXCLK, REFCLK, GPM timer, load-balance, and 32-bit GPU-clock fields are read to measure or synchronize hardware behavior.

No filesystem state, kernel heap allocation, locks, or reference counts are implemented here. Persistence risk comes from programming sticky hardware registers incorrectly, failing to restore them after suspend/resume/reset, or interpreting status fields as writable policy fields.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register header set:

- `gc_9_4_2_offset.h` supplies matching register offsets such as `mmGB_ADDR_CONFIG`, `mmDB_DEBUG2`, and `mmRLC_CGCG_CGLS_CTRL`.
- Other portions of `gc_9_4_2_sh_mask.h` define adjacent fields outside this chunk, including the start of `CGTT_SX_CLK_CTRL4` before line 19702 and the remainder of `RLC_SERDES_WR_CTRL` after line 22065.
- AMDGPU SOC15 access helpers and field macros provide the C-level read/modify/write operations that combine these shifts and masks with register values.
- `gfx_v9_0.c`, SDMA setup, power-management code, virtualization paths, XGMI/RAS handling, and firmware-loading conditionals depend on GC 9.4.2 identification and the associated register layout.

The data is a hardware specification contract. Macro names can look very similar across GC 9.x, 10.x, 11.x, and 12.x, but field widths and even field meanings can differ. Consumers must include the header for the active ASIC generation and use the matching offset header.

## Integration Points

Important integration points include:

- GFX topology setup: `GB_ADDR_CONFIG` and `GB_ADDR_CONFIG_READ` fields feed pipe, bank, SE, RB-per-SE, compressed-fragment, and interleave calculations in GFX initialization. These values affect memory tiling and render-backend assumptions.
- Golden settings and hardware workarounds: `DB_DEBUG2`, `CB_DCC_CONFIG`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ` appear in GFX golden-setting tables and initialization paths. The masks must match hardware so masked writes alter only intended bits.
- Clock gating and power management: CGTT controls, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_MEM_SLP_CNTL`, and `RLC_PG_*` integrate with `adev->cg_flags`, RLC safe-mode entry/exit, SR-IOV restrictions, suspend/resume, and runtime power-management code.
- Rendering backend operation: DB fields influence depth/stencil compression, fast-Z/stencil, HTILE synchronization, cache miss behavior, subtile grouping, DFSM flushing, watermarks, FIFO depths, and RMI cache policy. CB fields influence blending, fast clear, DCC, cache tags, FIFO sizing, arbitration, NACK handling, and color-cache prefetch.
- Surface layout and metadata: `GB_TILE_MODE*` and `GB_MACROTILE_MODE*` describe tile/macro-tile layouts that must stay consistent with userspace-visible tiling, kernel buffer metadata, SDMA settings, display usage, and firmware/golden values.
- RLC diagnostics and control: `RLC_STAT`, safe-mode fields, GPM timers, clock counters, SERDES master masks, SERDES busy/read-data fields, and interrupt status integrate with debug, bring-up, validation, and low-level power-gating flows.
- RAS and virtualization: GC 9.4.2-specific paths in the tree branch on `IP_VERSION(9, 4, 2)`. Incorrect field metadata can affect VF restrictions, RAS enablement, XGMI behavior, and firmware/ucode handling even when the macros are used indirectly.

## Risks

- A wrong shift or mask silently changes the wrong hardware bits. For this chunk, likely symptoms include broken clock gating, unstable RLC safe-mode transitions, incorrect render-backend topology, surface tiling corruption, depth/stencil rendering errors, or DCC/HTILE/cache behavior regressions.
- The range contains many debug and override fields with negative names such as `DISABLE_*`, `FORCE_*`, and `*_OVERRIDE`. Setting or clearing one bit with inverted semantics can turn off compression, bypass synchronization, force cache misses, disable clock gating, or mask a hardware workaround.
- `GB_ADDR_CONFIG`, `GB_TILE_MODE*`, and `GB_MACROTILE_MODE*` are topology/layout fields. Mismatches can compile cleanly but cause cross-engine disagreement between GFX, SDMA, display, firmware, and userspace about memory layout.
- RLC state is sensitive to ordering. Writes to `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_MEM_SLP_CNTL`, power-gating request registers, or SERDES controls should be done only in the expected safe-mode or idle context.
- Status fields and command fields are mixed in the same generated header. Treating status such as `RLC_STAT`, `RLC_GPM_STAT`, `RLC_DYN_PG_STATUS`, or SERDES busy/data registers as ordinary configuration can lead to meaningless writes or missed handshakes.
- Reserved and spare masks occupy many high or middle bits. Consumers doing raw writes instead of masked read/modify/write can disturb reserved bits and create ASIC-specific failures.
- The chunk starts and ends mid-register. The previous chunk owns the beginning of `CGTT_SX_CLK_CTRL4`; the next chunk owns the remainder of `RLC_SERDES_WR_CTRL`. Any merged per-file analysis must account for those split registers before making complete-register claims.
- Generated register headers should not be hand-edited casually. Updates should normally come from regenerated ASIC register specifications so offsets, masks, defaults, and comments remain synchronized.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU configurations that include GC 9.4.2 headers and `gfx_v9_0.c`, ensuring every referenced field macro resolves with the expected offset header.
- Static consistency checks that registers represented here have corresponding `mm*` entries in `gc_9_4_2_offset.h` and, where applicable, matching default/golden-setting coverage.
- Boot smoke tests on GC 9.4.2 hardware that initialize GFX, load RLC firmware, apply golden settings, read `GB_ADDR_CONFIG`, and populate `adev->gfx.config` without register access faults.
- Clock-gating tests that toggle MGCG/CGCG/CGLS/MGLS/FGCG support and verify `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_MEM_SLP_CNTL`, and CGTT controls report expected state through the driver clock-gating query path.
- Suspend/resume, GPU reset, and SR-IOV VF tests, because these paths stress whether persistent RLC, CGTT, DB, CB, and GB registers are restored or masked correctly.
- Rendering workloads that stress depth/stencil compression, fast-Z/stencil, HTILE, MSAA/EQAA, DCC, blending, fast clear, and tiled/macro-tiled surfaces. Visual corruption, VM faults, hangs, or performance cliffs are strong signals for bad DB/CB/GB field handling.
- SDMA and graphics interop tests that copy or render tiled buffers, because `GB_ADDR_CONFIG` and tile-mode fields must agree across engines.
- RLC diagnostic tests that read busy/status fields, capture GPU clock counts, exercise GPM timers/threads, and perform SERDES read sequences while checking `RLC_SERDES_RD_PENDING` and read-data registers.

### subset-b-002676: lines 22066-24623

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 22066-24623

## Purpose

This chunk is generated-style bitfield metadata for the AMD GC 9.4.2 graphics core, used by the AMDGPU driver and KFD bridge for Aldebaran-class GFX9.4.2 hardware. It defines `__SHIFT` and `_MASK` macros for fields in RLC, RMI, shader/SPI, compute-dispatch, and early `gc_shsdec` status/control registers. The definitions are compile-time constants only; consumers combine them with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, and packet builders instead of hard-coding bit positions.

The range starts in the tail of `RLC_SERDES_WR_CTRL`, covers a large RLC block, crosses into `gc_rmi_rmidec`, then into `gc_shdec` shader and compute registers, and ends partway through `gc_shsdec` at `SPI_WF_LIFETIME_LIMIT_9`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, storage objects, or runtime APIs in this range. The exposed interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the low bit of a register field.
- `REGISTER__FIELD_MASK` gives the unshifted 32-bit mask for the field.
- `REGISTER__DATA__SHIFT` and `REGISTER__DATA_MASK` indicate full-word payload registers.
- Address-block comments such as `gc_rmi_rmidec`, `gc_shdec`, and `gc_shsdec` identify hardware decode domains, not C namespaces.

Important register groups in this chunk include:

- RLC SERDES and GPM/SPM/SRM registers: `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, `RLC_GPM_GENERAL_0..15`, `RLC_GPM_SCRATCH_*`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_*`, `RLC_GPM_LOG_*`, `RLC_GPM_INT_*`, `RLC_SRM_*`, and `RLC_SRM_INDEX_CNTL_*`.
- RLC microcontroller, save/restore, and utility controls: `RLC_CSIB_*`, `RLC_CP_SCHEDULERS`, `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS*`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL2_CNTL`, `RLC_DS_CNTL`, `RLC_SEMAPHORE_*`, clock-capture registers, spare interrupts, and RLCV spare interrupt registers.
- RLC diagnostic/error-counting controls: `RLC_EDC_CNT`, `RLC_EDC_CNT2`, `RLC_DSM_CNTL`, `RLC_DSM_CNTLA`, `RLC_DSM_CNTL2`, and `RLC_DSM_CNTL2A` describe SEC/DED counters plus design-for-test RAM irritator and error-injection fields.
- RMI/RB memory interface controls in `gc_rmi_rmidec`: `RMI_GENERAL_CNTL*`, `RMI_GENERAL_STATUS`, `RMI_SUBBLOCK_STATUS0..3`, `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1/2`, `RMI_TCIW_FORMATTER0/1_CNTL`, `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS0..2`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, and `RMI_SPARE*`.
- Pixel/graphics shader programming registers in `gc_shdec`: `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO/HI_PS`, `SPI_SHADER_PGM_RSRC1/2_PS`, the 32-entry `SPI_SHADER_USER_DATA_PS_*` array, and equivalent resource/user-data groups for VS, GS/ES, HS/LS, and `SPI_SHADER_USER_DATA_COMMON_0..31`.
- Compute shader dispatch and resource registers: `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_LO/HI`, dispatch packet and scratch base addresses, `COMPUTE_PGM_RSRC1/2/3`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0..7`, `COMPUTE_TMPRING_SIZE`, restart/relaunch/wave-restore registers, checksum, and `COMPUTE_USER_DATA_0..15`.
- Early `gc_shsdec` controls: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_CONFIG_PS_CU_EN`, `SPI_WF_LIFETIME_CNTL`, and `SPI_WF_LIFETIME_LIMIT_0..9`.

## Control Flow

This header chunk has no executable control flow. Its behavior is via preprocessing: C files include the header, then compile these constants into register read-modify-write expressions, CP packet construction, debug register setup, golden-setting tables, or field decoders.

Typical runtime flow in consumers is:

1. Include `gc/gc_9_4_2_offset.h` for register offsets and `gc/gc_9_4_2_sh_mask.h` for field masks.
2. Build a register value with `REG_SET_FIELD` or extract a field with `REG_GET_FIELD`.
3. Write the value with SOC15 register helpers or emit it into a `PACKET3_SET_SH_REG` command stream.
4. Hardware persists, samples, or reports the corresponding register state until later programming, reset, or status clearing.

The local `gfx_v9_4_2.c` path shows this pattern for compute work: it emits `PACKET3_SET_SH_REG` packets for `regCOMPUTE_PGM_LO`, `regCOMPUTE_PGM_HI`, and `regCOMPUTE_USER_DATA_0`, then builds the dispatch initiator word with `REG_SET_FIELD(0, COMPUTE_DISPATCH_INITIATOR, COMPUTE_SHADER_EN, 1)` before a direct dispatch. `amdgpu_amdkfd_aldebaran.c` includes the same GC 9.4.2 mask header for KFD debug/trap register construction. Older same-name consumers in nearby GFX versions show how `RLC_SERDES_WR_CTRL` fields are commonly assembled for BPM/SERDES power and command operations.

## State And Persistence Behavior

The macros themselves are stateless and have no storage, lifetime, locking, or persistence behavior. They describe state that resides in GPU hardware registers and command packets.

State categories represented by this chunk include:

- Persistent configuration until reset or reprogramming: shader program resource registers, user-data registers, compute resource limits, thread-management masks, RLC UTCL1 controls, RMI arbitration/crossbar controls, and SPI wave lifetime limits.
- Per-dispatch or command-stream state: compute dimensions, start coordinates, thread counts, dispatch packet addresses, scratch bases, shader program base addresses, dispatch IDs, relaunch payloads, and user SGPR payloads.
- Volatile hardware status: SERDES master busy registers, SRM command FIFO status, RLC/RMI UTCL1 fault/retry/PRT status, RMI busy/error/subblock status, scoreboard counters, semaphore/interrupt indicators, and wave lifetime/EDC counts.
- Diagnostic and error-injection state: RLC and SPI DSM controls, SEC/DED counters, RAM irritator selections, inject-enable bits, and inject-delay fields. These are validation-oriented and can alter hardware behavior if programmed accidentally.
- Save/restore and power-management-related state: RLC SRM/ARAM/DRAM accessors, RLCV command/status, RLC static power-gating status, `RLC_PG_DELAY_3`, clock capture registers, and wave-restore addresses participate in low-level graphics microcontroller, reset, or debug flows rather than normal application state.

Because many fields are sticky or hardware-owned, consumers must follow the GC 9.4.2 register spec for clear-on-write, reserved-bit preservation, and reset/suspend/resume reinitialization. The header does not encode those semantics.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register set:

- `gc_9_4_2_offset.h` provides matching register offsets such as `regCOMPUTE_PGM_LO`, `regCOMPUTE_USER_DATA_0`, and RLC/RMI/SPI register symbols.
- Other generated GC 9.4.2 headers provide adjacent mask/default definitions outside this line range.
- AMDGPU SOC15 helpers, CP packet helpers, and register field macros provide the code-level operations that use these masks and shifts.
- `gfx_v9_4_2.c` depends on the header for Aldebaran GFX initialization, golden settings, compute-based VGPR/LDS clearing, RAS/UTC support, and wave-assignment diagnostics.
- `amdgpu_amdkfd_aldebaran.c` depends on the same generated register family for KFD debug/trap integration on Aldebaran.

The definitions are hardware-contract data. They must remain synchronized with the GC 9.4.2 register specification and with sibling offset/default headers. Similar macro names exist in GC 9.0, GC 9.2.1, GFX8, and later generations, but field layouts can differ; cross-generation substitution is unsafe even when names compile.

## Integration Points

Primary integration points are:

- Aldebaran GFX initialization and golden settings in `gfx_v9_4_2.c`, which include this header and use the same register namespace for chip-specific setup.
- Compute dispatch construction, especially `COMPUTE_PGM_LO/HI`, `COMPUTE_USER_DATA_*`, `COMPUTE_DIM_*`, and `COMPUTE_DISPATCH_INITIATOR`. These fields directly affect shader start address, dispatch dimensions, user SGPR payloads, scratch behavior, VMID, and wave scheduling.
- KFD/HSA integration. The KFD flat-memory documentation in the tree describes aperture mode selection in terms of `COMPUTE_DISPATCH_INITIATOR` fields and `SH_MEM_CONFIG`; Aldebaran KFD code includes this GC 9.4.2 mask header for debug and trap programming.
- RLC microcontroller workflows: GPM/SPM/SRM registers, SERDES write controls, scheduler bits, semaphores, spare interrupts, clock capture, and save/restore command/status fields integrate with graphics firmware, reset, power, and RAS flows.
- RMI/RB memory interface handling: VMID bypass, XNACK/UTCL1 controls, xbar and demux arbitration, scoreboard invalidation/status, TCIW formatter controls, and clock-control masks tie into memory translation, cache invalidation, render-backend traffic, and hang/fault diagnosis.
- Shader-stage programming through SPI resource registers and user-data arrays for PS, VS, GS/ES, HS/LS, common user data, and compute. These macros are the field-level contract for CP register programming and shader ABI setup.
- Diagnostics and validation through DSM/EDC and wave lifetime registers, which can be read for error counters or programmed to enable controlled test behavior.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. In this range that can corrupt shader resource setup, dispatch initiator words, CU/SIMD masks, VMID invalidation behavior, RLC save/restore commands, or RMI arbitration.
- The chunk mixes production control fields with debug, DSM, and error-injection fields. Accidentally setting inject-enable, irritator, force-stall, or debug-disable fields can create hangs, spurious RAS errors, or severe performance regressions.
- Reserved fields are explicitly represented in many registers. Consumers must preserve reserved bits when doing read-modify-write operations unless the hardware spec says otherwise.
- Several status fields may be sticky, clear-on-read, or clear-on-write depending on the underlying register. This header exposes only bit positions and cannot prevent destructive reads or incorrect clears.
- Compute dispatch fields are command-stream visible. Incorrect `COMPUTE_PGM_*`, scratch, user-data, resource-limit, thread-count, or initiator values can run the wrong shader address, misconfigure SGPR/VGPR allocation, break memory aperture selection, or hang a ring.
- RMI fields affect VMID bypass, XNACK handling, UTCL1 behavior, xbar/demux arbitration, and scoreboard invalidation. Misprogramming them can surface as GPUVM faults, invalidation timeouts, render-backend stalls, or hard-to-localize memory ordering bugs.
- Cross-generation names are deceptively similar. Reusing GC 9.0 or GFX8 assumptions for GC 9.4.2, especially around compute initiator, shader resource, RLC DSM/EDC, or RMI fields, can compile but misprogram Aldebaran hardware.
- Manual edits to this file are high risk because it is generated register metadata. Changes should generally come from regenerated AMD ASIC register sources.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU configurations that compile `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` with `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h`.
- Static consistency checks that registers in this chunk have corresponding offset symbols in `gc_9_4_2_offset.h` and that generated masks/shifts do not overlap unexpectedly within a register.
- Aldebaran boot and GFX initialization tests that apply golden settings, initialize RLC/CP/GFX blocks, and complete ring bring-up without invalid register access or timeout warnings.
- Compute dispatch smoke tests on GC 9.4.2 hardware, especially paths that program `COMPUTE_PGM_LO/HI`, `COMPUTE_USER_DATA_*`, `COMPUTE_DIM_*`, and `COMPUTE_DISPATCH_INITIATOR`.
- KFD process/debug tests that exercise trap enable/disable, wave launch modes, flat-memory aperture behavior, and VMID-specific debug state.
- Suspend/resume and GPU reset tests that verify RLC save/restore, SRM/RLCV command status, clock capture, semaphore, and power-gating related fields recover correctly.
- RAS/EDC diagnostics that read SEC/DED counters and verify DSM/error-injection controls are disabled in normal operation and only enabled in controlled validation.
- GPUVM/XNACK/invalidation stress tests that monitor RMI/RLC UTCL1 status, scoreboard status, busy bits, and fault/retry/PRT flags under memory pressure and preemption.
- Graphics and compute workloads that stress shader-stage user-data programming, scratch/LDS usage, CU masking, wave lifetime limits, render-backend memory traffic, and CP dispatch packet formation.

### subset-b-002677: lines 24624-27042

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 24624-27042

## Purpose

This chunk is generated register-field metadata for the AMD GC 9.4.2 graphics core, used by the Linux AMDGPU driver for Aldebaran-class hardware. It contains `#define` constants for field shifts and bit masks, not executable code. Consumers combine these definitions with the matching `gc_9_4_2_offset.h` register offsets and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

The range starts at the tail of `SPI_WF_LIFETIME_LIMIT_9`, covers SPI wave lifetime/status, load-balance, trap, arbitration, compute-queue, and compute-unit reservation fields, then enters the `gc_sqdec` address block. The SQ portion defines shader-queue configuration, SQC cache/DSM/error counters, timeout/debug/indirect wave access registers, shader instruction word layouts, SQ load-balance counters, EDC/RAS fields, thread-trace token layouts, write-exec address words, and the beginning of buffer/image resource descriptor formats through `SQ_IMG_RSRC_WORD1`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or variables in this chunk. The public surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's low bit.
- `REGISTER__FIELD_MASK` gives the unshifted bit mask within a 32-bit register or descriptor word.
- Full-width masks such as `SQ_IND_DATA__DATA_MASK`, `SQ_TIME_HI__TIME_MASK`, `SQ_TIME_LO__TIME_MASK`, `SQ_BUF_RSRC_WORD0__BASE_ADDRESS_MASK`, and `SQ_BUF_RSRC_WORD2__NUM_RECORDS_MASK` mark whole-word payloads.
- The `// addressBlock: gc_sqdec` comment marks a hardware decode block boundary, not a C namespace.

Important register groups in this range include:

- SPI wave and scheduling state: `SPI_WF_LIFETIME_STATUS_0..20`, `SPI_LB_CTR_CTRL`, `SPI_LB_CU_MASK`, `SPI_LB_DATA_*`, `SPI_CSQ_WF_ACTIVE_STATUS`, `SPI_CSQ_WF_ACTIVE_COUNT_0..7`, and `SPI_COMPUTE_WF_CTX_SAVE` expose wave lifetime, active wave counters, load-balance snapshots, and compute wave context-save status.
- SPI debug/trap and arbitration: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_GDBG_WAVE_CNTL3`, `SPI_GDBG_TRAP_DATA0/1`, and `SPI_ARB_CNTL_0` define trap enablement, per-VMID debug controls, wave launch/control fields, and arbitration weighting.
- SPI resource reservation: `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` define per-CU reservations for VGPR, SGPR, LDS, waves, barriers, enabled resource types, queue masks, and reserve-space-only behavior.
- SQ/SQC configuration and status: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, `SQ_FIFO_SIZES`, `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL*`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_TIMEOUT_CONFIG`, `SQ_TIMEOUT_STATUS`, `SH_CAC_CONFIG`, `SP_MFMA_PORTD_RD_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, and `GC_USER_SHADER_RATE_CONFIG`.
- DSM/error-injection and EDC counters: `SQ_DSM_CNTL*`, `SQC_DSM_CNTL*`, `SQC_EDC_FUE_CNTL`, `SQC_EDC_CNT2/3`, `SQC_EDC_PARITY_CNT3`, `SQC_EDC_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, and `SQ_EDC_FUE_CNTL`.
- UTCL1 and interrupt controls: `SQ_UTCL1_CNTL1`, `SQ_UTCL1_CNTL2`, `SQ_UTCL1_STATUS`, `SQ_FED_INTERRUPT_STATUS`, and `SQ_CGTS_CONFIG` describe shader-side translation-cache controls, fault/status bits, fed interrupt status, and clock-gating/test fields.
- Wave debug and commands: `SQ_HOSTTRAP_STATUS`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CONFIG1`, and `SQ_CMD` define the indirect wave/register access path and SQ command encoding.
- Shader instruction layouts: `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_INST`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP3*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA*` define bit positions for ISA instruction words.
- Thread-trace and descriptors: `SQ_THREAD_TRACE_WORD_*` macros define trace token fields for events, instructions, issue, perf, register writes, timestamps, wave IDs, PCs, and userdata. `SQ_WREXEC_EXEC_HI/LO`, `SQ_BUF_RSRC_WORD0..3`, and `SQ_IMG_RSRC_WORD0..1` define write-exec addressing and the start of shader buffer/image descriptor layouts.

## Control Flow

This header has no runtime control flow. Its only behavior is preprocessor substitution at compile time.

Runtime control flow appears in consumers:

1. GC 9.4.2-specific source includes `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h`.
2. Driver code selects a register instance, shader engine, shader array, CU, VMID, or XCC as needed.
3. It reads or writes a 32-bit register through SOC15 helpers.
4. It uses these shift/mask macros through `REG_SET_FIELD`, `REG_GET_FIELD`, or direct shifts to encode or decode individual hardware fields.

Concrete integration examples include `gfx_v9_4_2_init_sq()`, which sets `SQ_CONFIG1__DISABLE_XNACK_CHECK_IN_RETRY_DISABLE` when MEC firmware supports chained XNACK handling; `gfx_v9_4_2_debug_trap_config_init()`, which programs `SPI_GDBG_PER_VMID_CNTL` and clears `SPI_GDBG_TRAP_DATA0/1`; and `wave_read_ind()`, which constructs `SQ_IND_INDEX` from `WAVE_ID`, `SIMD_ID`, `INDEX`, and `FORCE_READ` before reading `SQ_IND_DATA`.

## State And Persistence Behavior

The macros themselves are stateless and persist only as compiled constants. The state they describe lives in GPU registers, shader descriptors, trace buffers, and status counters.

State categories represented here:

- Configuration state that persists until reprogrammed, reset, or power-cycled: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_CONFIG1`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_UTCL1_CNTL*`, `SPI_ARB_*`, `SPI_RESOURCE_RESERVE_*`, and trap-control registers.
- Volatile command/debug access: `SQ_CMD`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_TIME_HI/LO`, and `SQ_HOSTTRAP_STATUS`.
- Hardware counters and snapshots: `SPI_WF_LIFETIME_STATUS_*`, `SPI_CSQ_WF_ACTIVE_*`, `SPI_LB_DATA_*`, `SQ_LB_DATA*`, `SQC_EDC_*`, `SQ_EDC_*`, and `SQ_TIMEOUT_STATUS`.
- Fault and interrupt status: `SQ_UTCL1_STATUS`, `SQ_FED_INTERRUPT_STATUS`, EDC/FUE fields, host-trap pending status, and SQ timeout fields.
- Validation/destructive test controls: `SQ_DSM_CNTL*` and `SQC_DSM_CNTL*` contain stall, irritator, single-write, and error-injection fields. These are not ordinary performance tuning knobs.

Several consumer paths are explicitly stateful. `gfx_v9_4_2_enable_watchdog_timer()` programs `SQ_TIMEOUT_CONFIG` per shader engine under `grbm_idx_mutex`. `gfx_v9_4_2_query_sq_timeout_status()` iterates SE/SH/CU selections, reads `SQ_TIMEOUT_STATUS`, logs wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`, then writes zero to clear old status. Debug trap setup is VMID-scoped and protected by `srbm_mutex` while GRBM selection changes.

## Dependencies

This chunk depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h` for matching `reg*` register offsets.
- AMDGPU SOC15 accessors and field helpers that know how to combine these masks with register values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which includes this header for Aldebaran golden settings, SQ initialization, trap setup, RAS/EDC handling, watchdog timeout handling, and wave inspection.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, which routes GC 9.4.2 initialization and shared GFX v9 paths, including SQ command and wave debug patterns.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c`, which includes the same GC 9.4.2 offset/mask headers for KFD-facing Aldebaran behavior.

The definitions are hardware-contract data. Similar macro names exist in other GC generations, but layouts are not interchangeable; including the wrong ASIC header can compile and still program the wrong bits.

## Integration Points

Primary integration points are:

- Golden-register and ASIC initialization paths in `gfx_v9_4_2.c`; while not every register in this chunk is programmed by golden tables, the same generated header family supplies the field names and register layout for GC 9.4.2 setup.
- SQ initialization, especially `SQ_CONFIG1` XNACK-related fields gated on MEC firmware version.
- VMID-scoped debug trap setup through `SPI_GDBG_PER_VMID_CNTL`, `SPI_GDBG_TRAP_DATA0`, and `SPI_GDBG_TRAP_DATA1`.
- Wave timeout/RAS diagnostics through `SQ_TIMEOUT_CONFIG`, `SQ_TIMEOUT_STATUS`, `SQ_IND_INDEX`, and `SQ_IND_DATA`.
- RAS and EDC accounting through SQC and SQ EDC counter masks, including SEC/DED/FUE fields and per-block counter extraction.
- Thread-trace tooling and trace decoders that must interpret `SQ_THREAD_TRACE_WORD_*` token fields consistently with the hardware.
- Shader tooling, firmware, debuggers, and descriptor builders that use SQ instruction and resource descriptor field definitions to decode or construct GC 9.4.2 words.

## Risks

- Incorrect shift or mask values silently target wrong hardware bits. In this chunk that can break wave debug, SQ command execution, trap delivery, shader descriptor interpretation, watchdog handling, or RAS accounting.
- Some fields are write-sensitive or status-clear fields. For example, SQ timeout status is cleared by writes in consumer code; changing the field interpretation can hide real watchdog failures or leave stale status.
- DSM and error-injection fields are hazardous if used accidentally in production paths. Enabling inject/stall/single-write controls can create artificial faults or severe performance anomalies.
- Per-CU and per-VMID fields require correct instance selection and locking. Consumers already use `grbm_idx_mutex` and `srbm_mutex`; new users must preserve that pattern when programming selected shader engines, CUs, or VMIDs.
- Thread-trace records mix 16-bit-style and 32-bit-style token layouts and split fields across `1_OF_2`/`2_OF_2` words. Decoders must not assume a single flat token width.
- Instruction encoding and resource descriptor macros look like ordinary register masks but may describe ISA or memory descriptor words. Treating those as MMIO registers would be a category error.
- This file is generated metadata. Manual edits are likely to diverge from AMD register specifications and sibling generated headers.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU configurations that include GC 9.4.2 headers, especially `gfx_v9_4_2.c`, `gfx_v9_0.c`, and `amdgpu_amdkfd_aldebaran.c`.
- Static consistency checks that each register name in this chunk has a matching offset in `gc_9_4_2_offset.h`.
- Boot and GFX initialization on Aldebaran/GC 9.4.2 hardware, including golden-register programming and SQ initialization without invalid-register warnings.
- KFD compute queue smoke tests that exercise SQ command paths, trap setup, and VMID-scoped debug behavior.
- Watchdog/RAS tests that enable `SQ_TIMEOUT_CONFIG`, trigger or simulate timeout reporting, read wave state through `SQ_IND_INDEX`/`SQ_IND_DATA`, and verify `SQ_TIMEOUT_STATUS` clearing.
- RAS/EDC validation that reads SQC/SQ SEC, DED, and FUE counters and confirms values are decoded into the expected block names and counts.
- Shader debugger/profiler tests that decode `SQ_THREAD_TRACE_WORD_*` records and wave/instruction words into stable PC, timestamp, CU/SIMD/wave, register, event, and perf-counter data.
- Graphics/compute workloads that stress global memory, LDS, image/buffer descriptors, GDS interactions, trap handling, and XNACK retry behavior, since these paths depend on SQ/SPI fields covered by this chunk.

### subset-b-002678: lines 27043-29425

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 27043-29425

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core, used by Aldebaran-class AMDGPU paths. It defines `__SHIFT` and `_MASK` constants for shader resource descriptor words, shader queue cache controls, texture cache/texture pipe blocks, address-translation L2 blocks, L2 TLB performance counters, and VM L2 protection-fault reporting.

The definitions are compile-time data only. They let driver code use symbolic field names with macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, and SOC15 register accessors instead of hard-coding bit positions. The matching offsets live in `gc_9_4_2_offset.h`; this file supplies the bit-level layout for those registers.

The range begins at the tail of the `SQ_IMG_RSRC_WORD1` descriptor group, covers `SQ_IMG_RSRC_WORD2..7`, sampler descriptors, flat scratch and M0 index words, SQC UTCL1 controls, then moves through address blocks `gc_tcdec`, `gc_tcpdec`, `gc_tpdec`, `gc_utcl2_atcl2dec`, `gc_utcl2_atcl2pfcntldec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_l2tlbdec`, `gc_utcl2_l2tlbpldec`, `gc_utcl2_l2tlbprdec`, and ends inside `gc_utcl2_vml2pfdec` after `VM_L2_MM_GROUP_RT_CLASSES`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or global variables in this range. The API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit of a field.
- `REGISTER__FIELD_MASK` gives the unshifted 32-bit field mask.
- Full-word fields such as `SQ_IMG_RSRC_WORD7__META_DATA_ADDRESS_MASK`, `TCA_BURST_MASK__ADDR_MASK_MASK`, `TA_SCRATCH__SCRATCH_MASK`, `ATC_L2_CACHE_DATA1__VIRTUAL_PAGE_ADDRESS_LOW_MASK`, `ATC_L2_CACHE_DATA2__PHYSICAL_PAGE_ADDRESS_MASK`, and `VM_L2_PROTECTION_FAULT_ADDR_LO32__LOGICAL_PAGE_ADDR_LO32_MASK` represent entire register words.
- Address block comments identify hardware decode domains, not C namespaces.

Important macro families in this chunk include:

- Shader image resource descriptors: `SQ_IMG_RSRC_WORD2..7` fields describe image width, height, depth, pitch, destination component selects, base and last mip levels, swizzle mode, resource type, base array, array pitch, metadata address fragments, metadata layout/alignment flags, max mip, compression enablement, color transform, and lost color/alpha bits.
- Shader sampler descriptors: `SQ_IMG_SAMP_WORD0..3` cover clamp modes, anisotropy ratio/threshold/bias/override, depth compare function, unnormalized coordinates, degamma controls, coordinate truncation, filter modes, LOD min/max/bias, mip/filter selectors, PRT zero blending, border color pointer, and border color type.
- Scratch and indexing descriptors: `SQ_FLAT_SCRATCH_WORD0/1` describe flat scratch size and offset, while `SQ_M0_GPR_IDX_WORD` describes the M0-relative GPR index and source/destination relative-addressing flags.
- SQC UTCL1 controls and status: `SQC_ICACHE_UTCL1_CNTL1/2`, `SQC_DCACHE_UTCL1_CNTL1/2`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS` define GPUVM page-size defaults, permission and response modes, client ID, VMID invalidation fields, force-miss and in-order diagnostics, FIFO/cache depth reductions, bypass and snoop controls, performance event selection, and fault/retry/PRT status.
- `gc_tcdec` texture cache fabric controls: `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CHAN_STEER_0..5`, `TCP_ADDR_CONFIG`, `TCP_EDC_CNT`, `TCP_EDC_CNT_NEW`, `TC_CFG_L1/L2_*_POLICY*`, `TC_CFG_*_VOLATILE`, `TCI_*`, `TCC_*`, `TCA_*`, and `TCX_*` cover cache invalidation/status, channel steering, address swizzle configuration, load/store/atomic policy tables, volatile hints, clock-gating/chicken bits, FIFO/cache depth, writeback/invalidate behavior, SRAM EDC counters, redundancy/disable controls, soft reset, burst controls, and DSM/error-injection controls.
- `gc_tcpdec` TCP watch and UTCL1 controls: `TCP_WATCH0..3_ADDR_H/L/CNTL` provide address-watchpoint high/low address, mask, VMID, ATC, mode, and valid fields. `TCP_GATCL1_CNTL`, `TCP_UTCL1_CNTL1/2`, `TCP_UTCL1_STATUS`, `TCP_DSM_CNTL*`, and `TCP_PERFCOUNTER_FILTER*` define TCP-side translation-cache invalidation, response/fault modes, performance filters, and memory error-injection controls.
- `gc_tpdec` texture pipe controls: `TD_STATUS`, `TD_EDC_CNT`, `TD_DSM_CNTL*`, `TD_SCRATCH`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_FEATURE_CNTL`, `TA_STATUS`, `TA_SCRATCH`, `TA_DSM_CNTL*`, and `TA_EDC_CNT` describe texture data/address FIFO state, EDC counters, determinism disables, filter and anisotropy behavior, LOD and cube-map controls, texture atomic/coalescing features, busy bits, scratch words, and DSM/error-injection controls.
- `gc_utcl2_atcl2dec` address translation cache L2 controls: `ATC_L2_CNTL*`, `ATC_L2_CACHE_DATA0..3`, `ATC_L2_STATUS*`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, `ATC_L2_CGTT_CLK_CTRL`, `ATC_L2_CACHE_{4K,32K,2M}_DSM_INDEX`, `ATC_L2_CACHE_{4K,32K,2M}_DSM_CNTL`, and `ATC_L2_MM_GROUP_RT_CLASSES` describe translation request crediting, host/device request modes, cache invalidation/update modes, bank/way selection, cached virtual/physical page data, uncorrectable-error status, clock and memory light-sleep controls, per-page-size DSM indexing, SED/DED counters, and RT class grouping.
- `gc_utcl2_atcl2pfcntldec` and `gc_utcl2_atcl2pfcntrdec` performance counters: `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, `ATC_L2_PERFCOUNTER_LO`, and `ATC_L2_PERFCOUNTER_HI` select ATC L2 events, event ranges, modes, enables, clears, trigger fields, saturation behavior, result low/high words, and compare values.
- `gc_utcl2_l2tlb*` TLB support: `L2TLB_TLB0_STATUS`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*`, `UTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`, `L2TLB_PERFCOUNTER*_CFG`, `L2TLB_PERFCOUNTER_RSLT_CNTL`, `L2TLB_PERFCOUNTER_LO`, and `L2TLB_PERFCOUNTER_HI` describe TLB busy state, GPUVA/VMID translation-assist request and response fields, and L2TLB performance measurement.
- `gc_utcl2_vml2pfdec` VM L2 controls: `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_STATUS`, dummy-page-fault controls and addresses, `VM_L2_PROTECTION_FAULT_CNTL*`, `VM_L2_PROTECTION_FAULT_STATUS`, protection-fault address/default-address registers, identity aperture low/high registers, identity physical offset registers, `VM_L2_CNTL4`, and `VM_L2_MM_GROUP_RT_CLASSES` define page-table cache mode, PDE/PTE force-miss controls, retry/fault behavior, page migration and PRT controls, fault identity, busy bits, and identity mapping apertures.

## Control Flow

This header chunk has no runtime control flow. Including code obtains constants that are folded by the C preprocessor and compiler into register read/modify/write expressions, table initializers, and field extraction code.

The typical runtime pattern in consumers is:

1. Include `gc_9_4_2_offset.h` and `gc_9_4_2_sh_mask.h` for the target ASIC.
2. Select an offset with `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, or generated `reg*` names.
3. Build or decode a field with `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD`.
4. Read or write the hardware register with AMDGPU SOC15 accessors.

The main direct consumers in this tree are `amdgpu/gfx_v9_4_2.c` and `amdgpu/amdgpu_amdkfd_aldebaran.c`. `gfx_v9_4_2.c` includes this header for Aldebaran golden settings, RAS/EDC field tables, UTC EDC counter walking, and register programming. `amdgpu_amdkfd_aldebaran.c` includes it for KFD debug/trap and TCP address-watch programming. Other GC and MMHUB files show similar field patterns for sibling hardware generations, but they must not be treated as layout-compatible without checking the exact ASIC header.

## State And Persistence Behavior

The macros themselves are stateless and do not allocate or persist memory. They describe state held elsewhere:

- Descriptor state: `SQ_IMG_RSRC_WORD*`, `SQ_IMG_SAMP_WORD*`, `SQ_FLAT_SCRATCH_WORD*`, and `SQ_M0_GPR_IDX_WORD` describe GPU-visible descriptor words consumed by shader execution. The descriptor values persist in command buffers, kernel/user queues, or memory objects managed by higher layers, not in this header.
- Persistent hardware configuration: cache policy registers, channel steering, `TCP_UTCL1_CNTL*`, `SQC_*_UTCL1_CNTL*`, `TCI_CNTL_*`, `TCC_CTRL*`, `TCA_CTRL`, `TA_CNTL*`, `ATC_L2_CNTL*`, `VM_L2_CNTL*`, and protection fault controls remain active until reset, power transition, resume reprogramming, or another register write changes them.
- Volatile status: `TCP_STATUS`, SQC/TCP UTCL1 status registers, `TCI_STATUS`, `TD_STATUS`, `TA_STATUS`, `ATC_L2_STATUS*`, `L2TLB_TLB0_STATUS`, and `VM_L2_STATUS` expose current hardware condition and should be treated as observation points.
- Error counters and fault latches: `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, ATC L2 DSM counter fields, and `VM_L2_PROTECTION_FAULT_STATUS` represent hardware error accounting or fault capture. Consumer code may clear counters after reading; `gfx_v9_4_2_query_sram_edc_count()` explicitly reads EDC registers and writes zero to clear them.
- Debug/watch state: `TCP_WATCH0..3_*` registers persist configured watchpoints for KFD debug until overwritten or cleared by the debug path.
- DSM/error-injection state: many `*_DSM_CNTL*` and `*_CACHE_*_DSM_CNTL` fields intentionally inject, delay, or count SRAM errors. These are validation features and should not be enabled during normal operation.

No disk state, kernel heap lifetime, locks, or reference counts are implemented in this file. Synchronization and lifetime rules belong to consuming code. For example, `gfx_v9_4_2_query_sram_edc_count()` uses `grbm_idx_mutex` while selecting instances, but this header only supplies the masks used by its field helpers.

## Dependencies

This chunk depends on the generated GC 9.4.2 register family and AMDGPU SOC15 helper conventions:

- `gc_9_4_2_offset.h` supplies the matching `reg*` offsets for the field names defined here.
- AMDGPU register helpers in the SOC15 stack provide `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `SOC15_REG_OFFSET`, `WREG32*`, and `RREG32*` usage.
- `gfx_v9_4_2.c` relies on this header for golden setting names such as `regTCP_CHAN_STEER_0..5`, `regTA_CNTL_AUX`, `regTCP_UTCL1_CNTL1`, and `regTCI_CNTL_3`, and for RAS field extraction from EDC counter registers covered by this chunk.
- `amdgpu_amdkfd_aldebaran.c` relies on `TCP_WATCH0_CNTL` field masks for address watchpoint mode, mask, and valid bits, plus TCP watch register offsets from the matching offset header.
- RAS code depends on `SOC15_REG_FIELD()` expansion for `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, and ATC L2 DSM counters.

The definitions are hardware-contract data. They must match the GC 9.4.2 register specification and sibling offset definitions. Similar names across GC 9.x, GC 10.x, GC 11.x, GC 12.x, and MMHUB headers are not interchangeable because field widths and semantics can differ.

## Integration Points

Primary integration points include:

- Aldebaran graphics initialization in `gfx_v9_4_2.c`: golden setting arrays program TCP channel steering, texture address control, TCP UTCL1 behavior, and TCI control fields. Incorrect masks here can misroute cache channels or apply invalid tuning values during GPU bring-up.
- KFD debugging in `amdgpu_amdkfd_aldebaran.c`: `kgd_gfx_aldebaran_set_address_watch()` builds `TCP_WATCH0_CNTL` using the `MODE`, `MASK`, and `VALID` fields, writes `TCP_WATCH*_ADDR_H/L`, and returns the control word for the caller to program. The chunk's watch register fields are therefore part of user-visible GPU debugging behavior.
- SRAM EDC/RAS in `gfx_v9_4_2.c`: RAS tables read TCP, TCI, TCC, TCA, TCX, TD, and TA EDC counters using fields defined in this range. Query paths aggregate SEC/DED counts and clear counters after reads.
- UTC EDC/RAS in `gfx_v9_4_2.c`: `gfx_v9_4_2_utc_blocks` maps ATC L2 cache page-size DSM index/control registers to bank/way/memory iteration logic and uses the `SEC_COUNT`, `DED_COUNT`, and `WRITE_COUNTERS` fields for SED/DED accounting.
- Shader descriptor construction and decoding: while this source tree may not directly build all `SQ_IMG_RSRC_*` and `SQ_IMG_SAMP_*` fields in the GC 9.4.2 driver file, those macros represent the ABI between shader-visible descriptor words and the hardware texture/image/sampler units.
- VM fault handling and diagnostics: `VM_L2_*` fields align with the GFXHUB/MMHUB-style fault reporting model used elsewhere in AMDGPU. The status and address fields identify client ID, VMID, read/write/atomic nature, permission/mapping errors, VF/VFID, and logical/default physical fault addresses.
- Performance tooling: ATC L2 and L2TLB performance counter fields expose event selection, trigger, clear, enable, result, and compare layouts for low-level performance or debug paths.

## Risks

- A wrong mask or shift silently targets the wrong bits. Since these macros are normally used inside helper macros, many mistakes compile cleanly and only appear as bad hardware behavior.
- Cache and translation controls are high impact. Incorrect `SQC_*_UTCL1`, `TCP_UTCL1_*`, `ATC_L2_*`, or `VM_L2_*` fields can break GPUVM translation, fault handling, invalidation ordering, or cache coherency.
- Golden settings rely on exact field layouts. Bad `TCP_CHAN_STEER_*`, `TA_CNTL_AUX`, `TCP_UTCL1_CNTL1`, or `TCI_CNTL_3` definitions can regress boot, multi-die routing, texture determinism, or cache behavior on Aldebaran.
- Address watchpoint fields are user-debug visible through KFD. Incorrect `TCP_WATCH0_CNTL` mask, VMID, mode, ATC, or valid bits can miss debug watchpoints, trigger on the wrong address range, or leave a watchpoint active unexpectedly.
- Descriptor fields are ABI-like. Errors in `SQ_IMG_RSRC_WORD*` or `SQ_IMG_SAMP_WORD*` definitions can corrupt image dimensions, mip selection, swizzle mode, compression metadata, sampler filtering, LOD, border color, or PRT behavior.
- DSM and error-injection fields are dangerous outside validation. Accidental writes to `*_ENABLE_ERROR_INJECT`, `*_IRRITATOR_*`, `WRITE_COUNTERS`, or delay-selection fields can inject faults, disturb counters, or mask real hardware errors.
- EDC counter fields may be read-clear or explicitly cleared by consumers. Adding diagnostics around them without preserving existing read/clear order can lose error evidence or double count errors.
- Cross-generation copy/paste is unsafe. GC 9.4.2 names resemble GC 9.4.x, MMHUB, and later GCVM names, but offsets, prefixes, and fields differ enough that a wrong include can produce valid C and invalid register programming.
- Generated register headers should usually be regenerated from AMD register metadata. Manual edits are hard to audit and risk desynchronizing masks from offsets and defaults.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU configurations that compile `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`, proving all `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_FIELD` references still resolve.
- Static consistency checks that every register name referenced by this chunk has a matching offset in `gc_9_4_2_offset.h` and that field masks do not overlap unexpectedly within a register unless the hardware spec requires aliases.
- Aldebaran boot and graphics initialization tests that apply golden settings without invalid register access warnings, especially `TCP_CHAN_STEER_0..5`, `TA_CNTL_AUX`, `TCP_UTCL1_CNTL1`, and `TCI_CNTL_3`.
- KFD debug watchpoint tests that set, trigger, and clear `TCP_WATCH0..3` entries across different masks and modes, verifying the address-low alignment shift and valid bit behavior.
- RAS/EDC tests that inject or simulate SRAM errors and confirm `TCP_EDC_CNT_NEW`, `TCI_EDC_CNT`, `TCC_EDC_CNT*`, `TCA_EDC_CNT`, `TCX_EDC_CNT*`, `TD_EDC_CNT`, `TA_EDC_CNT`, and ATC L2 DSM counters report SEC/DED counts in the expected fields and clear correctly after query.
- GPUVM fault tests that exercise invalid mappings, permission faults, retry/no-retry faults, dummy-page fault behavior, PRT/page migration behavior, and protection-fault status/address capture.
- Cache invalidation and coherency stress tests that exercise SQC/TCP UTCL1 invalidation, ATC L2 invalidation/update modes, TCC writeback/invalidate, and L2TLB translation assist under memory pressure.
- Graphics and compute workloads that stress image resources, samplers, compressed metadata, mip/array selection, anisotropic filtering, texture atomics, and tiled/virtual memory paths.
- Suspend/resume and GPU reset tests to verify persistent hardware configuration covered by this chunk is restored or reinitialized by the owning driver paths.

### subset-b-002679: lines 29426-31946

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 29426-31946

## Purpose

This chunk is generated-style register field metadata for the AMD GC 9.4.2 graphics core, focused on GPUVM/UTCL2/VML2 control, virtual-memory context setup, VM invalidate engines, SR-IOV/XGMI aperture controls, and graphics-core CAC power/activity accounting. It provides symbolic bit shifts and masks for 32-bit hardware registers so AMDGPU code can use `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, SOC15 register entries, and generated offset headers instead of open-coded bit positions.

The range begins at the tail of `VM_L2_MM_GROUP_RT_CLASSES`, covers VM L2 reserved-client, parity, clock-gating, ECC, EDC, and performance-counter registers, then moves through `gc_utcl2_vml2vcdec` VM context and invalidation registers. It continues into shared hypervisor/PF/VC VM aperture registers and ends in the `gccacind` indirect CAC register block with weight and accumulator fields through `GC_CAC_ACC_PA0`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or storage objects declared in this header slice. The exported interface is the generated macro contract:

- `REGISTER__FIELD__SHIFT` is the field low-bit position.
- `REGISTER__FIELD_MASK` is the unshifted field mask.
- Full-register fields such as page-table base low/high words, logical page ranges, CAC override values, and CAC accumulators use `0xFFFFFFFFL` masks.
- Address-block comments such as `gc_utcl2_vml2pldec`, `gc_utcl2_vml2prdec`, `gc_utcl2_vml2vcdec`, `gc_utcl2_vmsharedhvdec`, `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, and `gccacind` group related hardware decode domains.

Important register groups in this chunk include:

- VM L2 controls: `VM_L2_MM_GROUP_RT_CLASSES`, `VM_L2_BANK_SELECT_RESERVED_CID*`, `VM_L2_CACHE_PARITY_CNTL`, `VM_L2_CGTT_CLK_CTRL`, and `VM_L2_CGTT_BUSY_CTRL` define VM L2 routing class bits, reserved read/write client IDs, parity test controls, and clock-gating timing/override behavior.
- UTC/VML2 ECC and EDC: `VML2_MEM_ECC_INDEX`, `VML2_WALKER_MEM_ECC_INDEX`, `UTCL2_MEM_ECC_INDEX`, matching `*_ECC_CNTL` registers, matching `*_ECC_STATUS` registers, `UTCL2_EDC_MODE`, and `UTCL2_EDC_CONFIG` define indexed ECC counter/error-injection access, SEC/DED counters, UCE/FED status bits, and EDC propagation/bypass modes.
- VM L2 performance counters: `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`, and `MC_VM_L2_PERFCOUNTER_LO/HI` define event selection, mode, enable, counter selection, clear, and 64-bit result access.
- VM contexts 0-15: each `VM_CONTEXTn_CNTL` has the same field layout for enable, page-table depth/block size, retry behavior, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `VM_CONTEXTS_DISABLE` exposes per-context disable bits.
- VM invalidation engines 0-17: each engine has semaphore, request, acknowledge, and low/high address-range registers. Requests carry per-VMID invalidate masks, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status clearing, and optional request logging. ACK registers expose per-VMID completion and semaphore state.
- VM context address registers: `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXTn_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_*` describe page-directory base and legal logical page range fields for contexts 0-15.
- SR-IOV and XGMI VM sharing: `MC_VM_FB_SIZE_OFFSET_VF0..VF15`, `MC_SHARED_ACTIVE_FCN_ID`, `MC_VM_XGMI_GPUIOV_ENABLE`, `MC_SHARED_VIRT_RESET_REQ`, `VM_PCIE_ATS_CNTL`, and `VM_PCIE_ATS_CNTL_VF_*` define VF framebuffer apertures, active function identity, PF/VF XGMI GPU-IOV enable bits, virtualization reset request bits, and ATS enable/STU fields.
- PF and VC aperture setup: `MC_VM_FB_OFFSET`, system aperture default address LSB/MSB, `MC_VM_STEERING`, cacheable DRAM and local HBM address windows, `MC_VM_APT_CNTL`, `MC_VM_XGMI_LFB_CNTL/SIZE`, framebuffer/AGP/system aperture bounds, and `MC_VM_MX_L1_TLB_CNTL` define memory windows, host mapping, LFB sizing, ATC/L1 TLB behavior, MTYPE, and advanced driver model flags.
- GC CAC indirect registers: `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, many `GC_CAC_WEIGHT_*` registers, and `GC_CAC_ACC_*` registers define activity-counter block/signal selection, thresholds, force disable, override selection/value, per-block signal weights, and 32-bit accumulators for BCI, CB, CP, DB, GDS, IA, LDS, and PA in this slice.

## Control Flow

This file has no runtime control flow. Its behavior is compile-time substitution: including C files combine the masks and shifts with generated offsets from `gc_9_4_2_offset.h` and with AMDGPU register helpers.

Typical consumer flow is:

1. Include `gc/gc_9_4_2_offset.h` and `gc/gc_9_4_2_sh_mask.h` for the target ASIC.
2. Read or construct a register value with SOC15 helpers.
3. Use `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD` with these macro names to encode or decode hardware fields.
4. Write the register value, poll an ACK/status register, or report decoded state.

Concrete local examples include `amdgpu/gfx_v9_4_2.c`, which includes this exact header and uses the UTC ECC masks through `SOC15_REG_FIELD(VML2_MEM_ECC_CNTL, SEC_COUNT)`, `SOC15_REG_FIELD(VML2_MEM_ECC_CNTL, DED_COUNT)`, corresponding walker/UTCL2 fields, and `REG_SET_FIELD(..., WRITE_COUNTERS, 1)` while querying or clearing RAS counters. The common GC/GMC pattern is also visible in files such as `gmc_v9_0.c`, where a VM invalidate request is constructed with `VM_INVALIDATE_ENG0_REQ` fields for per-VMID invalidation, flush type, L2/L1 invalidation, and protection-fault clearing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. The state they describe lives in GPU registers and changes through MMIO or indirect register access.

Important state categories are:

- Long-lived VM configuration: VM context controls, page-table base/start/end address registers, context disable bits, aperture bounds, framebuffer/AGP locations, local HBM and cacheable DRAM windows, TLB controls, ATS enables, and XGMI/GPU-IOV enables remain in hardware until reprogrammed, reset, or lost across power transitions.
- Transient invalidation synchronization: `VM_INVALIDATE_ENG*_SEM`, `*_REQ`, `*_ACK`, and address-range fields are part of request/acknowledge cache-invalidation protocol. Consumers must issue the request with the correct VMID bits and poll or consume matching ACK/semaphore state.
- RAS/error state: ECC index/control registers select indexed memory blocks and expose SEC/DED counters. `*_ECC_STATUS` UCE/FED bits are status/clear fields used by GC 9.4.2 RAS paths; local code writes `0x3` to clear `UTCL2_MEM_ECC_STATUS`, `VML2_MEM_ECC_STATUS`, and `VML2_WALKER_MEM_ECC_STATUS` after logging or reset.
- Test and injection state: `ENABLE_ERROR_INJECT`, `ENABLE_SINGLE_WRITE`, `INJECT_DELAY`, `DSM_IRRITATOR_DATA`, `TEST_FUE`, forced VM L2 parity mismatch fields, EDC bypass/propagation fields, and clock-gating overrides can intentionally alter hardware behavior. These are not ordinary production toggles.
- Counter state: VM L2 performance counters and GC CAC accumulator registers collect hardware activity until cleared, reselected, reset, or overwritten. CAC weights and threshold/select fields influence how activity is counted or used by power-management logic.

There is no disk state, kernel allocation, reference counting, or lock ownership in this header. Persistence concerns are exclusively hardware persistence and whether driver init, suspend/resume, reset, SR-IOV mode changes, and RAS recovery paths restore the intended register state.

## Dependencies

This chunk depends on the rest of the generated GC 9.4.2 register family:

- `gc_9_4_2_offset.h` provides the matching register offsets and indirect register IDs.
- Neighboring `gc_9_4_2_sh_mask.h` chunks define adjacent fields used by the same generated header.
- AMDGPU helper macros and types such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `SOC15_REG_ENTRY`, `SOC15_REG_ENTRY_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and indirect-register helpers interpret these masks.
- GC 9.4.2 code in `amdgpu/gfx_v9_4_2.c` depends on the VML2/UTCL2 ECC fields matching the hardware RAS counter layout.
- GPUVM/GMC/GFXHUB code depends on the VM context and invalidation field names matching the register layout, even when similar field groups are defined under generation-specific prefixes in other ASIC families.
- Power-management and power-tune paths use CAC indirect registers in other generations through `CGS_IND_REG_GC_CAC`; the `gccacind` block here provides the GC 9.4.2 layout for equivalent weight, select, override, and accumulator registers.

The data is a hardware contract. It should stay synchronized with AMD's generated register sources, the matching offset header, and the firmware/SMU expectations for GC 9.4.2/Aldebaran-class devices.

## Integration Points

Primary integration points are:

- GFX RAS handling in `gfx_v9_4_2.c`: `gfx_v9_4_2_utc_blocks` uses `VML2_MEM_ECC_*`, `VML2_WALKER_MEM_ECC_*`, and `UTCL2_MEM_ECC_*` index/control fields to walk indexed UTC/VML2 memory blocks, read SEC/DED counts, log sub-block names, and clear counters with the `WRITE_COUNTERS` bit. RAS status query/reset paths read and clear the three `*_ECC_STATUS` registers.
- VM fault and invalidation machinery: VM invalidate fields match the common AMDGPU pattern for building per-VMID invalidation requests, selecting flush behavior, invalidating L2 PTE/PDE levels and L1 PTEs, and tracking per-engine ACK state.
- GPUVM context programming: VM context control fields and page-table base/start/end fields are used by hub initialization code to configure VMID contexts, retry/default fault handling, page-table geometry, and aperture ranges.
- SR-IOV and virtualization: VF framebuffer size/offset registers, active function ID, VF/PF reset request bits, ATS enable bits, and XGMI GPU-IOV enable bits integrate with PF/VF setup and virtualized memory isolation.
- XGMI and large-framebuffer setup: `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` provide PF LFB region and size fields analogous to MMHUB code that derives XGMI physical address ranges from LFB region/size registers.
- Memory aperture and host mapping setup: PF/VC shared aperture registers feed framebuffer, AGP, system aperture, cacheable DRAM, local HBM, host-mapping, TLB, MTYPE, ATC, and advanced-driver-model configuration.
- Performance and power instrumentation: VM L2 perfcounter fields and GC CAC weight/accumulator fields are the low-level register definitions used by profiling, diagnostics, firmware-mediated power logic, or power-management tables.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. For VM context and invalidation registers, that can produce stale translations, missed TLB flushes, incorrect protection-fault behavior, or broken page-table geometry.
- VM invalidate engines are replicated 18 times with identical field layouts. Copying a field from the wrong engine or computing engine spacing incorrectly can make one VMID appear flushed while another engine owns the outstanding request.
- Context address registers split logical/page-directory addresses across low/high words with narrow high masks on start/end ranges. Consumers must preserve address unit and width semantics; treating these as raw byte addresses or full 64-bit masks would misprogram apertures.
- ECC and EDC fields include both production RAS counters/status and destructive test/injection controls. Accidentally setting `ENABLE_ERROR_INJECT`, parity force bits, EDC bypass, or `TEST_FUE` can create false RAS events or real correctness loss.
- Counter clear behavior is register-specific. GC 9.4.2 RAS code clears UTC counters by writing a value containing `WRITE_COUNTERS` and clears status registers with `0x3`; new consumers should not assume all status or count fields are clear-on-read.
- SR-IOV, ATS, and XGMI GPU-IOV controls affect isolation and address translation for PF/VF functions. Misprogramming VF enable bits, active function IDs, reset requests, or ATS state can leak access, strand a VF, or break peer/CPU-connected memory access.
- CAC registers are indirect and power-sensitive. Incorrect weights, thresholds, or override values can skew activity accounting and power-management behavior even if graphics workloads otherwise run.
- Cross-generation names are similar but not interchangeable. GC 9.4.2, MMHUB, GCVM, and later GC variants use related `VM_CONTEXT*` and `VM_INVALIDATE_ENG*` names with prefix/layout differences; including the wrong ASIC header can compile but program invalid fields.
- The file is generated metadata. Manual edits are high risk and should normally be made by regenerating the ASIC register headers from the authoritative hardware source.

## Test Signals

Useful validation signals include:

- Build coverage for GC 9.4.2/Aldebaran code paths that include `gc_9_4_2_sh_mask.h`, especially `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c`.
- Static consistency checks that every register named in this chunk has a matching offset or indirect index in `gc_9_4_2_offset.h`.
- RAS tests on GC 9.4.2 hardware that query and reset GFX RAS counts, confirm SEC/DED increments are decoded from the expected `VML2_*` and `UTCL2_*` fields, and confirm `*_ECC_STATUS` bits are logged and cleared.
- GPUVM stress tests that allocate/free BOs across VMIDs, force page-table updates, issue invalidations, and verify no stale mappings, VM fault storms, or invalidate timeout messages occur.
- SR-IOV validation with PF and multiple VFs that checks VF framebuffer apertures, ATS enable behavior, virtual reset requests, and XGMI GPU-IOV enable state across VF reset and host suspend/resume.
- XGMI and large-framebuffer tests that verify peer-memory visibility and LFB region/size calculations after boot and reset.
- Power/performance instrumentation tests that read VM L2 perf counters and GC CAC accumulators, then verify counter selection, clear, and accumulation behavior remain stable under graphics and compute workloads.
- Runtime smoke tests across reset, suspend/resume, and RAS recovery paths, because these registers are mostly persistent hardware configuration rather than ordinary local variables.

### subset-b-002680: lines 31947-33003

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 31947-33003

## Scope

This chunk is the final section of the generated AMD GC 9.4.2 shift/mask header. It starts in the tail of the `GC_CAC_ACC_PA0` field definitions, continues through the late `gccacind` clock/activity counter metadata, covers power and throttle pattern masks, then defines the `secacind` and `sqind` shader-engine/shader-queue debug layouts through the SQ interrupt word formats. The range ends at the file's closing `#endif`.

The file contains preprocessor constants only. There are no C functions, structs, enums, variables, allocations, locks, callbacks, or executable branches in this range.

## Purpose

The purpose of this section is to expose the bit-level contract between AMDGPU/KFD code and GC 9.4.2 hardware registers. Each register field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field in a 32-bit value.

The matching register offsets and indirect indices are supplied by the companion GC 9.4.2 offset header. This mask header is consumed by AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, by MMIO accessors such as `RREG32_SOC15`/`WREG32_SOC15`, and by indirect register access paths for `gccacind`, `secacind`, and `sqind`.

## Important APIs, Types, And Macro Families

The API surface is the generated macro namespace. Important families in this chunk are:

- `GC_CAC_ACC_*` accumulator fields for graphics clock/activity counter blocks. These include PA, PC, SC, SPI0..5, EA0..5, RMI0, UTCL2/ATCL20..24, SQ lower/upper accumulator pairs, SX/SXRB, TA, TCC0..4, TCP0..4, TD0..5, VGT0..2, WD0, CU0..13, BCI1, UTCL2 router0..9, UTCL2 VML20..24, and UTCL2 walker0..4. Most are full 32-bit `ACCUMULATOR_31_0` fields; SQ accumulators split into lower 32 bits and upper 8 bits for a 40-bit accumulator view.
- `GC_CAC_WEIGHT_*` fields for packed 16-bit signal weights. The range covers EA, RMI, UTCL2/ATCL2, UTCL2 router, UTCL2 VML2, and UTCL2 walker weights, usually two signal weights per register with low and high halfword masks.
- `GC_CAC_OVRD_*` fields for block-specific override select/value bitmaps. The override width varies by block: single-bit domains such as IA/PC/SC/CU/SX/SXRB/TA/WD, wider block groups such as SPI/TD/EA, the 9-bit SQ override pair, and 10-bit UTCL2 router select/value fields.
- `EDC_STALL_PATTERN_*`, `PCC_STALL_PATTERN_*`, `PCC_THROT_REINCR_FIRST_PATN_*`, `PCC_THROT_DECR_FIRST_PATN_*`, `PWRBRK_STALL_PATTERN_CTRL`, `PWRBRK_STALL_PATTERN_*`, `PCC_PWRBRK_HYSTERESIS_CTRL`, and `FIXED_PATTERN_PERF_COUNTER_*`. These describe encoded stall/throttle lookup patterns, power-break hysteresis, and fixed-pattern performance counter fields.
- `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL` in the `secacind` block. These provide shader-engine CAC force-disable, threshold, block ID, signal ID, and full-width override selection/value fields.
- `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_WAVE_VALID_AND_IDLE`, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_INST_DW0/DW1`, `SQ_WAVE_IB_DBG0/DBG1`, `SQ_WAVE_FLUSH_IB`, `SQ_WAVE_TTMP0..15` except `TTMP2` in this visible range, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`. These define the SQ indirect wave debug/register-save view.
- `SQ_INTERRUPT_WORD_AUTO_CTXID`, `SQ_INTERRUPT_WORD_AUTO_HI/LO`, `SQ_INTERRUPT_WORD_CMN_CTXID`, `SQ_INTERRUPT_WORD_CMN_HI`, and `SQ_INTERRUPT_WORD_WAVE_CTXID/HI/LO`. These define packed SQ interrupt payload fields for thread-trace/timestamp/overflow events, common SE/encoding metadata, and wave-specific data such as shader array, privilege, wave ID, SIMD ID, CU ID, VM ID, and data payload bits.

There are no local type definitions. The effective "types" are 32-bit hardware register values interpreted through these shift/mask constants.

## Control Flow

This header has no runtime control flow. The runtime model is:

1. GC 9.4.2-specific code includes the generated offset and mask headers.
2. A caller selects a direct or indirect register offset, such as an `ixGC_CAC_*`, `ixSE_CAC_*`, or `ixSQ_WAVE_*` index from the matching offset header.
3. The caller composes or decodes a register value using the `__SHIFT` and `_MASK` macros in this file.
4. AMDGPU/KFD access helpers perform the actual MMIO or indirect read/write, and the hardware interprets the resulting packed value.

For CAC and throttle/power-pattern fields, sequencing is supplied by power-management, SMU, or initialization code that owns the relevant programming table. For SQ wave fields, debug and hang-analysis paths select a wave through SQ indirect access, then read these indexes to snapshot wave state. For SQ interrupt words, interrupt handlers decode payload words produced by hardware.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. The hardware fields they describe are stateful:

- CAC control, weight, and override fields persist in GPU registers until reset, power transition, reinitialization, or explicit reprogramming. Accumulator fields are hardware-updated counters whose reset/clear behavior is controlled by CAC hardware and surrounding driver sequences.
- SQ accumulator lower/upper pairs represent wider hardware counters. Consumers must treat the lower and upper reads as a coherent snapshot problem if hardware can update them between reads.
- PCC, EDC, and PWRBRK pattern/hysteresis/counter fields affect throttle behavior and expose performance or stall accounting. Some fields are durable configuration, while fixed-pattern counters and status-like fields are hardware-updated telemetry.
- `SE_CAC_CNTL` and override registers are shader-engine CAC configuration. These settings are hardware-owned and tied to the current ASIC power/performance configuration.
- SQ wave registers expose live execution state for a selected wave: mode bits, status/trap bits, hardware placement, GPR/LDS allocation, wait counters, PC, instruction dwords, instruction-buffer state, TTMP registers, M0, and EXEC. Values can change as waves execute, halt, trap, drain, or are context-saved.
- SQ interrupt word fields describe payloads delivered by interrupt/context-ID hardware. They are not persistent driver storage; they are decoded at interrupt handling time.

The header does not encode access permissions or side effects. A full-width mask may describe readback state, command data, or a scratch/debug value; it does not mean arbitrary writes are safe.

## Dependencies

This chunk depends on the generated GC 9.4.2 register database staying synchronized across:

- `gc_9_4_2_sh_mask.h`, which supplies the field masks and shifts researched here.
- The companion `gc_9_4_2_offset.h`, which supplies the matching `ix*`, `mm*`, or `reg*` register identifiers.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`, which derive field names from the generated macro convention.
- SOC15 direct register addressing for ordinary GC registers and indexed/indirect access mechanisms for `gccacind`, `secacind`, and `sqind`.
- Power-management/SMU/CAC programming code that selects CAC blocks/signals, weights, overrides, and throttle patterns.
- GFX debug and reset-diagnostics code that reads SQ wave state through SQ indirect registers.
- KFD interrupt handling and trap/context-save code that relies on generation-specific SQ wave status, trap, allocation, and interrupt payload bit positions.

Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU hardware metadata and has no Ceph filesystem behavior.

## Integration Points

The primary integration point is the generated AMD GPU register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level integration points include:

- GFX/SMU initialization and power-tuning paths that program CAC counters, weights, overrides, throttle patterns, power-break controls, and fixed-pattern performance counters.
- Driver code that reads CAC accumulators for activity, power, or diagnostics, including multi-register SQ accumulator reads.
- Shader-engine CAC configuration through `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL`.
- Debugfs, GPU reset, and hang-dump paths that select SQ waves and read `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, allocation registers, PC/instruction words, IB status/debug, TTMP, M0, and EXEC.
- KFD interrupt processing for SQ interrupt payloads. The same `SQ_INTERRUPT_WORD_*` layout pattern appears in GFX9 KFD code, where interrupt context IDs are decoded into thread-trace, overflow, wave ID, SIMD, CU, SE, privilege, and encoding information.
- KFD CWSR/trap handler assembly, which carries parallel constants for SQ wave status/trap/allocation behavior because save/restore code manipulates hardware wave state directly.

## Risks And Edge Cases

- The range starts mid-register at `GC_CAC_ACC_PA0`; the preceding line(s) from the prior chunk are needed to reconstruct the full `PA0` shift/mask pair in the merged per-file report.
- Header/offset mismatch is the main correctness risk. Pairing GC 9.4.2 masks with another GC generation's offset header can compile while programming the wrong fields.
- CAC override widths vary by block. Reusing an override mask from a similar block can overwrite adjacent fields or leave part of an override value unprogrammed.
- SQ accumulator lower/upper fields form a wider counter. Non-atomic reads can produce torn values if hardware updates the accumulator between lower and upper reads.
- Power/throttle pattern programming is performance- and stability-sensitive. Incorrect EDC/PCC/PWRBRK patterns, hysteresis, or first-pattern fields can cause unwanted throttling, power excursions, misleading counters, or hangs.
- SQ wave state is volatile and indirect. Callers must select the intended wave and tolerate races with wave execution, halt, trap, replay, context save/restore, or invalid wave slots.
- SQ interrupt word layouts are generation-sensitive. Similar names across GC generations do not guarantee identical payload packing, especially for context-ID versus high/low split formats.
- Reserved or unnamed bits are not documented by these macros. Read-modify-write sequences should preserve unrelated bits unless the ASIC programming sequence explicitly requires full-register writes.
- Full-width masks such as `0xFFFFFFFFL` occur for accumulators, override values, PC/instruction words, TTMP/M0/EXEC, and wave-slot bitmaps. Full-width masks are not proof that software owns every bit for writes.

## Test And Validation Signals

Useful validation is mostly build, static, and hardware coverage:

- Build coverage for AMDGPU and KFD paths that include the GC 9.4.2 offset/mask headers and use `REG_SET_FIELD`/`REG_GET_FIELD` with these names.
- Generated-header consistency checks that every field has a matching shift/mask pair, masks align with shifts, and register names match the companion GC 9.4.2 offset header.
- Static checks for non-overlapping fields inside each register, with expected exceptions for full-width data/counter registers and documented aliases.
- Power-management smoke tests on GC 9.4.2 hardware that initialize CAC, throttle, and power-break registers, then survive idle/load transitions, suspend/resume, and GPU reset.
- Activity-counter tests that verify CAC accumulators and fixed-pattern counters change plausibly under idle, graphics, and compute workloads, and that SQ upper/lower accumulator reads are handled coherently.
- SQ wave debug tests that capture wave dumps and decode mode, status, trap status, hardware ID, allocation, wait counters, PC, instruction dwords, TTMP/M0, and EXEC fields without malformed output.
- KFD interrupt tests that trigger thread-trace, timestamp, overflow, and wave-related interrupts and validate `SQ_INTERRUPT_WORD_*` decoding against known payloads.
- CWSR/trap save/restore tests for workloads that exercise trap, halt, replay, ECC/error, allocation, TTMP, and EXEC state bits.
