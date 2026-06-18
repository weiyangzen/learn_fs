# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 39387-41833

## Scope

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It contains 2,136 `#define` macros: 1,069 `__SHIFT` constants and 1,067 `_MASK` constants, plus 307 register/address-block comments. There are no executable statements, functions, structs, enums, storage objects, locks, allocations, or persistence logic in this range.

The range starts at the tail of the `BIF_CFG_DEV1_EPF0_0` PCIe lane-margining and Readiness Time Reporting area, covers the complete `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` endpoint/function configuration block, and then enters the `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` root-complex configuration block through the start of the PCIe 16GT per-lane equalization registers. The source mirror is under `sources/distributed-fs/ceph-client`, but this file is AMDGPU hardware metadata and has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` provides the bitfield-layout side of the generated NBIO 7.11.0 register interface. Each field is exported as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the already shifted mask for isolating or preserving that field.

This chunk describes PCI/PCIe configuration-space fields for an NBIF endpoint function (`DEV1_EPF1`) and for a root-complex/root-port instance (`DEV2_RC0`). Consumers combine these field-layout constants with sibling generated address/default metadata and AMDGPU register helpers to read, modify, or report PCIe capability, link, interrupt, power-management, virtualization, error-reporting, and lane-equalization state without hard-coding bit positions.

## Important Macro Families

The opening lines complete previous `DEV1_EPF0` lane and timing definitions:

- `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_STATUS` and lane 15 margining control/status fields expose receiver number, margin type, usage model, and payload/status payload for PCIe lane margining.
- `BIF_CFG_DEV1_EPF0_0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` describe PCIe Readiness Time Reporting capability metadata and reset/data-link-up/FLR/D3hot-to-D0 timing fields.

The main `BIF_CFG_DEV1_EPF1_0` endpoint/function block is a large generated PCIe endpoint configuration layout. It includes:

- Conventional PCI header fields: vendor/device ID, command/status, revision/class/programming interface, cache-line and latency timers, header type, BIST, BAR1-BAR6, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability headers.
- Power-management and PCIe capability fields: PM capability/status/control, SBRN/FLADJ/DBESL, PCIe capability type and interrupt message number, device capability/control/status, link capability/control/status, and second-generation device/link capability/control/status registers.
- MSI and MSI-X fields: MSI capability list, message control, 32-bit and 64-bit message address/data fields, mask and pending dwords, MSI-X message control, table, and PBA descriptors.
- SATA and vendor-specific capability fields: SATA capability words, IDP index/data, PCIe vendor-specific enhanced capability header, and vendor-specific data dwords.
- Advanced Error Reporting fields: enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- Endpoint BAR enhanced capabilities: BAR1-BAR6 capability and control fields for supported BAR size and BAR size selection.
- Power budgeting and Dynamic Power Allocation fields: power budget selector/data/capability, DPA capability/status/control, latency indicator, and substate power-allocation entries 0-7.
- Isolation and virtualization fields: ACS capability/control, PASID capability/control, ARI capability/control, SR-IOV capability/control/status/VF counts/VF BARs/page sizes/device ID/stride/offset, and VF resizable BAR capability/control fields.
- Readiness Time Reporting fields for the endpoint function.

The `BIF_CFG_DEV2_RC0` root-complex block begins after the endpoint block and covers:

- Conventional PCI bridge/root-port header fields: vendor/device ID, command/status, revision/class fields, header/BIST, base address registers, secondary/subordinate bus numbering, IO and memory base/limit windows, prefetchable base/limit upper words, bridge status/control, ROM BAR, capability pointer, and interrupts.
- Power-management, PCIe device/link/slot/root capability and control/status fields, including PM state/PME fields, max payload/read request controls, relaxed ordering, no-snoop, FLR, completion timeout, link speed/width/training status, slot power/hotplug controls, and root error/status controls.
- MSI, SSID, MSI-map, vendor-specific, virtual-channel, device serial number, and AER fields, including root error command/status, error source ID, header logs, and TLP prefix logs.
- Secondary PCIe capability and lane diagnostics: link control 3, lane error status, and per-lane 8GT equalization controls for lanes 0-15.
- ACS, Data Link Feature, and PCIe PHY 16GT enhanced capabilities, including 16GT equalization-complete/phase-success/request status, local/RTM parity mismatch status fields, and the start of per-lane 16GT DSP/USP TX preset controls.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace. All values are integer literals, mostly with an `L` suffix, and encode only field geometry.

These macros do not define register addresses, reset values, access permissions, field enumerations, write-one-to-clear behavior, read side effects, sequencing requirements, or firmware ownership. Runtime code must pair them with the matching generated address metadata, default-value headers, and AMDGPU access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the relevant NBIO/SMN/PCI configuration access path.

## Control Flow

This header contributes no local runtime control flow. The implied runtime pattern is external:

1. AMDGPU code selects a `BIF_CFG_DEV1_EPF1_0_*` or `BIF_CFG_DEV2_RC0_*` register address from sibling generated NBIO metadata.
2. Code reads a hardware register and extracts a field using the `__SHIFT` and `_MASK` constants, or performs a read-modify-write that preserves unrelated and reserved bits.
3. Hardware state exposed through these fields participates in PCI enumeration, endpoint function setup, bridge window decode, MSI/MSI-X programming, PCIe link setup, power-management transitions, AER/DPC-style diagnostics, virtualization feature enablement, SR-IOV VF sizing, ACS/PASID/ARI isolation, and equalization or lane-status reporting.

Several represented values are asynchronous hardware/protocol state rather than ordinary software state: link training and negotiated speed/width, PME and slot status, MSI mask/pending bits, AER status and header logs, lane error status, 8GT/16GT equalization phase status, parity mismatch status, SR-IOV VF enablement/status, and ACS/PASID/ARI policy state.

## State And Persistence Behavior

The header owns no state, performs no I/O, and persists nothing. The state it describes is stored in NBIO PCIe configuration registers and is governed by hardware reset domains, PCIe conventional reset, hot reset, FLR, link retraining, D-state transitions, platform firmware setup, suspend/resume restore, and explicit driver writes.

State categories represented in this chunk include:

- Identity and decode state for endpoint and root-complex functions: IDs, classes, BARs, bridge windows, bus numbering, ROM BARs, subsystem IDs, and capability list pointers.
- Control policy state: command bits, PCIe device/link/slot/root controls, PM controls, MSI/MSI-X controls, AER masks/severities, BAR size selections, DPA controls, ACS controls, PASID/ARI controls, SR-IOV controls, and VF resizable BAR controls.
- Observed hardware status: conventional status bits, PM/PME status, PCIe device/link/slot/root status, MSI pending bits, AER correctable/uncorrectable status and logs, root error status/source ID, lane error status, data-link feature status, 16GT link/equalization status, and local/RTM parity mismatch status.
- Capability readback state: PM, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, BAR sizing, power budget, DPA, ACS, PASID, ARI, SR-IOV, VF resizable BAR, Data Link Feature, and PCIe PHY 16GT capability fields.

The shift/mask definitions alone do not identify which fields are read-only capability values, sticky status latches, write-one-to-clear status bits, or writable controls. Callers must use hardware documentation and existing AMDGPU access patterns for clearing and restore behavior.

## Dependencies And Integration Points

Primary dependencies are the adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_offset.h` and/or SMN/config-space address headers for register offsets matching these names.
- `nbio_7_11_0_default.h` for reset/default values where generated.
- The rest of `nbio_7_11_0_sh_mask.h`, since this chunk begins and ends inside repeated register families.

Likely integration points in the AMDGPU tree include NBIO 7.11.0 initialization, SOC15-style register access, PCIe endpoint/root-port setup, reset and suspend/resume restoration, MSI/MSI-X programming, PCIe power management, AER/error reporting, link training/equalization diagnostics, SR-IOV virtualization setup, IOMMU-facing isolation controls through ACS/PASID/ARI, and debug paths that report PCIe capability/status registers.

Because this file is generated metadata, integration is symbol-based. A call site must use the register instance that matches the actual hardware function or root port: `DEV1_EPF1` endpoint constants are not interchangeable with `DEV2_RC0` root-complex constants even when similarly named fields have identical bit positions.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly but decode or program the wrong PCIe configuration bits, causing enumeration, BAR sizing, interrupt routing, link training, power management, error handling, or virtualization failures.
- The chunk starts in the middle of `DEV1_EPF0` lane-margining/RTR definitions and ends in the middle of `DEV2_RC0` 16GT lane equalization controls. Merge/reconciliation must use adjacent chunks before treating those boundary register families as complete.
- The endpoint and root-complex blocks contain many repeated PCIe fields with similar names. Using a `DEV1_EPF1` mask against a `DEV2_RC0` register, or vice versa, can be mechanically easy and behaviorally wrong.
- Status and log fields in AER, root error, MSI pending, slot status, and link status registers often have protocol-specific clear or latch semantics. This header does not encode those semantics, so callers must avoid clearing logs before associated status/source/header fields are captured.
- PCI bridge window, BAR sizing, SR-IOV VF BAR, ACS, PASID, and ARI fields affect DMA reachability and isolation. Incorrect programming can break enumeration, peer-to-peer routing, VF assignment, or IOMMU/security assumptions.
- Link control, lane equalization, and 16GT PHY fields can trigger or reflect asynchronous link training. Writers and diagnostics need timeout and race handling around reset, retrain, hotplug/removal, and low-power transitions.
- MSI/MSI-X message address/data, mask, pending, table, and PBA fields are interrupt-routing sensitive; stale restore values or wrong masks can lose or misroute interrupts.
- RTR timing, DPA, power budget, and PM fields expose timing and power-management information but do not express unit conversions or value ranges in the macro names.

## Test Signals

Useful validation signals are mechanical generated-header checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.11.0 support to catch missing, duplicated, or renamed generated symbols.
- Run consistency checks that complete registers in this range have paired `__SHIFT` and `_MASK` definitions and that masks match their shifts and widths. Boundary exceptions should be limited to chunk splits, such as the trailing `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT` shifts whose masks are in the next chunk.
- Cross-check register names against the matching NBIO 7.11.0 offset/SMN/default headers so each field layout maps to an expected address and reset/default value where one exists.
- Compare repeated endpoint/root-complex PCIe capability schemas against adjacent generated blocks to catch per-instance generator drift.
- On supported hardware, validate PCIe enumeration, BAR programming, bridge IO/memory windows, SR-IOV VF exposure, ACS/PASID/ARI controls, MSI/MSI-X delivery and masking, link speed/width negotiation, reset/FLR, suspend/resume, and D-state transitions.
- Exercise error and diagnostic paths: AER correctable/nonfatal/fatal status and masks, root error reporting/source ID, header/TLP-prefix log capture, lane error status, 8GT lane equalization controls, 16GT equalization phase status, and parity mismatch status readback.
- For code that writes these fields, inspect register traces to confirm reserved bits are preserved, status fields are cleared only after dependent logs are captured, and per-instance writes target the expected `DEV1_EPF1` endpoint or `DEV2_RC0` root-complex register.

## Chunk Boundary Notes

Line 39387 begins at `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_STATUS`; the matching lane 14 control register and earlier lane 13 status fields are in the previous chunk. The full `DEV1_EPF1` endpoint address block is contained in this work item.

The range then enters `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` and proceeds through `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT` shifts. The masks for lane 4 and subsequent 16GT lane equalization registers continue after line 41833. Whole-file reconciliation should treat both boundaries as artifacts of line chunking, not missing definitions in the generated source.
