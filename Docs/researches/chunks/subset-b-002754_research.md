# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 9529-10249

## Scope And Purpose

This chunk is the tail of the MMHUB 1.0 shader/register mask header. It is a generated-style hardware contract file: every exported symbol is a preprocessor macro that gives the bit shift or mask for a field inside a 32-bit MMHUB register. There are no functions, structs, variables, control-flow statements, or runtime decisions in this range.

The line range covers the final VM and shared MMHUB register groups:

- `VM_CONTEXT3_PAGE_TABLE_END_ADDR_*` through `VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, plus the tail of context 2 at the first two lines, describing low 32-bit and high 4-bit logical page-number fields for VMID page-table end addresses.
- `MC_VM_L2_PERFCOUNTER*`, defining eight MMHUB VM L2 performance counter selectors plus shared result/control and low/high counter read fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`, defining per-SR-IOV-virtual-function framebuffer size and offset packing.
- Shared VM aperture, ATS, clock, reset, memory power, cacheable-DRAM, APT, local-HBM, FB/AGP, system-aperture, and L1 TLB control fields.
- `ATC_L2_PERFCOUNTER*`, defining ATC L2 performance counter selector/result fields.
- `MMEA0_EDC_CNT*_VG20` and `MMEA1_EDC_CNT*_VG20`, defining Vega20 MMHUB memory error-detection counter fields for RAS.
- `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`, defining xGMI local framebuffer region and segment-size fields.

The source header is paired with `mmhub_1_0_offset.h`, where the corresponding `mm*` register offsets live. Consumers combine the address macro, mask/shift macro, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD` to read, modify, or decode MMIO registers without open-coded bit arithmetic.

## Important APIs, Types, And Constants

This chunk exports constants rather than C APIs or types. The important macro families are:

- `VM_CONTEXTn_PAGE_TABLE_END_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32_{MASK,__SHIFT}` and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4_{MASK,__SHIFT}` for contexts 3 through 15. The low half is full 32 bits and the high half uses bits 3:0, matching driver code that writes page frame numbers as `lower_32_bits(max_pfn - 1)` and `upper_32_bits(max_pfn - 1)` or as address shifts by 12 and 44.
- `MC_VM_L2_PERFCOUNTER[0-7]_CFG__*` with `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`. These configure MMHUB VM L2 performance event selection and counter behavior. `MC_VM_L2_PERFCOUNTER_RSLT_CNTL__*` selects a counter, starts/stops trigger windows, enables any counter, clears all counters, and optionally stops on saturation. `MC_VM_L2_PERFCOUNTER_{LO,HI}` provides the readout fields, with `HI` split between `COUNTER_HI` and `COMPARE_VALUE`.
- `MC_VM_FB_SIZE_OFFSET_VF[0-15]__VF_FB_SIZE` and `__VF_FB_OFFSET`, each packed into lower and upper 16-bit halves. These are the per-VF framebuffer aperture description fields used by SR-IOV-oriented MMHUB hardware.
- `VM_IOMMU_MMIO_CNTRL_1__IOMMU_MMIO_EN`, the MARC base/relocation/length fields (`MC_VM_MARC_*_[0-3]`), `VM_IOMMU_*`, and `VM_PCIE_ATS_CNTL*`. These define IOMMU, MMIO, memory aperture relocation, and PCIe Address Translation Service bits for physical and virtual functions.
- `UTCL2_CGTT_CLK_CTRL__SOFT_OVERRIDE*`, `MC_SHARED_VIRT_RESET_REQ__VIRT_RESET_REQ`, `MC_MEM_POWER_LS__*`, `MC_VM_CACHEABLE_DRAM_ADDRESS_{START,END}`, `MC_VM_APT_CNTL__*`, `MC_VM_LOCAL_HBM_ADDRESS_*`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK`. These provide clock override, virtualization reset, memory light-sleep, cacheable-address, address-translation/protection table, and local HBM control fields.
- `MC_VM_FB_LOCATION_{BASE,TOP}`, `MC_VM_AGP_{TOP,BOT,BASE}`, `MC_VM_SYSTEM_APERTURE_{LOW,HIGH}_ADDR`, and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_{LSB,MSB}`. These define framebuffer, AGP, and system aperture boundaries consumed by MMHUB GART setup paths.
- `MC_VM_MX_L1_TLB_CNTL__ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `ECO_BITS`, `MTYPE`, and `ATC_EN`. These fields are actively used when enabling or disabling the MMHUB L1 TLB.
- `ATC_L2_PERFCOUNTER[0-1]_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, and `ATC_L2_PERFCOUNTER_{LO,HI}` mirror the VM L2 perf-counter shape for the ATC L2 block.
- `MMEA0_EDC_CNT_VG20`, `MMEA0_EDC_CNT2_VG20`, `MMEA1_EDC_CNT_VG20`, and `MMEA1_EDC_CNT2_VG20` define 2-bit SEC/DED or SED counter fields for command, data, page, tag, GMI, and MAM memories. The `_VG20` suffix is significant: `mmhub_v1_0.c` uses these for Vega20-style MMHUB RAS field tables.
- `MC_VM_XGMI_LFB_CNTL__PF_LFB_REGION`, `MC_VM_XGMI_LFB_CNTL__PF_MAX_REGION`, and `MC_VM_XGMI_LFB_SIZE__PF_LFB_SIZE` describe xGMI physical function region ID, maximum region, and local framebuffer segment size.

## Control Flow And State Behavior

There is no local control flow. Inclusion makes the constants available at compile time, and runtime behavior is entirely in consumer code.

For page table bounds, `mmhub_v1_0_init_gart_aperture_regs()` writes VMID0 start/end registers from `adev->gmc.gart_start` and `adev->gmc.gart_end`. `mmhub_v1_0_setup_vmid_config()` iterates VMIDs 1 through 15 by using `hub->ctx_addr_distance`; it writes page-table start to zero and page-table end to `adev->vm_manager.max_pfn - 1`. The macros in this chunk describe the corresponding register bit layout, while the writes themselves use the paired offset macros.

For TLB control, `mmhub_v1_0_init_tlb_regs()` reads `mmMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `MTYPE`, and `ATC_EN`, then writes the register back. `mmhub_v1_0_gart_disable()` clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`. Those read-modify-write paths rely on these masks to preserve unrelated hardware bits.

For apertures, `mmhub_v1_0_get_fb_location()` reads `MC_VM_FB_LOCATION_BASE/TOP` and decodes `FB_BASE`/`FB_TOP` into `adev->gmc.fb_start` and `adev->gmc.fb_end` by shifting by 24. `mmhub_v1_0_init_system_aperture_regs()` writes AGP/system/default-address registers from `adev->gmc` state and scratch/dummy-page addresses; on several APUs it extends `MC_VM_SYSTEM_APERTURE_HIGH_ADDR` as a hardware workaround. SR-IOV VFs return early from part of this path, while `mmhub_v1_0_gart_enable()` explicitly programs VF copy `MC_VM_FB_LOCATION_BASE/TOP` registers before enabling GART.

For xGMI, display code calls `REG_GET(MC_VM_XGMI_LFB_CNTL, PF_MAX_REGION, &pf_max_region)` and treats zero as disabled. GFX hub code reads `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`, derives `num_physical_nodes` from `PF_MAX_REGION + 1`, derives `physical_node_id` from `PF_LFB_REGION`, and shifts `PF_LFB_SIZE` by 24 to compute the node segment size.

For RAS, `mmhub_v1_0.c` builds `soc15_ras_field_entry` tables from the `MMEA[01]_EDC_CNT*_VG20` masks and shifts. `mmhub_v1_0_query_ras_error_count()` reads the EDC counter registers, decodes SEC/DED counts with those fields, accumulates corrected and uncorrected error counts, and logs nonzero subblock counts. `mmhub_v1_0_reset_ras_error_count()` resets those counters by reading them back when MMHUB RAS is supported.

The persistent state is hardware state, not C storage in this header. Some fields are configuration state written during GART/MMHUB initialization, disable, SR-IOV setup, display xGMI probing, or power-management setup. Others are observational counters or status fields read from hardware. Their lifetime follows GPU reset, power gating, virtualization ownership, and firmware/BIOS programming rules.

## Dependencies And Integration Points

The immediate dependencies are:

- `mmhub_1_0_offset.h` for register addresses such as `mmVM_CONTEXT*_PAGE_TABLE_END_ADDR_*`, `mmMC_VM_MX_L1_TLB_CNTL`, `mmMMEA0_EDC_CNT_VG20`, and `mmMC_VM_XGMI_LFB_CNTL`.
- AMDGPU register helper macros from the SOC15 infrastructure, especially `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_ENTRY`, and `SOC15_REG_FIELD`.
- `amdgpu_device` state, including `adev->gmc`, `adev->vm_manager`, `adev->vmhub`, `adev->gmc.xgmi`, `adev->mem_scratch`, SR-IOV state, RAS support state, and APU hardware flags.

Important integration points visible in this source tree:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c` includes this header directly and consumes page-table end registers, aperture fields, `MC_VM_MX_L1_TLB_CNTL`, framebuffer location fields, and `MMEA[01]_EDC_CNT*_VG20` RAS fields.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c` uses the same field names for newer MMHUB instances with multiple AIDs and PSP-mediated SR-IOV programming, which makes this header part of a broader family of similarly shaped MMHUB register contracts.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c` and `gfxhub_v1_2.c` use `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` field names when deriving xGMI topology.
- `drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c` and `dce/dce_hwseq.h` expose `MC_VM_XGMI_LFB_CNTL` through display register tables and use `PF_MAX_REGION` as the xGMI-enabled signal.
- `amdgpu_gmc.h` carries mode2 save/restore slots for `VM_CONTEXT_PAGE_TABLE_END_ADDR_*` and `MC_VM_MX_L1_TLB_CNTL`, so values described by this chunk can be preserved by higher-level GMC reset/resume flows.

## Risks And Edge Cases

- The constants must exactly match the MMHUB 1.0 hardware spec. A one-bit mask or shift drift can silently set reserved bits, truncate a page-table end address, misconfigure TLB behavior, misreport xGMI topology, or undercount/overcount RAS errors.
- Page-table end address fields are split as 32 low bits plus 4 high bits. Consumers must pass page-frame/logical-page numbers, not raw byte addresses, and must use the expected 12/44-bit shifts or `lower_32_bits`/`upper_32_bits` PFN split. Mixing byte-address and page-number units can produce broad VM aperture faults.
- `REG_SET_FIELD` depends on exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming. Renaming or using the wrong register prefix breaks compile-time expansion or, worse, selects fields from another ASIC register namespace if a compatible name exists.
- Several register groups are repeated for 16 VM contexts or 16 VFs. Table or offset-distance consumers must maintain the same stride assumptions as `mmhub_1_0_offset.h`; manual edits to one repeated macro but not its siblings are high risk.
- Some fields are full-width masks (`0xFFFFFFFFL`) and many masks use an `L` suffix. Consumers should keep arithmetic in unsigned 32-bit or explicitly widened unsigned types to avoid sign-extension and formatting surprises.
- `MC_VM_XGMI_LFB_CNTL` differs for Aldebaran-specific code in `gfxhub_v1_1.c`, which carries local `_ALDE` field definitions with wider masks. Reusing MMHUB 1.0 `PF_*` widths on a different ASIC can misdecode node IDs or segment counts.
- RAS EDC counter fields are 2-bit packed counters. They can saturate or reset-on-read depending on hardware behavior; `mmhub_v1_0_reset_ras_error_count()` relies on readback to clear. Poll cadence and read ordering matter when interpreting field values.
- SR-IOV and PF/VF ownership matters. Some MMHUB registers are skipped in VF mode, some are VF copy registers, and some newer paths use PSP-mediated writes. Direct writes to shared PF-owned fields from the wrong context can be ineffective or unsafe.
- The chunk ends with the header guard `#endif`. Any generated merge, extraction, or regeneration must preserve it or every include of `mmhub_1_0_sh_mask.h` will fail.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are integration-oriented:

- Compile AMDGPU and display code that includes `mmhub_1_0_sh_mask.h`, especially `mmhub_v1_0.c`, `gfxhub_v1_1.c`, and DCE hardware sequencer code that consumes `MC_VM_XGMI_LFB_CNTL`.
- Static consistency checks: for each mask/shift pair, `(mask >> shift)` should be a dense field of the expected width; full-width fields should have shift zero; repeated VM context and VF macros should preserve identical layouts.
- GART bring-up tests on MMHUB 1.0 hardware: VMID0 and VMID1-15 page-table end programming should not produce VM faults under normal GART and user-VM traffic.
- Suspend/resume, mode2 reset, and GPU reset tests should verify `MC_VM_MX_L1_TLB_CNTL` and VM context page-table end values are restored consistently.
- SR-IOV VF smoke tests should verify framebuffer location and VF aperture behavior, with no invalid MMHUB register access warnings.
- xGMI topology tests on Vega20/Arcturus-class systems should confirm `PF_MAX_REGION`, `PF_LFB_REGION`, and `PF_LFB_SIZE` decode to the expected physical node count, node ID, and segment size.
- RAS injection or hardware error-counter tests should verify `MMEA0/1` SEC/DED/SED fields map to the intended subblock names and that readback reset behavior clears counters as expected.
- Perf-counter validation can manually program `MC_VM_L2_PERFCOUNTER*` and `ATC_L2_PERFCOUNTER*` selector/control fields, collect low/high reads, and confirm counter selection, clear, enable, trigger, and saturation behavior.

## Chunk Notes For Merge Lane

This is the final chunk of `mmhub_1_0_sh_mask.h`, not a standalone implementation. Whole-file research should merge it as the MMHUB 1.0 tail section that completes VM context page-table end masks and supplies performance counter, SR-IOV framebuffer, shared aperture, TLB, RAS EDC, and xGMI LFB field definitions. The header is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/mmhub/` and should be interpreted alongside `mmhub_1_0_offset.h` and `mmhub_v1_0.c`.
