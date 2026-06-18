# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h

## Purpose

`mmhub_2_3_0_offset.h` is a generated AMDGPU ASIC register-offset header for MMHUB IP version 2.3.0. It maps symbolic MMHUB register names to 32-bit register offsets and pairs every register macro with a `_BASE_IDX` macro. The file is part of the hardware contract used by the AMDGPU driver to program MMHUB memory-management, address-translation, invalidation, aperture, arbitration, clock-gating, and performance-counter registers.

The header is not executable code. Its primary value is stable register identity: consumers can write `mmMMVM_L2_CNTL`, `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, or `mmMMVM_INVALIDATE_ENG0_REQ` instead of hard-coding offsets such as `0x0700`, `0x0940`, or `0x0a01`. The matching shift/mask and default headers describe fields and reset values, while this file supplies register locations.

## Important APIs, Types, and Constants

This file defines no C functions, structs, enums, or runtime APIs. Its public interface is the set of C preprocessor constants protected by `_mmhub_2_3_0_OFFSET_HEADER`.

Important macro conventions:

- `mm<REGISTER>`: the register offset within the MMHUB register space.
- `mm<REGISTER>_BASE_IDX`: the SOC15 register base-index selector used by AMDGPU register access macros. All entries in this header use base index `1`.
- Address block comments: generated `// addressBlock:` and `// base address:` comments preserve the hardware block grouping and physical block base used to derive the relative offsets.

The header contains 2,326 `#define mm...` entries, including both register offsets and `_BASE_IDX` companions. Major register families include:

- `mmDAGB0_*`: DAGB read/write client slots, request/return controls, TLB/data credit controls, pending-status registers, clock-gating controls, FIFO/credit fullness state, performance counters, and reserved registers.
- `mmMMEA0_*`: memory endpoint arbitration for DRAM and IO paths, client/group/VC mapping, priority policy, address normalization, DRAM address decoding, hashing, harvesting, SDP arbitration, DSM/EDC status, clock controls, and always-on misc state.
- `mmPCTL*_*`: MMHUB power-control, deep-sleep, FSM/debug state, register-engine RAM access, state-save ranges, save-exclusion sets, status, and PCTL performance counters.
- `mmMMMC_VM_MX_L1_*`: L1 TLB status, L1 performance-counter configuration/result registers, and TLS0 control/start/end/status/fault-address ranges.
- `mmMM_ATC_L2_*`: ATC L2 controls, debug/cache data, status, clock-gating, memory power, SDP port control, and ATC L2 performance counters.
- `mmMMVM_L2_*`: MMVM L2 cache control, invalidation, dummy-page and protection-fault handling, identity aperture registers, cache parity, IH logging, clock gating, GCR, and PTE cache dump controls.
- `mmMMVM_CONTEXT[0-15]_*`: VM context control and per-context PTE cache fragment-size registers.
- `mmMMVM_CONTEXT[0-15]_PAGE_TABLE_*`: page-table base, start, end, and reserve registers for all 16 contexts.
- `mmMMVM_INVALIDATE_ENG[0-17]_*`: invalidation engine semaphore, request, acknowledgment, address range, and reserve registers for all 18 invalidation engines.
- `mmMMMC_VM_FB_SIZE_OFFSET_VF[0-31]` and `mmMMVM_PCIE_ATS_CNTL_VF_[0-31]`: SR-IOV/virtual-function framebuffer sizing and ATS-control registers.
- Shared aperture and system registers such as `mmMMMC_VM_FB_LOCATION_BASE`, `mmMMMC_VM_FB_LOCATION_TOP`, `mmMMMC_VM_AGP_*`, `mmMMMC_VM_SYSTEM_APERTURE_*`, `mmMMMC_VM_NB_*`, `mmMMMC_VM_LOCAL_MEM_*`, and `mmMMMC_VM_MX_L1_TLB_CNTL`.

## Address Block Inventory

| Address block | Base address | Macro entries | Register span |
| --- | ---: | ---: | --- |
| `mmhub_dagbdec` | `0x68000` | 342 | `mmDAGB0_RDCLI0` to `mmDAGB0_RESERVE9_BASE_IDX` |
| `mmhub_mmea_mmeadec0` | `0x68400` | 382 | `mmMMEA0_DRAM_RD_CLI2GRP_MAP0` to `mmMMEA0_MISC_AON_BASE_IDX` |
| `mmhub_pctldec` | `0x68e00` | 116 | `mmPCTL_CTRL` to `mmPCTL_RESERVED_3_BASE_IDX` |
| `mmhub_l1tlb_mmutcl1pfdec` | `0x69600` | 16 | `mmMMMC_VM_MX_L1_TLB0_STATUS` to `mmMMMC_VM_MX_L1_TLB7_STATUS_BASE_IDX` |
| `mmhub_l1tlb_mmutcl1pldec` | `0x69670` | 10 | `mmMMMC_VM_MX_L1_PERFCOUNTER0_CFG` to `mmMMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL_BASE_IDX` |
| `mmhub_l1tlb_mmutcl1prdec` | `0x69690` | 4 | `mmMMMC_VM_MX_L1_PERFCOUNTER_LO` to `mmMMMC_VM_MX_L1_PERFCOUNTER_HI_BASE_IDX` |
| `mmhub_l1tlb_mmvmtlspfdec` | `0x696c0` | 432 | `mmMMMC_VM_MX_L1_TLS0_CNTL` to `mmMMMC_VM_MX_L1_TLS0_IOMMU_FAULT_GVADDR_HI32_BASE_IDX` |
| `mmhub_mmutcl2_mmatcl2dec` | `0x69b00` | 30 | `mmMM_ATC_L2_CNTL` to `mmMM_ATC_L2_SDPPORT_CTRL_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2pfdec` | `0x69c00` | 72 | `mmMMVM_L2_CNTL` to `mmMMVM_L2_PTE_CACHE_DUMP_READ_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2vcdec` | `0x69d00` | 68 | `mmMMVM_CONTEXT0_CNTL` to `mmMMVM_L2_CONTEXT15_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2pldec` | `0x6a090` | 28 | `mmMMMC_VM_L2_PERFCOUNTER0_CFG` to `mmMMUTCL2_PERFCOUNTER_RSLT_CNTL_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2prdec` | `0x6a0e0` | 8 | `mmMMMC_VM_L2_PERFCOUNTER_LO` to `mmMMUTCL2_PERFCOUNTER_HI_BASE_IDX` |
| `mmhub_mmutcl2_mmvmsharedhvdec` | `0x6a130` | 184 | `mmMMMC_VM_FB_SIZE_OFFSET_VF0` to `mmMMVM_PCIE_ATS_CNTL_VF_31_BASE_IDX` |
| `mmhub_mmutcl2_mmvmsharedpfdec` | `0x6a340` | 48 | `mmMMMC_VM_NB_MMIOBASE` to `mmMMUTCL2_HARVEST_BYPASS_GROUPS_BASE_IDX` |
| `mmhub_mmutcl2_mmvmsharedvcdec` | `0x6a3b0` | 16 | `mmMMMC_VM_FB_LOCATION_BASE` to `mmMMMC_VM_MX_L1_TLB_CNTL_BASE_IDX` |
| `mmhub_mmutcl2_mmatcl2pfcntrdec` | `0x6a400` | 4 | `mmMM_ATC_L2_PERFCOUNTER_LO` to `mmMM_ATC_L2_PERFCOUNTER_HI_BASE_IDX` |
| `mmhub_mmutcl2_mmatcl2pfcntldec` | `0x6a420` | 6 | `mmMM_ATC_L2_PERFCOUNTER0_CFG` to `mmMM_ATC_L2_PERFCOUNTER_RSLT_CNTL_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2ptdec` | `0x6a500` | 256 | `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` to `mmMMVM_CONTEXT15_PAGE_TABLE_RESERVE1_BASE_IDX` |
| `mmhub_mmutcl2_mmvml2indec` | `0x6a800` | 288 | `mmMMVM_INVALIDATE_ENG0_SEM` to `mmMMVM_INVALIDATE_ENG17_RESERVE2_BASE_IDX` |
| `mmhub_mmutcl2_mml2tlbpfdec` | `0x6aa90` | 2 | `mmMML2TLB_TLB0_STATUS` to `mmMML2TLB_TLB0_STATUS_BASE_IDX` |
| `mmhub_mmutcl2_mml2tlbpldec` | `0x6ab00` | 10 | `mmMML2TLB_PERFCOUNTER0_CFG` to `mmMML2TLB_PERFCOUNTER_RSLT_CNTL_BASE_IDX` |
| `mmhub_mmutcl2_mml2tlbprdec` | `0x6ab20` | 4 | `mmMML2TLB_PERFCOUNTER_LO` to `mmMML2TLB_PERFCOUNTER_HI_BASE_IDX` |

## Control Flow

There is no direct runtime control flow in this header. All control flow is in consumers that use these constants with SOC15 register accessors.

The main consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`, which includes this file with `mmhub_2_3_0_sh_mask.h` and `mmhub_2_3_0_default.h`. Important consumer paths are:

- `mmhub_v2_3_init()` converts selected offset macros into absolute SOC15 register offsets stored in `adev->vmhub[AMDGPU_MMHUB0(0)]`. It also computes `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` by subtracting adjacent offset macros such as `mmMMVM_CONTEXT1_CNTL - mmMMVM_CONTEXT0_CNTL` and `mmMMVM_INVALIDATE_ENG1_REQ - mmMMVM_INVALIDATE_ENG0_REQ`.
- `mmhub_v2_3_gart_enable()` sequences MMHUB setup: SR-IOV framebuffer-location registers, GART page-table base and aperture, system aperture/default page, L1 TLB, L2 cache, system-domain context, identity-aperture disablement, VMID configuration, and invalidation-engine address ranges.
- `mmhub_v2_3_setup_vm_pt_regs()` uses the context page-table base offset plus `ctx_addr_distance * vmid` to program VMID-specific page-table base registers.
- `mmhub_v2_3_setup_vmid_config()` walks VM contexts 1 through 15 using the context-control and page-table address stride encoded by this header.
- `mmhub_v2_3_program_invalidation()` walks 18 invalidation engines using `mmMMVM_INVALIDATE_ENG0_ADDR_RANGE_*` and `eng_addr_distance`.
- `mmhub_v2_3_set_fault_enable_default()` updates `mmMMVM_L2_PROTECTION_FAULT_CNTL` fields for default-page redirection and crash-on-fault policy.
- `mmhub_v2_3_update_medium_grain_clock_gating()` and `mmhub_v2_3_update_medium_grain_light_sleep()` read and write `mmMM_ATC_L2_CGTT_CLK_CTRL`, `mmDAGB0_CNTL_MISC2`, `mmDAGB0_WR_CGTT_CLK_CTRL`, and `mmDAGB0_RD_CGTT_CLK_CTRL`.

The display stack also includes this header in `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` together with the matching shift/mask header. That inclusion makes MMHUB 2.3.0 register identifiers available to DCN 3.1 resource code and display-side VM helpers, even though the heavy MMHUB programming flow lives in the AMDGPU core driver.

## State and Persistence Behavior

The header has no mutable software state and persists nothing at runtime. Its constants are compiled into driver code and become part of the driver/hardware ABI for MMHUB 2.3.0 register programming.

Runtime state affected through these offsets lives in hardware registers and AMDGPU device structures:

- `adev->vmhub[AMDGPU_MMHUB0(0)]` stores absolute register offsets and register-spacing metadata derived from this header.
- `adev->gmc` supplies GART, VRAM, AGP, framebuffer, and translation configuration written through MMHUB aperture and page-table registers.
- `adev->vm_manager` supplies VM level, block size, and maximum PFN values used when programming contexts 1 through 15.
- MMHUB hardware registers hold TLB/cache enablement, page-table bounds, invalidation-engine ranges, protection-fault policy, clock-gating overrides, and performance-counter setup until reset, suspend/resume reinitialization, GPU reset, or power-management transitions require reprogramming.

Persistence boundaries are hardware-oriented:

- GPU reset or power-state transitions can clear MMHUB registers back to hardware defaults, requiring the driver to replay the initialization sequence.
- PCTL register-save ranges and exclusion sets indicate hardware-managed save/restore areas, but this offset header only names those registers.
- SR-IOV virtual functions have different access constraints; `mmhub_v2_3_gart_enable()` explicitly programs VF framebuffer-location copy registers, while other clock-gating paths skip work for VFs.

## Dependencies

Direct dependencies are minimal:

- C preprocessor support for include guards and `#define` constants.
- Consumers that follow AMDGPU/SOC15 register naming conventions.

Functional use depends on sibling generated headers for the same IP revision:

- `mmhub_2_3_0_sh_mask.h` provides bit-field shift and mask constants used by `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- `mmhub_2_3_0_default.h` provides hardware default values such as `mmMMVM_L2_CNTL3_DEFAULT`, `mmMMVM_L2_CNTL4_DEFAULT`, and `mmMMVM_L2_CNTL5_DEFAULT`.

Runtime consumers depend on AMDGPU infrastructure:

- SOC15 access macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.
- Register field helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- AMDGPU memory-management structures including `struct amdgpu_device`, `struct amdgpu_vmhub`, GMC state, GART backing objects, VM manager state, and SR-IOV helpers.
- IP-version dispatch in `gmc_v10_0.c`, which selects `mmhub_v2_3_funcs` for MMHUB IP version 2.3.0.

## Integration Points

The principal integration point is `amdgpu/mmhub_v2_3.c`, which registers `mmhub_v2_3_funcs` with callbacks for MMHUB initialization, GART enable/disable, fault-default policy, clock gating, and page-table register setup. The header supplies the raw offsets those callbacks pass to SOC15 accessors.

High-value integration assumptions include:

- Context-control registers are adjacent from `mmMMVM_CONTEXT0_CNTL` through `mmMMVM_CONTEXT15_CNTL`, allowing stride-based offset access.
- Context page-table register groups are regularly spaced from context 0 through context 15, allowing `ctx_addr_distance` to address each VMID.
- Invalidation-engine groups are regularly spaced from engine 0 through engine 17, allowing `eng_distance` and `eng_addr_distance` to address all engines.
- All `_BASE_IDX` values are `1`, matching the MMHUB register base selected by SOC15 accessors for this IP block.
- The offsets match the field definitions in `mmhub_2_3_0_sh_mask.h`; field helpers are unsafe if an offset header is paired with a mismatched shift/mask header.

The file is structurally aligned with other generated MMHUB offset headers for different IP revisions. It should only be used by code paths that target MMHUB 2.3.0 hardware, because same-looking macro families can move, grow, shrink, or change field semantics between hardware revisions.

## Risks and Edge Cases

- Hardware revision mismatch: using this header for a non-2.3.0 MMHUB revision can write the wrong registers while still compiling cleanly.
- Header pairing mismatch: combining this offset header with another IP revision's shift/mask or default header can produce valid C that programs invalid fields.
- Untyped constants: the compiler cannot prove that a `mm...` offset is used with the correct block, base index, or field macro.
- Stride assumptions: `mmhub_v2_3_init()` derives context and invalidation-engine distances from adjacent macros. Any generated-register-layout change that breaks regular spacing would corrupt offset arithmetic for VMID setup or invalidation programming.
- Address split handling: many programmed addresses are split across low/high 32-bit registers after hardware-specific shifts. Incorrect use of offsets around page-table base, aperture, default-page, and protection-fault registers can point translation hardware at the wrong physical page.
- SR-IOV constraints: VF-specific registers are present in the map, but not every MMHUB register is safe or accessible from VF mode. Consumers need the same VF guards used in `mmhub_v2_3.c`.
- Reserved and status registers: the header names reserve and status locations as offsets, but naming them does not make writes safe. Code should avoid programming reserved ranges without hardware guidance.
- Fault policy sensitivity: offsets for `MMVM_L2_PROTECTION_FAULT_*` and `MMVM_CONTEXT*_CNTL` control whether faults interrupt, redirect, retry, or crash. Offset mistakes here can cause fault storms, hidden page redirection, or GPU hangs.
- Power-management sensitivity: clock-gating and light-sleep offsets are used during runtime power transitions. Wrong offsets can cause resume failures or intermittent MMHUB/ATC stalls.

## Test Signals

Useful validation signals for changes touching this header or consumers include:

- AMDGPU build coverage with MMHUB v2.3 support enabled; missing or renamed macros should fail in `mmhub_v2_3.c` or display resource code.
- Boot/module-load testing on MMHUB 2.3.0 hardware with successful GART enablement and no register-access warnings.
- GPU VM workloads that exercise GART mappings, VMID context setup, page-table base updates, aperture bounds, invalidation requests, and TLB/L2 cache behavior.
- VM fault tests that trigger `MMVM_L2_PROTECTION_FAULT_STATUS` reporting and confirm sane client IDs, fault classes, and default-page/crash policy.
- Suspend/resume, GPU reset, and runtime power-management testing, especially with `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`.
- SR-IOV PF/VF testing that verifies VF framebuffer-location programming and skips inaccessible MMHUB clock-gating work.
- Register readback or hardware tracing that confirms computed strides for contexts and invalidation engines match the hardware layout.
- Display bring-up on DCN 3.1 paths that include this MMHUB header, checking for display VM helper regressions or build-time header conflicts.

## Summary

`mmhub_2_3_0_offset.h` is a generated register-map contract for AMD MMHUB 2.3.0. It exposes no runtime logic, but it is central to MMHUB initialization because the AMDGPU driver uses its offsets to program GART, VM contexts, L1/L2 translation, protection-fault handling, invalidation engines, apertures, virtualization registers, performance counters, and clock-gating controls. The main maintenance risk is silent hardware-contract drift: offsets, base indices, shift/mask fields, defaults, and consumer stride assumptions must remain synchronized for the exact MMHUB IP revision.
