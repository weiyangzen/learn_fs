# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 100976-103396

## Scope

This chunk covers generated NBIO 2.3 shift and mask macros for PCI configuration-space registers exposed through AMDGPU's NBIF/BIF virtual-function decode blocks. The range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF3_1_PCIE_CAP` family and ends after `BIF_CFG_DEV0_EPF0_VF6_1_PCIE_VENDOR_SPECIFIC2`, immediately before the `VF6_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST` definitions in the next chunk.

Covered address blocks and register groups include:

- The tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp`, from PCIe capability/device/link controls through MSI, MSI-X, vendor-specific, AER, ATS, and ARI masks.
- Complete `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp` mask coverage, including conventional PCI header fields, PCIe capabilities, MSI/MSI-X, vendor-specific capability, advanced error reporting, ATS, and ARI.
- The first part of `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`, from conventional PCI header fields through PCIe capability, MSI/MSI-X, and vendor-specific scratch registers. VF6 AER and later enhanced capabilities are outside this chunk.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it contains no C functions, structs, variables, runtime storage, or executable control flow.

## Purpose

The purpose of this section is to provide the bit-level ABI between AMDGPU NBIO/NBIF code and hardware PCI configuration-space registers for SR-IOV virtual functions. Every field is represented by the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating or composing that field.

The sibling NBIO offset header supplies register addresses, while this header supplies field layout. Driver code can then use common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and NBIO-specific indirect accessors without hard-coding bit positions for each virtual function.

## Important Macro Families

### Virtual Function Naming

The dominant prefix is `BIF_CFG_DEV0_EPF0_VF<N>_1`, where `VF<N>` is the virtual function number in the BIF configuration decode space. The chunk contains the end of VF3, complete VF4 and VF5, and the beginning of VF6. Most register definitions are mechanically repeated per VF with identical masks, so their semantic differences come from the addressed VF instance rather than from different bit layouts.

The address-block comments mark the generated source grouping:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`

VF3's address-block comment appears before this range, but the chunk still covers VF3 definitions through ARI control.

### Conventional PCI Header Fields

For VF4, VF5, and VF6 the chunk defines masks for the standard PCI header region:

- Identity and revision fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command and status bits: `COMMAND` fields such as I/O access, memory access, bus mastering, SERR, parity response, fast back-to-back, and interrupt disable; `STATUS` fields such as interrupt status, capability-list presence, DEVSEL timing, target/master aborts, system error, parity error, and immediate readiness.
- Header metadata: `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- BAR and ROM windows: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, and `ROM_BASE_ADDR`.
- Interrupt and legacy timing fields: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.

These definitions mirror PCI configuration-space semantics, but they are exposed as ASIC register fields for the virtualized NBIF decode path.

### PCI Express Capability and Link Control

For VF3 through VF6 this chunk defines PCIe capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` expose capability ID, next pointer, PCIe capability version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` encode maximum payload support/size, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, slot power information, function-level reset capability/initiation, error-reporting enables, no-snoop, read-request size, and pending/error status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` encode supported/current link speed, link width, ASPM and power-management controls, retraining, common clock, link disable, bandwidth interrupt enables/status, data-link active, and training state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` include completion-timeout support/control, ARI forwarding, atomic operation support/control, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix handling, emergency power reduction, and FRS support.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` include supported link speed vectors, compliance-mode controls, de-emphasis and transmit margin fields, equalization phase status, crosslink state, RTM presence, downstream component presence, and DRS message state.

These masks are integration points for PCIe link management, error handling, and virtualization policy code. They do not encode the ordering requirements for link retrain, FLR, or capability enablement; users must follow PCIe and AMDGPU sequencing rules around the register writes.

### MSI and MSI-X Configuration

Each covered VF includes MSI and MSI-X capability field masks:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` encode MSI capability ID, next pointer, MSI enable, multi-message capability/enable, 64-bit capability, and per-vector masking capability.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MSG_DATA_64`, `MSI_MASK`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64` provide the fields used for MSI target address, data, mask, and pending state.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` encode MSI-X enable/function mask, table size, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

These fields define interrupt-delivery configuration state for each VF. Misprogramming the address/data, mask, or MSI-X table/PBA fields can cause lost interrupts, unexpected interrupt routing, or VF isolation problems.

### Vendor-Specific Capability

For VF3 through VF6, the chunk defines `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.

The enhanced capability list and header fields provide `CAP_ID`, `CAP_VER`, `NEXT_PTR`, `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`. `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2` expose full-width `SCRATCH` fields. These scratch registers are vendor-defined state rather than standard PCIe fields; their meaning is established by AMD hardware/firmware conventions and the code that consumes them.

### Advanced Error Reporting, ATS, and ARI

The chunk fully covers VF3, VF4, and VF5 AER/ATS/ARI masks, while VF6 AER begins in the next chunk.

AER definitions include:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` for AER enhanced capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, and TLP prefix blocked errors.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` for first error pointer, ECRC generation/checking capability and enables, multi-header recording, and TLP prefix log presence.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` full-width capture fields.

ATS and ARI definitions include:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL`, covering capability-list metadata, invalidate queue depth, page-aligned requests, global invalidate support, ATC enable, and smallest translation unit.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering capability-list metadata, next function number, MFVC/ACS function group capability, function-group selection, and group enables.

These fields tie NBIO register layout to PCIe error reporting and virtualization features used by IOMMU and SR-IOV flows.

## Control Flow and State Behavior

This header has no runtime control flow. Its only effect is at compile time: C code includes the macros and uses them to construct or decode register values. The underlying state is hardware state in NBIO/NBIF PCI configuration-space windows.

Important state described by the chunk includes:

- Per-VF PCI identity, class, command, status, BAR, ROM, capability pointer, and interrupt-line/pin state.
- PCIe capability, device control/status, link control/status, and secondary capability state.
- MSI/MSI-X interrupt address, data, enable, mask, pending, table, and PBA state.
- AER status/mask/severity, header logs, TLP prefix logs, and ECRC controls for VF3 through VF5.
- ATS and ARI capability/control state for VF3 through VF5.
- Vendor-specific capability metadata and scratch fields.

Some fields are durable configuration bits, some are status bits, and some are action-oriented control bits. Examples include `INITIATE_FLR`, `RETRAIN_LINK`, MSI/MSI-X enable bits, error status bits, error masks, and ATC/ARI enables. The mask header does not describe whether a status bit is write-one-to-clear, sticky, read-only, or write-protected for a VF; that behavior comes from PCIe rules, AMD hardware documentation, and the owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header ecosystem:

- The matching `nbio_2_3_offset.h` file supplies register addresses for these names.
- The matching `nbio_2_3_default.h` file supplies reset/default values where generated.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` constants.
- PCI core and AMDGPU SR-IOV/NBIO code determine when the PF, VF, or hypervisor side may read or write each configuration field.

Integration points include:

- NBIO initialization and virtualization code that enumerates or programs per-VF BIF configuration-space state.
- SR-IOV enablement, reset, and VF management paths that need per-VF command/status, BAR, MSI/MSI-X, FLR, ARI, and AER layouts.
- PCIe link and error-handling code that interprets link status, device status, correctable/uncorrectable error status, masks, severities, and header logs.
- IOMMU/ATS related paths that coordinate `ATC_ENABLE`, invalidate capabilities, and STU programming with address translation policy.
- Interrupt setup paths that pair MSI/MSI-X address/data/table/PBA register layouts with Linux IRQ allocation and AMDGPU interrupt routing.

Because the same masks are repeated across VF instances, any generator or hand-editing error in one repeated block can silently affect only a subset of virtual functions. Cross-checking against the offset/default headers and hardware generation source is important when changing these definitions.

## Risks

- **Bitfield drift:** These constants are hardware ABI. A wrong shift or mask can make otherwise-correct driver code read or write the wrong PCIe field.
- **Partial chunk boundaries:** The range starts after the first VF3 PCIe capability fields and ends before VF6 AER. A final file-level report must merge neighboring chunks before drawing conclusions about complete VF3 or VF6 coverage.
- **Repeated-block assumptions:** VF4 and VF5 are complete in this chunk and appear mechanically identical in layout; consumers should not assume all VFs have identical runtime permissions or reset values merely because the mask layout is repeated.
- **Virtualization isolation:** MSI/MSI-X, BAR, command/status, AER, ATS, ARI, and vendor-specific scratch fields are per-VF state. Incorrect writes can leak PF/VF configuration, route interrupts incorrectly, expose memory windows, or break VF reset/error recovery.
- **PCIe sequencing:** Fields such as FLR initiation, link retrain, ARI forwarding, ATS ATC enable, MSI/MSI-X enable, and AER status clearing have ordering and polling requirements outside this header.
- **Generated-file maintenance:** Manual edits are risky. Regeneration from authoritative register descriptions is safer than patching individual masks.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- AMDGPU builds that include `nbio_2_3_sh_mask.h` without macro-name collisions or missing paired `__SHIFT`/`_MASK` definitions.
- Static comparison against the matching generated offset/default headers and AMD register database for NBIO 2.3 VF3/VF4/VF5/VF6 BIF config decode blocks.
- SR-IOV smoke tests with multiple VFs enabled, checking PCI enumeration, class/vendor/device IDs, BAR sizing, command/status behavior, FLR, and VF reset recovery.
- MSI and MSI-X tests on VFs, including interrupt enable/disable, masking, pending state, table/PBA placement, and interrupt delivery under load.
- PCIe AER injection or fault-observation tests for VF3 through VF5, verifying status, mask, severity, header log, and TLP prefix log interpretation.
- ATS/ARI validation in an IOMMU-enabled environment where supported, checking that capability bits and control fields match the advertised VF behavior.
- Link-management diagnostics that compare decoded link capability/control/status fields against `lspci -vv` and platform expectations.
