# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 17034-19455

## Purpose

This chunk is an auto-generated AMD NBIO 7.4 shift/mask slice for PCI/PCIe configuration-space fields exposed through `BIF_CFG_DEV0_EPF0_VF*_0` virtual-function blocks. It contains no executable driver logic. Its purpose is to publish preprocessor constants that let AMDGPU, display, PSP, and power-management code decode or program individual bitfields in NBIO-backed PCIe configuration registers.

The selected line range starts in the middle of the VF12 PCIe capability tail, covers the complete VF13 and VF14 configuration-field masks, and then covers most of the VF15 block through `PCIE_TLP_PREFIX_LOG3`. The remainder of VF15, including ATS and ARI fields, continues immediately after this chunk.

## Public Surface In This Chunk

The public surface is 2,135 `#define` macros in the assigned range: 1,060 `__SHIFT` constants and 1,075 `_MASK` constants. The count is not pair-perfect because the chunk starts and ends inside register groups, because full-width and reserved fields still have generated masks, and because fields named `*_MASK` generate macro names such as `*_MASK_MASK`.

Macro naming follows the generated register-field convention:

- `BIF_CFG_DEV0_EPF0_VF12_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe the tail of VF12 registers in this range.
- `BIF_CFG_DEV0_EPF0_VF13_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe a full VF13 PCIe config decode block.
- `BIF_CFG_DEV0_EPF0_VF14_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe a full VF14 PCIe config decode block.
- `BIF_CFG_DEV0_EPF0_VF15_0_<REGISTER>__<FIELD>__SHIFT` and `_MASK` describe VF15 from conventional PCI header fields through AER/TLP prefix logs in this range.

There are no functions, structs, enums, storage objects, or inline helpers here. The API contract is the exact macro spelling and numeric value, which must remain synchronized with `nbio_7_4_offset.h` and AMD's NBIO 7.4 register database.

## Register Coverage

The VF12 portion begins at the `DEVICE_CAP2` tail and covers PCIe capability 2, MSI/MSI-X, vendor-specific extended capability, Advanced Error Reporting, ATS, and ARI field definitions. This is the continuation of a VF12 block that began earlier in the header.

The VF13 and VF14 portions each provide a complete virtual-function PCI configuration decode map:

- Conventional PCI header fields: vendor/device ID, command, status, revision ID, class code bytes, cache-line size, latency timer, header type, BIST, six BARs, adapter ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability list header, PCIe capability flags, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and reserved slot capability/control/status 2 placeholders.
- MSI and MSI-X fields: capability IDs, next pointers, MSI enable/multiple-message controls, 64-bit MSI addressing/data/mask/pending forms, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields: capability ID/version/next pointer, VSEC ID/revision/length, and two scratch payload registers.
- Advanced Error Reporting fields: AER capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- ATS fields: ATS enhanced capability list, invalidate queue depth, page-aligned request/global invalidate capability, STU, and ATC enable.
- ARI fields: ARI enhanced capability list, MFVC/ACS function group capabilities, next function number, MFVC/ACS group enables, and function group selection.

The VF15 portion repeats the same layout as VF13/VF14 from vendor ID through `PCIE_TLP_PREFIX_LOG3`. The line range stops before VF15 `PCIE_ATS_ENH_CAP_LIST`, so ATS and ARI coverage for VF15 belongs to the next chunk.

## Field Semantics

The conventional PCI fields describe enumeration-visible identity, device class, BAR aperture attributes, command enables, status/error bits, interrupt routing, and capability-chain entry points for SR-IOV virtual functions. Command and status masks cover memory/I/O decode, bus mastering, parity/SERR handling, interrupt disable/status, capability-list presence, aborts, and parity/system-error observation.

The PCIe device and link fields expose negotiated and advertised behavior for payload sizing, phantom functions, extended tags, endpoint L0s/L1 latency, role-based error reporting, completion timeouts, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, emergency power reduction, TLP prefixes, target link speed, compliance entry, autonomous speed disable, de-emphasis, equalization status, and downstream component presence.

The MSI/MSI-X fields describe interrupt-message routing state rather than CPU interrupt delivery code. They provide masks for enable bits, message count fields, 64-bit address/data registers, per-vector mask and pending bits, MSI-X table/PBA BAR indicators, and MSI-X function masking. The overlapping offsets in the matching offset header for MSI 32-bit versus 64-bit forms mean consumers must interpret these fields according to the enabled MSI capability format.

The AER fields are diagnostics and policy controls. Uncorrectable status/mask/severity covers data-link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions. Correctable status/mask covers receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal errors, correctable internal errors, and header-log overflow. AER capability/control fields include first-error pointer, ECRC generation/check support and enable bits, multi-header-record support, TLP prefix log presence, and completion-timeout log capability.

The ATS and ARI fields are virtualization-sensitive. ATS controls address-translation cache behavior through invalidate queue depth, STU, and ATC enable. ARI controls alternative routing and function grouping so many virtual functions can be represented beyond the legacy PCI function-number limit. These fields are meaningful only when platform IOMMU, PCIe hierarchy, and SR-IOV policy agree.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_4_offset.h` and `nbio/nbio_7_4_sh_mask.h`.
2. Driver code selects a register address macro such as `cfgBIF_CFG_DEV0_EPF0_VF13_0_DEVICE_CNTL2`.
3. Register helpers or open-coded bit operations use the corresponding `BIF_CFG_DEV0_EPF0_VF13_0_DEVICE_CNTL2__<FIELD>__SHIFT` and `_MASK` macros to insert, extract, preserve, or compare fields.
4. Actual state changes occur through NBIO/PCI config, MMIO, SMN, or indirect register access code outside this header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware registers, PCIe config space, or firmware-managed NBIO state. Some fields are writable configuration controls that survive until reset, FLR, link reset, power transition, or driver reprogramming. Other fields are hardware-updated status, sticky error, log, or write-one-to-clear bits whose behavior must be inferred from the PCIe specification and AMD hardware documentation rather than from the macro names.

## Dependencies And Integration Points

The matching address definitions are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, where the same VF12 through VF15 registers use `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. These shift/mask macros must be paired with that same NBIO 7.4 offset header; mixing ASIC generations can silently target the wrong register or field.

Direct include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`, which is the main NBIO 7.4 implementation and uses generated masks with SOC15/NBIO register helpers.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c`, `drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c`, which use NBIO 7.4 register fields for platform power-management behavior.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c` and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h`, which include the same generated NBIO 7.4 mask surface for older powerplay paths.

Semantic dependencies are the PCI and PCI Express configuration-space specifications, SR-IOV virtual-function behavior, MSI/MSI-X interrupt capability layouts, AER, ATS, ARI, and AMD's generated NBIO 7.4 register database. The macros do not encode reset values, access permissions, lock sequencing, firmware ownership, side effects, or whether a field is valid on every NBIO 7.4 ASIC variant.

## Risks And Maintenance Notes

- The range is chunked mid-register context. It starts after the beginning of VF12 `DEVICE_CAP2` and ends before VF15 ATS/ARI, so adjacent chunks are required for a complete per-file report.
- VF13, VF14, and VF15 are intentionally repetitive. Prefix mistakes are the main review risk: a `VF14` mask paired with a `VF13` offset can compile cleanly while addressing the wrong virtual function.
- Wrong AER masks or severities can suppress important PCIe errors, misclassify fatal/non-fatal conditions, or misdecode sticky hardware logs.
- MSI/MSI-X mask misuse can affect interrupt routing, vector masking, pending-bit interpretation, or table/PBA BAR location.
- ATS and ARI fields interact with IOMMU and SR-IOV topology. Enabling or decoding them incorrectly can affect address translation, isolation, and virtual-function enumeration.
- Full-width `0xFFFFFFFFL` masks usually represent payload/log/scratch fields, not permission to write all bits indiscriminately.
- Names such as `*_MASK_MASK` are valid generated names when the hardware field is named `MASK`; cleanup scripts should not rename or normalize them.
- This generated header has no type safety. Field widths, access width, and side effects must be validated against the offset header and hardware documentation.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for all NBIO 7.4 include sites, especially `amdgpu/nbio_v7_4.c` and the Arcturus/Aldebaran/SMU power-management files.
- Cross-header checks that each register prefix in this chunk has a matching `cfgBIF_CFG_DEV0_EPF0_VF12_0_*`, `cfgBIF_CFG_DEV0_EPF0_VF13_0_*`, `cfgBIF_CFG_DEV0_EPF0_VF14_0_*`, or `cfgBIF_CFG_DEV0_EPF0_VF15_0_*` offset in `nbio_7_4_offset.h`.
- Generated-header comparison against AMD's authoritative NBIO 7.4 register database, with special attention to the repetitive VF13/VF14/VF15 blocks and the chunk boundary at VF15 ATS.
- Static checks that masks fit the expected 8-, 16-, or 32-bit PCI config register widths and that each `__SHIFT` has the expected generated mask.
- Hardware or simulator PCI config-space dumps for SR-IOV virtual functions 12 through 15, compared with `lspci -vvxxx`-style decoding for PCIe capabilities, MSI/MSI-X, AER, ATS, and ARI.
- Error-injection or observation tests that verify AER status, mask, severity, header log, and TLP prefix log fields decode correctly.
- Virtualization tests that enumerate many SR-IOV VFs, validate ARI behavior, enable/disable ATS under IOMMU control, and confirm that interrupt delivery through MSI/MSI-X remains stable.
