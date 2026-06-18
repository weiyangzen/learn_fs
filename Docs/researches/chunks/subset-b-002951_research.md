# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 115516-117939

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants for PCI/PCIe configuration-space bitfields; it does not define functions, structs, variables, executable code, locks, allocation paths, or direct register accesses.

The slice starts inside the `BIF_CFG_DEV0_EPF0_VF24_1` virtual-function block at `PROG_INTERFACE`/class-code area, finishes the remainder of VF24, covers complete repeated blocks for `BIF_CFG_DEV0_EPF0_VF25_1` and `BIF_CFG_DEV0_EPF0_VF26_1`, and then begins `BIF_CFG_DEV0_EPF0_VF27_1`, stopping inside `VF27_1_MSI_MSG_CNTL` after the `MSI_MULTI_EN` shift. The source path sits under a `ceph-client` mirror, but this file is AMDGPU hardware metadata and has no Ceph or distributed-filesystem behavior.

## Purpose

The macros provide symbolic bit positions and masks for NBIO 2.3 SR-IOV virtual-function PCI configuration images. Each field is emitted in the generated pattern:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

The companion `nbio_2_3_offset.h` file supplies matching `cfgBIF_CFG_DEV0_EPF0_VF<n>_1_*` addresses. Runtime AMDGPU code combines offsets from that file with this shift/mask header and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Register Coverage

The opening VF24 fragment contains the rest of one VF config-space block. It starts after the earlier `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, and `REVISION_ID` definitions and covers class-code bytes, cache line, latency, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min/max latency, PCIe capability/control/status, MSI/MSI-X, vendor-specific PCIe extended capability, AER, ATS, and ARI fields.

The complete VF25 and VF26 blocks each include:

- Basic PCI header fields: vendor/device ID, command/status, revision and class code fields, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X fields: MSI capability linkage, message control, address/data, mask and pending fields, 64-bit MSI aliases, MSI-X capability linkage/control, table, and PBA encodings.
- Vendor-specific PCIe extended capability fields: enhanced capability header, vendor-specific header, and two vendor-specific data dwords.
- Advanced Error Reporting fields: AER capability header, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- ATS and ARI fields: capability-list headers, ATS capability/control, ARI capability, and ARI control.

The trailing VF27 fragment covers the same layout only from `VENDOR_ID` through the start of `MSI_MSG_CNTL`. It includes PCI header fields, BARs, PCIe capability and device/link control/status groups, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `MSI_CAP_LIST`, and the first three MSI message-control shifts. The VF27 MSI masks, MSI address/data fields, MSI-X, vendor-specific, AER, ATS, and ARI fields continue in the next chunk.

## Important Macro Families

`*_COMMAND__*` and `*_STATUS__*` encode standard PCI command/status bits such as I/O access, memory access, bus mastering, parity/SERR handling, interrupt disable, capability-list presence, abort conditions, system error, and parity error.

`*_BASE_ADDR_[1-6]__BASE_ADDR_*`, `*_ROM_BASE_ADDR__BASE_ADDR_*`, and MSI-X table/PBA fields describe address or offset-bearing registers. These masks do not express all PCI semantics by themselves; consumers still need to preserve reserved bits and interpret BAR sizing, table BIR, and table offset rules correctly.

`*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` cover PCIe device capability and control state such as max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, phantom functions, FLR capability/initiation, completion timeout controls, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tag support, emergency power-reduction bits, and transaction/error status.

`*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` describe link speed/width capability and negotiated status, ASPM/power-management controls, link disable/retrain, common clock, autonomous width/speed controls, target link speed, compliance/de-emphasis controls, link equalization status, DRS, and downstream/component presence state.

`*_MSI_*` and `*_MSIX_*` map interrupt capability programming fields: MSI enable, multiple-message capability and enable, 64-bit capability, per-vector masking, message address/data, mask/pending registers, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.

`*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL__*`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` map AER status, masks, severity, ECRC, multiple-header recording, header logging, and TLP prefix logging. Error families include DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked.

`*_PCIE_ATS_*` and `*_PCIE_ARI_*` provide virtualization and IOMMU-related fields: ATS invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, ARI MFVC/ACS function-group support, next-function number, function-group enables, and selected function group.

## Control Flow

There is no runtime control flow in this chunk. The only compile-time behavior is that including translation units receive the generated macro names. Runtime flow is supplied by AMDGPU code that selects a config-space offset, reads a register value, applies these masks and shifts directly or through helper macros, and then writes an updated value or decodes status for higher-level PCIe, SR-IOV, reset, interrupt, power, or diagnostics paths.

Typical consumers include NBIO/BIF initialization, PCIe link policy, SR-IOV VF lifecycle handling, MXGPU virtualization support, MSI/MSI-X programming, AER diagnostics, ATS/ARI setup, FLR/reset paths, and suspend/resume or runtime power transitions.

## State And Persistence Behavior

This header stores no software state and persists nothing. It describes hardware-backed PCI configuration state for NBIO virtual functions. Some represented values are static capabilities or identity fields, some are software-programmed controls, some are hardware-updated status bits, and some are sticky diagnostic or write-one-to-clear style PCIe/AER state.

State represented by these masks may be changed by PF setup code, guest drivers, the Linux PCI core, firmware, hardware link training, VF FLR, PF-driven VF teardown/recreation, interrupt setup, IOMMU/ATS policy, and PCIe error handling. The masks do not encode access permissions, reset defaults, ownership rules, side effects, or polling requirements; those rules come from PCIe/NBIO hardware documentation and the surrounding driver code.

VF25 and VF26 are complete within this chunk and can be compared locally as repeated layouts. VF24 and VF27 are boundary fragments and require adjacent chunks before making whole-VF conclusions.

## Dependencies And Integration Points

This generated header must stay synchronized with the NBIO register database and these companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h` for register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h` for reset/default values where generated.

In-tree translation units that include `nbio_2_3_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`. The relevant integration surfaces are AMDGPU NBIO register access, PCIe link control, SR-IOV/MXGPU VF management, interrupt delivery, AER logging, ATS/ARI exposure, power-management policy, and reset handling.

The register naming mirrors standard PCI and PCIe capability layouts, so generic Linux PCI core policy and platform firmware behavior also matter for command/status, BARs, PCIe capabilities, MSI/MSI-X, AER, ATS, ARI, LTR, OBFF, completion timeout, link status, and FLR semantics.

## Risks And Edge Cases

- Generated macro drift is the main risk. A stale shift or mask can compile cleanly while decoding or modifying the wrong hardware bit.
- The repeated VF blocks are mechanically similar. Off-by-one suffix mistakes around VF24, VF25, VF26, and VF27 can silently point code or diagnostics at the wrong VF config image.
- This chunk has artificial boundaries. It starts after the beginning of VF24 and ends inside VF27 MSI message control, so final file-level research must merge adjacent chunks for complete VF24 and VF27 coverage.
- Untyped `#define` constants make width mistakes easy. Consumers need to respect whether a field belongs to an 8-bit, 16-bit, or 32-bit PCI config register despite many literals using the same `L` suffix style.
- PCIe control fields are sensitive. Incorrect values for FLR, link disable/retrain, max payload, max read request, completion timeout, relaxed ordering, no-snoop, LTR, OBFF, ARI, ATS, autonomous speed/width disable, or target link speed can cause enumeration failures, DMA ordering bugs, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields affect interrupt delivery. Mask, pending, 64-bit alias, table offset/BIR, or message address/data mistakes can cause lost, misrouted, or unexpectedly masked interrupts.
- AER status, mask, severity, header log, and prefix log registers have different semantics despite similar names. Generic read/modify/write handling can clear diagnostic evidence, leave errors masked, or misclassify severity.
- ATS and ARI fields are virtualization-sensitive. Incorrect ATC enable/STU, invalidate capability interpretation, next-function number, or function-group controls can affect IOMMU translation caching, VF enumeration, and function isolation.
- BAR, ROM, MSI-X table, and PBA fields carry address or offset encodings where low bits may be reserved or selectors. Code should preserve reserved/selector bits according to PCIe layout.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 consumers enabled; missing, renamed, or duplicate macros should surface in files including `nbio_2_3_sh_mask.h`.
- Compare VF25 and VF26 layouts against each other, against neighboring VF blocks, and against `nbio_2_3_offset.h` to confirm register names, order, widths, and repeated VF stride stay synchronized.
- Use static generated-header checks against the AMD hardware register database to catch mask/shift drift before runtime.
- Boot affected hardware and inspect PCIe config exposure for VFs in this range: identity/header fields, BARs, capability list, PCIe device/link capabilities, MSI/MSI-X, AER, ATS, and ARI should decode as expected.
- In SR-IOV or MXGPU configurations, create and remove VFs around VF24 through VF27, bind guest drivers, exercise VF FLR, and verify VF isolation, enumeration, reset, ATS/ARI behavior, and interrupt delivery.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI/MSI-X layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout, LTR/OBFF state, and FLR completion.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs decode to the expected PCIe errors.
- For ATS-capable configurations, exercise IOMMU/ATS enablement and invalidation paths; translation faults, stale DMA mappings, or inconsistent ATC behavior can point to ATS field issues.

## Chunk Notes

- Lines 115516-116149 are the tail of `BIF_CFG_DEV0_EPF0_VF24_1`, beginning in the class/header area and ending at ARI control.
- Lines 116150-116845 are a complete `BIF_CFG_DEV0_EPF0_VF25_1` address block.
- Lines 116846-117541 are a complete `BIF_CFG_DEV0_EPF0_VF26_1` address block.
- Lines 117542-117939 begin `BIF_CFG_DEV0_EPF0_VF27_1` and stop inside `MSI_MSG_CNTL`; remaining VF27 MSI, MSI-X, vendor-specific, AER, ATS, and ARI fields are outside this work item.
