# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 58625-61073

## Purpose

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment for BIF PCIe configuration decode registers. It contains no executable code. Its purpose is to publish C preprocessor constants that describe bit positions and already-shifted masks for PCI/PCIe endpoint-function configuration-space fields.

The range starts in the tail of `BIF_CFG_DEV1_EPF0_0`, covering the end of lane-margining definitions for lanes 14 and 15. It then covers the full `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` address block, from conventional PCI identity fields through PCIe, MSI/MSI-X, AER, BAR, power-budget, DPA, ACS, PASID, and ARI fields. The chunk ends inside `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, after full coverage of most `DEV2_EPF0_0` endpoint capabilities and in the middle of the PCIe lane-margining lane 4 control fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It has no Ceph or distributed-filesystem behavior.

## Public Surface

The public surface in this line range is 2,130 `#define` macros across 313 register-comment groups. Each hardware field follows the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already positioned in the register.

Macro prefixes in this chunk are:

- `BIF_CFG_DEV1_EPF0_0_*`: 17 macros for the tail of lane 14 status and lane 15 lane-margining control/status fields. The corresponding block begins in a previous chunk.
- `BIF_CFG_DEV1_EPF1_0_*`: 854 macros covering a complete endpoint-function field map.
- `BIF_CFG_DEV2_EPF0_0_*`: 1,259 macros covering a large endpoint-function field map that continues in the next chunk.

There are no functions, structs, enums, inline helpers, storage objects, locks, or allocation paths. The API contract is the exact macro spelling and bit geometry. Consumers are expected to pair these field definitions with register addresses from `nbio_7_7_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe config/index accessors.

## Register Coverage

The `DEV1_EPF1_0` block describes a complete PCI endpoint-function configuration layout. It includes conventional PCI header fields such as vendor/device ID, command/status, revision/class code bytes, cache-line/latency/header/BIST fields, six BARs, subsystem vendor/device IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability metadata.

The same block then describes power-management and PCIe capability fields: PM capability/status/control bits, SBRN/FLADJ/DBESL fields, PCIe capability header and device/link capability/control/status registers, device/link capability 2 and control/status 2 fields, MSI and MSI-X capability fields, vendor-specific extended capability headers, AER status/mask/severity/log fields, resizable/enhanced BAR capability and control fields for BAR1 through BAR6, power-budget fields, Dynamic Power Allocation fields, ACS capability/control fields, PASID capability/control fields, and ARI capability/control fields.

The `DEV2_EPF0_0` block repeats the endpoint-function shape with additional high-speed/link features in this chunk. It covers conventional PCI and PM/PCIe/MSI/MSI-X fields, vendor-specific capability fields, virtual-channel resources, AER, enhanced BARs, power budget, DPA, secondary PCIe capability and per-lane 8 GT/s equalization controls for lanes 0-15, ACS, PASID, LTR, ARI, data-link feature exchange, 16 GT/s PHY capability/control/status, local and retimer parity mismatch status, 16 GT/s per-lane equalization controls for lanes 0-15, PCIe lane margining enhanced capability, margining port capability/status, and lane-margining controls/statuses from lane 0 through part of lane 4.

The leading `DEV1_EPF0_0` tail and trailing `DEV2_EPF0_0` tail are incomplete within this chunk. The final per-file report should merge adjacent chunks before making whole-block claims about all margining lanes.

## Important Field Families

The conventional PCI fields define packed byte/word fields inside config-space dwords: command bits for I/O, memory, bus mastering, parity, SERR, and interrupt disable; status bits for capability-list presence and error reporting; class-code and revision fields; BAR address masks; subsystem IDs; ROM base; and interrupt routing bytes.

The PCIe capability fields define device/link behavior: max payload and read request sizes, relaxed ordering, extended tags, no-snoop, FLR initiation/capability, completion timeout, ARI/atomic/LTR/OBFF/ten-bit-tag capabilities, link speed/width, ASPM, retraining, common clock, bandwidth notification, equalization status, and 8 GT/s link equalization state.

The MSI/MSI-X fields define interrupt capability metadata and programming fields: capability IDs and next pointers, MSI enable and multi-message control, 32-bit and 64-bit message address/data variants, per-vector masking and pending bits, MSI-X table/PBA BIR and offsets, function mask, and table size. Several MSI fields intentionally overlap depending on whether the capability is configured in 32-bit or 64-bit mode.

The AER fields expose correctable/uncorrectable error status, masks, severity controls, ECRC capability/enables, first-error pointer, multiple-header logging, TLP prefix log presence, header logs, and TLP prefix logs. These fields are diagnostics and policy surfaces, and status bits may have PCIe-defined clear semantics.

The enhanced BAR fields expose resizable/enhanced BAR capability and control geometry for BAR1 through BAR6. The important fields are supported BAR sizes, current BAR size, BAR index, total BAR count, and upper supported-size bits.

The power and policy fields include PM state/PME controls, power-budget data selection and reporting, DPA latency/status/control and per-substate power allocation, LTR latency fields, and data-link feature exchange bits.

The isolation and function-routing fields include ACS source validation, translation blocking, peer-to-peer redirect/egress controls, direct translated peer-to-peer support, PASID support/enable bits, and ARI function-group/next-function fields. These are important for IOMMU, multifunction, and virtualized configurations.

The link-training and lane diagnostics fields include secondary PCIe link control 3, per-lane 8 GT/s equalization controls, 16 GT/s link status and parity mismatch fields, per-lane 16 GT/s downstream/upstream TX presets, and PCIe lane-margining control/status fields. Lane-margining registers use a repeated four-field shape: receiver number, margin type, usage model, and margin payload or payload status.

## Control Flow and Data Flow

This header has no runtime control flow. Runtime behavior is imposed by code that includes this generated header:

1. NBIO 7.7 code includes `nbio_7_7_0_offset.h` for register addresses and `nbio_7_7_0_sh_mask.h` for field geometry.
2. A caller reads a PCIe config or NBIO register through an AMDGPU access helper.
3. The caller extracts fields by applying the generated `_MASK` and `__SHIFT` constants directly or through `REG_GET_FIELD`.
4. For writes, the caller uses read/modify/write logic, commonly through `REG_SET_FIELD`, to alter one field while preserving unrelated bits.
5. Hardware, firmware, PCI core code, and AMDGPU NBIO logic define ordering, polling, reset, and error-handling behavior outside this generated file.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` directly includes this header and is the ASIC-specific NBIO 7.7 integration point. That file uses generated masks for NBIO bring-up, revision extraction, doorbell setup, interrupt control, HDP flush/remap handling, clock/power controls, and PCIe/indexed register access. The fields in this chunk are mostly endpoint PCIe capability metadata, so they are more likely to be consumed by generic PCIe/NBIO paths, diagnostics, firmware-coordinated flows, or future ASIC-specific code than by a dense local call graph in this line range.

## State and Persistence Behavior

The macros themselves hold no state and persist nothing. They describe externally persisted hardware state in PCI/PCIe configuration registers exposed through NBIO BIF decode blocks.

The underlying state includes device identity, BAR aperture configuration, command/status bits, interrupt programming, power-management state, PCIe device/link capabilities and controls, error status and logs, virtual-channel resources, BAR sizing capabilities, power-budget and DPA data, ACS/PASID/ARI/LTR policy, data-link feature state, equalization state, 16 GT/s PHY status, parity mismatch diagnostics, and lane-margining requests/results.

Persistence is hardware-defined. Some fields are firmware or strap initialized, some are configured by the OS PCI core, some are updated by hardware link training or error reporting, and some are writable controls that persist until FLR, link reset, GPU reset, suspend/resume, power transition, or driver reinitialization. Status and log fields may be sticky or write-one-to-clear according to PCIe and AMD hardware semantics, not according to this header.

## Dependencies and Integration Points

The direct sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies the register offsets for these field definitions. The names must stay synchronized: using a `BIF_CFG_DEV1_EPF1_0_*` mask with a `BIF_CFG_DEV2_EPF0_0_*` address can compile cleanly while targeting the wrong endpoint function.

The direct AMDGPU integration file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header and exposes the `nbio_v7_7_funcs` backend selected by ASIC discovery. Broader consumers are the AMDGPU register helper macros and any PCIe, interrupt, reset, RAS, power-management, virtualization, or diagnostics code that accesses NBIO 7.7 BIF configuration registers.

Semantic dependencies include the PCI and PCI Express specifications, MSI/MSI-X, Advanced Error Reporting, virtual channels, ACS, PASID, ARI, LTR, data-link feature exchange, Dynamic Power Allocation, enhanced/resizable BAR semantics, 8 GT/s and 16 GT/s equalization, lane margining, and AMD's NBIO 7.7.0 register database. The header does not encode reset values, access permissions, ownership rules, required sequencing, firmware arbitration, or whether every field is implemented on every NBIO 7.7 ASIC.

## Risks and Maintenance Notes

- This chunk starts and ends mid-block. `DEV1_EPF0_0` lane-margining coverage begins earlier, and `DEV2_EPF0_0` margining lanes continue later.
- Prefix drift is the main generated-header risk. `DEV1_EPF1_0` and `DEV2_EPF0_0` contain many similarly named fields; a wrong prefix can compile while reading or writing a different PCI function.
- Mask/offset mismatches are silent at compile time when both symbols exist. The offset and shift/mask headers must be regenerated or validated together.
- Packed PCI config fields intentionally share dwords. Consumers must preserve unrelated bits and avoid assuming a field macro names a standalone register.
- MSI/MSI-X fields are interrupt-delivery sensitive. Incorrect message address/data, mask, pending, table, PBA, or enable handling can cause missed interrupts or interrupt storms.
- AER status/mask/severity and log fields can hide, misclassify, or clear PCIe errors if handled with the wrong mask or clear semantics.
- ACS, PASID, ARI, LTR, and virtual-channel controls affect routing, isolation, IOMMU policy, and latency behavior. These should be changed only through code paths that understand platform and virtualization ownership.
- BAR and enhanced BAR fields affect aperture sizing and resource assignment. Wrong sizing can break enumeration, MMIO visibility, VF/PF assumptions, or firmware expectations.
- Link equalization, 16 GT/s, data-link feature, and lane-margining fields can affect negotiated speed, link stability, and diagnostics. Writes during active traffic, reset, or power transition can create hard-to-reproduce link failures.
- Generated masks must preserve reserved bits. Hand edits are high risk because repeated lane and capability blocks make one-bit or one-lane mistakes easy to miss in review.

## Test Signals

Useful validation signals for this chunk are:

- Build AMDGPU with NBIO 7.7 support enabled; missing or renamed generated macros should fail in include sites such as `nbio_v7_7.c`.
- Static consistency checks that each field has both `__SHIFT` and `_MASK`, that masks align with shifts, and that masks do not overlap unexpectedly within a register.
- Cross-header checks that every register field in this chunk maps to a corresponding register address in `nbio_7_7_0_offset.h` and that prefixes match exactly.
- Generated-header diff checks against AMD's authoritative NBIO 7.7.0 register database, especially for the repeated `DEV1_EPF1_0` and `DEV2_EPF0_0` endpoint blocks.
- PCI config-space dumps on NBIO 7.7 hardware compared against expected field extraction for vendor/device IDs, command/status, BARs, capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, and LTR.
- Runtime bring-up, reset, suspend/resume, and FLR testing with `amdgpu` loaded, watching for changed PCIe link speed/width, AER noise, failed interrupts, or BAR/resource enumeration regressions.
- MSI/MSI-X validation through graphics, SDMA, compute/KFD, and interrupt-heavy workloads.
- PCIe error and diagnostics testing for AER logs, correctable/uncorrectable error masks, ECRC bits, header/TLP prefix logs, and link retraining/equalization status.
- Virtualization and IOMMU-oriented tests for ACS/PASID/ARI behavior, including reset and teardown paths.
- Lane diagnostics for 8 GT/s and 16 GT/s equalization, parity mismatch status, and PCIe lane-margining control/status payloads across all lanes once adjacent chunks are merged.
