# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 32043-34496

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.11.0 register mask header. It begins at the tail of the `BIF_CFG_DEV0_EPF3_0` PCIe enhanced-capability area, fully covers the `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` address blocks, and ends inside the early `BIF_CFG_DEV0_EPF6_0` PCIe capability fields.

The covered register families include:

- Function 3 tail fields for ARI control and reset-time reporting (`PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`).
- Function 4 and function 5 PCI configuration header fields, including vendor/device IDs, command/status, class/revision, BARs, ROM BAR, subsystem IDs, capability pointer, interrupt line/pin, and latency/grant fields.
- Function 4 and function 5 PCI power-management and PCIe capability fields, including device/link capabilities, control, status, capability version, payload/read-request sizing, FLR, ASPM-related link fields, LTR, OBFF, ten-bit tags, atomic operations, DRS, and equalization status.
- Function 4 and function 5 MSI and MSI-X capability fields, including message control, 32-bit and 64-bit address/data fields, mask and pending bits, table BIR/offset, PBA BIR/offset, and MSI-X enable/function-mask state.
- Function 4 and function 5 SATA capability and IDP index/data windows.
- Function 4 and function 5 PCIe vendor-specific, AER, BAR enhanced capability, power-budget, DPA, ACS, PASID, ARI, and RTR capability fields.
- Function 6 header, PM, base PCIe capability, device/link capability, control, and status fields through `LINK_CAP2`.

The file is a generated hardware register bitfield map. It defines C preprocessor constants only; this chunk contains no functions, structs, variables, storage, or executable control flow.

## Purpose

This header section provides the bit-level ABI used by AMDGPU NBIO code and other register consumers when composing or decoding NBIO 7.11.0 PCI configuration-space register values. Each field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field.

The sibling `nbio_7_11_0_offset.h` file supplies register addresses and base indices, such as `regBIF_CFG_DEV0_EPF4_0_DEVICE_CNTL`, `regBIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV0_EPF6_0_LINK_CAP2`. This file supplies the matching field layouts. Driver code normally consumes these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

The macro names identify NBIO device 0 endpoint functions. The repeated `EPF4`, `EPF5`, and `EPF6` blocks model separate PCIe endpoint-function configuration spaces with mostly identical PCI/PCIe capability layouts but distinct offsets and hardware instances.

## Important Macro Families

### PCI Configuration Header Fields

The `BIF_CFG_DEV0_EPF4_0_*`, `BIF_CFG_DEV0_EPF5_0_*`, and partial `BIF_CFG_DEV0_EPF6_0_*` header fields describe normal PCI configuration-space state:

- `VENDOR_ID` and `DEVICE_ID`.
- `COMMAND` bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, SERR, fast back-to-back, and interrupt disable.
- `STATUS` bits for immediate readiness, interrupt status, capability-list presence, target/master aborts, and system-error reporting.
- Revision, programming interface, subclass, base class, cache line, latency, header type, device type, and BIST fields.
- Six `BASE_ADDR_*` BAR fields, `ROM_BASE_ADDR`, `ADAPTER_ID`, `ADAPTER_ID_W`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- `VENDOR_CAP_LIST` capability-header fields for vendor-defined capability ID, next pointer, and length.

These fields are the most conventional part of the chunk. They expose how the endpoint function appears to PCI enumeration and how the OS-visible PCI command/status and BAR state is represented in NBIO register space.

### Power Management and Base PCIe Capability

The PM capability group includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. It defines PM capability versioning, PME support, D1/D2 support, auxiliary current, immediate readiness on D0 return, power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data fields.

The base PCIe capability group includes `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for the full function 4 and 5 ranges. Function 6 is covered through `LINK_CAP2`.

Important encoded behavior includes:

- Max payload support and selected max payload size.
- Max read request size.
- Correctable, non-fatal, fatal, and unsupported-request reporting enables.
- Relaxed ordering, extended tags, phantom functions, no-snoop, auxiliary power PM, and FLR initiation/capability.
- Link speed, width, PM support, L0s/L1 latency, clock power management, link disable/retrain, common clock, extended sync, link bandwidth notification, autonomous bandwidth interrupt, DRS signaling, and DL active state.
- Completion-timeout range, timeout disable support/control, ARI forwarding support/control, atomic operation support/control, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, and FRS.
- Link-speed-generation support, crosslink support, SKP ordered-set support, RTM presence detection, DRS support, target link speed, compliance-mode controls, de-emphasis, equalization phase status, downstream component presence, and DRS message received.

These fields are integration points for PCIe bring-up, power management, reset, link diagnostics, and capability discovery. They are also easy to confuse because function 4 and 5 layouts are mechanically repeated.

### MSI and MSI-X Capabilities

Function 4 and 5 expose both MSI and MSI-X capability field macros:

- MSI list and message control fields include enable, multiple-message capable/enabled, 64-bit capability, per-vector masking capability, extended message data capability, and extended message data enable.
- MSI message address/data fields cover low/high address, data, extended data, 64-bit data variants, mask, and pending arrays.
- MSI-X fields include capability list, table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.

These definitions matter for interrupt delivery and masking. They describe hardware-visible MSI/MSI-X configuration-space fields, but interrupt setup sequencing is owned by PCI/AMDGPU code outside this generated header.

### SATA and IDP Capability Fields

Function 4 and 5 include SATA capability fields:

- `SATA_CAP_0` exposes capability ID, next pointer, major/minor revision, and reserved bits.
- `SATA_CAP_1` exposes BAR location and BAR offset.
- `SATA_IDP_INDEX` and `SATA_IDP_DATA` expose an indexed data path with index and data fields.

These are capability-structure definitions for endpoint functions that expose SATA-style or SATA-compatible capability state through PCI configuration space. The IDP index/data fields imply indirect access semantics; the header defines bit positions, not the ordering rules for safe indirect reads/writes.

### Vendor-Specific and Advanced Error Reporting

Function 4 and 5 define PCIe vendor-specific enhanced capability fields (`PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`). The list/header macros encode capability ID, version, next pointer, VSEC ID, VSEC revision, VSEC length, and scratch fields.

The AER group is larger and includes:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`.

Uncorrectable error bits include data-link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, and internal correctable error. The capability/control fields include first-error pointer, ECRC generation/check capabilities and enables, and multi-header record support.

These macros are central to PCIe RAS and diagnostics. The log fields carry captured TLP header and prefix data after AER events.

### BAR Enhanced Capability, Power Budget, DPA, ACS, PASID, ARI, and RTR

Function 4 and 5 include a dense set of PCIe extended capability definitions:

- `PCIE_BAR_ENH_CAP_LIST` plus `PCIE_BAR1_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL`, encoding supported BAR sizes, BAR index, total BAR count, selected size, and upper supported-size bits.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`, encoding selected power-budget table entry, base power, scale, PM sub-state, PM state, type, rail, and system allocation.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0..7`, encoding dynamic power allocation substates, transition latency units/values, power allocation scaling, substate status/control, and per-substate allocation values.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, encoding source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, egress control vector size, and their enables.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`, encoding PASID execute-permission support, privileged-mode support, max PASID width, and enables.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, encoding next function number, MFVC/ACS function group enables, and ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, encoding reset-time reporting capability metadata plus reset, DL-up, FLR, and D3hot-to-D0 timing values.

These extended capabilities have direct implications for virtualization, IOMMU integration, peer-to-peer routing, power budgeting, reset delay handling, BAR sizing, and PCIe error containment.

## Control Flow and State Behavior

This chunk has no runtime control flow. It affects behavior at compile time by giving C code symbolic field positions for 32-bit MMIO or PCI configuration-space register values.

The state described by the macros is hardware state, not software state stored in the header. Examples include:

- PCI command/status and BAR configuration state for endpoint functions.
- PM capability status/control state, including current power state and PME status.
- PCIe device/link capability and control state, including negotiated link status and reset/FLR controls.
- MSI/MSI-X address, data, mask, pending, and enable state.
- AER status/mask/severity bits plus captured header and TLP prefix logs.
- ACS/PASID/ARI state that can affect requester identity, isolation, peer-to-peer routing, and function enumeration.
- Power-budget and DPA table/control state.
- Reset-time reporting values used to communicate reset, DL-up, FLR, and D3hot-to-D0 timing.

Some fields are durable configuration bits, some are live status bits, some are capability readouts, and some are action-oriented controls such as `INITIATE_FLR`, link retrain, link disable, compliance entry, MSI/MSI-X enable, PME enable, or ACS/PASID enables. The macros do not encode side effects, required polling, write-one-to-clear behavior, or ordering constraints; those rules must come from PCIe specification handling, AMD hardware documentation, and the owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_11_0_offset.h` provides register addresses and base indices for the same `BIF_CFG_DEV0_EPF*_0_*` names. The corresponding function 4, 5, and 6 address blocks use base index 5 and distinct register offsets.
- `nbio_7_11_0_sh_mask.h` provides only field shifts and masks.
- AMDGPU register helper macros combine the address and field layers to read, write, set, or extract fields without hard-coded bit positions.

Observed integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio_7_11_0_offset.h` and this mask header. That file primarily uses other NBIO 7.11.0 register groups for revision ID, memory size, doorbell apertures, HDP flush offsets, PCIE index/data offsets, interrupt handling, register remapping, and clock gating. It demonstrates the intended consumption pattern: read a register through a SOC15 or PCIE helper, update fields with `REG_SET_FIELD` or masks, and write the result back.

The exact `BIF_CFG_DEV0_EPF4/5/6` fields in this chunk are most likely consumed by PCIe capability, diagnostics, reset, RAS, virtualization, or firmware-facing paths rather than by the short NBIO bring-up helpers alone. They align with older generic BIF/PCIe mask families such as `PCIE_UNCORR_ERR_STATUS`, `PCIE_ACS_CAP`, and `PCIE_PASID_CAP`, but are specialized here for NBIO 7.11.0 endpoint-function configuration spaces.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can modify unrelated PCI configuration bits, causing broken enumeration, disabled bus mastering, incorrect BAR sizing, lost interrupts, link instability, bad reset behavior, or failed power management.
- Repetition across endpoint functions is mechanically fragile. Function 4 and function 5 are nearly identical, and function 6 starts the same pattern. Copying an `EPF4` mask into `EPF5` or `EPF6` code would target the wrong register namespace even when the field layout appears identical.
- PCIe AER fields include sticky status, masks, severity controls, and captured logs. Misinterpreting status bits as masks, or severity bits as status, can hide fatal errors or misclassify correctable/non-fatal/fatal events.
- MSI/MSI-X fields are interrupt-critical. Incorrect table offsets, BIRs, message data, masks, pending bits, or enable bits can produce missing, misrouted, or unmasked interrupts.
- ACS and PASID controls affect isolation and requester identity. Incorrect enablement can break IOMMU/PASID behavior, peer-to-peer routing constraints, or virtualization security assumptions.
- Link and FLR controls have side effects. `INITIATE_FLR`, retrain, link disable, compliance, DRS, and de-emphasis fields must be used with appropriate sequencing and polling.
- Power-budget and DPA fields can interact with platform power policy. Treating them as arbitrary debug fields can produce inconsistent advertised power state or substate information.
- The chunk starts mid-family at the end of function 3 and ends mid-family in function 6. A merged report must stitch this document to adjacent chunks to avoid presenting partial function 3 and function 6 coverage as complete.

## Test and Validation Signals

Useful validation is mostly build-time and hardware-integration coverage:

- Build AMDGPU with NBIO 7.11.0 support enabled to catch missing or renamed macros in code that includes `nbio_7_11_0_sh_mask.h`.
- PCI enumeration and lspci/config-space validation should confirm vendor/device IDs, command/status, BARs, class codes, capability pointers, PM capability, PCIe capability, MSI, MSI-X, AER, ACS, PASID, ARI, and RTR capability layouts match expected hardware.
- Interrupt tests should exercise MSI and MSI-X enablement, masking, pending bits, table/PBA offsets, and 32-bit versus 64-bit MSI message fields.
- PCIe RAS tests should inject or observe correctable and uncorrectable errors, verify AER status/mask/severity interpretation, and confirm header/TLP-prefix log capture.
- Reset and power-management tests should cover FLR initiation, D3hot-to-D0 timing, reset-time reporting, PME enable/status, power-state fields, and link recovery after retrain or reset.
- Virtualization/IOMMU tests should validate PASID width/enables, ACS capability/control behavior, ARI next-function and function-group fields, and peer-to-peer isolation expectations.
- Link-training diagnostics should verify negotiated speed/width, training status, DL active, bandwidth notifications, equalization phase status, target link speed, and compliance/de-emphasis controls.

## Unresolved Cross-Chunk References

This chunk begins after `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP` has already started, so the complete function 3 PCIe capability and AER/BAR/power-management context is in earlier chunks. It ends at `BIF_CFG_DEV0_EPF6_0_LINK_CAP2`; the remaining function 6 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR fields belong to the following chunk. The merge/reconciliation lane should combine adjacent chunk research before producing a complete per-file document.
