# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_1_0_offset.h

## Purpose
This generated AMDGPU register-offset header names the ATHUB 2.1.0 memory-mapped register offsets used by SOC15 register access code. It covers three ATHUB address blocks: `athub_atsdec` at base address `0x3000`, `athub_xpbdec` at base address `0x31a0`, and `athub_rpbdec` at base address `0x3350`.

The file does not implement algorithms. Its purpose is to provide stable symbolic constants for address calculation, so driver code can read and write ATHUB ATS, PASID/VMID mapping, XPB routing, peer BAR, clock/power, fault, and performance-counter registers without embedding raw offsets.

## Important APIs, types, and functions
There are no C functions, structures, or runtime types. The public interface is the set of `#define` macros guarded by `_athub_2_1_0_OFFSET_HEADER`.

Important macro groups include:

- `mmATHUB_ATS_MODE_CNTL`, `mmATC_ATS_CNTL`, `mmATC_ATS_CNTL2`, `mmATC_ATS_MISC_CNTL`, and related ATS/fault/status registers for address translation services behavior.
- `mmATHUB_MISC_CNTL` and `mmATHUB_MEM_POWER_LS`, used with the paired `athub_2_1_0_sh_mask.h` masks by `athub_v2_1.c` to control medium-grain clock gating and memory light sleep.
- `mmATHUB_PCIE_ATS_CNTL`, `mmATHUB_PCIE_PASID_CNTL`, `mmATHUB_PCIE_PAGE_REQ_CNTL`, and `mmATHUB_PCIE_ATS_CNTL_VF_0` through `mmATHUB_PCIE_ATS_CNTL_VF_30` for PCIe ATS/PASID/page-request configuration across physical and virtual functions.
- `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID31_PASID_MAPPING` plus `mmATC_VMID_PASID_MAPPING_UPDATE_STATUS`, used as a contiguous register window where code can address VMID `n` as `mmATC_VMID0_PASID_MAPPING + n`.
- `mmXPB_RTR_SRC_APRTR0` through `mmXPB_RTR_SRC_APRTR13`, `mmXPB_RTR_DEST_MAP0` through `mmXPB_RTR_DEST_MAP13`, `mmXPB_P2P_BAR*`, `mmXPB_PEER_SYS_BAR*`, and CLG/unit-ID mapping registers for XPB routing, peer-to-peer BAR handling, and client matching.
- `mmRPB_*` registers for request path buffering, arbitration, queue controls, ATS controls, SDP port controls, and RPB performance counters.

Each register macro has a matching `<name>_BASE_IDX` macro. In this header all base indices are `0`, matching the ATHUB instance used by `SOC15_REG_OFFSET(ATHUB, 0, ...)` and `RREG32_SOC15/WREG32_SOC15` call sites.

## Control flow
The header has no executable control flow. Its compile-time control flow is limited to the include guard.

Runtime control flow appears in consumers:

- `athub_v2_1.c` reads `mmATHUB_MISC_CNTL`, sets or clears bits from `athub_2_1_0_sh_mask.h`, and writes the register only when clock-gating or light-sleep state changes.
- KFD/GMC paths read or write `SOC15_REG_OFFSET(ATHUB, 0, mmATC_VMID0_PASID_MAPPING) + vmid` to program or report the PASID associated with a VMID.
- Some mapping-update status handling is present but disabled behind `#if 0` in the GFX10 KFD path, which means callers currently write the PASID mapping without waiting on the ATHUB update-status register in that path.

## State and persistence behavior
The file itself has no mutable state and persists nothing. The constants address hardware state inside the GPU. Writes to these registers affect device state until hardware reset, driver reinitialization, power-management transitions, or another component rewrites the same register.

The most visible stateful areas are:

- Clock-gating/light-sleep bits in `mmATHUB_MISC_CNTL`.
- VMID-to-PASID mapping registers, where a valid bit and PASID field are interpreted with masks from `athub_2_1_0_sh_mask.h`.
- Fault status and fault address registers such as `mmATC_ATS_FAULT_STATUS_INFO`, `mmATC_ATS_FAULT_STATUS_ADDR`, and `mmATC_ATS_FAULT_STATUS_INFO2`.
- Sticky and write-one-to-clear style XPB status registers such as `mmXPB_STICKY` and `mmXPB_STICKY_W1C`.
- Performance-counter configuration/result registers in both the ATC and RPB blocks.

## Dependencies
This header depends only on the C preprocessor, but it is meaningful only with the AMDGPU register-access infrastructure:

- `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, and `WREG32` consumers that combine the offset with ATHUB base-address tables.
- `athub_2_1_0_sh_mask.h`, which defines the bit shifts and masks for these offsets.
- AMDGPU IP discovery/version code that routes ATHUB v2.1/v2.4 devices to the v2.1 ATHUB handling.
- ASIC register-base initialization, which supplies `adev->reg_offset[ATHUB_HWIP]` for SOC15-style address translation.

## Integration points
The direct include path is `drivers/gpu/drm/amd/amdgpu/athub_v2_1.c`, where `mmATHUB_MISC_CNTL` is used for ATHUB clock-gating reporting and programming. The same macro namespace is also visible to GMC and KFD code that needs ATHUB PASID mapping registers for GFX10-class devices.

The register groups integrate with:

- AMDGPU power management through ATHUB medium-grain clock gating and light sleep.
- KFD process address-space management through VMID/PASID mapping.
- GPU memory-management fault handling through ATS fault controls and status registers.
- SR-IOV behavior through shared virtualization reset/active-function registers and per-VF PCIe ATS control registers.
- Peer-to-peer and routing setup through XPB source aperture, destination map, BAR, and peer system BAR registers.
- Diagnostics/performance tooling through ATC and RPB performance counters and status registers.

## Risks and edge cases
The highest risk is offset drift: these constants are hardware-contract values, so a wrong number silently redirects register reads or writes to the wrong hardware location. That can break power management, memory translation, fault reporting, or virtualization state.

The VMID/PASID range relies on contiguity from `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID31_PASID_MAPPING`. Any code that computes `base + vmid` must keep VMID bounds checked elsewhere and must not assume a different generation's offsets, because ATHUB 2.0.0 and 2.1.0 place several registers at different offsets.

All base indices in this file are `0`; if future generated headers split blocks across different base indices, consumers that ignore `<name>_BASE_IDX` or hard-code instance selection could become wrong.

Virtualization registers are sensitive because PF/VF access restrictions are enforced by hardware and platform policy. Incorrect writes to shared reset, active function, or per-VF ATS control registers can affect isolation or guest behavior.

Status, sticky, and write-one-to-clear registers should be handled with care. A generic read/modify/write sequence against a W1C register such as `mmXPB_STICKY_W1C` can acknowledge events unexpectedly.

## Test signals
Useful validation signals are mostly integration and hardware-facing:

- Compile coverage for files including `athub_2_1_0_offset.h` and `athub_2_1_0_sh_mask.h`, especially `athub_v2_1.c`, GMC v10, and KFD GFX10 paths.
- Register-access traces showing `SOC15_REG_OFFSET(ATHUB, 0, mmATHUB_MISC_CNTL)` hits the expected ATHUB 2.1.0 address and toggles only `CG_ENABLE` or `CG_MEM_LS_ENABLE` bits during clock-gating transitions.
- KFD/GMC tests that program a PASID for VMIDs in the valid range, then read back `mmATC_VMID0_PASID_MAPPING + vmid` and observe the expected PASID and valid bit.
- SR-IOV tests confirming VF paths avoid privileged ATHUB writes where expected while PF paths can manage per-VF ATS controls.
- Fault-injection or debug tests confirming ATS fault status, fault address, and interrupt reporting line up with the offsets named here.
- ASIC bring-up comparison against AMD's register specification or generated register database for ATHUB 2.1.0.
