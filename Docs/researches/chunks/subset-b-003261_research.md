# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 4913-7394

## Scope

This chunk covers a generated NBIO 7.7.0 register shift/mask header section for AMDGPU PCIe configuration-space registers. It begins at the tail of `BIF_CFG_DEV0_EPF0_PCIE_LANE_13_EQUALIZATION_CNTL`, covers the end of the EPF0 PCIe enhanced capability region, then defines the AMD GPUIOV vendor-specific capability block, and finally starts the `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block for EPF1 PCI configuration space through `BIF_CFG_DEV0_EPF1_LANE_5_EQUALIZATION_CNTL_16GT`.

The range contains 2,104 `#define` entries: 1,051 `__SHIFT` values and 1,053 `_MASK` values. It is data-only generated hardware ABI material. There are no functions, structs, variables, loops, conditionals, or local storage in this chunk.

## Purpose

The chunk provides bitfield positions and masks for NBIO/BIF PCIe configuration registers. Driver code pairs these constants with register offsets from `nbio_7_7_0_offset.h` and with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

For this source tree, the direct NBIO 7.7 consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio/nbio_7_7_0_offset.h` and this `nbio/nbio_7_7_0_sh_mask.h`. That C file uses the same generated register style to implement NBIO operations for revision ID reads, memory-controller access enablement, doorbell aperture programming, interrupt-handler setup, HDP flush offsets, clock-gating control, light-sleep control, and register remapping. The exact bitfields in this chunk are mostly PCIe config-space capability definitions rather than the specific operational registers touched by `nbio_v7_7.c`, but they belong to the same generated NBIO register map and are available to any code adding EPF0/EPF1 PCIe capability handling.

## Important Macro Families

### EPF0 PCIe Capability Tail

The EPF0 portion continues lane equalization and then covers standard and extended PCIe capability fields:

- `BIF_CFG_DEV0_EPF0_PCIE_LANE_14_EQUALIZATION_CNTL` and `LANE_15_EQUALIZATION_CNTL` define 8.0 GT/s downstream/upstream transmit preset and receive preset hint fields. The immediate prior context shows lanes 8-13 use the same format, so this chunk completes the 16-lane 8 GT/s equalization table for EPF0.
- `PCIE_ACS_*` defines Access Control Services capability and control fields: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size.
- `PCIE_ATS_*`, `PCIE_PAGE_REQ_*`, and `PCIE_PASID_*` define Address Translation Services, Page Request Interface, and PASID capability/control/status fields. These are the PCIe-side descriptors for IOMMU/GPU virtual address integration.
- `PCIE_MC_*` defines multicast capability, enable/control, multicast address, receive, block-all, and block-untranslated masks.
- `PCIE_LTR_*` defines Latency Tolerance Reporting capability fields for snooped and non-snooped latency values and scales.
- `PCIE_ARI_*` defines Alternative Routing-ID Interpretation capability/control fields.
- `PCIE_SRIOV_*` defines SR-IOV capability/control/status and VF enumeration/configuration fields, including initial/total/current VF counts, function dependency link, first VF offset, VF stride, VF device ID, page size fields, VF BAR base registers 0-5, and VF migration-state array offset.
- `DATA_LINK_FEATURE_*`, `PCIE_PHY_16GT_*`, `LINK_*_16GT`, parity mismatch status, and `LANE_0..15_EQUALIZATION_CNTL_16GT` define 16.0 GT/s link feature/status and per-lane transmit preset fields.
- `PCIE_MARGINING_*` and `LANE_0..15_MARGINING_LANE_*` define port/lane margining control and status fields, including payloads, ready/soft-ready status, receiver number, margin type, usage model, sample reporting, voltage/time margin values, and max lanes.
- `PCIE_VF_RESIZE_BAR*` defines resizable BAR capability/control fields for virtual-function BARs 1-6.

These EPF0 fields describe endpoint function 0's PCIe config-space advertised capabilities and control bits. Some are read-only capability descriptors from the driver perspective, while control/status fields may be programmed or polled by firmware, platform code, or future driver paths.

### AMD GPUIOV Vendor-Specific Capability

The middle of the chunk defines the global `PCIE_VENDOR_SPECIFIC_*_GPUIOV` capability block. The sibling offset header maps this block around config offsets `0x0584` and following, for example `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV`, `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW0`, and `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF0_FB`.

Important fields include:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV` for enhanced capability ID/version/next pointer and vendor-specific ID/revision/length.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_SRIOV_SHADOW` for VF enable and VF number shadow state.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_RESET_CONTROL` for soft PF FLR control.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW0` and `DW1` for hypervisor/VM mailbox data, valid, ack, VF index, and per-VF transmit/receive-valid bits for VFs 0-15.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_CONTEXT` for context size/location/offset.
- `PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_TOTAL_FB` and `VF0_FB` through `VF15_FB` for total framebuffer availability/consumption and per-VF framebuffer size/offset descriptors.
- `UVDSCH_DW0..DW8`, `VCESCH_DW0..DW8`, and `GFXSCH_DW0..DW8` for scheduler data words associated with media and graphics scheduling in a GPUIOV environment.

This is the most virtualization-specific part of the chunk. It exposes PF/VF coordination surfaces and resource partition descriptors that connect PCIe config-space enumeration to AMDGPU SR-IOV runtime state elsewhere in the driver, such as `amdgpu_virt.c`, SR-IOV message table parsing, and VF/PF mode checks.

### EPF1 PCI Configuration Space

The EPF1 address block starts at line 5990. It defines the ordinary PCI header and capability chain for endpoint function 1:

- Basic PCI header fields: vendor/device IDs, `COMMAND`, `STATUS`, revision, class code, cache line, latency, header type, BIST, BARs 1-6, CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- Power management capability/status-control fields: PME support, D1/D2 support, aux current, DSI, power state, PME enable/status, data select/scale, and B2/B3 support.
- PCIe capability fields: device/port type, slot interrupt message number, device capabilities/control/status, link capabilities/control/status, device/link capabilities 2, and link control/status 2.
- MSI and MSI-X capability fields: message control, address/data registers, masks, pending bits, MSI-X table, and PBA descriptors.
- Device serial number, vendor-specific capability header, and vendor-specific data dwords.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- Resizable BAR capability/control for BARs 1-6.
- Power budget and Dynamic Power Allocation fields.
- Secondary PCIe capability, lane error status, and 8 GT/s equalization controls for lanes 0-15.
- ACS, ATS, Page Request, PASID, multicast, LTR, ARI, SR-IOV, data-link feature, 16 GT/s PHY/link/status/parity, and initial 16 GT/s per-lane equalization masks.

EPF1 mostly mirrors EPF0's PCIe capability structure, but this chunk includes EPF1 from the base PCI header onward while EPF0 is already in its extended capability tail. The offset header confirms example EPF1 offsets such as `cfgBIF_CFG_DEV0_EPF1_PCIE_UNCORR_ERR_STATUS` at `0x0154` and `cfgBIF_CFG_DEV0_EPF1_PCIE_SRIOV_CONTROL` at `0x0338`.

## APIs, Types, and Functions

This header contributes preprocessor constants only. Its effective API is the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit index used when shifting a field value into or out of a register word.
- `<REGISTER>__<FIELD>_MASK` gives the masked bit range in the register word.

The generated names are consumed by macro-based register helpers rather than by ordinary typed C APIs. The critical external dependency is that the register name portion must match the names used by offset headers and helper macros. For example, a caller that reads `cfgBIF_CFG_DEV0_EPF1_PCIE_SRIOV_CONTROL` or an MMIO/PCIe-port alias of that register would use `BIF_CFG_DEV0_EPF1_PCIE_SRIOV_CONTROL__SRIOV_VF_ENABLE_MASK` and related `__SHIFT` constants to interpret or compose the value.

No type safety is provided by this layer. All values are untyped integer constants, commonly suffixed with `L`, and correctness depends on matching the correct register macro family to the correct address.

## Control Flow

There is no executable control flow in the chunk. Runtime flow appears in consumers:

1. Select an NBIO register address from `nbio_7_7_0_offset.h` or an SOC15 register-offset macro.
2. Read a 32-bit register or config-space value.
3. Use this header's masks and shifts directly, or indirectly through `REG_GET_FIELD`/`REG_SET_FIELD`, to decode or update fields.
4. Write the modified value back if the field is writable.
5. Poll status bits for command/status style fields such as page-request status, AER status, data-link feature valid bits, 16 GT/s equalization status, lane margining ready/status bits, mailbox ack/valid bits, or SR-IOV migration status.

Control/status fields in this chunk imply hardware sequencing even though the header does not implement it. Examples include PRI reset/enable, SR-IOV VF enable and memory-space enable, GPUIOV mailbox valid/ack exchange, data-link feature exchange enable/valid, margining command/status exchanges, AER error status logging, and link equalization status.

## State and Persistence

The state described by these masks lives in hardware PCIe configuration space and vendor-specific capability registers, not in kernel memory owned by this header. Persistence and mutability depend on the field:

- Capability fields such as capability IDs, versions, next pointers, supported features, maximum payload sizes, link speed/width capabilities, page sizes, total VF counts, and supported BAR sizes are generally hardware/firmware-defined descriptors.
- Control fields such as command bits, power management state, link controls, ACS/ATS/PASID/PRI enables, MSI/MSI-X enables, SR-IOV VF enable/MSE, ARI enables, DPA controls, margining commands, and GPUIOV reset/mailbox bits are writable hardware state when access policy allows.
- Status/log fields such as PCI status, device/link status, AER uncorrectable/correctable status, header/TLP prefix logs, page-request status, 16 GT/s parity mismatch status, lane error status, margining status, and mailbox ack/valid bits are hardware-updated observations and may include write-one-to-clear or latch semantics depending on the PCIe specification and ASIC behavior.
- SR-IOV and GPUIOV resource fields represent virtualization configuration state. In VF mode many related registers may be read-only, inaccessible, or programmed by the host/PF rather than the guest driver. This matches broader AMDGPU patterns where SR-IOV paths in `amdgpu_virt.c`, hub setup, reset, and power management avoid direct programming of host-owned registers.

Because this header is generated, persistence also has a source-control dimension: the constants should remain synchronized with the ASIC register database and with the corresponding offset header. Manual one-off edits risk creating silent hardware decode errors.

## Dependencies and Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` supplies the register offsets for these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and binds NBIO 7.7 operations into `nbio_v7_7_funcs`.
- AMDGPU register helper macros provide the read/modify/write and field set/get mechanics.
- PCIe, AER, MSI/MSI-X, ACS, ATS, PRI, PASID, LTR, ARI, SR-IOV, DPA, DLF, PHY 16 GT/s, and lane margining semantics come from the PCIe hardware specification and AMD ASIC definitions.

Important integration surfaces:

- PCIe link training and diagnostics: 8 GT/s and 16 GT/s equalization, lane error status, parity mismatch, and margining masks.
- Interrupt configuration: MSI and MSI-X message control, data, mask, pending, table, and PBA fields.
- Error reporting and RAS diagnostics: AER status/mask/severity, header log, TLP prefix log, correctable/uncorrectable error masks.
- IOMMU and process address-space support: ACS, ATS, PRI/page request, and PASID fields align with GPU VM/KFD PASID handling elsewhere in AMDGPU.
- Virtualization: SR-IOV capability/control and the AMD GPUIOV vendor-specific block connect to PF/VF resource partitioning, mailbox signaling, VF framebuffer allocation, and reset coordination.
- Power and latency: PM capability/status, LTR, power budget, and DPA masks interact with platform PCIe power management.

## Risks

- Register/field mismatch: using an EPF0 mask on EPF1 data, or a 16 GT/s lane mask on the 8 GT/s equalization register, can produce valid-looking but incorrect bit manipulation.
- Offset/header drift: the mask header and `nbio_7_7_0_offset.h` must be regenerated together. A changed register layout with stale masks can corrupt unrelated bits.
- Access-policy violations under SR-IOV: guests may not be allowed to program PF-owned SR-IOV, GPUIOV, hub, or BAR/resource fields. Writes that work in bare-metal mode can fail, trap, or be ignored in VF mode.
- Capability/control confusion: many similarly named fields have separate `CAP`, `CNTL`, `STATUS`, `MASK`, and `SEVERITY` registers. Treating advertised support bits as enable bits, or status bits as durable configuration, can break PCIe enumeration or diagnostics.
- Write-clear and latch semantics: AER, status, mailbox, margining, and page-request fields may have side effects on write. Generic read/modify/write code must respect the hardware clearing model.
- Width assumptions: some masks are 16-bit PCI config fields embedded in 32-bit constants, while others span full 32-bit registers. Callers must use the correct access width and alignment for config-space operations.
- Generated-name fragility: helper macros rely on exact register and field tokens. Renaming or normalizing these constants manually can break macro expansion without obvious runtime clues.

## Test Signals

Useful validation for changes touching this chunk or consumers includes:

- Build coverage for AMDGPU with NBIO 7.7 enabled, proving all generated macro names still compile with `nbio_v7_7.c` and any PCIe/SR-IOV users.
- Static comparison against the ASIC register source or regenerated header output, especially for paired `__SHIFT`/`_MASK` values and EPF0/EPF1 duplicated capability blocks.
- PCIe enumeration checks on NBIO 7.7 hardware: `lspci -vv` should show coherent capability chains, MSI/MSI-X, AER, ACS/ATS/PASID/PRI, SR-IOV, LTR, and link capability/status data.
- Bare-metal and SR-IOV smoke tests. In SR-IOV, verify VF discovery, VF BAR sizing, mailbox/resource table exchange, and that guest paths avoid host-owned register writes.
- Link training diagnostics at 8 GT/s and 16 GT/s: equalization complete/phase status, lane error status, parity mismatch status, and margining status should be readable and stable.
- AER injection or platform error-log tests where available, checking that status, mask, severity, header log, and TLP prefix log fields decode correctly.
- Runtime AMDGPU probes around NBIO setup: revision ID, memory size, doorbell aperture setup, interrupt setup, HDP flush offsets, and clock-gating state should continue to behave normally because they rely on the same generated register-header integration model.
