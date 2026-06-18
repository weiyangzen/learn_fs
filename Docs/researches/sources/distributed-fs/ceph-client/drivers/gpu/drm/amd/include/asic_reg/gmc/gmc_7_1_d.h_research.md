# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_d.h

## Scope

This report covers `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_1_d.h`, a 1,464-line AMDGPU register-definition header for the GMC 7.1 memory-controller generation. The file is a generated-style C preprocessor header with a copyright/license block, the `GMC_7_1_D_H` include guard, and 1,437 exported `#define` constants. It contains no functions, structs, enums, runtime variables, locks, allocations, callbacks, or direct I/O logic.

Although this repository path is under `distributed-fs/ceph-client`, this source is Linux AMDGPU driver hardware metadata. Its behavior is realized by consumers that include it and pass the numeric register constants to AMDGPU read/write helpers.

## Purpose

The header gives CIK/Sea Islands-era AMDGPU code symbolic names for GMC 7.1 memory-management, memory-controller, VM, ATC, GMCON, memory-sequencer, and memory PHY/debug registers. These constants prevent consumers from using unlabelled MMIO offsets and keep register names aligned with the sibling bitfield header `gmc_7_1_sh_mask.h`.

Major register groups covered by the file include:

- `mmMC_*`: memory-controller configuration, arbitration, hub request/return paths, memory-channel mapping, VM aperture registers, crossbar/XPB routing, perf counters, DRAM timing, memory BIST, memory sequencer, memory PHY, memory PLL, power-management, blackout, and debug/data-port registers.
- `mmVM_*`: GPU VM L2 cache controls, VM context control registers, page-table base/start/end registers, invalidate request/response, protection-fault status/client/address/default-address registers, PRT aperture controls, and identity aperture controls.
- `mmATC_*`: address-translation-cache aperture, ATS status/fault, L1/L2 debug/status/control, and VMID-to-PASID mapping registers.
- `mmGMCON_*`: graphics-memory-controller register-engine, save-range, perf, power-gating FSM, mask, target, and debug registers.
- `ixMC_TSM_DEBUG_*` and `ixMC_IO_DEBUG_*`: indexed debug-register selector values used with `mmMC_SEQ_TSM_DEBUG_INDEX`/`DATA` and `mmMC_SEQ_IO_DEBUG_INDEX`/`DATA`.

## API Surface

The public API is entirely macro based:

- `mm...` macros are MMIO register offsets. Examples: `mmMC_VM_FB_LOCATION`, `mmVM_L2_CNTL`, `mmVM_INVALIDATE_REQUEST`, `mmATC_VMID0_PASID_MAPPING`, `mmMC_SEQ_IO_DEBUG_INDEX`, and `mmMPLL_CNTL_MODE`.
- `ix...` macros are indexed register or debug table selectors written through an index/data register pair. Examples: `ixMC_TSM_DEBUG_GCNT`, `ixMC_IO_DEBUG_DQB0L_MISC_D0`, and `ixMC_IO_DEBUG_WCDR_RX_DYN_PM_D1`.

There are no type definitions or callable functions. Consumers use the macros with AMDGPU register helpers such as `RREG32`, `WREG32`, `amdgpu_ring_emit_wreg`, `cgs_read_register`, and command-table entries. Bit manipulation is handled by `REG_GET_FIELD`, `REG_SET_FIELD`, and mask/shift macros from `gmc_7_1_sh_mask.h`.

The file's macro distribution is heavily memory-controller oriented: 912 `mm...` definitions and 524 `ix...` definitions, with the largest prefixes being `MC` (1,280), `VM` (58), `ATC` (52), `GMCON` (21), and `MPLL` (17).

## Control Flow

This header has no executable control flow. The effective flow is preprocessor substitution in including driver code:

1. A GMC 7.x/CIK driver source includes `gmc/gmc_7_1_d.h` and normally `gmc/gmc_7_1_sh_mask.h`.
2. The source references a symbolic register name in a register read, write, ring packet, or power-management command table.
3. The C preprocessor substitutes the numeric offset.
4. Runtime register helpers issue MMIO reads/writes or ring-emitted register writes to the hardware.

Important consumer paths include `amdgpu/gmc_v7_0.c`, which programs GART/VM/TLB state; `amdgpu/cik_sdma.c` and `amdgpu/gfx_v7_0.c`, which emit VM invalidation writes from rings; `amdgpu/amdgpu_amdkfd_gfx_v7.c`, which writes PASID mappings; `pm/powerplay/hwmgr/ci_baco.c`, which uses GMC register offsets in BACO entry/exit tables; `pm/powerplay/smumgr/ci_smumgr.c`, which reads memory-sequencer state; and `display/dc/resource/dce80/dce80_resource.c`, which includes the same ASIC register family for display-resource setup.

## State And Persistence Behavior

The header itself owns no state and persists nothing. It names hardware state that persists inside the GPU until reset, power transition, suspend/resume, firmware action, or explicit driver programming changes it.

Key state families are:

- Framebuffer and aperture state: `mmMC_VM_FB_LOCATION`, AGP aperture registers, system aperture registers, and default addresses define memory windows visible to GPU clients.
- VM and TLB state: `mmVM_CONTEXT*`, `mmVM_L2_*`, `mmVM_INVALIDATE_*`, and PRT registers govern page-table roots, context enablement, cache behavior, fault behavior, and invalidation acknowledgements.
- PASID/ATC state: `mmATC_VMID*_PASID_MAPPING` and ATS fault/status registers map process address-space IDs to VMIDs and expose address-translation failures.
- Memory-controller state: arbitration timing, request credits, refresh, DRAM timing, channel remap, crossbar routing, blackout, clock gating, BIST, and sequencer registers influence live memory access and power behavior.
- Firmware/load-time state: MC microcode loading writes `mmMC_SEQ_SUP_CNTL`, `mmMC_SEQ_IO_DEBUG_INDEX`, `mmMC_SEQ_IO_DEBUG_DATA`, and `mmMC_SEQ_SUP_PGM`; those registers shape sequencer operation and training.
- Debug and perf state: perf counter config/result registers and indexed debug selectors expose diagnostic state but can also perturb hardware if written incorrectly.

## Dependencies And Integration Points

Primary dependencies:

- `gmc/gmc_7_1_sh_mask.h` supplies the matching masks and shifts for fields inside these offsets.
- AMDGPU register helpers (`RREG32`, `WREG32`, `amdgpu_ring_emit_wreg`, `cgs_read_register`) provide the actual MMIO or ring-write transport.
- ASIC-family headers such as `bif_4_1_*`, `oss_2_0_*`, `dce_8_0_*`, `smu_7_0_1_*`, and `gfx_7_2_*` are often included beside this file in CIK power, display, and graphics paths.
- Firmware structures in `gmc_v7_0.c` provide MC microcode and IO-debug register/value arrays; this header provides the index/data and sequencer registers used to load them.
- KFD/HSA paths depend on `mmATC_VMID*_PASID_MAPPING` and `mmIH_VMID_0_LUT`-adjacent programming to keep VMID/PASID state coherent.

Integration is strict by name and number. A consumer that compiles successfully still depends on the numeric offsets matching the exact ASIC generation. For example, `gmc_v7_0_emit_flush_gpu_tlb()` computes page-table base registers by adding a VMID to either `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR` or `mmVM_CONTEXT8_PAGE_TABLE_BASE_ADDR`, so contiguous register layout is part of the contract.

## Risks

- Offset drift can cause register writes to hit the wrong hardware block. This is especially high risk for VM, blackout, PLL, DRAM timing, and sequencer registers because failures can appear as GPU hangs, memory corruption, display failures, or power-transition failures.
- Mask/header mismatch is subtle. `gmc_7_1_d.h` can compile with stale or wrong `gmc_7_1_sh_mask.h` data, producing writes to the right register with wrong bit positions.
- Indexed debug selectors are easy to misuse. The large `ixMC_IO_DEBUG_*` space relies on correct pairing with the index/data registers; one wrong selector can program training or PHY debug state for the wrong lane/channel.
- Contiguous-register assumptions are embedded in consumers. VM context base-address and ATC PASID mapping code adds `vmid` to base macros; holes or reordered definitions would break runtime behavior even if individual macro names remain present.
- Cross-generation similarity increases review risk. GMC 6.x, 7.0, 7.1, 8.1, and 8.2 headers share many names and offsets but are not always interchangeable. Including the wrong generation header may compile while targeting incompatible hardware behavior.
- The file is large and repetitive, so manual review is poor at catching single-value errors. Generated-source provenance or comparison against AMD register databases is a stronger validation signal than style review.

## Test Signals

Useful validation signals are mostly compile-time, hardware bring-up, and stress/runtime behavior:

- Build AMDGPU CIK/GMC 7.x code with `gmc_7_1_d.h` and `gmc_7_1_sh_mask.h`; missing or renamed macros should fail in `gmc_v7_0.c`, `ci_baco.c`, KFD GFX v7 integration, and ring-emission code.
- Boot affected ASICs such as Bonaire/Hawaii/Topaz-class hardware and verify MC firmware loads, memory training completes, VRAM/GART apertures are detected, and `gmc_v7_0_gart_enable()` succeeds.
- Exercise GPU VM paths: BO mapping, page-table updates, page faults/default-page handling, PRT enable/disable, `mmVM_INVALIDATE_REQUEST` writes, and invalidate response reads.
- Exercise KFD/PASID paths that program VMID mappings and confirm process isolation, queue execution, and TLB invalidation by PASID.
- Run suspend/resume and BACO entry/exit tests, watching for failures around `mmMPLL_*`, `mmMCLK_PWRMGT_CNTL`, `mmMC_IO_RXCNTL_*`, `mmMC_SEQ_CNTL_2`, and blackout/register-save behavior.
- Run display and memory pressure tests that stress request arbitration, hub credits, channel remap, VM faults, and perf/status counters.
- For source validation, compare every `mm...` and `ix...` value against the authoritative GMC 7.1 register database or a known-good upstream snapshot, with spot checks on contiguous VM context and PASID ranges.
