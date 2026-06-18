# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 123213-125593

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains only C preprocessor constants for PCIe/NBIO register field bit positions and raw masks. There are no C functions, structs, enums, variables, register reads/writes, allocations, locks, or local runtime branches in this range.

The requested range is 2,381 source lines: 2,178 `#define` statements and 201 generated comments. It starts in the middle of `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL`, continues through the end of the `BIFPLR1_2` root-port capability tail, enters `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, and then defines most of the `BIFPLR2_2` root-port/bridge PCIe configuration field layout through the beginning of `BIFPLR2_2_PCIE_ESM_CAP_5`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU DRM hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the bitfield companion to AMD's generated NBIO 7.7.0 register-address headers. For each hardware register field, this header exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask in the unshifted register value.

Driver code combines these constants with matching register offsets from `nbio_7_7_0_offset.h` and AMDGPU register helper macros to decode PCIe/NBIO configuration registers or compose read-modify-write values without hard-coded bit numbers.

This chunk focuses on PCIe root-port and bridge configuration surfaces for the `BIFPLR1_2` tail and `BIFPLR2_2` block: L1 PM substates, Downstream Port Containment, root-port PIO error logging, Enhanced Speed Mode support, 16 GT/s and 32 GT/s link capabilities, conventional bridge configuration header fields, PCIe/PM/MSI/SSID/vendor/virtual-channel capabilities, AER, lane equalization, ACS, multicast, and part of the repeated ESM data-rate capability bitmap.

## Public Surface

The public API is entirely macro based. The macros are untyped preprocessor integer literals, mostly with an `L` suffix for masks. They encode bit geometry only; they do not encode register offsets, defaults, access width, read/write permissions, write-one-to-clear semantics, polling rules, firmware ownership, legal value constraints, or programming order.

Representative families in this chunk include:

- `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL*`, `BIFPLR1_2_PCIE_DPC_*`, `BIFPLR1_2_PCIE_RP_PIO_*`, `BIFPLR1_2_PCIE_ESM_*`, and `BIFPLR1_2_LINK_*`.
- `BIFPLR2_2_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class/header/BIST fields, bus-number and bridge-window fields, interrupt and bridge-control fields.
- `BIFPLR2_2_PMI_*`, `PCIE_CAP*`, `DEVICE_*`, `LINK_*`, `SLOT_*`, and `ROOT_*` conventional PCIe capability fields.
- `BIFPLR2_2_MSI_*`, `SSID_*`, `MSI_MAP_*`, `PCIE_VENDOR_SPECIFIC*`, `PCIE_VC*`, and `PCIE_DEV_SERIAL_NUM_*`.
- `BIFPLR2_2_PCIE_ADV_ERR_*`, uncorrectable/correctable AER status/mask/severity, header logs, root error command/status, error source IDs, and TLP prefix logs.
- `BIFPLR2_2_PCIE_SECONDARY_*`, lane 0-15 equalization controls, ACS, multicast, L1 PM substates, DPC, RP PIO, and ESM fields.

Spot checks against `nbio_7_7_0_offset.h` show matching offset symbols for names in this range, such as `regBIFPLR1_2_PCIE_ESM_CAP_7`, `regBIFPLR2_2_VENDOR_ID`, and `regBIFPLR2_2_PCIE_DPC_CNTL`. The only direct in-tree include found for this generated header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.

## Important Register Families

The `BIFPLR1_2` tail starts with the remaining masks for L1 PM substate control, including link activation, common-mode restore time, and LTR L1.2 threshold value/scale. It then defines L1.2 power-on timing in `PCIE_L1_PM_SUB_CNTL2`.

The `BIFPLR1_2` DPC and RP PIO families define containment and error-logging fields: DPC enhanced capability ID/version/next pointer, DPC interrupt message number, RP extension support, poisoned TLP egress blocking, software trigger support, PIO log size, DL-active error signaling, DPC trigger/completion/interrupt/error controls, trigger status/reason, RP busy, first PIO error pointer, error source ID, PIO status/mask/severity/system-error/exception bits for config, I/O, and memory unsupported-request, completer-abort, and completion-timeout cases, plus four TLP header-log DWORDs and four TLP prefix-log DWORDs.

The `BIFPLR1_2` ESM family describes Enhanced Speed Mode capability and control. `PCIE_ESM_CAP_LIST`, headers, status, and control fields cover capability-list metadata, entering ESM, determining width, current speed, link equality with the data-link layer, block type, negotiated ESM data rate, and directed speed change. `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7` expose bitmap-style support for decimal data-rate bands from 8.0 GT/s through 28.0 GT/s. The chunk then closes the `BIFPLR1_2` high-speed link tail with 16 GT/s and 32 GT/s link capability/control/status fields for equalization bypass, no-equalization-needed indication, modified TS usage, precoding state, enhanced link behavior control, current modified TS usage, and equalization phase completion status.

The `BIFPLR2_2` address block begins a root-port or bridge-like PCI configuration space. It covers identity and bridge-routing metadata: vendor/device ID, command bits for I/O, memory, bus mastering, parity, SERR, fast back-to-back, and interrupt disable; status bits for error and capability-list state; revision and class-code bytes; cache line, latency, header type, BIST, primary/secondary/subordinate bus numbering, I/O and memory windows, prefetchable windows and upper DWORDs, capability pointer, interrupt line/pin, secondary status, and extended bridge control.

The `BIFPLR2_2` PM and PCIe capability families describe power state and link/device policy. PM fields include capability ID/version/next pointer, D1/D2 support, PME support, D-state, no-soft-reset, PME enable/status, data select/scale, bus power enable, and PMI data. PCIe capability fields include port type, slot implementation, interrupt message number, max payload, phantom functions, extended tags, L0s/L1 latency, role-based error reporting, captured slot power limits, FLR, completion timeout support/control, ARI, AtomicOp, ID-based ordering, LTR, OBFF, ten-bit tags, emergency power reduction, end-to-end TLP prefix support and blocking, link speed/width, ASPM, read completion boundary, link disable/retrain/common-clock, extended sync, hardware autonomous width disable, bandwidth interrupt enables/status, target link speed, compliance/de-emphasis controls, transmit margin, equalization completion and phase success bits, lower SKP ordered-set support, DRS, and 32 GT/s related link bits.

The `BIFPLR2_2` interrupt, vendor, VC, and identity capability groups include MSI address/data/control fields, MSI-map capability/address fields, SSID capability/subsystem IDs, vendor-specific enhanced capability headers/data, virtual-channel port capabilities/control/status, VC0 and VC1 resource capabilities, arbitration control, traffic-class maps, VC enable/ID, negotiation-pending status, and device serial number DWORDs.

The AER and secondary PCIe capability groups are broad. They define uncorrectable error status/mask/severity for data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress block, TLP prefix block, and poisoned TLP egress block. Correctable status/mask covers receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, correctable internal error, and header-log overflow. AER capability/control fields include first error pointer, ECRC generation/check capability/enables, multi-header recording, and TLP prefix log presence. The same area defines header logs, root error command/status, error source IDs, TLP prefix logs, Link Control 3, lane error status, and lane 0-15 equalization control fields for downstream/upstream TX presets and RX preset hints.

The ACS, multicast, L1 PM substate, DPC, and RP PIO families expose isolation, routing, power, and containment policy. ACS capability/control fields include source validation, translation blocking, P2P request and completion redirects, upstream forwarding, P2P egress control, direct-translated P2P support/control, and egress vector support. Multicast fields define group count, max group, window size, multicast enablement, ECRC regeneration, multicast base address, receive/block-all vectors, untranslated blocking, and overlay BAR values. L1 PM substate fields describe L1.1/L1.2 support and enablement, common-mode restore time, T_POWER_ON scale/value, ASPM and PCI-PM L1.2 controls, and LTR threshold value/scale. DPC and RP PIO repeat the containment and PIO logging pattern described for `BIFPLR1_2`.

The chunk ends in the `BIFPLR2_2` ESM capability range. It defines ESM capability-list/header/status/control fields plus `PCIE_ESM_CAP_1` through the beginning of `PCIE_ESM_CAP_5`. The visible ESM bitmap entries cover 8.0 GT/s through 18.9 GT/s before the next chunk continues the remaining `PCIE_ESM_CAP_5` masks and later ESM/link families.

## Control Flow

This header has no local control flow. Its runtime effect is compile-time substitution:

1. AMDGPU code includes `nbio_7_7_0_sh_mask.h`.
2. A caller selects a matching register address from `nbio_7_7_0_offset.h` or related generated NBIO address metadata.
3. The caller reads a hardware register or PCIe configuration register using AMDGPU access helpers, then applies the `*_MASK` and `*__SHIFT` constants to extract fields, or composes a new value for a write.

Actual sequencing is performed by surrounding AMDGPU, PCI core, firmware, and hardware state machines. The field names in this chunk point at asynchronous operations such as PCIe enumeration, bridge window routing, MSI programming, link training and retraining, lane equalization, 16/32 GT/s link behavior, ESM entry and directed speed changes, AER capture/reporting/clearing, DPC containment, RP PIO logging, ACS isolation, multicast routing, virtual-channel negotiation, L1 PM substate transitions, PME signaling, suspend/resume restoration, and reset/FLR recovery.

## State And Persistence Behavior

The header owns no memory and persists no software state. It describes hardware-visible state in NBIO/PCIe configuration registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, function-level reset, power-state transitions, firmware or BIOS initialization, suspend/resume restore, driver reload, and explicit register writes.

State represented by this chunk includes conventional PCI identity and command/status bits, bridge bus numbers and resource windows, PM capability state, PCIe device/link/slot/root capability state, MSI routing fields, subsystem IDs, MSI-map and vendor-specific capability payloads, virtual-channel resource maps, serial number values, AER status/masks/severity/logs, root error status, secondary PCIe lane equalization controls, ACS isolation controls, multicast windows and masks, L1 PM substate controls and thresholds, DPC status/control, RP PIO status/logs, ESM status/control/capability bitmaps, and 16/32 GT/s link-control/status fields.

Many of these fields are dynamic or side-effect sensitive rather than ordinary persistent configuration. Examples include AER correctable/uncorrectable status, root error status, header and TLP prefix logs, DPC trigger and busy status, RP PIO first error pointers, link training and equalization status, bandwidth management/status bits, slot/hotplug status, PME status, MSI pending state, multicast/VC negotiation status, ESM status, and directed speed-change controls. The shift/mask definitions alone do not say whether a bit is read-only, write-one-to-clear, self-clearing, clear-on-read, reserved, sticky across reset, or firmware-owned.

## Dependencies And Integration Points

This generated header depends on AMD's NBIO 7.7.0 register database staying synchronized across companion files:

- `nbio_7_7_0_offset.h` supplies matching `regBIFPLR...` addresses and base indices for names in this chunk.
- Other generated NBIO headers, including default and SMN variants where present, provide reset values or alternate access-path metadata.
- AMDGPU register and bitfield helpers provide token-pasting, masking, shifting, MMIO, PCIe config, and SMN access selected by the call site.

Runtime integration is with AMDGPU NBIO initialization and PCIe-facing driver paths: GPU discovery, PCI bridge/root-port configuration, BAR and bus-window programming, interrupt setup through MSI, power management, ASPM/L1 substate policy, suspend/resume, GPU reset and FLR, AER/error-reporting diagnostics, DPC containment handling, ACS/IOMMU and peer-to-peer behavior, virtual-channel setup, multicast support, link-speed policy, 16/32 GT/s equalization, ESM support, and debug tooling that decodes PCIe register dumps.

The semantic dependencies are the PCI and PCI Express specifications plus AMD-specific NBIO/ESM definitions. This file names the fields but does not define policy, legal programming sequences, timing, or side effects.

## Risks And Edge Cases

- Generated-data drift can compile cleanly while decoding or programming the wrong hardware bit. In this area that could break PCI enumeration, bridge windows, interrupts, AER/DPC reporting, ACS isolation, L1 PM substates, ESM, or high-speed link training.
- The chunk begins after the `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL` comment and shift definitions; only the final masks for that register are visible here. It ends in `BIFPLR2_2_PCIE_ESM_CAP_5`; the remainder of that register family is owned by the next chunk.
- Similar repeated families exist across `BIFPLR1_2` and `BIFPLR2_2`. Names are intentionally parallel, but root-port instances, offsets, feature presence, and active lanes can differ.
- AER, DPC, RP PIO, PME, slot, and link-status fields may be latched, write-one-to-clear, or otherwise side-effectful. Generic read-modify-write can lose diagnostic evidence or fail to clear an interrupt source.
- Link control, target speed, retrain, equalization, 16/32 GT/s behavior, directed speed change, and ESM controls are sequencing-sensitive and can disrupt PCIe connectivity until reset.
- ACS, multicast, VC, bridge-window, and peer-to-peer related fields affect isolation and routing. Incorrect masks can produce subtle IOMMU, passthrough, P2P, or virtualization failures.
- MSI and MSI-map fields are interrupt-delivery critical. Field-width or shift errors can cause lost interrupts, interrupt storms, or vector misattribution.
- Full-width fields such as TLP/header logs, prefix logs, serial-number DWORDs, vendor-specific payloads, MSI address fields, and multicast/overlay values look mechanically simple but may have alignment, ownership, or capture semantics outside this header.
- High-bit masks with `L` suffixes rely on callers using the established AMDGPU register-value types and helpers; ad hoc signed arithmetic or truncation could mis-handle 32-bit fields.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` and this generated header. Missing, renamed, or malformed macros should surface as compile failures in NBIO, PCIe, interrupt, reset, or power-management code.
- Mechanically compare every `__SHIFT` and `_MASK` in lines 123213-125593 against AMD's authoritative NBIO 7.7.0 register source.
- Cross-check `BIFPLR1_2_*` and `BIFPLR2_2_*` register groups in this slice against `nbio_7_7_0_offset.h` so every field layout maps to the intended register address and base index.
- Run static sanity checks: masks align with shifts, fields in a register do not overlap unexpectedly, full-width data/log fields use `0xFFFFFFFFL`, lane 0-15 equalization groups remain structurally consistent, and repeated DPC/RP PIO/AER/ESM families match the spec.
- Decode known-good NBIO 7.7.0 PCIe register dumps with these masks and compare against `lspci -vvxxx`, AMD reference tooling, or hardware documentation for command/status, bridge windows, PM state, MSI, VC, AER, ACS, L1 PM, DPC, RP PIO, ESM, and link status fields.
- On supported hardware, exercise PCIe enumeration, BAR/resource assignment, bridge-window routing, MSI delivery, suspend/resume, FLR/GPU reset, D-state transitions, ASPM/L1.1/L1.2 transitions, link retraining, 16/32 GT/s equalization, and ESM/direct speed-change paths.
- Exercise error paths where available: AER correctable/uncorrectable capture, header/TLP-prefix logging, root error status/source IDs, DPC trigger/status, RP PIO status/logging, poisoned TLP egress blocking, ACS controls, multicast routing, and VC negotiation.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-003310`. The final per-file research should merge it with neighboring chunks for complete `nbio_7_7_0_sh_mask.h` coverage. The previous chunk owns the start of `BIFPLR1_2_PCIE_L1_PM_SUB_CNTL`; the next chunk owns the remainder of `BIFPLR2_2_PCIE_ESM_CAP_5` and subsequent `BIFPLR2_2` high-speed link families.
