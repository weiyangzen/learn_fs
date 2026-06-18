# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h lines 2466-3366

## Scope

This chunk is the final MMHUB 1.8.0 register-offset range in the generated AMDGPU MMHUB offset header. It begins in the tail of `aid_mmhub_pctldec0`, runs through L1 TLB, ATC L2, VM L2, VM context, shared VM aperture, virtualization, performance counter, L2 TLB, and MM_CANE RAS/error status address blocks, then ends at the header guard `#endif`.

The file section contains only preprocessor constants. Every hardware register offset is represented as a `reg...` macro and, immediately after it, a matching `reg..._BASE_IDX` macro. There are no C functions, structs, data objects, runtime branches, or software-side persistence in this chunk.

Covered address blocks:

- Continued `aid_mmhub_pctldec0`, base `0x62a00`, 9 register offsets from `regPCTL0_SLICE4_CFG_DAGB_BUSY` through `regPCTL0_SLICE4_MISC`.
- `aid_mmhub_l1tlb_vml1dec`, base `0x62c00`, 8 L1 TLB status offsets from `regMC_VM_MX_L1_TLB0_STATUS` through `regMC_VM_MX_L1_TLB7_STATUS`.
- `aid_mmhub_l1tlb_vml1pldec`, base `0x62c80`, 5 L1 TLB performance-counter configuration/control offsets.
- `aid_mmhub_l1tlb_vml1prdec`, base `0x62cc0`, 2 L1 TLB performance-counter result offsets.
- `aid_mmhub_utcl2_atcl2dec`, base `0x62d00`, 20 ATC L2 control, status, cache, DSM, power, clock, and real-time-class offsets.
- `aid_mmhub_utcl2_vml2pfdec`, base `0x62d80`, 41 VM L2 control, status, protection-fault, identity-aperture, ECC/EDC, and clock offsets.
- `aid_mmhub_utcl2_vml2vcdec`, base `0x62e80`, 203 VM context, invalidate-engine, and per-context page-table offsets.
- `aid_mmhub_utcl2_vmsharedpfdec`, base `0x63200`, 24 shared VM/host-MMIO aperture and default/system aperture offsets.
- `aid_mmhub_utcl2_vmsharedvcdec`, base `0x63270`, 8 framebuffer aperture, AGP aperture, MC_VM_MISC, and L1 TLB control offsets.
- `aid_mmhub_utcl2_vmsharedhvdec`, base `0x632b0`, 62 virtualization, IOMMU, MARC, ATS, function-ID, and XGMI GPU IOV offsets.
- ATC L2, VM L2, and L2 TLB performance counter config/result blocks from bases `0x633b0`, `0x633b8`, `0x633d0`, `0x63430`, `0x63490`, and `0x634b0`.
- `aid_mmhub_utcl2_l2tlbdec`, base `0x63470`, L2 TLB status and GPUVA/VMID translation-assist request/response offsets.
- `aid_mmhub_mm_cane_mmcanedec`, base `0x635f0`, 6 MM_CANE clock/error/RAS status offsets.

## Purpose

This header section provides the numeric register-offset ABI for the MMHUB 1.8.0 IP block. AMDGPU code includes this header together with `mmhub_1_8_0_sh_mask.h`; the offset header tells the SOC15 register helpers where each register is, while the mask header tells field-setting code how to modify individual bits.

The primary local consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`. That implementation uses these macros through `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET` to bring up MMHUB virtual memory, program GART/page-table state, set VMID context ranges, enable L1/L2 translation caches, configure fault defaults, program invalidation windows, and expose RAS error-status registers.

Because these are compile-time constants, the chunk is part of the hardware contract rather than application logic. If an offset is wrong, the driver can still build cleanly while reading or writing the wrong MMIO register at runtime.

## Important Macro Families

### PCTL0 Tail

The first lines complete the `PCTL0` power/deep-sleep control table for slice 4 and miscellaneous per-slice state:

- `regPCTL0_SLICE4_CFG_DAGB_BUSY`
- `regPCTL0_SLICE4_CFG_DS_ALLOW`
- `regPCTL0_SLICE4_CFG_DS_ALLOW_IB`
- `regPCTL0_UTCL2_MISC`
- `regPCTL0_SLICE0_MISC` through `regPCTL0_SLICE4_MISC`

These offsets are hardware control-plane state for MMHUB power and deep-sleep behavior. This chunk does not contain the code that toggles them; it only defines the addresses available to clock/power-management code.

### L1 TLB Status and Performance Counters

`aid_mmhub_l1tlb_vml1dec` defines status registers for eight L1 TLB slices: `regMC_VM_MX_L1_TLB0_STATUS` through `regMC_VM_MX_L1_TLB7_STATUS`.

`aid_mmhub_l1tlb_vml1pldec` and `aid_mmhub_l1tlb_vml1prdec` define L1 TLB counter programming and result registers:

- Counter config offsets `regMC_VM_MX_L1_PERFCOUNTER0_CFG` through `regMC_VM_MX_L1_PERFCOUNTER3_CFG`.
- Result control `regMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`.
- Low/high result offsets `regMC_VM_MX_L1_PERFCOUNTER_LO` and `regMC_VM_MX_L1_PERFCOUNTER_HI`.

`mmhub_v1_8.c` directly programs `regMC_VM_MX_L1_TLB_CNTL`, which appears later in the shared VM control block, to enable L1 TLB, advanced driver model, system access mode, and ATC. These status and counter windows are the diagnostic/performance side of the same L1 translation front end.

### ATC L2

`aid_mmhub_utcl2_atcl2dec` exposes ATC L2 cache and translation-control state:

- Control/status: `regATC_L2_CNTL`, `regATC_L2_CNTL2`, `regATC_L2_CNTL3`, `regATC_L2_CNTL4`, `regATC_L2_STATUS`, and `regATC_L2_STATUS2`.
- Cache data: `regATC_L2_CACHE_DATA0` through `regATC_L2_CACHE_DATA3`.
- Clock/power: `regATC_L2_MISC_CG`, `regATC_L2_MEM_POWER_LS`, and `regATC_L2_CGTT_CLK_CTRL`.
- DSM controls for 4K, 32K, and 2M pages.
- `regATC_L2_MM_GROUP_RT_CLASSES` for memory-management real-time class grouping.

ATC L2 performance counter blocks later in the chunk define `regATC_L2_PERFCOUNTER_LO/HI`, `regATC_L2_PERFCOUNTER0_CFG`, `regATC_L2_PERFCOUNTER1_CFG`, and `regATC_L2_PERFCOUNTER_RSLT_CNTL`.

### VM L2 Control, Fault Handling, ECC, and EDC

`aid_mmhub_utcl2_vml2pfdec` contains the central VM L2 register offsets used by MMHUB setup:

- Cache controls: `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, `regVM_L2_CNTL4`, `regVM_L2_CNTL5`, status, bank-selection, parity, and clock-gating controls.
- Dummy-page fault registers: `regVM_DUMMY_PAGE_FAULT_CNTL`, `regVM_DUMMY_PAGE_FAULT_ADDR_LO32`, and `regVM_DUMMY_PAGE_FAULT_ADDR_HI32`.
- Protection fault controls/status/default-address registers, including `regVM_L2_PROTECTION_FAULT_CNTL`, `regVM_L2_PROTECTION_FAULT_CNTL2`, `regVM_L2_PROTECTION_FAULT_STATUS`, and the low/high default fault address registers.
- Context 1 identity-aperture low/high address registers and identity physical offset registers.
- ECC/EDC controls and status for VML2 memory, VML2 walker memory, and UTCL2 memory.

`mmhub_v1_8_init_cache_regs()` reads and writes `regVM_L2_CNTL`, `regVM_L2_CNTL2`, `regVM_L2_CNTL3`, and `regVM_L2_CNTL4` to enable L2 cache, force invalidation of L1/L2 translation state, tune bank selection and fragment size, and choose physical request behavior for XGMI-connected CPU or APP APU systems. `mmhub_v1_8_init_system_aperture_regs()` writes the protection-fault default address registers and enables active-page-migration read retry in `regVM_L2_PROTECTION_FAULT_CNTL2`. `mmhub_v1_8_set_fault_enable_default()` toggles a broad set of default fault-handling bits through `regVM_L2_PROTECTION_FAULT_CNTL`.

### VM Context and Invalidation Tables

`aid_mmhub_utcl2_vml2vcdec` is the largest block in the chunk. It contains:

- `regVM_CONTEXT0_CNTL` through `regVM_CONTEXT15_CNTL`.
- `regVM_INVALIDATE_ENG0_SEM`, request, acknowledge, and address-range low/high registers for invalidate engines 0 through 17.
- Per-context page-table base address low/high registers for contexts 0 through 15.
- Per-context page-table start and end address low/high registers for contexts 0 through 15.

`mmhub_v1_8.c` relies on this table being regular. In `mmhub_v1_8_init()`, the driver stores absolute offsets for context 0 page-table base, invalidate request/ack, context control, and protection-fault status/control into `adev->vmhub[AMDGPU_MMHUB0(i)]`. It then computes spacing values from adjacent macros:

- `ctx_distance = regVM_CONTEXT1_CNTL - regVM_CONTEXT0_CNTL`
- `ctx_addr_distance = regVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`
- `eng_distance = regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`
- `eng_addr_distance = regVM_INVALIDATE_ENG1_ADDR_RANGE_LO32 - regVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`

Those distances drive later offset-based register writes. `mmhub_v1_8_setup_vm_pt_regs()` writes the context page-table base for a VMID using `ctx_addr_distance * vmid`. `mmhub_v1_8_setup_vmid_config()` iterates VMIDs 1 through 15, uses `ctx_distance` and `ctx_addr_distance`, enables each context, configures page-table depth/block size, enables fault classes, and sets page-table start/end ranges. `mmhub_v1_8_program_invalidation()` iterates 18 invalidate engines and programs each address range using `eng_addr_distance`.

### Shared VM Aperture and System Addressing Blocks

`aid_mmhub_utcl2_vmsharedpfdec` and `aid_mmhub_utcl2_vmsharedvcdec` define the shared VM address windows used during framebuffer, AGP, GART, and system-aperture setup:

- Host/MMIO apertures: `regMC_VM_NB_MMIOBASE`, `regMC_VM_NB_MMIOLIMIT`, `regMC_VM_NB_TOP_OF_DRAM_SLOT1`, `regMC_VM_NB_LOWER_TOP_OF_DRAM2`, `regMC_VM_NB_UPPER_TOP_OF_DRAM2`, `regMC_VM_NB_TOP_OF_DRAM3`, and related debug/bus/security registers.
- System aperture and default address: `regMC_VM_SYSTEM_APERTURE_LOW_ADDR`, `regMC_VM_SYSTEM_APERTURE_HIGH_ADDR`, `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB`, and `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_MSB`.
- Framebuffer and AGP apertures: `regMC_VM_FB_LOCATION_BASE`, `regMC_VM_FB_LOCATION_TOP`, `regMC_VM_AGP_BASE`, `regMC_VM_AGP_BOT`, and `regMC_VM_AGP_TOP`.
- `regMC_VM_MX_L1_TLB_CNTL`, the L1 TLB control register programmed by `mmhub_v1_8_init_tlb_regs()` and `mmhub_v1_8_disable_l1_tlb()`.

`mmhub_v1_8_get_fb_location()` reads the framebuffer base/top registers and stores the decoded values in `adev->gmc.fb_start` and `adev->gmc.fb_end`. `mmhub_v1_8_init_gart_aperture_regs()` and `mmhub_v1_8_init_system_aperture_regs()` write the GART, framebuffer, AGP, system aperture, and default-page address registers. The code bypasses several direct writes for SR-IOV VFs and can route L1 TLB control through PSP register programming when `amdgpu_sriov_reg_indirect_l1_tlb_cntl()` is true.

### Virtualization, IOMMU, MARC, ATS, and XGMI GPU IOV

`aid_mmhub_utcl2_vmsharedhvdec` provides per-VF and host-virtualization offsets:

- `regMC_VM_FB_SIZE_OFFSET_VF0` through `regMC_VM_FB_SIZE_OFFSET_VF15`.
- `regVM_IOMMU_MMIO_CNTRL_1`, `regVM_IOMMU_CONTROL_REGISTER`, and `regVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`.
- MARC base, relocation, and length low/high registers for entries 0 through 3.
- PCIe ATS control for PF and VFs: `regVM_PCIE_ATS_CNTL` and `regVM_PCIE_ATS_CNTL_VF_0` through `regVM_PCIE_ATS_CNTL_VF_15`.
- `regMC_SHARED_ACTIVE_FCN_ID` and `regMC_VM_XGMI_GPUIOV_ENABLE`.

The immediate `mmhub_v1_8.c` path does not directly write every virtualization register in this chunk, but SR-IOV conditionals around aperture, TLB, cache, and fault programming show that these offsets belong to the same PF/VF execution environment. Mistakes in this range can affect virtual function framebuffer mapping, ATS/IOMMU behavior, or XGMI GPU IOV enablement.

### VM L2 and L2 TLB Performance/Assist Blocks

VM L2 performance counter blocks define eight config registers (`regMC_VM_L2_PERFCOUNTER0_CFG` through `regMC_VM_L2_PERFCOUNTER7_CFG`), result control, and low/high result registers. The L2 TLB blocks define:

- `regL2TLB_TLB0_STATUS`.
- GPUVA/VMID translation assist request and response low/high registers.
- L2 TLB performance counter config/control and result registers.

These offsets are primarily diagnostic and profiling integration points for translation behavior. They are not directly manipulated by the main GART-enable sequence in `mmhub_v1_8.c`, but they expose status that can validate TLB/cache behavior after VM setup.

### MM_CANE RAS/Error Status

The final block, `aid_mmhub_mm_cane_mmcanedec`, defines:

- `regMM_CANE_ICG_CTRL`
- `regMM_CANE_ERR_STATUS`
- `regMM_CANE_UE_ERR_STATUS_LO` and `regMM_CANE_UE_ERR_STATUS_HI`
- `regMM_CANE_CE_ERR_STATUS_LO` and `regMM_CANE_CE_ERR_STATUS_HI`

`mmhub_v1_8.c` uses the CE/UE low/high pairs in `mmhub_v1_8_ce_reg_list[]` and `mmhub_v1_8_ue_reg_list[]` via `AMDGPU_RAS_REG_ENTRY(MMHUB, 0, ...)`. Those tables feed `amdgpu_ras_inst_query_ras_error_count()` and `amdgpu_ras_inst_reset_ras_error_count()` for MMHUB RAS accounting.

## Control Flow

This chunk has no executable control flow. Its practical control-flow impact is through compile-time expansion in MMHUB code:

1. `mmhub_v1_8_init()` records important context, invalidate, and fault register offsets and computes the spacing assumptions used for VMID and invalidate-engine iteration.
2. `mmhub_v1_8_gart_enable()` calls GART aperture setup, system aperture setup, L1 TLB setup, L2 cache setup, snoop override setup, system-domain enablement, identity-aperture disablement, VMID configuration, and invalidation range programming.
3. Those routines write or read offsets from this chunk to establish MMHUB translation behavior across every enabled AID/MMHUB instance in `adev->aid_mask`.
4. Fault handling and RAS paths later use protection-fault and MM_CANE offsets from the same chunk to redirect faults, crash on selected fault classes, query error counts, and reset error counters.

The generated header does not encode sequencing, locking, polling, or timeout policy. Those rules live in `mmhub_v1_8.c`, the SOC15 register access helpers, firmware/PSP-mediated SR-IOV paths, and the hardware specification.

## State and Persistence

The state represented here is hardware MMIO state, not file-backed or heap-backed software state. Important state categories include:

- Translation cache and TLB control/status state in L1 TLB, ATC L2, VM L2, and L2 TLB registers.
- Per-VMID context enablement, page-table base, start, and end ranges.
- Invalidate-engine semaphore, request, acknowledgment, and address-range registers.
- System, framebuffer, AGP, host-MMIO, and default-page apertures.
- Fault default addresses and fault-class handling controls.
- ECC/EDC mode, status, and counter state.
- Virtualization-visible per-VF framebuffer sizing, IOMMU, ATS, MARC, active function, and XGMI GPU IOV state.
- MM_CANE corrected/uncorrected error status latches.

Some registers are durable configuration until reset or reprogramming; others are counters, status windows, request/ack mailboxes, or sticky error latches. The header does not describe reset values or side effects. Callers must use the matching field masks and the documented hardware sequence.

## Dependencies and Integration Points

Key dependencies:

- `mmhub_1_8_0_sh_mask.h` supplies fields used with offsets from this file, such as `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_CONTEXT0_CNTL`, `VM_CONTEXT1_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `MC_VM_FB_LOCATION_BASE`, `MC_VM_FB_LOCATION_TOP`, and `MC_VM_MX_L1_TLB_CNTL`.
- `soc15.h` and `soc15_common.h` provide the `RREG32_SOC15*`, `WREG32_SOC15*`, and `SOC15_REG_OFFSET` accessors that combine IP block, instance, base index, and offset.
- `amdgpu/mmhub_v1_8.c` is the direct generation-matched implementation for this header.
- `amdgpu_ras.h` integration uses `regMM_CANE_*_ERR_STATUS_*` through RAS register-entry macros.
- `amdgpu_psp.h` integration is relevant for SR-IOV indirect L1 TLB control programming through `psp_reg_program_no_ring()`.

Important integration behaviors:

- Multi-instance handling uses `adev->aid_mask` and `for_each_inst()` to repeat MMHUB programming across instances.
- VM hub bookkeeping stores SOC15 absolute offsets in `adev->vmhub[AMDGPU_MMHUB0(i)]`.
- SR-IOV VF checks skip or redirect programming for registers that a VF should not touch directly.
- XGMI/APP APU state affects VM L2 physical request fields, so the same offsets support different memory-coherency behavior depending on platform topology.

## Risks

- Offset drift is silent at compile time. A wrong `reg...` value can target a valid but unrelated MMIO register.
- The context and invalidate tables rely on adjacent offsets being regular. Bad `regVM_CONTEXT1_*`, `regVM_CONTEXT0_*`, `regVM_INVALIDATE_ENG1_*`, or `regVM_INVALIDATE_ENG0_*` values break computed distances and can misprogram every VMID or invalidate engine.
- VM context registers split 64-bit addresses and ranges into low/high 32-bit offsets. Swapping or shifting these offsets can create invalid page-table bases or virtual address ranges.
- Fault-control offsets are safety-sensitive. Misaddressing `regVM_L2_PROTECTION_FAULT_CNTL*` or default fault-address registers can change whether faults are redirected, retried, or escalated.
- Framebuffer, AGP, system aperture, and host-MMIO offsets determine what physical address ranges MMHUB considers valid. Incorrect values can make memory inaccessible or expose the wrong aperture.
- SR-IOV/IOMMU/ATS/MARC/VF offset mistakes can affect only virtualized deployments, which makes regressions harder to catch in bare-metal testing.
- RAS tables use the MM_CANE CE/UE register pairs from this chunk. Wrong low/high pairs can undercount, overcount, or misclassify corrected and uncorrected errors.
- The `*_BASE_IDX` macros are uniformly `0` in this chunk. If the generated base index is wrong for any register, SOC15 accessors can compute the wrong physical address even when the offset value looks correct.

## Test Signals

Useful validation signals for changes touching this header section:

- Build coverage for `amdgpu/mmhub_v1_8.c` with `mmhub_1_8_0_offset.h` and `mmhub_1_8_0_sh_mask.h` included together; undefined macro or field-name mismatches catch generation skew.
- Boot or probe logs on MMHUB 1.8.0 hardware showing successful GART enablement and no MMHUB VM fault flood.
- Functional VM tests that allocate VRAM/GART memory, bind user VMs, and exercise GPUVA translations across VMIDs 0 through 15.
- TLB invalidation tests that update mappings and verify stale translations are not observed after invalidation requests.
- SR-IOV PF/VF smoke tests covering VF framebuffer sizing, indirect L1 TLB control handling, and isolation-sensitive aperture programming.
- RAS query/reset tests for MMHUB that verify `MM_CANE` corrected and uncorrected error registers are readable, counted, and reset through the `mmhub_v1_8_*ras*` paths.
- Counter/debug tests that read L1 TLB, ATC L2, VM L2, and L2 TLB performance counter result registers after configuring their counter controls.

## Summary

Lines 2466-3366 are a generated MMHUB 1.8.0 register map segment. The most important runtime consumers are the MMHUB 1.8 GART/VM initialization paths, which use these offsets to program L1/L2 translation control, VMID contexts, page-table address ranges, system/framebuffer apertures, invalidation engines, fault defaults, and MM_CANE RAS status registers. The code in this chunk is declarative, but it is a high-risk hardware ABI surface because most errors manifest as incorrect MMIO behavior rather than compiler failures.
