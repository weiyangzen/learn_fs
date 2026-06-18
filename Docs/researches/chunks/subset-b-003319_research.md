# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 145029-147480

## Purpose

This chunk is part of the generated AMD NBIO 7.7.0 register shift/mask header used by the DRM AMDGPU driver to address bitfields in NBIO/PCIe configuration registers. It contains C preprocessor constants only: every field is represented as a `__SHIFT` constant and a matching `_MASK` constant so driver code can compose, extract, or update hardware register values without embedding raw bit positions.

The range starts in the tail of endpoint function EPF4 PCIe extended capabilities, then covers the complete generated mask/shift set for `addressBlock: nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, continues through most of the equivalent EPF6 block, and ends in the opening portion of EPF7 at `BIF_CFG_DEV0_EPF7_1_DEVICE_CNTL2__OBFF_EN__SHIFT`. The repeated EPF5/EPF6/EPF7 naming shows that this file models multiple PCI endpoint functions on device 0, each with a similarly shaped PCI configuration space.

## Important APIs, Types, and Macros

There are no functions, structs, enums, inline helpers, or runtime APIs in this chunk. The exported interface is the macro namespace:

- `BIF_CFG_DEV0_EPF4_1_PCIE_*`: the end of EPF4 ACS/PASID/ARI capability field definitions.
- `BIF_CFG_DEV0_EPF5_1_*`: a complete EPF5 PCI configuration-space field map in this range.
- `BIF_CFG_DEV0_EPF6_1_*`: a near-complete EPF6 map following the same layout as EPF5 through ARI control.
- `BIF_CFG_DEV0_EPF7_1_*`: the first EPF7 fields through PCIe device control 2.

Each field follows the generated pattern `<REGISTER>__<FIELD>__SHIFT` for the low bit index and `<REGISTER>__<FIELD>_MASK` for the unshifted bit mask. Consumers typically use these with AMDGPU register helpers/macros from nearby generated address headers and common bitfield helpers. Full-width data fields use masks such as `0xFFFFFFFFL`; byte and word PCI config fields use `0xFFL`, `0xFFFFL`, or appropriately shifted masks.

## Register Coverage

The EPF4 tail contains:

- ACS control fields for source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated P2P.
- PASID enhanced capability list, PASID capability, and PASID control fields for PASID enablement, execute permission, privileged mode support, and maximum PASID width.
- ARI enhanced capability list, ARI capability, and ARI control fields for MFVC/ACS function groups, next function number, and function group selection.

The EPF5 block begins at `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` and includes the standard PCI header and capabilities:

- Core PCI header: vendor/device ID, command, status, revision, class/prog-interface, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem/adapter ID, ROM base, capability pointer, interrupt line/pin, minimum grant, maximum latency, and a vendor capability list.
- Power management and USB/SATA-related capability fields: PMI capability list, PMI capability, PMI status/control, SBRN, FLADJ, DBESL/DBESLD, SATA capability words, and SATA index/data pair fields.
- PCIe base capability: PCIe capability list/capability, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2.
- MSI and MSI-X: MSI capability list, message control, message address/data fields, extended data, 32-bit and 64-bit mask/pending forms, MSI-X message control, table, and PBA descriptors.
- PCIe vendor-specific and AER: vendor-specific enhanced capability list/header/scratch registers, advanced error reporting enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, TLP header logs, and TLP prefix logs.
- Enhanced BAR, power, and latency capabilities: BAR enhanced capability list, BAR1-BAR6 capability/control pairs, power budget enhanced capability/data select/data/capability, dynamic power allocation enhanced capability, DPA capability, latency indicator, status, control, and substate power allocations 0-7.
- Isolation and addressing capabilities: ACS enhanced capability/capability/control, PASID enhanced capability/capability/control, and ARI enhanced capability/capability/control.

The EPF6 block repeats the EPF5 structure from standard PCI header fields through ARI control. The masks and shifts are largely identical after the prefix changes from `EPF5` to `EPF6`, which is expected for multiple PCI functions sharing the same hardware capability layout.

The EPF7 block starts a third repetition and, within this chunk, reaches only through the beginning of device control 2. It includes the standard header, PMI, PCIe base capabilities, link/device capability groups, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power budget, DPA, ACS/PASID/ARI portions visible before the chunk boundary, and finally the opening `DEVICE_CNTL2` shift definitions.

## Control Flow

This header has no executable control flow. Its compile-time role is data-definition: other C files include it and select macros based on the register they need to read or write. Runtime control flow lives in the consuming AMDGPU/NBIO code that performs MMIO, indirect config-space, or PCI config access, then applies these masks and shifts to encode or decode fields.

The logical flow within the chunk is generated register order:

1. Complete the previous EPF4 extended capability definitions.
2. Start EPF5 with `addressBlock: nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`.
3. Emit each register's field shifts, then masks, in PCI config-space order.
4. Repeat the same generated layout for EPF6.
5. Start EPF7 and continue until the chunk boundary.

## State and Persistence Behavior

The macros do not allocate memory, mutate state, persist data, or perform I/O. They describe persistent hardware state owned by the NBIO/PCIe block: command/status bits, BAR sizing/control, power-management state, MSI/MSI-X configuration, AER status/log registers, ACS/PASID/ARI controls, and DPA/power budget configuration. Writes by driver code to fields such as command enable bits, MSI control, AER masks/severity, ACS controls, PASID controls, or ARI controls affect hardware-visible PCIe behavior until reset or reprogramming according to the register semantics.

Several fields are status or log oriented and may have hardware clear-on-write or sticky behavior in the real registers, especially PCI status, device status, link status, AER status, header log, TLP prefix log, MSI pending, and DPA status fields. This chunk only supplies the bit layout; it does not encode read/clear policy.

## Dependencies and Integration Points

This file is part of the generated ASIC register include set under `drivers/gpu/drm/amd/include/asic_reg/nbio`. It depends on naming consistency with companion NBIO address headers that provide register offsets and with AMDGPU register access helpers that use masks and shifts.

Expected integration points include:

- AMDGPU NBIO initialization and PCIe configuration code that enables or inspects endpoint functions.
- PCIe error handling paths that read AER status, mask, severity, header log, and prefix log fields.
- Interrupt setup paths that configure MSI/MSI-X message control, address/data, masks, pending bits, tables, and PBA offsets.
- Power-management paths that inspect or program PMI, power budget, DPA, ASPM/link, emergency power reduction, and LTR fields.
- IOMMU/SRIOV/virtualization or multi-function handling paths that use ACS, PASID, and ARI capability/control fields.
- BAR discovery/control code using the enhanced BAR capability and BAR index/size fields.

The macros also provide compile-time ABI between generated hardware descriptions and C source. Renaming, deleting, or changing constants can break builds or silently corrupt register programming in downstream call sites.

## Risks and Edge Cases

- The chunk boundary cuts through generated sequences. It starts after earlier EPF4 ACS control shift definitions and ends before the EPF7 `DEVICE_CNTL2` masks and subsequent registers. Any per-file synthesis must merge neighboring chunks before claiming complete EPF4/EPF7 coverage.
- Because EPF5, EPF6, and EPF7 are repetitive, copy-generation mistakes are hard to see manually. A wrong prefix, mask, or shift would compile but target the wrong field semantics.
- `*_MASK_MASK` names in AER mask registers are intentional generated names, not typographical duplication: the register is itself an error mask register and the field suffix is also `MASK`.
- Full-width masks with `L` suffix assume the consuming code handles the target integer width correctly. Sign extension or truncation bugs can appear if code stores these constants in narrower or signed types.
- Status/log fields require correct hardware access semantics in consumers. The presence of a mask alone does not identify read-only, write-one-to-clear, sticky, or side-effecting behavior.
- Capability list `NEXT_PTR` and enhanced capability `NEXT_PTR` fields use different widths and shifts; callers must match the macro to the exact register family.
- Security-sensitive isolation fields such as ACS, PASID, and ARI control bits can affect peer-to-peer routing, address space IDs, and function grouping. Incorrect bit use can create DMA isolation or virtualization bugs.

## Test Signals

Useful validation is mostly compile-time and hardware/driver integration oriented:

- Build the AMDGPU driver with this header included to catch missing or malformed macro names.
- Run static checks or generated-header diff checks against the authoritative NBIO 7.7.0 register specification to verify every `__SHIFT` has the expected `_MASK` partner and value.
- Exercise PCIe bring-up on hardware exposing these endpoint functions, then inspect config-space fields for vendor/device IDs, command/status, BARs, link state, MSI/MSI-X, and capability list traversal.
- Test AER injection or error reporting paths to confirm uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode correctly.
- Validate power-management transitions involving PMI, ASPM/link control, LTR, power budget, DPA substates, and emergency power reduction fields.
- In virtualization or multi-function configurations, verify ACS/PASID/ARI capability discovery and control programming using EPF5/EPF6/EPF7-specific macro prefixes.
