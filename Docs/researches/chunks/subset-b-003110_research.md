# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 102487-104918

## Scope

This chunk covers 2,432 lines from AMDGPU's generated NBIO 7.0 shift/mask header. It contains 2,147 `#define` field-layout constants and 279 register-family comments. There are no functions, structs, enums, variables, executable statements, locks, allocations, or direct MMIO/SMN/PCI configuration accesses in this range.

The range starts in the middle of `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL`, after the shift definitions and at the remaining masks for lane 7. It then covers lane 8 through lane 15 equalization and ACS definitions for `DEV0_RC2`, the complete `addressBlock: nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`, and most of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. It ends inside `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL` after the `SOURCE_VALIDATION_EN_MASK`; the remaining ACS control masks continue in the next chunk.

Although this file is under a `ceph-client` source mirror, the content is AMD GPU/NBIO PCIe register metadata and has no distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. Each exported macro gives either:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate or update that field.

This chunk focuses on NBIF0 PCI configuration-space decode blocks. `BIF_CFG_DEV1_RC2_*` describes a PCIe root-complex/bridge-style function with standard PCI header fields, PCI PM, PCIe, MSI, SSID, MSI-map, vendor-specific, virtual-channel, device-serial-number, AER, secondary PCIe, lane equalization, and ACS capability fields. `BIF_CFG_DEV0_EPF0_3_*` describes an endpoint-function configuration-space block with standard endpoint header fields, BARs, ROM BAR, vendor and adapter IDs, PCI PM, PCIe, MSI/MSI-X, VC, serial number, AER, BAR enhanced capability, power-budget, dynamic power allocation, secondary PCIe, lane equalization, and ACS fields.

The header does not configure PCIe, expose a runtime API, or enforce sequencing. It supplies symbolic field geometry to code that performs those operations through companion offset/default headers and AMDGPU register helpers.

## Important Macro Families

The opening partial section completes `BIF_CFG_DEV0_RC2` lane-equalization and ACS field masks:

- `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` ends with the downstream/upstream TX preset and RX preset-hint masks plus the reserved bit mask.
- `BIF_CFG_DEV0_RC2_PCIE_LANE_8_EQUALIZATION_CNTL` through lane 15 repeat the same layout: downstream TX preset at bits 0-3, downstream RX preset hint at bits 4-6, upstream TX preset at bits 8-11, upstream RX preset hint at bits 12-14, and a reserved bit at bit 15.
- `BIF_CFG_DEV0_RC2_PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services capability IDs, version/next pointers, support bits, and enable bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, and direct translated P2P.

The `BIF_CFG_DEV1_RC2_*` block is a complete bridge/root-port-style PCI config-space map:

- Standard PCI identity and bridge header fields: vendor/device ID, command/status, revision/class code, cache line, latency, header type, BIST, bridge BAR, bus numbers, I/O base/limit, memory base/limit, prefetchable base/limit upper/lower fields, capability pointer, interrupt line/pin, bridge control, and extended bridge control.
- Power-management capability: PM capability list/header fields, supported D-states, PME support, version, next pointer, and PM status/control fields such as power state, PME enable/status, data select, data scale, and bus-power/clock-control bits.
- PCIe capability: PCIe capability header, device/link/slot/root capability, control, and status registers; capability 2, device control/status 2, link capability/control/status 2, and slot control/status 2.
- MSI and MSI mapping: MSI capability list, message control, 32-bit/64-bit message address/data, MSI map capability, and MSI map base address fields.
- Subsystem ID and vendor-specific enhanced capability scratch/header fields.
- Virtual Channel capability: port VC capability/control/status plus VC0 and VC1 resource capability/control/status, TC-to-VC maps, arbitration tables, VC IDs, and enable/status bits.
- Device serial number enhanced capability: low and high 32-bit serial number fields.
- Advanced Error Reporting: uncorrectable/correctable error status, masks, severity, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe and ACS: link control 3, lane error status, per-lane equalization control registers for lanes 0-15, ACS enhanced capability list, ACS capability, and ACS control.

The `BIF_CFG_DEV0_EPF0_3_*` block is an endpoint-function PCI config-space map:

- Standard endpoint header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, BAR1 through BAR6, adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor/adapter and power-management capabilities: vendor capability list, adapter ID write field, PM capability, and PM status/control.
- PCIe endpoint capability: device/link capability, control, and status registers; capability 2, device/link control/status 2, and slot-control/status 2 definitions present in this endpoint block.
- MSI/MSI-X: MSI message control, address/data, mask and pending fields including 64-bit variants; MSI-X capability list, message control, table, and PBA fields.
- Vendor-specific, VC, serial-number, and AER enhanced capabilities: same broad capability families as `DEV1_RC2`, with endpoint-specific root-error fields absent where not applicable in this range.
- BAR enhanced capability: BAR1 through BAR6 capability/control fields for BAR sizing/indicator/prefetchability and control enablement.
- Power budget and DPA: power-budget data select/data/capability fields, DPA capability, latency indicator, status, control, and substate power allocations 0-7.
- Secondary PCIe and lane equalization: link control 3, lane error status, lane 0-15 equalization control layouts, and the beginning of ACS capability/control.

## APIs, Types, And Functions

There are no callable APIs, C types, or local helper functions in this chunk. The exported interface is the generated macro namespace. The constants are untyped C preprocessor integer literals, typically suffixed with `L`, and must be paired with:

- `nbio_7_0_offset.h` for register offsets/address selectors.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helpers such as field extraction/composition helpers and MMIO, SMN, or PCI configuration accessors selected by the consuming code.

The macros encode only field location and width. They do not encode read/write permissions, reset value, access size, write-one-to-clear behavior, self-clearing behavior, firmware ownership, side effects, or required ordering.

## Control Flow

This header has no local runtime control flow. Runtime usage is external and typically follows this pattern:

1. Driver code selects an NBIO 7.0 register offset from the generated offset header.
2. It reads a PCIe/NBIO register through the appropriate AMDGPU access path.
3. It decodes a field with a `__SHIFT` and `_MASK`, or composes a read-modify-write value while preserving unrelated bits.
4. Hardware reacts according to PCIe/NBIO semantics: configuration-space enablement, link control, interrupt programming, AER status/mask changes, ACS routing/isolation policy, power-management policy, BAR/DPA capability handling, or lane equalization state.

The source order follows the generated register database, not an execution sequence. Several logical hardware flows are represented by field names: PCI enumeration and bridge-window programming, endpoint BAR/resource programming, MSI/MSI-X setup, PCI PM and PCIe power-management negotiation, AER error reporting, virtual-channel arbitration, secondary PCIe lane equalization, ACS policy, power budgeting, DPA substate selection, and link diagnostics.

## State And Persistence Behavior

The header owns no software state and persists nothing. It names hardware-visible fields in NBIO PCI configuration-space decode blocks. Persistence depends on PCI reset semantics, GPU/NBIO reset domains, function-level reset, power state transitions, firmware/BIOS initialization, suspend/resume restore, and explicit driver writes.

The represented hardware state includes:

- Configuration controls such as command bits, bus mastering, memory/I/O decode, interrupt disable, bridge controls, link controls, MSI/MSI-X enables, AER masks, ACS enables, VC resource controls, BAR controls, PM/DPA controls, and power-budget selectors.
- Capability and identity fields such as vendor/device ID, class code, capability IDs, link capability, slot/root/device capabilities, serial number, BAR capability descriptors, DPA capability, and ACS support bits.
- Status or sticky fields such as PCI status, secondary status, device/link/slot/root status, AER error status, lane error status, MSI pending bits, DPA status, VC status, and power-management status.
- Command-like fields such as secondary bus reset, link retrain, PME status/enable, AER root error commands, VC arbitration load/select, BAR control updates, DPA transition controls, and MSI/MSI-X mask bits.

The shift/mask definitions cannot be used alone to decide whether a field is volatile, sticky, write-one-to-clear, read-only, write-only, reserved, or self-clearing. Consumers must rely on PCIe specifications, AMD hardware documentation, and local driver policy.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register-header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` supplies matching default values; the `BIF_CFG_DEV1_RC2_*` and `BIF_CFG_DEV0_EPF0_3_*` names appear there as `smn..._DEFAULT` definitions.
- AMDGPU SOC15/NBIO platform code includes the NBIO 7.0 generated headers to access ASIC-specific registers.

The practical integration points are PCIe and NBIF behavior rather than file-system logic: GPU enumeration, bridge/root-complex configuration, endpoint-function resource setup, interrupt setup, AER handling, ACS/IOMMU isolation policy, PCIe link training and diagnostics, ASPM/power management, MSI/MSI-X table handling, virtual-channel programming, BAR capability reporting, power-budget/DPA reporting, reset/recovery, and debug register dumps.

## Risks And Edge Cases

- The chunk starts and ends mid-register-family. `DEV0_RC2` lane 7 shifts are before this chunk, and the remaining `DEV0_EPF0_3_PCIE_ACS_CNTL` masks are after this chunk. File-level conclusions must reconcile adjacent chunks.
- A wrong generated shift or mask can compile cleanly while writing the wrong PCIe configuration bit, clearing adjacent status, misreporting capability support, or breaking interrupt, link, or isolation behavior.
- PCI status, secondary status, device status, root status, AER status, MSI pending, and similar fields may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear errors if it writes status registers without W1C-aware handling.
- `COMMAND`, BAR, ROM BAR, bridge resource-window, bus-number, and bridge-control masks can affect whether devices decode memory/I/O, whether bus mastering is allowed, and whether downstream resources are reachable.
- `SECONDARY_BUS_RESET`, link retrain/disable, target speed, compliance, DPA, and power-management control fields can disrupt active devices or links if written outside controlled reset or power-management sequences.
- MSI and MSI-X fields distinguish message address/data, enable/mask, table/PBA location, and pending bits. Confusing pending/status fields with masks or enables can cause lost or stuck interrupts.
- AER status, mask, and severity registers often use identical bit positions with different meanings. Copying fields between status/mask/severity contexts can change whether errors are reported, suppressed, classified fatal, or cleared.
- ACS fields affect peer-to-peer routing and isolation. Incorrect capability/control decoding can affect IOMMU grouping, VFIO/passthrough assumptions, SR-IOV-style isolation, or peer DMA policy.
- Lane equalization control is repeated for lanes 0-15. Off-by-one lane selection or a prefix mix-up between `DEV0_RC2`, `DEV1_RC2`, and `DEV0_EPF0_3` can appear only as link training instability on certain widths or speeds.
- The endpoint `EPF0_3` block includes MSI-X, BAR enhanced capability, power-budget, and DPA fields that have different semantics from the bridge/root-port `DEV1_RC2` block. Similar field names should not be treated as interchangeable across function types.
- Reserved masks are present throughout. Writers must preserve reserved bits unless authoritative hardware documentation explicitly permits writing them.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0/SOC15 support. Compile failures catch malformed generated symbols or missing companion definitions.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every field should have the expected shift/mask, every register should have a matching offset entry, and default values should exist where defined.
- Cross-check repeated lane equalization families for lanes 0-15 across `DEV0_RC2`, `DEV1_RC2`, and `DEV0_EPF0_3`: the field layouts should match except for the register prefix.
- Validate PCIe enumeration on supported hardware: vendor/device/class IDs, bridge bus numbers, I/O and memory windows, BARs, ROM BAR, command/status, capability pointers, and PCIe capability chains should decode coherently with `lspci -vv` or equivalent diagnostics.
- Exercise MSI/MSI-X setup, vector masking/unmasking, pending-bit visibility, suspend/resume restore, GPU reset restore, and interrupt delivery under load for functions using these NBIF config-space blocks.
- Exercise PCIe link behavior: negotiated speed/width, link retraining, lane error reporting, Gen speed changes, equalization status, ASPM/PM transitions, and reset recovery.
- Exercise AER handling where available: correctable and uncorrectable status, mask, severity, header-log, TLP-prefix-log, root-error command/status, and error-source-ID decoding.
- Validate ACS and IOMMU grouping/passthrough behavior on platforms exposing these blocks, especially when peer-to-peer DMA or virtualization depends on isolation.
- Validate power-related reporting and controls for endpoint functions: PCI PM status/control, power-budget data selection, DPA status/control, and DPA substate power allocation values across cold boot, warm reset, and resume.
- Include boundary checks during merge: complete `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` from the prior chunk and complete `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL` from the following chunk before producing the final per-file report.
