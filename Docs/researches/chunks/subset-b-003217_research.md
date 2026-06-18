# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 138529-141010

## Scope

This chunk covers generated shift and mask macros for AMD NBIO 7.2.0 PCI/PCIe configuration-space bitfields. The range starts inside `BIF_CFG_DEV0_EPF3_1_PCIE_UNCORR_ERR_MASK`, continues through the remaining EPF3 PCIe extended capability field definitions, covers a full EPF4 endpoint-function configuration block, and begins the EPF5 endpoint-function block through the first `LINK_STATUS2` shift definitions.

The source is a generated register mask header. It defines preprocessor constants only: no C functions, structs, variables, storage, or executable control flow live in this chunk. The assigned range is boundary-sensitive: the EPF3 uncorrectable error mask register begins before line 138529, and the EPF5 `LINK_STATUS2` register continues after line 141010 with additional shifts and masks that belong to the next chunk.

## Purpose

The purpose of this section is to provide the bit-level ABI between AMDGPU/NBIO driver code and PCI configuration registers exposed for NBIF device 0 endpoint functions. Each field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field.

These macros are intended to be paired with matching offset definitions from the generated NBIO offset headers and consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The header itself does not perform access; it prevents C code from hard-coding PCIe capability bit positions.

## Important Macro Families

### EPF3 PCIe Advanced Error Reporting

The chunk starts with the tail of `BIF_CFG_DEV0_EPF3_1_PCIE_UNCORR_ERR_MASK`, defining mask bits for uncorrectable PCIe/AER errors including data-link protocol, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, multicast blocked TLP, atomic egress block, TLP prefix block, and poisoned TLP egress block.

The following EPF3 AER registers are then covered:

- `PCIE_UNCORR_ERR_SEVERITY`, with the same uncorrectable error classes encoded as fatal/non-fatal severity bits.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`, covering receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal errors, internal corrected errors, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, covering first-error pointer, ECRC check capability/enable, multi-header recording capability/enable, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`, each exposing full 32-bit captured TLP header or prefix words.

These macros describe the status, masking, severity, and diagnostic capture side of PCIe AER. They are critical for error reporting and recovery paths because shifting the wrong bit changes which hardware error is suppressed, reported as fatal, or decoded from captured logs.

### EPF3 PCIe Extended Capabilities

The rest of the EPF3 section covers several PCIe extended capability structures:

- BAR enhanced capability list plus `PCIE_BAR1_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL`, describing supported BAR sizes, active BAR size, BAR index, total BAR count, and upper supported-size bits.
- Power budget capability registers: capability list, data select, power budget data fields such as base power, data scale, PM state/sub-state, power rail, type, and system-allocated flag.
- Dynamic Power Allocation registers: capability, latency indicator, status, control, and eight substate power allocation registers.
- ACS capability and control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, and direct translated P2P.
- PASID capability and control bits for maximum PASID width, execute permission, privileged mode, and enable bits.
- ARI capability and control bits for next-function number, function groups, and function-group enable/selection.
- TPH requester capability/control and `TPH_ST_TABLE_0..63`, each table word split into lower and upper steering-tag entries.

The TPH steering table is the largest repeated structure in the EPF3 subsection. It is hardware state used to steer PCIe transactions for better placement or locality; consumers should treat it as a table with fixed-width packed entries rather than a set of unrelated scalar registers.

### Complete EPF4 Configuration Block

The middle of the chunk is a full `addressBlock: nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` section for `BIF_CFG_DEV0_EPF4_1_*`. It mirrors a PCI endpoint function's configuration space and capability list. Covered groups include:

- Standard PCI header fields: vendor/device ID, command/status, revision/prog-if/subclass/base-class, cache line, latency, header, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and writable adapter ID.
- Power management capability: PM capability list, PM capability, PM status/control, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe capability: capability list, PCIe capability, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI and MSI-X capability fields: message control, message address/data, extended data, mask/pending registers, 64-bit variants, MSI-X table and PBA descriptors.
- Vendor-specific enhanced capability fields and AER capability fields.
- BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, TPH requester, and `TPH_ST_TABLE_0..63`.

This block is highly regular and is likely generated from the same register schema used for neighboring endpoint functions. The semantic difference is the endpoint-function prefix (`EPF4_1`), which selects a specific PCI function's configuration-space decode path.

### EPF5 Configuration Block Start

The end of the chunk begins `addressBlock: nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` and covers the start of `BIF_CFG_DEV0_EPF5_1_*` through the first seven `LINK_STATUS2` shift fields. Included groups are:

- Standard PCI header and BAR fields analogous to EPF4.
- Vendor capability, PM capability, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe capability, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability 2, and link control 2.
- The beginning of `LINK_STATUS2`, including current de-emphasis level, 8 GT/s equalization completion and phase success bits, equalization request, and `RTM1_PRESENCE_DET`.

The range stops before the rest of `LINK_STATUS2` and before EPF5 MSI/MSI-X definitions. Any final file-level reconciliation should avoid claiming this chunk covers the complete EPF5 capability list.

## Control Flow and State Behavior

There is no runtime control flow in this header. The macros influence driver behavior at compile time by determining how callers compose and decode MMIO or PCI configuration-space values.

The persistent state described here is hardware state in PCIe configuration registers. Important state classes include:

- AER status, masks, severity, first-error pointer, ECRC/multi-header enablement, and captured TLP header/prefix logs.
- BAR sizing and capability state for endpoint functions.
- Power management, power budgeting, DPA substate power allocation, and PM status/control state.
- ACS, PASID, ARI, and TPH requester control state, which can affect transaction isolation, address-space tagging, function enumeration behavior, and transaction steering.
- MSI/MSI-X state for EPF4, including message address/data, masks, pending bits, table size/control, table BIR/offset, and PBA BIR/offset.
- PCIe device/link control and status state for EPF4 and early EPF5, including payload/read-request sizing, relaxed ordering/no-snoop, FLR, completion timeout, atomic operation controls, LTR, OBFF, ASPM, link retrain/disable, link speed/width, equalization, and compliance controls.

Some fields are status bits latched by hardware, some are writable controls, some are capability descriptors, and some represent interrupt masking or pending state. The header does not encode write-one-to-clear, sticky, read-only, or sequencing rules; those must come from the hardware specification and owning AMDGPU access paths.

## Dependencies and Integration Points

This chunk depends on the generated NBIO register-header family:

- Matching `nbio_7_2_0_offset.h` definitions provide register addresses and base indices for the register names defined here.
- Matching default/reset headers, where present, provide reset values; this file only provides field layout.
- AMDGPU helper macros consume the `__SHIFT` and `_MASK` names when setting or extracting fields.

Integration points are implied by the names and by normal AMDGPU register access patterns:

- PCIe error reporting and recovery code can use the AER status/mask/severity/header-log fields to report, mask, or classify link and transaction errors.
- PCI resource discovery/configuration code relies on BAR capability/control fields when determining supported aperture sizes and active BAR programming.
- Power-management and platform policy code can read PM, power-budget, and DPA fields to understand advertised power states and substate allocation.
- IOMMU, virtualization, and isolation-related paths are sensitive to ACS, PASID, and ARI capability/control fields.
- Interrupt setup paths use MSI/MSI-X fields for message enablement, address/data, masks, pending state, MSI-X table size, table BIR/offset, and PBA placement.
- PCIe link-management paths use device/link capability/control/status fields for payload sizing, completion timeouts, link retraining, equalization, ASPM/clock power management, LTR, OBFF, and compliance controls.

Because the EPF3, EPF4, and EPF5 blocks are near-duplicates for different endpoint functions, integrations must include the exact endpoint-function prefix that matches the hardware function being accessed. Accidentally mixing `EPF4_1` masks with an `EPF5_1` register address may compile but would document or manipulate the wrong function's configuration-space state.

## Risks

- The chunk starts and ends in partial register definitions. The preceding EPF3 `PCIE_UNCORR_ERR_MASK` comment and possibly earlier fields are outside the assigned range, and the EPF5 `LINK_STATUS2` masks and remaining fields are outside the assigned range. Merge logic should preserve those boundaries.
- These are generated constants; manual edits risk desynchronizing field layout from the hardware register database and sibling offset/default headers.
- PCIe AER mask/severity mistakes can hide fatal errors, over-report benign corrected errors, or misclassify recovery behavior.
- ACS/PASID/ARI control bit mistakes can affect isolation, transaction routing, and function enumeration semantics.
- TPH steering table and BAR enhanced capability fields are packed, repeated encodings. Off-by-one table indexing or wrong shift/mask use can steer transactions incorrectly or advertise invalid BAR sizing.
- MSI/MSI-X fields overlap normal PCI capability semantics. Incorrect masks can leave vectors disabled, incorrectly masked, or pointed at wrong message/table/PBA addresses.
- Link control/status fields include command-like controls such as retrain, disable, compliance, and autonomous speed/width disable. Wrong writes can destabilize the PCIe link.

## Test Signals

Useful validation signals for consumers of these macros include:

- Compile-time coverage: code that includes `nbio_7_2_0_sh_mask.h` together with matching NBIO 7.2.0 offset headers should build without undefined register-field names.
- Register helper sanity: `REG_SET_FIELD` and `REG_GET_FIELD` operations on representative AER, BAR, MSI-X, ACS/PASID/ARI, and link-control fields should round-trip within the documented masks.
- Hardware bring-up logs: PCIe link speed/width, AER status, MSI/MSI-X enablement, BAR sizing, and PM capability reporting should match `lspci`/kernel PCI core observations for the targeted AMD GPU.
- Error-path diagnostics: injected or observed PCIe AER events should set the expected corrected/uncorrected status bits and header-log fields without unexpected masking.
- Boundary check for this research chunk: the generated report should be merged with adjacent chunks before making full-file claims about the complete EPF3 uncorrectable error mask or complete EPF5 `LINK_STATUS2`/MSI capability coverage.
