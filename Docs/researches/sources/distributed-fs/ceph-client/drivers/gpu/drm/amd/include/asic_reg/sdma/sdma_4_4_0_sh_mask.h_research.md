# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003363`: lines 1-2607, `Docs/researches/chunks/subset-b-003363_research.md`
- `subset-b-003364`: lines 2608-5210, `Docs/researches/chunks/subset-b-003364_research.md`
- `subset-b-003365`: lines 5211-7807, `Docs/researches/chunks/subset-b-003365_research.md`
- `subset-b-003366`: lines 7808-10409, `Docs/researches/chunks/subset-b-003366_research.md`
- `subset-b-003367`: lines 10410-13008, `Docs/researches/chunks/subset-b-003367_research.md`
- `subset-b-003368`: lines 13009-13922, `Docs/researches/chunks/subset-b-003368_research.md`

## Chunk Research

### subset-b-003363: lines 1-2607

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 1-2607

## Scope

This chunk covers the opening 2,607 lines of the generated AMD SDMA 4.4.0 shift/mask header. It begins with the include guard and the `sdma0_sdma0dec` address block, then defines bitfield shifts and masks for the public SDMA0 register set, UTCL1 fault/XNACK controls, EDC/RAS counters, performance counters, status/debug registers, and the first queue-context register templates: `GFX`, `PAGE`, `RLC0` through `RLC5`, and the start of `RLC6`.

The file is a C preprocessor register-field map only. It does not define functions, structs, storage, locks, or executable control flow. Its constants are consumed together with `sdma_4_4_0_offset.h` and AMDGPU register helper macros.

## Purpose

The purpose of this header section is to encode the SDMA 4.4.0 hardware ABI at bit granularity. Each field follows the generated AMD naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.

Consumers use these constants with helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32` to compose writes or decode reads without hard-coding bit positions. The companion offset header supplies register addresses such as `regSDMA0_POWER_CNTL`, `regSDMA0_EDC_COUNTER`, and `regSDMA0_GFX_RB_CNTL`; this header supplies only field layout.

## Important Macro Families

### Global SDMA0 Control, Firmware, Power, and Status

The first section defines fields for SDMA microcode and global control registers:

- `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, and `SDMA0_UCODE_CHECKSUM` describe the microcode access and checksum fields.
- `SDMA0_VF_ENABLE` gates virtual-function operation.
- `SDMA0_POWER_CNTL`, `SDMA_POWER_GATING`, `SDMA_PGFSM_CONFIG`, `SDMA_PGFSM_WRITE`, `SDMA_PGFSM_READ`, `SDMA0_POWER_CNTL_IDLE`, `SDMA0_CLK_CTRL`, `SDMA0_CLK_STATUS`, and `SDMA0_ULV_CNTL` expose power gating, clock gating, memory power, idle delay, PGFSM, and ultra-low-voltage status/control fields.
- `SDMA0_CNTL`, `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_RD_BURST_CNTL`, `SDMA0_BA_THRESHOLD`, `SDMA0_CRD_CNTL`, and `SDMA0_RELAX_ORDERING_LUT` tune command processing, burst behavior, credits, copy overlap, relaxed ordering, preemption, traps, interrupts, and workarounds.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, and `SDMA0_STATUS4_REG` provide detailed idle, FIFO, outstanding request, command, exception, queue, SR-IOV, and polling status fields.

These are integration points for bring-up, reset, suspend/resume, idle detection, power management, queue drain, debugging, and timeout paths.

### Addressing, VM, UTCL1, XNACK, and Invalidation

The UTCL1-related portion defines SDMA virtual-memory and memory-translation status:

- `SDMA0_GB_ADDR_CONFIG` and `SDMA0_GB_ADDR_CONFIG_READ` describe graphics-bank addressing topology fields.
- `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_RD_STATUS`, and `SDMA0_UTCL1_WR_STATUS` expose translation cache control, read/write queue watermarks, FIFO empty/full states, page fault/null indicators, next-vector fields, merge state, and request-to-L2 idle status.
- `SDMA0_UTCL1_INV0`, `SDMA0_UTCL1_INV1`, and `SDMA0_UTCL1_INV2` encode invalidation command state, timeout handling, VMID vectors, flush type, and invalidation addresses.
- `SDMA0_UTCL1_RD_XNACK*`, `SDMA0_UTCL1_WR_XNACK*`, and `SDMA0_UTCL1_TIMEOUT` capture XNACK addresses, VMID/vector data, XNACK classification, and read/write XNACK timeout limits.
- `SDMA0_UTCL1_PAGE`, `SDMA0_PHYSICAL_ADDR_LO`, and `SDMA0_PHYSICAL_ADDR_HI` describe page fault/request attributes and physical-address reporting.

These fields are relevant when SDMA participates in GPUVM translation, page fault recovery, retry/XNACK handling, invalidation, or address/debug reporting. The header does not encode the protocol sequencing or clear semantics; it only names the fields.

### EDC, RAS, Error, and Diagnostic Counters

The chunk includes the RAS-facing SDMA error counters:

- `CC_SDMA0_EDC_CONFIG` exposes EDC disable control.
- `SDMA0_EDC_COUNTER` packs two-bit single-error-detection counters for `SDMA_MBANK_DATA_BUF0_SED` through `SDMA_MBANK_DATA_BUF15_SED`.
- `SDMA0_EDC_COUNTER2` packs counters for ucode, ring-buffer command, indirect-buffer command, UTCL1, data LUT, split data, memory-write address, and memory-read-return buffers.
- `SDMA0_ERROR_LOG`, `SDMA0_RAS_STATUS`, `SDMA0_EA_DBIT_ADDR_DATA`, and `SDMA0_EA_DBIT_ADDR_INDEX` expose error override/status, ECC/NACK error bits, and double-bit address diagnostic storage.

`amdgpu/sdma_v4_4.c` consumes `SDMA0_EDC_COUNTER` and `SDMA0_EDC_COUNTER2` through `SOC15_REG_FIELD` entries in `sdma_v4_4_ras_fields`. Its RAS path reads those registers per SDMA instance, reports nonzero single-error-detection counts as SDMA uncorrectable errors, and clears the counters by writing zero to both EDC counter registers.

### Performance, Scratch, and Debug Registers

The performance/debug group includes:

- `SDMA0_PERFCNT_PERFCOUNTER0_CFG`, `SDMA0_PERFCNT_PERFCOUNTER1_CFG`, `SDMA0_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA0_PERFCNT_MISC_CNTL`, `SDMA0_PERFCNT_PERFCOUNTER_LO`, and `SDMA0_PERFCNT_PERFCOUNTER_HI` for event selection, modes, enable/clear bits, triggers, result selection, saturation behavior, counter values, and compare value.
- `SDMA0_F32_CNTL`, `SDMA0_FREEZE`, and `SDMA0_F32_COUNTER` for halting, stepping, resetting, freezing, and observing the internal F32 micro-engine state.
- `SDMA0_SCRATCH_RAM_DATA`, `SDMA0_SCRATCH_RAM_ADDR`, `SDMA0_PUB_DUMMY_REG0` through `SDMA0_PUB_DUMMY_REG3`, and `SDMA0_CONTEXT_GROUP_BOUNDARY` for scratch/dummy/context grouping fields.
- `SDMA0_CE_CTRL` and `SDMA0_ATOMIC_*` for copy-engine and atomic/preop configuration.

These fields support profiling, diagnostics, firmware/micro-engine debugging, and low-level command-engine tuning.

### Queue Context Templates: GFX, PAGE, RLC0-RLC6

From `SDMA0_GFX_RB_CNTL` onward, the chunk defines a repeated queue-context register layout. The complete contexts covered here are `GFX`, `PAGE`, and `RLC0` through `RLC5`; the chunk ends after `SDMA0_RLC6_MIDCMD_DATA3`, so the remainder of the `RLC6` template continues in a later chunk.

Each complete context defines a common set of ring and IB controls:

- `*_RB_CNTL` fields for ring enable, ring size, swap, read-pointer writeback enable/swap/timer, privilege, and VMID.
- `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` for ring base and read/write pointers.
- `*_RB_WPTR_POLL_CNTL`, `*_RB_WPTR_POLL_ADDR_HI`, and `*_RB_WPTR_POLL_ADDR_LO` for write-pointer polling, polling frequency, idle count, and polling address.
- `*_RB_RPTR_ADDR_HI` and `*_RB_RPTR_ADDR_LO` for read-pointer writeback address and idle status.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` for indirect-buffer execution state.
- `*_SKIP_CNTL`, `*_CONTEXT_STATUS`, `*_CONTEXT_CNTL` where present, `*_PREEMPT`, and `*_MINOR_PTR_UPDATE` for scheduling, preemption, context switching, and pointer update behavior.
- `*_DOORBELL`, `*_DOORBELL_OFFSET`, `*_DOORBELL_LOG`, and `*_STATUS` for queue doorbell enable/capture, offsets, logged back-end error/data, failed write-pointer updates, and pending updates.
- `*_WATERMARK`, `*_CSA_ADDR_LO`, `*_CSA_ADDR_HI`, `*_AQL_CNTL`, `*_DUMMY_REG`, `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10`, and `*_MIDCMD_CNTL` for queue watermarks, context-save-area addresses, AQL packet handling, dummy storage, and mid-command preemption/resume payloads.

The repeated layout makes it practical for driver code to configure similar queue instances by varying register offsets. It also makes generator or copy/paste errors especially damaging because a wrong suffix can silently program the wrong queue field.

## Control Flow

There is no executable control flow in this header. Runtime control flow is in consumers such as `amdgpu/sdma_v4_4.c` and other AMDGPU SDMA code.

The implied control flow for queue bring-up is:

1. Use the offset header and SDMA instance base computation to locate the target context registers.
2. Program ring base, size, VMID, privilege, swap, writeback, and pointer-polling fields.
3. Program doorbell offset/enable and IB controls if needed.
4. Enable the ring with the `RB_ENABLE` field.
5. During drain, preemption, reset, or timeout handling, read status/context fields and optionally use preempt/freeze/mid-command state fields.

The implied RAS flow in `sdma_v4_4.c` is:

1. For each SDMA instance, calculate the instance register offset from the SDMA0 offsets.
2. Read `regSDMA0_EDC_COUNTER` and `regSDMA0_EDC_COUNTER2`.
3. Extract fields using the masks/shifts from this header.
4. Add nonzero SED values to the uncorrectable-error count and log the field name.
5. Clear counters by writing zero to the EDC counter registers when reset is requested.

## State and Persistence Behavior

This chunk defines hardware register state, not software-owned persistent state. Persistence depends on the SDMA hardware reset domain, firmware policy, SR-IOV mode, power management state, and AMDGPU save/restore paths.

State classes named by this chunk include:

- Programmed engine state: microcode address/data, global control bits, power/clock/ULV fields, burst/credit/order tuning, and PGFSM controls.
- Runtime status: idle bits, FIFO full/empty bits, outstanding request bits, context selected/idle/expired/exception/preempted bits, queue write-pointer update status, and doorbell capture/log state.
- Translation and fault state: UTCL1 read/write status, invalidation state, XNACK addresses/vectors, timeout limits, page attributes, and physical-address report fields.
- Queue state: ring bases, pointers, writeback addresses, polling configuration, IB bases/offsets/sizes, doorbell offsets, CSA addresses, AQL controls, and mid-command save/resume payloads.
- RAS/perf/debug state: EDC counters, RAS status, error log, double-bit diagnostic address storage, performance counter selection/results, scratch RAM, F32 counter, and dummy registers.

The header does not indicate whether a field is read-only, write-one-to-clear, sticky, reset-on-read, or write-zero-to-clear. One known consumer behavior is that `sdma_v4_4.c` clears the two EDC counter registers by writing zero. Other status or control fields require the ASIC programming guide or existing AMDGPU paths for safe access semantics.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h` supplies the matching `reg*` addresses and base indices for these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes this header directly and uses the EDC counter field macros for SDMA RAS reporting.
- AMDGPU register helpers such as `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` are the normal mechanism for field extraction and composition.
- SDMA initialization, power management, reset, hang detection, queue scheduling, GPUVM invalidation/fault handling, SR-IOV, debugfs/perf tooling, and RAS reporting are natural consumers of these definitions.
- The SDMA 4.4.0 register layout supports multiple SDMA instances by using SDMA0 offsets plus instance-specific base offsets; the masks in this header are shared across those instances.

## Risks

- Register layout drift: every shift and mask must match SDMA 4.4.0 hardware. A single bad bit definition can corrupt queue setup, VM fault handling, power control, RAS counting, or preemption state.
- Repeated-template mistakes: `GFX`, `PAGE`, and `RLCn` blocks are mechanically similar. A mismatched suffix or mask in one context could silently affect only one queue class.
- Chunk boundary risk: this line range ends in the middle of the `SDMA0_RLC6_*` template. Any merged per-file research must reconcile later chunks before treating RLC6 as complete.
- Ambiguous access semantics: the header exposes masks but not read/write/clear rules. Treating status fields as ordinary writable fields can fail to clear hardware state or clobber adjacent fields.
- Packed counter interpretation: EDC counter fields are two-bit packed values. Incorrect extraction can overcount, undercount, or attribute RAS events to the wrong SDMA internal buffer.
- Queue pointer alignment: several address and pointer fields intentionally mask low bits, for example ring write-pointer poll addresses and IB base addresses. Consumers must pass properly aligned addresses.
- Power and clock controls: misuse of `POWER_CNTL`, `CLK_CTRL`, PGFSM, or ULV fields can leave SDMA inaccessible, prevent idle, or race with firmware-managed power transitions.
- VM/XNACK/invalidation controls: wrong VMID vectors, timeout values, or invalidation address fields can break GPUVM correctness or produce hard-to-debug page fault behavior.
- Doorbell and SR-IOV fields: incorrect doorbell enable/offset or VF controls can route queue updates to the wrong context or expose virtualization isolation bugs.

## Test Signals

Useful validation signals for code consuming this chunk include:

- Compile coverage for `sdma_v4_4.c` and any SDMA 4.4.0 users with no missing or conflicting macro definitions.
- Field composition/extraction checks around representative packed fields: `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, `SDMA0_UTCL1_INV0`, `SDMA0_EDC_COUNTER`, `SDMA0_EDC_COUNTER2`, `SDMA0_GFX_RB_CNTL`, and one `SDMA0_RLCn_RB_CNTL`.
- Hardware or emulator queue bring-up tests that program ring base/size/writeback/doorbell fields, enable the ring, submit an SDMA packet, and verify read/write pointer movement and idle status.
- RAS tests that inject or simulate EDC counter values, confirm `sdma_v4_4.c` reports SDMA uncorrectable counts, and verify reset writes zero to both EDC counter registers for every SDMA instance.
- GPUVM/XNACK tests that exercise SDMA page fault or retry paths and confirm UTCL1 status, invalidation idle, VMID vector, and XNACK address fields decode as expected.
- Suspend/resume, GPU reset, and runtime power tests that confirm programmed queue, power, clock, scratch, EDC, and perf-counter state is either restored or intentionally reinitialized.
- SR-IOV/VF tests that verify `VF_ENABLE`, doorbell capture/logging, active queue ID, and RLC queue context fields remain isolated per virtual function.

### subset-b-003364: lines 2608-5210

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

### subset-b-003365: lines 5211-7807

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 5211-7807

## Scope

This chunk is a generated AMD SDMA 4.4.0 shift/mask header segment. It covers lines 5211-7807 of `sdma_4_4_0_sh_mask.h` and defines 2,120 preprocessor constants: 1,061 `__SHIFT` values and 1,059 `_MASK` values under 475 visible register comments. The range begins inside `SDMA1_RLC5_MIDCMD_CNTL`, covers complete `SDMA1_RLC6` and `SDMA1_RLC7` queue-context register groups, enters the `sdma0_sdma2dec` address block for SDMA instance 2, covers SDMA2 global/status/RAS/performance fields, then covers `SDMA2_GFX`, `SDMA2_PAGE`, and `SDMA2_RLC0` through `SDMA2_RLC4` queue groups. It ends inside `SDMA2_RLC5_RB_CNTL`, before the remaining `SDMA2_RLC5` fields.

The file is data-only register metadata. It has no functions, structs, control statements, or storage. Runtime behavior comes from C code that includes this header together with `sdma_4_4_0_offset.h`, then uses the constants in register access macros such as `RREG32`, `WREG32`, `SOC15_REG_FIELD`, `REG_SET_FIELD`, and related AMDGPU helpers.

## Purpose

The chunk provides bit layouts for SDMA 4.4.0 registers. Each logical field has a shift constant and usually a mask constant, allowing driver code to construct, update, and decode 32-bit MMIO register values without hard-coding bit positions at call sites. This matters for SDMA ring setup, indirect-buffer execution, context switching, doorbell delivery, queue preemption, RAS/error reporting, performance counters, and low-level debug/status reads.

The source path is under `drivers/gpu/drm/amd/include/asic_reg/sdma`, so it belongs to AMDGPU hardware-description headers rather than Ceph-specific code. In this repository it is carried inside the Linux client source tree used by the distributed-fs snapshot.

## Important Macro Families

- Boundary carry-in: lines 5211-5216 finish `SDMA1_RLC5_MIDCMD_CNTL` by defining `SPLIT_STATE` and `ALLOW_PREEMPT` shifts/masks plus the `DATA_VALID` and `COPY_MODE` masks. Because the chunk starts mid-register, the `DATA_VALID` and `COPY_MODE` shifts are in the previous chunk.
- `SDMA1_RLC6_*` and `SDMA1_RLC7_*`: two complete SDMA1 RLC queue contexts. Each context has ring-buffer control/base/read-pointer/write-pointer registers, write-pointer poll registers, indirect-buffer control/base/size/offset/read-pointer registers, skip count, context status, doorbell state/log/offset, read/write watermarks, context-save-area addresses, IB preemption, dummy/debug storage, AQL packet sizing, minor pointer update, and eleven mid-command data registers plus mid-command control.
- `SDMA2_UCODE_*`, `SDMA2_VF_ENABLE`, `SDMA2_CONTEXT_GROUP_BOUNDARY`, `SDMA2_POWER_CNTL`, `SDMA2_CLK_CTRL`, and `SDMA2_CNTL`: global SDMA2 setup fields for microcode access, virtualization enable, power/clock behavior, trap and interrupt enables, data/fence swap, mid-command preemption/expiry/world-switch, auto context switching, and frozen/preempt interrupt enables.
- `SDMA2_STATUS_REG`, `SDMA2_STATUS1_REG`, `SDMA2_STATUS2_REG`, `SDMA2_STATUS3_REG`, and `SDMA2_STATUS4_REG`: status decode fields for idle/full/empty conditions, ring and IB command states, memory-controller read/write idleness, semaphore state, interrupt stall state, copy-engine sub-block idleness, and additional internal status words.
- `SDMA2_RD_BURST_CNTL`, `SDMA2_HBM_PAGE_CONFIG`, `SDMA2_F32_CNTL`, `SDMA2_PHASE0_QUANTUM`, `SDMA2_PHASE1_QUANTUM`, `SDMA2_PHASE2_QUANTUM`, `SDMA2_BA_THRESHOLD`, and `SDMA2_RELAX_ORDERING_LUT`: scheduling, burst, page, functional-test/debug, quantum, boundary-address, and relaxed-ordering controls.
- `SDMA2_EDC_COUNTER`, `SDMA2_EDC_COUNTER2`, `SDMA2_ERROR_LOG`, and `SDMA2_RAS_STATUS`: RAS/error-observation fields. The chunk includes single-error-detection counters for SDMA memory banks, ucode/RB/IB command buffers, UTCL1 FIFOs, data LUT/split buffers, memory-controller FIFOs, plus RAS fetch ECC and NACK-generation status bits.
- `SDMA2_UTCL1_*`: UTCL1 control, watermark, read/write status, invalidation slots, read/write XNACK address ranges, timeout, and page-control fields. These tie SDMA memory accesses into GPU virtual-memory translation, retry, and fault-observation paths.
- `SDMA2_PERFCNT_*` and `SDMA2_F32_COUNTER`: performance-counter selection, clear/reset/start/stop controls, result readout control, low/high counter values, and a free-running or debug counter.
- `SDMA2_GFX_*`, `SDMA2_PAGE_*`, and `SDMA2_RLC0_*` through `SDMA2_RLC4_*`: queue-specific register groups with a repeated layout. `GFX` and `PAGE` cover graphics and page queues; `RLCn` covers RLC-managed queue contexts. The chunk begins the `SDMA2_RLC5_RB_CNTL` group but only includes the first part of that register.

## Register Field Semantics

The repeated queue groups expose the SDMA queue programming model:

- `*_RB_CNTL` fields include `RB_ENABLE`, `RB_SIZE`, byte-swap controls, read-pointer writeback enable/swap/timer, privilege bit, and VMID. These fields control whether the ring runs, how large it is, how pointers are written back, and which VM context owns commands.
- `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` describe the ring buffer address and producer/consumer offsets. Low address fields often use alignment masks such as `0xFFFFFFFCL`, while high fields are full or partial upper address words.
- `*_RB_WPTR_POLL_CNTL` and `*_RB_WPTR_POLL_ADDR_{HI,LO}` configure polling of a memory write pointer, including enable, swap, F32 poll mode, poll frequency, idle poll count, and aligned poll address.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_{LO,HI}`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` define indirect-buffer execution state. These fields gate IB execution, endian/swap handling, switching inside an IB, command VMID, IB address, current pointer, and remaining sub-buffer size.
- `*_CONTEXT_STATUS` exposes scheduler/context state: selected, idle, expired, exception, context-switch capable, context-switch ready, preempted, and preempt disabled.
- `*_DOORBELL`, `*_DOORBELL_OFFSET`, and `*_DOORBELL_LOG` define doorbell enable/captured bits, queue doorbell offset, logged doorbell data, and backend-error status.
- `*_WATERMARK` captures outstanding read/write thresholds, while `*_CSA_ADDR_{LO,HI}` points at context-save storage.
- `*_PREEMPT`, `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10`, and `*_MIDCMD_CNTL` support mid-command preemption/restart. Control fields identify whether saved data is valid, whether copy mode is active, split state, and whether preemption is allowed.
- `*_RB_AQL_CNTL` and `*_MINOR_PTR_UPDATE` support AQL packet sizing/step and minor pointer update behavior for queues that can process AQL-formatted packets.

Most masks are 32-bit `L` integer constants. Consumers are expected to combine masks with shifts through the AMD register-field macros rather than by direct arithmetic where possible.

## Control Flow

There is no direct control flow in this header. The operational flow implied by the macros is:

1. Include `sdma_4_4_0_offset.h` for register addresses and this file for field masks.
2. Compute the register address for a given SDMA instance and queue. In `amdgpu/sdma_v4_4.c`, `sdma_v4_4_get_reg_offset()` starts from `adev->reg_offset[SDMA0_HWIP][0][0]` and adds instance deltas such as `SDMA1_REG_OFFSET`, `SDMA2_REG_OFFSET`, `SDMA3_REG_OFFSET`, and `SDMA4_REG_OFFSET`.
3. Read or compose a register value with `RREG32`, `WREG32`, `REG_SET_FIELD`, or `SOC15_REG_FIELD`.
4. For ring/IB setup, program base addresses, pointer addresses, pointer polling, doorbells, and enable bits. For shutdown or preemption, clear enable/preempt bits and poll status bits such as `IDLE`, `CONTEXT_EMPTY`, or per-context `CONTEXT_STATUS`.
5. For diagnostics and RAS, read status/counter registers, mask and shift the relevant fields, then report or clear counters.

The queue groups are intentionally regular, so driver code can often calculate offsets from an RLC0 base register and a per-queue stride. Adjacent KFD code in the AMDGPU tree uses this pattern for SDMA RLC save/restore and queue enable/disable flows.

## State And Persistence

The header itself persists only compile-time constants. Hardware state lives in SDMA MMIO registers and in GPU-visible memory addresses programmed through those registers:

- Ring state persists in RB base, read pointer, write pointer, and read-pointer writeback registers until reset, reinitialization, or context teardown.
- IB state persists in IB base, size, offset/read-pointer, and remaining-size registers while an indirect buffer is executing.
- Doorbell state is partly MMIO-visible through enable/captured/log fields and partly external through doorbell aperture writes.
- Context-switch and preemption state persists in context status, CSA address, mid-command data, and mid-command control registers.
- RAS and performance state persists in EDC/error/status/perf-counter registers until cleared or reset.
- Power/clock and global SDMA2 control fields persist as device runtime state and are usually reprogrammed during ASIC init, resume, reset, or mode changes.

Because these are hardware register definitions, incorrect masks can corrupt persistent device state even though the header has no C storage of its own.

## Dependencies

- `sdma_4_4_0_offset.h`: supplies the matching `regSDMA*` register offsets and base-index metadata. The masks in this chunk are only meaningful with the matching offset header from the same generated register package.
- `amdgpu/sdma_v4_4.c`: directly includes both the offset and shift/mask headers. Its RAS helpers use SDMA register field metadata and instance offset calculations to query and clear SDMA EDC counters.
- AMDGPU register helpers: `RREG32`, `WREG32`, `REG_SET_FIELD`, `SOC15_REG_FIELD`, and `SOC15_REG_ENTRY` are the normal integration layer for these constants.
- AMDGPU device state: `struct amdgpu_device`, especially `adev->reg_offset`, `adev->sdma.num_instances`, and RAS support checks, determines which physical SDMA instances are accessed.
- KFD/compute SDMA queue management patterns: related AMDGPU KFD files use RLC queue register offsets, enable bits, context status bits, doorbells, and CSA/mid-command ranges for queue save, restore, disable, and resume.

## Integration Points

- ASIC bring-up and reset: global SDMA2 power, clock, control, freeze, status, and microcode fields help bring an SDMA instance online and verify idleness.
- Ring and IB submission: `GFX`, `PAGE`, and `RLCn` queue macros support ring buffer and indirect-buffer setup, including endian/swap handling and write-pointer writeback.
- Doorbell signaling: queue doorbell enable, captured, offset, and log fields integrate with userspace/kernel queue notification and hang diagnosis.
- GPU virtual memory: UTCL1 control/status/XNACK/timeout fields connect SDMA memory operations to GPUVM translation and retry/fault paths.
- RAS: EDC counters, error log, and RAS status fields feed AMDGPU RAS reporting. `sdma_v4_4.c` queries and clears EDC counter registers across SDMA instances.
- Performance/debug: performance-counter config/result fields, F32 controls/counter, scratch RAM fields, dummy registers, and status words support low-level debug and performance tracing.
- Queue preemption and context switching: per-queue context status, `PREEMPT`, CSA address, and mid-command save/control fields integrate with scheduler and KFD queue lifecycle flows.

## Risks

- Generated-header drift: masks must match the hardware register specification and the paired offset header. A stale or mismatched mask can silently write the wrong bit, which is especially dangerous for enable, VMID, privilege, doorbell, preempt, RAS, and address fields.
- Chunk boundary hazards: this research range starts and ends mid-register family. `SDMA1_RLC5_MIDCMD_CNTL` is incomplete at the start, and `SDMA2_RLC5_RB_CNTL` is incomplete at the end. Any merge/reconciliation pass must combine adjacent chunks before making per-file conclusions about those two registers.
- Repetition mistakes: `GFX`, `PAGE`, and `RLC0`-`RLC7` groups are highly repetitive. Manual edits or generated diffs can easily alter one queue context but not its siblings.
- Address alignment assumptions: several low address fields mask off low bits (`ADDR` shifted by 2 or 5). Callers must pass aligned GPU addresses or the low bits will be discarded.
- Width/sign assumptions: constants use `L` suffixes and many masks occupy bit 31. Consumers should use unsigned 32-bit temporaries for register values to avoid signed comparison or promotion surprises.
- Instance offset assumptions: `sdma_v4_4.c` computes instance register addresses by adding fixed deltas from the SDMA0 base. If the ASIC instance layout or number of instances changes, the same field masks may still compile but target the wrong MMIO block.
- RAS interpretation risk: `sdma_v4_4.c` treats SDMA RAS single-error-detection counts as uncorrectable error count increments and sets correctable count to zero. Field mapping errors in EDC masks would directly skew user-visible RAS accounting.

## Test Signals

- Compile coverage: any typo or missing macro used by SDMA v4.4 code should surface during kernel/AMDGPU compilation, especially in `amdgpu/sdma_v4_4.c`.
- Register-field sanity: inspect generated pairs to ensure each `__SHIFT` has the intended `_MASK`, masks align to field widths, and paired offset names exist in `sdma_4_4_0_offset.h`.
- Runtime ring tests: SDMA queue initialization, memcpy/fill operations, IB execution, and fence completion verify `RB_*`, `IB_*`, writeback, and doorbell masks.
- Suspend/resume and GPU reset: these flows stress persistence and reprogramming of ring base/pointer, global control, status, and RAS/perf state.
- KFD compute queue tests: RLC queue save/restore, doorbell updates, context idle polling, and preemption paths exercise the `RLCn` queue register families.
- RAS injection or counter-read tests: reading and clearing EDC counters should produce expected SDMA RAS counts and logs, validating the EDC and status masks used by `sdma_v4_4.c`.
- Hang/debug diagnostics: status register dumps should decode idle/full/stall/preempt states consistently with observed SDMA behavior.

## Research Notes

This chunk was read as a hardware-description block, not as executable logic. The most important structural fact is that it is part of one generated mask namespace for SDMA 4.4.0 and is consumed by code that already knows the matching register offsets. For final per-file reconciliation, merge this with adjacent chunks to restore the full `SDMA1_RLC5` and `SDMA2_RLC5` register groups and to verify that every SDMA instance/queue group remains internally consistent across the full header.

### subset-b-003366: lines 7808-10409

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 7808-10409

## Purpose

This chunk is part of AMD's generated `sdma_4_4_0_sh_mask.h` register-field header for the SDMA 4.4.0 block. It does not implement runtime logic; it defines `__SHIFT` and `_MASK` constants used by the AMDGPU driver to pack, unpack, and test SDMA MMIO register fields without hard-coding bit positions in C code.

The covered range starts inside the `SDMA2_RLC5_RB_CNTL` field set, then covers the rest of `SDMA2_RLC5`, all of `SDMA2_RLC6` and `SDMA2_RLC7`, the `addressBlock: sdma0_sdma3dec` public register block for `SDMA3`, the full `SDMA3_GFX` and `SDMA3_PAGE` queue register groups, the full `SDMA3_RLC0` through `SDMA3_RLC3` compute queue groups, and the beginning of `SDMA3_RLC4` through `SDMA3_RLC4_RB_WPTR_POLL_CNTL`.

## Important APIs, Types, and Macro Families

There are no functions, structs, enums, or storage definitions in this chunk. The important public surface is the preprocessor macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the already-shifted field mask.
- The register names match the companion offset header, `sdma_4_4_0_offset.h`, where `regSDMA3_GFX_RB_CNTL`, `regSDMA3_PAGE_RB_CNTL`, `regSDMA3_RLC0_RB_CNTL`, and related address constants are defined.
- Driver code consumes these macros through common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32`, and `WREG32`.

The queue register groups repeat a common SDMA queue programming schema across `SDMA2_RLC5/6/7`, `SDMA3_GFX`, `SDMA3_PAGE`, and `SDMA3_RLC0/1/2/3`, with the start of the same schema for `SDMA3_RLC4`:

- Ring-buffer control and addressing: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer state: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, `IB_SUB_REMAIN`.
- Scheduling and context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, `MIDCMD_CNTL`.
- Doorbell and queue status: `DOORBELL`, `DOORBELL_OFFSET`, `DOORBELL_LOG`, `STATUS`, `WATERMARK`, `MINOR_PTR_UPDATE`.
- AQL queue support: `RB_AQL_CNTL`.

The `SDMA3` public engine block adds fields for firmware and engine-wide controls:

- Microcode and virtualization: `SDMA3_UCODE_ADDR`, `SDMA3_UCODE_DATA`, `SDMA3_VF_ENABLE`.
- Power, clock, and global control: `SDMA3_POWER_CNTL`, `SDMA3_CLK_CTRL`, `SDMA3_CNTL`, `SDMA3_POWER_CNTL_IDLE`, `SDMA3_CLK_STATUS`.
- Engine status and debug: `SDMA3_STATUS_REG`, `SDMA3_STATUS1_REG`, `SDMA3_STATUS2_REG`, `SDMA3_STATUS3_REG`, `SDMA3_STATUS4_REG`, `SDMA3_ERROR_LOG`, `SDMA3_PROGRAM`, `SDMA3_FREEZE`, `SDMA3_ID`, `SDMA3_VERSION`.
- Memory translation and UTCL1 behavior: `SDMA3_UTCL1_CNTL`, `SDMA3_UTCL1_WATERMK`, `SDMA3_UTCL1_RD_STATUS`, `SDMA3_UTCL1_WR_STATUS`, invalidation/XNACK registers, timeout, and page configuration.
- RAS and EDC: `CC_SDMA3_EDC_CONFIG`, `SDMA3_EDC_COUNTER`, `SDMA3_EDC_COUNTER2`, `SDMA3_RAS_STATUS`.
- Performance and diagnostics: `SDMA3_PERFCNT_*`, `SDMA3_F32_*`, `SDMA3_SCRATCH_RAM_*`, public dummy registers, and physical address debug fields.

## Control Flow and Runtime Use

This header has compile-time control flow only: include guards expose macro constants to translation units that include it. The runtime control flow lives in consumers. In this tree, `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes `sdma_4_4_0_offset.h` and this mask header, then uses the generated field macros indirectly through register helpers and RAS field tables.

For SDMA 4.4, `sdma_v4_4_get_reg_offset()` computes the absolute MMIO offset for SDMA instances by adding per-instance deltas such as `SDMA3_REG_OFFSET` to the SDMA0 base. KFD integration code also relies on queue register spacing, for example deriving an RLC queue register base from `mmSDMA*_RLC0_RB_CNTL` and adding `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. The repeated `RLCn` macro groups in this chunk must therefore stay aligned with the offset header's spacing assumptions.

Queue programming normally follows the hardware state model represented by these masks: program ring base and size, configure write/read pointer handling, set doorbell offset/enables, configure IB and VMID behavior, then enable the queue or allow preemption/context switching. The header only supplies field locations for those writes; ordering, synchronization, and polling are enforced by the driver and hardware documentation.

## State and Persistence Behavior

The macros describe persistent hardware state held in SDMA MMIO registers and, for selected queues, state mirrored to GPU memory:

- `RB_BASE*`, `RB_RPTR*`, `RB_WPTR*`, and `RB_CNTL` define queue ring-buffer state. Misprogramming these fields can persist until queue teardown, engine reset, or full GPU reset.
- `RB_RPTR_ADDR_*` enables read-pointer writeback into memory. `RPTR_WB_IDLE` in the low address register is a hardware-visible status bit, while the address field is aligned by a low-bit shift.
- `RB_WPTR_POLL_*` registers let hardware poll a memory write pointer, which creates persistence outside the MMIO register file because GPU memory contents drive queue progress.
- `CSA_ADDR_*`, `CONTEXT_STATUS`, `PREEMPT`, `MIDCMD_DATA*`, and `MIDCMD_CNTL` represent context-save/preemption state. These fields are especially relevant for recovery and context switch correctness.
- `DOORBELL`, `DOORBELL_OFFSET`, and `DOORBELL_LOG` connect the queue to doorbell aperture writes from the CPU or user-mode/KFD paths. Doorbell state persists while the queue is active.
- `EDC_COUNTER*`, `RAS_STATUS`, `STATUS*_REG`, `UTCL1_*_STATUS`, and XNACK/invalidation registers expose accumulated or in-flight hardware status that may survive until read-clear, explicit reset, or engine reset depending on the register.

Because this is a generated register header, there is no software serialization or persistence mechanism in the file itself. Its state model is entirely the SDMA hardware register file plus memory locations referenced by address fields.

## Dependencies and Integration Points

This chunk depends on exact agreement with several neighboring generated and driver components:

- `sdma_4_4_0_offset.h` supplies the `regSDMA*` offsets that pair with these masks.
- `sdma_4_4_0_default.h` or other default tables, where present in sibling ASIC register trees, must match reset defaults for fields such as `RB_CNTL`, `IB_CNTL`, `CONTEXT_STATUS`, and AQL control.
- `amdgpu/sdma_v4_4.c` includes this header for SDMA 4.4 RAS and register access support.
- `amdgpu_amdkfd_arcturus.c` and related KFD code derive SDMA RLC queue register bases and depend on consistent `RLCn` register layout across engines and queue IDs.
- Generic SOC15 register macros depend on the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern.

The generated macros are also conceptually tied to firmware and ASIC documentation. A one-bit drift in fields such as VMID, doorbell enable, writeback enable, preempt, UTCL1 credit/watermark, or RAS counters changes hardware behavior even though the C compiler will still build successfully.

## Risks and Edge Cases

- The line range begins mid-register at `SDMA2_RLC5_RB_CNTL`, so chunk-local readers need the previous chunk for the first four field definitions in that register. The remaining `RB_CNTL` fields in this chunk still show the same layout repeated for later queues.
- Queue blocks are repetitive but not purely cosmetic. A missing, duplicated, or shifted macro in one instance can break only a single engine/queue combination, making failures hardware- and workload-specific.
- `SDMA3_RLC4` is incomplete in this chunk; only `RB_CNTL` through `RB_WPTR_POLL_CNTL` appear before the line boundary. The following chunk must be consulted for the rest of that queue's IB, doorbell, context, and mid-command fields.
- Field widths encode alignment requirements. Address fields such as `IB_BASE_LO`, `RB_RPTR_ADDR_LO`, `DOORBELL_OFFSET`, and polling address lows mask off low bits. Consumers must provide aligned addresses and avoid assuming the raw register stores byte-granular values.
- `RB_VMID`, `CMD_VMID`, `RB_PRIV`, and doorbell fields are privilege/VM isolation sensitive. Incorrect masks can allow commands to execute in the wrong VM context or with wrong privilege.
- Preemption and mid-command save fields are recovery-sensitive. Incorrect `MIDCMD_CNTL`, `PREEMPT`, or `CONTEXT_STATUS` masks can make queue preemption, reset recovery, or context switch diagnostics unreliable.
- UTCL1 and XNACK fields affect memory translation retry, invalidation, and timeout behavior. Bad field definitions can present as hangs, page fault storms, or silent performance regressions rather than obvious compile failures.
- RAS counter masks feed error accounting. If EDC field masks drift, `sdma_v4_4` RAS reporting can undercount, overcount, or attribute errors to the wrong SDMA buffer.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for AMDGPU with SDMA 4.4 support verifies macro names expected by `sdma_v4_4.c`, SOC15 helpers, and KFD code still exist.
- Register read/write smoke tests should confirm `RB_CNTL` enable/size/writeback fields, `IB_CNTL`, doorbell enable/offset, and write-pointer polling fields land in the documented bits for `SDMA3_GFX`, `SDMA3_PAGE`, and representative `RLCn` queues.
- KFD queue creation tests on SDMA-capable ASICs should exercise RLC queue spacing and doorbell programming, especially queues near the edges covered here: `SDMA2_RLC7`, `SDMA3_RLC0`, `SDMA3_RLC3`, and `SDMA3_RLC4`.
- GPU reset, queue preemption, and hang-recovery tests should watch `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, and `MIDCMD_*` behavior.
- RAS injection or counter polling tests should validate `SDMA3_EDC_COUNTER`, `SDMA3_EDC_COUNTER2`, and `SDMA3_RAS_STATUS` accounting through the `sdma_v4_4` RAS path.
- VM fault and XNACK stress tests should monitor `SDMA3_UTCL1_*` status, invalidation, timeout, and page fields.
- Performance-counter tests should ensure `SDMA3_PERFCNT_*` configuration and result masks produce stable, nonzero counters under SDMA traffic.

### subset-b-003367: lines 10410-13008

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 10410-13008

## Scope

This chunk is a generated AMD SDMA 4.4.0 shift/mask header slice. It starts in the middle of the `SDMA3_RLC4_RB_WPTR_POLL_CNTL` register field list and ends in the middle of `SDMA4_RLC3_IB_CNTL`, after the `SWITCH_INSIDE_IB` shift field and before the remaining fields and masks. The document therefore covers a complete view of several repeated SDMA queue contexts, but not the full source header or even every register family touched by the first and last lines.

The covered register groups are:

- The tail of SDMA3 RLC4 queue-context masks, including write-pointer polling, read-pointer writeback address, indirect-buffer, doorbell, watermark, preempt, AQL, minor pointer, and mid-command fields.
- Full SDMA3 RLC5, RLC6, and RLC7 queue-context definitions with the same ring-buffer, indirect-buffer, context-status, doorbell, CSA, AQL, and mid-command layouts.
- The `sdma0_sdma4dec` address block for SDMA4 engine-public registers, including microcode access, VF enable, power/clock/control, status, error, UTCL1, performance counter, RAS, scratch, and copy-engine control registers.
- SDMA4 GFX and PAGE queue contexts.
- SDMA4 RLC0, RLC1, and RLC2 queue contexts.
- The beginning of SDMA4 RLC3 queue context through the first `IB_CNTL` shift fields.

This header chunk defines preprocessor constants only. It has no C functions, structs, variables, allocation paths, locks, or executable control flow.

## Purpose

The purpose of this range is to encode the bit-level contract between AMDGPU SDMA v4.4 code and the corresponding SDMA hardware registers. Every exported definition follows the generated convention:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the raw register mask used to isolate or compose the field.

The companion header `sdma_4_4_0_offset.h` supplies register addresses such as `regSDMA4_POWER_CNTL`, `regSDMA4_GFX_RB_CNTL`, and `regSDMA4_RLC0_RB_CNTL`. This `_sh_mask` header supplies the field positions used with AMDGPU/SOC15 helpers such as `SOC15_REG_FIELD`, `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, and `WREG32`.

`drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes this header directly. That driver calculates per-instance SDMA register offsets, queries and clears SDMA RAS counters, and programs or observes SDMA hardware using the matching generated address and mask names.

## Important Macro Families

### SDMA Queue Contexts

Most of the chunk is generated repetition for queue contexts. The common layout appears for SDMA3 RLC queues, SDMA4 GFX/PAGE queues, and SDMA4 RLC queues:

- `*_RB_CNTL` fields control ring-buffer enablement, ring size, byte swapping, read-pointer writeback, writeback timer, privilege bit, and VMID.
- `*_RB_BASE` and `*_RB_BASE_HI` provide the ring-buffer base address fields.
- `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` expose the ring read/write pointer offsets.
- `*_RB_WPTR_POLL_CNTL` controls hardware polling of the write pointer, including enable, swap enable, F32 polling, polling frequency, and idle poll count.
- `*_RB_RPTR_ADDR_HI` and `*_RB_RPTR_ADDR_LO` encode the read-pointer writeback address and the low-register `RPTR_WB_IDLE` status bit.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` describe indirect-buffer execution state.
- `*_SKIP_CNTL`, `*_PREEMPT`, `*_CONTEXT_STATUS`, `*_CSA_ADDR_LO`, and `*_CSA_ADDR_HI` describe command skipping, IB preemption, context-switch readiness/status, and context save area addresses.
- `*_DOORBELL`, `*_DOORBELL_LOG`, and `*_DOORBELL_OFFSET` define doorbell enable/captured state, logged backend error/data, and the doorbell offset.
- `*_WATERMARK` controls read and write outstanding request watermarks.
- `*_RB_AQL_CNTL` exposes AQL enablement, AQL packet size, and packet step.
- `*_MINOR_PTR_UPDATE` enables minor pointer update behavior.
- `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10` plus `*_MIDCMD_CNTL` encode the mid-command preemption snapshot/control surface, including data-valid, copy-mode, split-state, and allow-preempt fields.

The RLC context families are especially repetitive. SDMA3 RLC5-RLC7 and SDMA4 RLC0-RLC2 are complete in this chunk. SDMA3 RLC4 lacks the earlier ring-control/base/pointer definitions because those are in the previous chunk. SDMA4 RLC3 starts here but continues in the next chunk.

### SDMA4 Engine Control and Status

The `sdma0_sdma4dec` block defines fields for SDMA4 itself:

- Microcode access: `SDMA4_UCODE_ADDR`, `SDMA4_UCODE_DATA`, `SDMA4_UCODE_CHECKSUM`, and `SDMA4_PUB_REG_TYPE0`.
- Virtualization enablement: `SDMA4_VF_ENABLE`.
- Power and clock control: `SDMA4_POWER_CNTL`, `SDMA4_POWER_CNTL_IDLE`, `SDMA4_CLK_CTRL`, `SDMA4_CLK_STATUS`, and `SDMA4_ULV_CNTL`.
- Top-level control: `SDMA4_CNTL`, `SDMA4_CHICKEN_BITS`, `SDMA4_CHICKEN_BITS_2`, `SDMA4_FREEZE`, `SDMA4_F32_CNTL`, `SDMA4_PHASE0_QUANTUM`, `SDMA4_PHASE1_QUANTUM`, and `SDMA4_PHASE2_QUANTUM`.
- Memory and address configuration: `SDMA4_GB_ADDR_CONFIG`, `SDMA4_GB_ADDR_CONFIG_READ`, `SDMA4_HBM_PAGE_CONFIG`, `SDMA4_PHYSICAL_ADDR_LO`, and `SDMA4_PHYSICAL_ADDR_HI`.
- Fetch/progress registers: `SDMA4_RB_RPTR_FETCH`, `SDMA4_RB_RPTR_FETCH_HI`, `SDMA4_IB_OFFSET_FETCH`, `SDMA4_PROGRAM`, and `SDMA4_SEM_WAIT_FAIL_TIMER_CNTL`.
- Status families: `SDMA4_STATUS_REG`, `SDMA4_STATUS1_REG`, `SDMA4_STATUS2_REG`, `SDMA4_STATUS3_REG`, and `SDMA4_STATUS4_REG`.

These fields describe engine idle state, ring and IB command fullness, packet readiness, memory-client read/write idle status, semaphore and interrupt stalls, context empty state, active queue ID, SR-IOV command activity, freeze/preempt state, and scheduler quantum selection.

### UTCL1, Address Translation, and XNACK

The `SDMA4_UTCL1_*` registers expose translation-cache and retry/error behavior:

- `SDMA4_UTCL1_CNTL` configures request mode, bypass flags, invalidation mode, retry disablement, redirection behavior, client ID, and queue depth.
- `SDMA4_UTCL1_WATERMK` sets read/write watermark thresholds.
- `SDMA4_UTCL1_RD_STATUS` and `SDMA4_UTCL1_WR_STATUS` expose FIFO empty/full state, page fault/null status, L2 idle state, next vector, merge state, and read/write routing or pointer-data FIFO state.
- `SDMA4_UTCL1_INV0`, `INV1`, and `INV2` describe invalidation requests, timeout/error controls, VMID vectors, flush type, and invalidate address pieces.
- `SDMA4_UTCL1_RD_XNACK*` and `WR_XNACK*` record XNACK address, VMID, vector, and XNACK state for read and write paths.
- `SDMA4_UTCL1_TIMEOUT` controls read/write XNACK timeout limits.
- `SDMA4_UTCL1_PAGE` defines page-fault request attributes such as VM hole, request type, memory type use, and page-table snoop use.

These fields are integration points with GPUVM, retryable page faults, memory translation, and diagnostic paths. The masks themselves do not encode the legal sequencing for invalidation or XNACK recovery.

### RAS, EDC, Error, and Performance Monitoring

The chunk includes SDMA4 reliability and observability fields:

- `CC_SDMA4_EDC_CONFIG` exposes EDC disablement.
- `SDMA4_EDC_COUNTER` has per-data-buffer single-error-detect counters for MBANK buffers 0 through 15.
- `SDMA4_EDC_COUNTER2` covers additional single-error-detect counters, including microcode, ring-buffer command, indirect-buffer command, UTCL1 read/write, data LUT, split data, and memory-client FIFOs.
- `SDMA4_RAS_STATUS` exposes ECC and NACK-generated error status for ring fetch, IB fetch, F32 data, semaphore/write-pointer atomic paths, copy data, SRAM, write-return data, and write/read pointer atomic paths.
- `SDMA4_ERROR_LOG` provides override and status fields.
- `SDMA4_PERFCNT_*` registers configure two performance counters, select result counters, set start/stop triggers, clear counters, stop on saturation, and read low/high counter values plus compare value.

`sdma_v4_4.c` has RAS query/reset code that uses shared SDMA counter masks through `SOC15_REG_FIELD` entries. The chunk's SDMA4-specific counter definitions are the generated per-instance equivalents of the same hardware layout.

## Control Flow and State Behavior

This chunk has no runtime control flow. Its effect is compile-time substitution:

1. AMDGPU code includes `sdma_4_4_0_offset.h` and `sdma_4_4_0_sh_mask.h`.
2. Code reads or prepares a 32-bit SDMA register value at an address from the offset header.
3. Code applies a generated mask and shift to decode a field or compose a new value.
4. Hardware state changes only when code outside this header writes the corresponding register.

The state represented by these macros is hardware state. Persistent or semi-persistent configuration includes ring bases, ring sizes, VMIDs, privilege bits, read-pointer writeback addresses, doorbell offsets, AQL settings, context save area addresses, watermarks, power/clock controls, UTCL1 control policy, performance counter configuration, and scheduler quantum registers. Transient state includes read/write pointers, context selected/idle/preempted flags, doorbell captured/log fields, status registers, FIFO full/empty flags, XNACK records, RAS/error status, EDC counters, and performance counter results.

Some fields are command-like or side-effectful at the hardware level, such as preempt, freeze, F32 halt/step/reset, counter clear, interrupt clear, invalidation controls, and RAS/counter clear behavior. The header does not indicate write-one-to-clear, sticky, polling, timeout, reset, or ordering requirements; those rules must come from the SDMA v4.4 driver and hardware specification.

## Dependencies and Integration Points

The immediate dependencies are the generated SDMA register headers:

- `sdma_4_4_0_offset.h` for register addresses and base indices.
- `sdma_4_4_0_sh_mask.h` for the shifts and masks in this chunk.
- Other SDMA generation headers such as `sdma_4_4_2_*` for nearby ASIC variants, which must not be mixed with 4.4.0 definitions without checking generation compatibility.

The main source-tree integration point is `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c`, which includes this header and the offset header. That driver provides per-instance register offset calculation, RAS error query/reset paths, and SDMA v4.4 hardware management. SDMA ring, VM, RAS, interrupt, reset, SR-IOV, and power-management code use the same generated naming convention through AMDGPU and SOC15 helpers.

Semantically, the queue-context fields integrate with AMDGPU ring scheduling and doorbells; IB fields integrate with indirect command submission; CSA and mid-command fields integrate with context switch and preemption; UTCL1 fields integrate with GPUVM, page-fault, and XNACK handling; EDC/RAS fields integrate with AMDGPU RAS reporting; performance counters integrate with profiling and debug paths; power/clock fields integrate with runtime power management and suspend/resume.

## Risks and Maintenance Notes

- The range starts and ends mid-family. Adjacent chunks are required for the complete SDMA3 RLC4 and SDMA4 RLC3 context descriptions.
- Bitfield drift is high impact. A wrong shift or mask can program the wrong ring size, VMID, address, doorbell, preempt bit, UTCL1 behavior, power state, or error counter.
- The queue-context blocks are highly repetitive. Copy or generation errors can be hard to review because only the SDMA instance and queue prefix changes.
- Address fields have alignment encoded in masks, such as ring-pointer writeback lows and IB base lows. Consumers must preserve the expected low-bit alignment and not treat full-width masks as arbitrary byte addresses.
- Doorbell and pointer fields are synchronization-sensitive. Incorrect polling frequency, stale read/write pointer decode, or bad doorbell offset can hang queues or lose submissions.
- Context-switch and mid-command fields are preemption-sensitive. Incorrect masks can break context save/restore, IB preemption, or SR-IOV/RLC scheduling behavior.
- UTCL1 invalidation and XNACK fields are VM-sensitive. Incorrect writes can turn translation faults into hangs, mask retry state, or invalidate the wrong VMID/address range.
- RAS and EDC counters may have clear-on-write or sticky semantics outside this header. Treating counter/status masks as normal read/write fields can lose diagnostic evidence.
- Full-width constants use the generated `L` suffix, including `0xFFFFFFFFL`; callers should continue using the established AMDGPU register helper types to avoid signedness or truncation problems.
- Cross-generation reuse is risky. The 4.4.0 and 4.4.2 headers look similar, but queue count, offsets, and masks can differ.

## Test and Validation Signals

Useful validation for this chunk is mostly build, static consistency, and hardware integration coverage:

- Build AMDGPU with SDMA v4.4 support so all includes of `sdma_4_4_0_sh_mask.h` and `sdma_4_4_0_offset.h` resolve.
- Static checks should confirm that each complete field in this chunk has matching `__SHIFT` and `_MASK` definitions and that masks are aligned with their shift positions.
- Cross-header checks should confirm every complete register family in this chunk has a matching address macro in `sdma_4_4_0_offset.h`.
- SDMA ring tests should submit GFX, PAGE, and RLC queue work and verify ring base, size, read/write pointer, doorbell, writeback, and IB progress fields decode correctly.
- Preemption/context-switch tests should exercise `CONTEXT_STATUS`, `CSA_ADDR`, `PREEMPT`, and `MIDCMD_*` behavior under IB preemption and context switching.
- VM and page-fault tests should exercise UTCL1 read/write status, invalidation, timeout, and XNACK reporting under GPUVM and retryable fault workloads.
- RAS validation should inject or observe SDMA EDC/ECC/NACK conditions and confirm `EDC_COUNTER`, `EDC_COUNTER2`, `RAS_STATUS`, and reset paths report and clear the intended fields.
- Power-management tests should cover SDMA clock/power gating, ULV entry/exit, freeze/unfreeze, suspend/resume, and idle status polling.
- Performance-counter validation should configure both SDMA4 counters, trigger start/stop/clear paths, and verify low/high result decoding without disturbing queue execution.
- SR-IOV or virtualization validation should cover VF enablement, RLC queue ownership/VMID fields, and status fields such as active queue ID and SR-IOV command activity.

### subset-b-003368: lines 13009-13922

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 13009-13922

## Scope

This chunk covers a generated AMD SDMA 4.4.0 shift/mask header region for `SDMA4_RLC*` queue registers. The range starts in the tail of the `SDMA4_RLC3_IB_CNTL` field definitions and continues through the complete `SDMA4_RLC4`, `SDMA4_RLC5`, `SDMA4_RLC6`, and `SDMA4_RLC7` register-field groups, ending just before the header guard's final `#endif`.

The chunk contains 703 preprocessor `#define` entries. It defines constants only: there are no C functions, structs, enums, variables, allocations, locking paths, or executable branches in the selected lines.

## Purpose

The purpose of this header section is to provide the bit-level ABI between SDMA 4.4.0 hardware and AMDGPU code that reads or writes SDMA RLC queue registers. Each hardware field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

These macros are intended to be paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h`, which supplies the matching `regSDMA4_RLC*_*` register addresses. Runtime consumers include the SDMA 4.4 support code that includes this header, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c`, and the broader AMDGPU register helper machinery around `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and SOC15 offset handling.

## Register Families

### RLC3 Tail

The first lines continue an `SDMA4_RLC3_IB_CNTL` definition started before the chunk. Within this chunk the visible fields are:

- `CMD_VMID`, plus masks for `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`.
- Indirect-buffer pointer/address/size fields: `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Queue status and scheduling fields: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, and `MINOR_PTR_UPDATE`.
- Doorbell and pointer polling fields: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Context-save and diagnostic fields: `CSA_ADDR_LO`, `CSA_ADDR_HI`, `DUMMY_REG`, `WATERMARK`, `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

Because the line range begins after the first `SDMA4_RLC3_IB_CNTL` shift definitions, `IB_ENABLE__SHIFT`, `IB_SWAP_ENABLE__SHIFT`, and `SWITCH_INSIDE_IB__SHIFT` for RLC3 live in the preceding chunk even though their masks are present here.

### RLC4 Through RLC7 Queues

The rest of the range repeats the same queue register layout for `SDMA4_RLC4`, `SDMA4_RLC5`, `SDMA4_RLC6`, and `SDMA4_RLC7`. Each complete queue group exposes:

- Ring-buffer control and addressing: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
- Write-pointer polling: `RB_WPTR_POLL_CNTL`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer dispatch: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Queue status, preemption, and context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, and `MINOR_PTR_UPDATE`.
- Doorbell handling: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- Flow-control and command snapshot fields: `WATERMARK`, `RB_AQL_CNTL`, `DUMMY_REG`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

The repeated layout makes these RLC queues register-compatible. Driver code can often use a base register plus a queue stride, while the generated macros preserve queue-specific symbolic names for compile-time field composition.

## Important Fields

`RB_CNTL` is the primary ring-buffer configuration register. Its fields include `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`. Incorrect values here can prevent queue execution, corrupt pointer writeback, or run a queue under the wrong VMID/privilege context.

`RB_BASE` and `RB_BASE_HI` describe the ring buffer GPU address. The low-address register is full-width in this mask header, while the high register masks only 24 bits. Pointer registers (`RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`) are full-width offsets, and the writeback address low registers mask address bits with 4-byte alignment.

`RB_WPTR_POLL_CNTL` controls hardware polling of the write pointer. The relevant fields are `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, `FREQUENCY`, and `IDLE_POLL_COUNT`. The companion poll address registers provide the memory location being polled.

`IB_CNTL` enables indirect-buffer execution and describes command interpretation with `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`. `IB_BASE_LO` is 32-byte aligned, `IB_RPTR` and `IB_OFFSET` use bit-2 alignment, and `IB_SIZE`/`IB_SUB_REMAIN` expose 20-bit size counters.

`CONTEXT_STATUS` is the main queue state observation register. It includes `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`. These bits are useful for bring-up, queue reset, preemption, and post-hang diagnostics.

`DOORBELL` and `DOORBELL_OFFSET` define whether MMIO/doorbell writes are enabled for the queue and where the queue listens in the doorbell aperture. `DOORBELL_LOG` captures backend error state and logged doorbell data. `STATUS` exposes write-pointer update failure and pending indicators.

`WATERMARK` carries read and write outstanding thresholds. `RB_AQL_CNTL` enables AQL packet mode and configures packet size/step. `MIDCMD_DATA*` and `MIDCMD_CNTL` capture or restore mid-command state with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`, which is relevant to preemption and command replay.

## APIs, Types, and Functions

This chunk does not define callable APIs or C types. Its practical API surface is the generated macro naming convention consumed by AMDGPU register helpers:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` expects the same mask/shift pair.
- `SOC15_REG_FIELD`, RAS field tables, and generated register metadata use the same `REGISTER__FIELD_*` convention.
- `RREG32`/`WREG32` and SOC15-specific wrappers perform the actual MMIO access once a matching register offset is selected.

The companion offset header provides register addresses such as `regSDMA4_RLC4_RB_CNTL`, `regSDMA4_RLC5_DOORBELL`, and `regSDMA4_RLC7_MIDCMD_CNTL`. This mask header provides only field extraction/composition constants for the values read from or written to those addresses.

## Control Flow

There is no local control flow in the chunk. The effective runtime flow happens in driver code that includes the header:

1. Select an SDMA instance and queue register offset from the offset header or a helper that applies an instance base offset.
2. Read the current register value when preserving unrelated fields is required.
3. Use `REG_SET_FIELD` or direct mask/shift operations to compose new field values.
4. Write the composed value with an MMIO helper.
5. Poll status fields such as `CONTEXT_STATUS`, `STATUS`, or pointer registers when waiting for idle, queue stop, pointer writeback, or reset completion.

For this repository snapshot, `amdgpu/sdma_v4_4.c` includes `sdma_4_4_0_sh_mask.h` and uses the same generated-mask style for SDMA 4.4 RAS counter fields. Queue setup code for nearby SDMA generations, such as `sdma_v4_4_2.c`, demonstrates the normal pattern: configure ring buffer size/address, pointer writeback, write-pointer polling, doorbells, then set `RB_ENABLE` and `IB_ENABLE`.

## State and Persistence

The macros themselves are compile-time constants and hold no process or kernel state. The hardware registers they describe are volatile device state:

- Ring and indirect-buffer base addresses persist in hardware until reset, suspend, power gating, or explicit reprogramming.
- Read/write pointers and IB offsets change as SDMA consumes queue work.
- Doorbell capture/log/status fields reflect runtime doorbell activity and errors.
- Context-status and mid-command fields reflect queue scheduling/preemption state and may be meaningful during hang recovery or context save/restore.
- RLC context-save addresses (`CSA_ADDR_LO`/`CSA_ADDR_HI`) point hardware at memory used for queue context state.

On suspend/resume, reset, GPU recovery, or XCP/partition transitions, driver code must reestablish the relevant register state from `struct amdgpu_ring`, firmware-derived topology, doorbell assignments, and memory manager allocations. The header is part of that persistent hardware contract but does not persist anything by itself.

## Dependencies and Integration Points

This chunk depends on generated ASIC register conventions shared across AMDGPU:

- `sdma_4_4_0_offset.h` for `regSDMA4_RLC*_*` register addresses.
- `soc15.h` and AMDGPU MMIO helpers for translating logical register names into mapped MMIO offsets.
- `amdgpu_ring` state for ring base address, read/write pointer backing memory, doorbell index, and queue size.
- Doorbell management in AMDGPU/KFD paths, because `DOORBELL` and `DOORBELL_OFFSET` must match the doorbell aperture assignment visible to user queues or kernel queues.
- VMID and context-switching code, because `RB_VMID`, `CMD_VMID`, `CSA_ADDR*`, `PREEMPT`, and `CONTEXT_STATUS` encode queue ownership and preemption behavior.
- SDMA firmware and microcode behavior, which consumes these register values and updates status/pointer fields.

There is also a KFD-facing integration point in `amdgpu_amdkfd_arcturus.c`, which computes SDMA RLC register spacing from `mmSDMA4_RLC0_RB_CNTL` in the related `sdma4_4_2_2` register set. That pattern reinforces that RLC queue registers are laid out as repeated queue blocks.

## Risks

The main risk is register-definition drift. If a mask or shift does not match the SDMA 4.4.0 hardware specification, the driver may silently program the wrong bits. For this chunk, high-impact examples include `RB_ENABLE`, `IB_ENABLE`, `DOORBELL__ENABLE`, `RB_VMID`, `CMD_VMID`, `RB_BASE_HI`, `RB_RPTR_ADDR_LO__ADDR`, and `MIDCMD_CNTL`.

Alignment-sensitive fields are another risk. Several address/offset fields intentionally mask low bits: `IB_BASE_LO` starts at bit 5, `IB_RPTR`/`IB_OFFSET` start at bit 2, doorbell offsets are 4-byte aligned, and pointer writeback addresses mask low bits. Driver code that shifts or pre-aligns values incorrectly can point hardware at the wrong memory.

The RLC3 portion is split across chunk boundaries. Research or generated checks that treat this chunk as an independent complete register group must account for the missing RLC3 `IB_CNTL` shift lines that precede line 13009.

Queue-specific repetition can hide copy/paste or generation errors. RLC4-RLC7 should be structurally identical for most fields, so a single divergent mask may only affect one queue and appear as an intermittent multi-queue scheduling or KFD workload issue.

Doorbell and VMID fields are security-sensitive in virtualized or multi-process GPU workloads. A wrong doorbell offset or VMID can cause work submission to target the wrong queue or address space.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-level, and hardware-integration signals:

- The kernel tree compiles with `sdma_4_4_0_sh_mask.h` included by `amdgpu/sdma_v4_4.c`; missing or renamed masks should fail builds where corresponding `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD` uses exist.
- Generated-header consistency checks can compare every `SDMA4_RLC4` through `SDMA4_RLC7` register group for identical field names, shifts, and masks where the hardware layout is expected to repeat.
- Offset/mask pairing checks can verify that every register comment in this chunk has a matching `regSDMA4_RLC*_*` definition in `sdma_4_4_0_offset.h`.
- Runtime queue bring-up should show successful SDMA ring tests and IB tests, with ring pointers advancing and no `WPTR_UPDATE_FAIL_COUNT` growth.
- Doorbell tests should confirm that enabling `DOORBELL__ENABLE` and programming `DOORBELL_OFFSET` causes write-pointer updates to reach the expected queue.
- Hang recovery and reset tests should observe sensible `CONTEXT_STATUS` transitions, successful `PREEMPT` behavior where supported, and restored ring/IB state after resume.
- RAS and diagnostics should still compile and report SDMA instance state correctly, because the SDMA 4.4 code includes this generated mask header alongside the offset header.
