# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003360`: lines 1-2437, `Docs/researches/chunks/subset-b-003360_research.md`
- `subset-b-003361`: lines 2438-4848, `Docs/researches/chunks/subset-b-003361_research.md`
- `subset-b-003362`: lines 4849-5224, `Docs/researches/chunks/subset-b-003362_research.md`

## Chunk Research

### subset-b-003360: lines 1-2437

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h lines 1-2437

## Scope

This chunk covers the beginning of the generated SDMA 4.4.0 register-offset header. It starts at the license and include guard, then defines register address-offset macros for:

- Complete `sdma0_sdma0dec` address block, base address comment `0x4980`, covering `regSDMA0_*` offsets from `regSDMA0_UCODE_ADDR` through `regSDMA0_RLC7_MIDCMD_CNTL`.
- Complete `sdma0_sdma1dec` address block, base address comment `0x6180`, covering `regSDMA1_*` offsets from `regSDMA1_UCODE_ADDR` through `regSDMA1_RLC7_MIDCMD_CNTL`.
- The start of `sdma0_sdma2dec`, base address comment `0x78000`, covering `regSDMA2_*` offsets from `regSDMA2_UCODE_ADDR` through `regSDMA2_PAGE_MIDCMD_DATA9`. The chunk ends mid-register-family before the matching `BASE_IDX` line for `regSDMA2_PAGE_MIDCMD_DATA9` and before the rest of SDMA2's PAGE/RLC context offsets.

The file is generated hardware metadata. It defines C preprocessor constants only: no functions, structs, variables, memory allocation, locks, loops, branches, or executable control flow appear in the covered range.

## Purpose

`sdma_4_4_0_offset.h` is the address map used by the AMDGPU SDMA v4.4 driver code for ASIC-family-specific register access. Each register appears as a pair:

- `reg<NAME>`: the register offset used by AMDGPU/SOC15 register helpers.
- `reg<NAME>_BASE_IDX`: the base-index selector for the register block. In this chunk all base-index values are `0`.

The offset header is paired with `sdma_4_4_0_sh_mask.h`, which provides bit shifts and masks for fields inside the same registers. Consumers combine the offset macros with SOC15 helpers such as `SOC15_REG_ENTRY`, `SOC15_REG_OFFSET`, `RREG32`, `WREG32`, and AMDGPU field helpers. In this source tree, `drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes both this offset header and the matching shift/mask header.

## Important Macro Families

### SDMA Instance-Level Registers

Each covered SDMA instance starts with common engine-management registers:

- Microcode loading and identification: `UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`, `ID`, and `VERSION`.
- Engine control and clocks: `POWER_CNTL`, `POWER_CNTL_IDLE`, `CLK_CTRL`, `CLK_STATUS`, `CNTL`, `FREEZE`, `PROGRAM`, and `CHICKEN_BITS` / `CHICKEN_BITS_2`.
- Addressing and memory behavior: `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `PHYSICAL_ADDR_LO`, `PHYSICAL_ADDR_HI`, `HBM_PAGE_CONFIG`, `RD_BURST_CNTL`, `RELAX_ORDERING_LUT`, and `BA_THRESHOLD`.
- Interrupt/error/status visibility: `STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, `STATUS3_REG`, `STATUS4_REG`, `ERROR_LOG`, `RAS_STATUS`, `EDC_COUNTER`, `EDC_COUNTER2`, and `CC_SDMA*_EDC_CONFIG`.
- Virtualization and queue grouping controls: `VF_ENABLE` and `CONTEXT_GROUP_BOUNDARY`.
- Translation/cache and atomic support: `UTCL1_*`, `ATOMIC_CNTL`, `ATOMIC_PREOP_LO`, and `ATOMIC_PREOP_HI`.
- Performance and debug facilities: `PERFCNT_*`, `F32_*`, `SCRATCH_RAM_*`, `PUB_DUMMY_REG*`, `EA_DBIT_ADDR_*`, `CRD_CNTL`, `ULV_CNTL`, and `CE_CTRL`.

For SDMA0 only, this chunk also defines shared-looking power-gating FSM macros without an instance number: `regSDMA_POWER_GATING`, `regSDMA_PGFSM_CONFIG`, `regSDMA_PGFSM_WRITE`, and `regSDMA_PGFSM_READ`. These sit in the SDMA0 block near offsets `0x002e` through `0x0031` and are not repeated in the SDMA1 section.

### Queue Context Register Sets

The chunk defines a regular context layout for several queue classes:

- `GFX_*`: graphics SDMA ring and indirect-buffer context.
- `PAGE_*`: paging SDMA ring and indirect-buffer context.
- `RLC0_*` through `RLC7_*`: eight RLC-context register sets for each complete SDMA0 and SDMA1 block.

Each complete context family follows the same shape:

- Ring-buffer controls and base pointers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, and `RB_AQL_CNTL`.
- Polling and memory-backed read-pointer/write-pointer support: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, and `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer registers: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Scheduling/context state: `SKIP_CNTL`, `CONTEXT_STATUS`, `STATUS`, `WATERMARK`, `MINOR_PTR_UPDATE`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, `PREEMPT`, and `DUMMY_REG`.
- Doorbell integration: `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- Mid-command capture/resume state: `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.

This regular layout lets driver code program ring buffers, doorbells, IB execution, preemption state, and context save/restore state with a consistent naming convention across SDMA instances and queue classes.

### Offset Patterns

SDMA0's complete block begins at offset `0x0000`; SDMA1's complete block begins at `0x0600`. Within each complete block, the same queue families have the same relative positions:

- `GFX_RB_CNTL`: SDMA0 `0x0080`, SDMA1 `0x0680`.
- `PAGE_RB_CNTL`: SDMA0 `0x00d8`, SDMA1 `0x06d8`.
- `RLC0_RB_CNTL`: SDMA0 `0x0130`, SDMA1 `0x0730`.
- `RLC7_MIDCMD_CNTL`: SDMA0 `0x03e3`, SDMA1 `0x09e3`.

The partial SDMA2 block is not a simple `+0x600` continuation. It starts at `regSDMA2_UCODE_ADDR = 0x1cda0`, with `GFX_RB_CNTL = 0x1ce20` and `PAGE_RB_CNTL = 0x1ce78`. The SDMA v4.4 driver compensates for this by calculating per-instance offsets from the SDMA0 offset namespace and instance constants such as `SDMA1_REG_OFFSET = 0x600` and `SDMA2_REG_OFFSET = 0x1cda0`.

## Control Flow and State

There is no runtime control flow in this header. The control-flow effect is indirect: driver code chooses a register macro, combines it with an instance/base calculation, reads or writes MMIO, and then interprets fields through the matching shift/mask header.

The registers described by these macros represent hardware state, not software-owned persistent state. Important hardware state surfaces include:

- Microcode address/data windows used during SDMA firmware loading.
- Ring-buffer read/write pointers and polling addresses for memory-backed queue progress.
- Doorbell registers used by CPU or user-mode queues to notify SDMA of new work.
- Indirect-buffer base/size/offset state for command execution.
- Context save area addresses and mid-command data used for preemption or context switching.
- Error and RAS counters used for diagnostics.
- UTCL1 translation and XNACK status used by GPU memory-management paths.
- Performance counters and scratch/debug registers.

No file, disk, or repository persistence is performed by this header. Persistence is in hardware registers and firmware-visible state across engine operation, reset, suspend/resume, and RAS collection paths.

## Dependencies and Integration Points

Primary dependencies are compile-time and hardware-contract dependencies:

- The matching bitfield header `sdma_4_4_0_sh_mask.h` must describe the same registers and fields.
- `sdma_v4_4.c` includes this header and uses `regSDMA0_EDC_COUNTER` / `regSDMA0_EDC_COUNTER2` with per-instance offset calculation for RAS error reporting.
- SOC15/AMDGPU register helpers consume the `reg*` and `_BASE_IDX` constants to construct MMIO addresses.
- Firmware loading, queue programming, preemption, doorbell, page-queue, RLC, RAS, and performance-counter code depend on these numeric offsets matching the ASIC's SDMA 4.4 register specification.
- This source tree also contains related SDMA 4.4 headers such as `sdma_4_4_2_offset.h`; those represent a different register map and should not be mixed with this file unless driver IP-version selection does so explicitly.

Because the full header continues beyond this chunk, the SDMA2 analysis here is intentionally partial. Merge/reconciliation should combine this chunk with later chunks before producing a per-file conclusion about SDMA2, SDMA3, SDMA4, and the final include guard.

## Risks

- Incorrect numeric offsets can make the kernel read or write the wrong MMIO register, which can break queue setup, firmware loading, power management, preemption, RAS reporting, or GPU reset.
- Register names are very regular, so copy-generation errors are easy to miss. A single wrong suffix, skipped register, or mismatched `_BASE_IDX` can compile cleanly but fail only on affected hardware paths.
- SDMA0 includes shared `regSDMA_*` power-gating FSM macros that are not duplicated under `regSDMA1_*`; consumers must know whether those registers are shared or instance-local before applying instance arithmetic.
- The driver pattern in `sdma_v4_4.c` uses SDMA0 register offsets plus per-instance deltas. Any consumer that directly uses `regSDMA1_*` or `regSDMA2_*` alongside the helper could double-apply an instance offset.
- The chunk ends in the middle of the SDMA2 PAGE mid-command register set. Any generated documentation or code review that treats this chunk as a complete file would miss the remainder of SDMA2 and later instances.
- These definitions are architecture-specific. Reusing them for a nearby IP revision, such as SDMA 4.4.2, risks silent register-layout mismatches.

## Test Signals

Useful validation signals for this header are mostly integration and hardware-facing:

- Compile coverage of `sdma_v4_4.c` with this header and `sdma_4_4_0_sh_mask.h` included.
- Static checks that every `reg*` macro has a matching `reg*_BASE_IDX` macro, except where a chunk boundary deliberately cuts a pair such as the final `regSDMA2_PAGE_MIDCMD_DATA9` line here.
- Generation-diff checks against AMD's authoritative SDMA 4.4.0 register specification.
- Runtime boot/probe on SDMA 4.4 hardware, confirming firmware load, ring allocation, doorbell writes, queue submission, and GPU reset paths.
- RAS diagnostics that read `EDC_COUNTER` and `EDC_COUNTER2` across instances and report expected instance-specific counters.
- Suspend/resume and preemption tests that exercise `CSA_ADDR_*`, `MIDCMD_*`, `PREEMPT`, and ring pointer state.
- Performance-counter smoke tests that configure and read `PERFCNT_*` registers without hangs or invalid values.

### subset-b-003361: lines 2438-4848

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h lines 2438-4848

## Purpose

This chunk is a generated AMD SDMA 4.4.0 register-offset header slice. It is not executable driver logic; it exports preprocessor constants that name memory-mapped SDMA register offsets and their generated base-index selectors for the AMDGPU SDMA 4.4 register ABI.

The range starts at the tail of the `SDMA2_PAGE` mid-command register group, covers `SDMA2_RLC0` through `SDMA2_RLC7`, covers the full visible `SDMA3` instance register block in this header slice, then covers `SDMA4` public, GFX, PAGE, and RLC queue groups through the beginning of `SDMA4_RLC3_MIDCMD_DATA0`. The chunk ends mid-`SDMA4_RLC3` queue group, so the remaining `SDMA4_RLC3` mid-command registers and later RLC queues continue in the next chunk.

## Public Surface

The exported API is macro-only:

- `regSDMA*_...` macros define register offsets for SDMA 4.4.0 instance, queue, status, doorbell, RAS, performance-counter, UTCL1, and command-stream state registers.
- `regSDMA*_..._BASE_IDX` macros define the generated register-base index. In this chunk these base indices are consistently `0`.
- `regCC_SDMA3_EDC_CONFIG` and `regCC_SDMA4_EDC_CONFIG` are clock/control EDC configuration register offsets associated with SDMA3 and SDMA4.

There are no functions, structs, enums, inline helpers, allocation sites, locks, or persistent software objects in this chunk. Field-level decoding and composition live in the matching `sdma_4_4_0_sh_mask.h` header.

## Register Families Covered

The chunk contains 1201 address macros plus their generated base-index companions, with one extra base-index-only line at the start because the range begins immediately after `regSDMA2_PAGE_MIDCMD_DATA9`.

The `SDMA2` coverage is queue-focused. It completes `SDMA2_PAGE_MIDCMD_DATA10` and `SDMA2_PAGE_MIDCMD_CNTL`, then defines the complete RLC queue register sets for `SDMA2_RLC0` through `SDMA2_RLC7`. Each RLC set has ring-buffer control and base/rptr/wptr registers, write-pointer polling controls and poll address registers, indirect-buffer controls, skip/context status, doorbell and doorbell log/offset, watermark, CSA address, remaining IB state, preempt and dummy registers, AQL control, minor pointer update, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.

The `SDMA3` coverage includes the instance-level public block followed by all queue classes. Public registers include microcode access (`UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`), virtualization enable, context-group boundary, power and clock control/status, global control, chicken bits, graphics-memory address configuration, read-pointer and IB fetch registers, program/status registers, read burst and HBM page configuration, F32 controls/counter, freeze and phase quantum controls, EDC configuration/counters, BA threshold, ID/version, atomic pre-operation controls, UTCL1 controls/status/invalidation/XNACK/timeout/page registers, power idle and relaxed-ordering controls, physical-address and error-log registers, public dummy registers, performance-counter configuration/result registers, CRD and ULV controls, EA double-bit address capture, scratch RAM, CE control, and RAS status.

The `SDMA3_GFX` and `SDMA3_PAGE` queue blocks use the same ring-buffer/IB/doorbell/status/CSA/preempt/AQL/minor-pointer/mid-command pattern as the RLC queues. `SDMA3_GFX` additionally includes `CONTEXT_CNTL`. The chunk then defines complete RLC queue blocks for `SDMA3_RLC0` through `SDMA3_RLC7`.

The `SDMA4` coverage mirrors the `SDMA3` public block and queue layout for the fourth SDMA instance. It defines the public instance registers, complete `SDMA4_GFX` and `SDMA4_PAGE` queue blocks, complete `SDMA4_RLC0` through `SDMA4_RLC2` queue blocks, and a partial `SDMA4_RLC3` block ending at `regSDMA4_RLC3_MIDCMD_DATA0_BASE_IDX`.

## Important APIs And Usage Patterns

Consumers include this header together with `sdma_4_4_0_sh_mask.h`, then pass the register-offset macros to AMDGPU's SOC15/raw register access helpers. In `amdgpu/sdma_v4_4.c`, the SDMA 4.4 RAS path includes this header and uses the generated offsets with `sdma_v4_4_get_reg_offset()` and `RREG32()`/`WREG32()` to access per-instance EDC counter registers. That helper maps instance numbers onto SDMA base offsets such as `SDMA2_REG_OFFSET`, `SDMA3_REG_OFFSET`, and `SDMA4_REG_OFFSET`.

The queue offsets in this chunk are also semantically aligned with the newer `amdgpu/sdma_v4_4_2.c` implementation pattern: stop/resume paths program ring-buffer base, read/write pointer, doorbell, polling, and IB state; ring functions fetch and commit pointers; VM/page queues use the PAGE register group; compute queues use RLC groups; and diagnostics dump or reset queue and engine state. Even when this exact header slice is not directly referenced by handwritten queue setup code in the inspected tree, it is the generated ABI source for SDMA 4.4 register names and can be used by RAS, debug, register dump, or future queue-management paths.

## Control Flow

This header has no runtime control flow. Runtime behavior occurs in callers:

1. Driver code selects an SDMA instance and queue family.
2. It resolves the register address from the generated `regSDMA*` macro, often through an instance-offset helper or SOC15 register macro.
3. It reads or writes the register with AMDGPU MMIO helpers.
4. It uses the matching shift/mask header to decode fields such as ring enable, ring size, VMID, writeback enable, doorbell enable, status bits, EDC counters, or queue context status.

Because this chunk is offset-only, it does not encode register access ordering, locking, polling timeouts, write-one-to-clear behavior, or required firmware/hardware sequencing. Those rules must come from the SDMA implementation, AMDGPU ring/VM/RAS code, and hardware specifications.

## State And Persistence

The header itself stores no state. The state named by these macros lives in SDMA hardware registers and in memory buffers addressed by those registers.

Important hardware state includes loaded SDMA microcode address/data windows, power and clock-gating configuration, global SDMA enable/control state, RAS/EDC counters, UTCL1 translation/cache invalidation and XNACK status, performance counter configuration/results, scratch RAM, ring-buffer base/rptr/wptr state, write-pointer polling addresses, indirect-buffer progress, queue context status, doorbell state/logs/offsets, watermarks, CSA save areas, preemption state, AQL mode, and mid-command replay/resume data.

Some state is configuration programmed during initialization, resume, reset recovery, or queue creation. Other state is live hardware-owned progress or diagnostic status. RAS/EDC and error-log registers may be sticky or clear-on-write depending on field semantics from the paired shift/mask header and hardware documentation.

## Dependencies And Integration Points

The direct companion is `sdma_4_4_0_sh_mask.h`, which defines field shifts and masks for many of the register names declared here. Driver code also depends on AMDGPU register-access infrastructure such as SOC15 register macros, `RREG32()`, `WREG32()`, ring helpers, VM update paths, KFD compute queue setup, RAS managers, reset handling, and firmware loading.

The SDMA 4.4 integration point in this source tree is `amdgpu/sdma_v4_4.c`, which includes this offset header for RAS counter access. Related SDMA implementations and KFD code show the same queue-register families used for GFX, PAGE, and RLC ring setup, doorbell programming, write-pointer polling, preemption, and queue reset/restore.

The register layout is hardware-version-specific. Mixing these `regSDMA*_...` offsets with `mmSDMA*_...` offsets or masks from older generated directories such as `sdma2_4_2_2`, `sdma3_4_2_2`, `sdma4_4_2_2`, or GC 10.x headers can target the wrong address space or apply subtly wrong field definitions.

## Risks And Maintenance Notes

- This file is generated and highly repetitive. A single wrong offset or duplicated base index can silently route MMIO to the wrong SDMA instance, queue, or register.
- Chunk boundaries are partial. This range starts with `regSDMA2_PAGE_MIDCMD_DATA9_BASE_IDX` without the corresponding address macro and ends after `regSDMA4_RLC3_MIDCMD_DATA0_BASE_IDX`; merge-time reconciliation must join adjacent chunks before treating SDMA2 PAGE or SDMA4 RLC3 as complete.
- RLC queue blocks are structurally similar but not interchangeable. `RLC0` through `RLC7` have repeated names with different addresses; copy/paste or generated-table mistakes can affect the wrong compute queue.
- GFX, PAGE, and RLC queue groups share many register names, but their scheduling roles differ. Using PAGE offsets for normal copy queues, or RLC offsets for VM/page queues, can break VM updates, compute queue scheduling, or KFD integration.
- Doorbell, write-pointer polling, and read-pointer writeback registers connect MMIO state to host-visible memory and doorbell apertures. Bad offsets can cause missed interrupts, stuck rings, stale pointers, or writes to an unintended doorbell.
- IB base/size/offset, CSA, preempt, and mid-command registers are recovery-sensitive. Incorrect programming can corrupt resume-after-preempt state or make queue reset recovery unreliable.
- RAS/EDC, UTCL1, EA double-bit address, error-log, and status registers are diagnostic and may have sticky or side-effecting semantics not represented by the offset macros.
- All base indices in this chunk are `0`; callers must not infer that the same base index applies to other generated SDMA or GC register namespaces.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for `amdgpu/sdma_v4_4.c` and any generated-header users including `sdma_4_4_0_offset.h` and `sdma_4_4_0_sh_mask.h`.
- Static generated-header checks that each address macro has a matching `_BASE_IDX` macro, allowing for known chunk-boundary exceptions during per-chunk research.
- Cross-header checks that queue register names in this offset header have matching field definitions in `sdma_4_4_0_sh_mask.h` where fields are expected.
- Runtime SDMA RAS validation on SDMA 4.4 hardware that reads and resets `EDC_COUNTER` and `EDC_COUNTER2` through each instance offset and reports only the intended SDMA instance.
- Ring bring-up tests that initialize GFX, PAGE, and RLC queues, confirm ring write/read pointer movement, and complete `test_ring` and `test_ib` style DMA submissions.
- Doorbell tests that verify each queue's doorbell offset/log and write-pointer polling address correspond to the intended ring.
- VM update tests using SDMA page queues to exercise PAGE ring offsets and detect stuck VM PTE/PDE updates.
- KFD/compute queue tests that exercise RLC queue setup, AQL control, preemption, and context-save-area programming.
- Reset, suspend/resume, and preemption tests that validate CSA, IB remaining/submission state, and mid-command data registers are restored or ignored according to the SDMA firmware contract.
- Register-dump comparison against AMD SDMA 4.4 hardware documentation or golden generated headers, especially around the SDMA2 PAGE tail and SDMA4 RLC3 boundary.

### subset-b-003362: lines 4849-5224

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h lines 4849-5224

## Purpose

This chunk is the final slice of the generated AMD SDMA 4.4.0 register-offset header. It is not executable driver logic; it exports preprocessor constants that name SDMA4 RLC context queue registers and their register-base indices.

The covered range finishes the `regSDMA4_RLC3_MIDCMD_*` block, then defines complete `regSDMA4_RLC4_*`, `regSDMA4_RLC5_*`, `regSDMA4_RLC6_*`, and `regSDMA4_RLC7_*` register blocks. The file ends with the `#endif` for `_sdma_4_4_0_OFFSET_HEADER`, so this is the tail of the source file.

## Public Surface

The exported interface is macro-only:

- `regSDMA4_RLC*_...` macros map symbolic register names to 32-bit register offsets for SDMA instance 4.
- `regSDMA4_RLC*_..._BASE_IDX` macros map each register to base index `0`.

There are no functions, structs, enums, inline helpers, state variables, or side-effecting code in this chunk. Consumers include this header and pass the offset constants into AMDGPU/SOC15 register access helpers, or use them as generated ABI data for register dumps and tooling.

## Register Families Covered

The first lines complete RLC3 mid-command snapshot registers: `MIDCMD_DATA1` through `MIDCMD_DATA10` and `MIDCMD_CNTL`. Adjacent previous lines define `MIDCMD_DATA0`, so merge-time documentation should treat RLC3 as a partial block in this chunk.

Each complete RLC4-RLC7 block follows the same layout:

- Ring-buffer setup and pointer registers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Write-pointer polling and read-pointer writeback registers: `RB_WPTR_POLL_CNTL`, `RB_RPTR_ADDR_HI`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_HI`, `RB_WPTR_POLL_ADDR_LO`.
- Indirect-buffer registers: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Scheduling/context state registers: `SKIP_CNTL`, `CONTEXT_STATUS`, `PREEMPT`, `MINOR_PTR_UPDATE`, and `DUMMY_REG`.
- Doorbell and queue status registers: `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, and `DOORBELL_OFFSET`.
- Context-save area registers: `CSA_ADDR_LO` and `CSA_ADDR_HI`.
- AQL and mid-command capture registers: `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA10`, and `MIDCMD_CNTL`.

The offsets are regular and context-strided. RLC4 begins at `0x1d830`, RLC5 at `0x1d888`, RLC6 at `0x1d8e0`, and RLC7 at `0x1d938`, with the same internal gaps before status and mid-command regions. This regularity matters because generated-header consumers often assume same-generation register groups have a stable shape across RLC contexts and SDMA instances.

## Important APIs, Types, And Functions

This chunk itself defines no C API beyond macros. Its important integration API is the AMDGPU register-access convention:

- `amdgpu/sdma_v4_4.c` includes both `sdma/sdma_4_4_0_offset.h` and `sdma/sdma_4_4_0_sh_mask.h`.
- `sdma_v4_4_get_reg_offset()` computes an absolute register address for SDMA instances 0-4 from the SDMA0 base plus instance deltas. The hard-coded SDMA4 instance delta is `0x1d5a0`.
- SOC15-style helpers and macros such as `SOC15_REG_ENTRY`, `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and field helpers combine an offset macro from this file with bit definitions from `sdma_4_4_0_sh_mask.h`.

The matching shift/mask header provides semantic fields for these offsets. For example, the RLC ring-buffer control registers carry enable, size, swap, read-pointer writeback, privilege, and VMID fields; indirect-buffer control carries enable, swap, in-IB switching, and command VMID fields; context status exposes selected, idle, expired, exception, context-switch, preempted, and preempt-disable state; doorbell registers expose enable/captured status; and mid-command control exposes data-valid, copy-mode, split-state, and allow-preempt bits.

## Control Flow

There is no runtime control flow in the header. The effective flow in driver code is compile-time substitution followed by hardware MMIO access:

1. An SDMA 4.4 translation unit includes this offset header and the matching shift/mask header.
2. Driver code selects a register macro for an SDMA instance/context queue, or computes the equivalent instance address from the SDMA0 register layout.
3. The AMDGPU register helper resolves the SOC15 block base and per-instance offset.
4. The driver reads or writes the hardware register, using shift/mask macros for bit fields when needed.
5. Hardware consumes the programmed queue base, pointer, doorbell, polling, context, AQL, preemption, or mid-command state.

For this specific chunk, the control surface is queue/context management for SDMA4 RLC queues 3-7 rather than the global SDMA engine control path.

## State And Persistence Behavior

The header persists no software state. All state represented by these macros lives in SDMA hardware registers or in memory regions pointed to by those registers.

Ring-buffer registers persist queue configuration until reset or reprogramming: base addresses, high address bits, read/write pointers, write-pointer polling configuration, and read-pointer writeback addresses. Indirect-buffer registers persist IB execution state such as base, offset, read pointer, and size. Doorbell registers persist enable/offset state and capture doorbell activity. Context and preemption registers expose scheduler-visible state for queue selection, idleness, exceptions, context-switch readiness, preemption, and context-save area location. `MIDCMD_DATA*` and `MIDCMD_CNTL` hold hardware mid-command snapshot or resume state, used when preemption or context switching interrupts a command stream.

Several registers represent live or hardware-owned state rather than simple configuration. `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `CONTEXT_STATUS`, `IB_SUB_REMAIN`, and `MIDCMD_*` values can change as the engine executes work. The macros do not encode read-only, write-one-to-clear, reset, ordering, or synchronization rules; callers must rely on SDMA hardware documentation and the surrounding AMDGPU queue-management code.

## Dependencies And Integration Points

The direct generated-header dependency is `sdma_4_4_0_sh_mask.h`, which supplies the bit layout for the register names defined here. The broader AMDGPU dependency is the SOC15 register-access layer and the SDMA 4.4 implementation in `amdgpu/sdma_v4_4.c`.

The register families integrate with:

- AMDGPU SDMA queue setup and teardown, where ring-buffer bases, pointer registers, polling addresses, and doorbells are configured.
- GPU scheduler and context-switch/preemption flows, where `CONTEXT_STATUS`, `PREEMPT`, `CSA_ADDR_*`, `IB_SUB_REMAIN`, and `MIDCMD_*` registers are relevant.
- Doorbell infrastructure, where user or kernel queues notify hardware through doorbell offsets and logs.
- VMID and privilege handling via ring-buffer and indirect-buffer control fields in the matching shift/mask header.
- AQL/HSA-style queue operation through `RB_AQL_CNTL`.
- Register dumps, diagnostics, RAS/debug flows, and generated tooling that need symbolic names for SDMA4 RLC queue registers even if handwritten driver code tends to use SDMA0-style offsets plus instance deltas.

## Risks And Maintenance Notes

- The file is generated and repetitive. A single wrong offset can point queue setup, preemption state, or diagnostics at the wrong hardware register without a C compiler warning.
- This chunk starts mid-RLC3. Merge/reconciliation must include the previous chunk to capture `regSDMA4_RLC3_MIDCMD_DATA0` and the earlier RLC3 queue registers.
- RLC4-RLC7 blocks are structurally identical but not interchangeable. Copying a register name or offset across RLC indices can target a different queue context.
- These are SDMA4-specific offsets. `sdma_v4_4.c` also computes SDMA instance addresses from SDMA0 offsets and instance deltas; generated SDMA4 offsets must remain consistent with that calculation.
- All `_BASE_IDX` values in this chunk are `0`. If a future generation changes base indexing, using these names with the wrong generation's SOC15 metadata would misaddress registers.
- Ring-buffer, IB, doorbell, and polling registers touch GPU-visible memory addresses. Bad offset use can cause the engine to read or write the wrong queue memory, stale pointer writeback area, or doorbell slot.
- Context-save, preemption, and mid-command registers are sensitive to scheduler timing. Reading or writing them outside the expected quiescent/preemption flow can race active hardware.
- Full-width data/address registers rely on 32-bit unsigned MMIO paths. Signed constants or truncating address composition would be unsafe for `*_BASE_HI`, `*_ADDR_HI`, and `MIDCMD_DATA*` registers.
- The final `#endif` is part of this chunk. Any generated-file edit that drops or duplicates it will break the whole include guard.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for `amdgpu/sdma_v4_4.c` with `sdma_4_4_0_offset.h` and `sdma_4_4_0_sh_mask.h` included together.
- Generated-header consistency checks that every `regSDMA4_RLC4` through `regSDMA4_RLC7` offset has a matching `_BASE_IDX` and matching field definitions in `sdma_4_4_0_sh_mask.h`.
- Cross-instance checks that SDMA4 offsets match SDMA0 offsets plus the `SDMA4_REG_OFFSET` delta used by `sdma_v4_4_get_reg_offset()`.
- Static checks for complete RLC4-RLC7 register sequences: RB, IB, context/status, doorbell, CSA, polling, AQL, minor pointer update, and `MIDCMD_DATA0` through `MIDCMD_DATA10` plus `MIDCMD_CNTL`.
- Register-dump validation on SDMA 4.4 hardware that symbolic SDMA4 RLC4-RLC7 addresses decode to the same values reached through the driver's instance-offset calculation.
- Runtime SDMA queue tests that submit work on contexts using ring-buffer, indirect-buffer, doorbell, and write-pointer polling paths, then verify pointer writeback and queue idleness.
- Preemption/context-switch tests that force SDMA IB preemption and verify `CONTEXT_STATUS`, `IB_SUB_REMAIN`, `CSA_ADDR_*`, and `MIDCMD_*` state is coherent before and after resume.
- Negative diagnostics for doorbell misrouting: doorbell logs and queue write pointers should change only for the intended RLC context.
