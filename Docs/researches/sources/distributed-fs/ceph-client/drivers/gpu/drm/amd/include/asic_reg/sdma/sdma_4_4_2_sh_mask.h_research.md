# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003370`: lines 1-2529, `Docs/researches/chunks/subset-b-003370_research.md`
- `subset-b-003371`: lines 2530-3300, `Docs/researches/chunks/subset-b-003371_research.md`

## Chunk Research

### subset-b-003370: lines 1-2529

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_sh_mask.h lines 1-2529

## Scope

This chunk covers the beginning of the generated SDMA 4.4.2 AMDGPU shift/mask header through the start of the `SDMA_RLC4_RB_CNTL` field set. The source range is a C preprocessor register metadata file, not executable driver logic. It contains the copyright/license header, the include guard `_sdma_4_4_2_SH_MASK_HEADER`, and 2,137 `#define` entries across 367 visible register blocks in the requested line span.

The covered register families include:

- Public SDMA microcode, F32, MMHUB, VM context, VF/virtual reset, and context/public register-type bitmap fields.
- Global SDMA queue fetch, status, freeze, phase quantum, power-gating, PGFSM, EDC, burst, atomic, UTCL1, page-fault/XNACK, error-log, performance-counter, GPU IOV violation, ULV, RAS, clock, control, chicken-bit, and address-config fields.
- GFX and PAGE queue context registers for ring buffers, indirect buffers, write-pointer polling, read-pointer writeback, doorbells, CSA addresses, preemption, AQL, minor pointer update, and mid-command save/restore data.
- RLC queue context register templates for `SDMA_RLC0`, `SDMA_RLC1`, `SDMA_RLC2`, `SDMA_RLC3`, and the beginning of `SDMA_RLC4`.

The file continues after this chunk with the remainder of the `SDMA_RLC4` family and later SDMA context blocks. Those later definitions must be merged with this chunk for a whole-file report.

## Purpose

This header supplies the bitfield ABI for programming and decoding SDMA 4.4.2 hardware registers. For each register field it defines the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset where the field starts.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose the field value.

Consumers combine these macros with the matching SDMA 4.4.2 offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, and SOC15/IP-specific address helpers. The offset header supplies the register address; this header supplies the field layout inside the 32-bit register value.

## Important Macro Families

### Core SDMA and Virtualization Registers

The top of the chunk defines basic SDMA control surfaces:

- `SDMA_UCODE_ADDR` and `SDMA_UCODE_DATA` describe microcode-address and data payload fields.
- `SDMA_F32_CNTL` exposes halt, step, debug select, reset, and checksum-clear fields for the F32 block.
- `SDMA_MMHUB_CNTL`, `SDMA_MMHUB_TRUSTLVL`, `SDMA_VM_CNTL`, `SDMA_VM_CTX_LO`, `SDMA_VM_CTX_HI`, and `SDMA_VM_CTX_CNTL` describe MMHUB trust/security flags, VM command fields, context addresses, privilege, and VMID.
- `SDMA_ACTIVE_FCN_ID`, `SDMA_VIRT_RESET_REQ`, and `SDMA_VF_ENABLE` expose VF/PF identity, virtual reset request, and VF enable state used by virtualization paths.

These definitions are small, but they touch privileged hardware state: VMID selection, secure/trust-level flags, VF reset, and active function identity must match the ASIC specification exactly.

### Context and Public Register Type Bitmaps

`SDMA_CONTEXT_REG_TYPE0` through `SDMA_CONTEXT_REG_TYPE3` and `SDMA_PUB_REG_TYPE0` through `SDMA_PUB_REG_TYPE3` are bitmaps that classify which SDMA context or public registers belong to broad generated type groups. The context type maps include GFX ring-buffer, indirect-buffer, doorbell, context-control/status, preempt, AQL, minor-pointer, and mid-command fields. The public type maps include microcode, status, burst, HBM page config, freeze, power, PGFSM, EDC, atomic, UTCL1, performance-counter, error-log, GPU IOV, RAS, clock, control, chicken-bit, and global address-config registers.

These type masks are integration glue for save/restore, register enumeration, debug, or generated register-table code. They do not configure hardware directly unless a consumer writes the referenced registers through the separately generated addresses.

### Status, Power, Clock, and Control Registers

The public register section defines detailed SDMA status and control layouts:

- `SDMA_STATUS_REG`, `SDMA_STATUS1_REG`, `SDMA_STATUS2_REG`, `SDMA_STATUS3_REG`, and `SDMA_STATUS4_REG` expose idle, FIFO full/empty, command, copy-engine, UTCL1, RAS, context, interrupt, and queue-state observations.
- `SDMA_FREEZE`, `SDMA_PHASE0_QUANTUM`, `SDMA_PHASE1_QUANTUM`, and `SDMA_PHASE2_QUANTUM` define preemption/freeze and scheduler quantum fields.
- `SDMA_POWER_GATING`, `SDMA_PGFSM_CONFIG`, `SDMA_PGFSM_WRITE`, `SDMA_PGFSM_READ`, `SDMA_POWER_CNTL_IDLE`, `SDMA_POWER_CNTL`, `SDMA_CLK_STATUS`, and `SDMA_CLK_CTRL` define power state machine access, idle delays, power-status duration counters, clock gating status, and software override bits.
- `SDMA_CNTL` defines main SDMA enable/interrupt controls including trap, UTC L1, semaphore wait interrupt, swap enables, mid-command preempt/expire, register-write-protect, invalid doorbell, VM hole, ECC, retry timeout, page-null/fault, NACK error, world-switch, automatic context switch, DRM restore, context-empty, frozen, IB preempt, and RB preempt interrupt controls.
- `SDMA_CHICKEN_BITS` and `SDMA_CHICKEN_BITS_2` expose tuning or workaround-oriented fields such as copy efficiency, stalls on full/no-free buffers, F32 MGCG, burst length/wait, overlap, RAW check, SRBM retrying, clock-gating output, SRAM fine-grain clock gating, F32 command delay, and postcode enable.

Most of these fields are low-level hardware controls rather than ordinary software state. Several are likely sticky, status-only, command-like, or write-one-to-clear depending on the register semantics outside this mask file.

### Memory Translation, Fault, XNACK, and Page Registers

The chunk contains UTCL1 and address-translation related registers:

- `SDMA_UTCL1_CNTL` and `SDMA_UTCL1_WATERMK` control redirect, fault handling, retry behavior, and FIFO watermarks.
- `SDMA_UTCL1_RD_STATUS` and `SDMA_UTCL1_WR_STATUS` expose read/write FIFO empty/full state, page fault/null state, L2 idle, CE/F32 stalls, next vector, merge state, router state, and polling status.
- `SDMA_UTCL1_INV0`, `SDMA_UTCL1_INV1`, and `SDMA_UTCL1_INV2` define invalidation control, flush type, VMID vectors, and invalidation address fields.
- `SDMA_UTCL1_RD_XNACK0/1` and `SDMA_UTCL1_WR_XNACK0/1` capture XNACK addresses, VMID, vector, and XNACK classification.
- `SDMA_UTCL1_TIMEOUT` defines read and write XNACK timeout limits.
- `SDMA_UTCL1_PAGE`, `SDMA_PHYSICAL_ADDR_LO`, and `SDMA_PHYSICAL_ADDR_HI` describe VM hole, request type, TMZ, memory type/snoop/no-alloc controls, valid/dirty flags, and translated physical address bits.

These fields integrate SDMA with GPUVM/MMHUB behavior. Misprogramming can change page-fault handling, retry timeout behavior, protected-memory access, cacheability/snoop attributes, or fault address reporting.

### Error, RAS, EDC, IOV, and Performance Monitoring

The chunk defines diagnostic and reliability-facing fields:

- `CC_SDMA_EDC_CONFIG`, `SDMA_EDC_COUNTER`, and `SDMA_EDC_COUNTER2` cover EDC disable/write-protect behavior and many parity/error counters for command, queue, UTCL1, DSC, split, AQL, RLC, and multicast paths.
- `SDMA_ERROR_LOG`, `SDMA_EA_DBIT_ADDR_DATA`, `SDMA_EA_DBIT_ADDR_INDEX`, `SDMA_RAS_STATUS`, `SDMA_UE_ERR_STATUS_LO`, and `SDMA_UE_ERR_STATUS_HI` provide error override/status, double-bit address access, RAS poison/error status, and uncorrectable error status low/high bits.
- `SDMA_GPU_IOV_VIOLATION_LOG` and `SDMA_GPU_IOV_VIOLATION_LOG2` expose GPU IOV violation status, multiple-violation state, address, write operation, VF/VFID, and initiator ID.
- `SDMA_PERFCNT_PERFCOUNTER0_CFG`, `SDMA_PERFCNT_PERFCOUNTER1_CFG`, `SDMA_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA_PERFCNT_MISC_CNTL`, `SDMA_PERFCNT_PERFCOUNTER_LO`, and `SDMA_PERFCNT_PERFCOUNTER_HI` define event selection, mode, enable, clear, start/stop triggers, saturation behavior, command-op filtering, MMHUB request event selection, counter result, and compare value.

These macros support hardware diagnostics, RAS collection, performance monitoring, and virtualization violation reporting. Correct masks are important for field-service debug and for security-sensitive IOV paths.

### GFX and PAGE Queue Contexts

From `SDMA_GFX_RB_CNTL` through `SDMA_GFX_MIDCMD_CNTL`, and again from `SDMA_PAGE_RB_CNTL` through `SDMA_PAGE_MIDCMD_CNTL`, the chunk defines two similarly shaped SDMA queue contexts. Each family contains:

- Ring-buffer controls and addresses: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
- Indirect-buffer controls and addresses: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, and `IB_SIZE`.
- Queue and context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `IB_SUB_REMAIN`, `PREEMPT`, and `DUMMY_REG`.
- Host polling and AQL controls: `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`, `RB_AQL_CNTL`, and `MINOR_PTR_UPDATE`.
- Mid-command state: `MIDCMD_DATA0` through `MIDCMD_DATA10` and `MIDCMD_CNTL`.

The ring controls define enable, size, swap, read-pointer writeback, privilege, and VMID fields. IB controls define enable, swap, switch-inside-IB, command VMID, and privilege. Context status fields expose selected, idle, expired, exception, context-switch ability/readiness, preempted, and preempt-disable state. Doorbell and polling fields link hardware queues to CPU-visible doorbell/write-pointer mechanisms.

### RLC Queue Context Templates

The final large section in this chunk repeats the same queue-context template for `SDMA_RLC0`, `SDMA_RLC1`, `SDMA_RLC2`, and `SDMA_RLC3`, then begins `SDMA_RLC4_RB_CNTL` before the chunk ends at line 2529. The RLC queue families mirror the GFX/PAGE shape:

- `RB_CNTL`, base, read/write pointer, write-pointer polling, and read-pointer writeback fields.
- `IB_CNTL`, IB pointer/base/size fields.
- Context status, doorbell, doorbell log, watermark, doorbell offset, CSA address, preempt, AQL, minor pointer update, and mid-command data/control fields.

The repeated layouts imply generated ASIC metadata for multiple SDMA queue contexts. The consistency is intentional, but it also makes copy or generator drift hard to detect by eye. The whole-file merge should verify that RLC4 and later RLC queue sections continue the same pattern in following chunks.

## Control Flow and State Behavior

This chunk has no runtime control flow. It defines compile-time constants only: no functions, structs, variables, allocations, loops, conditionals, or persistence mechanisms appear in the source span.

The state described by the macros is persistent or transient hardware register state inside the SDMA 4.4.2 IP block. Configuration fields include queue enables, ring sizes, VMIDs, privilege bits, swap controls, write-pointer polling parameters, AQL enable/packet sizing, interrupt enables, power/clock gating controls, page/translation controls, performance-counter selection, and virtualization enable/reset fields. Status fields include idle/full/empty indicators, page-fault and XNACK state, RAS/EDC counters, violation logs, context status, doorbell capture/log data, power/clock status, and performance-counter results.

The header itself does not encode whether a field is read-only, write-only, sticky, write-one-to-clear, reset-sensitive, or requires polling/timeouts. Those semantics must come from the SDMA hardware specification and the AMDGPU code that consumes these macros.

## Dependencies and Integration Points

The chunk depends on the generated AMD register-header convention:

- The matching `sdma_4_4_2_offset.h` supplies register addresses and base indices for names such as `regSDMA_CNTL`, `regSDMA_GFX_RB_CNTL`, or `regSDMA_RLC3_MIDCMD_CNTL`.
- The matching `sdma_4_4_2_default.h`, where present, supplies reset/default values.
- AMDGPU SDMA, VM, power-management, reset, RAS, and virtualization code consumes the `__SHIFT` and `_MASK` macros through AMD register helpers rather than hard-coded bit constants.

Likely integration points in the source tree include:

- SDMA IP initialization and teardown paths that program `SDMA_CNTL`, queue rings, doorbells, VMIDs, interrupt enables, clock/power gating, and microcode/control registers.
- Ring-management paths for GFX, PAGE, and RLC queues that maintain read/write pointers, ring bases, write-pointer polling, read-pointer writeback, IB execution, preemption, and mid-command context state.
- GPUVM/MMHUB paths that rely on UTCL1 invalidation, page-fault, XNACK, VM hole, TMZ, physical-address, and timeout encodings.
- SR-IOV or GPU virtualization paths that use VF enable/reset, active function ID, trust-level, and GPU IOV violation fields.
- RAS and diagnostics paths that decode EDC counters, RAS status, uncorrectable error status, error logs, performance counters, and public status registers.
- Power-management code that reads or writes power-gating, PGFSM, ULV, clock status/control, idle-delay, and chicken-bit fields.

The definitions are ASIC-generation specific. Mixing SDMA 4.4.2 masks with offsets or defaults from a nearby SDMA generation can silently program wrong bits even when register names are similar.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can corrupt queue setup, point SDMA at the wrong ring/IB address, write reserved bits, misdecode status, or enable incorrect interrupt behavior.
- Queue-context blocks are highly repetitive. GFX, PAGE, and RLC families share layouts, so generator or manual copy errors can swap a queue prefix, lose a high-address mask, or mismatch a field while still compiling.
- Address alignment masks are critical. Ring read-pointer writeback low addresses use low-bit alignment masks, IB base low fields start at bit 5, and doorbell offsets use aligned offsets; using the wrong mask can produce invalid DMA addresses.
- VM, UTCL1, page, XNACK, and TMZ fields affect memory translation and protected memory behavior. Incorrect values can cause page faults, retries/timeouts, stale invalidations, or security-sensitive access changes.
- Virtualization and GPU IOV fields are privilege-sensitive. VF enable/reset, active function ID, trust levels, and violation logs must not be decoded or written with masks from another ASIC.
- Status and error fields may be sticky or write-one-to-clear in hardware. Treating masks as proof of ordinary read/write behavior can lose diagnostic evidence or fail to clear real faults.
- Power, clock, chicken-bit, and PGFSM controls can affect hardware stability. Writes require the sequencing and constraints enforced by the owning driver paths, not just the bit masks.
- The chunk ends inside `SDMA_RLC4_RB_CNTL`, so this document is not sufficient to describe the full RLC4 queue context or the rest of the header.

## Test and Validation Signals

Useful validation is mostly build-time and hardware integration coverage:

- Build AMDGPU code that includes `sdma/sdma_4_4_2_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Compile or static-check SDMA 4.4.2 consumers that use `REG_GET_FIELD`/`REG_SET_FIELD` against queue, VM, power, RAS, and virtualization fields.
- Exercise SDMA ring bring-up for GFX, PAGE, and RLC queues and confirm ring base, size, read/write pointer, doorbell, write-pointer polling, read-pointer writeback, and IB fields behave on supported hardware.
- Run GPUVM/page-fault/XNACK scenarios that validate UTCL1 invalidation, page status, VM hole, timeout, XNACK address/vector, and TMZ-related fields.
- Validate preemption and context save/restore paths, including context status, CSA addresses, IB sub-remaining, mid-command data/control, and minor pointer update fields.
- Use RAS/error-injection or hardware diagnostics where available to confirm EDC counters, RAS status, uncorrectable error status, error logs, and GPU IOV violation logs decode as expected.
- Exercise power-management transitions to verify power-gating, PGFSM, ULV, clock status/control, idle-delay, and chicken-bit settings do not regress suspend/resume or runtime power behavior.
- Validate SR-IOV/VF paths on supported hardware to confirm VF enable/reset, active function ID, trust-level, and violation-log fields match expected PF/VF behavior.

### subset-b-003371: lines 2530-3300

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_sh_mask.h lines 2530-3300

## Purpose

This chunk is the tail of the generated SDMA 4.4.2 shift/mask header. It defines C preprocessor constants for bit shifts and masks used to program SDMA RLC queue registers, specifically the end of `SDMA_RLC4_RB_CNTL`, the full RLC5 and RLC6 register-field sets, and the full RLC7 set through `SDMA_RLC7_MIDCMD_CNTL`, followed by the header guard close.

The values are hardware ABI data rather than executable logic. Driver code combines these masks with matching register offsets from `sdma_4_4_2_offset.h` and helper macros such as `REG_SET_FIELD()` / `REG_GET_FIELD()` to configure and inspect SDMA queues without hard-coding bit positions at each call site.

## Important Definitions

The chunk repeats the same register-field pattern for RLC queue instances 4 through 7:

- Ring buffer control and pointer state:
  `SDMA_RLCx_RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
  The control fields include `RB_ENABLE`, `RB_SIZE`, byte-swap enable, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID`.
- Write-pointer polling and read-pointer writeback:
  `RB_WPTR_POLL_CNTL`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`.
  These encode enable bits, polling frequency, idle poll count, alignment-constrained addresses, and `RPTR_WB_IDLE`.
- Indirect buffer execution:
  `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
  Important fields include `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, command VMID, privilege, aligned IB base, and remaining IB size.
- Queue scheduling/status:
  `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `MINOR_PTR_UPDATE`, and `DUMMY_REG`.
  `CONTEXT_STATUS` exposes `SELECTED`, `IDLE`, `EXPIRED`, `EXCEPTION`, `CTXSW_ABLE`, `CTXSW_READY`, `PREEMPTED`, and `PREEMPT_DISABLE`.
- Doorbells and diagnostics:
  `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, and `DOORBELL_OFFSET`.
  These cover doorbell enable/captured state, write-pointer update failure/pending state, logged backend error/data, outstanding read/write watermarks, and the queue doorbell aperture offset.
- AQL and mid-command state:
  `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.
  These fields describe AQL packet sizing/step and a saved or inspected in-flight command payload with `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.

The masks are consistent across RLC5, RLC6, and RLC7, and match the earlier RLC0-RLC4 pattern in the same header. Line 2530 starts after the first several `SDMA_RLC4_RB_CNTL` shift/mask definitions, so the chunk contains only the final `RB_PRIV` and `RB_VMID` masks for that register before continuing with the rest of RLC4.

## Control Flow

There is no runtime control flow in this header. The operational flow appears in consumers:

1. SDMA/KFD code includes `sdma_4_4_2_offset.h` and this mask header.
2. It computes an SDMA engine or RLC queue register address using the offset constants.
3. It reads or writes the register with `RREG32()` / `WREG32()` or SDMA instance wrappers.
4. It uses the shift/mask constants through field helpers, or directly tests masks, to enable queues, poll idle state, configure doorbells, dump state, or restore MQD contents.

`amdgpu_amdkfd_gc_9_4_3.c` demonstrates the intended RLC queue model. It computes a per-queue RLC base from `regSDMA_RLC0_RB_CNTL` and the stride to `regSDMA_RLC1_RB_CNTL`, then addresses any queue by adding `queue_id * stride`. That means the repeated RLC4-RLC7 definitions in this chunk must remain layout-compatible with RLC0/RLC1 because queue code can address later queues using the same register layout and field semantics.

## State and Persistence Behavior

The constants describe hardware state, not stored software state. The relevant persistent or recoverable state lives in SDMA hardware registers and MQD snapshots:

- Ring base, read/write pointers, writeback addresses, doorbell offset, and `RB_CNTL` persist in hardware while the queue is active.
- KFD queue load writes an MQD's SDMA RLC fields into the hardware queue registers, disables `RB_ENABLE` while waiting for `CONTEXT_STATUS.IDLE`, programs doorbell/pointers/base/writeback addresses, then enables the ring.
- Queue destroy disables the ring, waits for `CONTEXT_STATUS.IDLE`, disables the doorbell, and records the current read pointer back into the MQD-like software structure.
- Queue dump reads contiguous RLC register ranges, including the mid-command data/control area described in this chunk, so user/debug tooling can inspect live or suspended SDMA queue state.

The header itself has no allocation, locking, I/O, or persistence code. Correctness depends on the constants matching the hardware register layout exactly.

## Dependencies and Integration Points

- Paired offset header: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_2_offset.h` provides `regSDMA_RLC4_*` through `regSDMA_RLC7_*` addresses that correspond to these field masks.
- Main SDMA implementation: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c` includes this header and the offset header for SDMA 4.4.2/4.4.4/4.4.5 register programming and register dumps.
- KFD GC 9.4.3 integration: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gc_9_4_3.c` includes the same headers and uses RLC register offsets/masks to load, destroy, inspect, and report SDMA HQD state.
- Common AMDGPU register helpers: `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on the naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Any rename or inconsistent field name breaks these macro expansions.
- Hardware-visible ABI: firmware, kernel SDMA setup, KFD MQD handling, doorbell routing, and debug register dumps all assume these definitions match SDMA 4.4.2 silicon.

## Risks

- A single incorrect mask or shift can silently program the wrong bit in a memory-mapped hardware register, causing queue hangs, missed doorbells, invalid VMID/privilege selection, broken writeback, or failed preemption.
- The chunk is repetitive and generated-style; manual edits are high risk because RLC4-RLC7 must remain stride-compatible and field-compatible with RLC0-RLC3.
- Alignment masks such as `*_ADDR_MASK` encode hardware alignment requirements. Incorrect low-bit masks can point hardware at invalid ring, IB, writeback, or doorbell memory.
- `CONTEXT_STATUS` masks are used in timeout loops. Wrong `IDLE` or `SELECTED` values can create false readiness, timeout failures, or incorrect active-doorbell reporting.
- Doorbell masks and offsets are security-sensitive in multi-process/KFD use because they control how user queues signal hardware.
- This file is included in kernel C translation units; malformed macro names, missing `L` suffixes where expected, or guard damage can cause broad build failures in AMDGPU code.

## Test Signals

- Kernel build coverage for AMDGPU with SDMA 4.4.2/GC 9.4.3 enabled validates macro names and include integration.
- Static compile checks around `REG_SET_FIELD()` / `REG_GET_FIELD()` users catch missing or renamed field macros.
- Runtime SDMA ring tests should confirm queue initialization, ring pointer movement, writeback, doorbell signaling, and IB execution.
- KFD SDMA queue tests should cover HQD load/destroy/dump, doorbell offset reporting, MQD restoration, and multi-queue operation using queue ids that map beyond RLC0/RLC1.
- GPU reset, suspend/resume, and preemption tests are useful signals because this chunk includes context status, preempt, and mid-command state fields.
- Debug register dump comparison against expected SDMA 4.4.2 register layouts can catch offset/mask drift for RLC4-RLC7.
