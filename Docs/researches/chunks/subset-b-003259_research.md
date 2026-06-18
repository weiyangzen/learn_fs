# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 1-2454

## Purpose

This chunk is the opening slice of the generated AMD NBIO 7.7.0 register shift/mask header. It contains no executable C logic. Its purpose is to publish preprocessor constants that describe bit positions and pre-shifted masks for NBIO, PCI/PCIe configuration, root-complex, error-reporting, link-training, and lane-margining registers. Driver code pairs these constants with offsets from `nbio_7_7_0_offset.h` and AMDGPU register helpers to extract fields from hardware register reads or to assemble register writes without open-coded magic numbers.

The range starts with the header guard and license, covers the small `nbio_iohub_nb_nbcfg_nb_cfgdec` northbridge config block, then covers all of the `BIF_CFG_DEV0_RC` root-complex config-decode block through lane margining. It then enters the matching `BIF_CFG_DEV1_RC` block and stops mid-register inside `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`. The next chunk must continue that DEV1 AER severity register and the later DEV1 capability map.

## Public Surface In This Chunk

The public surface is 2,146 generated `#define` macros in the requested line range: 1,076 `__SHIFT` constants and 1,069 `_MASK` constants, plus the include guard. The slight mismatch is expected because the chunk ends in the middle of `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`, so its later mask definitions are outside this range.

Macro naming follows the generated register-field convention:

- `NB_*__<FIELD>__SHIFT` and `NB_*__<FIELD>_MASK` for the top-level northbridge config fields.
- `BIF_CFG_DEV0_RC_<REGISTER>__<FIELD>__SHIFT` and `_MASK` for PCI/PCIe root-complex function 0 fields.
- `BIF_CFG_DEV1_RC_<REGISTER>__<FIELD>__SHIFT` and `_MASK` for the parallel root-complex function 1 fields.

There are no structs, enums, functions, inline helpers, global variables, locks, or callbacks in this header slice. The API contract is the exact macro spelling and numeric value, which must remain synchronized with the same ASIC generation's offset header and AMD's generated register database.

## Register Coverage

The initial northbridge block defines masks for vendor/device identification, command/status bits, revision, cache-line and latency timers, header type, adapter/subsystem IDs, and `NBCFG_SCRATCH_4`.

The `BIF_CFG_DEV0_RC` section is broad and complete within this chunk:

- Conventional PCI bridge/root-port config fields: vendor ID, device ID, command, status, revision, class codes, cache line, latency, header/BIST, BARs, bus numbering, I/O and memory windows, prefetchable windows, capability pointer, ROM BAR, interrupt line/pin, bridge control, and extended bridge control.
- Power-management and PCIe capability fields: PM capability/status/control, PCIe capability header, device capability/control/status, link capability/status, slot capability/control/status, root control/capability/status, and PCIe capability 2 fields.
- MSI and identification capabilities: MSI capability list, MSI message control/address/data variants, subsystem ID capability, and MSI mapping capability.
- Vendor-specific and virtual-channel capabilities: PCIe VSEC header and scratch dwords, VC enhanced capability, port VC capability/control/status, and VC0/VC1 resource capability/control/status.
- Device serial number and Advanced Error Reporting: serial-number dwords, AER capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, root error command/status, source IDs, and TLP prefix logs.
- Secondary PCIe, ACS, DLF, 16 GT PHY, and margining capabilities: lane error status, 8 GT per-lane equalization controls for lanes 0-15, ACS capability/control, data-link feature capability/status, 16 GT PHY capability/status/parity and per-lane preset controls, margining capability/status, and margining control/status pairs for lanes 0-15.

The `BIF_CFG_DEV1_RC` section repeats the same root-complex layout for device 1 from conventional PCI fields through MSI, subsystem/MSI-map, VSEC, VC, serial number, and the start of AER. The chunk ends after the shift definitions and the first subset of mask definitions for `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`.

## Field Semantics

Most fields mirror PCI and PCI Express configuration-space semantics. Capability fields advertise supported features; control fields enable policy; status fields report current hardware or sticky event state. Examples include memory and bus-master decode, SERR/parity handling, PME power-state reporting, payload and read-request sizing, relaxed ordering, no-snoop, link speed/width, slot hotplug events, CRS visibility, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, and function readiness.

The AER groups are operationally sensitive. Status bits identify uncorrectable and correctable PCIe errors such as data-link protocol errors, surprise-down, poisoned TLPs, flow-control errors, completion timeout/abort, unexpected completions, receiver overflow, malformed TLPs, ECRC failures, unsupported requests, ACS violations, internal errors, multicast blocked TLPs, atomic egress blocking, TLP prefix blocking, poisoned egress blocking, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal events, and header-log overflow. The companion mask and severity fields control which errors are reported and whether uncorrectable errors are treated as fatal or non-fatal.

The link-training fields are repetitive but high-risk. DEV0 has 8 GT equalization controls per lane, 16 GT equalization status and per-lane transmit presets, retimer/local parity mismatch vectors, and margining command/status fields per lane. The lane-number suffix, speed suffix, and downstream/upstream direction are part of the semantic contract; a wrong constant can target the wrong lane or equalization phase.

The VC and ACS fields affect traffic classes, virtual-channel enablement/negotiation, arbitration table loads, peer-to-peer forwarding/redirection, source validation, translation blocking, and egress control. Those fields are important for DMA isolation, IOMMU-visible topology, multi-function routing, and PCIe fabric behavior.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. NBIO 7.7.0-aware AMDGPU code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. The caller selects a matching `cfg*` offset, usually from the same generated offset header.
3. AMDGPU register helper macros such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT` use the mask/shift constants to read, update, or write individual fields.
4. Hardware, firmware, PCIe core behavior, and surrounding AMDGPU code determine access ordering, side effects, and persistence.

The header stores no software state and persists nothing by itself. Persistent or semi-persistent state lives in NBIO and PCIe configuration registers. Some fields are programmed configuration state that survives until reset, function reset, power transition, link retrain, or explicit reprogramming. Other fields are hardware-updated status, sticky error, pending, log, or write-one-to-clear style bits whose exact behavior is defined outside this header by the PCIe specification and AMD hardware documentation.

## Dependencies And Integration Points

The direct generated-header dependency is `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`; every field macro in this chunk is meaningful only when paired with the matching `cfgNB*`, `cfgBIF_CFG_DEV0_RC_*`, or `cfgBIF_CFG_DEV1_RC_*` offset. The same source tree's direct include site is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both the offset and shift/mask headers and uses the broader NBIO 7.7 generated register set through SOC15 and PCIe-port access helpers.

Important integration domains are:

- AMDGPU NBIO initialization, memory-controller access, HDP flush, doorbell aperture, interrupt, and PCIe-port helper paths in `amdgpu/nbio_v7_7.c`.
- PCI/PCIe configuration-space semantics for bridge/root-complex devices and capability chains.
- PCIe Advanced Error Reporting, MSI, power management, virtual channels, ACS, Data Link Feature, 16 GT PHY, lane equalization, and lane margining.
- Hardware/firmware register ownership rules that are not encoded in the macro names: access width, reset values, read-only/write-only policy, reserved bits, write-one-to-clear status, sticky logs, and sequencing requirements.

The generated macros do not carry type information or validation. Callers must know whether a field belongs to NB config, DEV0 RC config, DEV1 RC config, SOC15 MMIO, indirect PCIe port access, or PCI config space and must keep the offset prefix aligned with the mask prefix.

## Risks And Maintenance Notes

- The range is a generated-header slice, not a complete logical source file. It begins at the file start but ends mid-register at `BIF_CFG_DEV1_RC_PCIE_UNCORR_ERR_SEVERITY`, so local reviewers must not infer that DEV1 AER support is incomplete in the full header.
- DEV0 and DEV1 root-complex blocks intentionally duplicate many register names with only the device number changed. Mixing `BIF_CFG_DEV0_RC_*` masks with `cfgBIF_CFG_DEV1_RC_*` offsets, or the reverse, can silently access the wrong config function.
- Repetitive per-lane fields are easy to mis-edit. Lane number, 8 GT versus 16 GT suffix, downstream/upstream direction, control versus status, and margining payload/status naming are often the only differences across adjacent definitions.
- `*_MASK_MASK` names are valid when the hardware field itself is named `MASK`; generated tooling and manual cleanups must preserve them.
- Full-width masks such as `0xFFFFFFFFL` often represent BARs, serial-number dwords, scratch registers, header/TLP logs, or reserved payloads. They should not be treated as permission to write all bits as ones.
- AER, ACS, VC, MSI, link, and margining fields can affect error reporting, isolation, interrupt delivery, link stability, and fabric routing. A wrong numeric value may compile cleanly but cause subtle hardware misconfiguration.
- The header does not encode reserved-bit preservation or W1C behavior. Read-modify-write sites must use the correct access rules from hardware documentation and surrounding driver helpers.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `amdgpu/nbio_v7_7.c` and any ASIC code paths that include the NBIO 7.7.0 generated headers.
- Cross-header checks that every complete register group in this chunk has a matching `cfgNB*`, `cfgBIF_CFG_DEV0_RC_*`, or `cfgBIF_CFG_DEV1_RC_*` offset in `nbio_7_7_0_offset.h`, with DEV1 checks continuing into the next chunk for the truncated AER severity register.
- Generated-header comparison against AMD's authoritative NBIO 7.7.0 register source, especially for AER status/mask/severity, ACS controls, VC resource controls, link status, 8 GT/16 GT equalization, and margining lane controls.
- Static checks that each mask fits the intended 8-, 16-, or 32-bit register width and that each complete field has the expected `__SHIFT` plus `_MASK` pair.
- Hardware or simulator register dumps that decode DEV0 and DEV1 root-complex config space consistently with PCIe capability-chain expectations and `lspci -vvxxx`-style output.
- PCIe error-injection tests that verify AER status, masks, severity, root error status, source IDs, header logs, and TLP prefix logs decode correctly.
- Link-training and margining validation on NBIO 7.7.0 hardware that exercises 8 GT equalization, 16 GT equalization/parity reporting, and per-lane margining command/status paths.
- Isolation and routing tests for ACS and VC behavior, checking that source validation, peer-to-peer redirection, translation blocking, traffic-class mapping, and VC negotiation behave as decoded by these masks.
