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
