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
