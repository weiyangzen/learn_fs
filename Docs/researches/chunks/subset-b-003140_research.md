# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 44285-46731

## Scope

This chunk is a generated AMDGPU NBIO 7.11 shift/mask header segment for PCI/PCIe configuration-space fields in the `BIF_CFG_DEV2` endpoint-function blocks. It contains 2,134 `#define` field-layout macros and 309 register/address-block comments. There are no functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms in this range.

The range starts inside `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, after the first two shift definitions for completion-timeout fields, covers the rest of endpoint function 1's PCIe capability and extended-capability tail, covers the complete `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` address block, and then enters `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp` through the first two `BIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL` shifts. Adjacent chunks are needed for the complete `EPF1_0_DEVICE_CNTL2` and `EPF3_0_PCIE_BAR5_CNTL` register definitions.

Although this repository mirror is under a `ceph-client` source tree, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.11 register interface. Each public macro follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK` gives the encoded mask in the raw register value.

This chunk describes PCI/PCIe configuration-space layout for secondary functions of NBIF device 2. The covered fields let AMDGPU code decode and compose endpoint PCI config registers for identity, command/status, BAR windows, capability lists, power management, PCIe link/device controls, MSI/MSI-X routing, SATA capability metadata, vendor-specific capabilities, Advanced Error Reporting, BAR enhanced capability controls, power-budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and RTR metadata.

The macros intentionally describe only field geometry. They do not provide register addresses, reset values, access permissions, legal value combinations, write-one-to-clear behavior, or sequencing rules.

## Important Macro Families

The endpoint-function 1 tail covers PCIe capability and extended-capability fields after `DEVICE_CAP2`:

- `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` define completion-timeout control, ARI/AtomicOp/IDO/LTR/OBFF/10-bit-tag/TLP-prefix controls, supported link speeds, compliance/de-emphasis settings, equalization-complete phase bits, crosslink state, downstream-component presence, and DRS message status.
- MSI and MSI-X groups define capability-list headers, message-control bits, 32-bit and 64-bit message address/data fields, per-vector mask and pending bit arrays, MSI-X table/PBA BIR and offsets, function mask, and enable bits.
- SATA capability and IDP groups expose SATA capability revision, BAR location/offset, indexed-data-port index, and data fields.
- Vendor-specific and AER groups define enhanced-capability headers, vendor-specific payload dwords, uncorrectable error status/mask/severity, correctable error status/mask, ECRC/multiple-header controls, header logs, and TLP prefix logs.
- BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR groups expose BAR size support/control, power-budget data select/data/capability, DPA substate power allocation and status/control fields, ACS capability/control, PASID capability/control, ARI next-function/group controls, and routing-data payload fields.

The endpoint-function 2 block is complete in this chunk and repeats a full type-0 endpoint configuration layout:

- Standard PCI config fields: vendor/device IDs, command/status, revision and class-code bytes, cache-line/latency/header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and adapter write field.
- Power-management fields: PM capability list, PM capability, status/control, PME support/status, data-select/scale, D-state, no-soft-reset, and B2/B3 support.
- PCIe capability fields: capability header, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Interrupt fields: MSI and MSI-X capability, address/data/mask/pending/table/PBA fields.
- Extended-capability fields: SATA capability, vendor-specific capability, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR.

The endpoint-function 3 prefix begins the same generated pattern as endpoint-function 2:

- It covers standard identity, command/status, class/header/BAR, adapter/ROM/capability/interrupt fields.
- It includes PM capability/status, plus USB-oriented `SBRN`, `FLADJ`, and `DBESL_DBESLD` registers before the PCIe capability block.
- It then covers PCIe device/link capability and control, MSI/MSI-X, SATA, vendor-specific, AER, header/TLP-prefix logs, BAR enhanced capability headers, BAR1-BAR5 capability/control groups, and stops after the first two `PCIE_BAR5_CNTL` shift definitions.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. Constants are untyped integer literals, usually with an `L` suffix for masks, and encode the low-level layout of 8-bit, 16-bit, and 32-bit PCI/NBIO register fields.

Consumers must combine these field constants with the sibling generated offset header, for example `regBIF_CFG_DEV2_EPF2_0_VENDOR_ID` in `nbio_7_11_0_offset.h`, and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or PCI/NBIO accessors appropriate to the target register. This header alone cannot identify where a register lives or how it should be accessed safely.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_11_0_sh_mask.h`.
2. Driver code selects a matching address macro from `nbio_7_11_0_offset.h` or another generated NBIO address source.
3. The code reads a PCI/NBIO config register, extracts fields using `*_MASK` and `*__SHIFT`, or composes a new value while preserving unrelated bits.
4. Hardware, firmware, or PCI core behavior interprets the resulting config-space state.

The field names imply external hardware flows outside this header: PCIe link training and equalization, completion timeout behavior, MSI/MSI-X interrupt routing, power-management state transitions, Dynamic Power Allocation substate selection, AER logging and clearing, ACS/PASID/ARI routing and isolation, BAR sizing/enabling, and error-report containment/reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO 7.11 PCI/PCIe configuration registers. Persistence depends on GPU reset domains, PCI function reset, bus reset, FLR, suspend/resume restore, firmware/BIOS initialization, and explicit driver or PCI core writes.

Represented state includes endpoint identity and BAR apertures, command/status enables, interrupt configuration, power-management state, PCIe device/link capabilities and controls, MSI/MSI-X mask and pending arrays, AER status/mask/severity/log registers, BAR size negotiation controls, DPA and power-budget values, ACS/PASID/ARI enablement, and routing/vendor-specific metadata. Some fields are capability or status readbacks; others are writable controls whose persistence and side effects are defined by the PCIe specification and AMD hardware documentation, not by these macros.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11 register database and must remain synchronized with companion headers:

- `nbio_7_11_0_offset.h` supplies matching register addresses and base indices, including `regBIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, `regBIF_CFG_DEV2_EPF2_0_VENDOR_ID`, and `regBIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL`.
- Other generated NBIO 7.11 headers in the same directory provide related address/default metadata where present.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both the offset and shift/mask headers and is the direct AMDGPU NBIO 7.11 integration point. Display resource files include the offset header for DCN 3.5/3.5.1 address integration.

Semantic dependencies are the PCI and PCI Express specifications for endpoint configuration headers, PM capabilities, PCIe capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, BAR enhanced capability, power budgeting, DPA, and vendor-specific enhanced capabilities. The generated names mirror those architectural fields but do not enforce valid values or ordering.

## Risks And Edge Cases

- The chunk begins and ends mid-register. Whole-file reconciliation must include adjacent chunks before treating `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2` or `BIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL` as complete.
- Generated shift/mask drift can compile cleanly while causing code to read or write the wrong PCIe config bit. The failure mode may surface as bad BAR sizing, broken interrupt delivery, incorrect power management, link instability, or silent loss of error reporting.
- Status fields in PCIe/AER/MSI/MSI-X capability space can have side effects or write-one-to-clear semantics. A mask definition does not imply read-modify-write is safe.
- ACS, PASID, and ARI controls affect isolation, address translation, function routing, and peer-to-peer behavior. Incorrect field programming can become a security or DMA-isolation issue, not just a device-local bug.
- AER mask/severity/status fields are highly repetitive and easy to miscompare in review. Misaligned masks can hide uncorrectable errors, escalate benign correctable errors, or log the wrong TLP/header data.
- BAR enhanced capability fields are repeated across BAR1-BAR6 and endpoint functions. Generation or copy drift can break only one BAR or one endpoint function, which makes runtime symptoms hardware-configuration dependent.
- Power-budget and DPA fields influence power/performance state choices. Bad values can cause incorrect power accounting, latency reporting, or substate allocation.
- Full-width masks such as `0xFFFFFFFFL` rely on existing AMDGPU helper types. New code should avoid ad hoc signed arithmetic or truncation-prone casts around these constants.

## Test Signals

- Build AMDGPU with NBIO 7.11 support enabled so include users such as `amdgpu/nbio_v7_11.c` catch missing or renamed macros.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should align with their shifts, repeated EPF2/EPF3 register families should match except where the hardware intentionally differs, and reserved fields should not overlap named fields.
- Cross-check this chunk against `nbio_7_11_0_offset.h` so each covered register has a matching `reg...` address and `_BASE_IDX`.
- On NBIO 7.11 hardware, compare decoded endpoint config space with `lspci -vvxxx`, PCI core dumps, or AMDGPU debug register reads for vendor/device IDs, BARs, PM state, link capabilities/status, MSI/MSI-X state, AER masks/status/logs, ACS/PASID/ARI state, DPA, and power-budget fields.
- Exercise suspend/resume, FLR or GPU reset, PCIe retraining, MSI/MSI-X enable/disable, and error-reporting paths to confirm that callers preserve reserved bits and restore expected config state.
- For AER-facing changes, inject or observe correctable and uncorrectable PCIe errors and verify that status, masks, severity, header logs, and TLP prefix logs decode to the intended bits.
