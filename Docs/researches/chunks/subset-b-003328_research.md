# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 2526-4978

## Scope

This chunk covers lines 2526-4978 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains 2,127 preprocessor `#define` entries: 1,063 `__SHIFT` constants and 1,064 `_MASK` constants. There are no C functions, structs, enums, global variables, allocation paths, locks, direct register reads/writes, or persistent software data structures in this range.

The range starts inside `GDC0_A2S_CNTL_SW2`, after its first `STATIC_VC_ENABLE` and `STATIC_VC_VALUE` shift definitions were emitted in the previous chunk. It then covers GDC0 AXI/SDP arbitration, tag allocation, SHUB protection, NGDC clock/power gating, GFX doorbell status, ATDMA arbitration, and S2A controls. At line 2673 it switches to `addressBlock: aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, a PCIe endpoint-function 0 configuration-space field map for `BIF_CFG_DEV0_EPF0`. The chunk runs through standard PCI header fields, PM, PCIe, MSI/MSI-X, vendor-specific, virtual-channel, serial-number, AER, BAR, power, DPA, secondary PCIe, per-lane equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, data-link, 16 GT/s/32 GT/s PHY/equalization, lane margining, and GPUIOV vendor-specific virtualization fields. It ends inside `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`, with only the `DW3` shift present; the `DW3` mask and following scheduler fields continue in the next chunk.

Although this file sits under a local `ceph-client` source mirror, the content is AMD GPU NBIO/PCIe register metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the generated bitfield companion for NBIO 7.9.0 register and PCIe configuration-space offsets. Each macro encodes one of two pieces of field geometry:

- `REGISTER__FIELD__SHIFT`: least-significant bit position of a field.
- `REGISTER__FIELD_MASK`: bit mask of that field in the containing register.

Driver code combines these names with matching offsets from `nbio_7_9_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The goal is to keep NBIO, PCIe, interrupt, power-management, error-reporting, and virtualization programming symbolic instead of hard-coding bit numbers.

## Important Definitions

The opening GDC0/NGDC portion describes internal NBIO fabric behavior:

- `GDC0_A2S_CNTL_SW2`, `GDC0_A2S_TAG_ALLOC_0`, `GDC0_A2S_TAG_ALLOC_1`, and `GDC0_A2S_MISC_CNTL` expose virtual-channel selection, response reorder controls, SDP write chaining, weighted read/write arbitration, per-VC tag allocation, tag FIFO behavior, and minimum read/write tag set sizes.
- `GDC0_SHUB_REGS_IF_CTL` controls SHUB register request protection, including non-PF request handling and VF protection disablement.
- `GDC0_NGDC_MGCG_CTRL`, `GDC0_NGDC_PG_MISC_CTRL`, `GDC0_NGDC_PGMST_CTRL`, and `GDC0_NGDC_PGSLV_CTRL` define medium-grain clock gating, SRAM fine-grain clock gating, endpoint D3-only power gating policy, clock permissions, power-gating hysteresis, idleness-count enables, firmware power-gating exits, and per-clock idle hysteresis.
- `GDC0_NBIF_GFX_DOORBELL_STATUS` exposes the 16-bit GFX doorbell-sent status bitmap.
- `GDC0_ATDMA_MISC_CNTL` and `GDC0_S2A_MISC_CNTL` cover ATDMA/S2A arbitration modes, virtual-channel weights, host completion behavior, HDP performance enhancement disablement, and write-response arbitration.

The `BIF_CFG_DEV0_EPF0` address block maps the physical endpoint-function PCI configuration image:

- Conventional PCI header fields include vendor/device ID, command/status, revision/class code, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability list fields.
- PM capability fields include capability IDs and next pointers, version, PME clock/support, D1/D2 support, auxiliary current, power state, PME enable/status, data select/scale, bus-power enable, and PMI data.
- PCIe capability fields include device type, device capability/control/status, link capability/control/status, Device/Link Capability 2, Device/Link Control 2 including `LTR_EN`, OBFF, atomic op, ARI forwarding, IDO, ten-bit tag, and end-to-end TLP prefix controls, plus Link Status 2 equalization, retimer, crosslink, downstream-component, and DRS status.
- MSI and MSI-X fields define capability lists, enable bits, multi-message capability/enable, 64-bit addressing, per-vector masking, extended message data, message address/data, masks, pending bits, table/PBA BIRs, table offsets, function mask, and MSI-X enable.
- Vendor-specific and virtual-channel fields include VSEC headers, scratch dwords, VC enhanced capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status for TC/VC mapping and arbitration.
- Serial number and AER fields include device serial dwords, uncorrectable/correctable error status, masks, severity, ECRC capability/enable bits, first-error pointer, multi-header support, TLP prefix log presence, header logs, and TLP prefix logs.
- Extended endpoint capability families include resizable/enhanced BAR controls for BAR1-BAR6, power budget data/select/capability, dynamic power allocation capability/status/control and per-substate power allocation, secondary PCIe Link Control 3, lane error status, and lane 0-15 equalization controls.
- Isolation and address-translation families include ACS capability/control, ATS capability/control, page request interface control/status/capacity/allocation, PASID capability/control, multicast capability/control/address/receive/blocking fields, LTR capability, and ARI capability/control.
- SR-IOV fields include capability/control/status, initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BARs 0-5, and VF migration-state array offset.
- High-speed link and diagnostic fields include Data Link Feature capability/status, 16 GT/s link capability/control/status, 16 GT/s parity mismatch status and per-lane equalization controls, lane margining capability/status and per-lane control/status for lanes 0-15, and 32 GT/s link capability/control/status.

The closing GPUIOV vendor-specific capability is AMD virtualization metadata:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV` define the GPUIOV extended-capability and VSEC headers.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE`, `INTR_STATUS`, and `RESET_CONTROL` define hypervisor/VF mailbox interrupt enable/status bits and a soft PF FLR bit.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW0` selects a VF and carries small transmit/receive message payloads, valid, and acknowledgement bits.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1` maps transmit-acknowledge and receive-valid bits for VF0-VF15.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW2` maps the same mailbox state for VF16-VF30 and PF.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_CONTEXT`, `TOTAL_FB`, `REGION`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB` describe virtualization context placement, total/used framebuffer accounting, region ID, peer-over-XGMI enablement, and per-VF framebuffer size/offset.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_OFFSETS` through `OFFSETS4` provide scheduler metadata offsets for VCN0-VCN11 and GFX0-GFX7.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW0` through the start of `UVD0SCH_DW3` expose full-width scheduler data words; the last register is split by the chunk boundary.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. The macros are meaningful only when paired with the correct NBIO 7.9.0 address metadata and with the access path expected by the register family:

- GDC0/NGDC names pair with `regGDC0_*` offsets and SOC15/NBIO register access.
- `BIF_CFG_DEV0_EPF0_*` names pair with endpoint-function config-space offsets such as `cfgBIF_CFG_DEV0_EPF0_*` in `nbio_7_9_0_offset.h`.
- GPUIOV names pair with the GPUIOV capability offsets in the same endpoint config-space image.

The macros encode field positions and masks only. They do not encode reset values, access permissions, side effects, write-one-to-clear behavior, firmware ownership, or required register ordering.

## Control Flow

This header has no local runtime control flow. Runtime use is external and normally follows this pattern:

1. AMDGPU selects the NBIO 7.9.0 register offset or PCIe config offset matching the active ASIC/IP version.
2. It reads the register through the proper SOC15, PCIe, or SMN/MMIO helper.
3. It extracts a field with the generated mask and shift, or composes a read-modify-write value using the field macros while preserving unrelated bits.
4. Hardware applies the semantics: arbitration, tag allocation, clock/power gating, doorbell-status reporting, endpoint enumeration, interrupt routing, PCIe link training, power-management transitions, AER reporting, isolation/translation policy, SR-IOV/GPUIOV virtualization state, or scheduler metadata exchange.

The order in the file follows the generated register database, not an execution sequence. Repeated status, mask, severity, and control register families often share bit positions while representing different operations.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. All state named here lives in NBIO hardware registers or in hardware-backed PCIe configuration-space/capability images.

Represented state includes:

- Fabric configuration: GDC0 virtual-channel selection, tag allocations, arbitration weights, response ordering, SHUB VF protection, ATDMA/S2A routing, and doorbell status.
- Clock and power controls: NGDC medium-grain clock gating, SRAM fine-grain gating, endpoint D3-only behavior, power-gating hysteresis, idle-count policies, and firmware exit controls.
- PCI configuration state: command bits, BAR decode, interrupt disable, PM state, PME enable/status, MSI/MSI-X programming, link controls, payload/read-request sizing, LTR enablement, OBFF, ARI forwarding, atomic/IDO controls, ACS/ATS/PASID/PRI controls, multicast controls, SR-IOV controls, and GPUIOV mailbox/framebuffer allocation.
- Capability and diagnostic state: PCI/PCIe identity, capability-chain headers, link capabilities/status, AER status/masks/severity/logs, lane/equalization/margining status, data-link feature status, 16 GT/s and 32 GT/s status, and GPUIOV mailbox valid/ack state.

Persistence is determined by PCIe reset rules, GPU/NBIO reset domains, function-level reset, SR-IOV VF lifecycle, suspend/resume restore, runtime power transitions, firmware initialization, and explicit driver writes. Callers must know from the hardware specification which fields are read-only, sticky, write-one-to-clear, reserved, firmware-owned, or safe for read-modify-write.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 offset header staying synchronized with the mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching `regGDC0_*` offsets and `cfgBIF_CFG_DEV0_EPF0_*` config-space offsets.

No `nbio_7_9_0_default.h` file is present in this source tree, so reset/default information is not available from a sibling generated default header here.

Integration points are AMDGPU NBIO and PCIe platform behavior: GPU enumeration, BAR/resource setup, interrupt setup, ASPM/LTR policy, power management, suspend/resume, GPU reset recovery, AER logging and clearing, PCIe link diagnostics, ACS/IOMMU isolation, ATS/PASID/PRI address translation, SR-IOV VF creation and BAR assignment, GPUIOV mailbox handling, framebuffer partitioning, VCN/GFX scheduler metadata, and debug register dumps. Older NBIO implementations in this tree use the same semantic families, for example NBIO code programs `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` when enabling or disabling LTR on related generations.

## Risks And Edge Cases

- The chunk starts mid-`GDC0_A2S_CNTL_SW2`; the first two shift definitions for that register are outside this work item. It ends mid-`PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3`; the mask for `DW3` is outside this work item. Merge/reconciliation must combine adjacent chunks before making whole-register conclusions.
- Shift/mask mistakes compile cleanly but can read or write adjacent bits, corrupting PCI command state, BAR sizing, interrupt configuration, link controls, AER policy, SR-IOV state, or GPUIOV mailbox/framebuffer metadata.
- Status, mask, severity, and control registers intentionally reuse similar field names. Copying a field between `*_STATUS`, `*_MASK`, and `*_SEVERITY` groups can change clearing behavior, reporting policy, or fatal/nonfatal classification.
- AER, PCI status, device status, link status, lane status, margining status, and GPUIOV interrupt status may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear diagnostics if it writes a status register without W1C-aware handling.
- Reserved fields are present, including full-register reserved masks. Writers should preserve reserved bits unless hardware documentation explicitly says otherwise.
- GDC0 arbitration, tag, and VC controls are performance and forward-progress sensitive. Incorrect tag allocation or weighting can cause starvation, reduced throughput, or ordering issues under load.
- SHUB VF protection, ACS, ATS, PASID, PRI, SR-IOV, GPUIOV, and VF framebuffer allocation fields are virtualization-sensitive. Misprogramming can break isolation, expose PF/VF state incorrectly, or invalidate VFIO/IOMMU assumptions.
- Link retraining, compliance, equalization, 16 GT/s/32 GT/s, and lane margining fields are operationally sensitive. Changing them on an active link can destabilize PCIe connectivity or produce misleading diagnostics.
- Similar names exist across NBIO generations and endpoint/function/VF namespaces. Code must include the header matching the active IP version and pair a mask with the correct `reg*` or `cfg*` offset.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch missing or malformed symbols and mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field in this chunk should have the expected shift and mask, every register family should have a matching offset in `nbio_7_9_0_offset.h`, and chunk-boundary split fields should reconcile cleanly with neighboring chunks.
- Validate PCIe enumeration on matching hardware with `lspci -vv`: vendor/device/class IDs, BARs, capability pointers, PM/PCIe/MSI/MSI-X/VSEC/VC/AER/ACS/ATS/PASID/ARI/SR-IOV/Data Link/16 GT/s/32 GT/s/GPUIOV capabilities, and link capability/status should decode coherently.
- Exercise interrupt setup and teardown: MSI/MSI-X enable bits, table/PBA BAR indicators, pending/mask bits, and GPUIOV mailbox interrupt status should behave as expected.
- Exercise ASPM/LTR and runtime power-management paths, including suspend/resume and GPU reset recovery, to confirm PM state, `LTR_EN`, NGDC clock/power gating controls, and restored configuration state remain consistent.
- Exercise PCIe AER and link diagnostics where hardware and platform support it: correctable/uncorrectable status, masks, severity, ECRC controls, header/TLP prefix logs, lane error status, equalization status, margining status, and 16 GT/s/32 GT/s link status should match platform observations.
- Validate SR-IOV/GPUIOV workflows on capable hardware: VF counts, VF BARs, page sizes, first VF offset/stride, mailbox valid/ack bits, PF/VF reset behavior, per-VF framebuffer size/offset, and VCN/GFX scheduler offsets should match the hypervisor or firmware contract.
- Compare this NBIO 7.9.0 layout with neighboring generation headers before sharing code across generations; fields with the same semantic name may live at different offsets or have different reserved bits.

## Boundary Notes

- Line 2526 begins after the `GDC0_A2S_CNTL_SW2__STATIC_VC_ENABLE__SHIFT` and `STATIC_VC_VALUE__SHIFT` definitions. This chunk contains the remaining shifts and all masks for that register family.
- Line 4978 contains only `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD0SCH_DW3__DW3__SHIFT`; its `_MASK` definition is expected in the following chunk.
