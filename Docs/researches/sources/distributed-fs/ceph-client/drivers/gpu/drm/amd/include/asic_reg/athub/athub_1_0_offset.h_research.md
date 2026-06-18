# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_offset.h

## Purpose
This generated register-offset header defines ATHUB 1.0 register offsets and base-index selectors. ATHUB handles address translation services, VMID-to-PASID mapping, PCIe ATS/PASID/page-request controls, crossbar/routing, peer-to-peer BAR mappings, queues, arbitration, and performance counters.

## Important APIs, Types, And Constants
The file has no types or functions; it is a list of `mm*` register offset macros paired with `*_BASE_IDX` macros. All base indices in this header are 0.

Registers are grouped into three address blocks:

`athub_atsdec` at base address `0x3080` defines `mmATC_ATS_CNTL`, status and fault registers, default page controls, VMID/PASID mapping update status, `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID31_PASID_MAPPING`, ATS VMID and ATCL2 status, ATC performance counters, PCIe ATS/PASID/page-request controls, per-VF ATS controls, memory power, IH credits, shared virtualization reset/active function registers, and VMID snapshot status registers.

`athub_xpbdec` at base address `0x31f0` defines XPB router source apertures, XDMA router apertures, destination maps, CLG config/match/unit-ID mappings, local/host/interface status, P2P BAR registers, peer system BAR registers, clock gating, pipe/sub-control, sticky status, and performance knobs.

`athub_rpbdec` at base address `0x33b0` defines RPB pass/block/tag configuration, efficiency and arbitration controls, BIF controls, read/write switch controls, CID and EA queue registers, virtual-channel switch, performance counters, queue controls, ATS controls, and SDP port control.

## Control Flow
There is no executable control flow. Including code combines these offsets with the ATHUB base segment in the ASIC-specific IP offset table, then reads or writes the resulting addresses through AMDGPU register access macros.

## State And Persistence
This header stores no state. The macros name hardware registers that contain live GPU state such as mappings, faults, counters, queue settings, and virtualization controls. Persistence is entirely in hardware until reset or reprogramming by the driver.

## Dependencies And Integration Points
The header is included by ATHUB and memory-management code such as `athub_v1_0.c`, `gmc_v9_0.c`, `mmhub_v9_4.c`, and KFD GFX v9 integration code. It depends on ASIC offset headers, such as Aldebaran or Arcturus IP base tables, to supply the block base address for base index 0.

It integrates with VMID/PASID setup, ATS fault handling, PCIe ATS enablement, SR-IOV per-VF controls, interrupt credit handling, peer-to-peer routing, clock-gating setup, and performance-counter paths.

## Risks
Generated register offsets are low-level hardware ABI. An incorrect offset can break address translation, VMID/PASID isolation, fault reporting, virtualization reset, or peer routing. Because this header provides offsets only, callers must use the matching mask/shift header when manipulating fields; hard-coded bit operations around these offsets are riskier.

The VMID mapping range extends through VMID31, while other display-side VMID code may use smaller VMID counts. Callers must respect the IP block's supported VMID range and the ASIC's configured VMID policy.

## Test Signals
Compile coverage through all include sites catches missing symbols. Runtime signals include successful ATHUB initialization, ATS enable/disable, PASID mappings for VMIDs 0-31 as applicable, recoverable fault reporting, SR-IOV VF ATS programming, KFD queue operation, peer-to-peer BAR routing, ATHUB clock-gating transitions, and performance-counter reads.
