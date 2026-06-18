# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 149939-152374

## Scope

This chunk is a generated AMD NBIO 7.7.0 register field mask header section. It contains no executable C logic; it exports `__SHIFT` and `_MASK` macros for fields in PCI/PCIe configuration-space registers surfaced through the NBIO/BIF register map. The assigned range starts immediately after the `BIF_CFG_DEV1_EPF1_1_VENDOR_CAP_LIST` length field, covers the remainder of the `BIF_CFG_DEV1_EPF1_1` endpoint-function 1 capability space, switches at line 150809 to `addressBlock: nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, and then covers `BIF_CFG_DEV2_EPF0_1` standard PCI configuration, PCIe base/extended capabilities, AER, VC, BAR, DPA, ACS/PASID/LTR/ARI/DLF, 16 GT/s PHY, and lane margining fields through most of lane 10 margining status.

The line range ends mid-register at `BIF_CFG_DEV2_EPF0_1_LANE_10_MARGINING_LANE_STATUS__LANE_10_USAGE_MODEL_STATUS_MASK`; the final `LANE_10_MARGIN_PAYLOAD_STATUS_MASK` is on the following line outside this chunk and should be handled by the adjacent chunk. The companion address constants are in `nbio_7_7_0_offset.h`; this file supplies only bit positions and masks.

## Purpose

The macros in this slice encode the hardware ABI for PCIe config-space fields on NBIO 7.7.0. AMDGPU code can use symbolic register and field names instead of hard-coded bit numbers when reading or composing values with the common register helpers.

The covered fields describe two related surfaces:

- The tail of `BIF_CFG_DEV1_EPF1_1`, including power-management capability, PCIe device/link capabilities and controls, MSI/MSI-X, a SATA capability block, vendor-specific extended capability, AER, enhanced BAR control, power budget, dynamic power allocation, ACS, PASID, and ARI.
- The beginning and most of the advanced capability set for `BIF_CFG_DEV2_EPF0_1`, including standard vendor/device/command/status/header/BAR fields, PM/PCIe capability fields, MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, enhanced BAR control, power budget, DPA, secondary PCIe link/lane equalization controls, ACS, PASID, LTR, ARI, data-link feature, 16 GT/s PHY equalization/status, and PCIe lane margining through lane 10 status.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The important interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` is the right-shift value for a field.
- `<REGISTER>__<FIELD>_MASK` is the unshifted field mask.
- Comment anchors such as `//BIF_CFG_DEV2_EPF0_1_DEVICE_CNTL` group all field macros belonging to one logical register.
- The companion offset header provides `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX`; the shared register stem lets `REG_GET_FIELD` and `REG_SET_FIELD` combine address, mask, and shift definitions.

Operationally important macro groups in this range include:

- `BIF_CFG_DEV1_EPF1_1_PMI_*`, `PCIE_CAP*`, `DEVICE_*`, and `LINK_*`: PM state/PME controls, PCIe device type, payload/read-request sizing, FLR initiation, error enables/status, ASPM/link retrain/common-clock controls, negotiated speed/width, completion-timeout controls, atomic operation controls, LTR, OBFF, 10-bit tags, DRS, crosslink, and 8 GT/s equalization status.
- `BIF_CFG_DEV1_EPF1_1_MSI_*` and `MSIX_*`: MSI enable/vector count, 64-bit address/data variants, per-vector mask/pending dwords, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- `BIF_CFG_DEV1_EPF1_1_SATA_*`: SATA capability and index/data-pair fields, including revision, BAR location, BAR offset, IDP index, and IDP data.
- `BIF_CFG_DEV1_EPF1_1_PCIE_ADV_ERR_*`, `PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_HDR_LOG*`, and `PCIE_TLP_PREFIX_LOG*`: AER extended-capability header, uncorrectable status/mask/severity, correctable status/mask, first-error pointer, ECRC controls, multi-header receive controls, TLP prefix log presence, completion-timeout log capability, and captured TLP header/prefix logs.
- `BIF_CFG_DEV1_EPF1_1_PCIE_BAR[1-6]_*`, `PCIE_PWR_BUDGET_*`, and `PCIE_DPA_*`: per-BAR fixed-size/address-assignment and reset/disable/invalidate controls, power-budget selector/data/capability, DPA transition latency, substate count, power allocation scale, enable/status, and eight substate power allocations.
- `BIF_CFG_DEV1_EPF1_1_PCIE_ACS_*`, `PCIE_PASID_*`, and `PCIE_ARI_*`: source validation, translation blocking, peer-to-peer redirect/completion redirect, upstream forwarding, egress control, direct translated P2P, PASID enable/width/permission bits, and ARI function grouping/next-function fields.
- `BIF_CFG_DEV2_EPF0_1_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class-code/header/BIST/BAR, adapter ID, ROM base, interrupt, and capability pointer fields: the standard PCI configuration header for device 2 endpoint function 0.
- `BIF_CFG_DEV2_EPF0_1_PCIE_VC_*`: virtual-channel extended capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields, including arbitration table offsets, TC/VC maps, load/selection controls, and negotiation pending status.
- `BIF_CFG_DEV2_EPF0_1_PCIE_SECONDARY_*` and `PCIE_LANE_[0-15]_EQUALIZATION_CNTL`: secondary PCIe link control, lane error status, and per-lane downstream/upstream 8 GT/s TX preset and RX preset-hint fields.
- `BIF_CFG_DEV2_EPF0_1_PCIE_LTR_*`, `PCIE_DLF_*`, `DATA_LINK_FEATURE_*`, `PCIE_PHY_16GT_*`, `LINK_STATUS_16GT`, parity mismatch status, and `LANE_[0-15]_EQUALIZATION_CNTL_16GT`: latency tolerance reporting, data-link feature exchange, 16 GT/s equalization completion/phase status, parity mismatch reporting, and per-lane 16 GT/s DSP/USP TX presets.
- `BIF_CFG_DEV2_EPF0_1_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and lane margining `CNTL`/`STATUS` fields for lanes 0 through 10: margining readiness plus receiver number, margin type, usage model, and payload command/status fields. Lane 10 status is incomplete in this exact chunk due to the line boundary.

## Control Flow

This header contributes no runtime control flow. Its compile-time flow is indirect:

1. NBIO 7.7 code includes `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`.
2. Driver code reads a register through the AMDGPU/SOC15/NBIO access layer.
3. Code decodes or updates fields with helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, which depend on the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` spellings.
4. Updated values are written back through the matching register accessor when the field is writable.

For this chunk, most definitions describe PCIe configuration-space capability fields rather than hot-path display or memory-management logic. They still define the low-level ABI for reset, link training, interrupt delivery, error reporting, virtualization isolation, power management, and diagnostics.

## State And Persistence Behavior

The macros are stateless source constants. The hardware fields they describe have several state classes:

- Capability descriptors: vendor/device IDs, class-code fields, PCIe/extended capability headers, device/link capability registers, BAR capabilities, VC capabilities, ACS/PASID/LTR/ARI capability registers, DLF/16 GT/s/margining capability headers, and power-budget/DPA capability fields are generally hardware-defined descriptors.
- Driver- or firmware-programmed controls: PCI command bits, PM power state/PME enables, device error enables, payload/read-request size, FLR initiation, link disable/retrain/common-clock/ASPM controls, MSI/MSI-X enables and masks, BAR reset/disable/invalidate controls, DPA controls, VC resource controls, ACS/PASID/ARI controls, LTR-related enables, DLF exchange enable, equalization presets, and lane margining control payloads can be written as part of initialization, recovery, diagnostics, or feature enablement.
- Latched or negotiated status: PCI status bits, device/link status, AER correctable/uncorrectable status, AER header and TLP-prefix logs, DPA status, VC negotiation pending status, lane error status, 8 GT/s and 16 GT/s equalization phase status, parity mismatch status, data-link feature status, margining readiness, margining software-ready, and per-lane margining status reflect hardware events or negotiated link state.
- Packed fields: many logical registers share one 16- or 32-bit dword, including vendor/device ID, command/status, adapter ID, ACS capability/control, PASID capability/control, ARI capability/control, DPA status/control, and repeated lane/equalization/margining fields.

Persistence across suspend/resume, GPU reset, FLR, or PCIe hot reset is not handled in this header. It depends on hardware reset behavior and AMDGPU initialization/save-restore paths that use these constants.

## Dependencies And Integration Points

This generated file depends on the AMD register-header convention used under `drivers/gpu/drm/amd/include/asic_reg`. It is coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which provides the address and `BASE_IDX` symbols for the same register stems.
- AMDGPU register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, which require exact mask/shift macro names.
- NBIO/SOC15 register accessors in the AMDGPU driver stack, including paths that read or write NBIO PCIe/BIF registers for ASIC-specific initialization and diagnostics.
- Linux PCIe concepts for PM, MSI/MSI-X, AER, ACS, PASID, LTR, ARI, VC, DLF, 8 GT/s and 16 GT/s equalization, and PCIe link margining.

The `addressBlock: nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp` marker is a key integration boundary. It shows that subsequent `BIF_CFG_DEV2_EPF0_1_*` macros belong to a different endpoint-function block than the preceding `BIF_CFG_DEV1_EPF1_1_*` macros. Adjacent chunk research must preserve this boundary when reconciling the full source file.

## Risks

- Bitfield drift from the hardware register source is high impact. A wrong shift or mask can silently enable the wrong PCIe feature, miss or clear the wrong AER/status bit, corrupt MSI/MSI-X programming, alter BAR behavior, or misreport link state.
- Prefix mistakes are easy in this file because `BIF_CFG_DEV1_EPF1_1_*` and `BIF_CFG_DEV2_EPF0_1_*` define many similarly named registers with identical or near-identical layouts. Matching masks to the wrong endpoint/function may appear to work until a field diverges or an address differs.
- The assigned chunk starts and ends inside larger logical blocks. It starts after the first part of `VENDOR_CAP_LIST` and ends before the final lane 10 margining status payload mask. Merge/reconciliation must not infer that these logical registers are complete solely from this chunk.
- Status, mask, and severity AER registers use very similar field names. Confusing `*_STATUS`, `*_MASK`, and `*_SEVERITY` changes error handling semantics, not just decoding.
- Repeated BAR, DPA substate, VC resource, equalization lane, 16 GT/s lane, and margining lane definitions are prone to off-by-one generator/copy errors. Lane-indexed fields must be checked for both register address alignment in the offset header and lane number alignment in the field stem.
- ACS, PASID, ARI, and VC controls affect isolation and routing. Misprogramming them can create peer-to-peer routing surprises, IOMMU/PASID mismatches, or virtualization/security isolation gaps.
- Link control, equalization, 16 GT/s, data-link feature, and margining fields interact with physical PCIe link training. Incorrect writes can destabilize the link or make diagnostics misleading.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware integration oriented:

- Build AMDGPU configurations that include NBIO 7.7 headers to ensure all expected macro names resolve.
- Compare this chunk against the AMD register generator source or register XML, especially at the `DEV1_EPF1` to `DEV2_EPF0` address-block transition and at the truncated lane 10 margining status boundary.
- Cross-check each register stem against `nbio_7_7_0_offset.h` so masks in this header align with the intended `reg...` address and `BASE_IDX`.
- Runtime PCIe sanity tests on NBIO 7.7 hardware should confirm vendor/device/class IDs, command/status behavior, BAR layout, capability traversal, negotiated link speed/width, MSI/MSI-X capability layout, and AER capability visibility.
- Error-injection or fault-log tests should verify AER uncorrectable/correctable status, mask, severity, first-error pointer, header log, and TLP-prefix log decoding.
- Reset, FLR, suspend/resume, and GPU recovery testing should watch command, PM, device control, link control/status, MSI/MSI-X, BAR, DPA, ACS/PASID/ARI, VC, and AER fields for expected defaults or restoration.
- PCIe link diagnostics should compare 8 GT/s and 16 GT/s equalization status, lane error/parity status, data-link feature exchange, and lane margining ready/status fields against observed link behavior.
