# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_0_0_offset.h

## Purpose
This generated-style header defines the SOC15 register offsets for ATHUB hardware version 2.0.0. ATHUB is the Address Translation Hub used by the AMDGPU memory-management and KFD paths for ATS/ATC control, VMID-to-PASID mapping, PCIe ATS/PASID/page-request controls, XPB routing, and RPB queue/performance registers.

The file is not executable code. Its value is the stable set of `mm...` offset macros and matching `..._BASE_IDX` macros consumed by register-access helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, and `WREG32_SOC15()`.

## Important APIs, types, and functions
There are no functions, structs, or enums in this header. The exported interface is the macro namespace:

- `mmATC_*` registers cover ATS control/status/fault reporting, ATC performance counters, VMID status, and VMID-to-PASID mapping.
- `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID31_PASID_MAPPING` define a contiguous mapping table. Callers rely on this contiguity by adding `vmid` to the VMID0 offset.
- `mmATHUB_MISC_CNTL`, `mmATHUB_MEM_POWER_LS`, and related ATHUB control registers are used by the ATHUB power-management code.
- `mmATHUB_PCIE_ATS_CNTL`, `mmATHUB_PCIE_PASID_CNTL`, `mmATHUB_PCIE_PAGE_REQ_CNTL`, `mmATHUB_PCIE_OUTSTAND_PAGE_REQ_ALLOC`, and `mmATHUB_PCIE_ATS_CNTL_VF_0` through `_VF_30` describe host and SR-IOV VF-facing PCIe translation controls.
- `mmXPB_*` registers describe the XPB decoder block, including source apertures, destination maps, peer/P2P BARs, clock gating, status, sticky status, and unit-ID mapping.
- `mmRPB_*` registers describe the RPB decoder block, including arbitration, BIF controls, read/write queues, ATS controls, SDP port controls, and performance counters.

Every register has a paired `*_BASE_IDX`, and every paired value in this file is `0`. SOC15 accessors combine these offsets with the ATHUB IP base table from ASIC-specific `*_ip_offset.h` files.

## Register Layout
The file is divided into three address blocks:

- `athub_atsdec`, base address `0x3000`, offset range `0x0000` through `0x0062`. This block contains ATS/ATC control, fault, VMID/PASID, PCIe ATS, interrupt-credit, virtualization reset, and snapshot/status registers.
- `athub_xpbdec`, base address `0x3190`, offset range `0x0064` through `0x00ce`. This block contains XPB routing aperture/destination maps, XDMA routing, P2P and peer BAR setup, clock-gating/status controls, match/mask registers, and GFX/MM/GUS unit-ID mappings.
- `athub_rpbdec`, base address `0x3350`, offset range `0x00d4` through `0x00fa`. This block contains RPB pass-through/block/tag configuration, arbitration and BIF controls, queue controls, ATS controls, SDP port controls, and RPB performance counters.

There are intentional gaps in the numeric offsets, for example between `mmATC_ATS_SDPPORT_CNTL` and the VMID snapshot registers, between `mmXPB_P2P_BAR_SETUP` and delta registers, and between the XPB and RPB blocks. These gaps reflect hardware register layout and must not be compacted.

## Control Flow
The header itself has no control flow. It affects runtime behavior when included by C files that calculate register addresses:

- `amdgpu/athub_v2_0.c` reads and writes `mmATHUB_MISC_CNTL` to report or update ATHUB medium-grain clock gating and light sleep. The offset macros select the hardware register; the bit masks come from `athub_2_0_0_sh_mask.h`.
- `amdgpu/gmc_v10_0.c` uses `SOC15_REG_OFFSET(ATHUB, 0, mmATC_VMID0_PASID_MAPPING) + vmid` to read VMID-to-PASID mappings when handling GPU memory-management state.
- `amdgpu/amdgpu_amdkfd_gfx_v10.c` writes the same contiguous VMID mapping table when assigning KFD PASIDs to VMIDs, and also updates IH lookup state in OSSSYS.

The normal access pattern is: include this offset header, include the matching shift/mask header, compute the SOC15 register address from `ATHUB` instance `0` plus an `mm...` offset, then read or write the register using AMDGPU register helpers.

## State and Persistence Behavior
This file persists no software state. The defined offsets address volatile hardware registers whose contents are controlled by ASIC reset state, firmware, driver initialization, runtime power management, SR-IOV state, and active GPU workloads.

Runtime state impacted through these offsets includes VMID/PASID mappings, ATS enablement/status, fault capture registers, performance counters, clock-gating and light-sleep bits, XPB routing tables, P2P/peer BAR configuration, sticky status, and RPB queue/arbitration state. Persistence across suspend/resume or GPU reset depends on higher-level AMDGPU reinitialization paths reprogramming hardware, not on this header.

## Dependencies
This header depends only on preprocessor inclusion and its include guard. Practical consumers depend on:

- Matching ATHUB 2.0.0 mask and default headers: `athub_2_0_0_sh_mask.h` and `athub_2_0_0_default.h`.
- SOC15 register access infrastructure in `soc15_common.h` and related AMDGPU headers.
- ASIC-specific ATHUB base-address definitions such as `sienna_cichlid_ip_offset.h`, `aldebaran_ip_offset.h`, or other IP offset tables selected by the build.
- AMDGPU and KFD memory-management code that interprets VMID, PASID, ATS, and page-fault state.

## Integration Points
The direct include sites found in this tree are:

- `drivers/gpu/drm/amd/amdgpu/athub_v2_0.c` for ATHUB v2.0 clock-gating and light-sleep control.
- `drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c` for GFX10 memory-controller and VM fault/PASID integration.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c` for KFD GFX10 queue and PASID/VMID programming.

The header also sits beside other ATHUB generation files for 1.x, 2.1, 3.x, and 4.1 layouts. Cross-version code must include the offset header that matches the selected IP version because similar register names can move; for example ATHUB 2.1.0 has different early offsets for shared virtualization reset and ATC control.

## Risks and Edge Cases
Incorrect offsets are high impact: a read or write through an `mm...` macro can target the wrong register and corrupt address translation, PASID assignment, power state, routing, or performance-counter state.

The VMID/PASID mapping table is especially sensitive because callers add `vmid` to `mmATC_VMID0_PASID_MAPPING`. Any future hardware layout that breaks contiguity would require call-site changes, not just header regeneration.

Macros in this file share names with older GMC/ATHUB register headers. Incorrect include ordering or compiling the wrong generation into a translation unit can cause macro redefinition problems or register accesses against the wrong ASIC layout.

The `*_BASE_IDX` values are all `0`, so code assumes the first ATHUB base segment. If a future ASIC routes these registers through another segment or instance, both the generated offset data and access paths need review.

The SR-IOV VF control registers stop at `mmATHUB_PCIE_ATS_CNTL_VF_30`; code must not infer that an absent VF31 register exists. Conversely, host/VF code must preserve the hardware-defined distinction between PF-level PCIe ATS controls and per-VF controls.

## Test Signals
Useful validation is mostly integration and hardware oriented:

- Build coverage for translation units that include the header with `athub_2_0_0_sh_mask.h`, checking for macro conflicts and missing register names.
- Register smoke tests on ATHUB 2.0.0 ASICs showing `athub_v2_0_get_clockgating()` reads `mmATHUB_MISC_CNTL` correctly and `athub_v2_0_set_clockgating()` toggles only the intended mask bits.
- KFD/GMC tests that program PASID mappings for several VMIDs and confirm reads via `mmATC_VMID0_PASID_MAPPING + vmid` return valid PASID data.
- Suspend/resume and GPU reset tests that verify ATHUB mappings and clock-gating/light-sleep state are restored by higher-level driver paths.
- SR-IOV tests that exercise PF and VF ATS control paths without touching nonexistent VF registers or host-only registers from a VF context.
- Negative fault-path testing that checks ATC/ATS fault status and VM fault reporting still point at coherent status registers after page faults.
