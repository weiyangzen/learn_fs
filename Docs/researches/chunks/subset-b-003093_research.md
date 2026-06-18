# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 61423-63822

## Scope

This chunk covers generated AMD NBIO 7.0 PCIe configuration-space shift and mask macros. It starts in the middle of the `BIFPLR4_1_PCIE_LANE_7_EQUALIZATION_CNTL` field set, continues through the tail of the `BIFPLR4_1` PCIe root-port enhanced capabilities, then enters `addressBlock: nbio_pcie0_bifplr5_cfgdecp` and defines most of the `BIFPLR5_1` PCI/PCIe bridge configuration header and capability field masks. The range contains 2,173 `#define` entries across 225 register records.

This file section is data only. It defines preprocessor constants for register bit positions and masks; it has no C functions, structs, variables, runtime storage, or executable control flow.

## Purpose

The chunk supplies the bit-level ABI between AMDGPU NBIO code and NBIO 7.0 PCIe hardware registers. Each field is represented using the standard generated register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate, clear, or compose the field.

The matching `nbio_7_0_offset.h` and `nbio_7_0_smn.h` headers provide register addresses and SMN/PCIe access paths; this header provides the bit layout consumed by helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `RREG32_PCIE`.

## Important Macro Families

### BIFPLR4 PCIe Capability Tail

The first part of the chunk finishes the `BIFPLR4_1` PCIe port capability area:

- Lane equalization control for lanes 7 through 15, with downstream/upstream TX presets and RX preset hints. The adjacent previous chunk contains lanes 0 through part of lane 7.
- ACS enhanced capability fields: capability-list header, supported access-control services, and enable bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, and direct translated peer-to-peer.
- Multicast capability fields: maximum group count, ECRC regeneration support, enable/group count, base address, receive vectors, block-all vectors, untranslated-block vectors, and overlay BAR fields.
- L1 PM Substates capability/control fields: PCI-PM and ASPM L1.1/L1.2 support/enables, common-mode restore time, LTR L1.2 threshold value/scale, and T_POWER_ON value/scale.
- Downstream Port Containment fields: DPC capability, trigger/completion control, interrupt enable/status, poisoned TLP egress blocking, software trigger, root-port PIO log size, busy/status, and error source ID.
- Root Port PIO status/mask/severity/system-error/exception fields for config, I/O, and memory unsupported-request completions, completer-abort completions, and completion timeouts.
- Root-port TLP header, implementation-specific, and prefix log registers.
- ESM capability fields: capability-list and vendor header registers, minimum time in electrical idle, ESM enable/control, and supported rate bitmaps from 8.0 GT/s through 28.0 GT/s across `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`.

The `BIFPLR4_1_PCIE_ESM_CTRL` fields are especially relevant to link-speed reporting: `ESM_GEN_3_DATA_RATE`, `ESM_GEN_4_DATA_RATE`, and `ESM_ENABLED` encode alternate PCIe speed values when ESM is active.

### BIFPLR5 PCI/PCIe Bridge Header

At line 62246 the chunk switches to `nbio_pcie0_bifplr5_cfgdecp`. The first `BIFPLR5_1` groups mirror a PCI-to-PCI bridge configuration header:

- Identity/classification: vendor ID, device ID, revision ID, programming interface, subclass, base class, header type/device type, BIST, cache line size, and latency timer.
- Command/status: I/O and memory access enables, bus mastering, special cycles, memory-write-invalidate, parity/SERR controls, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort, system-error, parity-error, and DEVSEL timing fields.
- Bus/window registers: primary/secondary/subordinate bus numbers, secondary latency timer, I/O base/limit and high halves, memory base/limit, prefetchable memory base/limit and upper halves.
- Interrupt and bridge control: capability pointer, interrupt line/pin, parity/SERR/ISA/VGA/master-abort/secondary-bus-reset/fast-B2B bridge controls, and an extended I/O port 0x80 enable field.

These definitions model what the host PCI core and AMDGPU bridge-management paths see when reading or programming the NBIO root-port bridge function.

### Power Management, MSI, SSID, and Vendor Capabilities

The chunk defines conventional PCI capability records for `BIFPLR5_1`:

- PMI capability and status/control: version, PME clock/support, device-specific init, auxiliary current, D1/D2 support, PME support, power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.
- MSI capability: capability header, MSI enable, multiple-message capability/enable, 64-bit support, per-vector masking capability, message address low/high, and message data for 32-bit and 64-bit forms.
- SSID capability: subsystem vendor ID and subsystem ID.
- MSI map capability: enable/fixed/capability type and low/high mapping address fields.
- Vendor-specific enhanced capability: enhanced-capability header plus VSEC ID, revision, length, and two scratch registers.

These masks are consumed indirectly by PCIe/NBIO initialization, diagnostics, and any code that needs to decode or emulate the NBIO bridge capability space.

### PCIe Device, Link, Slot, Root, and Secondary Capability Fields

The `BIFPLR5_1_PCIE_*` definitions cover the core PCI Express capability and several enhanced capabilities:

- PCIe capability header and capability fields: version, device type, slot implemented, and interrupt message number.
- Device capability/control/status: max payload support/size, phantom functions, extended tag, L0s/L1 acceptable latency, role-based error reporting, captured slot power limit/scale, FLR capability, correctable/nonfatal/fatal/unsupported-request reporting enables, relaxed ordering, no-snoop, max read request size, bridge config retry, and pending/error status bits.
- Link capability/control/status: speed, width, PM support, exit latencies, clock power management, surprise-down/DL-active/link bandwidth notification support, ASPM optionality, port number, PM control, retrain/disable/common-clock/extended-sync/autonomous width and bandwidth interrupt controls, current speed/width, training, slot clock config, data-link active, and bandwidth status.
- Slot capability/control/status: attention/power/MRL/presence/hotplug/interlock fields, slot power limit and scale, indicator/power-controller controls, command-completed and DL-state-change interrupts/status.
- Root capability/control/status: SERR enables, PM interrupt enable, CRS software visibility, PME requestor/status/pending.
- PCIe 2.0+ secondary fields: completion-timeout, ARI, atomic operation, IDO, LTR, OBFF, end-to-end TLP prefix, target link speed, compliance and equalization controls/status, supported link speeds, lane error status, and link control 3 equalization request bits.

Lane equalization is fully represented for BIFPLR5 lanes 0 through 15, using the same four fields per lane: downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint.

### Virtual Channel, Serial Number, AER, and Error Reporting

The BIFPLR5 enhanced capability area also includes:

- Virtual Channel capability/control/status for port VC state and VC0/VC1 resource capabilities, controls, traffic-class mapping, arbitration, VC ID, enable, and negotiation-pending status.
- Device serial number low/high dwords.
- Advanced Error Reporting capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, TLP prefix logs, root error command/status, and error source ID.
- DPC and Root Port PIO blocks matching the BIFPLR4 definitions, including trigger controls/status, DPC source ID, PIO masks/severity/system-error/exception bits, and header/prefix logs.

The error-field macros are risk-sensitive because status, mask, severity, and reporting-command registers share similar field names but different semantics. For example, a `_STATUS` bit records an event, a `_MASK` bit suppresses reporting, and a `_SEVERITY` bit changes fatal/nonfatal classification.

### ACS, Multicast, L1 PM Substates, and ESM for BIFPLR5

The BIFPLR5 tail repeats the ACS, multicast, L1 PM substates, DPC/RP-PIO, and ESM capability families:

- ACS capability/control mirrors source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, and direct translated peer-to-peer fields.
- Multicast mirrors group count, enable, address, receive, block, untranslated-block, and overlay BAR fields.
- L1 PM Substates mirror L1.1/L1.2 PCI-PM and ASPM support/enables plus restore time, LTR threshold, and power-on timing fields.
- ESM capability/header/status/control and supported-rate bitmaps are present through `BIFPLR5_1_PCIE_ESM_CAP_3` in this chunk; the range ends before the masks for the later ESM capability registers are complete.

## Control Flow and State Behavior

There is no software control flow in this header. Its effect is compile-time: included C files expand these constants into reads, writes, field extraction, and field composition for 32-bit MMIO/PCIe register values.

The persistent state described by this chunk lives in hardware configuration registers, not in the header. Some fields are durable configuration, such as command register enables, bridge windows, link controls, ACS controls, VC resource controls, multicast tables, L1 PM controls, MSI programming, and ESM enable/rate fields. Others are hardware status or sticky error state, such as PCI status bits, device/link/slot/root status, AER status, DPC status, root-port PIO status, lane error status, and TLP header/prefix logs.

Several fields are action-like controls or event clear/reporting knobs. Examples include link retrain, secondary bus reset, DPC software trigger, DPC interrupt enable/status, AER root error command, slot command completed interrupt enable/status, and L1 PM state enables. Correct sequencing, polling, and clearing rules are enforced by the owning driver paths and PCIe hardware specification; the masks themselves only encode bit placement.

## Dependencies and Integration Points

Direct dependencies are the generated NBIO register header set:

- `nbio_7_0_offset.h` supplies the register identifiers and offsets corresponding to these field names.
- `nbio_7_0_default.h` supplies generated reset/default values where available.
- `nbio_7_0_smn.h` supplies SMN/PCIe address constants used by `RREG32_PCIE`/`WREG32_PCIE` paths.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, which includes this header and uses NBIO field masks with SOC15 register helpers for doorbells, HDP remapping, memory-controller access, interrupt control, clock gating, and PCIe/NBIO management.
- `drivers/gpu/drm/amd/amdgpu/soc15.c`, which includes this header as part of SOC15 ASIC bring-up, reset, PCIe, and interrupt initialization support.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which includes the NBIO 7.0 default/offset/mask headers for SMU10 power-management code.
- SMU PCIe link-speed paths in `arcturus_ppt.c`, `aldebaran_ppt.c`, and `smu_v13_0_6_ppt.c` read `smnPCIE_ESM_CTRL` and manually decode the same bit layout represented here: bit 15 is ESM enabled and bits 8:14 carry the Gen4 ESM data rate offset. Those call sites currently use literal shifts/masks instead of these generated `PCIE_ESM_CTRL` field names.
- Linux PCI/PCIe infrastructure indirectly depends on equivalent semantics when enumerating or configuring the AMD root-port bridge: command/status, bridge windows, MSI, PM, PCIe device/link/slot/root capabilities, AER, ACS, DPC, VC, and L1 PM registers follow standard PCIe capability layouts even though this generated header is AMD-internal.

## Risks

- Bitfield drift can cause severe PCIe failures. A wrong shift or mask can enable the wrong command bit, misprogram bridge address windows, corrupt link training/equalization controls, mask real AER/DPC errors, or misreport link speed/state.
- Repeated capability families are mechanically fragile. BIFPLR4 and BIFPLR5 share many similarly named ACS, MC, L1 PM, DPC, RP-PIO, ESM, and lane-equalization definitions, but they refer to different port instances.
- Status, mask, severity, and control registers are easy to confuse. AER and RP-PIO fields reuse error names across `_STATUS`, `_MASK`, `_SEVERITY`, `_SYSERROR`, and `_EXCEPTION` registers with distinct behavior.
- Power-management and link-management fields interact with firmware and the PCIe link partner. Incorrect L1 substates, target link speed, equalization, retrain, clock power management, or ESM programming can produce performance loss, link instability, or suspend/resume failures.
- ACS and multicast controls affect transaction routing and isolation. Incorrect peer-to-peer redirect, translation blocking, egress control, or multicast block/receive vectors can break DMA routing or isolation assumptions.
- The chunk boundaries split complete definitions: it starts after part of lane 7 equalization has already been defined and ends inside the BIFPLR5 ESM capability bitmap family. The final merged document should connect adjacent chunks for complete lane and ESM coverage.

## Test and Validation Signals

Useful validation signals are build coverage plus hardware/PCIe integration tests:

- Compile AMDGPU and SMU code that includes `nbio_7_0_sh_mask.h`; missing or renamed generated fields should fail at build time in `nbio_v7_0.c`, `soc15.c`, and SMU include users.
- PCI enumeration should show stable bridge vendor/device/class, command/status, bus numbers, bridge windows, MSI, PM, PCIe, AER, ACS, DPC, VC, serial-number, and L1 PM capabilities.
- Link-speed and link-width tests should cover normal PCIe link status plus ESM-enabled reporting paths where `PCIE_ESM_CTRL` overrides conventional speed decoding.
- Suspend/resume and runtime power tests should exercise L1 PM Substates, PME, clock power management, link retrain, and DPC/AER status preservation or clearing.
- Error-injection or platform AER tests should verify uncorrectable/correctable error status, masks, severity, root error command/status, source IDs, header logs, TLP prefix logs, DPC trigger/status, and RP-PIO status/mask/severity behavior.
- SR-IOV or peer-to-peer DMA validation should cover ACS controls, multicast fields, egress/block vectors, and transaction-routing behavior when supported by the platform.
- PCIe compliance or signal-integrity tests should exercise lane equalization presets/hints, lane error status, link control 2/3, and equalization status fields for all BIFPLR5 lanes.

## Unresolved Cross-Chunk References

This chunk begins after the `BIFPLR4_1_PCIE_LANE_7_EQUALIZATION_CNTL` comment and several lane-7 shift definitions, so the adjacent previous chunk owns the beginning of that register group. This chunk ends after the shift definitions and first mask for `BIFPLR5_1_PCIE_ESM_CAP_3`, before the rest of its masks and the following ESM capability registers. The merge/reconciliation lane should stitch those boundaries to produce a complete per-file report.
