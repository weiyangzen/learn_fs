# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 14756-17197

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.11.0 register mask header. The range starts in the middle of `BIF_CFG_DEV2_EPF5_LINK_CAP`, at the PCIe link-capability reporting fields, and ends inside `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`, after the first three corrected-error mask fields. It contains 2,145 preprocessor definitions, including 1,071 `__SHIFT` constants and 1,170 `_MASK` constants.

The covered address blocks are:

- Tail of `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`: DEV2 endpoint function 5 PCIe capability, MSI/MSI-X, SATA, vendor-specific, advanced error reporting, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR field layouts.
- All visible `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`: DEV2 endpoint function 6 standard PCI config header fields plus the same PCIe capability and extended-capability families as EPF5.
- Start of `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`: DEV0 endpoint function 5 standard PCI config header fields, PMI/USB-related fields, PCIe capability fields, MSI/MSI-X, SATA, vendor-specific capability, and the beginning of AER corrected-error masks.

This file is generated register-description data. It has no C functions, structs, variables, loops, branches, or direct storage. Its behavior comes from how compiled driver code combines these macros with matching register offsets and AMDGPU bitfield helpers.

## Purpose

The purpose of this chunk is to define bit-level layouts for several NBIO PCI/PCIe configuration spaces on AMD GPU ASICs using NBIO 7.11.0. Each hardware field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or update the field.

The sibling `nbio_7_11_0_offset.h` file supplies register addresses and base indices. For example, the matching offsets identify DEV0 EPF5 at `regBIF_CFG_DEV0_EPF5_0_VENDOR_ID` address `0x11400`, DEV2 EPF5 at `regBIF_CFG_DEV2_EPF5_0_VENDOR_ID` address `0x15400`, and DEV2 EPF6 at `regBIF_CFG_DEV2_EPF6_0_VENDOR_ID` address `0x15800`. This chunk supplies the masks for fields inside those registers, including AER registers such as `regBIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_STATUS`, `regBIF_CFG_DEV2_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV2_EPF6_0_PCIE_UNCORR_ERR_STATUS`.

AMDGPU code includes this header from `amdgpu/nbio_v7_11.c` together with the matching offset header. The normal consumers are register helpers such as `REG_SET_FIELD`, direct mask tests, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### PCIe Link and Device Capabilities

The chunk begins with the remaining `BIF_CFG_DEV2_EPF5_LINK_CAP` fields:

- Data-link active reporting capability.
- Link bandwidth notification capability.
- ASPM optionality compliance.
- Port number.

It then defines complete `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` layouts for DEV2 EPF5, DEV2 EPF6, and DEV0 EPF5. These fields cover PCIe link speed and width, link retrain and disable controls, common-clock and extended-sync controls, clock power management, link bandwidth interrupts/status, completion timeout support/control, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, Gen3 equalization status, crosslink state, RTM presence detection, downstream component presence, and DRS support/signaling.

These macros are capability-space definitions rather than policy. The kernel PCI core and firmware normally own most PCIe config negotiation. AMDGPU-specific NBIO code can still use these masks for ASIC-specific diagnostics, workarounds, or direct config-space access through NBIO/PCIE index-data windows.

### Standard PCI Config Header Fields

The DEV2 EPF6 and DEV0 EPF5 sections include ordinary PCI header fields:

- Vendor/device ID.
- Command and status.
- Revision, programming interface, subclass, and base class.
- Cache line size, latency timer, header type, BIST.
- BARs 1 through 6 and ROM BAR.
- Capability pointer, interrupt line/pin, min grant, max latency.
- Adapter/vendor capability registers.

The `COMMAND` and `STATUS` masks expose standard PCI enable/status bits such as I/O space, memory space, bus mastering, parity and SERR enables, interrupt disable, interrupt status, capability-list presence, 66 MHz capability, fast back-to-back support, master data parity error, DEVSEL timing, signaled target abort, received target abort, received master abort, signaled system error, and detected parity error.

Because these are PCI config-space fields, many bits are controlled by enumeration, firmware, PCI core policy, or device reset state. Direct AMDGPU writes must preserve unrelated bits with read-modify-write helpers.

### Power Management and USB/SATA-Related Capability Fields

The chunk includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` layouts for the endpoint functions. These define capability ID/next pointer, PCI power-management version, PME clock and D-state support, D1/D2 support, PME support, power state, no-soft-reset, PME enable/status, data select/scale, and power-management data fields.

DEV0 EPF5 also includes `SBRN`, `FLADJ`, and `DBESL_DBESLD`, which are USB-related capability fields for serial bus release number, frame-length adjustment, and BESL/deep-BESL latency values. DEV2 EPF5, DEV2 EPF6, and DEV0 EPF5 include SATA capability and indirect data port definitions:

- `SATA_CAP_0` and `SATA_CAP_1` identify capability revision, BAR location, and BAR offset.
- `SATA_IDP_INDEX` and `SATA_IDP_DATA` describe the indirect index/data port format.

These definitions let the driver decode hardware-exposed PCI capabilities when NBIO presents non-graphics endpoint functions or embedded endpoint capabilities.

### MSI and MSI-X Capability Fields

For each covered endpoint function, the chunk defines MSI and MSI-X capability layouts:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` include capability ID, next pointer, MSI enable, multiple-message capable/enable, 64-bit address capability, per-vector masking, extended message capability, and hypertransport-specific alias fields.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, and their 64-bit forms expose interrupt message address/data fields.
- `MSI_MASK`, `MSI_PENDING`, `MSI_MASK_64`, and `MSI_PENDING_64` expose per-vector mask and pending bits.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` expose MSI-X enable, function mask, table size, table/PBA BIR, and offsets.

Interrupt routing is high risk because MSI/MSI-X state interacts with the kernel PCI subsystem, interrupt remapping, IOMMU state, and GPU interrupt handler setup. These generated masks only define wire format; they do not encode ownership or ordering.

### Vendor-Specific and Routing Capability Fields

The `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` fields define extended capability headers, vendor-specific IDs/revisions/lengths, and scratch registers. These are AMD/vendor extension points.

The `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` fields define routing-related extended capability metadata and data values. They expose capability ID/version/next pointer and opaque data fields.

### Advanced Error Reporting

The AER families are repeated for DEV2 EPF5, DEV2 EPF6, and partially for DEV0 EPF5:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines the AER extended capability header.
- `PCIE_UNCORR_ERR_STATUS` exposes uncorrectable error status bits: DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- `PCIE_UNCORR_ERR_MASK` controls masking for the same uncorrectable error classes.
- `PCIE_UNCORR_ERR_SEVERITY` controls whether each uncorrectable error is treated as fatal or non-fatal.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal, and correctable internal error bits.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC generation/check capability and enable bits, and multi-header receive capability/enable bits.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` provide captured TLP header and prefix log storage.

The assigned range ends after `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK__BAD_DLLP_MASK_MASK`; the remaining DEV0 EPF5 corrected-error mask fields and `ADV_ERR_CAP_CNTL` fields continue in the next chunk.

### BAR, Power Budget, DPA, ACS, PASID, and ARI Extended Capabilities

DEV2 EPF5 and DEV2 EPF6 include complete definitions for several PCIe extended capabilities:

- BAR enhanced capability: capability header plus BAR 1 through BAR 6 capability/control fields for fixed BAR size, BAR size capability, and atomic operation routing/blocking behavior.
- Power budget capability: data select, base power, data scale, PM substate, power rail, type, and system allocation.
- Dynamic Power Allocation: capability/control/status fields, latency indicator, transition completed status, substate enable, and substate power allocation fields 0 through 7.
- ACS: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and I/O request blocking capability/control bits.
- PASID: execution permission, privileged mode, max PASID width, and enable controls.
- ARI: next function, function group, multi-function group, and ACS function group control fields.

These fields matter for virtualization, IOMMU, peer-to-peer routing, atomic operations, and power-management behavior. They should be interpreted against the endpoint function and PCIe capability chain that owns them, not as global NBIO state.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It affects behavior at compile time by providing constants used by C code to compose and decode MMIO or PCI configuration register values.

The state described by these macros is persistent hardware state in NBIO PCIe configuration space. Some fields are latched capability bits, some are driver/PCI-core owned control bits, some are sticky status/error bits, and some are log registers capturing the first or most recent PCIe error context. Examples include link status, completion-timeout control, MSI mask/pending state, MSI-X function mask, AER status/mask/severity registers, header logs, PASID/ACS/ARI controls, DPA substate allocation, BAR control, and power-management status.

Several status fields are clear-on-write or sticky according to PCIe rules, especially error status registers. The macros do not express those semantics. Callers must follow PCI/PCIe and AMD NBIO programming sequences, including preserving reserved bits and using the correct error-clear value.

## Dependencies and Integration Points

This chunk depends on the generated NBIO register-header set:

- `nbio_7_11_0_offset.h` provides register addresses and base indices for the register names whose fields are defined here.
- `nbio_7_11_0_default.h`, where present for a register family, provides reset/default values.
- AMDGPU helper macros consume `__SHIFT` and `_MASK` constants for field extraction and updates.

Observed integration in this source tree:

- `amdgpu/nbio_v7_11.c` includes both `nbio/nbio_7_11_0_offset.h` and this mask header.
- `nbio_v7_11.c` uses these headers for NBIO setup functions including HDP flush offsets, PCIE index/data windows, PCIE port index/data windows, doorbell ranges, interrupt handling, memory-controller access, register remap, medium-grain clock gating, light sleep, and NBIO initialization.
- The local initialization path writes `regRCC_DEV0_EPF5_STRAP4` for NBIO IP versions 7.11.0 through 7.11.4, showing that DEV0 EPF5-related config state is part of the NBIO 7.11 setup surface even though this exact chunk covers config-space masks rather than that strap register.
- PCIe config-space fields in this chunk can also be reached indirectly through NBIO PCIE index/data windows returned by `nbio_v7_11_get_pcie_index_offset`, `nbio_v7_11_get_pcie_data_offset`, `nbio_v7_11_get_pcie_port_index_offset`, and `nbio_v7_11_get_pcie_port_data_offset`.

Cross-generation similarity is high. Similar AER and PCIe capability masks appear in other NBIO generations such as `nbio_7_7_0_sh_mask.h` and `nbio_7_2_0_sh_mask.h`, but consumers must include the matching 7.11.0 offset/mask/default set because address maps and endpoint-function coverage differ by ASIC generation.

## Risks

- Register/mask mismatch: using a 7.11.0 mask with another NBIO generation's offset can silently target the wrong field or endpoint function.
- Endpoint-function confusion: DEV0 EPF5, DEV2 EPF5, and DEV2 EPF6 have similar field names but different config-space address ranges.
- Reserved-bit damage: many PCIe capability registers include reserved bits or hardware-owned status bits; direct writes must preserve unrelated fields.
- Interrupt disruption: MSI/MSI-X enable, mask, pending, table, and PBA fields can affect interrupt delivery and must stay coordinated with PCI core and AMDGPU interrupt setup.
- Error-reporting regressions: AER status/mask/severity fields influence PCIe error visibility and fatal/non-fatal classification. Incorrect masks can hide link/device failures or escalate recoverable errors.
- Link training and power-management instability: link control, ASPM, completion timeout, LTR, OBFF, emergency power reduction, and DPA fields affect PCIe negotiation and low-power behavior.
- Virtualization and isolation risk: ACS, PASID, ARI, atomic-op, and BAR enhanced capability fields affect routing, request identity, and peer-to-peer behavior. Incorrect programming can break IOMMU isolation or P2P access assumptions.
- Generated-header drift: manual edits to this file are risky because the source of truth is likely an AMD register database; regenerated headers can overwrite local changes.

## Test Signals

Useful validation signals for changes involving this chunk are mostly integration and hardware-facing:

- The AMDGPU driver builds cleanly with `nbio_v7_11.c` including this header and no undefined or duplicate macros.
- `REG_SET_FIELD`/`REG_GET_FIELD` users compile against expected field names after any generated-header update.
- Boot logs show successful NBIO initialization for IP versions 7.11.0 through 7.11.4, with no PCIe config, AER, interrupt, or doorbell setup errors.
- PCI enumeration exposes expected endpoint functions and capability chains through `lspci -vvv`, including MSI/MSI-X, PCIe, AER, ACS/PASID/ARI where applicable.
- Runtime GPU workloads do not report new AER errors such as completion timeout, malformed TLP, ECRC, unsupported request, receiver overflow, or surprise down.
- Suspend/resume, hot reset, FLR, and GPU reset paths preserve PCIe link state, MSI/MSI-X delivery, and error-reporting configuration.
- Virtualization or SR-IOV test lanes, if applicable to the ASIC, confirm ACS/PASID/ARI routing and per-function interrupts still work.
- Header consistency checks compare the shift/mask definitions against the matching `nbio_7_11_0_offset.h` register names and any generated default header.
