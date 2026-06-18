# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 12148-14604

## Purpose

This chunk is generated AMD GC 9.2.1 register bitfield metadata. It contains no executable C code; its interface is a sequence of `#define` constants that publish hardware register field bit positions (`__SHIFT`) and masks (`_MASK`). AMDGPU, AMDKFD, and power-management code pair these constants with register offsets from `gc_9_2_1_offset.h` to compose, preserve, write, and decode MMIO register values for Vega-era graphics and compute blocks.

The selected range starts in the command processor decode block with ring-buffer VMID/write-pointer/doorbell fields, covers command processor interrupt, ECC, queue, VMID, context, and power controls, crosses `addressBlock: gc_cppdec2` for scheduler doorbells and CP reset/status fields, then covers `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, and the start of `gc_tcpdec`. It ends after the first `TCP_GATCL1_CNTL` fields, so later TCP cache-control fields are left to the next chunk.

Although this repository path is under `ceph-client`, this file is GPU driver hardware metadata and has no distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or C control-flow constructs in this range. The macro contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- Consumers combine the shift/mask macros with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` from `gc_9_2_1_offset.h`, then use AMD register access helpers and read-modify-write patterns.

Major register groups in this chunk:

- CP ring-buffer and doorbell controls: `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB*_BASE`, `CP_RB*_BASE_HI`, `CP_RB*_CNTL`, `CP_RB*_RPTR_ADDR`, `CP_RB*_RPTR_ADDR_HI`, `CP_RB*_ACTIVE`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and scheduler-specific `CP_RB_DOORBELL_CONTROL_SCH_0` through `_SCH_7`. These define VMIDs, queue base addresses, write/read pointer addresses, buffer sizing, cache policy, read-pointer update controls, doorbell offsets, enable/hit bits, and doorbell address ranges.
- CP/CPC/CPG fault and interrupt controls: `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS_RING0/1/2`, `CP_ME1_PIPE0-3_INT_CNTL`, `CP_ME2_PIPE0-3_INT_CNTL`, matching `*_INT_STATUS` registers, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, and `CP_HPD_UTCL1_*`. Common fields cover dequeue requests, ECC, SUA violations, GPF, WRM poll timeouts, privileged instruction/register errors, opcode errors, timestamps, reserved-bit errors, generic interrupts, UTCL1 fault/retry/PRT detection, and VMID/address context for faults.
- CP power, reset, context, and microcode entry controls: `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1/2`, `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START`, `CP_CE/PFP/ME/MEC*_INTR_ROUTINE_START`, `CP_CPC_IC_BASE_*`, and `CP_CPC_IC_OP_CNTL`. These encode clock halt bits, memory light/deep sleep knobs, sub-block enables, soft reset selectors, context limits, IQ wait timers, program-counter and interrupt-routine starts, CPC instruction-cache base/VMID/cache policy, and cache invalidate/prime status bits.
- Queue scheduling, priority, and VMID controls: `CP_ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_ME1/ME2_PIPE*_PRIORITY`, `CP_PQ_WPTR_POLL_CNTL`, `CP_PQ_WPTR_POLL_CNTL1`, `CP_PQ_STATUS`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_MEC1/2_F32_INT_DIS`, `CP_CPC_GFX_CNTL`, `CP_GFX_MQD_CONTROL`, `CP_GFX_MQD_BASE_ADDR*`, `CP_MQD_BASE_ADDR*`, and `CP_MQD_CONTROL`. These describe priority counters, queue masks, write-pointer polling, VMID reset/preempt/status vectors, interrupt-disable bits, graphics queue mapping, and MQD fetch/processing controls.
- SPI arbitration, debug, trap, and resource reservation fields in `gc_spipdec`: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_CDBG_SYS_GFX`, `SPI_CDBG_SYS_HP3D`, `SPI_CDBG_SYS_CS0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_TRAP_MASK`, `SPI_GDBG_WAVE_CNTL2/3`, `SPI_GDBG_TRAP_DATA0/1`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_0` through `_15`, `SPI_RESOURCE_RESERVE_EN_CU_0` through `_15`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`. These fields tune pipeline arbitration, wave limits, compute/debug trap mode, compute queue reset, per-CU reservation of VGPR/SGPR/LDS/waves/barriers, reservation enable/type/queue masks, and compute wavefront context-save status.
- HQD/HPD queue descriptor fields in `gc_cpphqddec`: `CP_HQD_GFX_CONTROL`, `CP_HQD_GFX_STATUS`, `CP_HPD_ROQ_OFFSETS`, `CP_HPD_STATUS0`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_*`, `CP_HQD_IB_*`, `CP_HQD_IQ_*`, `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_OFFLOAD`, `CP_HQD_SEMA_CMD`, `CP_HQD_MSG_TYPE`, atomic preop registers, HQ scheduler/status/control registers, `CP_HQD_EOP_*`, context-save address/size registers, `CP_HQD_GDS_RESOURCE_STATE`, `CP_HQD_ERROR`, and `CP_HQD_AQL_CONTROL`. These macros define the persistent state and live status for hardware queues, packet queues, indirect buffers, interrupt queues, end-of-pipe queues, context save/restore, GDS resource ownership, AQL controls, and detailed queue error reporting.
- DIDT/CAC/EDC/throttle fields in `gc_didtdec` and `gc_gccacdec`: `DIDT_IND_INDEX`, `DIDT_IND_DATA`, `DIDT_INDEX_AUTO_INCR_EN`, `GC_CAC_CTRL_1/2`, `GC_CAC_AGGR_*`, `PCC_PERF_COUNTER`, `GC_CAC_SOFT_CTRL`, `GC_DIDT_CTRL0/1/2`, `GC_DIDT_WEIGHT`, `GC_EDC_CTRL`, `GC_EDC_THRESHOLD`, `GC_DIDT_DROOP_CTRL*`, `GC_EDC_DROOP_CTRL`, `GC_THROTTLE_CTRL`, and CAC/SE indirect index/data windows. These govern current/activity counter capture, dynamic inductive droop throttling, electrical design current controls, droop thresholds, power weights, PCC throttling, and indirect register access.
- TCP watchpoint/cache fields in `gc_tcpdec`: `TCP_WATCH0-3_ADDR_H`, `TCP_WATCH0-3_ADDR_L`, `TCP_WATCH0-3_CNTL`, and the visible start of `TCP_GATCL1_CNTL`. These describe four texture/cache watchpoint address/mask/VMID/ATC/mode/valid slots and cache behavior flags such as invalidate-all-VMID, force miss, force in-order, and reduced FIFO/cache depth.

Field names are hardware-descriptive. `*_EN` and `*_ENABLE` fields gate behavior, `*_STATUS` fields expose live or sticky status, `*_HIT` and `*_UPDATED` fields report doorbell events, `*_BASE*` and `*_ADDR*` fields carry aligned addresses, `*_HI` fields carry high address bits, `*_RPTR`/`*_WPTR` fields are queue read/write pointers, and full-width `0xFFFFFFFFL` fields usually represent data, counters, indirect windows, or opaque scheduler/control payloads.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by driver code that includes the GC 9.2.1 offset and shift/mask headers:

1. ASIC-specific driver code selects a register by its `mm*` offset macro.
2. The driver composes or decodes individual fields using the `__SHIFT` and `_MASK` macros from this header.
3. The driver performs MMIO reads or writes through AMDGPU register helpers, often with read-modify-write preservation for unrelated and reserved bits.
4. Hardware blocks, firmware, CP/MEC microcode, RLC, KFD queue management, debug tooling, or power-management flows provide the actual sequencing, polling, reset, and interrupt handling.

The chunk describes fields used in stateful flows such as queue setup, MQD load/processing, doorbell enablement, write-pointer polling, VMID reset/preemption, interrupt enable/status handling, UTCL1 fault diagnosis, compute queue reset, SPI trap/debug control, HQD dequeue/offload/EOP processing, context save/restore, GDS ownership, and DIDT/EDC throttling. It does not encode the legal programming order, required delays, register access type, firmware ownership, or reset/power-gating constraints.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state accessed through GC 9.2.1 registers.

The represented hardware state is highly persistent and live at the device level: ring-buffer bases and pointers, doorbell mappings and hits, interrupt masks and sticky status, ECC first-occurrence metadata, VMID reset/preempt vectors, CP clock/memory sleep controls, MQD/HQD queue descriptors, HQD packet/IB/IQ/EOP pointers, context-save addresses and sizes, GDS resource allocation, SPI wave/debug/trap configuration, per-CU resource reservations, DIDT/EDC/CAC power and throttle settings, and TCP watchpoint controls. Values may survive until changed by the driver, reset by GPU reset, cleared by queue teardown, lost during suspend or power-gating, or advanced asynchronously by hardware.

Many fields in this chunk are not durable configuration values. Doorbell hit bits, queue-active bits, interrupt status bits, fault-detected bits, processing/busy flags, EOP empty/available fields, queue-idle fields, and cache-primed fields can be live, sticky, write-one-to-clear, or self-clearing depending on the hardware definition. Full-width data and indirect windows are especially sensitive because the macro alone does not indicate whether a register is read-only, write-only, latched, indexed, or hardware-owned.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h`, which provides matching register offsets and base indices. The same generated ASIC register database also has enum/default-value material used by nearby GFX9 code.

Known include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`

GC 9.2.1 is also selected through GFX9 ASIC-specific paths such as `gfx_v9_0.c`, which contains Vega12 golden-setting tables and ASIC dispatch. Integration points include GFX hub setup, Vega12 power-management register access, graphics/compute queue initialization, AMDKFD MQD/HQD programming, command processor interrupt handling, GPU reset/recovery, VMID management, doorbell configuration, debug/trap support, profiling or register-dump tooling, and hardware validation scripts.

This chunk is expected to be used with offset macros from the same ASIC generation. Mixing it with another GC 9.x shift/mask or offset header can still compile because names are often similar, but the resulting register writes can target wrong fields or incompatible bit layouts.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong literal in a `__SHIFT` or `_MASK` macro silently changes hardware programming and may only fail on the GC 9.2.1 ASIC or a specific queue/power/debug path.
- Header/offset pairing must stay exact. `gc_9_2_1_sh_mask.h` fields must be paired with `gc_9_2_1_offset.h` offsets, not a neighboring GFX9/GFX10 variant.
- The macros are untyped constants. They do not encode access mode, reset value, W1C behavior, self-clearing behavior, alignment requirements, index/data coupling, firmware ownership, or legal values.
- Queue programming is sequencing-sensitive. Ring bases, RPTR report addresses, WPTR polling addresses, doorbells, PQ/IB/IQ/EOP controls, MQD/HQD active bits, dequeue requests, and context-save controls must be ordered with queue quiesce/load/activate/deactivate flows.
- Interrupt and fault fields are easy to misuse. Enabling CP/CPC/MEC interrupts without clearing or preserving status can cause spurious interrupts, while writing status registers with ordinary masks may clear sticky fault evidence.
- VMID reset/preempt fields are broad bit vectors. A wrong shift or unchecked write can reset or preempt the wrong VMID and affect unrelated processes or queues.
- Power and reset fields can disturb active hardware. `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, DIDT/EDC, and throttle controls interact with clocking, power gating, and running queues.
- Debug/trap/watchpoint fields can perturb workloads. SPI trap mode, compute queue reset, resource reservations, context-save controls, and TCP watchpoints may change scheduling, wave residency, cache behavior, or fault routing.
- Full-width `0xFFFFFFFFL` masks are not automatically safe writes. Several represent opaque scheduler fields, indirect data windows, pointer/data registers, or hardware-owned status payloads.
- Reserved fields appear in control and status registers. Consumers must preserve reserved bits unless the hardware guide explicitly requires writing a value.
- The chunk boundary is artificial. It begins after `CP_FATAL_ERROR` shift definitions from the previous chunk and ends in `TCP_GATCL1_CNTL`; adjacent chunks are required for a complete per-file report.

## Test Signals

Useful validation is mostly build, static, and hardware smoke coverage:

- Build AMDGPU and powerplay paths that include `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h`, especially `gfxhub_v1_1.c`, Vega12 power-management includes, and GFX9 ASIC selection paths.
- Static generated-header checks that every visible `__SHIFT` has a corresponding `_MASK`, every mask is aligned to its shift, and register names match entries in `gc_9_2_1_offset.h`.
- Diff checks against AMD's authoritative GC 9.2.1 register database and neighboring generated GC 9.x headers where register layouts are expected to remain compatible.
- Queue smoke tests that initialize graphics and compute queues, program MQD/HQD state, enable doorbells, submit packets, observe WPTR/RPTR movement, process EOP events, and tear queues down without stuck active/busy/dequeue bits.
- Interrupt and fault tests that enable selected CP/CPC/MEC interrupt sources, trigger controlled doorbell/dequeue/timestamp or error conditions where possible, verify status/context fields, and confirm clear/disable sequencing.
- VMID and preemption tests that exercise VMID reset/preempt/status paths while multiple queues or processes are active, checking that only the intended VMID is affected.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests around CP soft reset, clock halt, memory sleep, MQD/HQD state, doorbell state, and DIDT/EDC/throttle controls.
- Debug/profiling tests for SPI trap controls, compute queue reset, resource reservation fields, wavefront context save, and TCP watchpoints, watching for hangs, false faults, missed traps, or cache/watchpoint misattribution.
- Regression indicators include stuck queue-active or queue-idle bits, doorbell hits not observed, write pointers not polled, spurious CP interrupts, lost ECC/UTCL1 fault context, GPU hangs during queue teardown, unexpected throttling, or failures limited to Vega12/GC 9.2.1 hardware.
