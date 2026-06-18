# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 61873-64306

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, locks, allocation paths, or direct register reads/writes in this range.

The slice starts at the final `PSWUSCFG0_1_LINK_STATUS` mask bit, then covers most of the `PSWUSCFG0_1` PCIe capability and extended-capability field layout. It includes PCIe Device/Link Capability 2, MSI, subsystem ID, vendor-specific, virtual channel, AER, secondary PCIe, 8 GT/s lane equalization, ACS, multicast, LTR, ARI, data-link feature, 16 GT/s PHY, lane margining, and 32 GT/s PHY fields. It then switches to `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and defines the beginning of the `BIF_CFG_DEV0_RC1` root-complex PCI configuration layout from identity/header fields through ACS capability. The chunk stops at the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` comment; its control-field definitions are outside this work item.

Although this path sits under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions for NBIO 4.3.0 PCIe configuration-space and PCIe extended-capability registers. Each hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update that field.

The matching address constants live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`. Runtime AMDGPU code combines offsets from that file with these masks through register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

## Important Macro Families

The opening `PSWUSCFG0_1` PCIe capability portion describes PCIe Device/Link Capability 2, Control 2, and Status 2 fields. Important fields include completion-timeout ranges and disable controls, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, TLP prefix support/blocking, emergency power reduction, supported link speeds, crosslink support, SKP ordered set support, downstream presence, DRS, compliance entry, transmit margin, de-emphasis, 8 GT/s equalization status, and autonomous link bandwidth status.

The `PSWUSCFG0_1` MSI and identity capability section defines capability-list linkage, MSI enable/multiple-message/64-bit/per-vector-mask/extended-data controls, MSI address/data fields, and subsystem vendor/device IDs. The two `PCIE_VENDOR_SPECIFIC` scratch dwords expose full 32-bit payload masks under a vendor-specific extended capability.

The `PSWUSCFG0_1` virtual-channel section covers the VC enhanced-capability header, port VC capability/control/status, and VC0/VC1 resource capability/control/status fields. These masks describe extended VC counts, arbitration table sizes and offsets, TC-to-VC maps, load/select controls, VC enable bits, negotiation-pending status, and max time slots.

The `PSWUSCFG0_1` AER section defines advanced error reporting capability list fields, uncorrectable status/mask/severity bits, correctable status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered uncorrectable errors include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. Correctable fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, correctable internal error, and header-log overflow.

The `PSWUSCFG0_1` link-training and isolation capabilities include secondary PCIe link control 3, lane error status, per-lane 8 GT/s equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/blocking registers, LTR capability, ARI capability/control, and data-link feature capability/status. These masks are relevant to link equalization, peer-to-peer routing restrictions, multicast routing, latency tolerance reporting, ARI function-group behavior, and DLF exchange.

The `PSWUSCFG0_1` high-speed PHY capability sections cover 16 GT/s and 32 GT/s link capabilities. The 16 GT/s block contains equalization bypass, modified TS, transmitter precoding, DRS, retimer presence, control/status, parity mismatch status for local/RTM1/RTM2 paths, and per-lane downstream/upstream TX presets for lanes 0 through 15. The 32 GT/s block similarly describes highest-rate equalization bypass, no-equalization-needed support/disable, modified TS modes, 32 GT/s equalization phase status, enhanced link behavior status, transmitter precoding state/request, and per-lane TX preset fields.

The `PSWUSCFG0_1` margining block defines the PCIe margining enhanced-capability header, port capability/status, and per-lane control/status pairs for lanes 0 through 15. Each lane uses fields for receiver number, margin type, usage model, and margin payload, mirrored by matching status fields.

After the `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` marker, the `BIF_CFG_DEV0_RC1` block defines a root-complex PCI-to-PCI bridge configuration image. It starts with vendor/device ID, command/status, class code, cache-line/latency/header/BIST, BARs, secondary/subordinate bus numbering, I/O and memory base/limit windows, prefetchable base/limit upper halves, capability pointer, ROM base, interrupt line/pin, and power-management capability/status/control.

The `BIF_CFG_DEV0_RC1` PCIe capability portion includes device, link, and slot capability/control/status fields, plus Device/Link/Slot Capability 2 and Control 2/Status 2. Important fields include payload and read-request sizing, relaxed ordering, no-snoop, extended tag, FLR, link speed/width, ASPM and clock policy, retrain/link-disable controls, slot power/indicator/hotplug fields, completion timeout, ARI forwarding, atomic operations, LTR, OBFF, emergency power reduction, 10-bit tags, TLP prefix blocking, crosslink/SKP/DRS support, and 8 GT/s equalization status.

The `BIF_CFG_DEV0_RC1` MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, lane equalization, and ACS sections mirror many of the `PSWUSCFG0_1` concepts for the RC1 configuration space. The chunk fully covers RC1 AER status/mask/severity/log fields, lane 0 through lane 15 8 GT/s equalization controls, and ACS capability bits. It does not include the actual RC1 ACS control field definitions because the assigned range ends immediately after the `PCIE_ACS_CNTL` comment.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU code selects a register offset from `nbio_4_3_0_offset.h`.
2. It reads a PCIe or SOC15 register value through the AMD register access layer.
3. It extracts or composes a field using these `__SHIFT` and `_MASK` macros directly or through `REG_GET_FIELD` and `REG_SET_FIELD`.
4. It writes a control field, decodes capability/status, polls a hardware-owned bit, clears a sticky status, or reports hardware state to PCIe, power-management, display, reset, virtualization, or diagnostics code.

Direct in-tree includes of the NBIO 4.3.0 shift/mask header appear in `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`. Display resource files include the paired offset header for related NBIO addressing.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and extended-capability state owned by the GPU, platform firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU NBIO/SMU code.

The represented state includes capability-list topology, MSI programming, subsystem identity, virtual-channel configuration, AER status/masks/severity/logs, link equalization and lane error status, ACS routing restrictions, multicast address/blocking controls, LTR and ARI capability/control state, data-link feature state, PCIe 4.0/5.0/6.0-era PHY equalization and margining state, bridge resource windows, PM capability state, slot controls, and RC1 link/device/slot state. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some AER or link diagnostic fields may be sticky or write-one-to-clear in the underlying hardware. The generated masks do not encode reset defaults, access permissions, side effects, ordering requirements, or ownership boundaries.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 4.3.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` provides the matching register addresses.
- Any generated NBIO 4.3.0 default-value header, when present in the source tree, must remain aligned with these register and field names.
- AMDGPU register helper macros and accessors provide the actual read/modify/write mechanics.

Integration points include AMDGPU NBIO setup, SMU13 power-management policy, PCIe link training and speed policy, ASPM/LTR/OBFF configuration, MSI interrupt programming, AER diagnostics, ACS and peer-to-peer isolation, multicast routing, bridge resource-window handling, hotplug/slot status, retimer-aware equalization, 16 GT/s and 32 GT/s link tuning, lane margining diagnostics, suspend/resume, runtime power transitions, reset/FLR paths, and platform PCIe enumeration.

The fields overlap generic PCIe concepts that may also be managed by firmware and the Linux PCI core. Consumers must pair the right mask with the right NBIO instance and offset, and must respect whether the PCI core, firmware, AMDGPU, SMU, or hardware owns a particular control or status bit at a given point in time.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts with only the final `PSWUSCFG0_1_LINK_STATUS__LINK_AUTONOMOUS_BW_STATUS_MASK` line and ends at the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` comment before any ACS control shifts or masks.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while decoding or programming the wrong hardware field.
- The file is mechanically generated and heavily repetitive. Lane 0-15 equalization and margining blocks are especially vulnerable to copy/generation drift, lane-number mismatch, or off-by-one field naming.
- PCIe control fields are interoperability-sensitive. Incorrect completion timeout, ARI, atomic-op, IDO, LTR, OBFF, TLP-prefix, ASPM, retrain, link-disable, target-speed, de-emphasis, or equalization programming can cause enumeration failures, DMA ordering bugs, link instability, reset failures, or platform-specific hangs.
- MSI fields carry interrupt-delivery side effects. Width, 64-bit address, extended data, mask, or multiple-message mistakes can cause lost or misrouted interrupts.
- AER status/mask/severity/log fields may be sticky or write-one-to-clear in hardware. Generic read/modify/write use can lose diagnostic evidence or leave errors masked incorrectly.
- ACS and multicast fields affect routing and isolation. Incorrect source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, or multicast blocking can break isolation or peer-to-peer traffic behavior.
- Bridge base/limit, BAR, ROM, bus-number, and prefetchable-window masks affect resource exposure. Wrong masks can confuse PCI enumeration or expose invalid apertures.
- 16 GT/s, 32 GT/s, retimer, parity, and margining fields are signal-integrity sensitive. Incorrect interpretation can hide marginal links or destabilize high-speed link training.
- `PSWUSCFG0_1` and `BIF_CFG_DEV0_RC1` names describe different address blocks. Applying a mask from one family to an offset from the other may still produce plausible bit operations while corrupting unrelated configuration state.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 support enabled; missing, renamed, or duplicate macros should surface in `nbio_v4_3.c`, SMU13 power-management files, or generated-header include paths.
- Compare this field list against `nbio_4_3_0_offset.h` to confirm the `PSWUSCFG0_1` and `BIF_CFG_DEV0_RC1` register names, ordering, and address-block transitions remain synchronized.
- Boot affected hardware and verify PCIe config-space exposure for RC1: vendor/device IDs, bridge windows, PM capability, PCIe capability, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, lane equalization, and ACS capability should decode consistently.
- Exercise PCIe link-speed changes, retraining, suspend/resume, runtime power, ASPM/LTR/OBFF policy, and reset paths while monitoring link width/speed, equalization completion, lane error status, DRS/retimer presence, and autonomous bandwidth status.
- Use MSI-enabled workloads and interrupt-stress tests to catch MSI address/data/mask or multiple-message field drift.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severities, header logs, TLP prefix logs, and first-error pointers.
- Validate ACS, multicast, and peer-to-peer DMA scenarios on systems that expose those features; isolation failures, blocked traffic, or unexpected upstream forwarding can indicate mask or ownership mistakes.
- Run high-speed link diagnostics for 16 GT/s and 32 GT/s-capable platforms, including lane equalization, parity mismatch reporting, transmitter precoding, modified TS state, and lane margining readiness/status.

## Chunk Notes

- Line 61873 is only the final mask from the preceding `PSWUSCFG0_1_LINK_STATUS` block.
- Lines 61874 through the 32 GT/s lane equalization section cover a broad `PSWUSCFG0_1` PCIe endpoint/upstream-switch-style capability map.
- The `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` marker begins the `BIF_CFG_DEV0_RC1` root-complex configuration-space map within this same chunk.
- Line 64306 is only the `BIF_CFG_DEV0_RC1_PCIE_ACS_CNTL` section marker; the ACS control field definitions begin after the assigned range.
