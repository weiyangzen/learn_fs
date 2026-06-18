# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 9822-12317

## Scope

This chunk is a generated AMDGPU NBIO 7.2 shift/mask header segment for PCI/PCIe configuration-space fields in `BIF_CFG_DEV0` endpoint-function blocks. It contains 2,122 `#define` field-layout macros across 368 register comments in the 2,496-line range. There are no C functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms here.

The range starts mid-register in `BIF_CFG_DEV0_EPF3_LINK_CNTL`, after the shift definitions and after the first link-control masks, then covers the rest of the `EPF3` PCIe capability and extended-capability tail. It then covers the complete `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` address block, from standard PCI identity registers through the TPH requester steering-tag table. The range finally enters `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` and stops after `BIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL`; the following `EPF5` USB/PCIe capability fields are outside this chunk.

Although the repository path is under a `ceph-client` source tree, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.2 register interface. Each public macro follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK` gives the encoded mask in the raw register value.

This chunk describes the PCI/PCIe configuration-space layout for secondary endpoint functions on NBIF device 0. Driver code can pair these macros with addresses from `nbio_7_2_0_offset.h` to decode or compose register values for endpoint identity, command/status enables, BAR apertures, capability-list traversal, power management, PCIe link/device controls, MSI/MSI-X routing, Advanced Error Reporting, BAR enhanced capability controls, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and TPH requester state.

The macros intentionally describe only field geometry. They do not provide register addresses, reset values, access permissions, legal value combinations, write-one-to-clear behavior, or sequencing rules.

## Important Macro Families

The `EPF3` tail covers PCIe capability and extended-capability fields after the earlier part of `LINK_CNTL`:

- `BIF_CFG_DEV0_EPF3_LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` define link-speed/width status, link-training and data-link-active bits, completion-timeout support/control, ARI/AtomicOp/IDO/LTR/OBFF/10-bit-tag/TLP-prefix controls, supported link speeds, compliance/de-emphasis settings, equalization phase status, crosslink state, downstream-component presence, and DRS message status.
- MSI and MSI-X groups define capability-list headers, message-control bits, 32-bit and 64-bit message address/data fields, per-vector mask and pending arrays, MSI-X table and pending-bit-array BIR/offset fields, function mask, and enable bits.
- Vendor-specific and AER groups define enhanced-capability headers, vendor-specific payload dwords, uncorrectable error status/mask/severity, correctable error status/mask, ECRC/multiple-header controls, header logs, and TLP prefix logs.
- BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and TPH requester groups expose BAR size support/control, power-budget data select/data/capability, DPA substate allocation and status/control fields, ACS capability/control, PASID capability/control, ARI next-function/group controls, TPH requester capability/control, and 64 two-entry steering-tag table registers.

The `EPF4` block is complete in this chunk and repeats a full type-0 endpoint configuration layout:

- Standard PCI config fields: vendor/device IDs, command/status, revision and class-code bytes, cache-line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and adapter write field.
- Power-management fields: PM capability list, PM capability, PM status/control, PME support/status, data-select/scale, D-state selection, no-soft-reset, B2/B3 support, and bus-power enable.
- USB-adjacent capability bytes before the PCIe block: `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe capability fields: capability header, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Interrupt and extended-capability fields: MSI, MSI-X, vendor-specific capability, AER, header/TLP-prefix logs, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and TPH requester capability/control plus steering-tag table entries 0 through 63.

The `EPF5` prefix begins the next endpoint-function block:

- It covers standard identity and header fields through BARs, adapter IDs, ROM base, capability pointer, interrupt fields, and vendor capability.
- It includes PM capability list, PM capability, and `PMI_STATUS_CNTL` fields for D-state, PME enable/status, power data select/scale/data, no-soft-reset, B2/B3 support, and bus-power enable.
- The chunk ends before `EPF5_SBRN`, `EPF5_FLADJ`, `EPF5_DBESL_DBESLD`, and the rest of the `EPF5` PCIe capability block.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. Constants are untyped integer literals, usually with an `L` suffix for masks, and encode the low-level layout of 8-bit, 16-bit, and 32-bit PCI/NBIO register fields.

Consumers must combine these field constants with the sibling generated offset header, for example `cfgBIF_CFG_DEV0_EPF3_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF4_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF4_PCIE_TPH_ST_TABLE_63`, and `cfgBIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL` in `nbio_7_2_0_offset.h`, and with AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or PCIe-port/config accessors appropriate to the target register. This header alone cannot identify where a register lives or how it should be accessed safely.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_2_0_sh_mask.h`.
2. Driver code selects a matching address macro from `nbio_7_2_0_offset.h` or another generated NBIO address source.
3. The code reads a PCI/NBIO config register, extracts fields using `*_MASK` and `*__SHIFT`, or composes a new value while preserving unrelated bits.
4. Hardware, firmware, or PCI core behavior interprets the resulting config-space state.

The field names imply external hardware flows outside this header: PCIe link training and equalization, completion timeout behavior, interrupt routing through MSI/MSI-X, power-management state transitions, Dynamic Power Allocation substate selection, Advanced Error Reporting logging and clearing, ACS/PASID/ARI routing and isolation, BAR sizing/enabling, TPH requester steering-tag selection, and vendor-specific capability handling.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO 7.2 PCI/PCIe configuration registers. Persistence depends on GPU reset domains, PCI function reset, bus reset, FLR, suspend/resume restore, firmware/BIOS initialization, and explicit driver or PCI core writes.

Represented state includes endpoint identity and BAR apertures, command/status enables, interrupt configuration, power-management state, PCIe device/link capabilities and controls, MSI/MSI-X mask and pending arrays, AER status/mask/severity/log registers, BAR size negotiation controls, DPA and power-budget values, ACS/PASID/ARI enablement, TPH requester controls and steering-tag table entries, and vendor-specific metadata. Some fields are capability or status readbacks; others are writable controls whose persistence and side effects are defined by the PCIe specification and AMD hardware documentation, not by these macros.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2 register database and must remain synchronized with companion headers:

- `nbio_7_2_0_offset.h` supplies matching configuration-space offsets, including `cfgBIF_CFG_DEV0_EPF3_LINK_STATUS`, `cfgBIF_CFG_DEV0_EPF4_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF4_PCIE_TPH_ST_TABLE_63`, and `cfgBIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL`.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` and is the direct AMDGPU NBIO 7.2 integration point in this source tree.
- AMDGPU register helper macros and accessors supply the actual read/modify/write behavior. The shift/mask macros are meaningful only when used with the correct register width and access path.

Semantic dependencies are the PCI and PCI Express specifications for endpoint configuration headers, power-management capabilities, PCIe capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, BAR enhanced capability, power budgeting, DPA, TPH requester steering tags, and vendor-specific enhanced capabilities. The generated names mirror those architectural fields but do not enforce valid values or ordering.

## Risks And Edge Cases

- The chunk begins mid-register. Whole-file reconciliation must include the previous chunk before treating `BIF_CFG_DEV0_EPF3_LINK_CNTL` as complete.
- The chunk ends at `BIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL`; the rest of `EPF5` belongs to the next chunk.
- Generated shift/mask drift can compile cleanly while causing code to read or write the wrong PCIe config bit. The failure mode may appear as bad BAR sizing, broken interrupt delivery, incorrect power management, link instability, missing TPH steering behavior, or silent loss of error reporting.
- Status fields in PCIe/AER/MSI/MSI-X capability space can have side effects or write-one-to-clear semantics. A mask definition does not imply read-modify-write is safe.
- ACS, PASID, and ARI controls affect isolation, address translation, function routing, and peer-to-peer behavior. Incorrect field programming can become a security or DMA-isolation issue, not just a device-local bug.
- AER mask/severity/status fields are highly repetitive and easy to miscompare in review. Misaligned masks can hide uncorrectable errors, escalate benign correctable errors, or log the wrong TLP/header data.
- BAR enhanced capability fields are repeated across BAR1-BAR6 and endpoint functions. Generation or copy drift can break only one BAR or one endpoint function, which makes runtime symptoms hardware-configuration dependent.
- TPH steering-tag tables contain many mechanically repeated lower/upper-entry fields. Off-by-one table addressing can route hints to the wrong traffic class or requester context while leaving adjacent macros apparently valid.
- Full-width masks such as `0xFFFFFFFFL` rely on existing AMDGPU helper types. New code should avoid ad hoc signed arithmetic or truncation-prone casts around these constants.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled so include users such as `amdgpu/nbio_v7_2.c` catch missing or renamed macros.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should align with their shifts, repeated EPF3/EPF4/EPF5 register families should match except where the hardware intentionally differs, and reserved fields should not overlap named fields.
- Cross-check this chunk against `nbio_7_2_0_offset.h` so each covered register has a matching `cfg...` offset.
- On NBIO 7.2 hardware, compare decoded endpoint config space with `lspci -vvxxx`, PCI core dumps, or AMDGPU debug register reads for vendor/device IDs, BARs, PM state, link capabilities/status, MSI/MSI-X state, AER masks/status/logs, ACS/PASID/ARI state, TPH requester controls/tables, DPA, and power-budget fields.
- Exercise suspend/resume, FLR or GPU reset, PCIe retraining, MSI/MSI-X enable/disable, and error-reporting paths to confirm that callers preserve reserved bits and restore expected config state.
- For AER-facing changes, inject or observe correctable and uncorrectable PCIe errors and verify that status, masks, severity, header logs, and TLP prefix logs decode to the intended bits.
