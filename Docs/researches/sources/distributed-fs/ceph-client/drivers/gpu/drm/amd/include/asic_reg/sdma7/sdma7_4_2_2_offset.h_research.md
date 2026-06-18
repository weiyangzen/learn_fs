# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma7/sdma7_4_2_2_offset.h

## Purpose

This header is an AMDGPU ASIC register offset table for the Arcturus `SDMA7` engine, revision `4_2_2`. It publishes preprocessor constants named `mmSDMA7_*` that identify SDMA7 register offsets within the `sdma7_sdma7dec` address block. The file comment records the address block base as `0x7d000`, while the macros themselves expose register-relative dword offsets from `0x0000` through `0x03e1`.

The header contains no executable logic. Its role is to let SDMA/KFD driver code construct MMIO register addresses through AMDGPU's register access helpers, especially `SOC15_REG_OFFSET()`, `RREG32()`, and `WREG32()`. It is paired with `sdma7_4_2_2_sh_mask.h`, which supplies field masks and shifts for the registers listed here.

## Important API Surface

The public API is the macro namespace guarded by `_sdma7_4_2_2_OFFSET_HEADER`.

- 507 register offset macros use the form `mmSDMA7_<REGISTER_NAME>`.
- Each offset macro has a matching `mmSDMA7_<REGISTER_NAME>_BASE_IDX` macro.
- Every `_BASE_IDX` value in this file is `1`, indicating that consumers should resolve these offsets against base-index slot `1` in the relevant SOC15 IP base data.
- The first register is `mmSDMA7_UCODE_ADDR` at `0x0000`.
- The last register is `mmSDMA7_RLC7_MIDCMD_CNTL` at `0x03e1`.

The major register families are:

- Global SDMA engine registers: microcode access (`UCODE_ADDR`, `UCODE_DATA`, `UCODE_CHECKSUM`), VM context controls, virtualization controls, public/context register type controls, MMHUB control, clock/power controls, SDMA control/status registers, EDC/error counters, atomic controls, UTCL1 controls, GPU IOV violation logs, and performance counters.
- `GFX` queue registers: ring buffer base/read/write pointer registers, indirect buffer registers, doorbell controls/logging, context status/control, preemption, AQL control, minor pointer update, and mid-command data/control registers.
- `PAGE` queue registers: a parallel ring/IB/doorbell/status/preemption/mid-command layout for page-related SDMA operation.
- `RLC0` through `RLC7` queue registers: eight repeated queue-control register groups with identical structure and a fixed stride between queue instances.

There are no C types, enums, inline functions, or callable functions defined in this header.

## Register Layout Observations

The global register region begins at offset `0x0000` and covers engine-level control and status. The `GFX` queue block starts at `0x0080`, the `PAGE` queue block starts at `0x00d8`, and the RLC queue blocks begin at `0x0130`.

The RLC queue blocks follow a repeated pattern:

- `RLC0_RB_CNTL` starts at `0x0130`.
- `RLC1_RB_CNTL` starts at `0x0188`.
- `RLC2_RB_CNTL` starts at `0x01e0`.
- `RLC3_RB_CNTL` starts at `0x0238`.
- `RLC4_RB_CNTL` starts at `0x0290`.
- `RLC5_RB_CNTL` starts at `0x02e8`.
- `RLC6_RB_CNTL` starts at `0x0340`.
- `RLC7_RB_CNTL` starts at `0x0398`.

The queue stride is therefore `0x58` dwords. Driver code can exploit this regularity by deriving a queue offset from `RLC1_RB_CNTL - RLC0_RB_CNTL`, as the Arcturus KFD integration does.

## Control Flow

This file has compile-time control flow only:

- An include guard prevents duplicate macro definitions.
- The preprocessor expands register names into numeric constants wherever included.

There are no branches, loops, locking paths, callbacks, or runtime sequencing in this header. Runtime control flow appears in consumers that use these offsets to program SDMA queues, load microcode, read status registers, and dump queue state.

## State And Persistence

The header owns no mutable state and persists nothing. The constants describe hardware register locations. Persistent or semi-persistent state affected through these constants lives outside the file:

- GPU hardware state in SDMA7 registers.
- SDMA microcode state accessed through `UCODE_ADDR` and `UCODE_DATA`.
- Queue state stored in ring buffer base, read pointer, write pointer, IB, doorbell, context-save-area, and preemption registers.
- Driver-side MQD/ring state that is written into or restored from those registers by AMDGPU/KFD code.

Incorrect offsets in this table would make consumers read or write the wrong hardware register, causing state corruption in the device rather than in this source file.

## Dependencies

The header has no C includes. Its dependencies are contractual:

- SOC15 IP base data must define the SDMA7 base segments for base index `1`.
- AMDGPU register helpers must understand the `mm*` offset plus `_BASE_IDX` convention.
- Matching field definitions in `sdma7_4_2_2_sh_mask.h` must correspond to the same register revision.
- Consumers must include the correct SDMA engine-specific offset header for the engine they address.

The file is part of the generated AMD ASIC register header set under `drivers/gpu/drm/amd/include/asic_reg/`.

## Integration Points

The direct in-tree integration observed for this header is `amdgpu/amdgpu_amdkfd_arcturus.c`, which includes all SDMA0 through SDMA7 `4_2_2` offset and mask headers. For engine id `7`, `get_sdma_rlc_reg_offset()` uses:

- `SOC15_REG_OFFSET(SDMA7, 0, mmSDMA7_RLC0_RB_CNTL)` to resolve the absolute register address for SDMA7 RLC queue 0.
- `mmSDMA7_RLC0_RB_CNTL` to subtract back to an engine base offset.
- The common RLC queue stride derived from SDMA0 offsets to select `queue_id`.

Once that per-engine/per-queue offset is computed, KFD code writes and reads queue registers through the common `mmSDMA0_RLC0_*` names plus the calculated offset. This works only if each SDMA engine header, including this SDMA7 header, preserves the same relative RLC register layout.

Likely broader integration includes register dump/debug paths, queue load/destroy/is-occupied operations, doorbell programming, and firmware or hardware bring-up logic that needs SDMA7-specific offsets.

## Risks

- Offset drift: these constants must match the exact hardware revision. A stale or mismatched generated header can silently direct MMIO accesses to the wrong register.
- Base-index mismatch: every `_BASE_IDX` is `1`; if IP base tables or helper conventions change, address resolution can break even when offsets are correct.
- Cross-engine layout assumptions: Arcturus KFD uses SDMA0 register names plus a computed offset after resolving SDMA7's base. This depends on SDMA7's RLC queue layout matching SDMA0's relative layout and stride.
- Queue stride sensitivity: RLC queue blocks are regular, but code deriving queue offsets from `RLC1 - RLC0` will fail if a later hardware variant changes spacing or holes.
- Generated-file maintenance: manual edits are risky because this file is a dense hardware contract with no local type checking beyond macro names.
- Testing difficulty: many failures require real hardware or accurate emulation because compile-only checks can validate names but not semantic register correctness.

## Test Signals

Useful validation signals for this header are mostly integration and hardware-facing:

- Compile coverage for Arcturus AMDGPU/KFD paths that include `sdma7_4_2_2_offset.h`.
- Static checks that every `mmSDMA7_*` offset has a matching `_BASE_IDX` macro and that all base indexes are expected.
- Diff or generation checks against AMD's authoritative register database for SDMA7 `4_2_2`.
- Boot/probe on Arcturus-class hardware with SDMA7 present, confirming that SOC15 register resolution succeeds.
- KFD SDMA queue lifecycle tests covering load, occupied check, dump, and destroy for `engine_id == 7` and queue ids `0..7`.
- Ring/doorbell tests that verify SDMA7 queues accept work and advance read/write pointers.
- Register dump sanity checks that RLC queue ranges match the expected contiguous regions used by `kgd_arcturus_hqd_sdma_dump()`.

## Subset Research Notes

This research read the complete 1,043-line header. The file is a pure register-offset definition table: there are no hidden functions, data structures, persistence mechanisms, or runtime paths inside it. The substantive behavior is the compile-time hardware address contract consumed by AMDGPU and KFD SDMA code.
