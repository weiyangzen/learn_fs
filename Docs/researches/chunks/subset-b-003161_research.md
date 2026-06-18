# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 2446-4910

## Scope

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It contains 2,122 `#define` macros: 1,060 `__SHIFT` constants and 1,062 `_MASK` constants, plus 337 register/address-block comments. There are no executable statements, functions, structs, enums, storage objects, locks, allocations, or persistence logic in this range.

The range starts in the middle of the `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS` Advanced Error Reporting status masks for a root-complex/root-port style function, completes the remaining `DEV1_RC` PCIe capability, AER, ACS, Data Link Feature, 16GT PHY, lane equalization, and lane margining field definitions, then enters the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint/function configuration block. The `DEV0_EPF0` block covers conventional PCI configuration, PCIe capabilities, MSI/MSI-X, AER, resizable BAR, power, DPA, ACS/ATS/PASID/PRI/multicast/LTR/ARI/SR-IOV/TPH, Data Link Feature, 16GT PHY, and the beginning of lane margining through the `LANE_4_MARGINING_LANE_STATUS` comment. The source mirror sits under `sources/distributed-fs/ceph-client`, but this file is AMDGPU hardware register metadata and has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` provides the bitfield-layout side of the generated NBIO 7.2.0 register interface. Each field is exported as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the already shifted mask used to isolate, preserve, or update the field.

Consumers combine these constants with the matching generated register offsets from `nbio_7_2_0_offset.h` and AMDGPU register helpers. The header avoids hard-coded PCIe bit positions in runtime code that configures or diagnoses endpoint and root-port PCIe state.

## Important Macro Families

The opening `BIF_CFG_DEV1_RC` root-complex segment includes:

- Advanced Error Reporting fields: uncorrectable error mask/severity, correctable error status/mask, AER capability/control, TLP header logs, root error command/status, error source ID, and TLP prefix logs.
- Secondary PCIe, lane diagnostic, and ACS fields: secondary enhanced capability metadata, link control 3, lane error status, per-lane 8GT equalization controls for lanes 0-15, ACS capability, and ACS control.
- Data Link Feature and PCIe 16GT PHY fields: DLF capability/status, 16GT link capability/control/status, local/RTM parity mismatch status, and per-lane 16GT equalization transmit presets for lanes 0-15.
- PCIe margining fields: margining enhanced capability metadata, port capability/status, and per-lane margining control/status registers for lanes 0-15.

The generated comments then mark `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec` and `nbio_iohub_nb_pciedummy1_pciedummy_cfgdec` address blocks before the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint/function block begins.

The `BIF_CFG_DEV0_EPF0` endpoint block includes:

- Conventional PCI header and identity fields: vendor/device ID, command/status, revision/class/programming interface, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- Power-management and PCIe base capability fields: vendor capability list, PM capability/status/control, PCIe capability type and message number, device capability/control/status, link capability/control/status, and device/link capability/control/status version 2 fields.
- Interrupt fields: MSI capability, MSI message control, 32-bit and 64-bit message address/data, MSI mask/pending bits, MSI-X capability, MSI-X message control, table, and PBA descriptors.
- PCIe vendor-specific, virtual-channel, serial-number, and AER fields: enhanced capability headers, VC port/resource capability/control/status, device serial number dwords, uncorrectable/correctable AER status/mask/severity, AER capability/control, header logs, and TLP prefix logs.
- BAR sizing and power fields: enhanced BAR capability/control for BAR1-BAR6, power budget selector/data/capability, Dynamic Power Allocation capability/status/control, latency indicator, and DPA substate power allocation entries 0-7.
- Isolation, translation, and virtualization fields: ACS capability/control, ATS capability/control, page request capability/status/capacity/allocation, PASID capability/control, multicast capability/control/address/receive/block registers, LTR capability, ARI capability/control, SR-IOV capability/control/status/VF counts/VF offset/stride/device ID/page size/VF BARs/migration array offset, and TPH requester capability/control.
- Link diagnostic and PHY fields: Data Link Feature capability/status, 16GT enhanced capability metadata, 16GT link capability/control/status, local and RTM parity mismatch status, per-lane 16GT equalization presets for lanes 0-15, PCIe margining capability/status, and lane margining control/status through lane 4 at the chunk boundary.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace. The values are integer literals, mostly with an `L` suffix, and encode field geometry only.

This header does not define register addresses, reset values, access permissions, enumerated value meanings, read side effects, write-one-to-clear behavior, firmware ownership, or sequencing rules. Runtime code must pair these constants with sibling address metadata and AMDGPU access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the actual call path.

## Control Flow

This chunk contributes no local runtime control flow. The implied external pattern is:

1. AMDGPU code selects a `BIF_CFG_DEV1_RC_*` or `BIF_CFG_DEV0_EPF0_*` register address from matching NBIO 7.2.0 offset metadata.
2. Code reads a hardware/config-space register and extracts a field with the matching `__SHIFT` and `_MASK`, or performs a read-modify-write that preserves unrelated and reserved bits.
3. Hardware state exposed by these fields participates in PCI enumeration, endpoint configuration, BAR sizing, MSI/MSI-X setup, PCIe link setup, AER diagnostics, power management, ACS/ATS/PASID/PRI/ARI routing and isolation, SR-IOV VF exposure, DPA/power-budget reporting, and lane equalization or margining diagnostics.

Several represented values are asynchronous protocol or hardware state rather than ordinary software state: link training status, negotiated link speed/width, equalization phase completion, parity mismatch status, AER/root error latches and logs, MSI pending state, page request status, SR-IOV VF enablement, and margining readiness/results.

## State And Persistence Behavior

The header owns no state, performs no I/O, and persists nothing. It describes NBIO PCIe configuration register fields whose values live in hardware and are affected by hardware reset domains, PCIe conventional reset, hot reset, FLR, link retraining, D-state transitions, platform firmware initialization, suspend/resume restore, and explicit driver writes.

State categories represented here include:

- Identity and decode state: IDs, class codes, BARs, ROM BARs, capability pointers, subsystem/adapter identifiers, and endpoint address decode controls.
- Control policy state: PCI command bits, PM controls, PCIe device/link controls, AER masks/severities, MSI/MSI-X controls, BAR size selections, DPA controls, ACS/ATS/PASID/PRI/ARI controls, multicast controls, SR-IOV controls, TPH controls, and lane margining controls.
- Observed status and logs: PCI status, device/link status, PM/PME status, MSI pending bits, AER status and header/TLP-prefix logs, root error source/status, parity mismatch status, page request status, 16GT equalization status, and lane margining status.
- Capability readback state: PM, PCIe, MSI/MSI-X, VC, AER, resizable BAR, power budget, DPA, ACS, ATS, PASID, multicast, LTR, ARI, SR-IOV, TPH, Data Link Feature, 16GT PHY, and margining capabilities.

The shift/mask definitions do not identify which fields are read-only capabilities, sticky status latches, write-one-to-clear status bits, or writable controls. Callers must rely on the PCIe specification, AMD hardware documentation, and established AMDGPU access patterns for clearing, restore, and ownership behavior.

## Dependencies And Integration Points

The direct generated dependency in this source tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the matching register offsets. No same-directory `nbio_7_2_0_default.h` companion is present in this tree, so reset/default-value analysis for these exact registers cannot be derived from a matching default header here.

Likely AMDGPU integration points include NBIO 7.2.0 initialization, SOC15/NBIO register access, PCIe endpoint/root-port setup, PCI enumeration support paths, reset and suspend/resume restore, MSI/MSI-X programming, link speed/width and equalization diagnostics, AER/error reporting, power-management and DPA handling, SR-IOV virtualization setup, IOMMU-facing isolation controls through ACS/ATS/PASID/PRI/ARI, and debug or telemetry paths that report PCIe capability/status registers.

The namespace is instance-sensitive. `DEV1_RC` root-complex constants are not interchangeable with `DEV0_EPF0` endpoint constants even when the field names and bit positions mirror standard PCIe layouts.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while decoding or programming the wrong PCIe configuration bits, causing enumeration, BAR sizing, interrupt routing, link training, power management, AER, virtualization, or isolation failures.
- This range starts inside `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS` masks and ends at the `BIF_CFG_DEV0_EPF0_LANE_4_MARGINING_LANE_STATUS` comment. Whole-file reconciliation must use adjacent chunks before treating those boundary register families as complete.
- Many endpoint and root-complex registers use repeated standard PCIe field names. A mechanical substitution between `DEV1_RC` and `DEV0_EPF0` can silently target the wrong hardware instance.
- AER, root error, MSI pending, page request, link status, parity mismatch, and lane margining status fields may have sticky, write-one-to-clear, or log-capture ordering requirements not expressed in this header.
- BAR, resizable BAR, SR-IOV VF BAR, ACS, ATS, PASID, PRI, ARI, and multicast fields affect DMA reachability and isolation. Incorrect programming can break enumeration, peer-to-peer routing, VF assignment, or IOMMU/security assumptions.
- Link control, equalization, 16GT PHY, and margining fields interact with asynchronous link training and low-power transitions. Diagnostics and writers need timeout, retrain, reset, and hotplug race handling.
- MSI/MSI-X message address/data, mask, pending, table, and PBA fields are interrupt-routing sensitive; stale restore values or wrong masks can lose or misroute interrupts.
- Power budget, DPA, LTR, readiness, and margining fields expose encoded values whose units and valid ranges are not carried by the macro names.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware coverage:

- Build AMDGPU configurations that include NBIO 7.2.0 support to catch missing, duplicated, or renamed generated symbols.
- Verify that complete registers in this range have paired `__SHIFT` and `_MASK` definitions, and that masks align with their shifts and expected widths. Boundary exceptions should be limited to the leading status masks and trailing lane 4 margining status continuation.
- Cross-check register names against `nbio_7_2_0_offset.h` so each field layout maps to an expected NBIO 7.2.0 register address.
- Compare repeated standard PCIe schemas between `DEV1_RC` and `DEV0_EPF0`, and against neighboring generated NBIO versions, to catch generator drift.
- On supported hardware, validate PCIe enumeration, BAR sizing/programming, MSI/MSI-X delivery and masking, link speed/width negotiation, FLR/reset, suspend/resume, D-state transitions, SR-IOV VF exposure, ACS/ATS/PASID/PRI/ARI controls, and IOMMU isolation behavior.
- Exercise diagnostic paths for AER correctable/nonfatal/fatal status and masks, root error reporting/source ID, header and TLP-prefix log capture, VC status, page request status, link equalization status, lane error status, 16GT parity mismatch status, and lane margining readback.
- For code that writes these fields, inspect register traces to confirm reserved bits are preserved, status fields are cleared only after dependent logs are captured, and per-instance writes target the intended `DEV1_RC` or `DEV0_EPF0` register.

## Chunk Boundary Notes

Line 2446 is already inside the `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_STATUS` mask list; the matching shifts and earlier masks for that status register are in the previous chunk. The `DEV1_RC` portion is otherwise carried through complete PCIe AER, secondary, ACS, DLF, 16GT PHY, and lane margining families.

Line 4910 is the comment introducing `BIF_CFG_DEV0_EPF0_LANE_4_MARGINING_LANE_STATUS`; the fields for that status register and the remaining endpoint lane margining registers continue in the next chunk. These are line-chunk artifacts, not missing definitions in the generated header.
