# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 59015-61422

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,169 `#define` field-layout macros and 237 register-family comments across 2,408 source lines. There are no C functions, structs, enums, global variables, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIFPLR3_1_DEVICE_CAP2`, after the `CPL_TIMEOUT_RANGE_SUPPORTED` shift and mask definitions from the previous chunk, and continues through the rest of the `BIFPLR3_1` PCIe root-port/configuration template. It then switches at `addressBlock: nbio_pcie0_bifplr4_cfgdecp` to the parallel `BIFPLR4_1` template, covering its conventional PCI bridge header, PCI PM/PCIe capability, MSI, SSID, MSI mapping, vendor-specific, virtual-channel, device-serial-number, Advanced Error Reporting, secondary PCIe capability, and per-lane equalization definitions through lane 7. The source boundary ends before `BIFPLR4_1_PCIE_LANE_8_EQUALIZATION_CNTL` and later lane definitions.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. For each hardware register or PCI configuration-space word it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes software-visible PCIe bridge/root-port configuration for `BIFPLR3_1` and `BIFPLR4_1`. The represented fields cover PCIe device/link capability and control words, MSI programming, subsystem identity, MSI mapping windows, vendor-specific capability headers, Virtual Channel resources, Device Serial Number, Advanced Error Reporting, secondary PCIe equalization controls, Access Control Services, multicast routing/filtering, L1 PM substates, Downstream Port Containment, Root Port PIO error reporting, and ESM capability/status/control data.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `BIFPLR3_1` continuation starts at PCIe Capability 2 and then covers extended root-port capabilities:

- Device/link capability 2 and control 2 fields expose completion-timeout support/control, ARI forwarding, AtomicOp routing/completion support, ID-based ordering, LTR, OBFF, end-to-end TLP prefix support/blocking, target link speed, compliance entry, autonomous speed disable, de-emphasis, equalization status, and link equalization request status.
- MSI and subsystem identity fields describe capability-list links, MSI enable/multiple-message state, 64-bit MSI support, per-vector masking support, MSI address/data payloads, subsystem vendor/device identifiers, and MSI-map enable/fixed/type/base-address fields.
- Vendor-specific capability fields define PCIe VSEC metadata, VSEC ID/revision/length, and scratch words.
- Virtual Channel fields define capability-list metadata, port VC capability and arbitration-table controls, VC arbitration-table load/status, VC0/VC1 resource capabilities, traffic-class-to-VC mapping, VC IDs, enable bits, and negotiation-pending status.
- Device Serial Number fields expose enhanced-capability metadata and the low/high serial-number dwords.
- Advanced Error Reporting fields define uncorrectable error status/mask/severity bits, correctable error status/mask bits, ECRC generation/check capability and enablement, first-error pointer, multiple-header receive controls, TLP-prefix-log presence, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe fields define link-control-3 equalization trigger and interrupt enablement, lower SKP OS generation enablement, lane error bitmap, and lane 0 through lane 15 equalization controls with downstream/upstream TX presets and RX preset hints.
- ACS fields cover source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, memory target access, and unclaimed-request redirect controls.
- Multicast fields define multicast capability/control, MC address dwords, receive masks, block-all masks, untranslated-block masks, and overlay BAR values.
- L1 PM Substates fields define ASPM/PCI-PM L1.1 and L1.2 support/enables, common-mode restore time, power-on value/scale, T-power-on programming, and clock power-management capability.
- DPC and Root Port PIO fields define DPC capability/control/status, trigger reason/detail, interrupt/message numbers, containment state, error source IDs, PIO status/mask/severity/system-error/exception fields, and PIO header/prefix/impspec logs.
- ESM fields define enhanced capability metadata, ESM header dwords, status/control bits, and capability dwords 1 through 7.

The `BIFPLR4_1` portion repeats the same root-port/bridge configuration pattern from its start through lane 7 equalization:

- Conventional PCI bridge header fields include vendor/device ID, command/status, revision/class codes, cache-line/latency/header/BIST values, secondary/subordinate bus numbers, I/O and memory base/limit windows, prefetchable window upper dwords, capability pointer, interrupt line/pin, IRQ bridge control, and extended bridge control.
- PCI command/status fields describe I/O and memory access enables, bus mastering, parity/SERR response, interrupt disable/status, capability-list presence, DEVSEL timing, target/master abort reporting, and detected parity error.
- PCI PM and PCIe base capability fields describe PM capability metadata, D-state/PME support and state, PCIe device/port type, slot implementation, device/link/slot/root capabilities, controls, and status.
- MSI, SSID, MSI-map, VSEC, Virtual Channel, Device Serial Number, AER, root error, secondary PCIe, link-control-3, lane error, and lane 0 through lane 7 equalization definitions mirror the `BIFPLR3_1` field families above.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. Consumers include the header and combine these shifts/masks with register addresses/defaults from sibling generated NBIO 7.0 headers.

The constants are untyped preprocessor integer literals, generally with an `L` suffix for masks. They encode only field geometry. They do not encode register address, reset value, access width, read/write permission, write-one-to-clear behavior, privilege requirements, ordering constraints, firmware ownership, or side effects. Callers must get those semantics from the hardware specification, companion generated headers, and the AMDGPU register-access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects an NBIO/PCIe register or configuration-space offset from a companion generated address header.
2. The code reads a hardware value, extracts fields with `__SHIFT` and `_MASK` constants, or composes an updated value while preserving unrelated and reserved bits.
3. The decoded value drives PCIe probing, bridge/window setup, interrupt setup, link management, power-management policy, virtualization/isolation policy, error reporting, or diagnostics; composed values program hardware controls.

Fields in this chunk participate in flows such as PCI bridge enumeration, memory and I/O window decode, bus-mastering enablement, MSI programming, PCIe link retraining and equalization checks, LTR/OBFF and L1-substate power management, AER collection/masking/clearing, DPC containment and recovery, ACS isolation, multicast filtering, VC arbitration/resource negotiation, root-port PIO diagnostics, and ESM status/control handling.

## State And Persistence Behavior

The header itself owns no mutable state and persists nothing. It describes hardware-visible state in NBIO PCIe root-port/bridge registers. Persistence is determined by the GPU/NBIO reset domain, PCIe hot/warm/cold reset, link reset, function-level reset where applicable, suspend/resume save-restore, firmware or BIOS programming, hypervisor/PF policy, and explicit AMDGPU writes.

Represented state includes PCI identity/class values, command/status bits, bus-number and aperture windows, interrupt routing fields, PM state and PME indicators, PCIe device/link/slot/root controls and statuses, MSI address/data state, virtual-channel mappings and negotiation status, serial-number dwords, AER status/mask/severity/logs, root error command/status, link equalization presets/status, ACS and multicast policy, L1-substate timing/enables, DPC trigger/status/interrupt state, root-port PIO error logs, and ESM status/control/capability data.

Some fields are static capabilities, some are writable policy, some are live status, and some are sticky or side-effecting command/status bits. Examples include `MEM_ACCESS_EN` and `BUS_MASTER_EN` gating decode/DMA, link retrain/equalization command bits affecting live PCIe link state, MSI enables affecting interrupt delivery, AER/DPC/PIO status and log registers preserving diagnostic evidence, and ACS/multicast/VC fields affecting routing and isolation. The generated masks alone are insufficient to infer persistence or clear semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling headers:

- `nbio_7_0_default.h` provides matching reset/default values such as `smnBIFPLR3_1_*_DEFAULT` and `smnBIFPLR4_1_*_DEFAULT`.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide address metadata for the same NBIO generation where present.
- AMDGPU helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and NBIO/SMN/PCIe configuration access helpers consume these field constants.

Direct include users in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Higher-level integration is through AMDGPU PCIe/NBIO initialization, GPU reset, interrupt setup, power management, virtualization/isolation, link/error handling, and hardware diagnostics.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while making software read, preserve, clear, or write the wrong hardware bit. This is especially risky for command, bridge-window, interrupt, link-control, AER, DPC, ACS, VC, and power-management fields.
- The chunk starts and ends mid-family. The previous chunk is required for the complete `BIFPLR3_1_DEVICE_CAP2` definition, and the next chunk is required for the rest of `BIFPLR4_1` lane equalization and any following extended capabilities.
- Many PCIe status fields are sticky or write-one-to-clear in hardware even though this header only names masks. Treating them as ordinary writable state can lose error evidence or fail to clear a condition.
- Bridge command and aperture fields gate MMIO/I/O decode and bus mastering. Incorrect masks can break PCI probing, expose the wrong address window, or enable DMA at the wrong time.
- MSI address/data/control fields affect interrupt routing. Wrong extraction or update logic can cause lost, repeated, or misrouted interrupts.
- AER, DPC, Root Port PIO, and ESM fields are diagnostic and recovery surfaces. Incorrect handling can hide fatal/nonfatal errors, misidentify sources, or disrupt containment/recovery flows.
- ACS, multicast, and VC controls affect routing, peer-to-peer behavior, isolation, and traffic classes. Incorrect masks can violate IOMMU/hypervisor assumptions or break traffic arbitration.
- L1 PM Substate and LTR/OBFF fields affect link power management. Incorrect values can cause resume latency, link instability, or power-state transition races.
- Per-lane equalization definitions are mechanically repeated. A lane-specific generator mismatch can appear only on certain widths or board topologies, while the chunk boundary can falsely look like an incomplete lane set.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit the register width, masks should not overlap unexpectedly within a register, reserved fields should cover documented gaps, and repeated lane definitions should match except for lane number.
- Cross-check `BIFPLR3_1` and `BIFPLR4_1` register names against sibling default/address headers so every field layout maps to a known register and default value.
- Runtime probe on supported hardware should show stable PCI bridge/root-port enumeration, correct class/capability data, sane bus-number and memory/I/O windows, and expected command-bit transitions.
- Interrupt validation should cover MSI enablement, message address/data programming, masking behavior where supported, and absence of lost or spurious interrupts.
- PCIe link validation should cover negotiated speed/width, link-control-2 target speed handling, link-control-3 equalization triggers, lane error status, and per-lane equalization preset readback across cold boot, warm reset, and resume.
- Error-path validation should use fault injection or observed hardware faults to confirm AER, DPC, Root Port PIO, ESM, header-log, prefix-log, and source-ID fields decode correctly and that diagnostic evidence is not cleared accidentally.
- Power-management tests should verify LTR/OBFF and L1 PM Substate programming across suspend/resume and runtime power transitions, including timeout handling for links that do not converge.
- Virtualization/isolation tests should cover ACS policy, peer-to-peer routing behavior, multicast filters, VC negotiation, and interaction with IOMMU/hypervisor expectations.
