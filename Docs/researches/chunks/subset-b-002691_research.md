# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 14504-16929

## Purpose

This chunk is a generated AMD GC 9.4.3 register field mask header range. It provides C preprocessor constants for command processor, shader processor interface, HQD/MQD queue, and texture cache/TCP register fields. Each field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro, letting AMDGPU code compose and decode 32-bit hardware register values without embedding raw bit positions.

The range starts at `CP_ME1_PIPE1_INT_CNTL`, after the adjacent `CP_ME1_PIPE0_INT_CNTL` family has already begun in the previous chunk, and ends inside `TCP_UTCL1_CNTL2`, before `TCP_UTCL1_STATUS` appears in the next lines. The content is declarative hardware metadata rather than executable code. Its correctness matters because consumers normally combine these masks with companion GC 9.4.3 register offset headers and AMD register helpers such as field set/get macros around MMIO or indirect register reads and writes.

## Major Register Areas Covered

The opening section covers command processor MEC/ME interrupt enable and status fields for `CP_ME1_PIPE1_INT_CNTL` through `CP_ME2_PIPE3_INT_CNTL`, followed by matching `CP_ME1_PIPE0_INT_STATUS` through `CP_ME2_PIPE3_INT_STATUS` groups and aggregate debug status registers `CP_ME1_INT_STAT_DEBUG` and `CP_ME2_INT_STAT_DEBUG`. These families expose queue and pipe events such as compare-query status, dequeue requests, CP ECC errors, SUA violations, graphics page faults, WRM poll timeouts, privileged register faults, opcode errors, timestamps, reserved-bit errors, and generic interrupt lanes.

The next command processor block defines priority, program-counter start, interrupt routine start, context, VMID, CPC interrupt, indirect-cache, preemption, queue status, and ECC/error reporting fields. Important register groups include `CP_ME*_PIPE_PRIORITY_CNTS`, per-pipe priorities, `CP_*_PRGRM_CNTR_START`, `CP_*_INTR_ROUTINE_START`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME*`, `CP_VMID_RESET`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CP_VMID_PREEMPT`, `CP_PQ_STATUS`, `CP_CPC_IC_*`, `CP_MEC*_F32_INT_DIS`, `CP_VMID_STATUS`, and CPC/CPF/CPG correctable and uncorrectable error status low/high registers.

The `xcd0_gc_cppdec2` address block adds scheduler ring doorbell controls and command processor diagnostic/error injection controls. It includes `CP_RB_DOORBELL_CONTROL_SCH_0` through `_SCH_7`, `CP_RB_DOORBELL_CLEAR`, CPF/CPG/CPC DSM control families, `CP_EDC_FUE_CNTL`, graphics MQD base/control fields, ring buffer status, CPG/CPC/CPF UTCL1 fault-status fields, shader dispatch control, soft reset control, and CPC graphics control.

The `xcd0_gc_spipdec` address block describes SPI arbitration, wave/debug, scratch, queue reset, and compute-unit resource reservation fields. It includes `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_CDBG_SYS_*`, workload pipe percentages for graphics, HP3D, and compute queues, graphics debug wave/trap/per-VMID controls, scratch address check/status, reset/debug controls, compute queue reset, `SPI_RESOURCE_RESERVE_CU_0` through `_CU_15`, matching enable registers, compute wavefront context save controls, and `SPI_ARB_CNTL_0`.

The `xcd0_gc_cpphqddec` address block is the largest part of the chunk. It defines HQD/HPD/MQD queue-management fields for graphics and compute queues: HQD graphics control/status, persistent state, pipe and queue priority, scheduling quantum, packet queue base/read/write pointers, doorbell control, packet queue control, indirect buffer base/control, IQ timer/read pointer, dequeue/offload controls, semaphore and message type, atomic pre-operation registers, HQ scheduler/status/control pairs, EOP base/control/read/write/event fields, context-save addresses and sizes, GDS resource state, HQD error bits, EOP write-pointer memory, AQL control/dispatch IDs, and MQD base/control fields.

The final `xcd0_gc_tcpdec` block covers TCP watchpoints, GATCL1 controls, DSM controls, clock controls, and UTCL1 control fields. It defines four TCP watch address/control groups with address, VMID, ATC, mode, valid, and mask fields; cache/TLB invalidation and force-miss fields in `TCP_GATCL1_CNTL`; ATC EDC count fields; TCP DSM irritator selection/single-write controls; TCP clock-gating disable fields in `TCP_CNTL2`; UTCL1 GPUVM response, invalidation, force miss, cache-size, and FIFO-depth controls in `TCP_UTCL1_CNTL1`; and the beginning of `TCP_UTCL1_CNTL2` fields for spare bits, MTYPE override, line-valid state, GPUVM invalidation mode, force snoop, forced invalidate ack, 2M-to-64K fragmentation, and thrashing controls.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the macro namespace:

- `*_SHIFT` constants give the bit offset for a register field.
- `*_MASK` constants give the 32-bit field mask.
- Register comments such as `//CP_HQD_PQ_CONTROL` and address block comments such as `// addressBlock: xcd0_gc_cpphqddec` preserve generated grouping information.

Consumers are expected to include this file with the matching GC 9.4.3 offset definitions and then use the macros through AMDGPU register helpers or direct bit operations. The names are part of the source-level hardware binding for this ASIC generation; renaming or changing a value breaks callers even though the header itself has no linker-visible symbols.

## Control Flow

This header has no runtime control flow. The effective flow is compile-time and caller-driven:

1. AMDGPU source includes the GC 9.4.3 offset and mask headers.
2. The caller chooses a register and field macro for a specific graphics, command processor, SPI, HQD, or TCP programming path.
3. Register helper macros shift, mask, insert, or extract field values.
4. The caller performs MMIO, indexed, or other hardware register access using the companion register offset.

The repeated interrupt, doorbell, HQD, and resource-reservation families imply external loops or table-driven setup code, but this file does not encode those loops. It also does not encode access type, reset value, write-one-to-clear behavior, ordering requirements, or locking.

## State and Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GC 9.4.3 hardware registers and persists according to hardware and driver lifecycle rules.

Command processor interrupt and status bits represent live events, enables, queue faults, ECC/error states, VMID state, preemption state, and diagnostics. Doorbell and ring/MQD/HQD fields describe persistent queue configuration such as base addresses, sizes, read/write pointers, doorbell routing, active state, priorities, scheduling quantum, context-save addresses, EOP buffers, and AQL dispatch tracking. SPI fields describe arbitration/debug state and reserved compute-unit masks. TCP fields describe watchpoint state, cache/TLB invalidation behavior, UTCL1 response and fault behavior, and clock/power gating controls.

Programmed values can survive until a later driver write, queue teardown, context restore, power transition, suspend/resume reinitialization, GPU reset, or firmware-driven sequence changes them. This header does not enforce validation or sequencing; callers must avoid writing reserved bits and must respect side effects documented by the hardware specification.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it must stay synchronized with AMD's generated GC 9.4.3 register database and the matching offset/header files under the same `asic_reg/gc` tree. Integration points include:

- AMDGPU command processor initialization, interrupt setup, and interrupt-status decoding for ME/MEC pipes, CPC, CPF, and CPG.
- Ring, doorbell, VMID, MQD, HQD, AQL, EOP, packet queue, indirect buffer, and context-save setup paths for graphics and compute queues.
- GPU fault and hang diagnostics that decode ECC, UTCL1, GPF, privilege, opcode, reserved-bit, and HQD error status fields.
- SPI debug, wave trap, compute queue reset, arbitration, and CU resource reservation programming.
- TCP watchpoint programming, UTCL1 invalidation/fault controls, cache/TLB behavior, DSM/error-injection support, and clock-gating controls.

Because many macros are consumed via token-pasting field helpers, the exact `REGISTER__FIELD` spelling is an API contract for source consumers. Numeric correctness also depends on using a GC 9.4.3 offset definition with the GC 9.4.3 mask definition; mixing ASIC generations can silently target wrong fields.

## Risks and Edge Cases

The primary risk is bitfield drift between this generated header and the hardware specification. A wrong shift or mask can enable the wrong interrupt, miss a fatal error, misprogram a doorbell, corrupt a queue pointer field, reserve the wrong compute units, or change TCP/UTCL1 cache behavior. These failures often appear as hangs, missed interrupts, VM faults, bad preemption, or misleading diagnostics rather than clean compile errors.

Repeated register families create review risk. ME1/ME2 pipe interrupt groups, doorbell scheduler controls, SPI CU reservation registers, and HQD queue fields differ mostly by register number, so generator or copy errors can be hard to spot manually. Several fields are full-width address, pointer, dispatch ID, or reserved masks (`0xFFFFFFFFL`), so callers must use appropriate 32-bit register access types and pair high/low address halves correctly.

The chunk boundaries are partial. `CP_ME1_PIPE0_INT_CNTL` belongs to the preceding chunk, while `TCP_UTCL1_CNTL2` continues immediately before later TCP status and DSM2 definitions. Merge tooling should preserve this exact range and not treat either adjacent family as completely covered by this document alone.

The header does not distinguish control, status, sticky status, clear-on-write, read-only, write-only, or debug/test-only fields. That is especially important for interrupt status, ECC status, soft reset, DSM/FUE/error injection, dequeue/offload, watchpoint, and UTCL1 invalidation fields, where incorrect read-modify-write behavior can lose events or cause hardware side effects.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Build AMDGPU with GC 9.4.3 support enabled to catch syntax errors, duplicate definitions, and consumers expecting different macro names.
- Compare this range against the authoritative GC 9.4.3 register database and matching offset header to verify every field name, shift, mask, width, and register grouping.
- Exercise command submission on GC 9.4.3 hardware, including graphics and compute queues, doorbells, VMID assignment, MQD/HQD setup, AQL queues, EOP handling, indirect buffers, preemption, and queue teardown.
- Validate interrupt enable/status handling with normal workloads and fault-injection paths for CP ECC, GPF, privileged register, opcode, reserved-bit, timestamp, dequeue, and generic interrupts.
- Run suspend/resume, GPU reset, and hang-recovery scenarios to catch stale queue, context-save, EOP, soft-reset, and UTCL1 state.
- Use debug or bring-up tests for SPI wave/trap state, compute queue reset, CU resource reservation masks, TCP watchpoints, UTCL1 invalidation/fault controls, and DSM/FUE error-injection fields where hardware access is available.
