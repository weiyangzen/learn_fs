# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 2455-4912

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains C preprocessor constants for register field bit positions and masks only. There are no functions, structs, enums, variables, allocations, locks, direct MMIO operations, or executable control flow in this range.

The requested lines contain about 2.1k `#define` statements and 321 generated register/address-block comments. The range starts in the middle of `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`, covers the rest of the DEV1 root-complex PCIe extended capability field layouts, all of the `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` address block, and then the beginning of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint-function block through `BIF_CFG_DEV0_EPF0_PCIE_LANE_13_EQUALIZATION_CNTL`. The first and last visible register families are incomplete and must be reconciled with adjacent chunks during the final per-file merge.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.7.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the encoded in-register bit mask.

Driver code pairs these constants with matching register-address metadata from sibling generated headers and with AMDGPU register helpers to compose or decode PCI/PCIe configuration-space and NBIO register values without hard-coded bit positions.

This chunk describes PCIe root-complex and endpoint configuration surfaces: advanced error reporting, header and TLP-prefix logs, root error reporting, lane equalization, ACS, data link feature reporting, 16 GT/s link status and per-lane presets, PCIe margining, root-complex bridge configuration, BAR/window routing, power-management capability state, MSI/MSI-X metadata, vendor-specific and virtual-channel capabilities, serial number capability, resize BAR controls, power budgeting, dynamic power allocation, and the start of endpoint 8 GT/s lane equalization fields.

## Important Macro Families

The DEV1 root-complex tail covers PCIe reliability and high-speed link capabilities:

- AER severity/status/mask/control fields for uncorrectable and correctable errors, including unsupported request, ACS violation, internal errors, malformed/bad TLP or DLLP, replay rollover or timeout, advisory nonfatal, header log overflow, ECRC enable/capability, multi-header logging, root error command/status, error source IDs, four DWORD TLP header logs, and four TLP prefix logs.
- Secondary and ACS enhanced capability fields, including capability ID/version/next pointers, source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P support, and matching enable bits.
- Data Link Feature capability/status fields for local and remote DLF support and exchange-valid state.
- PCIe 16 GT/s PHY capability/status fields, including equalization complete, per-phase equalization success, link equalization request, local/RTM parity mismatch status, and per-lane 16 GT/s downstream/upstream TX presets for lanes 0 through 15.
- PCIe margining capability and per-lane control/status fields, including margining uses, sample reporting method, independent timing/voltage margin capability, voltage/time offset support, max timing and voltage offsets, sampling rate, ready/abort flags, margin command fields, receiver number, margin type, usage model, and margin payload/status for lanes 0 through 15.

The DEV2 root-complex address block maps a PCI-to-PCI bridge style root-complex configuration space:

- Identity, class, header, BIST, BAR, bus-number, IO/memory/prefetchable window, ROM, interrupt, bridge-control, and extended bridge-control fields.
- Power-management status/control fields for D-state, no-soft-reset, PME enable/status, data select/scale, bus power enable, and PMI data.
- PCIe capability fields for device/link/slot capabilities and controls: max payload, extended tag, relaxed ordering, no-snoop, FLR, link speed/width, ASPM, link retrain/disable, link training, data-link active, slot power, hotplug events, slot indicators, secondary bus reset, and slot control/status extensions.
- MSI and subsystem capability fields, including MSI address/data variants and MSI map controls.
- Vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, ACS, 16 GT/s PHY, and margining enhanced capability list entries. DEV2's AER content in this chunk is narrower than DEV1 and DEV0: it includes correctable status/mask, logs, and prefix logs, but not the full uncorrectable severity group visible for DEV1 or DEV0 in this slice.

The DEV0 endpoint-function block starts the endpoint configuration-space model for function 0:

- Endpoint identity and conventional PCI config fields: vendor/device IDs, command/status, revision/class, cache line/latency, header/BIST, BAR1 through BAR6, cardbus CIS pointer, subsystem IDs, expansion ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Power-management capability and status/control fields similar to DEV2 but in endpoint form.
- PCIe endpoint capability fields: device/link capabilities, device/link control and status, extended Device Capabilities 2 and Control 2, Link Capabilities 2, Link Control 2, Link Status 2, and Link Control 3. These cover completion timeout support/control, ARI, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, TLP prefix support/blocking, emergency power reduction, supported link speeds, skip ordered set support, DRS, target link speed, compliance controls, equalization status, and downstream-component presence.
- MSI and MSI-X capability fields: MSI enable/multi-message control, 64-bit address/data, extended message data, masks and pending bits, MSI-X table/PBA BIR and offsets, table size, function mask, and enable bits.
- Endpoint enhanced capabilities: vendor-specific headers/data, virtual channels and VC0/VC1 resource controls, device serial number, AER uncorrectable/correctable status/masks/severity/logs, resize BAR capabilities/controls for BAR1 through BAR6, power budgeting, dynamic power allocation, secondary PCIe capability, and the first endpoint per-lane 8 GT/s equalization controls.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

The macros do not encode register offsets, reset values, access widths, read/write permissions, write-one-to-clear behavior, polling requirements, firmware ownership, or sequencing. Consumers must combine them with sibling address/default headers and AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or NBIO/SMN accessors selected by the call site.

## Control Flow

This header has no local runtime control flow. Runtime behavior is external:

1. AMDGPU code selects a DEV1 root-complex, DEV2 root-complex, or DEV0 endpoint-function register address from generated NBIO metadata.
2. The code reads a hardware register or PCIe configuration register, extracts fields with the `__SHIFT` and `_MASK` pair, or composes a read-modify-write value while preserving unrelated and reserved bits.
3. Hardware and firmware state machines perform the actual behavior: PCIe enumeration, bridge window routing, MSI/MSI-X delivery, link training, link retraining, AER capture/reporting, ACS isolation, virtual-channel arbitration, dynamic power allocation, resize BAR handling, lane equalization, and margining diagnostics.

The field names imply asynchronous hardware flows outside this header: AER status latching and clearing, root error message delivery, ECRC generation/checking, link equalization phases, per-lane 8 GT/s and 16 GT/s preset negotiation, margining command completion, data-link feature exchange, MSI/MSI-X programming by the PCI core, hotplug/slot-event signaling for root ports, and power-management/D-state transitions.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCI/PCIe configuration registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, FLR, D-state transitions, suspend/resume, BIOS or firmware initialization, driver reinitialization, and explicit register writes.

Represented state includes conventional PCI identity/configuration fields, bridge resource windows, BAR decode and resize settings, capability-list pointers, MSI/MSI-X address/data/mask/pending state, power-management status/control, PCIe device/link/slot control and status, AER latched error state and logs, ACS controls, virtual-channel resource controls, serial number data, power budget and DPA substate values, and lane equalization/margining status.

Many fields are live status or latched error indicators rather than persistent configuration. Examples include link training/data-link-active status, AER correctable/uncorrectable status, root error status, header-log overflow, MSI pending bits, slot status, DPA substate status, equalization phase success, and margining ready/abort/status fields. The mask definitions alone do not specify whether such bits are read-only, self-clearing, write-one-to-clear, clear-on-read, or reset by a particular PCIe event.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7.0 register database staying synchronized across sibling files:

- `nbio_7_7_0_offset.h`, `nbio_7_7_0_smn.h`, or related generated address headers provide register offsets and access-path metadata for names in this shift/mask header.
- `nbio_7_7_0_default.h`, where present, provides reset/default values for related registers.
- AMDGPU bitfield and register-access helpers provide token-pasting, masking, shifting, MMIO, PCIe config, or SMN access.

Runtime integration points include AMDGPU NBIO initialization, PCIe capability setup, PCI resource and BAR programming, resize BAR handling, AER enablement and diagnostics, GPU reset and FLR handling, SR-IOV and IOV-related capability exposure in adjacent endpoint functions, MSI/MSI-X interrupt setup, suspend/resume restore, link-speed/link-width policy, link retraining and equalization recovery, ACS/IOMMU isolation behavior, virtual-channel handling, power-management policy, and hardware debug paths that read margining or AER logs.

The path's `ceph-client` prefix is only part of the source mirror layout. The actual consumers are GPU DRM/AMDGPU code paths, not Ceph filesystem code.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while decoding or programming the wrong PCIe bit, causing enumeration failures, bad BAR/resource windows, broken interrupts, missed AER reporting, link instability, or incorrect power-management behavior.
- The chunk begins after the `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY` register comment and earlier field definitions, so DEV1 AER severity is incomplete here. It also ends before the final masks for `BIF_CFG_DEV0_EPF0_PCIE_LANE_13_EQUALIZATION_CNTL` and before endpoint lanes 14 and 15, so endpoint equalization coverage is incomplete.
- Full-width fields such as header logs, TLP prefix logs, BARs, MSI addresses, serial-number DWORDs, vendor-specific data, and ROM/base fields look mechanically simple but often carry alignment, ownership, or side-effect requirements outside this header.
- AER and status registers may use clear-sensitive semantics. Treating all fields as ordinary read/write bits can lose diagnostic evidence or fail to clear an interrupt source.
- Link control, target speed, retrain, equalization, DRS, and compliance fields are sequencing-sensitive. Misuse can temporarily or permanently disrupt PCIe connectivity until reset.
- ACS, VC, BAR, and resize-BAR fields affect isolation, routing, peer-to-peer behavior, and host resource assignment. Incorrect masks can create subtle IOMMU, passthrough, or virtualization failures.
- MSI/MSI-X address, data, mask, table, and PBA fields are interrupt-delivery critical. A wrong field width can cause lost interrupts, interrupt storms, or vector misattribution.
- Repeated DEV1/DEV2/DEV0 and lane 0-15 families invite copy/paste assumptions. Similar names do not guarantee identical fields across root-complex and endpoint blocks.
- Reserved fields are present throughout the covered configuration space. Writers must preserve reserved bits unless hardware documentation and existing driver sequences say otherwise.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include NBIO 7.7.0 support. Missing, renamed, or malformed macros should surface as compile failures in NBIO, PCIe, interrupt, reset, or power-management consumers.
- Mechanically compare every `__SHIFT` and `_MASK` in this line range against AMD's authoritative NBIO 7.7.0 register database.
- Cross-check each `BIF_CFG_DEV1_RC_*`, `BIF_CFG_DEV2_RC_*`, and `BIF_CFG_DEV0_EPF0_*` register group against sibling offset/default headers so field layouts map to known registers.
- Run shift/mask sanity checks: masks should align with shifts, paired fields should not overlap unexpectedly, full-width log/data fields should use `0xFFFFFFFFL`, per-lane equalization and margining families should be structurally consistent, and reserved gaps should match the hardware spec.
- On supported hardware, validate PCIe enumeration, BAR sizing and resize BAR behavior, link speed/width negotiation, retraining, suspend/resume, FLR/GPU reset, D-state transitions, and hot reset recovery.
- Exercise MSI and MSI-X setup, masking, pending-bit behavior, and interrupt delivery under load.
- Exercise AER and link diagnostics where available: correctable/uncorrectable error capture, header/TLP-prefix logs, root error status/source IDs, ECRC enable/check behavior, ACS controls, virtual-channel status, DPA substate reporting, and lane equalization or margining status.
- Decode known-good register dumps with these masks and compare against reference tooling or hardware documentation, especially for AER logs, link status, MSI/MSI-X state, BAR controls, power-management controls, ACS, VC, DPA, and per-lane equalization fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-003260`. The final per-file research should merge it with neighboring chunks for full `nbio_7_7_0_sh_mask.h` coverage. The previous chunk owns the start of `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`; the next chunk completes `BIF_CFG_DEV0_EPF0_PCIE_LANE_13_EQUALIZATION_CNTL` and continues endpoint lane/equalization and later NBIO register families.
