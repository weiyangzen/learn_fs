# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 9838-12285

## Scope And Purpose

This chunk is generated register-field metadata for AMD NBIO 7.11.0 PCI/PCIe configuration-space registers. It contains only C preprocessor macros: each register field has a `__SHIFT` value and a corresponding `_MASK` value. The chunk starts in the `BIF_CFG_DEV2_EPF0` endpoint-function register block, continues through that block's conventional PCI header, PCIe capability, MSI/MSI-X, SATA, vendor-specific, advanced error reporting, resizable BAR, power-budgeting, DPA, ACS, PASID, ARI, data-link feature, 16 GT PHY, lane equalization, lane margining, and RTR capability fields, then enters the `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` address block and covers `BIF_CFG_DEV0_EPF4` through part of BAR5 control.

The header is a hardware contract, not executable logic. The macros let AMDGPU/NBIO code extract, construct, and update bitfields without hard-coding raw bit positions. They are intended to be used with the sibling `nbio_7_11_0_offset.h` register-address macros and the AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Important Macro Families

`BIF_CFG_DEV2_EPF0_*` describes the PCIe endpoint function 0 under device 2. The visible fields cover:

- Basic PCI configuration header pieces: latency/header/BIST, BAR1-BAR6 base addresses, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability list.
- Power management and USB/SATA-adjacent capability fields: PMI capability list, power state/PME status/control, SBRN, FLADJ, DBESL/DBESLD, SATA capability/header and indirect data port index/data.
- PCIe capability and control/status fields: device capabilities, device control/status, link capabilities, link control/status, link capability/control/status 2, and feature bits such as FLR, max payload, max read request size, ASPM, common-clock config, retrain link, target speed, equalization completion, and lane/preset indicators.
- Interrupt capabilities: MSI list/control/address/data/mask/pending fields plus MSI-X list/message-control/table/PBA fields.
- Extended capability list headers: vendor-specific, virtual channel, advanced error reporting, BAR enhancement, power budget, dynamic power allocation, secondary PCIe, ACS, PASID, LTR, ARI, data-link feature, 16 GT PHY, margining, and RTR.
- Error-reporting diagnostics: uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- Resizable/enhanced BAR data: BAR1-BAR6 capability and control fields with supported-size, active size, BAR index, total BAR count, and upper supported-size bits.
- Power and arbitration capability fields: virtual-channel resource capability/control/status, power budget data selection/data/capability, DPA capability/status/control, and eight DPA substate power allocation fields.
- Isolation and address-space features: ACS capability/control, PASID capability/control, LTR max snoop/no-snoop latency, ARI capability/control, and data-link feature capability/status.
- High-speed link diagnostics: 16 GT link capability/control/status, local and RTM parity mismatch status, per-lane 16 GT equalization presets for lanes 0-15, and per-lane PCIe margining control/status fields for lanes 0-15.
- RTR data fields: two registers with buffer size, memory-map aperture size, routing ID, and offset fields.

`BIF_CFG_DEV0_EPF4_*` begins a separate endpoint function block for device 0, function 4. In this chunk it includes the early PCI configuration header, PCIe capability/control/status fields, MSI/MSI-X, SATA capability fields, vendor-specific fields, advanced error reporting, TLP header/prefix logs, and the start of the enhanced BAR capability/control sequence through `PCIE_BAR5_CNTL`. This block mirrors much of the DEV2 EPF0 layout but is scoped to a different BIF configuration decoder address block.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The externally consumed API is the macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for that field.
- Register names intentionally match the offset-header names without the `reg` prefix and instance suffix, so code can combine `regBIF_CFG_DEV2_EPF0_0_*` or `regBIF_CFG_DEV0_EPF4_0_*` offsets with the matching field masks.

The macros are suitable for AMDGPU helper patterns such as:

- `REG_GET_FIELD(value, BIF_CFG_DEV2_EPF0_DEVICE_STATUS, FATAL_ERR)`
- `REG_SET_FIELD(value, BIF_CFG_DEV2_EPF0_DEVICE_CNTL, MAX_PAYLOAD_SIZE, size)`
- manual extraction with `(value & MASK) >> SHIFT` when helper macros are not used.

## Control Flow

The chunk has no control flow. Its effect occurs at compile time when included by NBIO or PCIe-related AMDGPU source files. At runtime, driver control flow comes from the consumers: they read a 16-bit or 32-bit register, use these masks/shifts to isolate or update a field, and write the resulting value back through MMIO or indexed PCIe-port access.

The field ordering follows PCI/PCIe capability layout rather than driver execution order. Capability list fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`) define the linked-list structure of extended capabilities. Status/control pairs model hardware state machines where software writes control bits and polls or handles status bits, but the state transitions themselves are implemented by hardware.

## State And Persistence Behavior

These macros do not allocate, store, or persist software state. They describe persistent hardware register state:

- Configuration identity and resource registers such as BARs, subsystem IDs, class codes, and ROM base address can reflect hardware straps, firmware programming, or OS PCI resource assignment.
- Capability/control registers can be changed by kernel PCI core, platform firmware, or the AMDGPU driver depending on ownership and access path.
- Status registers such as PCIe error status, link status, parity mismatch status, lane margining status, and DPA status expose hardware state and often include write-one-to-clear or hardware-updated semantics governed by the PCIe specification and AMD hardware behavior.
- Log registers such as AER TLP header and prefix logs preserve diagnostic information until hardware or software clears the associated error state.

Because the macros are pure definitions, persistence risks come from consumers writing incorrect fields or using masks against the wrong register instance, not from this header itself.

## Dependencies And Integration Points

The direct dependency is the generated AMD register-header ecosystem:

- `nbio_7_11_0_offset.h` supplies the register offsets and base indices for the same blocks, including `regBIF_CFG_DEV2_EPF0_0_*` and `regBIF_CFG_DEV0_EPF4_0_*`.
- `amdgpu/nbio_v7_11.c` includes both the offset and shift/mask headers for NBIO 7.11.0 register programming.
- AMDGPU register helpers in the wider driver use the mask names to implement read/modify/write operations and field extraction.

The hardware integration points are PCIe endpoint configuration spaces exposed through NBIO/BIF decoders. Important subsystem touch points include PCI resource enumeration, link-speed and link-training reporting, AER handling, MSI/MSI-X programming, power management, resizable BAR programming, ACS/PASID/ARI features used by virtualization and IOMMU flows, and physical link diagnostics such as 16 GT equalization and lane margining.

## Risks And Edge Cases

The main risk is register-contract drift. If a mask or shift is wrong, the driver can silently read the wrong bit or write a neighboring field. In this chunk that risk is concentrated around:

- Dense control/status registers such as `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, ACS/PASID/ARI control, and DPA control/status where adjacent bits have different side effects.
- AER status/mask/severity definitions, where confusing status bits with mask bits can hide errors, misclassify severity, or clear/report the wrong condition.
- Repeated per-lane definitions for lanes 0-15, where copy-generation mistakes can swap lane numbers or reuse the wrong field prefix.
- Repeated enhanced BAR capability/control fields across BAR1-BAR6 and across DEV2 EPF0 versus DEV0 EPF4, where one prefix mismatch can target the wrong endpoint function.
- Capability-list `NEXT_PTR` fields, where a wrong mask width or shift can break software traversal of extended capabilities.
- Mixed 16-bit and 32-bit register layouts. Many masks are 16-bit-looking values, while others cover full 32-bit fields; consumers must use the correct access width and register address.

This chunk also ends in the middle of the `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` definition group, so any per-file summary must reconcile this with the following chunk before claiming complete DEV0 EPF4 BAR coverage.

## Test Signals

There are no unit tests tied directly to generated mask headers. Useful validation signals are mostly integration and hardware-facing:

- The kernel must compile with `nbio_v7_11.c` and other AMDGPU consumers including `nbio_7_11_0_sh_mask.h`.
- PCIe enumeration should expose sane BARs, MSI/MSI-X capabilities, power-management capabilities, and extended capability lists for NBIO 7.11.0 devices.
- AMDGPU bring-up should successfully program NBIO doorbells, interrupt paths, HDP flush registers, PCIe-port indexed registers, and any features that share the same generated register-header style.
- Runtime diagnostics should show plausible PCIe link width/speed/status, AER status, and capability data through kernel logs, debugfs, lspci, or driver-specific dumps.
- Error-injection or platform validation that exercises AER, FLR, resizable BAR, ACS/PASID/ARI, link retraining, 16 GT equalization, and lane margining would catch many mask/shift mistakes in this chunk.

## Chunk Boundary Notes

The assigned range is lines 9838-12285 only. It begins after earlier DEV2 EPF0 identity fields and ends before the rest of DEV0 EPF4 BAR5 control and later DEV0 EPF4 capability definitions. The final source-file research document should merge this chunk with adjacent chunks to avoid treating either boundary as a semantic start or end of the hardware block.
