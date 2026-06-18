# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 21953-24399

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, storage definitions, or executable control flow in the chunk. The constants describe bit positions and masks for PCIe configuration-space fields under `BIF_CFG_DEV0_EPF0_*` and the beginning of `BIF_CFG_DEV0_EPF1_*`.

The surrounding in-tree consumer for this ASIC generation is `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio/nbio_2_3_sh_mask.h` together with the matching offset/default headers and uses these masks through helpers such as `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, and `WREG32_SOC15`.

## Purpose

The chunk gives the AMDGPU driver symbolic access to fields in Navi-era NBIO/BIF PCIe registers. It lets driver code compose, extract, enable, disable, or test hardware-defined bitfields without hard-coding raw shifts and masks at each call site.

Major hardware areas covered:

- EPF0 PCIe Dynamic Power Allocation (DPA) capability, status, control, latency, and substate power allocation fields.
- EPF0 PCIe secondary extended capabilities, link equalization, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD vendor-specific GPUIOV fields.
- EPF0 GPUIOV interrupt, reset, hypervisor/VM mailbox, context, framebuffer partitioning, P2P-over-XGMI enablement, and per-engine scheduler descriptor fields for UVD, VCE, GFX, and UVD1.
- Start of EPF1 PCI configuration-space fields: IDs, command/status, class/revision, BARs, adapter IDs, ROM, interrupt pins, PM capability, PCIe capability, MSI/MSI-X, vendor-specific capability, virtual-channel capability, device serial number, AER, resizable BAR, and power-budget capability list.

## Important APIs, Types, And Constants

This chunk exports macros in the standard generated AMD register naming form:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Register comments such as `//BIF_CFG_DEV0_EPF0_PCIE_SRIOV_CONTROL` group the following shift/mask pairs by hardware register.

Important field families:

- DPA fields: `BIF_CFG_DEV0_EPF0_PCIE_DPA_CAP__SUBSTATE_MAX_MASK`, `TRANS_LAT_UNIT_MASK`, `PWR_ALLOC_SCALE_MASK`, `BIF_CFG_DEV0_EPF0_PCIE_DPA_STATUS__SUBSTATE_STATUS_MASK`, and `BIF_CFG_DEV0_EPF0_PCIE_DPA_CNTL__SUBSTATE_CNTL_MASK`.
- Link equalization fields: per-lane `BIF_CFG_DEV0_EPF0_PCIE_LANE_<0..15>_EQUALIZATION_CNTL__DOWNSTREAM_PORT_TX_PRESET_MASK`, RX preset hint masks, upstream TX preset masks, and upstream RX preset hint masks.
- ACS/ATS/PRI/PASID fields: `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`.
- SR-IOV fields: `BIF_CFG_DEV0_EPF0_PCIE_SRIOV_CONTROL__SRIOV_VF_ENABLE_MASK`, `SRIOV_VF_MSE_MASK`, `SRIOV_ARI_CAP_HIERARCHY_MASK`, VF count/stride/offset/device ID masks, supported/system page-size masks, and VF BAR base address masks.
- Gen4/16 GT/s fields: `BIF_CFG_DEV0_EPF0_LINK_STATUS_16GT__EQUALIZATION_COMPLETE_16GT_MASK`, phase success masks, per-lane 16 GT/s DSP/USP TX preset masks, and parity mismatch status masks.
- Margining fields: `BIF_CFG_DEV0_EPF0_MARGINING_PORT_STATUS__MARGINING_READY_MASK` and per-lane `MARGINING_LANE_CNTL`/`MARGINING_LANE_STATUS` receiver, margin type, usage model, and payload masks.
- VF resize BAR fields: `BIF_CFG_DEV0_EPF0_PCIE_VF_RESIZE_BAR[1-6]_{CAP,CNTL}` masks for supported BAR sizes, selected BAR index, total number, and configured size.
- GPUIOV fields: `BIF_CFG_DEV0_EPF0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_INTR_ENABLE`, `INTR_STATUS`, `RESET_CONTROL`, `HVVM_MBOX_DW0`, `HVVM_MBOX_DW1`, `HVVM_MBOX_DW2`, `CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, `P2P_OVER_XGMI_ENABLE`, `VF<0..30>_FB`, and scheduler descriptors for UVD/VCE/GFX/UVD1.
- EPF1 PCIe capability fields: `BIF_CFG_DEV0_EPF1_COMMAND`, `STATUS`, `PMI_*`, `DEVICE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, VC, DSN, AER, and BAR enhancement masks.

There are no C types declared in this chunk. Type safety and register width assumptions come from the AMDGPU register helper layer and the C integer constants themselves.

## Control Flow

The header has no runtime control flow. Runtime effects occur only when included driver code passes the constants to register helper macros.

Typical usage pattern in this ASIC generation:

1. Driver code reads a 32-bit register through `RREG32_PCIE`, `RREG32_SOC15`, or `RREG32`.
2. `REG_SET_FIELD` or explicit mask/shift operations update a field using the `__SHIFT` and `_MASK` macros from this header.
3. Driver code writes the modified value back through `WREG32_PCIE`, `WREG32_SOC15`, or `WREG32`.

For example, `nbio_v2_3.c` uses the same header family to program NBIO link/power behavior: it updates `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK` when enabling/disabling LTR, programs link-control masks for ASPM, and selects the `mmPCIE_INDEX2`/`mmPCIE_DATA2` indirect PCIe access registers. This chunk extends that same mechanism to later PCIe capability and virtualization registers.

## State And Persistence

The macros are compile-time constants and do not persist state. The state they describe is hardware state in PCIe configuration registers and vendor-specific NBIO/BIF registers.

Persistence characteristics depend on the underlying field:

- Capability fields such as IDs, class codes, supported link speeds, supported page sizes, BAR size support, and DPA capability values are generally hardware/strap/firmware-defined and exposed as read-only or read-mostly PCIe config state.
- Control fields such as DPA substate control, ACS/ATS/PASID enable bits, SR-IOV VF enable/MSE bits, TPH enablement, margining lane controls, VF resize BAR controls, GPUIOV interrupt enables, GPUIOV reset control, and EPF1 device/link/MSI/MSI-X control fields can be software-visible mutable hardware state.
- Status and log fields such as lane error status, 8 GT/s and 16 GT/s equalization status, margining status, GPUIOV interrupt status, AER status, header logs, and TLP prefix logs are transient diagnostic state supplied by hardware.
- GPUIOV framebuffer partition and scheduler fields encode virtualization resource allocation state. Their persistence is tied to PF/hypervisor programming, SR-IOV lifecycle, GPU reset, and firmware/hardware ownership rules.
- Reset, FLR, secondary bus reset, D3/D0 transitions, and GPU reset paths can clear or reinitialize many of these registers. The header itself does not enforce restore ordering.

## Dependencies

Direct dependencies:

- Matching NBIO 2.3 offset/default headers, especially `nbio_2_3_offset.h`, provide register addresses such as `mm...` or `smn...` symbols. This chunk only provides field layout.
- AMDGPU register helpers in the driver provide the access semantics: `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_*`, `WREG32_*`, and `SOC15_REG_OFFSET`.
- Linux PCI/PCIe semantics define many fields mirrored here: PM, PCIe capabilities, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, TPH, LTR, ARI, VC, DSN, DPA, lane margining, and link equalization.
- AMD virtualization firmware/hypervisor interfaces consume or populate the GPUIOV-specific register blocks.

Implicit dependencies and assumptions:

- The constants must match the NBIO 2.3 hardware register specification exactly.
- The register width is effectively 32 bits for the generated masks in this chunk, even when a hardware register represents a 16-bit PCI config field.
- Callers must pair these masks with the correct register address and access path. A valid mask applied to a different register can silently corrupt unrelated hardware state.

## Integration Points

This chunk integrates with the AMDGPU NBIO and PCIe support in several ways:

- `nbio_v2_3.c` includes this header and uses the same generated constants for NBIO initialization, ASPM/LTR setup, light sleep, clock gating, doorbell aperture setup, HDP flush offset reporting, PCIe index/data offset reporting, and revision-id extraction.
- AMDGPU PCIe register access code can use NBIO-provided index/data offsets to expose or inspect PCIe register state through debug/sysfs paths.
- Linux PCI core and platform firmware interact with overlapping PCI config-space fields, especially command/status, PM, link control/status, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and BAR sizing fields. AMDGPU code must avoid racing or overriding policy owned by the PCI core unless an ASIC workaround requires it.
- SR-IOV and GPUIOV integration touches PF/VF lifecycle, mailbox handshakes, interrupt routing, per-VF framebuffer partitions, engine scheduling descriptors, and FLR/reset signaling.
- Power management integration uses DPA, LTR, link-status, link-control, data-link-feature, and ASPM-related fields to coordinate GPU power savings with PCIe link behavior.
- Diagnostics and service paths can use lane error, equalization, margining, AER, header log, and TLP prefix fields to identify PCIe reliability problems.

## Risks

- **Generated-header drift:** If a mask or shift is wrong for NBIO 2.3 silicon, every caller using `REG_SET_FIELD` or `REG_GET_FIELD` will read or write the wrong bits while still compiling cleanly.
- **Register/address mismatch:** This header does not contain register addresses. Using an EPF0 field mask with an EPF1 register, or using an EPF1 mask with EPF0 offsets, can modify unrelated PCI config state.
- **PCI core ownership conflicts:** Fields such as MSI/MSI-X, SR-IOV, AER, ACS, ATS, PASID, BAR sizing, and PM/link control also have Linux PCI subsystem ownership. Direct AMDGPU writes must be constrained to hardware-required paths.
- **Virtualization safety:** GPUIOV fields expose PF/VF resource partitioning, mailbox state, per-VF framebuffer windows, interrupt enables/status, and FLR-like reset controls. Incorrect programming can break VF isolation, lose mailbox messages, or reset active guests.
- **Status clear semantics:** AER, interrupt status, lane error, margining, and log fields may be write-1-to-clear or otherwise side-effectful in hardware. Generic read/modify/write code must understand per-register semantics beyond the masks.
- **Link training sensitivity:** Equalization, margining, target speed, de-emphasis, compliance, and autonomous speed/width controls can destabilize the PCIe link if changed outside the expected link state.
- **Power-management regressions:** DPA, LTR, TPH, ASPM, and link low-power fields can interact with device latency, DMA completion latency, and platform link policy.

## Test Signals

Useful validation signals for changes that touch this chunk or code that uses it:

- Build coverage: the AMDGPU driver should compile with this header included, with no undefined macro or duplicate macro diagnostics.
- Register helper coverage: sites using `REG_SET_FIELD`/`REG_GET_FIELD` with these names should compile and produce expected bit values in simple unit-style checks or debug assertions where available.
- PCIe enumeration: `lspci -vv` should continue to report sane capabilities for the GPU, including link capability/status, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, and resizable BAR capability where supported.
- Runtime link behavior: link speed/width, ASPM/LTR state, and retraining/equalization status should remain stable across boot, suspend/resume, runtime power transitions, and GPU reset.
- SR-IOV/GPUIOV: PF enablement, VF creation/removal, VF driver load/unload, mailbox handshakes, FLR, per-VF framebuffer partitioning, and VF interrupt delivery should work without stale status bits or resource leaks.
- Error handling: AER injection or observed PCIe errors should map to the expected uncorrectable/correctable status, mask, severity, header log, and TLP prefix fields.
- Diagnostics: lane margining/equalization status and lane error counters should read coherently on hardware that exposes these capabilities.

## Chunk Notes

- The line range begins in the middle of `BIF_CFG_DEV0_EPF0_PCIE_DPA_ENH_CAP_LIST`; earlier lines likely contain the corresponding `CAP_ID__SHIFT`, `CAP_VER__SHIFT`, `NEXT_PTR__SHIFT`, and `CAP_ID_MASK`.
- The line range ends at `BIF_CFG_DEV0_EPF1_PCIE_PWR_BUDGET_ENH_CAP_LIST__CAP_VER_MASK`, so the EPF1 power-budget capability block continues in the next chunk.
- Because this is generated register metadata, the most important maintenance check is cross-file consistency: names in this header, register addresses in `nbio_2_3_offset.h`, and reset/default values in `nbio_2_3_default.h` must describe the same hardware revision.
