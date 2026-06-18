# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 142582-145028

## Scope

This chunk is a generated AMD NBIO 7.7.0 shift/mask header slice. It contains C preprocessor constants only; there are no executable functions, structs, callbacks, locks, or allocation paths. The range starts in the tail of the `BIF_CFG_DEV0_EPF2_1` endpoint-function PCI configuration block, covers a complete `BIF_CFG_DEV0_EPF3_1` block for `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, and ends partway through the `BIF_CFG_DEV0_EPF4_1` block at the ACS control fields.

The chunk defines 2,132 `#define` entries. Each register field generally appears as a pair:

- `REGISTER__FIELD__SHIFT`: the low bit position for the field.
- `REGISTER__FIELD_MASK`: the unshifted bit mask in the register value.

## Purpose and Register Families

The constants describe PCI/PCIe configuration-space and extended-capability bitfields exposed by AMD's NBIO/BIF fabric for device 0 endpoint functions. They are used by AMDGPU register helper macros to extract and program individual fields without embedding raw bit numbers in driver code.

The `BIF_CFG_DEV0_EPF2_1` tail contains:

- MSI-X PBA location fields: `MSIX_PBA_BIR` and `MSIX_PBA_OFFSET`.
- SATA capability and indexed data-port fields: SATA capability revisions, BAR location/offset, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`.
- Vendor-specific PCIe extended capability list/header/scratch fields.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity, correctable error status/mask, ECRC capability/control, multiple header log registers, and TLP prefix logs.
- PCIe BAR enhanced capability fields for BAR1 through BAR6, including supported size, selected size, BAR index, total BAR count, and upper supported-size fields.
- Power Budgeting capability fields: data select, base power, scale, PM state/substate, type, power rail, and system-allocated flag.
- Dynamic Power Allocation fields: DPA capability, transition latency indicators, current/enabled substate status, substate control, and substate power allocation entries 0-7.
- ACS, PASID, and ARI extended capability fields: peer-to-peer control/isolation bits, PASID enable/permissions/width, and ARI next-function/group controls.

The `BIF_CFG_DEV0_EPF3_1` block is a full endpoint-function configuration view. It includes:

- Standard PCI identity and header fields: vendor/device IDs, command/status, revision/programming interface/subclass/base class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- Vendor, PM, and USB-style capability fields: vendor capability list, writable adapter ID, PMI capability/status/control/data, `SBRN`, `FLADJ`, and BESL/deep-BESL fields.
- PCI Express capability fields: device capability/control/status, link capability/control/status, device/link capability 2, control 2, and status 2.
- MSI and MSI-X fields: capability list pointers, message control, 32-bit and 64-bit message address/data, extended message data, mask and pending bitmaps, MSI-X table size/function mask/enable, table BAR indicator/offset, and PBA BAR indicator/offset.
- SATA, vendor-specific, AER, BAR enhanced capability, power budgeting, DPA, ACS, PASID, and ARI groups that mirror the EPF2_1 tail but for EPF3_1.

The `BIF_CFG_DEV0_EPF4_1` portion begins the same endpoint-function pattern for EPF4_1:

- Standard PCI identity/header, BAR, ROM, adapter ID, interrupt, vendor capability, PM, and PCIe capability fields.
- PCIe device/link capability and control fields, including max payload/read request size, FLR, relaxed ordering, no-snoop, ASPM/clock power management, retrain/link disable, DRS signaling, current link speed/width, DL active, link bandwidth status, target link speed, compliance controls, de-emphasis, transmit margin, and equalization status.
- MSI/MSI-X, SATA, vendor-specific, AER, BAR enhanced capability, power budgeting, DPA, and ACS fields up to `BIF_CFG_DEV0_EPF4_1_PCIE_ACS_CNTL`.

## Important APIs, Types, and Macros

This header does not define callable APIs. Its exported surface is the generated macro namespace used by AMDGPU's SOC15/NBIO register access layer:

- Field readers such as `REG_GET_FIELD(value, reg, field)` expand to this file's `_MASK` and `__SHIFT` constants.
- Field writers such as `REG_SET_FIELD(value, reg, field, new_value)` use the same constants to clear and insert bitfield values.
- Register access wrappers such as `RREG32_SOC15`, `WREG32_SOC15`, and field-specific write helpers combine these masks with register address definitions from the companion `nbio_7_7_0_d.h` header.

The naming convention is the main interface contract. For example, the EPF3 PCIe link-control group exposes fields such as `BIF_CFG_DEV0_EPF3_1_LINK_CNTL__RETRAIN_LINK__SHIFT` and `BIF_CFG_DEV0_EPF3_1_LINK_CNTL__RETRAIN_LINK_MASK`; code that asks the helper macros for `LINK_CNTL, RETRAIN_LINK` relies on both symbols existing and matching the hardware spec.

## Control Flow and Data Flow

There is no direct control flow in this chunk. Runtime behavior occurs when driver or PCI support code uses these constants:

1. A driver reads a hardware register or PCI configuration-space register using the address from the matching `*_d.h` register header.
2. The code extracts a field with a helper macro, or builds a modified register value by clearing the field mask and shifting a new value into place.
3. A write updates device hardware state, while a read obtains hardware status, firmware-initialized configuration, or PCI core-programmed configuration.
4. Hardware may asynchronously set status bits for errors, link state, power-management state, pending interrupts, or DPA/DPC-style events. Software may clear some of those bits according to the register's hardware-defined semantics.

The chunk's field groups model repeated PCIe capability flow rather than driver control flow: standard config header fields lead to capability-list fields, which point to PM/PCIe/MSI/MSI-X/SATA/vendor/AER/BAR/power/DPA/ACS/PASID/ARI extended capability structures. The EPF2_1, EPF3_1, and EPF4_1 prefixes distinguish otherwise similar capability layouts for different endpoint functions.

## State and Persistence

The header itself has no mutable software state and no persistence format. The represented state is in hardware registers:

- PCI command/status, BAR, ROM, interrupt, class, capability pointer, subsystem, PM, MSI, and MSI-X fields are configuration-space state. They may be initialized by firmware, enumerated by the PCI core, and adjusted by the AMDGPU driver or generic PCI infrastructure.
- AER fields capture link/protocol errors such as DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked events. Header-log and TLP-prefix-log registers preserve diagnostic payload until cleared or overwritten by hardware semantics.
- Link capability/control/status fields reflect negotiated speed/width, training, DL active, bandwidth-management state, target speed, equalization, compliance, margining/de-emphasis, and optional DRS/crosslink support.
- Power-oriented groups include PM status/control, Power Budgeting data, DPA latency/substate/power-allocation registers, and PCIe LTR/OBFF-related controls in device capability 2/control 2.
- ACS/PASID/ARI fields represent isolation, process address-space tagging, and function-numbering capability/control state relevant to virtualization, peer-to-peer routing, and IOMMU integration.

Hardware reset, FLR, hot reset, suspend/resume, and PCI re-enumeration can change the underlying register state. The masks remain compile-time constants; if one is wrong, every caller using that field will consistently read or program the wrong bits.

## Dependencies and Integration Points

This file belongs to the generated AMDGPU ASIC register database under `drivers/gpu/drm/amd/include/asic_reg/nbio`. The chunk depends on:

- `nbio_7_7_0_d.h` for register offsets and address-block definitions.
- AMDGPU SOC15 register helpers and common bitfield helpers.
- Generic PCI/PCIe configuration-space rules for command/status, BAR sizing, capability list traversal, PM, MSI, MSI-X, AER, ACS, PASID, ARI, power budgeting, DPA, and link capability/control/status registers.
- Hardware documentation or generated register XML for the exact NBIO 7.7.0 field positions.

Integration is compile-time and indirect. The AMDGPU driver includes the ASIC-specific header selected for the device generation, then uses field names through helper macros. The PCI core owns much of the normal configuration-space programming, while AMDGPU/NBIO code may use these fields for ASIC setup, link diagnostics, error handling, RAS reporting, interrupt configuration, reset handling, and power-management coordination.

## Risks and Edge Cases

- The EPF2_1, EPF3_1, and EPF4_1 blocks repeat many register names with only the endpoint-function prefix changed. Using the wrong prefix would target the wrong function's layout or decode the wrong function's status.
- Status, mask, severity, and control registers in AER have similar bit positions but different semantics. Mixing `*_STATUS`, `*_MASK`, and `*_SEVERITY` symbols could hide errors, misclassify fatality, or clear evidence unexpectedly.
- Some PCI/PCIe status bits are write-one-to-clear or otherwise side-effectful in hardware. Treating `_MASK` definitions as permission to do ordinary read/modify/write on status registers can lose interrupts or diagnostic state.
- BAR enhanced capability fields are repeated for BAR1-BAR6. Size-supported and size-selected fields must remain aligned with PCI BAR probing and with firmware/PCI core resource assignment.
- MSI/MSI-X fields split table/PBA BAR indicators from offsets and include both 32-bit and 64-bit MSI data/mask/pending variants. Incorrect extraction can route interrupts to the wrong address/data or mask the wrong vectors.
- Link-control fields such as `LINK_DIS`, `RETRAIN_LINK`, `TARGET_LINK_SPEED`, compliance controls, autonomous speed/width disables, and de-emphasis/margin settings can disrupt the PCIe link if programmed outside the expected training sequence.
- ACS/PASID/ARI masks define security- and isolation-relevant controls. A stale mask could enable peer-to-peer forwarding, translated requests, PASID privileges, or ARI function behavior incorrectly.
- Capability existence cannot be inferred solely from a macro definition. The actual register value, capability chain, ASIC feature tables, firmware setup, and PCI enumeration decide whether a field is meaningful on a specific device.

## Test and Validation Signals

Useful validation is indirect because the chunk has no standalone logic:

- Build coverage for AMDGPU configurations that include `nbio_7_7_0_sh_mask.h`; missing or renamed macros surface as compile failures in code paths that use these fields.
- PCI enumeration checks with `lspci -vv` on NBIO 7.7.0 hardware, confirming EPF3/EPF4 identity, BARs, PM, PCIe, MSI/MSI-X, AER, ACS, PASID, ARI, and power capability values match expectations.
- Runtime readback through AMDGPU debug paths or register dumps, especially for EPF3_1/EPF4_1 link speed/width, payload/read-request size, FLR, MSI-X table/PBA location, ACS controls, PASID controls, and AER mask/severity/status fields.
- AER/RAS/error-injection tests that verify uncorrectable/correctable status bits, mask bits, severity bits, ECRC controls, header logs, and TLP prefix logs decode to the same events reported by PCIe tooling.
- Interrupt tests covering MSI and MSI-X setup, masking, pending bits, function mask, table location, and PBA location for the affected endpoint functions.
- Link training, hot reset, FLR, suspend/resume, and power-management tests that verify programmed PCIe control fields are restored or reinitialized and that link-status/equalization fields decode correctly after state transitions.
