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
