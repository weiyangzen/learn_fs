# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_0_0_sh_mask.h

## Purpose

`athub_2_0_0_sh_mask.h` is a generated AMDGPU hardware register field header for ATHUB IP version 2.0.0. It does not implement executable logic. Instead, it defines the bit shifts and bit masks used by driver code to construct, inspect, and modify 32-bit ATHUB register values without open-coded constants.

The covered register blocks are:

- `athub_atsdec`: address translation service and ATC control/status registers, VMID/PASID mappings, PCIe ATS/PASID/page-request controls, ATHUB clock/light-sleep controls, virtualization reset/function state, interrupt-handler credits, and ATS SDP port controls.
- `athub_xpbdec`: XPB routing apertures, destination maps, crossbar local-group configuration, write-combine buffer status, P2P BAR and peer system BAR mappings, interface status/control, sticky status, performance knobs, and unit-id-to-local-group mappings.
- `athub_rpbdec`: RPB pass/block-level arbitration knobs, queue mappings, read/write switch and combine controls, performance counters, ATS request behavior, and SDP/NBIF credit controls.

The file is paired with `athub_2_0_0_offset.h`, which supplies register offsets such as `mmATHUB_MISC_CNTL` and `mmATC_VMID0_PASID_MAPPING`, and `athub_2_0_0_default.h`, which supplies reset/default register values.

## Important APIs, Types, And Constants

This header exports preprocessor constants only. There are no C functions, structs, enums, or storage definitions.

The dominant naming form is:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask in the full register word.

Important fields include:

- `ATC_ATS_CNTL__DISABLE_ATC_MASK`, `DISABLE_PRI`, `DISABLE_PASID`, `CREDITS_ATS_RPB`, and ordering/return fields. These describe ATS translation enablement, PRI/PASID participation, credit allocation, and logging/execution return behavior.
- `ATC_ATS_STATUS__BUSY_MASK`, `CRASHED`, `DEADLOCK_DETECTION`, and invalidation-outstanding fields. These are status signals for ATS work and failure states.
- `ATC_ATS_FAULT_CNTL`, `ATC_ATS_FAULT_STATUS_INFO`, `ATC_ATS_FAULT_STATUS_ADDR`, and `ATC_ATS_FAULT_STATUS_INFO2` fields. These describe how faults are logged, interrupted, crashed, and decoded, including VMID, VF/VFID, invalidation/page-request source, status, and page address bits.
- `ATC_TRANS_FAULT_RSPCNTRL__VMID0_MASK` through `VMID31_MASK`. These provide per-VMID translation fault response selection.
- `ATC_VMID_PASID_MAPPING_UPDATE_STATUS__VMID*_REMAPPING_FINISHED_MASK` and `ATC_VMID0_PASID_MAPPING` through `ATC_VMID31_PASID_MAPPING`. Each VMID/PASID mapping uses a 16-bit `PASID`, a `NO_INVALIDATION` bit, and a `VALID` bit.
- `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK`. These are the directly used clock-gating and memory light-sleep control bits in the ATHUB v2.0 driver.
- `ATC_PERFCOUNTER*_CFG`, `ATC_PERFCOUNTER_RSLT_CNTL`, `ATC_PERFCOUNTER_LO`, and `ATC_PERFCOUNTER_HI`. These expose ATC performance counter selection, mode, enable, clear, trigger, and result fields.
- `ATHUB_PCIE_ATS_CNTL`, `ATHUB_PCIE_PASID_CNTL`, `ATHUB_PCIE_PAGE_REQ_CNTL`, `ATHUB_PCIE_OUTSTAND_PAGE_REQ_ALLOC`, and `ATHUB_PCIE_ATS_CNTL_VF_0` through `VF_30`. These cover PF/VF ATS enablement, PASID, and page-request control.
- `XPB_RTR_SRC_APRTR*`, `XPB_RTR_DEST_MAP*`, and `XPB_XDMA_RTR_*`. These describe XPB aperture base addresses and destination routing fields such as `DEST_OFFSET`, `DEST_SEL`, `DEST_SEL_RPB`, `SIDE_OK`, and `APRTR_SIZE`.
- `XPB_P2P_BAR_CFG`, `XPB_P2P_BAR0` through `BAR7`, `XPB_P2P_BAR_SETUP`, `XPB_P2P_BAR_DELTA_ABOVE`, `XPB_P2P_BAR_DELTA_BELOW`, `XPB_PEER_SYS_BAR*`, and `XPB_XDMA_PEER_SYS_BAR*`. These define peer/P2P memory-window programming fields including validity, address, BAR selection, snooping, compression, updates, and ATC translation.
- `XPB_CLK_GAT`, `XPB_INTF_CFG`, `XPB_INTF_STS`, `XPB_PIPE_STS`, `XPB_SUB_CTRL`, `XPB_STICKY`, and `XPB_STICKY_W1C`. These support XPB clock gating, interface flow control/status, pipe occupancy/status, subordinate control, and sticky write-one-to-clear reporting.
- `RPB_PASSPW_CONF`, `RPB_BLOCKLEVEL_CONF`, `RPB_ARB_CNTL`, `RPB_BIF_CNTL`, `RPB_WR_SWITCH_CNTL`, `RPB_RD_SWITCH_CNTL`, `RPB_WR_COMBINE_CNTL`, `RPB_RD_QUEUE_CNTL`, `RPB_WR_QUEUE_CNTL`, `RPB_ATS_CNTL`, `RPB_ATS_CNTL2`, `RPB_SDPPORT_CNTL`, and `RPB_NBIF_SDPPORT_CNTL`. These describe RPB arbitration, queue, pass/block-level override, ATS command, and credit fields.

## Control Flow

There is no runtime control flow in the header itself. The operational flow appears in consumers:

1. A driver module includes this mask header together with `athub_2_0_0_offset.h`.
2. It reads a register through AMDGPU MMIO helpers such as `RREG32_SOC15(ATHUB, 0, mmATHUB_MISC_CNTL)` or computes an address with `SOC15_REG_OFFSET(ATHUB, 0, <register>)`.
3. It sets or clears fields using the masks from this file, usually with simple OR/AND operations.
4. It writes the modified value back through `WREG32_SOC15`, `WREG32`, or ring-emitted write helpers.

The clearest direct flow is `athub_v2_0_set_clockgating()` in `amdgpu/athub_v2_0.c`: it checks SR-IOV and IP-version gates, reads `mmATHUB_MISC_CNTL`, toggles `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` according to requested clock-gating state and supported `cg_flags`, then writes the register only if the value changed. `athub_v2_0_get_clockgating()` reads the same register and maps those two bits back into `AMD_CG_SUPPORT_ATHUB_MGCG` and `AMD_CG_SUPPORT_ATHUB_LS`.

KFD/GFX10 queue setup uses this header in `amdgpu_amdkfd_gfx_v10.c`. `kgd_set_pasid_vmid_mapping()` builds a PASID mapping value with `ATC_VMID0_PASID_MAPPING__VALID_MASK`, writes it to `mmATC_VMID0_PASID_MAPPING + vmid`, and also writes the corresponding IH LUT entry. The code contains a disabled wait-and-clear protocol for `ATC_VMID_PASID_MAPPING_UPDATE_STATUS`, documenting the intended remapping-completion handshake.

GMC v10 includes the header while wiring the v2.0 ATHUB path into memory-controller initialization and clock-gating state management. Its PASID ring emission updates IH LUT registers, while ATHUB clock-gating dispatch chooses v2.0 or v2.1 helpers based on `ATHUB_HWIP`.

## State And Persistence Behavior

All state represented here lives in GPU hardware registers. The header itself has no persistent data, initialization side effects, allocations, locks, or teardown path.

The state categories are:

- Latched configuration state: VMID/PASID mappings, ATS/PASID enablement, page-request behavior, XPB routing and BAR windows, RPB arbitration, queue, and credit knobs.
- Runtime status state: ATS busy/crashed/deadlock status, outstanding invalidations, VMID outstanding bits, ATCL2 powered-down bits, XPB interface/pipe/write-combine status, RPB performance counter status, and sticky XPB status.
- Clear/control state: performance-counter clear bits, command bits, mapping update status bits, and `XPB_STICKY_W1C` write-one-to-clear state.
- Power-management state: ATHUB clock-gating and memory light-sleep enable bits, plus related status bits.

Because register contents can reset across GPU reset, suspend/resume, power-gating, or function-level reset, the durable source of truth is the driver initialization/resume path and hardware defaults, not this header. Any code using these masks must preserve reserved bits and update only documented fields, typically by read-modify-write.

## Dependencies

This file depends only on the C preprocessor and include guards. Semantically it depends on:

- The matching offset header `include/asic_reg/athub/athub_2_0_0_offset.h` for register addresses.
- The matching default header `include/asic_reg/athub/athub_2_0_0_default.h` for reset values.
- SOC15 AMDGPU MMIO access infrastructure such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and ring write helpers.
- AMDGPU IP-version dispatch and hardware block IDs such as `ATHUB`, `ATHUB_HWIP`, and `IP_VERSION(...)`.
- Consumers that understand AMDGPU VMIDs, PASIDs, SR-IOV PF/VF behavior, ATS/PRI/PASID semantics, and the XPB/RPB data paths.

The header has a global macro namespace. Register field names are intentionally broad, so it must be included in contexts where another ASIC-generation mask header does not define conflicting names for the same unprefixed register names.

## Integration Points

Direct source integrations observed in this tree:

- `amdgpu/athub_v2_0.c` includes the offset, mask, and default headers for ATHUB 2.0.0 and uses `ATHUB_MISC_CNTL` masks for clock gating and memory light sleep.
- `amdgpu/athub_v2_0.h` exposes the v2.0 clock-gating entry points used by the GMC block.
- `amdgpu/gmc_v10_0.c` includes this mask/offset pair and dispatches to `athub_v2_0_set_clockgating()` or `athub_v2_0_get_clockgating()` for ATHUB versions below 2.1.0.
- `amdgpu/amdgpu_amdkfd_gfx_v10.c` includes this mask/offset pair for GFX10 KFD integration and uses `ATC_VMID0_PASID_MAPPING__VALID_MASK` while programming VMID-to-PASID mappings in ATHUB.
- Sibling headers for ATHUB 2.1.0, 3.0.0, and 4.1.0 provide similar mask layouts for newer IP revisions; the C helpers select the correct version-specific implementation based on IP version.

This file also aligns with older GMC/MC XPB and ATC register naming. That consistency lets AMDGPU code patterns migrate across ASIC generations while swapping only the included IP-version-specific offset/mask headers.

## Risks And Edge Cases

- Incorrect masks or shifts directly corrupt MMIO programming. For ATS and VMID/PASID fields, that can break GPU virtual memory isolation, translation fault handling, KFD process address spaces, or SR-IOV behavior.
- The VMID/PASID mapping registers are repeated for VMIDs 0-31, but consumers often compute `base + vmid`. Callers must validate VMID ranges before using the offset arithmetic.
- `kgd_set_pasid_vmid_mapping()` documents a mapping update wait-and-clear protocol, but it is disabled in this tree. Code depending on immediate remapping completion may be sensitive to hardware revisions or firmware behavior.
- Several fields are hardware status or write-one-to-clear style controls. Treating them as ordinary read/write configuration can lose events or clear diagnostics.
- Fields such as XPB BAR addresses, peer system BAR addresses, and aperture base addresses represent address windows. Misprogramming them can route traffic to the wrong memory or peer target.
- The header uses plain `L` integer constants. Most masks fit 32 bits, but code should continue to store register values in unsigned 32-bit types to avoid sign-extension surprises around masks such as `0x80000000L` or `0xFFFFFFFFL`.
- Because generated register names are not namespaced by ASIC version in the macro itself, including multiple ATHUB generation mask headers in one translation unit would create macro redefinition conflicts.
- Power-management bits must respect SR-IOV and clock-gating capability gates. The v2.0 helper skips programming for virtual functions and checks `adev->cg_flags` before toggling the relevant bits.

## Test Signals

Useful validation signals include:

- Build coverage for translation units that include this header: at least `amdgpu/athub_v2_0.c`, `amdgpu/gmc_v10_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v10.c`.
- Boot or probe logs on ATHUB 2.0.0-class GPUs showing no register access faults and normal GMC/ATHUB initialization.
- Clock-gating tests that call the GMC clock-gating state path and verify `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` are reflected in `athub_v2_0_get_clockgating()`.
- KFD process/queue tests that allocate PASIDs and VMIDs, run GPU workloads, and verify faults or queue hangs do not occur after `kgd_set_pasid_vmid_mapping()` writes `mmATC_VMID0_PASID_MAPPING + vmid`.
- GPU VM fault tests that exercise ATS fault status decoding and ensure VMID, PASID, VF/VFID, invalidation/page-request, and page address fields remain meaningful.
- Suspend/resume and GPU reset tests, because register state represented by this header is hardware-resident and must be restored or left in safe defaults after power transitions.
- SR-IOV PF/VF tests, especially around the per-VF ATS enable fields and `ATHUB_SHARED_*` virtualization registers, to confirm PF-owned state is not touched from VF paths.
- Register mask consistency checks comparing generated masks against hardware XML/register specs or sibling AMDGPU headers for ATHUB 2.0.0.
