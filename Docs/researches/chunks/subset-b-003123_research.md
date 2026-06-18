# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 2469-4901

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask metadata. It defines C preprocessor constants for bit positions and masks in PCIe root-complex configuration-space registers exposed through the NBIO BIF configuration decode blocks.

The range starts in the middle of the `BIF_CFG_DEV1_RC_PCIE_VC0_RESOURCE_CNTL` family, then covers the remainder of the DEV1 root-complex extended PCIe capability area: VC resource status, device serial number, Advanced Error Reporting, secondary PCIe capabilities, per-lane equalization, ACS, Data Link Feature, 16 GT/s PHY, lane margining, and Routing ID interpretation reporting. It then begins the `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` address block and covers DEV2 root-complex conventional PCI/PCIe configuration fields through AER, secondary capabilities, ACS/DLF/16 GT/s PHY, and lane margining up to the start of lane 11 margining control.

This file contains hardware field geometry only. It does not implement control flow, policy, or register access. AMDGPU code includes it so register helpers can set and decode individual fields without hard-coded bit literals.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this line range. The interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: register-positioned mask for that field.

Major macro groups in this chunk are:

- DEV1 PCIe virtual-channel fields: `BIF_CFG_DEV1_RC_PCIE_VC0_RESOURCE_CNTL` completion fields, `VC0_RESOURCE_STATUS`, full `VC1_RESOURCE_CAP`, `VC1_RESOURCE_CNTL`, and `VC1_RESOURCE_STATUS`. These describe traffic-class to VC mapping, port arbitration table loading/selection/status, VC ID, and VC enable/negotiation state.
- DEV1 device serial number and AER fields: `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, serial-number low/high dwords, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/status, error source ID, and TLP prefix logs.
- DEV1 link-training and extended capability fields: secondary enhanced capability list, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, per-lane equalization controls for lanes 0-15, ACS enhanced capability/capability/control, Data Link Feature capability/status, 16 GT/s PHY enhanced capability, 16 GT/s link capability/control/status, parity mismatch status, 16 GT/s per-lane equalization controls, PCIe margining capability/status, lane margining control/status for lanes 0-15, and RTR capability/data registers.
- DEV2 conventional PCI/bridge fields: vendor/device ID, command/status, revision/program/sub/base class, cache-line/latency/header/BIST, base-address registers, subordinate/secondary/primary bus numbers, I/O and memory windows, prefetchable windows, capability pointer, ROM BAR, interrupt line/pin, IRQ bridge control, and extended bridge control.
- DEV2 power-management and PCIe capability fields: PMI capability list, PM capability, PM status/control, PCIe capability list/capability, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, device capability/control/status 2, link capability/control/status 2, and slot capability/control/status 2.
- DEV2 interrupt and subsystem capability fields: MSI capability list, MSI message control/address/data dwords for 32-bit and 64-bit forms, SSID capability list/capability, MSI mapping capability list/capability, and vendor-specific enhanced capability header/data.
- DEV2 VC/AER/link feature fields: PCIe VC enhanced capability and port VC capability/control/status, VC0/VC1 resource capability/control/status, device serial number, AER status/mask/severity/control/log/source/prefix registers, secondary capability list, link control 3, lane error status, per-lane equalization controls for lanes 0-15, ACS, DLF, 16 GT/s PHY/link/parity/equalization, and lane margining capability/status.
- DEV2 lane margining fields: margining lane control/status pairs for lanes 0-10 are complete in this chunk. Each pair uses receiver number bits, margin type bits, usage model bit, and an 8-bit margin payload field. The final line starts `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL`; the rest of that register is outside this work item.

The companion address definitions for these symbols are expected in `nbio_7_11_0_offset.h`; this NBIO version directory does not include a separate `nbio_7_11_0_default.h` or `nbio_7_11_0_smn.h` file.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. The macros are compile-time constants used by AMDGPU code after it has selected an NBIO 7.11 ASIC path. The direct include site found in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes `nbio_7_11_0_offset.h` and this shift/mask header.

The implied hardware flows are:

1. Initialization, discovery, or diagnostics code reads PCIe configuration-space registers through NBIO register-access wrappers and decodes standard PCI/PCIe fields with these masks.
2. Link setup and retraining code can program device/link control bits, link control 2 target speed and compliance controls, link control 3 equalization controls, and per-lane equalization presets.
3. Error-handling paths can inspect AER uncorrectable/correctable status, mask, severity, root error command/status, source IDs, header logs, and TLP prefix logs to classify PCIe failures.
4. Capability-walking or feature gating can decode capability IDs, capability versions, and next pointers for PCIe extended capabilities such as AER, ACS, DLF, PHY 16 GT/s, margining, RTR, VC, serial number, MSI mapping, and vendor-specific registers.
5. Lane margining and high-speed link validation code can write per-lane receiver/type/usage/payload controls and poll the corresponding status fields.
6. DEV2 bridge-window fields expose conventional PCI bridge resource windows and bus numbering, so any config-space emulation, debug dump, or low-level bridge programming must preserve the split low/high and base/limit encodings.

The header does not enforce ordering. Callers must provide hardware-specific sequencing, such as masking before enabling errors, polling pending/complete bits, waiting for link training state changes, preserving write-one-to-clear status fields, and avoiding writes to read-only capability registers.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The represented state resides in NBIO PCIe root-complex hardware registers.

State categories represented here include:

- PCIe capability and identity state: vendor/device IDs, class code, revision ID, capability list pointers, extended capability IDs/versions/next pointers, serial number, SSID, and vendor-specific capability dwords.
- Bridge/resource-window state for DEV2: bus numbers, I/O base/limit, memory base/limit, prefetchable base/limit and upper dwords, ROM BAR, interrupt fields, bridge control, and IRQ bridge control.
- Feature-enable and policy state: PCI command bits, PM control, MSI enable/control/address/data, PCIe device/link/slot/root controls, VC resource enables and traffic-class maps, ACS controls, DLF exchange controls, AER masks/severities, root error command bits, link control 2/3, 16 GT/s link control, and lane margining control payloads.
- Observation and sticky status state: PCI status, PM status, PCIe device/link/slot/root status, VC negotiation pending and port arbitration status, AER status/log/source fields, lane error status, 16 GT/s link status and parity mismatch status, DLF status, margining port status, and per-lane margining status.

Persistence across GPU reset, FLR, secondary bus reset, suspend/resume, runtime power management, or BACO is not specified by this header. Those semantics come from NBIO hardware behavior and the NBIO 7.11 driver reinitialization paths that use these constants.

## Dependencies and Integration Points

Primary dependencies and integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, the direct user of this generated register metadata in the AMDGPU tree.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`, which provides the `cfg...` register offsets that pair with the field masks in this file.
- AMDGPU register helper macros and SOC/NBIO access wrappers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and NBIO-specific config/MMIO accessors used by the NBIO 7.11 implementation.
- Linux PCIe concepts and flows: conventional PCI bridge configuration, PCI capability and extended capability layouts, MSI programming, PCIe device/link/slot/root controls, AER, ACS, VC, DLF, 16 GT/s equalization, and PCIe lane margining.
- Adjacent chunks of `nbio_7_11_0_sh_mask.h`: the previous chunk owns the beginning of DEV1 VC0 resource capability/control definitions, and the next chunk completes the DEV2 lane 11 margining control/status sequence and subsequent registers.

Because this is generated metadata, integration depends on exact symbol names. A caller must pair the correct `BIF_CFG_DEV[1|2]_RC_*` field macros with the matching DEV1 or DEV2 register offset. DEV1 and DEV2 families intentionally repeat many field layouts but are distinct config decode blocks.

## Risks

- A wrong shift or mask can silently set the wrong PCIe control bit or misclassify a status bit. In this range that can affect link training, AER severity/masking, interrupt generation, ACS isolation, VC arbitration, MSI delivery, bridge resource windows, or lane margining.
- DEV1 and DEV2 use nearly identical names and repeated PCIe capability layouts. Mixing a DEV1 field macro with a DEV2 register offset, or the reverse, can produce plausible-looking but incorrect register operations.
- AER status/mask/severity fields are dense and similarly named. Confusing status with mask/severity can either suppress important errors or report non-errors as failures.
- Some status registers may be sticky or write-one-to-clear depending on hardware. The header only names masks; it does not indicate clear semantics, read-only fields, reserved bits, or reset values.
- Link and lane controls can be disruptive. Misprogramming target speed, equalization presets, compliance bits, retrain controls, or 16 GT/s equalization fields can degrade or drop the PCIe link.
- ACS, VC, and bridge-window fields affect traffic routing and isolation. Incorrect programming can break peer-to-peer routing, resource decode, ordering expectations, or security/isolation assumptions.
- MSI address/data and MSI mapping fields are security-sensitive interrupt routing surfaces. Incorrect writes can lose interrupts or target the wrong interrupt vector.
- Lane margining control/status registers are highly repetitive. Generator or copy/paste drift in one lane is easy to miss unless validation checks all lanes.
- The chunk ends at the comment for `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL`; merge/reconciliation must not treat the missing lane 11 fields here as a source defect.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware-level PCIe coverage:

- Build AMDGPU configurations that select NBIO 7.11 to confirm all included macros parse and match the direct include in `nbio_v7_11.c`.
- Mechanically verify that complete registers in lines 2469-4901 have paired `__SHIFT` and `_MASK` macros, while allowing the intentional chunk split at `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL`.
- Cross-check each `BIF_CFG_DEV1_RC_*` and `BIF_CFG_DEV2_RC_*` register name against `nbio_7_11_0_offset.h` so field macros have matching config-space offsets.
- Run symmetry checks across repeated per-lane fields: DEV1 lanes 0-15 equalization, DEV1 lanes 0-15 margining, DEV2 lanes 0-15 equalization, DEV2 16 GT/s equalization lanes 0-15, and DEV2 margining lanes 0-10 in this chunk should share common field positions.
- Compare repeated DEV1 and DEV2 PCIe capability families where the hardware design expects identical bit layouts, especially AER, ACS, DLF, VC, serial-number, link control 3, and lane equalization fields.
- Validate on NBIO 7.11 hardware by dumping PCIe config-space registers and decoding them with these masks; decoded link speed/width, capability IDs, next pointers, AER bits, MSI state, and bridge windows should agree with Linux PCI core views.
- Exercise PCIe AER test paths, where available, and confirm uncorrectable/correctable status, mask, severity, root error status, source ID, header log, and TLP prefix log fields decode correctly.
- Exercise link retrain/equalization and 16 GT/s capability paths on hardware that supports them; verify link status, equalization complete/phase bits, and parity mismatch status.
- Exercise PCIe lane margining validation across all lanes supported by the link; for this chunk specifically, lanes 0-10 of DEV2 and lanes 0-15 of DEV1 should decode receiver/type/usage/payload status consistently.
- Run suspend/resume, hot reset, FLR, and runtime power-management coverage to confirm driver setup restores writable policy fields and does not rely on undefined persistence for status or capability-derived state.

## Chunk Boundary Notes

The line range starts after the `BIF_CFG_DEV1_RC_PCIE_VC0_RESOURCE_CAP` definitions and after the first few `BIF_CFG_DEV1_RC_PCIE_VC0_RESOURCE_CNTL` shifts. The VC0 resource-control masks and subsequent status fields are inside this work item, but a complete per-file report should use the previous chunk for the beginning of that register family.

The range ends exactly at the `//BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL` comment. Lane 11 control fields, lane 11 status, and any later DEV2 lane margining registers belong to the following chunk.
