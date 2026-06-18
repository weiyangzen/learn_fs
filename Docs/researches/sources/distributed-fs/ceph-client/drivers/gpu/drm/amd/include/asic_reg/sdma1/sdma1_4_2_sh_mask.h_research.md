# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003384`: lines 1-2568, `Docs/researches/chunks/subset-b-003384_research.md`
- `subset-b-003385`: lines 2569-2948, `Docs/researches/chunks/subset-b-003385_research.md`

## Chunk Research

### subset-b-003384: lines 1-2568

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_sh_mask.h lines 1-2568

## Scope

This chunk covers the beginning of the generated SDMA1 v4.2 shift/mask header. It starts at the AMD license and include guard, then defines C preprocessor constants for bit shifts and masks in the `sdma1_sdma1dec` address block. The covered range includes:

- Public SDMA1 engine registers: microcode access, VM context controls, SR-IOV function/reset controls, context/public register type bitmaps, MMHUB unit selection, power/clock/control/chicken bits, address configuration, status, burst, F32, freeze, quantum, EDC, atomic, UTCL1, relax ordering, physical address, error, performance counter, GPU IOV, ULV, and EA debug fields.
- Complete queue-context field layouts for `SDMA1_GFX_*` and `SDMA1_PAGE_*`.
- Complete repeated queue-context field layouts for `SDMA1_RLC0_*` through `SDMA1_RLC4_*`.
- Most of `SDMA1_RLC5_*`, ending at `SDMA1_RLC5_MIDCMD_CNTL__COPY_MODE_MASK` on line 2568.

The chunk ends before `SDMA1_RLC5_MIDCMD_CNTL__SPLIT_STATE_MASK`, `SDMA1_RLC5_MIDCMD_CNTL__ALLOW_PREEMPT_MASK`, all `SDMA1_RLC6_*` and `SDMA1_RLC7_*` definitions, and the final include guard terminator. Those remaining definitions belong to later chunk coverage and should be merged before producing a final per-file conclusion.

The file is generated hardware metadata. It defines constants only: no functions, structs, variables, allocation, locking, loops, conditionals, or executable control flow appear in this covered range.

## Purpose

`sdma1_4_2_sh_mask.h` provides the field-level contract for SDMA1 registers on SDMA IP version 4.2-era AMD GPUs. Driver code combines these `__SHIFT` and `_MASK` macros with register offsets from `sdma1_4_2_offset.h` and SOC15/MMIO helpers to read, write, or patch individual SDMA1 hardware fields.

The matching consumer in this tree is `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, which includes:

- `sdma0/sdma0_4_2_offset.h`
- `sdma0/sdma0_4_2_sh_mask.h`
- `sdma1/sdma1_4_2_offset.h`
- `sdma1/sdma1_4_2_sh_mask.h`

That driver also defines SDMA1 golden settings for SDMA 4.2 registers such as `mmSDMA1_CHICKEN_BITS`, `mmSDMA1_CLK_CTRL`, `mmSDMA1_GB_ADDR_CONFIG`, `mmSDMA1_GFX_RB_RPTR_ADDR_LO`, `mmSDMA1_GFX_RB_WPTR_POLL_CNTL`, `mmSDMA1_PAGE_RB_*`, `mmSDMA1_RLC0_*` through `mmSDMA1_RLC7_*`, `mmSDMA1_UTCL1_PAGE`, and `mmSDMA1_UTCL1_TIMEOUT`. The masks in this header are the field definitions that make those register values interpretable and safe to update in field-aware code.

## Important Macro Families

### Access, VM, and Virtualization Registers

The first register definitions describe SDMA1 access windows and virtualization state:

- `SDMA1_UCODE_ADDR` and `SDMA1_UCODE_DATA` expose microcode address/data fields.
- `SDMA1_VM_CNTL`, `SDMA1_VM_CTX_LO`, `SDMA1_VM_CTX_HI`, and `SDMA1_VM_CTX_CNTL` define VM command, address, privilege, and VMID fields.
- `SDMA1_ACTIVE_FCN_ID`, `SDMA1_VIRT_RESET_REQ`, and `SDMA1_VF_ENABLE` define VFID/VF/PF and virtual-function enable/reset fields for SR-IOV or virtualized operation.

Address fields encode alignment in their shifts and masks. For example, `VM_CTX_LO__ADDR` starts at bit 2, while full-width high-address fields are often shifted by zero.

### Context and Public Register Type Bitmaps

`SDMA1_CONTEXT_REG_TYPE0` through `TYPE3` and `SDMA1_PUB_REG_TYPE0` through `TYPE3` are bitmaps. Each bit names another SDMA1 register or a group of registers. These fields allow hardware, firmware, or context-save logic to classify which registers belong to a context/public register set.

The context bitmap section covers the GFX context register set, including ring control/base/pointers, IB control/state, skip/context/doorbell fields, CSA addresses, preemption, AQL, minor pointer update, and mid-command data/control fields. The public bitmap section covers engine-global registers such as microcode, VM, active function, power, clock, control, status, UTCL1, atomics, perf counters, and IOV logging.

These bitmap macros are easy to confuse with ordinary control fields because they share the same `__SHIFT`/`_MASK` form. Their values represent presence/classification bits, not the runtime contents of the named target registers.

### Engine Control, Status, and Diagnostics

The public SDMA1 engine fields include:

- Power and clock: `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, and `SDMA1_POWER_CNTL_IDLE`.
- Engine control: `SDMA1_CNTL` for trap, UTC L1, semaphore wait interrupt, data/fence swap, mid-command preemption/world-switch, auto context switch, and interrupt enables.
- Tuning and memory layout: `SDMA1_CHICKEN_BITS`, `SDMA1_CHICKEN_BITS_2`, `SDMA1_GB_ADDR_CONFIG`, `SDMA1_GB_ADDR_CONFIG_READ`, `SDMA1_RD_BURST_CNTL`, `SDMA1_HBM_PAGE_CONFIG`, `SDMA1_BA_THRESHOLD`, `SDMA1_CRD_CNTL`, and `SDMA1_RELAX_ORDERING_LUT`.
- Status and debug: `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, `SDMA1_STATUS3_REG`, `SDMA1_ERROR_LOG`, `SDMA1_F32_COUNTER`, `SDMA1_PUB_DUMMY_REG*`, `SDMA1_EA_DBIT_ADDR_DATA`, and `SDMA1_EA_DBIT_ADDR_INDEX`.
- RAS/error correction: `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, and `SDMA1_EDC_COUNTER_CLEAR`.
- Atomics and pre-operation data: `SDMA1_ATOMIC_CNTL`, `SDMA1_ATOMIC_PREOP_LO`, and `SDMA1_ATOMIC_PREOP_HI`.
- Performance counters: `SDMA1_PERFMON_CNTL`, `SDMA1_PERFCOUNTER0_RESULT`, `SDMA1_PERFCOUNTER1_RESULT`, and `SDMA1_PERFCOUNTER_TAG_DELAY_RANGE`.

Several fields are single-bit enables or status bits, while others are packed numeric ranges, such as delay values, watermarks, burst sizes, VMIDs, status vectors, queue IDs, and counter selectors.

### UTCL1 and Address Translation Fields

The UTCL1 definitions describe SDMA1's translation/cache interaction:

- `SDMA1_UTCL1_CNTL` controls redo behavior, delays, credits, and virtual-address watermarks.
- `SDMA1_UTCL1_WATERMK` defines request, page, invalidate, and XNACK watermarks.
- `SDMA1_UTCL1_RD_STATUS` and `SDMA1_UTCL1_WR_STATUS` expose FIFO empty/full states, page fault/null flags, L2 idle, stall/routing/vector, merge, and polling state.
- `SDMA1_UTCL1_INV0`, `INV1`, and `INV2` define invalidation behavior, VMID vectors, invalidate address high/low, flush type, timeout behavior, and non-flush VMID vectors.
- `SDMA1_UTCL1_RD_XNACK*` and `WR_XNACK*` define XNACK address, VMID, vector, and `IS_XNACK` fields.
- `SDMA1_UTCL1_TIMEOUT` and `SDMA1_UTCL1_PAGE` define XNACK limits and page request attributes.

These fields integrate SDMA command execution with GPU virtual memory, page migration, fault handling, retry/XNACK behavior, and VM invalidation paths. Incorrect bit definitions here can produce failures that look like memory-management bugs rather than SDMA register bugs.

### Queue Context Layouts

The chunk contains complete context layouts for `GFX`, `PAGE`, `RLC0`, `RLC1`, `RLC2`, `RLC3`, and `RLC4`, plus most of `RLC5`. These context families are highly regular. Each complete family defines fields for:

- Ring setup: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Indirect buffers: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Context scheduling/state: `SKIP_CNTL`, `CONTEXT_STATUS`, `STATUS`, `WATERMARK`, `MINOR_PTR_UPDATE`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `PREEMPT`, and `DUMMY_REG`.
- Doorbell integration: `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- AQL and mid-command state: `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and `MIDCMD_CNTL`.

The field meanings are consistent across the repeated queue families. For example, `RB_CNTL` fields include `RB_ENABLE`, `RB_SIZE`, swap enable, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID`; `IB_CNTL` fields include `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`; `CONTEXT_STATUS` fields include selected/idle/expired/exception/context-switch/preempt status; and `MIDCMD_CNTL` includes data-valid, copy-mode, split-state, and allow-preempt fields.

The range ends mid-family: `RLC5` has its mid-command data fields and the first two `MIDCMD_CNTL` masks in this chunk, but the last two masks are just outside the chunk.

## Control Flow and State

There is no runtime control flow in this header. Its behavioral effect is indirect:

1. AMDGPU code selects a register offset from `sdma1_4_2_offset.h`, usually through `mmSDMA1_*` or SOC15 register helpers.
2. Code reads or writes the register through MMIO helpers such as `RREG32`, `WREG32`, `RREG32_SDMA`, `WREG32_SDMA`, or SOC15 golden-setting machinery.
3. Field-aware code uses these shift/mask macros, directly or through helper macros, to pack or extract individual fields.
4. Hardware changes SDMA behavior, reports state, or records diagnostics based on the programmed field values.

The state represented here is hardware state, not C-owned persistent state. Important state surfaces include microcode loading windows, VM context selection, VF/PF visibility, ring-buffer base and pointer state, doorbell configuration and captured doorbells, IB base/size/offset state, context switch/preemption state, CSA addresses, mid-command resume state, UTCL1 translation/fault/XNACK state, atomics, performance counters, and RAS/EDC counters.

No disk persistence, file I/O, heap state, reference counting, or locking is performed by this header. Persistence exists in hardware registers across normal operation and until reset, power management transitions, firmware reload, or driver reinitialization changes them.

## Dependencies and Integration Points

Primary dependencies are compile-time hardware-contract dependencies:

- `sdma1_4_2_offset.h` must provide matching register offsets for these SDMA1 field definitions.
- `sdma_v4_0.c` includes this header and applies SDMA1 4.2 golden settings for power, clock, address config, ring pointer writeback, write-pointer polling, RLC queues, and UTCL1 timeout/page behavior.
- SOC15 register macros and AMDGPU MMIO helpers consume the register offsets, while field helpers consume these `__SHIFT` and `_MASK` constants.
- Firmware loading, SDMA ring setup, paging queues, RLC queues, doorbells, indirect buffers, preemption/context save, virtual memory invalidation, XNACK/fault handling, RAS/EDC collection, GPU reset, and performance-counter paths depend on the field definitions matching the ASIC specification.
- Similar-looking headers exist for SDMA0 and for SDMA 4.2.2 instances. The SDMA1 4.2 field names and masks should not be mixed with SDMA0, SDMA2+, or 4.2.2 headers unless the driver's IP-version selection explicitly says the register layout is shared.

The generated naming convention is part of the integration contract. Driver code and generated tables rely on names such as `SDMA1_GFX_RB_WPTR_POLL_CNTL__FREQUENCY_MASK` or `SDMA1_RLC4_CONTEXT_STATUS__PREEMPTED_MASK` being stable and matching the associated `mmSDMA1_*` register names.

## Risks

- A wrong mask or shift can silently program the wrong hardware bits. Since the macros are constants, this usually compiles cleanly and fails only at runtime on matching ASICs.
- Register families are repetitive. Copy-generation errors across `GFX`, `PAGE`, and `RLCn` queues could affect only one queue class while leaving nearby queues functional.
- Bitmap registers such as `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` have fields that name other registers. Treating those fields as the named target registers' own fields would produce incorrect interpretation.
- Address fields encode alignment in the shift/mask pair. Losing low-bit alignment for ring bases, IB bases, CSA addresses, writeback addresses, or VM context addresses can point hardware at the wrong memory.
- The UTCL1/XNACK/page fields sit on the boundary between SDMA and GPU VM behavior. Bad values can surface as page faults, retry storms, invalidation hangs, or memory corruption symptoms.
- Virtualization fields such as VFID/VF/PF, VF enable, reset request, and GPU IOV violation logging are security-sensitive. Incorrect interpretation can affect isolation diagnostics or reset handling.
- The chunk boundary is inside `RLC5_MIDCMD_CNTL`; this document must not be used as evidence that the `RLC5` family is incomplete in the source file as a whole.
- SDMA 4.2 and 4.2.2 headers are adjacent in the tree. Accidentally mixing these field definitions with 4.2.2 offsets or with SDMA2+ instance headers risks subtle register-layout mismatches.

## Test Signals

Useful validation signals are mostly build-time, static, and hardware-integration oriented:

- Kernel build coverage for `drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c` with the SDMA1 4.2 offset and shift/mask headers included.
- Static generated-header checks that every field has a `__SHIFT` and `_MASK` pair, except where a chunk boundary deliberately splits a pair such as `SDMA1_RLC5_MIDCMD_CNTL` here.
- Cross-header checks that every `mmSDMA1_*` register in `sdma1_4_2_offset.h` has the expected field definitions in this header, and that SDMA0/SDMA1 corresponding fields intentionally match or intentionally differ.
- Golden-setting smoke checks in `sdma_v4_0.c`, especially for `CHICKEN_BITS`, `CLK_CTRL`, `GB_ADDR_CONFIG`, `GFX/PAGE/RLC*_RB_RPTR_ADDR_LO`, `GFX/PAGE/RLC*_RB_WPTR_POLL_CNTL`, `RD_BURST_CNTL`, `UTCL1_PAGE`, and `UTCL1_TIMEOUT`.
- Runtime boot/probe on SDMA 4.2 hardware, confirming firmware load, SDMA engine bring-up, GFX/page/RLC ring initialization, doorbell updates, queue submission, and idle detection.
- Suspend/resume, GPU reset, and preemption tests that exercise `FREEZE`, `CONTEXT_STATUS`, `PREEMPT`, CSA address, and mid-command state fields.
- VM stress tests that exercise SDMA paging, UTCL1 invalidation, XNACK, page fault/null, and timeout fields.
- RAS and diagnostics tests that read or clear EDC counters and inspect status/error/performance-counter registers without invalid values or hangs.

### subset-b-003385: lines 2569-2948

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_sh_mask.h lines 2569-2948

## Scope

This chunk is the tail of the generated AMD SDMA1 4.2 shift/mask header. It starts with the final mask lines for `SDMA1_RLC5_MIDCMD_CNTL`, then defines the complete bitfield geometry for SDMA1 RLC context queues 6 and 7, and ends with the file's closing include-guard `#endif`.

The file is C preprocessor metadata only. It contains no functions, structs, enums, static storage, allocation, locking, branches, loops, MMIO calls, or direct control flow. Its public surface is the generated `*_SHIFT` and `*_MASK` macro namespace used by AMDGPU register helpers and register programming code.

Although the repository path is under a `ceph-client` source mirror, this chunk documents AMD GPU SDMA hardware register fields. It does not implement distributed filesystem behavior.

## Purpose

`sdma1_4_2_sh_mask.h` supplies symbolic bit positions and masks for fields inside SDMA1 4.2 registers. It is paired with SDMA1 4.2 offset headers such as `sdma1_4_2_offset.h` and nearby revision headers, which provide the register addresses. Consumers combine the address macros with these shift/mask macros through AMDGPU helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` or through hand-built read/modify/write sequences.

The covered range describes queue-context register fields for the high RLC contexts on SDMA engine 1:

- The boundary lines finish `SDMA1_RLC5_MIDCMD_CNTL`, with masks for `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`.
- `SDMA1_RLC6_*` defines the full RLC6 queue-context bit layout.
- `SDMA1_RLC7_*` defines the full RLC7 queue-context bit layout.

RLC6 and RLC7 are structurally identical in this header. They expose ring-buffer configuration, read/write pointer handling, write-pointer polling, read-pointer writeback, indirect-buffer execution state, context status, doorbell state, queue status, watermarks, context-save addresses, preemption control, AQL controls, minor-pointer update, and mid-command snapshot/control fields.

## Important Macro Families

The exported macros follow a strict generated naming convention:

- `SDMA1_RLC[6|7]_RB_CNTL__*` describes ring-buffer control fields. It includes `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, read-pointer writeback enable/swap/timer fields, `RB_PRIV`, and `RB_VMID`.
- `SDMA1_RLC[6|7]_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` are full-width or high-address/offset fields for ring storage and queue pointers.
- `SDMA1_RLC[6|7]_RB_WPTR_POLL_CNTL` describes polling enable, swap enable, 32-bit polling mode, polling frequency, and idle poll count.
- `SDMA1_RLC[6|7]_RB_RPTR_ADDR_HI/LO` and `RB_WPTR_POLL_ADDR_HI/LO` describe GPU/CPU-visible memory addresses used for read-pointer writeback and write-pointer polling. The low address fields are 4-byte aligned through `ADDR__SHIFT = 0x2` and `ADDR_MASK = 0xFFFFFFFC`; `RB_RPTR_ADDR_LO` also exposes `RPTR_WB_IDLE`.
- `SDMA1_RLC[6|7]_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN` describe indirect-buffer enablement, address, progress, and remaining-size state.
- `SDMA1_RLC[6|7]_CONTEXT_STATUS` exposes scheduler/context-switch state: selected, idle, expired, exception code bits, context-switch ability/readiness, preempted state, and preempt-disable state.
- `SDMA1_RLC[6|7]_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET` define doorbell enable/captured status, logged data/error, and the aligned doorbell aperture offset.
- `SDMA1_RLC[6|7]_STATUS` reports write-pointer update failure count and pending update state.
- `SDMA1_RLC[6|7]_WATERMARK` packs read and write outstanding-watermark fields.
- `SDMA1_RLC[6|7]_CSA_ADDR_LO/HI` defines context-save area address fields.
- `SDMA1_RLC[6|7]_PREEMPT` exposes the `IB_PREEMPT` command bit.
- `SDMA1_RLC[6|7]_RB_AQL_CNTL` defines AQL enablement, packet size, and packet step fields for AQL/HSA-style queues.
- `SDMA1_RLC[6|7]_MIDCMD_DATA0` through `MIDCMD_DATA8` are full 32-bit mid-command data words, with `MIDCMD_CNTL` indicating validity, copy mode, split state, and whether preemption is allowed.

There are no callable APIs or C types in this chunk. The macros themselves are the interface.

## Control Flow and Data Flow

The header has no local runtime control flow. The effective flow occurs in AMDGPU SDMA consumers:

1. SDMA code selects an SDMA1 RLC6 or RLC7 register address from a matching offset header, such as `mmSDMA1_RLC6_RB_WPTR_POLL_CNTL` or `mmSDMA1_RLC7_RB_RPTR_ADDR_LO`.
2. Driver code reads, writes, or read/modify/writes the register through SOC15/AMDGPU MMIO helpers.
3. Field helper macros use the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions from this chunk to isolate or compose specific fields.
4. Hardware interprets the value as queue-context state for ring execution, pointer polling/writeback, doorbell notification, indirect-buffer processing, context switching, preemption, AQL packet handling, or mid-command resume.

The surrounding AMDGPU SDMA initialization code includes this shift/mask header in `amdgpu/sdma_v4_0.c`. The same RLC6/RLC7 register names appear in golden-setting tables, where `mmSDMA1_RLC6_RB_RPTR_ADDR_LO`, `mmSDMA1_RLC6_RB_WPTR_POLL_CNTL`, `mmSDMA1_RLC7_RB_RPTR_ADDR_LO`, and `mmSDMA1_RLC7_RB_WPTR_POLL_CNTL` receive masked initialization values. SDMA v5 code has analogous golden settings for the same queue-context concepts in later generated headers, so these field layouts are part of a recurring AMDGPU SDMA register contract.

## State and Persistence Behavior

This header stores no software state and persists nothing to disk. It describes hardware-owned register state:

- Ring state persists queue enablement, queue size, base addresses, read/write pointers, privilege and VMID selection, byte-swap behavior, and read-pointer writeback policy until reset or reprogramming.
- Polling state persists whether hardware polls a write-pointer memory location, how frequently it polls, how it swaps data, and how it behaves while idle.
- Doorbell state persists enablement, offset selection, captured-doorbell indication, and logged doorbell data/error status.
- Indirect-buffer state persists IB enablement, base, size, read pointer, current offset, and remaining sub-IB size while work executes.
- Context and scheduling state is live hardware status: selected, idle, expired, exception bits, context-switch readiness, preempted, and preempt-disabled conditions.
- Context-save and mid-command state persists addresses and snapshot words used by preemption/context-switch machinery to resume partially executed commands.
- AQL state persists whether AQL mode is active and how packets are sized and stepped.
- Watermark and status fields reflect live outstanding read/write pressure and write-pointer update failures or pending updates.

Persistence duration is controlled by the SDMA engine's reset, power-management, context-switch, and firmware rules. The header does not encode access types, reset values, sticky bits, write-one-to-clear behavior, or sequencing requirements.

## Dependencies and Integration Points

Direct dependencies are generated-header conventions and the AMDGPU register-access layer:

- Matching SDMA1 4.2 offset headers provide concrete `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*` register addresses. In `sdma1_4_2_offset.h`, RLC6 starts at `mmSDMA1_RLC6_RB_CNTL = 0x0380` and RLC7 starts at `mmSDMA1_RLC7_RB_CNTL = 0x03e0`; in `sdma1_4_2_2_offset.h`, the same field layout maps onto a slightly different address schedule.
- AMDGPU helper macros depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming scheme.
- `amdgpu/sdma_v4_0.c` includes this header and uses the related address macros in golden-setting arrays for SDMA1 RLC6/RLC7 pointer writeback and write-pointer polling setup.
- Register default headers for adjacent IP versions provide reset/default values, but this shift/mask header supplies only field geometry.

The registers described here integrate with SDMA queue setup, GPU scheduler queue context management, VMID/privilege selection, doorbell routing, memory-backed pointer writeback/polling, indirect-buffer dispatch, preemption/context save/restore, AQL queue operation, register dumps, diagnostics, and hardware bring-up validation.

## Risks and Edge Cases

- The chunk begins in the middle of the RLC5 mid-command control register. Any whole-file analysis must merge with the previous chunk before making complete RLC5 statements.
- The macros are untyped constants. A stale or incorrect mask can compile cleanly while causing writes to the wrong hardware bits.
- RLC6 and RLC7 layouts are nearly identical, making copy/paste or generator errors hard to spot. A wrong RLC index can silently target a different queue context.
- Address fields are split across low/high registers and often require alignment. Low address fields with `ADDR__SHIFT = 0x2` must not be populated with unaligned addresses.
- Ring, polling, read-pointer writeback, and doorbell fields connect the SDMA engine to memory and doorbell apertures. Bad programming can make hardware fetch stale queues, write back to the wrong memory, or wake the wrong context.
- `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and `MIDCMD_*` are live hardware-observed or hardware-updated state. Tests and diagnostics should not assume stable values without quiescing or polling rules.
- Preemption and mid-command fields are scheduler-sensitive. Writing them outside the expected preemption/context-switch sequence can corrupt resume state or leave queues stalled.
- VMID and privilege fields in `RB_CNTL` affect memory translation and isolation. Incorrect values can produce GPUVM faults or route work under the wrong address space.
- This field layout is SDMA1 4.2-specific. Nearby generations such as SDMA 4.2.2 and GC 10.x have related but not always identical generated headers; mixing masks and offsets across IP versions is unsafe.

## Test and Validation Signals

Useful validation is mainly generated-header and hardware integration coverage:

- Compile AMDGPU SDMA v4.0 paths that include `sdma1/sdma1_4_2_sh_mask.h` with the matching offset header; unresolved or renamed macros should fail at build time.
- Static generation checks should confirm every RLC6/RLC7 field has a matching `_SHIFT` and `_MASK` pair and that full-width fields use `0xFFFFFFFFL`.
- Cross-check this chunk against the authoritative SDMA1 4.2 register database, especially packed fields in `RB_CNTL`, `RB_WPTR_POLL_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `WATERMARK`, `RB_AQL_CNTL`, and `MIDCMD_CNTL`.
- Validate consistency with offset headers: RLC6/RLC7 register names in the offset header should all have field definitions here, and the RLC6/RLC7 context stride should match hardware documentation.
- Boot/probe on matching SDMA 4.2 hardware should apply golden settings for RLC6/RLC7 pointer writeback and write-pointer polling without hangs or register-write faults.
- Queue submission tests should verify ring pointer movement, read-pointer writeback, write-pointer polling, and doorbell notification for high RLC contexts if those queues are exposed by the ASIC/driver configuration.
- Preemption/context-switch tests should exercise `PREEMPT`, `CONTEXT_STATUS`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` state before and after forced SDMA IB preemption.
- Register dump decoders should use these masks to decode live RLC6/RLC7 state and compare decoded values against expected queue configuration, VMID, doorbell offset, AQL mode, and idle/preempt status.

## Chunk Boundary Notes

This is the final chunk of `sdma1_4_2_sh_mask.h`. Merge/reconciliation should combine the first few lines with the prior RLC5 chunk, then treat RLC6 and RLC7 as complete context-register field blocks and retain the closing include-guard note.
