# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 58547-61039

## Purpose

This chunk is a generated AMD NBIO 7.2 shift/mask header slice for PCI/PCIe configuration-space fields under the NBIF BIF configuration decode path. It exports C preprocessor constants that describe bit positions and bit masks for `BIF_CFG_DEV0_EPF*_0_*` registers. The constants are not executable code; they are compile-time metadata used by AMDGPU register-access helpers to pack, update, and decode NBIO register fields.

The range starts inside the `BIF_CFG_DEV0_EPF4_0_DEVICE_CAP2` mask list, completes the remaining `DEV0_EPF4` PCIe capability families, covers the complete `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` address block, and begins the `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` address block through the first three masks of `BIF_CFG_DEV0_EPF6_0_DEVICE_CAP`. Adjacent chunks are required for the missing start of `DEV0_EPF4_DEVICE_CAP2` and the rest of `DEV0_EPF6_DEVICE_CAP` and later EPF6 registers.

## Public Surface In This Chunk

The public surface is 2,115 `#define` macros. Each field normally has a pair of names:

- `BIF_CFG_DEV0_EPFx_0_REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `BIF_CFG_DEV0_EPFx_0_REGISTER__FIELD_MASK` gives the field's bit mask in the containing register.

There are no C types, functions, enums, structs, storage objects, or inline helpers. The important API contract is name compatibility with the companion offset header, especially `nbio_7_2_0_offset.h`, where the corresponding `regBIF_CFG_DEV0_EPFx_0_REGISTER` or `cfgBIF_CFG_DEV0_EPFx_0_REGISTER` constants identify the register location. Consumers are expected to use these macros through common AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe-port access wrappers from implementation files such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`.

## Register Families Covered

The visible `DEV0_EPF4` continuation covers PCIe 2.0 capability fields, MSI/MSI-X, vendor-specific capability fields, AER fields, enhanced BAR controls, power budget, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester, and all 64 TPH steering table entries. Important groups include:

- `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout, ARI forwarding, atomic operations, IDO, LTR, OBFF, end-to-end TLP prefixes, supported/target link speeds, compliance, de-emphasis, 8 GT equalization state, DRS messages, and presence detection.
- `MSI_*` and `MSIX_*` fields for capability IDs, message control, 32-bit and 64-bit message address/data paths, mask and pending vectors, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- `PCIE_VENDOR_SPECIFIC_*` fields for enhanced capability headers and scratch dwords.
- `PCIE_ADV_ERR_RPT_*`, `PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, and `PCIE_ADV_ERR_CAP_CNTL` fields for AER capability linkage, uncorrectable error status/mask/severity bits, correctable error status/mask bits, first-error pointer, ECRC controls, multiple-header recording, TLP prefix log presence, completion timeout prefix/header logging, and poison TLP egress blocking.
- `PCIE_HDR_LOG*` and `PCIE_TLP_PREFIX_LOG*` full-width log fields.
- `PCIE_BAR*_CAP` and `PCIE_BAR*_CNTL` for enhanced BAR fixed-size capability and size/resize controls for BAR1 through BAR6.
- `PCIE_PWR_BUDGET_*` and `PCIE_DPA_*` for power budget data selection, selected power data fields, DPA substate support, transition latency, status, control, and power allocation registers 0 through 7.
- `PCIE_ACS_*`, `PCIE_PASID_*`, and `PCIE_ARI_*` for isolation, process address space ID, and alternative routing ID capability/control bits.
- `PCIE_TPH_REQR_*` and `PCIE_TPH_ST_TABLE_0` through `_63` for TPH requester capability/control and steering tags.

The `DEV0_EPF5` block begins at line 59500 and repeats the same endpoint-function layout from standard PCI header fields through the complete 64-entry TPH steering table. It includes vendor/device IDs, command/status, revision and class-code bytes, cache line/latency/header/BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, PM capability/status/control, SBRN, FLADJ, DBESL/DBESLD, PCIe capability, device/link capability and control/status, MSI/MSI-X, vendor-specific enhanced capability, AER, enhanced BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester fields.

The `DEV0_EPF6` block begins at line 60816. This chunk covers its standard PCI header fields, vendor capability, PM capability/status/control, SBRN, FLADJ, DBESL/DBESLD, PCIe capability list/capability, and the opening of `DEVICE_CAP`. The range stops after the `MAX_PAYLOAD_SUPPORT`, `PHANTOM_FUNC`, and `EXTENDED_TAG` masks, while the masks for L0s/L1 latency, role-based error reporting, captured slot power, and FLR capability continue in the next chunk.

## Important Field Semantics

The macros model packed PCI and PCIe configuration registers. Many fields are single-bit enables or status flags, while others are multi-bit enumerations. Examples visible in this chunk include:

- PCI command bits such as I/O space, memory space, bus master, special cycle, memory write/invalidate, palette snoop, parity error response, SERR, fast back-to-back, and interrupt disable.
- PCI status bits such as interrupt status, capability-list present, target/master abort, system error, parity error, DEVSEL timing, and immediate readiness.
- PCIe device capability fields for maximum payload, phantom functions, extended tags, acceptable L0s/L1 latency, role-based error reporting, captured slot power, and FLR capability.
- PCIe device control fields for maximum payload/read request size, relaxed ordering, no-snoop, AUX power PM, error reporting enables, extended tag, IDO, LTR, emergency power reduction, OBFF, and completion timeout handling.
- PCIe link fields for maximum/current link speed, maximum/current link width, ASPM, read completion boundary, common clock configuration, extended sync, link disable, retrain, slot clock configuration, autonomous bandwidth, equalization, de-emphasis, and link training state.
- AER fields for data link protocol errors, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, blocked TLP, atomic egress block, TLP prefix block, correctable receiver/bad TLP/bad DLLP/replay/ advisory/non-fatal/header-log overflow status, and matching mask/severity controls.
- ACS, PASID, ARI, and TPH fields that affect DMA isolation, address-space tagging, function routing, and transaction steering behavior.

Because the field names reflect PCIe architectural names, they are semantically meaningful even though the file itself does not enforce read-only, write-one-to-clear, sticky, firmware-owned, or sequencing rules.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow is entirely compile-time:

1. A driver source file includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
2. The driver selects a register offset macro from the offset header and the matching shift/mask macros from this header.
3. Register helper macros expand the shift/mask constants into bit extraction or bit update operations.
4. The actual read or write is performed by the AMDGPU MMIO or PCIe-port access layer.

This means the chunk cannot validate whether a caller selected the correct endpoint function, used the correct register width, or respected PCIe side effects. Those checks live in generated-header validation, driver logic, hardware tests, and review.

## State And Persistence

The header stores no runtime state and has no persistence behavior. It describes hardware state that lives in NBIO/PCIe configuration registers on AMD ASICs. Depending on the register, that hardware state may be reset-only capability information, writable driver configuration, sticky error status, write-one-to-clear status, firmware-programmed state, or values negotiated with the PCIe link partner.

The most important persistent or externally visible state represented by this chunk includes BAR sizing and enablement, command/status and class-code exposure, PM capability and power-state bits, MSI/MSI-X interrupt routing state, PCIe link capability/control/status, AER status/mask/severity state, ACS/PASID/ARI isolation and routing controls, TPH requester steering tables, power budget and DPA state, and early EPF6 PCIe device capability fields.

## Dependencies And Integration Points

The direct source-level dependency is the generated AMD register-header naming scheme. This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the matching register offsets and base indices.
- NBIO 7.2 implementation code such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes this header and uses NBIO field masks with AMDGPU register helpers.
- The shared AMDGPU register macro layer, which expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming to match `REG_GET_FIELD` and `REG_SET_FIELD` conventions.
- PCI and PCI Express architectural definitions for standard config header fields, PM capability, MSI, MSI-X, PCIe capability, AER, enhanced BAR, power budget, DPA, ACS, PASID, ARI, and TPH requester capabilities.

Cross-generation headers such as `nbio_7_0_sh_mask.h` and `nbio_7_7_0_sh_mask.h` contain similar field names and repeated endpoint-function layouts, but they are not interchangeable. A same-looking field can move, disappear, gain new bits, or map to a different function depending on ASIC generation and register-map source data.

## Risks And Maintenance Notes

- The chunk starts and ends mid-register family. The first visible lines are only the tail masks of `DEV0_EPF4_DEVICE_CAP2`, and the final visible lines are only the first masks of `DEV0_EPF6_DEVICE_CAP`. Any per-file summary must merge adjacent chunk reports before claiming complete coverage.
- Generated-header drift is hard to review because EPF4, EPF5, and EPF6 contain large repeated blocks with only the endpoint-function number changing. A single shifted bit, omitted mask, or incorrectly copied prefix can compile cleanly while decoding the wrong hardware field.
- Names alone do not encode access rules. AER status fields may be write-one-to-clear, link control fields can retrain or disable links, MSI/MSI-X fields affect interrupt delivery, and ACS/PASID/ARI fields affect DMA isolation and routing.
- Packed PCI config registers frequently contain adjacent fields with different access policies. Updating one field requires preserving unrelated bits with the correct mask and width.
- Some fields are capability declarations rather than safe-to-write controls. Treating capability bits as writable controls can produce ineffective writes or undefined hardware behavior.
- Cross-generation similarity creates a copy/paste hazard. Driver code must include and use the NBIO 7.2 header that matches the selected ASIC IP version rather than borrowing same-named masks from NBIO 7.0, 7.7, or 7.11 headers.
- EPF-specific names matter. Using an EPF5 mask with an EPF4 or EPF6 offset might appear harmless because the bit layout is often repeated, but it weakens generated-map consistency checks and can hide real differences in partial or future blocks.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and any other translation unit that includes `nbio_7_2_0_sh_mask.h`.
- Generated-header consistency checks that every `__SHIFT` macro in this line range has a corresponding `_MASK` macro where the full register family is present, while allowing the known partial boundaries at `DEV0_EPF4_DEVICE_CAP2` and `DEV0_EPF6_DEVICE_CAP`.
- Cross-header checks that every register family here has a matching offset macro in `nbio_7_2_0_offset.h` and that field names use the exact same `BIF_CFG_DEV0_EPFx_0_REGISTER` prefix.
- Hardware register-dump comparison on NBIO 7.2 ASICs using AMDGPU debug register reads and PCI config-space tools such as `lspci -vvxxx`, especially for command/status, PM, MSI/MSI-X, PCIe capability, AER, ACS/PASID/ARI, TPH, power budget, DPA, and early EPF6 device capability fields.
- Interrupt tests that verify MSI/MSI-X enable, mask, pending, table, and PBA fields decode consistently with observed interrupt delivery.
- PCIe link and error-path tests that exercise AER status/mask/severity decoding, completion timeout behavior, link status/equalization fields, LTR/OBFF controls, and DRS/presence status without disturbing unrelated endpoint functions.
- IOMMU and virtualization-oriented tests that inspect ACS, PASID, and ARI capability/control behavior where supported by the hardware and firmware configuration.
