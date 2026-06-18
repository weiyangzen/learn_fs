<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_1_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_1_0_sh_mask.h

## Purpose
`athub_2_1_0_sh_mask.h` is an AMDGPU ASIC register bitfield header for ATHUB 2.1.0. It does not implement executable logic; it supplies preprocessor constants for register field shifts and masks used by C code that programs the Address Translation Hub, its PCIe ATS/PASID/PRI path, XPB routing and peer-to-peer BARs, and RPB request buffering/arbiter behavior.

The file is source-tree-aligned with the companion `athub_2_1_0_offset.h` register-offset header. Driver code combines `mm...` register names from the offset header with `...__SHIFT` and `..._MASK` constants from this header when reading, writing, or decoding hardware registers through AMDGPU register access helpers.

## Important APIs, Types, And Functions
This header exposes macro constants only. There are no C types, functions, storage definitions, or inline helpers.

The public surface is the register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask, usually suffixed with `L`.
- Each register group is introduced by a comment naming the hardware register.
- Address-block comments divide the file into `athub_atsdec`, `athub_xpbdec`, and `athub_rpbdec`.

Important register families covered by the header include:

- `ATHUB_ATS_MODE_CNTL`, `ATC_ATS_CNTL`, `ATC_ATS_CNTL2`, `ATC_ATS_TR_QOS_CNTL`, and `ATC_ATS_MISC_CNTL` for ATS enablement, PRI/PASID disable bits, request credits, translation control, quality-of-service, and 32K grouping behavior.
- `ATC_ATS_FAULT_CNTL`, `ATC_ATS_FAULT_STATUS_INFO`, `ATC_ATS_FAULT_STATUS_ADDR`, `ATC_ATS_FAULT_STATUS_INFO2`, `ATC_TRANS_FAULT_RSPCNTRL`, `ATC_ATS_STATUS`, and VMID snapshot/status registers for translation fault reporting and outstanding work observation.
- `ATHUB_MISC_CNTL` and `ATHUB_MEM_POWER_LS` for ATHUB clock-gating, light-sleep, power-gating status, busy status, and memory low-power timing.
- `ATHUB_PCIE_ATS_CNTL`, `ATHUB_PCIE_PASID_CNTL`, `ATHUB_PCIE_PAGE_REQ_CNTL`, `ATHUB_PCIE_OUTSTAND_PAGE_REQ_ALLOC`, `ATHUB_COMMAND`, and `ATHUB_PCIE_ATS_CNTL_VF_0` through `_VF_30` for PCIe ATS, PASID, PRI, bus-mastering, and virtualization-facing control.
- `ATC_VMID0_PASID_MAPPING` through `ATC_VMID31_PASID_MAPPING` plus `ATC_VMID_PASID_MAPPING_UPDATE_STATUS` for PASID-to-VMID mappings and completion bits.
- `ATC_PERFCOUNTER*` and `RPB_PERFCOUNTER*` groups for selecting, clearing, enabling, and reading ATC/RPB performance counters.
- `XPB_RTR_SRC_APRTR*`, `XPB_RTR_DEST_MAP*`, `XPB_CLG_*`, `XPB_P2P_BAR*`, `XPB_PEER_SYS_BAR*`, `XPB_*_STS`, and `XPB_SUB_CTRL` for XPB aperture routing, crossbar/client grouping, P2P BAR setup, peer system BAR routing, sticky status, reset, and stall controls.
- `RPB_PASSPW_CONF`, `RPB_BLOCKLEVEL_CONF`, `RPB_ARB_CNTL*`, `RPB_BIF_CNTL*`, `RPB_*_QUEUE_*`, `RPB_ATS_CNTL*`, `RPB_DF_SDPPORT_CNTL`, `RPB_SDPPORT_CNTL`, and `RPB_NBIF_SDPPORT_CNTL` for RPB pass-power overrides, block-level overrides, arbitration, queue selection, ATS command/routing fields, and SDP/NBIF/Data Fabric credit controls.

## Control Flow
There is no runtime control flow in the header. It participates in control flow when included by AMDGPU implementation files:

- `amdgpu/athub_v2_1.c` includes this header and `athub_2_1_0_offset.h`, reads `mmATHUB_MISC_CNTL`, sets or clears `ATHUB_MISC_CNTL__CG_ENABLE_MASK` for medium-grain clock gating, sets or clears `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` for light sleep, and writes the register back only if the value changes.
- `amdgpu/athub_v2_1.c` also decodes the same `ATHUB_MISC_CNTL` bits in `athub_v2_1_get_clockgating()` to report `AMD_CG_SUPPORT_ATHUB_MGCG` and `AMD_CG_SUPPORT_ATHUB_LS`.
- `amdgpu/amdgpu_amdkfd_gfx_v10.c` writes `ATC_VMID0_PASID_MAPPING + vmid` using `ATC_VMID0_PASID_MAPPING__VALID_MASK` and reads it back using `ATC_VMID0_PASID_MAPPING__PASID_MASK` and `...__VALID_MASK`. The code documents the intended update-status wait-and-clear protocol around `ATC_VMID_PASID_MAPPING_UPDATE_STATUS`, though that block is currently disabled there.
- `amdgpu/gmc_v10_0.c` reads the ATHUB `ATC_VMID0_PASID_MAPPING + vmid` register to expose ATC VMID/PASID mapping information to memory-management paths.
- Other generation-specific files use the same field names where compatible, so this header's symbols fit into the AMDGPU pattern of register access through `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## State And Persistence
The header itself has no state and persists no data. Its constants describe volatile hardware register state owned by the GPU.

State affected by consumers includes:

- ATHUB power-management state: clock-gating and memory light-sleep bits in `ATHUB_MISC_CNTL`.
- Address-translation state: PASID-to-VMID mapping registers, update-status bits, default page/fault response controls, fault log controls, and outstanding VMID status.
- PCIe and virtualization state: ATS enablement, PRI enable/reset, PASID capability enable bits, bus-master enable, per-VF ATS enablement, and shared PF/VF reset/active-function fields.
- Routing and buffering state: XPB aperture maps, P2P/peer BARs, client grouping tables, RPB arbitration/queue/credit configuration, and sticky status registers.
- Performance-monitoring state: ATC and RPB performance-counter select, clear, enable, result, compare, and saturation-control fields.

Persistence is limited to hardware lifetime and reset domains. Values may survive across driver call boundaries until explicitly reprogrammed, but they are not filesystem or kernel persistent state. Some fields are status or write-one-clear style, such as `XPB_STICKY_W1C__BITS_MASK`, and must be treated differently from normal read-modify-write configuration fields.

## Dependencies And Integration Points
Direct dependencies are minimal: C preprocessing and the include guard `_athub_2_1_0_SH_MASK_HEADER`. Practical use depends on companion register-offset/default headers and AMDGPU SOC15 register-access infrastructure.

Primary integration points include:

- `athub/athub_2_1_0_offset.h`, which provides `mm...` addresses for the field masks in this file.
- `amdgpu/athub_v2_1.c`, which uses `ATHUB_MISC_CNTL` masks for power-management programming on ATHUB IP versions 2.1.x and 2.4.0.
- KFD and GFX integration files such as `amdgpu_amdkfd_gfx_v10.c` and `amdgpu_amdkfd_gfx_v10_3.c`, which include ATHUB 2.1 headers and use ATC VMID/PASID mapping masks when mapping GPU VMIDs to process address spaces or decoding mappings.
- GMC code such as `gmc_v10_0.c`, which reports ATC mapping information through memory-management hooks.
- Golden-register programming paths in GMC/ATHUB generations, where RPB arbitration register values are programmed by offset and can be reasoned about with the masks in this header.
- Hardware virtualization paths: VF/PF reset, active-function, per-VF ATS enable, and SR-IOV checks in consuming code all depend on these bit layouts matching the ASIC specification.

## Risks And Edge Cases
The largest risk is bitfield drift from the hardware specification. A wrong mask or shift can silently program reserved bits, disable ATS/PASID/PRI behavior, misroute peer traffic, break VMID/PASID isolation, or corrupt performance-counter reads.

Register families with repeated numbered entries carry copy/paste risk. Examples include `ATC_VMID0_PASID_MAPPING` through `ATC_VMID31_PASID_MAPPING`, `ATHUB_PCIE_ATS_CNTL_VF_*`, `XPB_P2P_BAR*`, `XPB_PEER_SYS_BAR*`, `XPB_RTR_DEST_MAP*`, and repeated RPB/ATC performance-counter groups.

Some masks cover reserved fields, such as `ATC_ATS_CNTL2__RESERVED_MASK`, `ATC_ATS_MISC_CNTL__RESERVED_MASK`, `XPB_P2P_BAR*__RESERVED_MASK`, `RPB_DF_SDPPORT_CNTL__RESERVED_MASK`, and `RPB_SDPPORT_CNTL__RESERVED_MASK`. Consumers should not blindly set these masks unless a hardware programming guide explicitly requires it.

Status and command fields are not interchangeable with persistent configuration fields. For example, outstanding/status/fault/sticky bits may be read-only or clear-on-write depending on the register, while queue, credit, and routing fields are configuration knobs.

Virtualization and PASID fields are security-sensitive. Incorrect use of `ATC_VMID*_PASID_MAPPING__VALID_MASK`, `...__PASID_MASK`, per-VF ATS enable masks, or PF/VF reset masks can expose the wrong address-space mapping or leave stale mappings observable by GPU clients.

The constants are 32-bit-oriented even when written with `L` suffixes. Consumers should avoid sign-extension surprises by using unsigned 32-bit temporaries for register values, as the AMDGPU call sites generally do.

## Test Signals
Useful validation signals are mostly integration and hardware-facing:

- Kernel build coverage for AMDGPU/KFD with this header included catches missing symbols, duplicate names, or syntax/include-guard breakage.
- ATHUB clock-gating tests should show `athub_v2_1_set_clockgating()` toggling `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK`, while `athub_v2_1_get_clockgating()` reports the expected flags.
- KFD process/queue tests should show PASID-to-VMID mappings programmed and decoded correctly through `ATC_VMID0_PASID_MAPPING + vmid`; failures may appear as queue launch failures, address-translation faults, or missing process attribution.
- GPUVM and memory-management tests should confirm that ATC mapping-info hooks return the expected PASID and validity state.
- SR-IOV and PCIe ATS/PRI/PASID validation should exercise PF/VF-specific enable paths and catch bad per-VF masks or reset fields.
- P2P, peer BAR, and multi-GPU traffic tests are the strongest signal for XPB route/BAR mask correctness.
- Fault-injection or fault-observation tests should verify `ATC_ATS_FAULT_STATUS_*`, `ATC_ATS_STATUS`, and VMID outstanding/status fields decode plausible fault types, VMIDs, page addresses, and outstanding invalidations.
- Performance-counter tests should confirm ATC/RPB counter configuration, clear, enable, low/high reads, and saturation controls behave consistently with the selected events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_1_0_sh_mask.h -->
