# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 19675-22130

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 register field header. It contains C preprocessor constants for bit shifts and masks in PCI/PCIe configuration-space registers exposed through the NBIO BIF configuration decoder. The source is not executable logic: it is a hardware contract layer used by driver code and register helper macros to extract or compose fields without hard-coded numeric bit positions.

The requested slice starts inside the `BIF_CFG_DEV0_EPF7_COMMAND` field set, covers the rest of the `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` address block, and then begins the `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` address block. The `DEV0_EPF7` portion describes a complete PCIe endpoint/function configuration surface for function 7 of device 0. The `DEV1_EPF0` portion repeats the same conventional PCI header and PCIe capability surface for function 0 of device 1 and extends through lane 3 PCIe margining status before the chunk ends.

The companion offset definitions live in `nbio_7_11_0_offset.h`, while this header supplies field-level masks and shifts. `amdgpu/nbio_v7_11.c` includes both headers and uses their macros through standard AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and field helpers such as `REG_SET_FIELD`.

## Register And Macro Groups

The constants follow the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the field in the register value.
- Comment lines such as `//BIF_CFG_DEV1_EPF0_PCIE_UNCORR_ERR_STATUS` separate logical registers.
- Address block comments identify the hardware block to pair with offset macros from the sibling offset header.

Major `DEV0_EPF7` groups in this chunk include:

- Standard PCI header fields: command/status, revision, class codes, cache line size, latency, header type, BIST, BAR1 through BAR6, subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Power-management capability fields: PMI capability list, PME support, D-state support, PME enable/status, data select/scale, bus power enable, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe capability fields: device capabilities/control/status, link capabilities/control/status, and second-generation capability/control/status fields for extended tags, payload sizes, relaxed ordering, error reporting enables, link width/speed, ASPM, L0s/L1 exit latencies, retrain/common-clock controls, slot clock, target link speed, equalization, and link bandwidth status.
- MSI and MSI-X configuration fields: MSI capability list, message control, 32-bit and 64-bit message address/data/mask/pending registers, MSI-X message control, table BAR/offset, and PBA BAR/offset.
- SATA capability placeholders: `SATA_CAP_0`, `SATA_CAP_1`, IDP index, and IDP data.
- PCIe extended capabilities: vendor-specific capability header/data, AER uncorrectable/correctable status/mask/severity, AER capability/control and header/TLP prefix logs, enhanced BAR capabilities and controls for BAR1 through BAR6, power budget, dynamic power allocation, ACS, PASID, ARI, and readiness time reporting.

Major `DEV1_EPF0` groups in this chunk include:

- The same standard PCI header, PM, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, enhanced BAR, power budget, and DPA fields.
- A PCIe Virtual Channel extended capability for port VC capability/control/status and VC0/VC1 resource capability/control/status. These fields model traffic class to virtual channel mappings, arbitration table status, VC IDs, and VC enable/negotiation state.
- Secondary PCIe, ACS, PASID, LTR, ARI, DLF, 16 GT/s PHY, and margining extended capability groups. The chunk includes lane equalization controls for 8 GT/s and 16 GT/s links, link status bits for 16 GT/s equalization phases, parity mismatch status registers, and lane margining controls/status for lanes 0 through 3.

## Important Interfaces And Integration Points

This header does not define functions or types. Its API is the macro namespace consumed by low-level AMDGPU code. Important integration points are:

- `nbio_7_11_0_offset.h`: provides the matching `reg...` address constants and `BASE_IDX` values. The offsets locate registers; this chunk's masks and shifts interpret the values read from those offsets.
- `amdgpu/nbio_v7_11.c`: includes the header and demonstrates the intended pattern: read a hardware register, modify a field with `REG_SET_FIELD`, then write it back. The visible file mostly uses other NBIO fields, but it establishes that this header is part of the NBIO 7.11 register-access contract.
- PCI/PCIe core concepts in the kernel and hardware: these masks encode conventional PCI command/status, BAR, MSI/MSI-X, PCI Express capability, AER, ACS, PASID, ARI, LTR, DPA, DLF, 16 GT/s PHY, and lane margining semantics. Higher-level code depends on these definitions matching the silicon register layout.
- GPU virtualization and multi-function exposure: `DEV0_EPF7` and `DEV1_EPF0` names indicate endpoint/function surfaces. Fields such as ACS, PASID, ARI, BAR sizing, MSI/MSI-X, and readiness-time reporting are especially relevant when the GPU exposes multiple PCIe functions or participates in IOMMU/PASID-aware compute paths.

Because these macros are generated constants, downstream usage usually appears indirectly through generic field helpers rather than function calls in this header.

## Control Flow And Behavior

There is no runtime control flow in this chunk. The behavioral flow appears only when driver code uses the definitions:

1. Driver code reads a 16-bit or 32-bit PCIe/NBIO register through an MMIO or PCIe-port access helper.
2. Code isolates a field by applying the generated mask and shifting right by the generated shift, or composes a field by clearing the mask and ORing the shifted value.
3. Code may write the modified register back to enable/disable capabilities, program BAR capability controls, clear/write-one-to-clear status bits, or configure error reporting and link behavior.

The exact read/write semantics are hardware-specific. Many named fields are status bits, capability bits, enable bits, or write-one-to-clear error bits. The header itself cannot encode access permissions, reset values, side effects, ordering requirements, or whether a given bit is read-only, write-only, read-write, sticky, or clear-on-write. Callers must rely on the hardware specification and existing driver patterns.

## State And Persistence Behavior

The header has no in-memory state and persists nothing by itself. It describes persistent and semi-persistent hardware state in PCI/PCIe configuration registers:

- Command bits such as memory access, bus mastering, SERR enable, and interrupt disable affect device behavior until firmware, the OS, reset, or driver code changes them.
- BAR fields and enhanced BAR control/capability fields describe resource apertures that the PCI core and driver use to map GPU memory and MMIO resources.
- MSI/MSI-X registers hold interrupt routing configuration and masks/pending state.
- PM and DPA fields describe power-management capabilities and current control/status selections.
- AER status/mask/severity and header/TLP-prefix logs capture error state that can survive until explicitly cleared or reset.
- Link status, equalization status, parity mismatch, and margining fields reflect current physical-link condition and training state.

Persistence should be understood as device register persistence across the relevant reset domain, not filesystem or kernel object persistence.

## Dependencies

The chunk depends on AMD's generated register database for NBIO 7.11.0. It also depends on the local AMDGPU register helper conventions:

- Register values are generally `u32` even when the underlying PCI config field is logically 8 or 16 bits; masks such as `0xFFL`, `0xFFFFL`, and `0xFFFFFFFFL` encode the active field width.
- `REG_SET_FIELD` and related helper macros expect the register prefix and field name to match the `__SHIFT` and `_MASK` symbols in this file.
- The sibling offset header must stay synchronized with this mask header. A correct mask with the wrong offset, or a correct offset with the wrong mask, is equally dangerous.

This file is hardware-family-specific. Similar macro names appear in other NBIO generation headers, but small capability differences are expected between ASIC generations and should not be merged by hand.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit shift or mask can silently program the wrong hardware field, misreport capability status, or corrupt adjacent fields.
- The chunk begins mid-register at line 19675. Any per-chunk consumer must merge it with the previous chunk to get the full `BIF_CFG_DEV0_EPF7_COMMAND` definition, including the `IO_ACCESS_EN` and `MEM_ACCESS_EN` shift constants immediately before the requested line range.
- Several registers contain similarly named `_MASK_MASK` constants, such as AER uncorrectable error mask fields. These names are generated from fields already named `..._MASK`; callers and reviewers must distinguish the field name from the macro suffix.
- Error status fields such as AER uncorrectable/correctable status, MSI pending bits, and parity mismatch status may have special clear semantics. Treating all fields as normal read/write fields can lose diagnostic state or fail to clear latched errors.
- Link training and equalization fields are timing-sensitive. Polling or writing related control bits without respecting hardware sequencing can destabilize PCIe link negotiation, especially around 8 GT/s and 16 GT/s equalization and margining.
- ACS, PASID, ARI, and VC controls affect isolation, address translation, traffic routing, and virtualization behavior. Incorrect programming can break IOMMU isolation, GPU compute process addressing, SR-IOV-like function routing, or peer-to-peer traffic policy.
- BAR sizing/control fields are resource-enumeration critical. Bad masks can produce incorrect aperture sizes or BAR indexes, leading to failed resource allocation or invalid MMIO mappings.
- Some fields are capability-only or reserved. The presence of a mask macro does not imply driver code may write the field.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration signals:

- Kernel build coverage for `amdgpu/nbio_v7_11.c` and any other NBIO 7.11 consumers verifies that generated macro names match helper usage.
- Static checks can compare every `REG_SET_FIELD(..., REGISTER, FIELD, ...)` use against the existence of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- Generated-header consistency tests should compare this header against the AMD register source used to produce `nbio_7_11_0_offset.h`, including paired register offsets and masks for `DEV0_EPF7` and `DEV1_EPF0`.
- Runtime smoke tests should validate GPU enumeration, BAR assignment, interrupt delivery, and basic memory access on hardware using NBIO 7.11.0.
- PCIe diagnostics should watch AER counters/logs, MSI/MSI-X masking and pending behavior, link width/speed, link retraining/equalization status, and power-management transitions after driver initialization, suspend/resume, FLR, and hot reset.
- Virtualization and compute tests should cover PASID, ACS, ARI, and IOMMU/KFD paths if the ASIC exposes those capabilities.
- Margining and high-speed link tests should confirm 16 GT/s equalization status bits, parity mismatch status, and lane margining ready/status behavior on supported platforms.

Because this is a generated register contract, a clean compile is necessary but not sufficient. The strongest signal is successful operation on matching hardware with PCIe config-space behavior agreeing with the public PCIe capability model and AMD's silicon register specification.
