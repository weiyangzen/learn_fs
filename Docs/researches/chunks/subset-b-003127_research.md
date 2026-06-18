# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 12286-14755

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIF PCI configuration-space register images. The covered range starts in the middle of the `BIF_CFG_DEV0_EPF4` PCIe BAR capability/control section, spans the full `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp` address blocks, and ends partway through the `BIF_CFG_DEV2_EPF5_LINK_CAP` register.

The content is hardware metadata, not executable driver logic. AMDGPU code includes this file with matching generated offset/default/SMN headers so register-access helpers can encode and decode individual PCI configuration fields without open-coded bit numbers.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

Major macro groups in this chunk are:

- `BIF_CFG_DEV0_EPF4_PCIE_*`: the tail of endpoint function 4 on device 0, including BAR5/BAR6 sizing controls, power-budget enhanced capability/data/capability fields, Dynamic Power Allocation capability/status/control/substate power allocations, ACS capability/control, PASID capability/control, ARI capability/control, and Readiness Time Reporting enhanced capability plus `RTR_DATA1`/`RTR_DATA2`.
- `BIF_CFG_DEV2_EPF3_*`: a complete generated PCI config-space block for device 2 endpoint function 3. It includes standard PCI identity and command/status fields, BARs, subsystem IDs, ROM base, capability pointers, legacy interrupt fields, vendor capability, power-management capability/status, secondary bus reset number (`SBRN`), FLADJ, DBESL/DBESLD, PCIe capability/device/link/device2/link2 registers, MSI/MSI-X capability fields, SATA capability/index/data fields, PCIe vendor-specific enhanced capability registers, AER status/mask/severity/control/header-log/TLP-prefix-log fields, BAR enhanced capabilities, power budget, DPA, ACS, PASID, ARI, and RTR fields.
- `BIF_CFG_DEV2_EPF4_*`: the same broad schema for device 2 endpoint function 4, including the full standard PCI header, PM/PCIe/MSI/MSI-X/SATA/vendor-specific/AER/BAR/power-budget/DPA/ACS/PASID/ARI/RTR families.
- `BIF_CFG_DEV2_EPF5_*`: the beginning of device 2 endpoint function 5, from standard identity and command/status fields through PM capability/status, PCIe capability, device capability/control/status, and the first `LINK_CAP` shift fields.

Within the repeated PCIe capability areas, important fields include payload/read-request sizes, extended-tag/no-snoop/relaxed-ordering enables, FLR capability and initiation, transaction-pending and error-status bits, link speed/width/ASPM/clock-power-management/link-bandwidth fields, completion-timeout and atomic-op controls, MSI/MSI-X table and PBA location fields, AER uncorrectable/correctable error bitmaps, and enhanced BAR size/index fields.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is consumed at compile time by C code that performs MMIO, config-space, or indirect NBIO register accesses.

The implied hardware flows are:

1. PCI enumeration and device setup read identity, class-code, BAR, subsystem, capability-pointer, interrupt, MSI, MSI-X, and PCIe capability fields from the generated endpoint-function blocks.
2. Driver or firmware initialization can program command bits such as memory access, bus mastering, SERR, and interrupt disable; PCIe device-control bits such as max payload, max read request, relaxed ordering, no snoop, extended tags, and FLR; and link-control/link-control2 policy bits in adjacent chunks.
3. Power-management and DPA flows use PM capability/status, power-budget data, and DPA substate fields to advertise or control power states, substates, latency indicators, and allocated power values.
4. Reliability and diagnostics flows use AER status/mask/severity/header-log/TLP-prefix-log fields and device status bits to classify corrected, nonfatal, fatal, unsupported-request, completion-timeout, ECRC, ACS, and transaction-pending conditions.
5. Virtualization and multi-function routing features use ACS, PASID, and ARI capability/control fields to expose peer-to-peer controls, process address space IDs, and alternative routing interpretation.
6. Readiness Time Reporting fields advertise reset/DL-up/FLR/D3hot-to-D0 timings for PCIe software that needs bounded wait behavior after resets or power transitions.

The header does not perform sequencing, polling, clearing, locking, or value validation. Callers must pair these masks with the correct register address macros and follow PCIe/NBIO programming rules for write-one-to-clear status bits, capability traversal, FLR timing, AER logging, and reset ordering.

## State and Persistence

The header owns no mutable state, allocates no memory, and persists nothing. The represented state lives in NBIO/NBIF hardware configuration registers for multiple endpoint functions.

State categories represented here include:

- PCI identity/configuration state: vendor/device IDs, revision, class/subclass/program-interface, command/status, cache-line/latency/header/BIST, BARs, ROM BAR, subsystem IDs, and capability pointers.
- Interrupt state: legacy interrupt line/pin plus MSI/MSI-X message control, address/data, mask, pending, table, and PBA fields.
- PCIe capability state: device capability/control/status, link capability/control/status, second-generation device/link capability/control/status fields for endpoint functions covered completely in this chunk.
- Power state: PM capability/status, power-budget data, DPA capability/status/control, DPA substate power allocation, and readiness-time values.
- Error-reporting state: AER uncorrectable/correctable status and masks, uncorrectable severity, AER capability/control, captured header logs, and TLP prefix logs.
- Isolation/virtualization state: ACS, PASID, and ARI capability/control bits.
- Vendor/device-specific state: vendor-specific enhanced capability registers, SATA capability/index/data fields, DBESL/DBESLD, and FLADJ.

Retention across GPU reset, PCI FLR, secondary bus reset, suspend/resume, BACO, or runtime power transitions is not defined here. Those semantics are determined by hardware and by the AMDGPU/NBIO initialization paths that reprogram or reread these registers.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_offset.h` for register offsets matching these field names.
- `nbio_7_11_0_default.h` for reset/default values when generated for this ASIC block.
- Other chunks of `nbio_7_11_0_sh_mask.h`, because this work item starts inside `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` and ends before the full `BIF_CFG_DEV2_EPF5_LINK_CAP` mask set.

Likely integration areas in the AMDGPU tree include NBIO 7.11 setup code, SOC15 register access wrappers, PCIe capability/link management, SR-IOV or multi-function endpoint setup, AER/RAS handling, reset/FLR paths, and power-management code that reads or writes PM, DPA, power-budget, and readiness-time fields.

The macros are normally used through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC/NBIO read-modify-write wrappers. Correct use requires pairing a `*_SHIFT`/`*_MASK` macro from this file with the matching offset macro for the same register and endpoint function.

## Risks

- A wrong shift or mask silently targets the wrong PCI config bit. In this range that can affect BAR sizing, bus mastering, memory decoding, interrupt masking, FLR initiation, AER reporting, ACS isolation, PASID enablement, ARI routing, or link capability interpretation.
- The `DEV2_EPF3` and `DEV2_EPF4` blocks are highly repetitive. Generator or copy/paste drift can be hard to notice if tests exercise only one endpoint function.
- The chunk boundary starts with only the final masks for `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL`; the matching shifts and `BAR_INDEX_MASK` are in the previous chunk. Consumers must use the complete generated header, not this isolated range.
- The chunk boundary ends after `BIF_CFG_DEV2_EPF5_LINK_CAP__SURPRISE_DOWN_ERR_REPORTING__SHIFT`; remaining `LINK_CAP` shifts and all masks are in the next chunk.
- AER and device-status fields often have write-one-to-clear or latched semantics in hardware. Generic read-modify-write code that ignores those semantics can accidentally clear diagnostic state.
- Command/device-control bits such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `INITIATE_FLR`, payload size, max read request size, relaxed ordering, no snoop, and extended tags can cause functional failures if programmed without matching platform and link capabilities.
- ACS, PASID, and ARI fields are security/isolation-sensitive in virtualized or multi-function environments. Misprogramming can break peer-to-peer routing assumptions or DMA address-space isolation.
- BAR enhanced capability fields expose size-supported and size-control data; confusing capability versus control fields can produce invalid resource sizing or incorrect aperture programming.

## Test and Validation Signals

Useful validation is mostly generated-header and hardware integration coverage:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch malformed macro names, missing includes, or duplicate definitions.
- Mechanically verify every complete register in this range has expected `__SHIFT` and `_MASK` pairs, allowing the intentional split at the beginning of `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` and the end of `BIF_CFG_DEV2_EPF5_LINK_CAP`.
- Cross-check register names against `nbio_7_11_0_offset.h` and generated default files so `DEV0_EPF4`, `DEV2_EPF3`, `DEV2_EPF4`, and `DEV2_EPF5` fields line up with address definitions.
- Run symmetry checks across `BIF_CFG_DEV2_EPF3_*` and `BIF_CFG_DEV2_EPF4_*`; standard PCI, PM, PCIe, MSI/MSI-X, AER, BAR, DPA, ACS, PASID, ARI, and RTR field layouts should remain consistent unless hardware documentation says otherwise.
- On hardware or emulation, verify PCI config enumeration for the covered endpoint functions: vendor/device IDs, class codes, BAR discovery, capability list traversal, MSI/MSI-X discovery, PCIe link capability reporting, and AER capability discovery.
- Exercise controlled reset paths, including FLR and D3hot-to-D0 where supported, and compare readiness-time fields with observed polling/wait behavior.
- Validate error paths by injecting or observing AER corrected/uncorrected events and confirming status, masks, severity, header logs, and device-status bits decode with these masks.
- Validate virtualization/isolation setup by checking ACS/PASID/ARI capability and control values against expected IOMMU/SR-IOV or multi-function behavior.

## Chunk Boundary Notes

Lines 12286-14755 are a middle slice of a much larger generated header. The first register is incomplete because `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` begins at line 12280, before this chunk. The final register is also incomplete because `BIF_CFG_DEV2_EPF5_LINK_CAP` continues after line 14755. The merge/reconciliation lane should treat these as chunking artifacts and combine this document with adjacent chunk research for the final per-file report.
