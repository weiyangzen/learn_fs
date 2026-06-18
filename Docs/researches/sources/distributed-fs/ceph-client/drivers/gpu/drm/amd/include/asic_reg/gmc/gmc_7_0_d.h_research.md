<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_d.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_d.h

## Purpose

`gmc_7_0_d.h` is a generated AMDGPU register-address header for the GMC 7.0 memory-controller and GPU virtual-memory block. It exports symbolic MMIO register offsets for the CIK/GFX7-era memory controller, VM/TLB hardware, MC hub, arbitration, crossbar, ATC/ATS, power/clock gating, peer-to-peer routing, performance counters, and fault-reporting registers.

The file is pure register metadata. It lets driver code refer to hardware registers as names such as `mmMC_VM_FB_LOCATION`, `mmVM_INVALIDATE_REQUEST`, `mmVM_CONTEXT0_CNTL`, and `mmMC_ARB_RAMCFG` instead of embedding raw offsets. Consumers pair these offset macros with the companion `gmc_7_0_sh_mask.h` field definitions and the common `RREG32`, `WREG32`, `WREG32_P`, and ring write helpers.

## Important APIs, Types, And Macros

The header defines no C functions, structs, enums, or inline helpers. Its public API is the `mm...` macro namespace inside the `GMC_7_0_D_H` include guard.

Important macro families include:

- Memory-controller configuration and arbitration: `mmMC_CONFIG`, `mmMC_ARB_*`, `mmMC_ARB_RAMCFG`, DRAM timing, refresh, busy/status, return-credit, and harsh bandwidth controls.
- MC hub and client interface routing: `mmMC_HUB_*`, `mmMC_CITF_*`, `mmMC_RD_*`, and `mmMC_WR_*` registers for read/write clients, credits, watermarks, power, clock gating, idle/status, and per-client request paths.
- GPU memory aperture and VM setup: `mmMC_VM_FB_LOCATION`, `mmMC_VM_AGP_TOP`, `mmMC_VM_AGP_BOT`, `mmMC_VM_AGP_BASE`, `mmMC_VM_SYSTEM_APERTURE_*`, `mmMC_VM_MX_L1_TLB_CNTL`, `mmMC_VM_FB_OFFSET`, and debug/status registers for MC VM L1/L2 arbiters.
- XPB/crossbar and peer routing: `mmMC_XPB_*`, `mmMC_XBAR_*`, peer system BARs, P2P BAR setup, destination maps, local/global configuration, sticky/status registers, and crossbar credit/performance registers.
- Performance counters: low/high result registers and per-block counter configuration for CITF, HUB, RPB, MCBVM, MCDVM, VM L2, MC_ARB, ATC, and CHUB_ATC.
- ATC/ATS translation state: `mmATC_VM_APERTURE*`, `mmATC_ATS_*`, `mmATC_L1*`, `mmATC_L2*`, and `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID15_PASID_MAPPING`.
- GMCON and power-management control: `mmGMCON_*`, `mmMC_MEM_POWER_LS`, `mmMC_SHARED_BLACKOUT_CNTL`, and clock/power gating registers.
- VM L2 and context registers: `mmVM_L2_CNTL`, `mmVM_L2_CNTL2`, `mmVM_L2_CNTL3`, `mmVM_CONTEXT0_CNTL`, `mmVM_CONTEXT1_CNTL`, page-table base/start/end registers for VMIDs 0-15, `mmVM_INVALIDATE_REQUEST`, `mmVM_INVALIDATE_RESPONSE`, PRT aperture/control registers, fault status/client/address/default-address registers, `mmVM_L2_CG`, and identity aperture registers.

This header supplies offsets only. Bit layout comes from `gmc_7_0_sh_mask.h`, and some related GMC 7.1 sequencer offsets used by the same generation live in `gmc_7_1_d.h`.

## Control Flow

There is no runtime control flow in this file beyond the preprocessor include guard. Runtime behavior appears in consumers that compile these constants into MMIO accesses.

The most direct consumer is `amdgpu/gfx_v7_0.c`, which includes `gmc/gmc_7_0_d.h` and `gmc/gmc_7_0_sh_mask.h`. Its VM flush path emits `mmVM_INVALIDATE_REQUEST` into graphics ring packets after `amdgpu_gmc_emit_flush_gpu_tlb()`, then waits on the invalidate register. Its configuration path reads `mmMC_ARB_RAMCFG` to derive bank and rank geometry for GFX tiling configuration.

The broader GMC 7.x control flow is in `amdgpu/gmc_v7_0.c`, which uses the same register families while including the 7.1 GMC generated headers. That driver initializes VRAM/GART placement from `MC_VM` aperture registers, programs system and AGP apertures, enables L1/L2 VM translation, initializes VMID 0 and VMIDs 1-15 page-table bases, invalidates TLBs through `VM_INVALIDATE_REQUEST`, handles VM faults through `VM_CONTEXT1_PROTECTION_FAULT_*`, and toggles MC/HDP clock or light-sleep controls. SDMA and UVD ring code also poll or write `VM_INVALIDATE_REQUEST` when emitting VM flush packets.

## State And Persistence Behavior

The header itself has only immutable compile-time constants. The named registers represent volatile hardware state in the GPU memory controller and VM block.

Persistent or semi-persistent hardware state includes VRAM and GART aperture programming, AGP bounds, page-table base/start/end registers, VM context enable bits, default fault pages, PRT apertures, clock-gating controls, power-gating controls, channel maps, peer BAR routing, and arbitration timing. These values remain in hardware until driver reprogramming, suspend/resume, reset, firmware activity, power gating, or ASIC initialization overwrites them.

Volatile state includes busy/status registers, performance-counter results, VM fault status/address/client registers, ATC ATS fault status, invalidate response, idle indicators, and sticky or write-one-to-clear status bits. Consumers must treat these as hardware-owned state and avoid assuming cached software values are authoritative.

## Dependencies

This file depends on AMD's generated ASIC register database and naming conventions. The offsets must match the selected GFX7/GMC7 register map; using them with the wrong ASIC generation can target unrelated registers.

Functional use depends on:

- `gmc_7_0_sh_mask.h` for bit-field masks and shifts such as `MC_ARB_RAMCFG__NOOFBANK_MASK` and `VM_CONTEXT*_CNTL` fields.
- AMDGPU register access helpers such as `RREG32`, `WREG32`, `WREG32_P`, `amdgpu_ring_emit_wreg`, and packet builders in graphics, SDMA, and UVD ring code.
- Core AMDGPU structures and services that hold memory topology and VM state, including `struct amdgpu_device`, `struct amdgpu_gmc`, `struct amdgpu_vm`, GART allocation, BO management, IRQ handling, and KFD PASID/VMID integration.
- Related register headers for adjacent blocks such as BIF, OSS, DCE, GCA, and the GMC 7.1 sequencer header used by the CIK GMC implementation.

## Integration Points

`amdgpu/gfx_v7_0.c` is the direct include site for this header. It integrates the register offsets into graphics VM flush packets and graphics tiling configuration.

GMC setup integrates through `amdgpu/gmc_v7_0.c`: MC programming writes system aperture and AGP registers, GART enable writes VM L1/L2 and context registers, TLB flush code writes `VM_INVALIDATE_REQUEST`, PRT setup writes `VM_PRT_*`, VM fault IRQ handling reads `VM_CONTEXT1_PROTECTION_FAULT_*`, and clock-gating helpers use `MC_HUB`, `MC_CITF`, `MC_XPB`, `ATC_MISC_CG`, and `VM_L2_CG` registers.

Other integration points include `amdgpu/cik_sdma.c`, `amdgpu/uvd_v6_0.c`, and related ring emitters that use the VM invalidate register address in command streams; `amdgpu/cik.c`, `amdgpu/vi.c`, and `amdgpu/si.c` register allowlists and flush helpers; and `pm/legacy-dpm/si_dpm.c`, which reads `mmMC_ARB_RAMCFG` and programs MC arbitration/timing registers for memory-clock and DRAM-timing behavior.

## Risks And Edge Cases

The largest risk is register-map drift. A single wrong offset can make a VM flush, page-table base update, fault read, or MC aperture write hit the wrong MMIO register, which can show up as GPU hangs, memory corruption, invalid page faults, display corruption, or broken suspend/resume.

The file contains only offsets, so consumers must use the matching shift/mask header for the same generation. Mixing GMC 7.0 offsets with another generation's field layout is especially risky for context control, fault status, clock gating, and arbitration timing registers.

Some register ranges are indexed by arithmetic in consumers, such as VM context page-table base registers and PASID mapping registers. The offsets must remain contiguous exactly where code assumes `base + vmid`; otherwise VMID-specific state will be written to the wrong context. Ring packet paths also sometimes shift register offsets left by two for byte addressing, so using an already byte-addressed value would corrupt command streams.

Hardware state has ordering requirements that the header cannot express. Aperture changes, MC blackout, TLB invalidation, clock gating, PRT fault masking, and VM context enablement must be sequenced by the driver with idle waits, readbacks, or poll loops. Status and clear bits can be sticky or write-one-to-clear, so read-modify-write operations need the companion masks and hardware documentation.

## Test Signals

Build coverage should include `amdgpu/gfx_v7_0.c` so direct references to `gmc_7_0_d.h` macros and the companion field macros resolve. Static validation can compare every offset against AMD register metadata and verify contiguous ranges used by arithmetic, especially `mmATC_VMID*_PASID_MAPPING`, `mmVM_CONTEXT*_PAGE_TABLE_BASE_ADDR`, and context control registers.

Runtime signals include successful initialization messages for PCIE GART, stable VMID/TLB flushes from GFX, SDMA, and UVD rings, correct VRAM size and bank/rank geometry detection from `MC_ARB_RAMCFG`, no unexpected `VM_CONTEXT1_PROTECTION_FAULT_*` logs under ordinary workloads, working KFD PASID fault reporting, clean suspend/resume, and no MC idle timeout warnings during reset or memory-controller programming. GPUVM stress tests, GART eviction/recovery tests, SDMA copy tests, UVD decode with VM memory, and memory-clock switching tests are strong integration coverage for this register set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gmc/gmc_7_0_d.h -->
