# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 2608-5210

## Scope

This chunk covers generated shift and mask macros from the SDMA 4.4.0 AMD GPU register mask header. The range starts inside the `SDMA0_RLC6_MIDCMD_DATA*` register family, completes the `SDMA0_RLC7` queue/context register field definitions, opens the `sdma0_sdma1dec` address block, and then covers `SDMA1` public engine fields plus the `SDMA1_GFX`, `SDMA1_PAGE`, and `SDMA1_RLC0` through `SDMA1_RLC5` queue/register-context families. The chunk ends inside `SDMA1_RLC5_MIDCMD_CNTL`; `SDMA1_RLC6` begins in the following chunk.

The covered register families are:

- Tail fields for `SDMA0_RLC6_MIDCMD_DATA4` through `MIDCMD_DATA10` and `MIDCMD_CNTL`.
- Full `SDMA0_RLC7` ring-buffer, indirect-buffer, doorbell, context-status, preemption, AQL, pointer-polling, and mid-command capture controls.
- The `SDMA1` public engine block, including microcode address/data, VF enable, power and clock control, SDMA engine control, copy/chicken bits, memory tiling/address config, status registers, RAS/EDC counters, atomics, UTCL1 translation/cache controls, physical address capture, performance counters, scratch, RAS status, and clock status.
- `SDMA1_GFX` and `SDMA1_PAGE` queue contexts.
- `SDMA1_RLC0` through `SDMA1_RLC5` queue contexts.

This is a generated hardware bitfield map. It defines C preprocessor constants only. There are no functions, structs, variables, allocations, persistence mechanisms, or executable control-flow constructs in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU SDMA 4.4.0 driver code and the SDMA engine/register hardware. Each field appears as a generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when composing or decoding a field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or preserve that field.

Consumers combine these definitions with `sdma_4_4_0_offset.h`, which supplies the matching `regSDMA*_*` register offsets, and with AMDGPU/SOC15 register helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and SOC15 register-entry macros. The source tree's direct SDMA 4.4 consumer is `amdgpu/sdma_v4_4.c`, which includes both the offset and mask headers and uses the mask fields for SDMA RAS/EDC decoding.

## Important Macro Families

### SDMA0 RLC6/RLC7 Queue Tail

The range starts in the tail of `SDMA0_RLC6` mid-command capture state. `MIDCMD_DATA4` through `MIDCMD_DATA10` are full-width `DATA*` payload words, and `SDMA0_RLC6_MIDCMD_CNTL` exposes `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`. This is state used around mid-command preemption or command splitting; the previous chunk owns the beginning of the same `SDMA0_RLC6` queue context.

`SDMA0_RLC7` is complete in this chunk and follows the common SDMA queue-context layout:

- Ring buffer control and pointers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, and `RB_RPTR_ADDR_*`.
- Write-pointer polling: `RB_WPTR_POLL_CNTL` and `RB_WPTR_POLL_ADDR_*`, including enable, swap, F32 polling, poll frequency, and idle count fields.
- Indirect buffer controls: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, `IB_SUB_REMAIN`, and `SKIP_CNTL`.
- Queue state and signaling: `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `WATERMARK`, `PREEMPT`, `CSA_ADDR_*`, and `DUMMY_REG`.
- AQL and pointer behavior: `RB_AQL_CNTL` and `MINOR_PTR_UPDATE`.
- Mid-command state: `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.

The field names describe queue scheduling, doorbell-triggered write-pointer updates, context switching, IB preemption, context-save areas, and AQL packet mode.

### SDMA1 Public Engine Block

The `sdma0_sdma1dec` address block starts with public SDMA1 engine controls. `SDMA1_UCODE_ADDR` and `SDMA1_UCODE_DATA` provide microcode address/data access; `SDMA1_VF_ENABLE` gates VF behavior; and `SDMA1_PUB_REG_TYPE0` marks public register type bits for the microcode access registers.

Power and clock controls include `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, and `SDMA1_POWER_CNTL_IDLE`. They expose power-gating enables, external on/off requests, memory power overrides and delay fields, clock on/off timing, soft overrides, and idle delay thresholds.

`SDMA1_CNTL` contains core engine switches and interrupt enables: trap enable, UTC L1 enable, semaphore wait interrupt, data/fence byte swapping, mid-command preemption and expiration, mid-command world switch, automatic context switch, context-empty interrupt, frozen interrupt, and IB preempt interrupt. `SDMA1_CHICKEN_BITS` and `SDMA1_CHICKEN_BITS_2` expose copy-efficiency, stall, write-burst, overlap, RAW-check, polling retry, QoS, SRAM fine-grain clock-gating, and F32 command-processing tuning fields.

Memory layout and command fetch fields include `SDMA1_GB_ADDR_CONFIG`, `SDMA1_GB_ADDR_CONFIG_READ`, `SDMA1_RB_RPTR_FETCH*`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, and `SDMA1_PHYSICAL_ADDR_*`. These macros define how SDMA sees GPU memory tiling, ring/IB fetch offsets, command stream data, and captured physical-address state.

Status and diagnostic fields include `SDMA1_STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, `STATUS3_REG`, `STATUS4_REG`, `FREEZE`, `F32_CNTL`, `F32_COUNTER`, `ERROR_LOG`, `CLK_STATUS`, scratch RAM address/data, public dummy registers, and CE/RAS registers. These fields support idle detection, command-op observation, queue ID reporting, frozen-state handling, clock-state checks, scratch access, and error diagnosis.

### RAS, EDC, Performance, and Atomic Controls

The RAS/EDC portion includes `CC_SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, `SDMA1_EDC_COUNTER2`, and `SDMA1_RAS_STATUS`. `EDC_COUNTER` carries per-memory-bank single-error-detection fields for data buffers 0 through 15. `EDC_COUNTER2` carries single-error-detection fields for ucode, ring-buffer command, IB command, UTCL1 read/write FIFOs, data LUT, split data, memory-client write-address, and memory-client read-return buffers. `amdgpu/sdma_v4_4.c` uses the corresponding `SDMA0` field names through `SOC15_REG_FIELD` for all SDMA instances because the instances share the same field layout.

The performance-counter group includes `SDMA1_PERFCNT_PERFCOUNTER0_CFG`, `PERFCOUNTER1_CFG`, result control, miscellaneous control, and low/high result registers. The configuration fields select events and modes, enable counters, and clear/freezing or result behavior.

`SDMA1_ATOMIC_CNTL`, `ATOMIC_PREOP_LO`, and `ATOMIC_PREOP_HI` define atomic-loop timing, return interrupt enablement, and pre-operation data payloads. These fields are relevant when SDMA executes atomic packets or uses atomic operations as part of synchronization and memory updates.

### UTCL1 Translation and Fault/XNACK State

The UTCL1 group is one of the more stateful parts of the chunk. It includes:

- `SDMA1_UTCL1_CNTL` and `UTCL1_WATERMK` for redo behavior, invalidation-ack delays, L2 request credits, virtual-address/request/page/invalidation watermarks, and request depth.
- `UTCL1_RD_STATUS` and `UTCL1_WR_STATUS` for read/write-side FIFO empty/full state, page fault/null indications, L2 idle state, vector selectors, merge state, read/write route bits, write-pointer polling, and request-data FIFO state.
- `UTCL1_INV0`, `INV1`, and `INV2` for invalidation control, timeout behavior, invalid-address handling, VMID vectors, invalidate address high/low bits, and non-flush VMID vectors.
- `UTCL1_RD_XNACK*`, `UTCL1_WR_XNACK*`, and `UTCL1_TIMEOUT` for read/write XNACK address, VMID, vector, XNACK presence, and timeout-limit fields.
- `UTCL1_PAGE` for VM-hole behavior, request type, memory type usage, and page-table snoop behavior.

These macros are integration points between SDMA command execution and GPU virtual memory/page-fault handling. Incorrect field definitions here can break fault diagnosis, XNACK replay, invalidation, or VMID-scoped cache behavior.

### Repeated SDMA1 Queue Contexts

`SDMA1_GFX`, `SDMA1_PAGE`, and `SDMA1_RLC0` through `SDMA1_RLC5` mostly share the same queue-context register shape. For each queue family, the macros define:

- Ring-buffer enablement, size, swapping, read-pointer writeback enable/swap/timer, privilege, and VMID fields.
- Ring-buffer base, high base, read pointer, high read pointer, write pointer, high write pointer, and write-pointer polling address/control fields.
- Indirect-buffer enable, swap, switch-inside-IB, command VMID, read pointer, offset, base low/high, size, skip count, and sub-remaining fields.
- Context-status bits for selected, idle, expired, exception, context-switch able/ready, preempted, and preempt-disable.
- Doorbell enable/captured, doorbell offset, doorbell log, write-pointer update fail/pending status, read/write outstanding watermarks, context-save area address, and IB preempt.
- AQL enable, AQL packet size, packet step, and minor-pointer update enable.
- Mid-command payload words `MIDCMD_DATA0` through `MIDCMD_DATA10` and `MIDCMD_CNTL` fields for data validity, copy mode, split state, and preemption allowance.

`SDMA1_GFX` additionally has `SDMA1_GFX_CONTEXT_CNTL`, with `RESUME_CTX` and `SESSION_SEL`, which is not present in the `PAGE` and `RLC*` blocks covered here. The chunk covers complete queue families through `SDMA1_RLC4`; `SDMA1_RLC5` is complete through the start of `MIDCMD_CNTL`, with the final mask definitions continuing immediately after the line range.

## Control Flow and State Behavior

This header chunk has no runtime control flow. It affects compiled behavior by controlling how driver code composes values written to SDMA registers and decodes values read from SDMA registers.

The persistent state represented by the chunk is hardware state, not software state in the header. Important persistent or semi-persistent configuration state includes SDMA power/clock controls, engine control bits, microcode address/data access, VF enablement, memory-layout configuration, queue ring bases and sizes, pointer polling addresses, read-pointer writeback addresses, doorbell offsets, context-save-area addresses, AQL mode, VMID assignment, UTCL1 timeout/watermark/invalidation controls, performance-counter selection, and RAS/EDC configuration.

Other fields are runtime status, command, or diagnostic state. Examples include idle and FIFO state in `STATUS*` and `UTCL1_*_STATUS`, write-pointer update failure/pending state, doorbell capture and bus-error logs, context selected/idle/expired/preempted bits, IB preempt request bits, mid-command data-valid state, RAS/EDC counters, XNACK capture addresses, physical address capture, scratch RAM access, and performance counter results. The mask header does not encode whether individual fields are read-only, write-one-to-clear, sticky, latched, or command-on-write; those semantics come from the hardware specification and the owning SDMA driver sequences.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `sdma_4_4_0_offset.h` supplies the matching `regSDMA0_*`, `regSDMA1_*`, and queue register offsets.
- `sdma_4_4_0_sh_mask.h` supplies field encodings for those offsets.
- AMDGPU/SOC15 helpers consume `__SHIFT` and `_MASK` macros through register-field helper macros and direct read/modify/write sequences.

Direct integration in this source tree includes `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c`, which includes this header and the offset header. That driver uses the SDMA 4.4 register layout for SDMA RAS query/reset handling and uses instance offsets to read per-instance SDMA registers. Broader AMDGPU code relies on the same register-family shapes for SDMA queue setup, KFD/HSA queue exposure, ring pointer programming, doorbell programming, indirect-buffer control, preemption, golden-register programming, and hardware diagnostics.

The queue-context definitions integrate with several higher-level subsystems:

- AMDGPU ring and scheduler setup, which programs ring bases, sizes, read/write pointers, polling, and writeback.
- KFD/HSA queue management, which uses RLC queue contexts and AQL packet controls for compute-facing SDMA queues.
- VM and fault handling, which depends on UTCL1 invalidation, page, XNACK, timeout, and status fields.
- Doorbell and interrupt paths, which rely on doorbell enable/captured/log fields, write-pointer update status, context-empty/frozen/IB-preempt interrupt enables, and preemption request bits.
- RAS and diagnostics, which decode EDC counters, RAS status, error logs, status registers, performance counters, clock status, and scratch registers.
- Power management and clock-gating flows, which use power control, idle-delay, clock control, ULV, CRD, and fine-grain clock-gating fields.

Consumers must keep the SDMA 4.4.0 offset and mask headers together. Similar SDMA queue field names exist in `oss_*` and `sdma1_*` headers for other ASIC generations, but bit widths can differ; for example, older SDMA queue `RB_SIZE`, `SKIP_COUNT`, or `IB_SUB_REMAIN` masks are not always identical.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can program the wrong queue base, pointer, doorbell, VMID, interrupt enable, power, or translation field and produce hangs, missed interrupts, memory corruption, or silent queue stalls.
- The repeated queue-context blocks are copy-generation sensitive. `GFX`, `PAGE`, `RLC0` through `RLC7`, and `SDMA0` versus `SDMA1` families have near-identical fields, so a lane/name copy error can target the wrong queue or instance.
- The chunk starts and ends mid-family. `SDMA0_RLC6` depends on the previous chunk for the start of its mid-command data, and `SDMA1_RLC5_MIDCMD_CNTL` continues after this chunk. Merge/reconciliation must join adjacent chunks before treating either family as complete.
- Ring-buffer and IB address fields have alignment encoded in the masks (`ADDR` or `OFFSET` fields often start at bit 2 or bit 5). Misusing a full address without respecting the low-bit mask can corrupt pointer programming.
- Doorbell fields are privilege- and scheduling-sensitive. Incorrect doorbell enable, offset, log, or captured-bit handling can cause queues to miss submissions or expose stale write-pointer data.
- UTCL1 and XNACK fields are VM/fault-sensitive. Incorrect invalidation, VMID-vector, timeout, address, or page behavior masks can break GPU virtual memory fault recovery and make diagnostics misleading.
- RAS/EDC fields are diagnostic and may be sticky or counter-like. Treating them as ordinary read/write state can lose error evidence or fail to clear/query errors consistently.
- Power, clock, chicken, and relaxed-ordering fields can affect ordering, latency, and stability. Writes using incorrect masks may cause performance regressions, hangs, or memory-ordering violations.
- Queue preemption and mid-command capture fields affect context switching. Incorrect `ALLOW_PREEMPT`, `SPLIT_STATE`, `DATA_VALID`, context-status, or preempt fields can break reset recovery and timeslicing.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and targeted GPU runtime coverage:

- Build AMDGPU with SDMA 4.4 support enabled; this catches missing or renamed macros consumed by `sdma_v4_4.c` and shared SOC15 helpers.
- Boot on SDMA 4.4 hardware and verify SDMA instance enumeration, register offset selection, power/clock status, and idle state reporting.
- Exercise SDMA copy/fill workloads through GFX, PAGE, and RLC queues; check ring-base programming, read/write pointer movement, doorbell delivery, pointer writeback, and queue idle transitions.
- Run KFD/HSA queue workloads that use RLC SDMA queues and AQL mode; verify `RB_AQL_CNTL`, VMID, context status, and doorbell behavior.
- Test IB submission and preemption paths; validate `IB_*`, `PREEMPT`, `CONTEXT_STATUS`, and mid-command data/control behavior under reset or timeslicing.
- Run VM fault and replay/XNACK scenarios where available; validate UTCL1 status, invalidation, timeout, XNACK address/VMID/vector, and page-state decoding.
- Query SDMA RAS counters through the SDMA 4.4 RAS path; confirm EDC counter field decoding for all SDMA instances and verify reset/clear behavior against hardware expectations.
- Check performance-counter programming by selecting events, enabling/clearing counters, and confirming low/high result registers change during SDMA traffic.
- Validate suspend/resume or power-management flows for power-control, clock-control, idle-delay, ULV/CRD, freeze, and clock-status fields.
- Use fault-injection or stress tests for doorbell update failures, queue stalls, and read/write outstanding watermarks to confirm status and log fields decode as expected.
