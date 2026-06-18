# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003122`: lines 1-2468, `Docs/researches/chunks/subset-b-003122_research.md`
- `subset-b-003123`: lines 2469-4901, `Docs/researches/chunks/subset-b-003123_research.md`
- `subset-b-003124`: lines 4902-7362, `Docs/researches/chunks/subset-b-003124_research.md`
- `subset-b-003125`: lines 7363-9837, `Docs/researches/chunks/subset-b-003125_research.md`
- `subset-b-003126`: lines 9838-12285, `Docs/researches/chunks/subset-b-003126_research.md`
- `subset-b-003127`: lines 12286-14755, `Docs/researches/chunks/subset-b-003127_research.md`
- `subset-b-003128`: lines 14756-17197, `Docs/researches/chunks/subset-b-003128_research.md`
- `subset-b-003129`: lines 17198-19674, `Docs/researches/chunks/subset-b-003129_research.md`
- `subset-b-003130`: lines 19675-22130, `Docs/researches/chunks/subset-b-003130_research.md`
- `subset-b-003131`: lines 22131-24686, `Docs/researches/chunks/subset-b-003131_research.md`
- `subset-b-003132`: lines 24687-27116, `Docs/researches/chunks/subset-b-003132_research.md`
- `subset-b-003133`: lines 27117-29591, `Docs/researches/chunks/subset-b-003133_research.md`
- `subset-b-003134`: lines 29592-32042, `Docs/researches/chunks/subset-b-003134_research.md`
- `subset-b-003135`: lines 32043-34496, `Docs/researches/chunks/subset-b-003135_research.md`
- `subset-b-003136`: lines 34497-36940, `Docs/researches/chunks/subset-b-003136_research.md`
- `subset-b-003137`: lines 36941-39386, `Docs/researches/chunks/subset-b-003137_research.md`
- `subset-b-003138`: lines 39387-41833, `Docs/researches/chunks/subset-b-003138_research.md`
- `subset-b-003139`: lines 41834-44284, `Docs/researches/chunks/subset-b-003139_research.md`
- `subset-b-003140`: lines 44285-46731, `Docs/researches/chunks/subset-b-003140_research.md`
- `subset-b-003141`: lines 46732-49193, `Docs/researches/chunks/subset-b-003141_research.md`
- `subset-b-003142`: lines 49194-51624, `Docs/researches/chunks/subset-b-003142_research.md`
- `subset-b-003143`: lines 51625-54019, `Docs/researches/chunks/subset-b-003143_research.md`
- `subset-b-003144`: lines 54020-56559, `Docs/researches/chunks/subset-b-003144_research.md`
- `subset-b-003145`: lines 56560-57899, `Docs/researches/chunks/subset-b-003145_research.md`

## Chunk Research

### subset-b-003122: lines 1-2468

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 1-2468

## Scope

This chunk covers the opening portion of the generated NBIO 7.11.0 shift/mask header. It starts with the file license and include guard, then defines bitfield position and mask macros for these address blocks:

- `nbio_iohub_nb_nbcfg_nb_cfgdec`, covering northbridge PCI configuration identity, command/status, subsystem IDs, PCI control, scratch registers, PCI arbitration/power-management, DRAM slot base, and index/data mutex registers.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, covering a full PCIe root-complex/root-port configuration-space view for BIF CFG device 0, including PCI header fields, bridge windows, PM, PCIe, MSI, SSID, MSI-map, vendor-specific, VC, AER, secondary PCIe, ACS, DLF, 16GT PHY, margining, and ready-to-reset capabilities.
- The beginning of `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`, covering the same root-port-style field families for BIF CFG device 1 through the start of VC0 resource control.

The file is generated hardware metadata. This range defines preprocessor constants only: no C functions, structs, variables, storage, or executable control flow are present.

## Purpose

The purpose of this chunk is to provide the bit-level contract between AMDGPU NBIO/BIF driver code and NBIO 7.11.0 PCIe configuration registers. Every meaningful field is represented by a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field in a register value.

The sibling NBIO register-offset header supplies addresses; this `*_sh_mask.h` file supplies field encodings. Driver code normally consumes these constants through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, and SOC/NBIO-specific indexed-register accessors.

## Important Macro Families

### Northbridge PCI Configuration

The opening `NB_*` macros describe the NB PCI configuration header and local control fields. They include:

- Identification and class information: `NB_VENDOR_ID`, `NB_DEVICE_ID`, `NB_SUB_CLASS`, `NB_BASE_CODE`, `NB_HEADER`, and writable mirrors such as `NB_VENDOR_ID_W`, `NB_DEVICE_ID_W`, `NB_HEADER_W`, and `NB_ADAPTER_ID_W`.
- PCI command/status fields: `NB_COMMAND__IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, plus `NB_STATUS` capability-list and abort status bits.
- Subsystem and capability-pointer fields: `NB_ADAPTER_ID` and `NB_CAPABILITIES_PTR`.
- `NB_PCI_CTRL` fields for PME/SERR disable, MMIO enable, and hotplug disable.
- `NBCFG_SCRATCH_0` through `NBCFG_SCRATCH_4`, each exposing a full 32-bit scratch payload.
- `NB_PCI_ARB`, with VGA-hole, PME mode/turnoff/ack status, and PME target fields.
- `NB_DRAM_SLOT1_BASE`, exposing the high DRAM base field.
- `NB_INDEX_DATA_MUTEX0` and `NB_INDEX_DATA_MUTEX1`, with 31-bit mutex values and a high unlock bit.

These definitions are low-level platform/config-space controls rather than runtime graphics state. The mutex fields are particularly important for any indexed NB register access path because they describe hardware coordination bits, not simple software locks.

### BIF Device 0 Root-Port Header and Bridge Windows

The `BIF_CFG_DEV0_RC_*` block begins with conventional PCI configuration-space fields:

- Vendor/device ID, command/status, revision, programming interface, subclass, base class, cache-line, latency, header, BIST, BAR-like base address registers, and capability pointer.
- Bridge routing fields such as primary/secondary/subordinate bus numbers, secondary latency, I/O base/limit, memory base/limit, prefetchable base/limit, upper prefetchable base/limit, high I/O base/limit, ROM base, interrupt line/pin, and bridge control.
- Bridge control fields include parity response, SERR, ISA/VGA enable and VGA decode, master-abort mode, secondary bus reset, fast back-to-back enable, discard timers, and discard timer SERR enable.

These macros encode the root-complex view of PCIe hierarchy management. Incorrect mask usage here can expose the wrong downstream bus range, misprogram memory windows, or incorrectly assert a secondary bus reset.

### Power Management and PCIe Capability

Device 0 PM fields include `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, with PM capability ID/next-pointer, version, PME support, D1/D2 support, power state, PME enable/status, data select/scale, B2/B3 support, bus-power enable, and PMI data.

The base PCIe capability is represented by:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for payload/read-request sizing, error enables/status bits, relaxed ordering, no-snoop, extended tags, phantom functions, FLR capability, auxiliary power, pending transactions, and emergency power reduction detection.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for link speed/width, ASPM/power-management support, common-clock, retrain/disable, width/speed autonomy controls, bandwidth notification interrupts, DRS signaling, current negotiated link state, training, slot clock, and data-link active state.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` for hotplug-related slot power, indicators, MRL/presence/interlock, command completion, and data-link state change fields.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` for PME/error routing, CRS software visibility, and PME requester/status/pending state.

These fields are direct integration points with PCIe link management, hotplug, power management, and error handling. Many status bits are latched hardware state and may have write-one-to-clear behavior defined by hardware/PCIe, so users must not infer semantics from masks alone.

### PCIe Capability 2, Link 2, MSI, and Vendor Capabilities

The chunk continues through PCIe 2.x/3.x style extensions for device 0:

- `DEVICE_CAP2` and `DEVICE_CNTL2` expose completion-timeout ranges/disable, ARI forwarding, atomic operation support/enable, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, and FRS support.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` expose supported link speeds, crosslink support/resolution, lower-SKP ordered-set generation/receive support, RTM presence detection, DRS support, target link speed, compliance mode, speed autonomy disable, de-emphasis, transmit margin, and 8GT equalization phase status.
- Slot 2 registers are present but reserved in this range.
- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data, extended message data, and 64-bit variants encode MSI enablement, multi-message capability/control, 64-bit MSI support, per-vector masking capability, and extended message data support.
- `SSID_CAP_LIST` and `SSID_CAP` encode subsystem vendor/device IDs.
- `MSI_MAP_CAP_LIST` and `MSI_MAP_CAP` encode MSI mapping enable/fixed/type state.
- Vendor-specific enhanced capability list/header plus two scratch registers expose VSEC ID/revision/length metadata and scratch payloads.

These macros are consumed by code that reports capabilities, configures interrupt delivery, or touches PCIe extended capabilities. The MSI address low mask intentionally starts at bit 2, reflecting alignment requirements.

### Virtual Channel and Arbitration

Device 0 VC capability fields include:

- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1`, `PCIE_PORT_VC_CAP_REG2`, `PCIE_PORT_VC_CNTL`, and `PCIE_PORT_VC_STATUS`.
- `PCIE_VC0_RESOURCE_CAP/CNTL/STATUS` and `PCIE_VC1_RESOURCE_CAP/CNTL/STATUS`.

These fields describe extended VC counts, low-priority VC count, reference clock, port/VC arbitration table entry size and offsets, load/select strobes, VC IDs, VC enable, traffic-class-to-VC mapping, maximum time slots, reject-snoop behavior, and negotiation/status bits. Control fields such as `LOAD_VC_ARB_TABLE` and `LOAD_PORT_ARB_TABLE` are command-like bits that should be sequenced with the corresponding status fields.

### Device Serial Number and Advanced Error Reporting

The AER portion for device 0 is extensive:

- `PCIE_DEV_SERIAL_NUM_*` exposes enhanced capability metadata and 64-bit serial number halves.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` identifies the AER extended capability.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover data-link protocol, surprise-down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked fields.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, and correctable internal error bits.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC generation/check capability and enable bits, and multi-header recording controls.
- Header and TLP-prefix logs provide four full 32-bit words each.
- Root error command/status/source-ID registers control and report propagated correctable, nonfatal, and fatal error messages.

This is a major diagnostic and reliability integration point. The status, mask, severity, and log fields must be kept distinct: status reports events, mask controls reporting, severity classifies uncorrectable errors, and header/prefix logs capture transaction context.

### Secondary PCIe, ACS, DLF, 16GT PHY, Margining, and RTR

Device 0 also includes:

- Secondary PCIe capability fields for link control 3, 8GT equalization request interrupt enable, lower SKP generation enable, lane error status, and lane 0-15 8GT equalization controls.
- ACS capability/control fields for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress control vector size.
- Data Link Feature capability/status fields for local and remote DLF support, exchange enable, and remote support validity.
- 16GT PHY capability metadata, reserved 16GT capability/control registers, 16GT equalization phase status, local/RTM parity mismatch status, and lane 0-15 16GT equalization preset fields.
- PCIe margining capability/status plus lane 0-15 margining control/status fields for receiver number, margin type, usage model, and margin payload.
- Ready-to-reset capability metadata and reset/DL-up/FLR/D3hot-to-D0 timing fields with a valid bit.

These definitions are tied to high-speed PCIe training and diagnostics. Lane-indexed fields are highly repetitive by design; the driver must still address the correct lane register because each macro family is lane-specific.

### BIF Device 1 Mirrored Root-Port Definitions

The final part of the assigned range starts `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`. It repeats the same root-port style definitions for BIF CFG device 1:

- PCI header, bridge window, PM, PCIe base capability, device/link/slot/root control and status fields.
- Device/link capability 2 fields, MSI, SSID, MSI-map, vendor-specific enhanced capability, and VC enhanced capability.
- The range ends inside `BIF_CFG_DEV1_RC_PCIE_VC0_RESOURCE_CNTL`, after defining `TC_VC_MAP_TC0`, `TC_VC_MAP_TC1_7`, and `LOAD_PORT_ARB_TABLE` shifts.

The duplication is intentional and encodes separate hardware instances. Code should not mix `DEV0` and `DEV1` masks even when the field layouts currently match, because the register addresses and future generated deltas are instance-specific.

## APIs, Types, and Functions

There are no APIs, types, or functions in this chunk. The usable interface is the macro namespace. Important usage conventions are:

- Register fields are named by `<register>__<field>`.
- Shift constants are raw bit indices.
- Mask constants are integral literals suffixed with `L`.
- Full-width fields use masks such as `0xFFFFFFFFL`; narrow PCI config fields commonly use 8-bit, 16-bit, or packed 32-bit masks.

Consumers should use existing bitfield helpers rather than open-coding shifts and masks. That keeps call sites consistent with the generated AMDGPU register-header convention.

## Control Flow

This file has no runtime control flow. Hardware sequencing is implied by the register fields:

- Link control fields such as retrain, disable, compliance, speed selection, and equalization request bits are consumed by PCIe link-management flows.
- VC arbitration load bits imply write-then-poll sequences against VC status bits.
- AER status/mask/severity/log fields imply error collection and reporting flows.
- MSI address/data/control fields participate in interrupt setup.
- Margining, equalization, DLF, ACS, and RTR fields are capability-driven flows that should be entered only when the corresponding capability bits and hardware generation support the operation.

## State and Persistence

The macros do not store state, but they describe persistent and volatile hardware state:

- PCI identity/class/subsystem fields are mostly configuration identity state.
- Command, bridge-window, power-management, MSI, ACS, VC, and link-control fields are mutable configuration state programmed by firmware, PCI core code, or AMDGPU/NBIO logic.
- Status fields such as link status, slot status, root status, AER status, equalization status, parity mismatch, margining status, and data-link feature status reflect live or latched hardware state.
- Scratch registers and vendor-specific scratch fields expose persistent 32-bit payloads until reset or overwrite.
- Mutex unlock bits and VC load bits are coordination/command fields and should not be treated as ordinary persistent values.

Reset, suspend/resume, FLR, D3hot-to-D0, hotplug, and link retraining can all change the underlying hardware values without any change to this header.

## Dependencies and Integration Points

This chunk depends on:

- The matching NBIO 7.11.0 offset/address header for register addresses.
- AMDGPU register access and bitfield helper macros used throughout the DRM AMD driver.
- PCI/PCIe architectural semantics for config-space fields, PM capabilities, MSI, AER, ACS, VC, hotplug, link training, and margining.
- Firmware/BIOS/SMU/platform initialization that may preprogram parts of NBIO/BIF state before the kernel driver observes it.

Likely integration areas include NBIO initialization, PCIe link and error handling, MSI setup, reset/resume paths, GPU virtualization/root-port handling, debugfs or diagnostics that read AER/link/margining state, and generated-header consumers that include `nbio_7_11_0_sh_mask.h` alongside its offset header.

## Risks

- Instance confusion: `DEV0` and `DEV1` macros look nearly identical in this range, but must be paired with the matching register address block.
- Mask/shift drift: these generated constants are hardware ABI. Hand edits or stale generated output can silently corrupt register programming.
- Status versus control confusion: AER, slot, root, link, VC, margining, and equalization fields mix capability, control, status, mask, and severity registers with similar names.
- Command-like bits: fields such as VC arbitration loads, link retrain, compliance entry, and reset-related controls may trigger hardware actions.
- Reserved fields: several Slot 2 and 16GT capability/control fields are marked reserved; code should not assign policy meaning to them.
- Width/alignment errors: MSI address low starts at bit 2, bus/window fields are packed in nibbles or byte lanes, and serial/log fields are full 32-bit words. Open-coded bit math is easy to get wrong.
- PCIe generation sensitivity: 8GT/16GT equalization and margining fields are meaningful only on hardware and links that support those capabilities.

## Test Signals

Useful validation signals for changes involving this header include:

- Build coverage for AMDGPU code that includes NBIO 7.11.0 generated headers.
- Compile-time failures from missing/renamed macros in NBIO, PCIe, reset, interrupt, or diagnostic code.
- Runtime PCIe enumeration and `lspci -vv` consistency for command/status, bridge windows, PM, MSI, AER, ACS, VC, and link capability/status reporting.
- Link training and resume tests that verify negotiated speed/width, retrain behavior, and D3hot-to-D0/FLR readiness timing.
- MSI interrupt delivery tests after programming MSI control/address/data fields.
- AER injection or error-observation tests that confirm status, mask, severity, root error, source ID, and header-log handling are decoded correctly.
- Hotplug or downstream-presence tests for slot/root status and DL-active fields where supported.
- Static comparison against the authoritative generated register database for NBIO 7.11.0 to detect accidental bitfield drift.

### subset-b-003123: lines 2469-4901

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

### subset-b-003124: lines 4902-7362

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 4902-7362

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIO/NBIF PCI configuration-space registers. The range starts in the tail of the `BIF_CFG_DEV2_RC` root-complex PCIe margining area, then covers most of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block and the beginning of the matching `DEV0_EPF1` block.

The content is hardware metadata, not executable driver code. AMDGPU code pairs these `*_SHIFT` and `*_MASK` macros with register offsets from the companion NBIO 7.11.0 offset header and with common register-field helpers to encode and decode PCIe configuration fields without embedding literal bit positions.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this line range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_*` through `LANE_15_MARGINING_LANE_*`: root-complex receiver margining control/status fields for PCIe lanes 11-15. Each lane repeats receiver number, margin type, usage model, and payload fields.
- `BIF_CFG_DEV2_RC_PCIE_RTR_ENH_CAP_LIST`, `BIF_CFG_DEV2_RC_RTR_DATA1`, and `BIF_CFG_DEV2_RC_RTR_DATA2`: Readiness Time Reporting enhanced capability metadata and timing fields for reset, data-link-up, FLR, D3hot-to-D0, plus a valid bit.
- `BIF_CFG_DEV0_EPF0_*` conventional PCI header fields: vendor/device ID, command/status, revision/class code, cache line, latency, header/BIST, six base address registers, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and legacy min-grant/max-latency fields.
- `BIF_CFG_DEV0_EPF0_PMI_*`: power-management capability list, capability flags, power state, PME enable/status, data select/scale, bus power, and power-management data fields.
- `BIF_CFG_DEV0_EPF0_PCIE_*` core PCIe capability fields: PCIe capability list/header, device capability/control/status, link capability/control/status, PCIe 2.0 device/link capability/control/status fields, completion timeout, ARI/atomic operation support, IDO, LTR, OBFF, emergency power reduction, DRS, equalization, and target link speed controls.
- `BIF_CFG_DEV0_EPF0_MSI*` and `MSIX*`: MSI/MSI-X capability list, message-control bits, 32/64-bit message address/data registers, mask/pending registers, MSI-X table and PBA BAR/index fields.
- `BIF_CFG_DEV0_EPF0_PCIE_VENDOR_SPECIFIC*`, `PCIE_VC*`, and `PCIE_DEV_SERIAL_NUM*`: vendor-specific enhanced capability fields, virtual-channel capabilities/resources/status, and device serial number dwords.
- `BIF_CFG_DEV0_EPF0_PCIE_ADV_ERR_RPT*`: PCIe Advanced Error Reporting capability, including uncorrectable error status/mask/severity, correctable error status/mask, ECRC controls, first error pointer, TLP header logs, and TLP prefix logs.
- `BIF_CFG_DEV0_EPF0_PCIE_BAR*` and `PCIE_VF_RESIZE_BAR*`: resizable BAR capability/control fields for PF BARs and VF BARs, with repeated bar index, total count, current size, and supported-size upper fields.
- `BIF_CFG_DEV0_EPF0_PCIE_PWR_BUDGET*` and `PCIE_DPA*`: power-budgeting and dynamic power allocation capability fields, including data select, base power, scale, PM state/substate, power rail, DPA substate count/control/status, transition latency indicators, and per-substate power allocations 0-7.
- `BIF_CFG_DEV0_EPF0_PCIE_SECONDARY*`, lane equalization, and 16GT PHY capability fields: link control 3, lane error status, 8GT lane equalization controls for lanes 0-15, 16GT equalization status, parity mismatch status, and 16GT lane preset controls for lanes 0-15.
- `BIF_CFG_DEV0_EPF0_PCIE_ACS*`, `ATS*`, `PAGE_REQ*`, `PASID*`, `MC*`, `LTR*`, `ARI*`, and `SRIOV*`: access control services, address translation services, page request interface, PASID, multicast, latency tolerance reporting, ARI, and SR-IOV capability/control/status surfaces.
- `BIF_CFG_DEV0_EPF0_DATA_LINK_FEATURE_*` and `PCIE_MARGINING*`: data-link feature capability/status and PCIe lane margining port/lane control/status for lanes 0-15.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`: GPU IOV vendor-specific enhanced capability list fields, with capability ID/version/next pointer.
- `BIF_CFG_DEV0_EPF1_*`: the start of endpoint function 1's PCI configuration-space mask set. This chunk covers the same conventional PCI header, power-management, PCIe device/link capability/control/status, PCIe 2.0 device/link fields, and stops after `BIF_CFG_DEV0_EPF1_LINK_STATUS2`.

These macros are intended for use through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO register read-write paths. Register address definitions are not in this file; this header only describes field geometry.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is included by C sources at compile time and contributes constants to hardware register read, write, and read-modify-write operations.

The implied hardware flows are:

1. PCI enumeration or driver initialization can read conventional header fields for identity, class code, BAR layout, ROM BAR state, interrupt routing, and capability list traversal for `DEV0_EPF0` and `DEV0_EPF1`.
2. PCI command/status and PCIe device-control fields gate I/O, memory access, bus mastering, interrupt disable, error reporting enables, relaxed ordering, no-snoop, maximum payload size, maximum read request size, and function-level reset initiation.
3. Link capability/control/status fields report and control negotiated speed/width, link training, retraining, common clock, ASPM/clock power management, link bandwidth interrupts, target link speed, compliance entry, de-emphasis, equalization, DRS, crosslink, and downstream component presence.
4. MSI/MSI-X masks define interrupt capability programming surfaces: message count/enable, 64-bit capability, per-vector masking, message address/data, MSI-X table location, and pending-bit-array location.
5. AER fields let driver or firmware code classify PCIe corrected and uncorrected errors, mask selected events, configure severity, enable/check ECRC, and read logged TLP headers/prefixes after errors.
6. Resizable BAR and SR-IOV fields describe how PF and VF address windows, VF counts, VF stride, VF device ID, page sizes, and VF memory-space enable are exposed to PCIe software.
7. ACS, ATS, page request, PASID, ARI, multicast, LTR, data-link feature, DPA, and power-budget fields expose advanced PCIe capabilities that interact with IOMMU, virtualization, power management, and traffic-routing code.
8. Lane equalization and lane margining fields provide per-lane diagnostics and tuning surfaces for 8GT, 16GT, and PCIe receiver margining flows. Software writes lane control fields and reads status/error/parity indicators, but the timing and state machine behavior are in hardware.

The header does not sequence these operations, clear status bits, or enforce PCIe ordering rules. Callers must follow PCIe and ASIC-specific programming requirements when using the generated masks.

## State and Persistence

The header owns no memory, stores no runtime state, performs no I/O, and persists nothing. The represented state lives in NBIO/NBIF hardware registers.

State categories represented here include:

- PCI configuration identity and layout state: IDs, class codes, BARs, ROM BAR, subsystem IDs, capability pointers, interrupt line/pin, MSI/MSI-X table/PBA pointers, and SR-IOV VF BARs.
- PCI command and control policy: memory/bus-master enables, interrupt disable, PME enable/status, power state, error reporting enables, FLR initiation, completion timeout policy, atomic operation controls, IDO, LTR, OBFF, ARI forwarding, VF enable, and VF memory-space enable.
- PCIe link state: supported/current speeds and widths, link training, DL active, target speed, retrain/link-disable controls, common clock, bandwidth notification, compliance controls, equalization completion and phase status, 16GT parity mismatch, and per-lane equalization presets.
- Error reporting state: conventional PCI status bits, PCIe device status, AER corrected/uncorrected status/mask/severity, ECRC and multi-header logging controls, TLP header logs, TLP prefix logs, and lane error status.
- Power and virtualization capability state: power-budget records, DPA controls/status/substate allocations, LTR latency limits, PASID/page request/ATS state, multicast registers, ACS controls, ARI controls, SR-IOV VF counts/offset/stride/page sizes, and data-link feature negotiation.
- Lane diagnostics state: PCIe margining port ready/software-ready bits and per-lane margining control/status payloads for DEV2 root-complex lanes 11-15 and DEV0 EPF0 lanes 0-15.

Retention across GPU reset, PCI reset, FLR, suspend/resume, runtime power transitions, BACO, or hot reset is not specified by this header. Those semantics are defined by NBIO 7.11.0 hardware and by any AMDGPU initialization paths that restore configuration after reset or resume.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_offset.h` for the register offsets matching these register names.
- Other generated ASIC-family headers included by AMDGPU SOC15/NBIO code for register access conventions and related blocks.

Likely integration areas in the AMDGPU tree include:

- NBIO 7.11 setup and low-level register access paths that include generated NBIO masks.
- PCIe and NBIF initialization code that programs device/link capabilities, BAR sizing, power management, MSI/MSI-X, and link controls.
- AMDGPU virtualization/SR-IOV code that uses VF counts, VF stride, VF BARs, ARI, ATS, PASID, page-request, ACS, and VF enable/memory-space fields.
- Error-handling and RAS-adjacent PCIe code that reads PCI status, PCIe device status, AER status/mask/severity, TLP logs, lane error status, and parity/equalization diagnostics.
- Link training, speed-change, equalization, and hardware validation code that consumes 8GT/16GT equalization and margining controls.
- Power-management code that reads or programs PCI PM capability, LTR, DPA, power-budgeting, OBFF, clock power management, and emergency power reduction fields.

Integration is symbol-name based. A caller must pair a field macro from this file with the correct register address macro and with PCIe/NBIO documentation for field value meanings.

## Risks

- Incorrect shifts or masks can silently program the wrong PCIe control bit or misdecode status. In this range, that can affect bus mastering, memory decode, FLR, interrupt masking, link training, power management, AER classification, virtualization, or BAR sizing.
- The header is highly repetitive across lanes, BARs, VF BARs, and endpoint functions. Generator or copy/paste mistakes can be hard to detect if validation covers only lane 0, BAR1, or EPF0.
- Several fields can disrupt device operation when written incorrectly: `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `INITIATE_FLR`, `LINK_DIS`, `RETRAIN_LINK`, `TARGET_LINK_SPEED`, `ENTER_COMPLIANCE`, SR-IOV VF enable/MSE, MSI/MSI-X enable/masks, and AER masks/severity.
- AER status, mask, and severity names are intentionally similar. Mixing them can hide real PCIe faults, over-report benign faults, or misclassify fatal/nonfatal/corrected errors.
- BAR and resizable-BAR masks are full-width or size-encoded. Wrong size/index handling can expose invalid MMIO apertures or break PF/VF address layout.
- SR-IOV, ATS, PASID, page request, ACS, and ARI controls intersect with IOMMU and virtualization security. Misprogramming can break isolation or device assignment.
- Lane equalization and margining fields are per-lane hardware diagnostics. Incorrect lane indexes or payload encoding can make link-quality data misleading or destabilize validation flows.
- This chunk starts mid-register-family: the first `BIF_CFG_DEV2_RC_LANE_11_MARGINING_LANE_CNTL` comment and some context are in the previous chunk. It also ends immediately before `BIF_CFG_DEV0_EPF1_MSI_CAP_LIST`, so EPF1 interrupt and later capability masks are owned by the next chunk.

## Test and Validation Signals

Useful validation signals are generated-header consistency checks plus PCIe hardware coverage:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch missing or malformed macros.
- Mechanically verify that complete registers in lines 4902-7362 have paired `__SHIFT` and `_MASK` definitions, allowing the intentional chunk split at the first DEV2 lane 11 control register and after EPF1 `LINK_STATUS2`.
- Cross-check register names against `nbio_7_11_0_offset.h` so every mask set used by code has a matching address definition.
- Run symmetry checks across repeated families: lane margining lanes 0-15, 8GT and 16GT lane equalization lanes 0-15, BAR1-BAR6, VF resize BAR1-BAR6, and matching EPF0/EPF1 conventional PCIe fields.
- Validate PCIe enumeration and configuration on NBIO 7.11.0 ASICs by confirming vendor/device IDs, class code, BAR sizing, capability traversal, MSI/MSI-X setup, and PCIe link status decode.
- Exercise link speed changes, retraining, equalization status, and margining diagnostics on real hardware or bring-up benches and compare decoded values against PCIe analyzer or platform firmware observations.
- Exercise AER by injecting or observing controlled corrected/nonfatal/fatal events and checking status, masks, severity, ECRC controls, and TLP log decode.
- Validate SR-IOV and IOMMU-related paths by enabling VFs, checking VF counts/stride/BAR/page-size fields, and verifying ATS/PASID/PRI/ACS/ARI behavior under device assignment.
- Run suspend/resume, FLR, hot reset, and runtime power-management coverage to confirm driver initialization restores policy registers and decodes retained status according to hardware expectations.

## Chunk Boundary Notes

The range begins inside the DEV2 root-complex margining register family. The lane 11 control register starts in this chunk, but the prior lane 10 family and the comment for the chunk transition are in the previous work item.

The range ends after `BIF_CFG_DEV0_EPF1_LINK_STATUS2` masks and immediately before `BIF_CFG_DEV0_EPF1_MSI_CAP_LIST`. Merge/reconciliation should combine this with adjacent chunks to produce the final source-file report and avoid treating the boundary as a missing EPF1 MSI section.

### subset-b-003125: lines 7363-9837

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 7363-9837

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11 shift/mask header. It describes bit positions and masks for PCI/PCIe configuration-space registers exposed through NBIF/BIF configuration decoder blocks. The covered range is metadata only: it contains preprocessor constants that let driver code extract or program fields in hardware registers without embedding literal bit offsets.

The line range starts at the tail of `BIF_CFG_DEV0_EPF1_LINK_STATUS2`, continues through the rest of the `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` register field set, then covers most of `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, and finally enters the beginning of `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`. In PCIe terms, the chunk is dominated by endpoint function configuration fields for `DEV0_EPF1` and `DEV0_EPF2`, including MSI/MSI-X, PCIe advanced error reporting, resizable BARs, power-budgeting, dynamic power allocation, lane equalization, ACS/ATS/PASID/ARI, SR-IOV, data-link feature, 16 GT/s PHY capability, lane margining, VF resizable BARs, and readiness-time-reporting registers.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: shifted mask for the field in its register.

The chunk contains 2,118 `#define` entries spanning 350 register names: 1,184 macros under `BIF_CFG_DEV0_EPF1`, 878 under `BIF_CFG_DEV0_EPF2`, and 56 at the start of `BIF_CFG_DEV2_EPF0`.

Major `DEV0_EPF1` register families in this chunk are:

- MSI/MSI-X: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, address/data/extended-data/mask/pending registers, plus `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor/device identity and PCIe capability structures: vendor-specific enhanced capability, device serial number, advanced error reporting, BAR enhanced capability, power budget, DPA, secondary PCIe capability, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, data-link feature, 16 GT/s PHY, margining, VF resizable BAR, and RTR capability blocks.
- AER status and policy fields: uncorrectable status/mask/severity, correctable status/mask, error capability/control, header logs, and TLP prefix logs. These expose completion timeout, unsupported request, ECRC, poisoned TLP, ACS violation, internal error, malformed TLP, receiver overflow, advisory non-fatal, replay timer timeout, bad DLLP/TLP, and related PCIe error classes.
- BAR and VF BAR controls: BAR1 through BAR6 capability/control pairs and VF resizable BAR1 through BAR6 capability/control pairs, with BAR size and resize controls.
- Link training and physical-layer diagnostics: 8 GT/s lane equalization control for lanes 0-15, 16 GT/s lane equalization coefficients for lanes 0-15, local/RTM parity mismatch status, lane error status, link equalization control, and lane margining control/status for lanes 0-15.
- Virtualization and address-translation helpers: ACS capability/control, ATS capability/control, page request control/status/capacity/allocation, PASID capability/control, multicast address/receive/block fields, ARI capability/control, and SR-IOV VF count, stride, offset, device ID, page size, and VF BAR fields.

Major `DEV0_EPF2` register families are similar but shorter in this chunk:

- Standard PCI configuration header: vendor/device IDs, command/status, revision/class code, cache line, latency, header type, BIST, six base address registers, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency.
- Power-management and PCIe base capabilities: vendor capability list, adapter ID write field, PMI capability/status-control, SBRN/FLADJ/DBESL fields, PCIe capability list/capability, device capability/control/status, link capability/control/status, and second-generation device/link capability/control/status registers.
- Interrupt and AER fields: MSI, MSI-X, SATA capability/index/data fields, vendor-specific enhanced capability, advanced error reporting status/mask/severity/log fields, and TLP prefix logs.
- BAR, power, and security/virtualization controls: BAR enhanced capability/control for BAR1-BAR6, power-budgeting, DPA, ACS, PASID, ARI, and RTR data.

The `DEV2_EPF0` block begins at line 9771 and includes only the first standard PCI configuration fields through `BIF_CFG_DEV2_EPF0_LATENCY`. The next chunk continues that endpoint-function block.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is consumed by C preprocessor expansion during compilation. Runtime behavior appears only when AMDGPU or firmware-facing code combines these masks with register-address macros from the matching NBIO 7.11 offset/SMN headers and register access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, or SOC15/NBIO read-modify-write wrappers.

The implied hardware flows are:

1. PCI capability discovery and setup code reads capability-list and enhanced-capability fields to identify MSI, MSI-X, AER, ACS, ATS, PASID, ARI, SR-IOV, DPA, LTR, data-link, 16 GT/s PHY, lane margining, VF BAR, and RTR support.
2. Interrupt setup uses MSI/MSI-X control, address, data, mask, pending, table, and PBA fields to enable message-signaled interrupts and to mask or observe per-vector state.
3. PCIe error handling uses AER status, mask, severity, and log fields to classify correctable versus uncorrectable events, choose which events are masked, and capture header or TLP-prefix context for diagnostics.
4. Link-training and link-health code may inspect link status, equalization, lane error, 16 GT/s parity mismatch, and lane margining registers to diagnose negotiated speed/width issues or physical-layer problems.
5. Address-translation and isolation paths use ACS, ATS, page request, and PASID fields to expose or configure PCIe peer-to-peer isolation, translation request behavior, and process address space identifiers.
6. Virtualization setup uses SR-IOV and VF resizable BAR fields to describe virtual functions, VF BAR sizing, VF stride/offset, supported/system page size, and VF device identity.
7. Power-management and readiness paths use PMI, power-budgeting, DPA, LTR, and RTR fields to describe power states, allocated substate power, latency tolerance, and reset/link-up/FLR/D3hot-to-D0 timing.

The header does not enforce sequencing. Callers must still follow PCIe and ASIC-specific ordering, such as disabling a capability before changing size fields, masking errors before clearing status, programming MSI/MSI-X address/data before enabling delivery, or respecting reset and power-transition timing.

## State and Persistence

The file owns no state, allocates no memory, performs no I/O, and persists nothing. It names hardware state that lives in PCIe/NBIO configuration registers.

Represented state includes:

- Capability topology: capability IDs, versions, and next pointers for standard PCI and PCIe extended capability lists.
- Endpoint identity/configuration: vendor/device IDs, command and status bits, revision/class code fields, header type, BIST, BARs, ROM base, adapter ID, interrupt line/pin, and latency/min-grant fields.
- Interrupt state: MSI enable/multiple-message/64-bit/per-vector/ext-data fields, MSI message address/data/mask/pending fields, and MSI-X table/PBA location plus enable/function-mask/table-size state.
- Error-reporting state: AER uncorrectable/correctable status, masks, severity, first-error pointer, ECRC generation/check capability and enable bits, multiple header recording, header logs, and TLP prefix logs.
- Link and PHY state: link control/status, link control/status 2, lane equalization coefficients, equalization-complete flags, lane error status, 16 GT/s status, parity mismatch status, and lane margining control/status.
- Isolation and address-translation state: ACS, ATS, page request, PASID, ARI, multicast, and SR-IOV fields.
- Power and timing state: PMI status/control, DBESL, LTR, power-budget data, DPA capability/status/control/substate power allocation, and RTR reset/link/FLR/D3hot timing fields.

Persistence across GPU reset, PCI function-level reset, BACO, suspend/resume, runtime power management, or hot reset is not specified by this header. Those semantics depend on the hardware block and on driver reinitialization paths that reprogram or reread these fields.

## Dependencies and Integration Points

This file is useful only with the adjacent generated NBIO 7.11 register metadata:

- `nbio_7_11_0_offset.h` for register offsets that pair with these field names.
- `nbio_7_11_0_smn.h` for SMN-addressed NBIO registers where applicable.
- `nbio_7_11_0_default.h` for reset/default values where generated.
- Neighboring chunks of `nbio_7_11_0_sh_mask.h`: the previous chunk owns the start of `BIF_CFG_DEV0_EPF1_LINK_STATUS2`, and the next chunk continues `BIF_CFG_DEV2_EPF0` after `LATENCY`.

Likely AMDGPU integration areas include:

- NBIO 7.11 initialization and low-level register access paths that include generated ASIC register headers.
- PCIe capability setup, link management, and error handling code in the AMDGPU/SOC15 stack.
- RAS and diagnostic paths that read AER, lane error, parity mismatch, TLP prefix, and header-log registers.
- SR-IOV and virtualization code paths that need VF count, offset, stride, page-size, VF BAR, ARI, ACS, ATS, and PASID field geometry.
- Power-management code that inspects or programs PCI power management, LTR, DPA, power-budget, and readiness-time-reporting capabilities.

Integration is name-based and fragile: a caller must use the `*_SHIFT` and `*_MASK` macros for the same register as the address macro being accessed. The header does not include value enums for multi-bit fields, so interpretation of field values comes from PCIe specifications, ASIC register documentation, or companion driver code.

## Risks

- A wrong shift or mask can silently corrupt PCIe configuration programming. In this chunk, high-impact fields include MSI/MSI-X enables, AER masks/severity, ACS/ATS/PASID controls, SR-IOV controls, BAR resize controls, and link equalization/margining controls.
- The chunk starts and ends in the middle of logical register blocks. `BIF_CFG_DEV0_EPF1_LINK_STATUS2` begins in the previous chunk, and `BIF_CFG_DEV2_EPF0` continues in the next chunk. Per-file reconciliation must merge adjacent chunks before judging completeness.
- Many repeated lane registers use lane-indexed names for lanes 0-15. A generator error affecting one lane can be hard to catch if tests exercise only lane 0 or only the negotiated active-width subset.
- AER fields are similar across status, mask, and severity registers. Mixing them up can hide real hardware errors, report stale errors, or classify fatal/nonfatal/corrected errors incorrectly.
- Capability fields are repeated for `DEV0_EPF1` and `DEV0_EPF2` with mostly parallel schemas but not identical capability coverage. Copying assumptions from one endpoint function to the other can reference nonexistent or differently scoped fields.
- BAR and VF BAR resize controls can affect address aperture layout. Incorrect programming can break MMIO mapping, VF resource assignment, or guest-visible BAR sizing.
- SR-IOV, ATS, PASID, ACS, and ARI fields touch isolation and address-translation behavior. Bad writes can compromise peer-to-peer isolation expectations or make DMA/address-translation behavior inconsistent with IOMMU setup.
- Lane margining, equalization, and 16 GT/s PHY fields are diagnostic/control surfaces for physical-link behavior; using them outside documented sequences can destabilize the link.

## Test and Validation Signals

Useful validation is mostly mechanical plus hardware-facing smoke coverage:

- Build AMDGPU configurations that include NBIO 7.11 generated headers to catch malformed or missing macro names.
- Run a generated-header consistency check that every complete register in this line range has expected `__SHIFT`/`_MASK` pairs for each field, allowing the intentional boundary splits at `DEV0_EPF1_LINK_STATUS2` and `DEV2_EPF0_LATENCY`.
- Cross-check every register name in this chunk against the matching NBIO 7.11 offset/default headers so field masks are paired with address/default metadata where expected.
- Compare repeated schemas across `DEV0_EPF1` and `DEV0_EPF2`, especially MSI/MSI-X, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR fields.
- Validate AER by injecting or provoking controlled correctable and uncorrectable PCIe errors on supported hardware and confirming status, mask, severity, header-log, TLP-prefix-log, and clear behavior.
- Validate MSI/MSI-X setup by enabling interrupts, masking vectors, checking pending bits, and confirming message address/data handling under interrupt load.
- Exercise SR-IOV-capable configurations, checking VF count, stride, offset, page-size, VF BAR, ARI, ACS, ATS, and PASID reporting against PCI config-space dumps.
- Exercise link diagnostics by comparing link status, lane error, equalization, 16 GT/s parity mismatch, and lane margining fields with `lspci`, debugfs, and hardware validation tools on affected ASICs.
- Run reset, FLR, suspend/resume, and runtime power-management coverage to ensure driver code reinitializes policy fields and interprets readiness-time-reporting and DPA/PMI state correctly.

## Chunk Boundary Notes

Line 7363 begins with the last four `BIF_CFG_DEV0_EPF1_LINK_STATUS2` mask definitions; the corresponding register comment and shift definitions are in the previous work item. Lines 7367-8761 complete the remainder of `DEV0_EPF1` through `BIF_CFG_DEV0_EPF1_RTR_DATA2`. Lines 8762-9770 cover `DEV0_EPF2` from standard PCI identity fields through `BIF_CFG_DEV0_EPF2_RTR_DATA2`. Lines 9771-9837 start `DEV2_EPF0` and stop at `BIF_CFG_DEV2_EPF0_LATENCY`; the rest of that address block belongs to the following chunk.

### subset-b-003126: lines 9838-12285

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 9838-12285

## Scope And Purpose

This chunk is generated register-field metadata for AMD NBIO 7.11.0 PCI/PCIe configuration-space registers. It contains only C preprocessor macros: each register field has a `__SHIFT` value and a corresponding `_MASK` value. The chunk starts in the `BIF_CFG_DEV2_EPF0` endpoint-function register block, continues through that block's conventional PCI header, PCIe capability, MSI/MSI-X, SATA, vendor-specific, advanced error reporting, resizable BAR, power-budgeting, DPA, ACS, PASID, ARI, data-link feature, 16 GT PHY, lane equalization, lane margining, and RTR capability fields, then enters the `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` address block and covers `BIF_CFG_DEV0_EPF4` through part of BAR5 control.

The header is a hardware contract, not executable logic. The macros let AMDGPU/NBIO code extract, construct, and update bitfields without hard-coding raw bit positions. They are intended to be used with the sibling `nbio_7_11_0_offset.h` register-address macros and the AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Important Macro Families

`BIF_CFG_DEV2_EPF0_*` describes the PCIe endpoint function 0 under device 2. The visible fields cover:

- Basic PCI configuration header pieces: latency/header/BIST, BAR1-BAR6 base addresses, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability list.
- Power management and USB/SATA-adjacent capability fields: PMI capability list, power state/PME status/control, SBRN, FLADJ, DBESL/DBESLD, SATA capability/header and indirect data port index/data.
- PCIe capability and control/status fields: device capabilities, device control/status, link capabilities, link control/status, link capability/control/status 2, and feature bits such as FLR, max payload, max read request size, ASPM, common-clock config, retrain link, target speed, equalization completion, and lane/preset indicators.
- Interrupt capabilities: MSI list/control/address/data/mask/pending fields plus MSI-X list/message-control/table/PBA fields.
- Extended capability list headers: vendor-specific, virtual channel, advanced error reporting, BAR enhancement, power budget, dynamic power allocation, secondary PCIe, ACS, PASID, LTR, ARI, data-link feature, 16 GT PHY, margining, and RTR.
- Error-reporting diagnostics: uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four TLP header log dwords, and four TLP prefix log dwords.
- Resizable/enhanced BAR data: BAR1-BAR6 capability and control fields with supported-size, active size, BAR index, total BAR count, and upper supported-size bits.
- Power and arbitration capability fields: virtual-channel resource capability/control/status, power budget data selection/data/capability, DPA capability/status/control, and eight DPA substate power allocation fields.
- Isolation and address-space features: ACS capability/control, PASID capability/control, LTR max snoop/no-snoop latency, ARI capability/control, and data-link feature capability/status.
- High-speed link diagnostics: 16 GT link capability/control/status, local and RTM parity mismatch status, per-lane 16 GT equalization presets for lanes 0-15, and per-lane PCIe margining control/status fields for lanes 0-15.
- RTR data fields: two registers with buffer size, memory-map aperture size, routing ID, and offset fields.

`BIF_CFG_DEV0_EPF4_*` begins a separate endpoint function block for device 0, function 4. In this chunk it includes the early PCI configuration header, PCIe capability/control/status fields, MSI/MSI-X, SATA capability fields, vendor-specific fields, advanced error reporting, TLP header/prefix logs, and the start of the enhanced BAR capability/control sequence through `PCIE_BAR5_CNTL`. This block mirrors much of the DEV2 EPF0 layout but is scoped to a different BIF configuration decoder address block.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The externally consumed API is the macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for that field.
- Register names intentionally match the offset-header names without the `reg` prefix and instance suffix, so code can combine `regBIF_CFG_DEV2_EPF0_0_*` or `regBIF_CFG_DEV0_EPF4_0_*` offsets with the matching field masks.

The macros are suitable for AMDGPU helper patterns such as:

- `REG_GET_FIELD(value, BIF_CFG_DEV2_EPF0_DEVICE_STATUS, FATAL_ERR)`
- `REG_SET_FIELD(value, BIF_CFG_DEV2_EPF0_DEVICE_CNTL, MAX_PAYLOAD_SIZE, size)`
- manual extraction with `(value & MASK) >> SHIFT` when helper macros are not used.

## Control Flow

The chunk has no control flow. Its effect occurs at compile time when included by NBIO or PCIe-related AMDGPU source files. At runtime, driver control flow comes from the consumers: they read a 16-bit or 32-bit register, use these masks/shifts to isolate or update a field, and write the resulting value back through MMIO or indexed PCIe-port access.

The field ordering follows PCI/PCIe capability layout rather than driver execution order. Capability list fields (`CAP_ID`, `CAP_VER`, `NEXT_PTR`) define the linked-list structure of extended capabilities. Status/control pairs model hardware state machines where software writes control bits and polls or handles status bits, but the state transitions themselves are implemented by hardware.

## State And Persistence Behavior

These macros do not allocate, store, or persist software state. They describe persistent hardware register state:

- Configuration identity and resource registers such as BARs, subsystem IDs, class codes, and ROM base address can reflect hardware straps, firmware programming, or OS PCI resource assignment.
- Capability/control registers can be changed by kernel PCI core, platform firmware, or the AMDGPU driver depending on ownership and access path.
- Status registers such as PCIe error status, link status, parity mismatch status, lane margining status, and DPA status expose hardware state and often include write-one-to-clear or hardware-updated semantics governed by the PCIe specification and AMD hardware behavior.
- Log registers such as AER TLP header and prefix logs preserve diagnostic information until hardware or software clears the associated error state.

Because the macros are pure definitions, persistence risks come from consumers writing incorrect fields or using masks against the wrong register instance, not from this header itself.

## Dependencies And Integration Points

The direct dependency is the generated AMD register-header ecosystem:

- `nbio_7_11_0_offset.h` supplies the register offsets and base indices for the same blocks, including `regBIF_CFG_DEV2_EPF0_0_*` and `regBIF_CFG_DEV0_EPF4_0_*`.
- `amdgpu/nbio_v7_11.c` includes both the offset and shift/mask headers for NBIO 7.11.0 register programming.
- AMDGPU register helpers in the wider driver use the mask names to implement read/modify/write operations and field extraction.

The hardware integration points are PCIe endpoint configuration spaces exposed through NBIO/BIF decoders. Important subsystem touch points include PCI resource enumeration, link-speed and link-training reporting, AER handling, MSI/MSI-X programming, power management, resizable BAR programming, ACS/PASID/ARI features used by virtualization and IOMMU flows, and physical link diagnostics such as 16 GT equalization and lane margining.

## Risks And Edge Cases

The main risk is register-contract drift. If a mask or shift is wrong, the driver can silently read the wrong bit or write a neighboring field. In this chunk that risk is concentrated around:

- Dense control/status registers such as `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, ACS/PASID/ARI control, and DPA control/status where adjacent bits have different side effects.
- AER status/mask/severity definitions, where confusing status bits with mask bits can hide errors, misclassify severity, or clear/report the wrong condition.
- Repeated per-lane definitions for lanes 0-15, where copy-generation mistakes can swap lane numbers or reuse the wrong field prefix.
- Repeated enhanced BAR capability/control fields across BAR1-BAR6 and across DEV2 EPF0 versus DEV0 EPF4, where one prefix mismatch can target the wrong endpoint function.
- Capability-list `NEXT_PTR` fields, where a wrong mask width or shift can break software traversal of extended capabilities.
- Mixed 16-bit and 32-bit register layouts. Many masks are 16-bit-looking values, while others cover full 32-bit fields; consumers must use the correct access width and register address.

This chunk also ends in the middle of the `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` definition group, so any per-file summary must reconcile this with the following chunk before claiming complete DEV0 EPF4 BAR coverage.

## Test Signals

There are no unit tests tied directly to generated mask headers. Useful validation signals are mostly integration and hardware-facing:

- The kernel must compile with `nbio_v7_11.c` and other AMDGPU consumers including `nbio_7_11_0_sh_mask.h`.
- PCIe enumeration should expose sane BARs, MSI/MSI-X capabilities, power-management capabilities, and extended capability lists for NBIO 7.11.0 devices.
- AMDGPU bring-up should successfully program NBIO doorbells, interrupt paths, HDP flush registers, PCIe-port indexed registers, and any features that share the same generated register-header style.
- Runtime diagnostics should show plausible PCIe link width/speed/status, AER status, and capability data through kernel logs, debugfs, lspci, or driver-specific dumps.
- Error-injection or platform validation that exercises AER, FLR, resizable BAR, ACS/PASID/ARI, link retraining, 16 GT equalization, and lane margining would catch many mask/shift mistakes in this chunk.

## Chunk Boundary Notes

The assigned range is lines 9838-12285 only. It begins after earlier DEV2 EPF0 identity fields and ends before the rest of DEV0 EPF4 BAR5 control and later DEV0 EPF4 capability definitions. The final source-file research document should merge this chunk with adjacent chunks to avoid treating either boundary as a semantic start or end of the hardware block.

### subset-b-003127: lines 12286-14755

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 12286-14755

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIF PCI configuration-space register images. The covered range starts in the middle of the `BIF_CFG_DEV0_EPF4` PCIe BAR capability/control section, spans the full `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp` address blocks, and ends partway through the `BIF_CFG_DEV2_EPF5_LINK_CAP` register.

The content is hardware metadata, not executable driver logic. AMDGPU code includes this file with matching generated offset/default/SMN headers so register-access helpers can encode and decode individual PCI configuration fields without open-coded bit numbers.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

Major macro groups in this chunk are:

- `BIF_CFG_DEV0_EPF4_PCIE_*`: the tail of endpoint function 4 on device 0, including BAR5/BAR6 sizing controls, power-budget enhanced capability/data/capability fields, Dynamic Power Allocation capability/status/control/substate power allocations, ACS capability/control, PASID capability/control, ARI capability/control, and Readiness Time Reporting enhanced capability plus `RTR_DATA1`/`RTR_DATA2`.
- `BIF_CFG_DEV2_EPF3_*`: a complete generated PCI config-space block for device 2 endpoint function 3. It includes standard PCI identity and command/status fields, BARs, subsystem IDs, ROM base, capability pointers, legacy interrupt fields, vendor capability, power-management capability/status, secondary bus reset number (`SBRN`), FLADJ, DBESL/DBESLD, PCIe capability/device/link/device2/link2 registers, MSI/MSI-X capability fields, SATA capability/index/data fields, PCIe vendor-specific enhanced capability registers, AER status/mask/severity/control/header-log/TLP-prefix-log fields, BAR enhanced capabilities, power budget, DPA, ACS, PASID, ARI, and RTR fields.
- `BIF_CFG_DEV2_EPF4_*`: the same broad schema for device 2 endpoint function 4, including the full standard PCI header, PM/PCIe/MSI/MSI-X/SATA/vendor-specific/AER/BAR/power-budget/DPA/ACS/PASID/ARI/RTR families.
- `BIF_CFG_DEV2_EPF5_*`: the beginning of device 2 endpoint function 5, from standard identity and command/status fields through PM capability/status, PCIe capability, device capability/control/status, and the first `LINK_CAP` shift fields.

Within the repeated PCIe capability areas, important fields include payload/read-request sizes, extended-tag/no-snoop/relaxed-ordering enables, FLR capability and initiation, transaction-pending and error-status bits, link speed/width/ASPM/clock-power-management/link-bandwidth fields, completion-timeout and atomic-op controls, MSI/MSI-X table and PBA location fields, AER uncorrectable/correctable error bitmaps, and enhanced BAR size/index fields.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is consumed at compile time by C code that performs MMIO, config-space, or indirect NBIO register accesses.

The implied hardware flows are:

1. PCI enumeration and device setup read identity, class-code, BAR, subsystem, capability-pointer, interrupt, MSI, MSI-X, and PCIe capability fields from the generated endpoint-function blocks.
2. Driver or firmware initialization can program command bits such as memory access, bus mastering, SERR, and interrupt disable; PCIe device-control bits such as max payload, max read request, relaxed ordering, no snoop, extended tags, and FLR; and link-control/link-control2 policy bits in adjacent chunks.
3. Power-management and DPA flows use PM capability/status, power-budget data, and DPA substate fields to advertise or control power states, substates, latency indicators, and allocated power values.
4. Reliability and diagnostics flows use AER status/mask/severity/header-log/TLP-prefix-log fields and device status bits to classify corrected, nonfatal, fatal, unsupported-request, completion-timeout, ECRC, ACS, and transaction-pending conditions.
5. Virtualization and multi-function routing features use ACS, PASID, and ARI capability/control fields to expose peer-to-peer controls, process address space IDs, and alternative routing interpretation.
6. Readiness Time Reporting fields advertise reset/DL-up/FLR/D3hot-to-D0 timings for PCIe software that needs bounded wait behavior after resets or power transitions.

The header does not perform sequencing, polling, clearing, locking, or value validation. Callers must pair these masks with the correct register address macros and follow PCIe/NBIO programming rules for write-one-to-clear status bits, capability traversal, FLR timing, AER logging, and reset ordering.

## State and Persistence

The header owns no mutable state, allocates no memory, and persists nothing. The represented state lives in NBIO/NBIF hardware configuration registers for multiple endpoint functions.

State categories represented here include:

- PCI identity/configuration state: vendor/device IDs, revision, class/subclass/program-interface, command/status, cache-line/latency/header/BIST, BARs, ROM BAR, subsystem IDs, and capability pointers.
- Interrupt state: legacy interrupt line/pin plus MSI/MSI-X message control, address/data, mask, pending, table, and PBA fields.
- PCIe capability state: device capability/control/status, link capability/control/status, second-generation device/link capability/control/status fields for endpoint functions covered completely in this chunk.
- Power state: PM capability/status, power-budget data, DPA capability/status/control, DPA substate power allocation, and readiness-time values.
- Error-reporting state: AER uncorrectable/correctable status and masks, uncorrectable severity, AER capability/control, captured header logs, and TLP prefix logs.
- Isolation/virtualization state: ACS, PASID, and ARI capability/control bits.
- Vendor/device-specific state: vendor-specific enhanced capability registers, SATA capability/index/data fields, DBESL/DBESLD, and FLADJ.

Retention across GPU reset, PCI FLR, secondary bus reset, suspend/resume, BACO, or runtime power transitions is not defined here. Those semantics are determined by hardware and by the AMDGPU/NBIO initialization paths that reprogram or reread these registers.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11.0 headers:

- `nbio_7_11_0_offset.h` for register offsets matching these field names.
- `nbio_7_11_0_default.h` for reset/default values when generated for this ASIC block.
- Other chunks of `nbio_7_11_0_sh_mask.h`, because this work item starts inside `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` and ends before the full `BIF_CFG_DEV2_EPF5_LINK_CAP` mask set.

Likely integration areas in the AMDGPU tree include NBIO 7.11 setup code, SOC15 register access wrappers, PCIe capability/link management, SR-IOV or multi-function endpoint setup, AER/RAS handling, reset/FLR paths, and power-management code that reads or writes PM, DPA, power-budget, and readiness-time fields.

The macros are normally used through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC/NBIO read-modify-write wrappers. Correct use requires pairing a `*_SHIFT`/`*_MASK` macro from this file with the matching offset macro for the same register and endpoint function.

## Risks

- A wrong shift or mask silently targets the wrong PCI config bit. In this range that can affect BAR sizing, bus mastering, memory decoding, interrupt masking, FLR initiation, AER reporting, ACS isolation, PASID enablement, ARI routing, or link capability interpretation.
- The `DEV2_EPF3` and `DEV2_EPF4` blocks are highly repetitive. Generator or copy/paste drift can be hard to notice if tests exercise only one endpoint function.
- The chunk boundary starts with only the final masks for `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL`; the matching shifts and `BAR_INDEX_MASK` are in the previous chunk. Consumers must use the complete generated header, not this isolated range.
- The chunk boundary ends after `BIF_CFG_DEV2_EPF5_LINK_CAP__SURPRISE_DOWN_ERR_REPORTING__SHIFT`; remaining `LINK_CAP` shifts and all masks are in the next chunk.
- AER and device-status fields often have write-one-to-clear or latched semantics in hardware. Generic read-modify-write code that ignores those semantics can accidentally clear diagnostic state.
- Command/device-control bits such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `INITIATE_FLR`, payload size, max read request size, relaxed ordering, no snoop, and extended tags can cause functional failures if programmed without matching platform and link capabilities.
- ACS, PASID, and ARI fields are security/isolation-sensitive in virtualized or multi-function environments. Misprogramming can break peer-to-peer routing assumptions or DMA address-space isolation.
- BAR enhanced capability fields expose size-supported and size-control data; confusing capability versus control fields can produce invalid resource sizing or incorrect aperture programming.

## Test and Validation Signals

Useful validation is mostly generated-header and hardware integration coverage:

- Build AMDGPU configurations that include NBIO 7.11.0 generated headers to catch malformed macro names, missing includes, or duplicate definitions.
- Mechanically verify every complete register in this range has expected `__SHIFT` and `_MASK` pairs, allowing the intentional split at the beginning of `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` and the end of `BIF_CFG_DEV2_EPF5_LINK_CAP`.
- Cross-check register names against `nbio_7_11_0_offset.h` and generated default files so `DEV0_EPF4`, `DEV2_EPF3`, `DEV2_EPF4`, and `DEV2_EPF5` fields line up with address definitions.
- Run symmetry checks across `BIF_CFG_DEV2_EPF3_*` and `BIF_CFG_DEV2_EPF4_*`; standard PCI, PM, PCIe, MSI/MSI-X, AER, BAR, DPA, ACS, PASID, ARI, and RTR field layouts should remain consistent unless hardware documentation says otherwise.
- On hardware or emulation, verify PCI config enumeration for the covered endpoint functions: vendor/device IDs, class codes, BAR discovery, capability list traversal, MSI/MSI-X discovery, PCIe link capability reporting, and AER capability discovery.
- Exercise controlled reset paths, including FLR and D3hot-to-D0 where supported, and compare readiness-time fields with observed polling/wait behavior.
- Validate error paths by injecting or observing AER corrected/uncorrected events and confirming status, masks, severity, header logs, and device-status bits decode with these masks.
- Validate virtualization/isolation setup by checking ACS/PASID/ARI capability and control values against expected IOMMU/SR-IOV or multi-function behavior.

## Chunk Boundary Notes

Lines 12286-14755 are a middle slice of a much larger generated header. The first register is incomplete because `BIF_CFG_DEV0_EPF4_PCIE_BAR5_CNTL` begins at line 12280, before this chunk. The final register is also incomplete because `BIF_CFG_DEV2_EPF5_LINK_CAP` continues after line 14755. The merge/reconciliation lane should treat these as chunking artifacts and combine this document with adjacent chunk research for the final per-file report.

### subset-b-003128: lines 14756-17197

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 14756-17197

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.11.0 register mask header. The range starts in the middle of `BIF_CFG_DEV2_EPF5_LINK_CAP`, at the PCIe link-capability reporting fields, and ends inside `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`, after the first three corrected-error mask fields. It contains 2,145 preprocessor definitions, including 1,071 `__SHIFT` constants and 1,170 `_MASK` constants.

The covered address blocks are:

- Tail of `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`: DEV2 endpoint function 5 PCIe capability, MSI/MSI-X, SATA, vendor-specific, advanced error reporting, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR field layouts.
- All visible `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`: DEV2 endpoint function 6 standard PCI config header fields plus the same PCIe capability and extended-capability families as EPF5.
- Start of `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`: DEV0 endpoint function 5 standard PCI config header fields, PMI/USB-related fields, PCIe capability fields, MSI/MSI-X, SATA, vendor-specific capability, and the beginning of AER corrected-error masks.

This file is generated register-description data. It has no C functions, structs, variables, loops, branches, or direct storage. Its behavior comes from how compiled driver code combines these macros with matching register offsets and AMDGPU bitfield helpers.

## Purpose

The purpose of this chunk is to define bit-level layouts for several NBIO PCI/PCIe configuration spaces on AMD GPU ASICs using NBIO 7.11.0. Each hardware field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or update the field.

The sibling `nbio_7_11_0_offset.h` file supplies register addresses and base indices. For example, the matching offsets identify DEV0 EPF5 at `regBIF_CFG_DEV0_EPF5_0_VENDOR_ID` address `0x11400`, DEV2 EPF5 at `regBIF_CFG_DEV2_EPF5_0_VENDOR_ID` address `0x15400`, and DEV2 EPF6 at `regBIF_CFG_DEV2_EPF6_0_VENDOR_ID` address `0x15800`. This chunk supplies the masks for fields inside those registers, including AER registers such as `regBIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_STATUS`, `regBIF_CFG_DEV2_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV2_EPF6_0_PCIE_UNCORR_ERR_STATUS`.

AMDGPU code includes this header from `amdgpu/nbio_v7_11.c` together with the matching offset header. The normal consumers are register helpers such as `REG_SET_FIELD`, direct mask tests, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### PCIe Link and Device Capabilities

The chunk begins with the remaining `BIF_CFG_DEV2_EPF5_LINK_CAP` fields:

- Data-link active reporting capability.
- Link bandwidth notification capability.
- ASPM optionality compliance.
- Port number.

It then defines complete `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` layouts for DEV2 EPF5, DEV2 EPF6, and DEV0 EPF5. These fields cover PCIe link speed and width, link retrain and disable controls, common-clock and extended-sync controls, clock power management, link bandwidth interrupts/status, completion timeout support/control, ARI, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, emergency power reduction, Gen3 equalization status, crosslink state, RTM presence detection, downstream component presence, and DRS support/signaling.

These macros are capability-space definitions rather than policy. The kernel PCI core and firmware normally own most PCIe config negotiation. AMDGPU-specific NBIO code can still use these masks for ASIC-specific diagnostics, workarounds, or direct config-space access through NBIO/PCIE index-data windows.

### Standard PCI Config Header Fields

The DEV2 EPF6 and DEV0 EPF5 sections include ordinary PCI header fields:

- Vendor/device ID.
- Command and status.
- Revision, programming interface, subclass, and base class.
- Cache line size, latency timer, header type, BIST.
- BARs 1 through 6 and ROM BAR.
- Capability pointer, interrupt line/pin, min grant, max latency.
- Adapter/vendor capability registers.

The `COMMAND` and `STATUS` masks expose standard PCI enable/status bits such as I/O space, memory space, bus mastering, parity and SERR enables, interrupt disable, interrupt status, capability-list presence, 66 MHz capability, fast back-to-back support, master data parity error, DEVSEL timing, signaled target abort, received target abort, received master abort, signaled system error, and detected parity error.

Because these are PCI config-space fields, many bits are controlled by enumeration, firmware, PCI core policy, or device reset state. Direct AMDGPU writes must preserve unrelated bits with read-modify-write helpers.

### Power Management and USB/SATA-Related Capability Fields

The chunk includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` layouts for the endpoint functions. These define capability ID/next pointer, PCI power-management version, PME clock and D-state support, D1/D2 support, PME support, power state, no-soft-reset, PME enable/status, data select/scale, and power-management data fields.

DEV0 EPF5 also includes `SBRN`, `FLADJ`, and `DBESL_DBESLD`, which are USB-related capability fields for serial bus release number, frame-length adjustment, and BESL/deep-BESL latency values. DEV2 EPF5, DEV2 EPF6, and DEV0 EPF5 include SATA capability and indirect data port definitions:

- `SATA_CAP_0` and `SATA_CAP_1` identify capability revision, BAR location, and BAR offset.
- `SATA_IDP_INDEX` and `SATA_IDP_DATA` describe the indirect index/data port format.

These definitions let the driver decode hardware-exposed PCI capabilities when NBIO presents non-graphics endpoint functions or embedded endpoint capabilities.

### MSI and MSI-X Capability Fields

For each covered endpoint function, the chunk defines MSI and MSI-X capability layouts:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` include capability ID, next pointer, MSI enable, multiple-message capable/enable, 64-bit address capability, per-vector masking, extended message capability, and hypertransport-specific alias fields.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, and their 64-bit forms expose interrupt message address/data fields.
- `MSI_MASK`, `MSI_PENDING`, `MSI_MASK_64`, and `MSI_PENDING_64` expose per-vector mask and pending bits.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` expose MSI-X enable, function mask, table size, table/PBA BIR, and offsets.

Interrupt routing is high risk because MSI/MSI-X state interacts with the kernel PCI subsystem, interrupt remapping, IOMMU state, and GPU interrupt handler setup. These generated masks only define wire format; they do not encode ownership or ordering.

### Vendor-Specific and Routing Capability Fields

The `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` fields define extended capability headers, vendor-specific IDs/revisions/lengths, and scratch registers. These are AMD/vendor extension points.

The `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` fields define routing-related extended capability metadata and data values. They expose capability ID/version/next pointer and opaque data fields.

### Advanced Error Reporting

The AER families are repeated for DEV2 EPF5, DEV2 EPF6, and partially for DEV0 EPF5:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` defines the AER extended capability header.
- `PCIE_UNCORR_ERR_STATUS` exposes uncorrectable error status bits: DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- `PCIE_UNCORR_ERR_MASK` controls masking for the same uncorrectable error classes.
- `PCIE_UNCORR_ERR_SEVERITY` controls whether each uncorrectable error is treated as fatal or non-fatal.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover correctable receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal, and correctable internal error bits.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC generation/check capability and enable bits, and multi-header receive capability/enable bits.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` provide captured TLP header and prefix log storage.

The assigned range ends after `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK__BAD_DLLP_MASK_MASK`; the remaining DEV0 EPF5 corrected-error mask fields and `ADV_ERR_CAP_CNTL` fields continue in the next chunk.

### BAR, Power Budget, DPA, ACS, PASID, and ARI Extended Capabilities

DEV2 EPF5 and DEV2 EPF6 include complete definitions for several PCIe extended capabilities:

- BAR enhanced capability: capability header plus BAR 1 through BAR 6 capability/control fields for fixed BAR size, BAR size capability, and atomic operation routing/blocking behavior.
- Power budget capability: data select, base power, data scale, PM substate, power rail, type, and system allocation.
- Dynamic Power Allocation: capability/control/status fields, latency indicator, transition completed status, substate enable, and substate power allocation fields 0 through 7.
- ACS: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and I/O request blocking capability/control bits.
- PASID: execution permission, privileged mode, max PASID width, and enable controls.
- ARI: next function, function group, multi-function group, and ACS function group control fields.

These fields matter for virtualization, IOMMU, peer-to-peer routing, atomic operations, and power-management behavior. They should be interpreted against the endpoint function and PCIe capability chain that owns them, not as global NBIO state.

## Control Flow and State Behavior

There is no runtime control flow in this header chunk. It affects behavior at compile time by providing constants used by C code to compose and decode MMIO or PCI configuration register values.

The state described by these macros is persistent hardware state in NBIO PCIe configuration space. Some fields are latched capability bits, some are driver/PCI-core owned control bits, some are sticky status/error bits, and some are log registers capturing the first or most recent PCIe error context. Examples include link status, completion-timeout control, MSI mask/pending state, MSI-X function mask, AER status/mask/severity registers, header logs, PASID/ACS/ARI controls, DPA substate allocation, BAR control, and power-management status.

Several status fields are clear-on-write or sticky according to PCIe rules, especially error status registers. The macros do not express those semantics. Callers must follow PCI/PCIe and AMD NBIO programming sequences, including preserving reserved bits and using the correct error-clear value.

## Dependencies and Integration Points

This chunk depends on the generated NBIO register-header set:

- `nbio_7_11_0_offset.h` provides register addresses and base indices for the register names whose fields are defined here.
- `nbio_7_11_0_default.h`, where present for a register family, provides reset/default values.
- AMDGPU helper macros consume `__SHIFT` and `_MASK` constants for field extraction and updates.

Observed integration in this source tree:

- `amdgpu/nbio_v7_11.c` includes both `nbio/nbio_7_11_0_offset.h` and this mask header.
- `nbio_v7_11.c` uses these headers for NBIO setup functions including HDP flush offsets, PCIE index/data windows, PCIE port index/data windows, doorbell ranges, interrupt handling, memory-controller access, register remap, medium-grain clock gating, light sleep, and NBIO initialization.
- The local initialization path writes `regRCC_DEV0_EPF5_STRAP4` for NBIO IP versions 7.11.0 through 7.11.4, showing that DEV0 EPF5-related config state is part of the NBIO 7.11 setup surface even though this exact chunk covers config-space masks rather than that strap register.
- PCIe config-space fields in this chunk can also be reached indirectly through NBIO PCIE index/data windows returned by `nbio_v7_11_get_pcie_index_offset`, `nbio_v7_11_get_pcie_data_offset`, `nbio_v7_11_get_pcie_port_index_offset`, and `nbio_v7_11_get_pcie_port_data_offset`.

Cross-generation similarity is high. Similar AER and PCIe capability masks appear in other NBIO generations such as `nbio_7_7_0_sh_mask.h` and `nbio_7_2_0_sh_mask.h`, but consumers must include the matching 7.11.0 offset/mask/default set because address maps and endpoint-function coverage differ by ASIC generation.

## Risks

- Register/mask mismatch: using a 7.11.0 mask with another NBIO generation's offset can silently target the wrong field or endpoint function.
- Endpoint-function confusion: DEV0 EPF5, DEV2 EPF5, and DEV2 EPF6 have similar field names but different config-space address ranges.
- Reserved-bit damage: many PCIe capability registers include reserved bits or hardware-owned status bits; direct writes must preserve unrelated fields.
- Interrupt disruption: MSI/MSI-X enable, mask, pending, table, and PBA fields can affect interrupt delivery and must stay coordinated with PCI core and AMDGPU interrupt setup.
- Error-reporting regressions: AER status/mask/severity fields influence PCIe error visibility and fatal/non-fatal classification. Incorrect masks can hide link/device failures or escalate recoverable errors.
- Link training and power-management instability: link control, ASPM, completion timeout, LTR, OBFF, emergency power reduction, and DPA fields affect PCIe negotiation and low-power behavior.
- Virtualization and isolation risk: ACS, PASID, ARI, atomic-op, and BAR enhanced capability fields affect routing, request identity, and peer-to-peer behavior. Incorrect programming can break IOMMU isolation or P2P access assumptions.
- Generated-header drift: manual edits to this file are risky because the source of truth is likely an AMD register database; regenerated headers can overwrite local changes.

## Test Signals

Useful validation signals for changes involving this chunk are mostly integration and hardware-facing:

- The AMDGPU driver builds cleanly with `nbio_v7_11.c` including this header and no undefined or duplicate macros.
- `REG_SET_FIELD`/`REG_GET_FIELD` users compile against expected field names after any generated-header update.
- Boot logs show successful NBIO initialization for IP versions 7.11.0 through 7.11.4, with no PCIe config, AER, interrupt, or doorbell setup errors.
- PCI enumeration exposes expected endpoint functions and capability chains through `lspci -vvv`, including MSI/MSI-X, PCIe, AER, ACS/PASID/ARI where applicable.
- Runtime GPU workloads do not report new AER errors such as completion timeout, malformed TLP, ECRC, unsupported request, receiver overflow, or surprise down.
- Suspend/resume, hot reset, FLR, and GPU reset paths preserve PCIe link state, MSI/MSI-X delivery, and error-reporting configuration.
- Virtualization or SR-IOV test lanes, if applicable to the ASIC, confirm ACS/PASID/ARI routing and per-function interrupts still work.
- Header consistency checks compare the shift/mask definitions against the matching `nbio_7_11_0_offset.h` register names and any generated default header.

### subset-b-003129: lines 17198-19674

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 17198-19674

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11 shift/mask header. It defines C preprocessor constants for decoding and programming bitfields in NBIF/BIF PCI configuration-space registers exposed by the NBIO configuration decoder. The macros describe field geometry only; they do not implement Ceph or distributed-filesystem behavior despite the source path living under a `ceph-client` mirror.

The range covers 2,126 `#define` entries across 342 commented register blocks. It contains 1,062 `__SHIFT` definitions and 1,064 `_MASK` definitions. The two-mask surplus is caused by chunk boundaries: the range starts at the tail of `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`, where the matching shift definitions for several corrected-error mask bits are in the previous chunk. The range ends inside `BIF_CFG_DEV0_EPF7_COMMAND`, after the `IO_ACCESS_EN` and `MEM_ACCESS_EN` shift definitions but before the remaining command shifts and masks in the next chunk.

At a high level, this chunk covers:

- The tail of device 0 endpoint/function 5 (`DEV0_EPF5`) PCIe Advanced Error Reporting and extended capability fields.
- A complete visible `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` address block for device 1 endpoint/function 1 (`DEV1_EPF1`), including PCI header fields, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power, DPA, ACS, PASID, ARI, SR-IOV, VF resizable BAR, and reset-time-reporting fields.
- Most of the `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` address block for device 0 endpoint/function 6 (`DEV0_EPF6`), from vendor ID through reset-time-reporting.
- The first few fields of the next `DEV0_EPF7` block: vendor ID, device ID, and the first two `COMMAND` shifts.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

The chunk starts with the final masks for `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK` corrected-error sources: replay-number rollover, replay-timer timeout, advisory nonfatal error, and corrected internal error. The corresponding earlier corrected-error bits and shifts are outside this range.

The rest of the `DEV0_EPF5` tail covers:

- `PCIE_ADV_ERR_CAP_CNTL`: first-error pointer, ECRC generation/check capability and enable bits, and multiple-header-recording capability/enable.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`: full-dword logged TLP header and prefix capture fields for AER diagnostics.
- `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL`: enhanced BAR capability metadata, supported sizes, BAR index, total BAR count, selected size, and upper supported-size bits.
- `PCIE_PWR_BUDGET_*`: enhanced capability list, data selector, base power, data scale, PM substate/state, type, power rail, and system-allocated indication.
- `PCIE_DPA_*`: dynamic power allocation capability, latency indicator, status, control, and per-substate power allocation registers 0-7.
- `PCIE_ACS_*`: access control services capability/control fields for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress-control vector sizing.
- `PCIE_PASID_*`: PASID enhanced capability, supported execution/privileged-mode attributes, maximum PASID width, and enable bits.
- `PCIE_ARI_*`: alternative routing-ID interpretation capability/control and next-function/function-group fields.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`: reset-time-reporting capability metadata plus reset, data-link-up, FLR, D3hot-to-D0, and valid timing fields.

The `DEV1_EPF1` block is the largest section in this chunk. It defines standard PCI configuration fields such as vendor/device ID, `COMMAND`, `STATUS`, revision ID, programming interface, subclass, base class, cache-line size, latency, header type, BIST, six base-address registers, adapter/subsystem ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, and vendor capability list. It also defines power-management interface fields (`PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`) including PME support/status, D-state selection, no-soft-reset, data select/scale, and bridge-extension bits.

`DEV1_EPF1` then exposes the PCIe capability chain:

- PCIe capability header and endpoint capability fields: version, device type, slot implemented, interrupt message, maximum payload support, phantom function support, extended tag, L0s/L1 latency, role-based error reporting, captured slot power, and FLR capability.
- Device control/status fields: error-reporting enables, relaxed ordering, maximum payload/read request sizes, extended tag, phantom functions, aux power PM, no-snoop, corrected/nonfatal/fatal/unsupported-request status, aux power, transaction pending, ID ordering, LTR, OBFF, and end-to-end TLP prefix blocking controls.
- Link capability/control/status fields: maximum speed/width, ASPM support and control, exit latencies, clock power management, surprise/down-error reporting, active-state link, bandwidth notification, target speed, hardware autonomous speed disable, selectable de-emphasis, link training, slot clock config, data-link-layer active, bandwidth management, equalization, and lane/equalization state bits.
- MSI and MSI-X capability structures: message control, 32/64-bit address/data fields, masks, pending bits, table offset/BIR, and PBA offset/BIR.
- SATA capability/index/data fields that model SATA-specific registers in this BIF config image.
- PCIe vendor-specific enhanced capability header and vendor-specific payload dwords.
- Advanced Error Reporting: uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.
- Enhanced BAR, power-budget, DPA, ACS, PASID, ARI, SR-IOV, VF resizable BAR, and reset-time-reporting capability blocks.

The `DEV1_EPF1` SR-IOV fields define capability/control/status bits for VF migration, ARI-capable hierarchy, VF MSE, VF enable, VF migration interrupt, initial/total/active VF counts, function dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, and VF BAR0 through VF BAR5 encodings. Its VF resizable BAR registers define supported VF BAR sizes, selected size, BAR index, total BAR count, and upper supported-size bits for BAR1 through BAR6.

The `DEV0_EPF6` block repeats most of the same endpoint/function shape as `DEV1_EPF1` but, in this chunk, stops after ARI and reset-time-reporting and does not include the `DEV1_EPF1` SR-IOV or VF resizable BAR blocks. It includes standard PCI header fields, PM capability/status, PCIe device/link/device2/link2 controls, MSI/MSI-X, SATA, vendor-specific enhanced capability, AER, header/prefix logs, BAR enhanced capability controls, power budgeting, DPA, ACS, PASID, ARI, and RTR timing.

The `DEV0_EPF7` block begins at the end of the chunk with `VENDOR_ID`, `DEVICE_ID`, and the first two command-register shifts (`IO_ACCESS_EN` and `MEM_ACCESS_EN`). The rest of `COMMAND` belongs to the next chunk.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is included at compile time and contributes constants to AMDGPU/NBIO register access code. Runtime behavior is implied by code that pairs these macros with register addresses from the matching offset header and with register read/modify/write helpers such as AMDGPU's SOC15/NBIO access wrappers and bitfield helpers.

The implied hardware flows are:

1. PCI enumeration or ASIC initialization reads identity, class-code, header, BAR, ROM BAR, capability pointer, interrupt, and capability-list fields for each exposed endpoint/function.
2. Driver or firmware setup programs `COMMAND`, PM, PCIe device control, link control, MSI/MSI-X, ACS, PASID, ARI, SR-IOV, and BAR-related controls through these bit masks.
3. PCIe error handling reads AER uncorrectable/correctable status, applies masks/severity policy, and can use header/TLP-prefix log dwords to diagnose the faulting transaction.
4. Power-management and virtualization paths inspect or program power budgeting, dynamic power allocation, PASID, ACS isolation, ARI routing, SR-IOV VF topology, and VF BAR sizing.
5. Reset and recovery paths can use RTR timing fields to understand reset, data-link-up, function-level reset, and D3hot-to-D0 timing metadata.

The file itself does not read hardware, write hardware, clear latched status bits, validate field values, or sequence operations. Those semantics belong to the driver paths and the NBIO 7.11 hardware specification.

## State and Persistence

The header owns no state, allocates no memory, persists nothing, and performs no I/O. The represented state lives in NBIO/BIF PCI configuration-space registers.

State categories represented by this chunk include:

- PCI function identity and enumeration state: vendor/device IDs, revision and class codes, header/BIST, BARs, ROM base, adapter ID, capability pointers, interrupt line/pin, and grant/latency fields.
- Configuration policy state: PCI command enables, error-response enables, PM controls, PCIe device/link controls, MSI/MSI-X enablement and vector table pointers, ACS isolation controls, PASID enables, ARI controls, SR-IOV enables, and VF BAR sizing.
- Error-observation and error-policy state: AER uncorrectable/correctable status, masks, severity, ECRC capability/control, first-error pointer, and transaction logs.
- Power and performance state: power budgeting records, dynamic power allocation substate controls, transition latency indicators, and per-substate power allocations.
- Reset/recovery timing state: reset, data-link-up, FLR, D3hot-to-D0, and valid timing fields in RTR data registers.

Persistence across GPU reset, PCI reset, FLR, suspend/resume, BACO, or runtime power transitions is not described by this header. A wrong macro value, however, is persistent in the compiled driver until the generated header is corrected and the driver rebuilt.

## Dependencies and Integration Points

The direct companion in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`, which provides the register address/offset side of the same NBIO 7.11 register map.

No `nbio_7_11_0_default.h` or `nbio_7_11_0_smn.h` file is present beside this header in the inspected tree. Consumers therefore depend on this shift/mask header plus the available offset header and any generated defaults or SMN metadata supplied elsewhere in the build or by hardware documentation.

Likely integration areas in AMDGPU include:

- NBIO 7.11 ASIC bring-up and low-level register access paths that include generated ASIC register headers.
- PCIe and NBIF setup code that programs endpoint/function PCI configuration images.
- AER and RAS-related diagnostic paths that classify correctable/uncorrectable PCIe errors and decode logged TLP headers.
- Interrupt setup for MSI/MSI-X capabilities and vector masks.
- Power-management code that handles PM capability, D-states, power budgeting, DPA, ASPM, LTR, and OBFF controls.
- Virtualization and isolation paths that depend on ACS, PASID, ARI, SR-IOV, VF BAR, and VF count/stride/offset fields.
- Reset and recovery paths that care about FLR, D3hot-to-D0, reset, and data-link-up timing fields.

Integration is primarily by exact symbol naming. `BIF_CFG_DEV1_EPF1_*`, `BIF_CFG_DEV0_EPF6_*`, and `BIF_CFG_DEV0_EPF5_*` name different hardware function configuration images even when their field layouts are structurally identical.

## Risks

- Chunk boundaries split register definitions. This range starts mid-`DEV0_EPF5_PCIE_CORR_ERR_MASK` and ends mid-`DEV0_EPF7_COMMAND`; pair-completeness checks must be done after merging adjacent chunks.
- Repeated endpoint/function layouts are easy to cross-wire. Using a `DEV1_EPF1` macro while accessing a `DEV0_EPF6` offset would decode the same-looking field from the wrong function image.
- AER status, mask, and severity registers have similar field names. Confusing status with mask, or severity with status, can hide errors, misclassify correctable versus fatal events, or corrupt diagnostics.
- PCIe control fields such as maximum payload size, maximum read request size, relaxed ordering, no-snoop, ASPM, target link speed, LTR, OBFF, ACS, PASID, ARI, and SR-IOV affect bus behavior and device isolation. Incorrect masks can create enumeration failures, performance regressions, DMA isolation problems, or broken virtualization.
- MSI/MSI-X table and PBA fields combine offset and BIR subfields. Incorrect extraction can point interrupt code at the wrong BAR or table location.
- SR-IOV and VF resizable BAR fields are dense and repeated. Wrong VF count, stride, first-offset, page-size, or BAR-size masks can expose invalid VF topology or resource apertures.
- Header/TLP-prefix logs are full-dword fields. They look mechanically simple, but using the wrong function prefix can make diagnostics report the wrong endpoint's captured transaction.
- The `L` suffix and 16-bit-looking masks are generated for C macro use. Consumers should keep normal unsigned register-width handling to avoid sign/width surprises when composing values.

## Test and Validation Signals

Useful validation signals for this chunk are mostly generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.11 generated headers to catch malformed macro names and duplicate or missing definitions.
- Check that, after adjacent chunks are merged, every register field has a matching `__SHIFT` and `_MASK` pair. The expected local exceptions are the four starting `DEV0_EPF5_PCIE_CORR_ERR_MASK` masks and the incomplete ending `DEV0_EPF7_COMMAND` block.
- Cross-check all register names in this range against `nbio_7_11_0_offset.h` so field macros have matching address macros where expected.
- Run mechanical symmetry checks across repeated endpoint/function layouts: `DEV1_EPF1` and `DEV0_EPF6` should match for common PCI header, PM, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR fields, while `DEV1_EPF1` legitimately has extra SR-IOV and VF resize BAR sections in this range.
- Validate PCI config-space dumps on NBIO 7.11 hardware by decoding `DEV0_EPF5`, `DEV1_EPF1`, `DEV0_EPF6`, and `DEV0_EPF7` registers with these masks and comparing against expected capability chains.
- Exercise AER paths with controlled correctable and uncorrectable PCIe errors, then confirm status, mask, severity, first-error pointer, header log, and TLP-prefix log decoding.
- Validate MSI/MSI-X setup by checking message control, 64-bit address/data, vector masks, pending bits, table offset/BIR, and PBA offset/BIR for the relevant endpoint/function.
- Validate virtualization/isolation paths by enabling ACS/PASID/ARI and, for `DEV1_EPF1`, SR-IOV/VF BAR settings, then confirming enumeration, DMA isolation, VF resource sizing, and function routing.
- Run reset, FLR, D3 transition, and suspend/resume coverage to confirm driver initialization restores policy fields and that RTR timing/status fields decode as expected.

## Chunk Boundary Notes

This chunk begins at line 17198 with only the final masks of `BIF_CFG_DEV0_EPF5_PCIE_CORR_ERR_MASK`; the shifts and earlier corrected-error masks are in the previous work item. It then completes the visible `DEV0_EPF5` advanced-error and extended-capability tail through `RTR_DATA2`.

Lines 17501-18655 cover the visible `DEV1_EPF1` block from `VENDOR_ID` through `RTR_DATA2`, including SR-IOV and VF resizable BAR definitions. Lines 18656-19662 cover the visible `DEV0_EPF6` block from `VENDOR_ID` through `RTR_DATA2`. The chunk then starts `DEV0_EPF7` at line 19665 and stops at line 19674 after `COMMAND__MEM_ACCESS_EN__SHIFT`; the next chunk is required for the rest of `DEV0_EPF7_COMMAND` and later `DEV0_EPF7` fields.

### subset-b-003130: lines 19675-22130

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 19675-22130

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 register field header. It contains C preprocessor constants for bit shifts and masks in PCI/PCIe configuration-space registers exposed through the NBIO BIF configuration decoder. The source is not executable logic: it is a hardware contract layer used by driver code and register helper macros to extract or compose fields without hard-coded numeric bit positions.

The requested slice starts inside the `BIF_CFG_DEV0_EPF7_COMMAND` field set, covers the rest of the `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` address block, and then begins the `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` address block. The `DEV0_EPF7` portion describes a complete PCIe endpoint/function configuration surface for function 7 of device 0. The `DEV1_EPF0` portion repeats the same conventional PCI header and PCIe capability surface for function 0 of device 1 and extends through lane 3 PCIe margining status before the chunk ends.

The companion offset definitions live in `nbio_7_11_0_offset.h`, while this header supplies field-level masks and shifts. `amdgpu/nbio_v7_11.c` includes both headers and uses their macros through standard AMDGPU register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and field helpers such as `REG_SET_FIELD`.

## Register And Macro Groups

The constants follow the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the field in the register value.
- Comment lines such as `//BIF_CFG_DEV1_EPF0_PCIE_UNCORR_ERR_STATUS` separate logical registers.
- Address block comments identify the hardware block to pair with offset macros from the sibling offset header.

Major `DEV0_EPF7` groups in this chunk include:

- Standard PCI header fields: command/status, revision, class codes, cache line size, latency, header type, BIST, BAR1 through BAR6, subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Power-management capability fields: PMI capability list, PME support, D-state support, PME enable/status, data select/scale, bus power enable, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe capability fields: device capabilities/control/status, link capabilities/control/status, and second-generation capability/control/status fields for extended tags, payload sizes, relaxed ordering, error reporting enables, link width/speed, ASPM, L0s/L1 exit latencies, retrain/common-clock controls, slot clock, target link speed, equalization, and link bandwidth status.
- MSI and MSI-X configuration fields: MSI capability list, message control, 32-bit and 64-bit message address/data/mask/pending registers, MSI-X message control, table BAR/offset, and PBA BAR/offset.
- SATA capability placeholders: `SATA_CAP_0`, `SATA_CAP_1`, IDP index, and IDP data.
- PCIe extended capabilities: vendor-specific capability header/data, AER uncorrectable/correctable status/mask/severity, AER capability/control and header/TLP prefix logs, enhanced BAR capabilities and controls for BAR1 through BAR6, power budget, dynamic power allocation, ACS, PASID, ARI, and readiness time reporting.

Major `DEV1_EPF0` groups in this chunk include:

- The same standard PCI header, PM, PCIe, MSI/MSI-X, SATA, vendor-specific, AER, enhanced BAR, power budget, and DPA fields.
- A PCIe Virtual Channel extended capability for port VC capability/control/status and VC0/VC1 resource capability/control/status. These fields model traffic class to virtual channel mappings, arbitration table status, VC IDs, and VC enable/negotiation state.
- Secondary PCIe, ACS, PASID, LTR, ARI, DLF, 16 GT/s PHY, and margining extended capability groups. The chunk includes lane equalization controls for 8 GT/s and 16 GT/s links, link status bits for 16 GT/s equalization phases, parity mismatch status registers, and lane margining controls/status for lanes 0 through 3.

## Important Interfaces And Integration Points

This header does not define functions or types. Its API is the macro namespace consumed by low-level AMDGPU code. Important integration points are:

- `nbio_7_11_0_offset.h`: provides the matching `reg...` address constants and `BASE_IDX` values. The offsets locate registers; this chunk's masks and shifts interpret the values read from those offsets.
- `amdgpu/nbio_v7_11.c`: includes the header and demonstrates the intended pattern: read a hardware register, modify a field with `REG_SET_FIELD`, then write it back. The visible file mostly uses other NBIO fields, but it establishes that this header is part of the NBIO 7.11 register-access contract.
- PCI/PCIe core concepts in the kernel and hardware: these masks encode conventional PCI command/status, BAR, MSI/MSI-X, PCI Express capability, AER, ACS, PASID, ARI, LTR, DPA, DLF, 16 GT/s PHY, and lane margining semantics. Higher-level code depends on these definitions matching the silicon register layout.
- GPU virtualization and multi-function exposure: `DEV0_EPF7` and `DEV1_EPF0` names indicate endpoint/function surfaces. Fields such as ACS, PASID, ARI, BAR sizing, MSI/MSI-X, and readiness-time reporting are especially relevant when the GPU exposes multiple PCIe functions or participates in IOMMU/PASID-aware compute paths.

Because these macros are generated constants, downstream usage usually appears indirectly through generic field helpers rather than function calls in this header.

## Control Flow And Behavior

There is no runtime control flow in this chunk. The behavioral flow appears only when driver code uses the definitions:

1. Driver code reads a 16-bit or 32-bit PCIe/NBIO register through an MMIO or PCIe-port access helper.
2. Code isolates a field by applying the generated mask and shifting right by the generated shift, or composes a field by clearing the mask and ORing the shifted value.
3. Code may write the modified register back to enable/disable capabilities, program BAR capability controls, clear/write-one-to-clear status bits, or configure error reporting and link behavior.

The exact read/write semantics are hardware-specific. Many named fields are status bits, capability bits, enable bits, or write-one-to-clear error bits. The header itself cannot encode access permissions, reset values, side effects, ordering requirements, or whether a given bit is read-only, write-only, read-write, sticky, or clear-on-write. Callers must rely on the hardware specification and existing driver patterns.

## State And Persistence Behavior

The header has no in-memory state and persists nothing by itself. It describes persistent and semi-persistent hardware state in PCI/PCIe configuration registers:

- Command bits such as memory access, bus mastering, SERR enable, and interrupt disable affect device behavior until firmware, the OS, reset, or driver code changes them.
- BAR fields and enhanced BAR control/capability fields describe resource apertures that the PCI core and driver use to map GPU memory and MMIO resources.
- MSI/MSI-X registers hold interrupt routing configuration and masks/pending state.
- PM and DPA fields describe power-management capabilities and current control/status selections.
- AER status/mask/severity and header/TLP-prefix logs capture error state that can survive until explicitly cleared or reset.
- Link status, equalization status, parity mismatch, and margining fields reflect current physical-link condition and training state.

Persistence should be understood as device register persistence across the relevant reset domain, not filesystem or kernel object persistence.

## Dependencies

The chunk depends on AMD's generated register database for NBIO 7.11.0. It also depends on the local AMDGPU register helper conventions:

- Register values are generally `u32` even when the underlying PCI config field is logically 8 or 16 bits; masks such as `0xFFL`, `0xFFFFL`, and `0xFFFFFFFFL` encode the active field width.
- `REG_SET_FIELD` and related helper macros expect the register prefix and field name to match the `__SHIFT` and `_MASK` symbols in this file.
- The sibling offset header must stay synchronized with this mask header. A correct mask with the wrong offset, or a correct offset with the wrong mask, is equally dangerous.

This file is hardware-family-specific. Similar macro names appear in other NBIO generation headers, but small capability differences are expected between ASIC generations and should not be merged by hand.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit shift or mask can silently program the wrong hardware field, misreport capability status, or corrupt adjacent fields.
- The chunk begins mid-register at line 19675. Any per-chunk consumer must merge it with the previous chunk to get the full `BIF_CFG_DEV0_EPF7_COMMAND` definition, including the `IO_ACCESS_EN` and `MEM_ACCESS_EN` shift constants immediately before the requested line range.
- Several registers contain similarly named `_MASK_MASK` constants, such as AER uncorrectable error mask fields. These names are generated from fields already named `..._MASK`; callers and reviewers must distinguish the field name from the macro suffix.
- Error status fields such as AER uncorrectable/correctable status, MSI pending bits, and parity mismatch status may have special clear semantics. Treating all fields as normal read/write fields can lose diagnostic state or fail to clear latched errors.
- Link training and equalization fields are timing-sensitive. Polling or writing related control bits without respecting hardware sequencing can destabilize PCIe link negotiation, especially around 8 GT/s and 16 GT/s equalization and margining.
- ACS, PASID, ARI, and VC controls affect isolation, address translation, traffic routing, and virtualization behavior. Incorrect programming can break IOMMU isolation, GPU compute process addressing, SR-IOV-like function routing, or peer-to-peer traffic policy.
- BAR sizing/control fields are resource-enumeration critical. Bad masks can produce incorrect aperture sizes or BAR indexes, leading to failed resource allocation or invalid MMIO mappings.
- Some fields are capability-only or reserved. The presence of a mask macro does not imply driver code may write the field.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration signals:

- Kernel build coverage for `amdgpu/nbio_v7_11.c` and any other NBIO 7.11 consumers verifies that generated macro names match helper usage.
- Static checks can compare every `REG_SET_FIELD(..., REGISTER, FIELD, ...)` use against the existence of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- Generated-header consistency tests should compare this header against the AMD register source used to produce `nbio_7_11_0_offset.h`, including paired register offsets and masks for `DEV0_EPF7` and `DEV1_EPF0`.
- Runtime smoke tests should validate GPU enumeration, BAR assignment, interrupt delivery, and basic memory access on hardware using NBIO 7.11.0.
- PCIe diagnostics should watch AER counters/logs, MSI/MSI-X masking and pending behavior, link width/speed, link retraining/equalization status, and power-management transitions after driver initialization, suspend/resume, FLR, and hot reset.
- Virtualization and compute tests should cover PASID, ACS, ARI, and IOMMU/KFD paths if the ASIC exposes those capabilities.
- Margining and high-speed link tests should confirm 16 GT/s equalization status bits, parity mismatch status, and lane margining ready/status behavior on supported platforms.

Because this is a generated register contract, a clean compile is necessary but not sufficient. The strongest signal is successful operation on matching hardware with PCIe config-space behavior agreeing with the public PCIe capability model and AMD's silicon register specification.

### subset-b-003131: lines 22131-24686

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 22131-24686

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,141 `#define` field-layout macros over 2,556 source lines, covering 377 register names and 13 address-block comments. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of the `BIF_CFG_DEV1_EPF0_LANE_3_MARGINING_LANE_STATUS` field definitions, covers PCIe lane-margining fields for lanes 4-15, root/endpoint NBIO configuration, miscellaneous NBIO control, traps, RAS/poison reporting, IOMMU L2A controls, IOAPIC feature enables, and USB4/PCIe adapter-layer controls, then ends immediately after the `BIF_CFG_DEV0_RC0_COMMAND` register comment. Adjacent chunks are needed to complete the lane 3 status register and the dev0 RC0 command register.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This chunk describes NBIO register layout for PCIe configuration, error handling, RAS signaling, IOMMU cache control, and PCIe-over-USB4 transport control. Driver code combines these macros with companion address/default headers and AMDGPU register helpers to read status, decode error state, or compose write values without hard-coding bit numbers at call sites.

## Important Macro Families

The PCIe lane-margining section covers `BIF_CFG_DEV1_EPF0_LANE_4_MARGINING_LANE_CNTL` through lane 15 plus status registers, with a tail from lane 3 status. Each lane has receiver number, margin type, usage model, and margin payload fields, mirrored by status fields. The chunk also includes router enhanced capability list and router data fields for `BIF_CFG_DEV1_EPF0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`.

The NB configuration blocks cover `NB_NBCFG0_*` PCI-compatible identity/control registers, fast-register aperture layout, and a large `nbio_iohub_nb_misc_misc_cfgdec` group. Notable fields include PCI command/status/class/header/subsystem IDs, NB PCI arbitration and control, scratch registers, revision ID, LCLK deep-sleep mask, bus-number control, MMIO and DRAM aperture bounds, SB/SW location records, software NMI/SMI/SCI/GIC-SPI controls, sync-flood controls, CAM target/index/data matching registers, VDM routing/control registers, xbar stall controls, PSP/SMU/FASTREG/MISC base-address pairs, SMU CPU block control/status, and scratch/trap infrastructure.

The trap section defines request and response plumbing: `TRAP_STATUS`, `TRAP_REQUEST0`-`TRAP_REQUEST5`, byte-enable/data payload registers, `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, response data registers, and 16 repeated trap comparators (`TRAP0` through `TRAP15`) with enable, SMU interrupt, cross-trigger, low/high address, command, address mask, and command mask fields. These macros describe a hardware filter/response path for NBIO transactions rather than software exception handling.

The bridge and interrupt section covers `SB_*` secondary-bus bridge fields, USB QoS fields, MCA SMN interrupt request/MCM/aperture/control fields, and internal sideband steering/latency fields. These definitions are integration points between NBIO, system management, interrupt routing, and PCIe bridge configuration.

The RAS groups cover `PARITY_CONTROL_*`, parity severity controls for uncorrected/corrected/UCP groups, miscellaneous severity and RAS control, RAS scratch registers, sync-flood and NMI status, internal poison status/mask, egress poison status/mask/severity fields, and APML status/control/trigger. A PSP-specific RAS block mirrors poison status reporting for `PSP_INTERNAL_POISON_STATUS` and `PSP_EGRESS_POISON_STATUS_LO/HI`.

The IOMMU `L2A` block covers performance counter selection/counts, L2 status, cache behavior controls, DTC/ITC/PTC cache invalidation and bypass/parity/way/hash controls, credit controls, update-filter controls, error-rule disable/lock fields, page-size controls, memory power-gating controls, and ECO control. These fields describe IOMMU translation-cache and memory-power behavior exposed through NBIO register space.

The final PCIe/USB4 section covers IOAPIC `FEATURES_ENABLE`, PCIe/USB4 TXAL/RXAL/AL control, hysteresis timers, error-recording mode, router path clearing, clock/power gating, PCIe control, TX power control, and master-control payload/read-request/tag overrides. The range ends as the next `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` block begins.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. The constants are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, defaults, access widths, read/write permissions, reset domains, write-one-to-clear behavior, ownership, or sequencing. Consumers must use the matching generated address/default metadata, such as NBIO 7.11.0 offset/SMN/default headers, together with AMDGPU bitfield and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate PCI config/SMN/NBIO access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU or platform code selects a register address from the companion generated register metadata.
2. It reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or creates a write value by inserting field values while preserving unrelated and reserved bits.
3. The resulting values drive PCIe configuration, error reporting, RAS handling, IOMMU setup, bridge routing, trap/cross-trigger behavior, or PCIe/USB4 link and power-management control.

The field names imply asynchronous hardware flows outside this file: PCIe lane margining, router capability discovery, CAM match/cross-triggering, trap request/response capture, parity error generation/severity routing, sync-flood propagation, poison status latching, APML NMI/sync-flood signaling, IOMMU cache invalidation and performance counting, and PCIe/USB4 adapter-layer reset/idle/reconfiguration handshakes.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO registers. Persistence depends on the GPU reset domain, PCIe reset, power and clock gating, firmware/BIOS initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes.

Represented state includes PCI configuration bits, base/limit apertures, scratch registers, bus and bridge routing state, software interrupt/status vectors, CAM/trap comparator programming, request/response payloads, parity and poison status latches, severity policies, APML trigger enables, IOMMU cache/power/performance-counter controls, and PCIe/USB4 adapter-layer reset, idle, clock-gating, and payload/tag policy bits.

Several names indicate status or latch semantics (`STATUS`, `RW1C`, `TRIGGER`, poison and sync-flood bits, trap request/response fields). The shift/mask header does not define how those bits clear or whether a read has side effects; callers must follow the hardware spec and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with sibling headers that provide register addresses and defaults. It is intended to be included through AMDGPU ASIC register include stacks under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO, PCIe, PSP/SMU, RAS, IOMMU/ATS, interrupt routing, and power-management code paths. The lane-margining and USB4 fields are relevant to PCIe link diagnostics and PCIe-over-USB4 tunneling behavior. The RAS and poison fields integrate with error logging and escalation paths such as NMI, SMI, SCI, APML, sync-flood, and SMU interrupt/cross-trigger routing. The L2A fields integrate with IOMMU translation-cache behavior and performance/debug instrumentation.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing writes to the wrong hardware bit, leading to broken PCIe configuration, missed errors, false interrupts, poisoned-transaction mishandling, IOMMU cache corruption, or unstable PCIe/USB4 link behavior.
- This chunk starts and ends mid-register-family. Whole-file reconciliation must include the preceding lane 3 status fields and following `BIF_CFG_DEV0_RC0_COMMAND` fields before treating either boundary register as complete.
- Repeated lane-margining and trap-comparator definitions are mechanically patterned. A single lane/trap mismatch can affect only one lane or comparator, making failures appear intermittent or topology-specific.
- `NB_SPARE2` exposes 32 `RW1C` fields. Read-modify-write helpers that do not account for write-one-to-clear semantics can accidentally clear latched state.
- Trap, CAM, parity error-generation, APML trigger, sync-flood, and cross-trigger fields can inject or escalate hardware events. Writes must be tightly scoped and restored after diagnostics.
- RAS severity and mask fields change whether errors are corrected, escalated, ignored, or routed to NMI/SMI/SCI/APML paths. Incorrect programming can hide fatal conditions or cause unnecessary system-level interruptions.
- Poison status/status-mask fields span low/high register pairs. Consumers must handle 64-bit status coherently and avoid mixing stale halves.
- IOMMU L2A invalidation, bypass, parity, way-disable, page-size, and memory-power-gating fields are translation-cache sensitive; incorrect values can cause address-translation faults or silent data-path instability.
- USB4 adapter-layer reset/idle/flush/reconfiguration bits describe handshake-sensitive paths. Skipping required waits or forcing pass/ignore fields can create suspend/resume, hotplug, or tunneled-PCIe failures.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches removed, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit their register width, patterned lane/trap/status fields should align, and repeated low/high status blocks should expose expected bit coverage.
- Cross-check every register name in this chunk against NBIO 7.11.0 address/default headers so field layouts map to known registers and reset values.
- On supported hardware, validate PCIe link enumeration, lane-margining diagnostics, bridge bus-number/aperture setup, hotplug or retrain paths, suspend/resume, and GPU reset recovery.
- Exercise RAS paths where available: parity injection, poison status reporting, sync-flood/NMI/APML routing, SMU interrupt/cross-trigger behavior, and clearing of latched status without losing unrelated bits.
- Exercise IOMMU/ATS workloads and fault paths while sampling L2A performance counters and cache invalidation controls; watch for translation faults, stale mappings, or parity/error-rule regressions.
- For PCIe/USB4 systems, validate tunneled PCIe traffic across reset, low-power transitions, path clear, reconfiguration, and clock-gating states, with register traces confirming reserved bits are preserved.

### subset-b-003132: lines 24687-27116

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 24687-27116

## Purpose

This chunk is an auto-generated AMD NBIO 7.11.0 shift/mask slice for PCI and PCIe configuration-space registers. It begins inside `BIF_CFG_DEV0_RC0_COMMAND`, covers the rest of the `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` root-complex configuration decode block, then starts the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint/function block and runs through the first field of `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP`.

The file does not implement executable logic. Its interface is a large set of C preprocessor constants used by AMDGPU NBIO code to extract or compose hardware register fields alongside the companion `nbio_7_11_0_offset.h` register-address macros.

## Public Surface In This Chunk

The exported API is the generated register-field convention:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask for that field.

This range contains 2,147 `#define` lines spanning 281 register names. The root-complex portion covers `BIF_CFG_DEV0_RC0_*` standard PCI header, bridge window, PM, PCIe, MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, lane equalization, ACS, data-link feature, 16 GT/s PHY, margining, and RTR capability fields. The endpoint/function portion covers `BIF_CFG_DEV0_EPF0_0_*` standard PCI header, BARs, adapter ID, PM, PCIe, MSI/MSI-X, vendor-specific, virtual-channel, serial-number, AER, header logs, TLP prefix logs, and the BAR enhanced capability header.

The range starts after the `BIF_CFG_DEV0_RC0_COMMAND` comment and after the preceding chunk's vendor/device ID definitions. It ends at `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT`; the matching mask and later BAR capability/control fields are in the following chunk.

## Important Register Families

The `BIF_CFG_DEV0_RC0` block models a PCIe root complex or bridge-style configuration space. Its standard header fields include command/status bits, class-code bytes, cache-line and latency fields, bridge bus numbering, IO/memory/prefetchable window registers, interrupt line/pin, and bridge control bits such as secondary bus reset, VGA/ISA forwarding, SERR, parity response, and discard timer status. These masks are the low-level layout used when code needs to decode the NBIO root-complex configuration image rather than relying only on generic PCI helpers.

The RC0 power and interrupt capabilities include PM capability list, PM capability/status-control, MSI message control/address/data, SSID, and MSI-map capability fields. PCIe base capability fields cover device capability/control/status, link capability/control/status, slot and root capability/control/status, and PCIe 2.0 `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields. These names expose common controls and state such as max payload size, relaxed ordering, no-snoop, error reporting enables, function-level reset, target link speed, retraining, ASPM, negotiated link width/speed, equalization state, and root PME/error status.

The RC0 extended capability groups include vendor-specific headers and payload registers, virtual-channel capability/control/status and VC0/VC1 resource control/status, device serial number doublewords, and Advanced Error Reporting. AER fields define uncorrectable status/mask/severity bits for data link protocol, surprise-down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, and correctable internal errors. Header-log and TLP-prefix-log registers are full-width fields.

The RC0 secondary PCIe and link-training groups define `LINK_CNTL3`, lane error status, per-lane equalization controls for lanes 0-15, 16 GT/s equalization controls, local/RTM parity mismatch status, lane margining control/status for lanes 0-15, ACS capability/control bits, data-link feature capability/status, PHY 16 GT/s capability/control/status, and RTR capability/data fields. These are integration points for link bring-up, diagnostics, PCIe Gen4/16 GT/s training, lane margining, isolation policy, and data-link feature reporting.

The `BIF_CFG_DEV0_EPF0_0` block starts at the generated address-block marker for endpoint function 0. It defines endpoint-style vendor/device ID, command/status, revision and class-code bytes, cache/latency/header/BIST, six BAR registers, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor capability list, and writable adapter ID fields. Its PM and PCIe capability fields mirror endpoint-facing state: PM state/PME control, PCIe device/link capabilities and controls, PCIe 2.0 capabilities, MSI message controls and mask/pending registers, MSI-X table/PBA fields, vendor-specific extended capability, virtual channel resources, serial number, and AER status/mask/severity/log controls.

The EPF0 chunk ends in the BAR enhanced capability list and the first `BAR1_CAP` shift. The corresponding offset header places this block at base address `0x10140000` with `regBIF_CFG_DEV0_EPF0_0_PCIE_BAR_ENH_CAP_LIST` at `0x10080` and `regBIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP` at `0x10081`, both using base index 5.

## Control Flow And State

There is no runtime control flow in this header slice. The effective flow is compile-time macro substitution:

1. A translation unit includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`.
2. Driver code obtains a raw register value using an AMDGPU register access helper and a `reg...` offset macro from the offset header.
3. The caller uses `REG_GET_FIELD`, `REG_SET_FIELD`, direct mask/shift arithmetic, or similar AMDGPU helper patterns to decode or construct a field value from the generated `*_MASK` and `*__SHIFT` constants.

The header stores no C state and has no persistence layer. Persistent state is the hardware state in NBIO PCI/PCIe configuration registers. Many fields in this chunk represent state that can outlive a single register read: bridge apertures, bus numbering, BAR sizing, PM state, MSI/MSI-X routing, link speed/width and equalization state, AER mask/status/severity, VC allocation, ACS policy, lane margining results, and BAR enhanced capability support.

Some hardware status fields may be latched or write-one-to-clear according to their PCIe/NBIO semantics. This header only names bit positions; it does not encode access permissions, side effects, reset values, valid value ranges, or sequencing requirements.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`. That header defines the corresponding `regBIF_CFG_DEV0_RC0_*` offsets under `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` with base address `0x10100000`, and `regBIF_CFG_DEV0_EPF0_0_*` offsets under `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` with base address `0x10140000`. This directory has `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`; unlike some nearby NBIO generations, there is no visible `nbio_7_11_0_default.h` in this tree.

The only direct C include found for this exact header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio/nbio_7_11_0_offset.h` and `nbio/nbio_7_11_0_sh_mask.h`. That file uses the same generated macro family through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `REG_SET_FIELD`, although this specific chunk is primarily PCI/PCIe configuration-space layout rather than doorbell or HDP helper logic.

The semantic dependencies are the PCI and PCI Express specifications for standard configuration headers, bridge windows, PM capability, MSI/MSI-X, PCIe capability, AER, virtual channels, secondary PCIe/link equalization, ACS, data-link feature capability, 16 GT/s PHY capability, lane margining, RTR, vendor-specific capability layout, and BAR enhanced capability layout. The generated names encode those layouts but do not validate legal combinations.

## Risks And Maintenance Notes

- The assigned range is a partial slice: it starts after the `BIF_CFG_DEV0_RC0_COMMAND` register comment and ends before the complete `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP` definition. Adjacent chunks are required for a whole-register view at both boundaries.
- Masks and shifts are hardware ABI. A one-bit drift between this file and NBIO 7.11.0 silicon, firmware tables, or the offset header can silently decode the wrong PCIe state or program the wrong control bit.
- Several fields control externally visible PCIe behavior: bus mastering, memory enable, bridge apertures, PM/PME state, MSI/MSI-X routing, link retrain/target speed, AER masking/severity, ACS isolation, VC resource negotiation, lane equalization, lane margining, and BAR sizing. Incorrect writes can affect enumeration, DMA, interrupt delivery, error containment, isolation, or link stability.
- Status and error fields in AER, link status, lane error, parity mismatch, margining status, and root status may have side effects when cleared. The presence of a mask does not imply that a read-modify-write is safe.
- Cross-generation similarity is high but not exact. Nearby NBIO headers show differences such as the presence or absence of certain command bits and BAR mask widths, so these constants should not be reused for other NBIO versions.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0xFFF00000L` rely on the established AMDGPU unsigned 32-bit register-helper context. Ad hoc use in signed or narrower expressions can introduce truncation or sign-extension bugs.
- The repetitive lane and AER definitions are generation output, making manual review error-prone. Automated structural checks are more reliable than visual inspection for verifying shift/mask alignment.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` and any SOC paths that include the NBIO 7.11.0 offset and shift/mask headers.
- Static checks that every complete field in the chunk has a matching `*_MASK` and `*__SHIFT` pair, with the expected alignment between mask low bit and shift value. The known exception at this chunk boundary is `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT`, whose mask is outside the assigned range.
- Cross-header checks that each complete `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV0_EPF0_0_*` register family in this range has a matching `reg...` offset and `_BASE_IDX` in `nbio_7_11_0_offset.h`.
- Runtime PCIe/NBIO dumps on NBIO 7.11 hardware comparing decoded vendor/device IDs, command/status, class code, BARs, bus windows, PM state, MSI/MSI-X state, negotiated link speed/width, PCIe 2.0 controls, AER masks/status, VC resources, ACS controls, lane equalization, 16 GT/s state, margining results, and BAR enhanced capability fields against `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path validation that AER status/mask/severity and header/TLP-prefix logs are decoded and cleared with the intended bits only.
- Link-training and power-management tests around retrain-link, target-speed changes, equalization completion, lane error reporting, 16 GT/s status, lane margining commands/status, PME, and low-power link states.

### subset-b-003133: lines 27117-29591

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 27117-29591

## Scope

This chunk covers a generated AMD NBIO 7.11.0 register shift/mask slice for NBIF PCIe configuration fields. It starts mid-register at `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP`, continues through the tail of the `DEV0_EPF0` PCIe extended capability space, then enters `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and defines most of the `DEV0_EPF1` PCI/PCIe configuration-space field layout through the beginning of 16 GT/s lane equalization. The range contains 2,103 `#define` entries and 370 generated register/comment records.

The file section is data only. It exports preprocessor constants for field bit positions and masks; it has no C functions, structs, runtime variables, allocation, locking, persistence code, or executable control flow.

## Purpose

The chunk supplies the bit-level ABI between AMDGPU NBIO 7.11 code and PCIe/NBIF hardware registers. Each generated field follows the normal AMD register-header convention:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the raw mask used to isolate, clear, or compose that field.

Consumers combine these constants with matching register offsets from `nbio_7_11_0_offset.h` and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. The macros in this slice describe PCIe endpoint function configuration spaces, capability records, error-reporting state, link-training controls, I/O virtualization capabilities, and GPU I/O virtualization/vendor-specific records.

## Important Macro Families

### DEV0 EPF0 Extended Capability Tail

The first part of the chunk finishes the `BIF_CFG_DEV0_EPF0_0` enhanced capability area. It starts after the `PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT` definition from the previous chunk, so this range owns only the BAR1 mask plus the following BAR control fields. The BAR and VF resizable-BAR groups expose supported BAR sizes, BAR index, total BAR count, active size, and upper supported-size bits for BAR1 through BAR6.

Power and latency capability groups include Power Budgeting, Dynamic Power Allocation, Latency Tolerance Reporting, and L1-related endpoint capability fields. DPA fields cover substate maximums, transition latency unit/value fields, power allocation scale, selected substate status/control, and per-substate power allocations. LTR fields expose snoop and non-snoop latency values and scales.

The secondary PCIe capability group defines `PCIE_LINK_CNTL3`, lane error status, and per-lane 8 GT/s equalization controls for lanes 0 through 15. Each lane has downstream/upstream TX preset fields and RX preset-hint fields. The later 16 GT/s capability block adds link status, parity mismatch status, and per-lane 16 GT/s DSP/USP TX preset controls.

Isolation, address translation, and virtualization capability groups include ACS, ATS, Page Request Interface, PASID, ARI, SR-IOV, multicast, data link feature exchange, lane margining, VF resizable BARs, RTR data registers, and a GPU IOV vendor-specific enhanced capability header. Important fields include ACS source validation and peer-to-peer redirect controls, ATS enable and smallest translation unit, PRI response failure/reset/status bits, PASID execution and privileged-mode support/enables, SR-IOV VF enable/MSE/ARI/ten-bit tag controls, VF counts/stride/device ID/page sizes/VF BARs, and multicast receive/block vectors.

Lane margining definitions cover the PCIe margining enhanced capability plus lane 0 through lane 15 control/status pairs. These fields report receiver number, margin type, payload/usage mode, sampling reporting method, voltage/timing offset support, maximum lanes, independent error sampler support, margin software ready status, and per-lane control/status values such as margin payload, software ready, error count, sampler active, setup error, margining voltage/timing status, and lane number.

### DEV0 EPF1 Standard PCI Header And Capabilities

The chunk switches to `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and begins a new `BIF_CFG_DEV0_EPF1_0` function block. The initial registers model a conventional PCI endpoint header: vendor and device IDs, command/status bits, revision and class code bytes, cache line, latency, header type, BIST, base address registers 1 through 6, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability entries.

Power management and PCIe capability fields cover PM capability/status-control, PCIe capability header/type, device capability/control/status, link capability/control/status, and PCIe 2.0 device/link fields. The definitions include payload/read-request sizes, relaxed ordering, no-snoop, error reporting enables, FLR, link speed/width, ASPM, retraining, common clock, extended sync, target link speed, compliance, hardware autonomous speed disable, equalization request/status, supported link speeds, and completion-timeout controls.

MSI and MSI-X groups define capability-list headers, message control, 32-bit and 64-bit message address/data fields, per-vector masks, pending bits, MSI-X table/PBA BAR indicators and offsets, and MSI-X function mask/enable controls. Vendor-specific capability groups expose capability IDs, versions, next pointers, VSEC ID/revision/length, and two vendor data registers.

### DEV0 EPF1 Error Reporting And BAR/Power Extensions

The EPF1 AER group defines enhanced capability headers, uncorrectable error status/mask/severity fields, correctable error status/mask fields, AER capability/control bits, TLP header logs, and TLP prefix logs. The error bit names cover data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.

The EPF1 BAR, power-budgeting, DPA, secondary PCIe, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, data link feature, and 16 GT/s PHY capability families repeat the same layout pattern as EPF0 for a second endpoint function. This repetition is intentional and function-scoped: identical field names after the prefix refer to different PCIe function register images.

The chunk ends at the comment for `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`. The shifts and masks for EPF1 16 GT/s lanes 4 through 15 are outside this range and belong to the adjacent next chunk.

## Control Flow And State Behavior

There is no software control flow in this header slice. Its behavior is compile-time substitution:

1. A translation unit includes `nbio_7_11_0_sh_mask.h`.
2. Driver code reads or prepares an NBIO/PCIe register value through a matching address macro.
3. The caller applies `*_MASK` and `*_SHIFT` constants, usually through AMDGPU field helpers, to decode or update a specific hardware field.

The header itself stores no state. Persistent and sticky state lives in the GPU's NBIF PCIe configuration registers and is changed only by hardware, firmware, the PCI core, or driver code outside this header. Some fields describe durable configuration, such as command enables, BAR sizes, MSI/MSI-X programming, PASID/ATS/PRI/SR-IOV controls, ACS routing controls, multicast tables, LTR latency values, DPA substate controls, link controls, and VF BAR sizing. Other fields are hardware status or logs, such as PCI status bits, device/link status, AER status and header logs, lane error status, 16 GT/s equalization status, parity mismatch status, margining status, DPA status, PRI status, and data-link feature status.

Several fields are action-like or side-effect-sensitive when written by owning code. Examples include link retrain, FLR, PRI reset, SR-IOV VF enable, MSI/MSI-X enable/mask bits, DPA substate control, ATS/PASID enables, data-link feature exchange enable, and margining software-ready/control bits. The masks only define bit positions; they do not encode PCIe sequencing, polling, write-one-to-clear behavior, or firmware coordination rules.

## Dependencies And Integration Points

The direct generated-header dependency is `nbio_7_11_0_offset.h`, which supplies the matching register offsets and identifiers for these fields. Unlike some older NBIO generations in this tree, this NBIO 7.11.0 header set only has offset and shift/mask headers visible under `include/asic_reg/nbio`; no sibling `nbio_7_11_0_default.h` or `nbio_7_11_0_smn.h` file was present in this checkout.

The concrete source-tree integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio_7_11_0_offset.h` and this shift/mask header. That NBIO implementation uses SOC15 and PCIe-port register access helpers to program HDP remaps, memory-controller access, SDMA/VPE/VCN/IH doorbell ranges, doorbell apertures, interrupt controls, PCIe/USB4 master controls, and related NBIO state. Display resource code for DCN 3.5/3.5.1 includes the companion offset header, tying this register namespace into display bring-up even when it does not directly include the mask header.

The semantic dependencies are PCI and PCI Express capability layouts: standard endpoint configuration header, PM capability, PCIe device/link capability, MSI/MSI-X, vendor-specific capabilities, device serial number, Advanced Error Reporting, resizable BAR, Power Budgeting, Dynamic Power Allocation, Secondary PCIe/equalization, ACS, ATS, Page Request Interface, PASID, multicast, LTR, ARI, SR-IOV, data link feature, 16 GT/s PHY capability, lane margining, and AMD GPU IOV/RTR vendor-specific records.

## Risks And Maintenance Notes

- The range is mechanically generated and highly repetitive. EPF0 and EPF1 contain many parallel capability families where only the function prefix changes, making generation drift or copy/paste review errors difficult to spot.
- Chunk boundaries split complete definitions. The first line is only the `BAR1_CAP` mask after its shift appeared in the previous chunk, and the last line is only the comment for EPF1 lane 4 16 GT/s equalization before its fields appear in the next chunk.
- Wrong masks in command, BAR, MSI/MSI-X, SR-IOV, ATS, PASID, ACS, PRI, or VF BAR fields can affect DMA reachability, interrupt delivery, virtualization isolation, IOMMU translation behavior, and guest-visible PCI configuration.
- Status, mask, severity, enable, and control fields have different hardware semantics even when their field names are similar. AER status/mask/severity registers are especially easy to confuse.
- Some hardware status bits may be sticky, write-one-to-clear, firmware-owned, or updated asynchronously by PCIe link logic. Generic read-modify-write code must respect the owning register's hardware rules instead of relying on the mask name alone.
- Link management fields for 8 GT/s and 16 GT/s equalization, lane error status, parity mismatch status, target link speed, retraining, and data link feature exchange can affect link stability and performance if programmed out of sequence.
- Lane margining and 16 GT/s equalization fields are compliance/debug oriented. Using the masks outside tested diagnostic flows can disturb the link partner or produce misleading signal-integrity results.
- Integer constants use the existing AMD style with `L` suffixes and full-width masks such as `0xFFFFFFFFL`; consumers should keep the established 32-bit register helper types to avoid signedness or truncation issues.
- These definitions are NBIO 7.11.0-specific and should not be mechanically reused for other NBIO versions without comparing the version-specific generated offset and mask headers.

## Test And Validation Signals

Useful validation signals for this chunk include:

- Build coverage for translation units that include `nbio_7_11_0_sh_mask.h`, especially `amdgpu/nbio_v7_11.c`.
- Static generated-header checks that every complete register field in the slice has consistent `*_SHIFT` and `*_MASK` pairs, masks are aligned with shifts, and repeated lane/function families have the expected per-lane or per-function coverage.
- Cross-header checks that `BIF_CFG_DEV0_EPF0_0_*` and `BIF_CFG_DEV0_EPF1_0_*` register names in this slice have matching register offset definitions in `nbio_7_11_0_offset.h`.
- PCI enumeration and config-space dumps on NBIO 7.11 hardware comparing decoded vendor/device IDs, class/header fields, BARs, PM, PCIe link/device state, MSI/MSI-X, serial number, AER, resizable BAR, ACS, ATS, PASID, PRI, SR-IOV, LTR, DPA, multicast, DLF, 16 GT/s, and margining capability records against `lspci -vvxxx` or AMDGPU debug register reads.
- Interrupt tests covering MSI and MSI-X enable/mask/table/PBA fields, plus AMDGPU IH behavior after NBIO initialization.
- Virtualization and IOMMU tests covering ATS, PASID, PRI, ARI, SR-IOV VF counts/stride/device IDs/VF BARs, ACS isolation controls, and GPU IOV vendor-specific capability exposure.
- PCIe error-path tests or platform AER injection validating uncorrectable/correctable error status, masks, severity, AER capability/control, TLP header logs, and prefix logs without touching unrelated bits.
- Link validation covering target speed, retrain behavior, 8 GT/s and 16 GT/s equalization state, lane error status, parity mismatch status, data link feature exchange, and lane margining diagnostics across all available lanes.
- Power-management validation around Power Budgeting, DPA substates, LTR latency values, PM capability state, ASPM-related link controls, suspend/resume, and runtime power transitions.

## Unresolved Cross-Chunk References

The previous chunk owns the `BIF_CFG_DEV0_EPF0_0_PCIE_BAR_ENH_CAP_LIST` definitions and the `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT` line immediately before this range. The next chunk owns `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT` and the remaining EPF1 16 GT/s lane equalization controls. The merge/reconciliation lane should stitch those boundaries when creating the final per-file research document.

### subset-b-003134: lines 29592-32042

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 29592-32042

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains only preprocessor constants for hardware register bitfields; there are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The slice starts in the middle of `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`, covers the tail of the `BIF_CFG_DEV0_EPF1_0` endpoint-function capability layout, then defines the complete `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space shift/mask block. It then begins the `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block and stops inside `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP`. Adjacent chunks are required for the beginning of the EPF1 lane-4 equalization register and the remaining EPF3 ARI capability/control and later capability fields.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` provides the field-layout half of the generated NBIO register interface for AMD GPU drivers. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`: the starting bit position.
- `<REGISTER>__<FIELD>_MASK`: the shifted mask used to isolate, preserve, clear, or compose the field.

Runtime code combines these macros with address definitions from `nbio_7_11_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The local NBIO 7.11 implementation, `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, includes this exact shift/mask header and uses that helper pattern.

## Important Macro Families

The EPF1 tail covers advanced PCIe link and capability fields:

- `BIF_CFG_DEV0_EPF1_0_LANE_[4-15]_EQUALIZATION_CNTL_16GT` provides 16 GT/s downstream/upstream transmit preset fields. The lane-4 register is only partially inside this chunk; lanes 5-15 are complete here.
- `BIF_CFG_DEV0_EPF1_0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` describe PCIe lane-margining capability discovery and software-readiness bits.
- `BIF_CFG_DEV0_EPF1_0_LANE_[0-15]_MARGINING_LANE_CNTL` and `..._STATUS` repeat the same per-lane layout: receiver number, margin type, usage model, and 8-bit margin payload/status fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VF_RESIZE_BAR_ENH_CAP_LIST` and `PCIE_VF_RESIZE_BAR[1-6]_{CAP,CNTL}` describe virtual-function resizable BAR support and control fields, including BAR index, total BAR count, selected size, and upper supported-size bits.
- `BIF_CFG_DEV0_EPF1_0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` expose Readiness Time Reporting fields for reset, data-link-up, FLR, D3hot-to-D0 timing, and validity.

The EPF2 block is complete in this slice and mirrors a full endpoint-function PCI/PCIe configuration image:

- Conventional PCI identity and header fields: vendor/device IDs, command/status, revision/class codes, cache line, latency, header, BIST, BARs 1-6, adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, and maximum latency.
- Vendor and power-management capability fields: `VENDOR_CAP_LIST`, writable adapter ID, `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus PCIe capability 2 fields for completion timeouts, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, FRS, supported link speeds, equalization status, and compliance controls.
- MSI/MSI-X fields: capability headers, MSI enable/multiple-message/64-bit/per-vector/extended-data controls, message address/data registers, masks, pending bits, MSI-X table/PBA BIR and offsets, function mask, and enable bit.
- SATA capability/IDP fields: SATA capability revision, BAR location/offset, index, and data registers.
- Vendor-specific enhanced capability fields: VSEC header and two full-width scratch dwords.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity for DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked; correctable error status/mask; AER capability/control; four TLP header-log dwords; and four TLP-prefix-log dwords.
- Resizable BAR, power, and DPA fields: `PCIE_BAR[1-6]_{CAP,CNTL}`, power budget capability/data selection/data, DPA capability/latency/status/control, and DPA substate power allocation 0-7.
- Isolation and address-space capabilities: ACS capability/control, PASID capability/control, ARI capability/control, and RTR data.

The EPF3 block repeats the same generated endpoint-function layout from vendor/device identity through most of the advanced PCIe capabilities:

- It covers the full conventional header, PM, PCIe device/link capability, MSI/MSI-X, SATA, VSEC, AER, header/TLP-prefix logs, resizable BAR, power budget, DPA, ACS, and PASID sections.
- It reaches `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_ENH_CAP_LIST` and the first five field definitions of `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP`, ending after the `ARI_ACS_FUNC_GROUPS_CAP_MASK`. The `ARI_NEXT_FUNC_NUM_MASK`, `PCIE_ARI_CNTL`, and any later EPF3 registers continue outside this work item.

## APIs, Types, And Functions

There are no callable APIs or C data types in this range. The public interface is the generated macro namespace. Macro values are integer constants, mostly `L`-suffixed masks, that encode bit geometry only.

These definitions do not encode register addresses, reset values, read/write permissions, write-one-to-clear behavior, reserved-bit policy, access size, firmware ownership, or operation ordering. Consumers must pair them with `nbio_7_11_0_offset.h`, the appropriate AMDGPU register access path, and hardware-specific knowledge of each field's semantics.

## Control Flow And Runtime Behavior

This header has no local control flow. The runtime flow implied by these constants is:

1. AMDGPU or platform firmware code selects the appropriate NBIO/PCIe register address for the active endpoint function and register instance.
2. Code reads a register and decodes fields with `*_MASK` and `*__SHIFT`, or composes a new value with `REG_SET_FIELD` while preserving unrelated bits.
3. The resulting hardware state participates in PCIe endpoint enumeration, BAR sizing, MSI/MSI-X routing, link training, link equalization, lane margining, power management, DPA substate management, ACS/PASID/ARI isolation and address-space controls, AER error reporting, and readiness-time reporting.

Several represented fields are asynchronous protocol or hardware state rather than simple software-owned values: PCIe link speed/width/training, equalization completion and phase success, lane-margining status, PME status, MSI/MSI-X pending/masking, AER status and logs, DPA substate status, and readiness-time validity.

## State And Persistence Behavior

The header owns no state and persists nothing. The represented state lives in NBIO 7.11.0 hardware registers and PCIe configuration-space views.

State categories described by this chunk include:

- EPF1 link-training and diagnostics state for 16 GT/s lane equalization, lane margining control/status, VF resizable BAR controls, and readiness-time reporting.
- EPF2 and EPF3 conventional PCI configuration state: identity, command/status, BARs, ROM BAR, capability pointers, interrupt line/pin, and class/revision fields.
- PCIe endpoint policy: payload/read-request sizing, relaxed/no-snoop ordering, completion timeout, function-level reset, ARI forwarding, atomic operations, LTR/OBFF, ten-bit tags, end-to-end TLP prefix behavior, target link speed, compliance mode, and link disable/retrain controls.
- Interrupt routing and pending state for MSI and MSI-X, including 32-bit and 64-bit message address/data variants, mask registers, pending bits, MSI-X table/PBA offsets, function masking, and enable controls.
- Error-observation and error-policy state for AER status, masks, severity, ECRC generation/checking, first-error pointer, multi-header capture, header logs, and TLP-prefix logs.
- Resource sizing and power management state for resizable BARs, power budget data, DPA capability/status/control, and DPA substate power allocations.
- Isolation and process-addressing controls through ACS, PASID, and ARI capability/control registers.

Retention across GPU reset, PCI reset, FLR, BACO, suspend/resume, runtime power transitions, or firmware reinitialization is not specified by the macros. Driver initialization and restore paths must reprogram any non-retained policy registers and must observe hardware-specific status/log clearing rules.

## Dependencies And Integration Points

Primary generated dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h` for matching register addresses and base indices. This NBIO generation has an offset header; no sibling `nbio_7_11_0_smn.h` or `nbio_7_11_0_default.h` file is present in the local tree.
- Adjacent chunks of `nbio_7_11_0_sh_mask.h`, because this range begins inside an EPF1 lane equalization register and ends inside an EPF3 ARI capability register.
- AMDGPU helper macros and SOC15/NBIO accessors that consume generated shift/mask definitions.

Integration areas include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h` and uses generated field macros for NBIO programming.
- PCIe endpoint setup, enumeration, BAR sizing, resizable BAR and VF resizable BAR support, MSI/MSI-X setup, link training/equalization diagnostics, lane margining diagnostics, and readiness-time reporting.
- GPU reset, FLR, suspend/resume, and runtime power-management paths that must restore PCIe/NBIO policy fields and avoid losing diagnostic status.
- Error handling and RAS-adjacent paths that read AER status/mask/severity fields and capture header/TLP-prefix logs before clearing status bits.
- Virtualization/IOMMU/KFD-adjacent paths that depend on ACS, PASID, ARI, BAR, and interrupt-routing behavior for isolation and per-process addressing.

## Risks And Edge Cases

- Generated mask/shift drift can compile cleanly while causing wrong-bit programming. In this chunk that can affect BAR sizing, endpoint enablement, interrupts, link behavior, power management, AER policy, isolation, or PASID/ARI behavior.
- The range is highly repetitive across EPF2 and EPF3. A generator or manual correction error can be topology-dependent if one endpoint function differs while another remains correct.
- Status, mask, and severity registers have very similar names. Confusing AER `*_STATUS`, `*_MASK`, and `*_SEVERITY` fields can either hide errors or report them with the wrong severity.
- Some PCIe status and AER fields are usually write-one-to-clear or log-sensitive, but that access behavior is not visible in this header. Code must capture header and prefix logs before clearing related status bits.
- MSI/MSI-X address/data, mask, pending, table, and PBA fields are interrupt-routing sensitive. Bad restore values or wrong masks can misroute, suppress, or spuriously trigger interrupts.
- Link-control, equalization, lane-margining, DPA, and power-management fields can trigger asynchronous hardware transitions. Callers need timeout and recovery handling outside this header.
- ACS, PASID, and ARI controls affect DMA isolation, address-space tagging, and function routing. Misprogramming can break peer-to-peer traffic, virtualization isolation, or process-address-space semantics.
- The source boundaries are artificial: EPF1 lane-4 equalization is incomplete at the start, and EPF3 ARI capability is incomplete at the end. Reconciliation must not treat those boundary omissions as source defects.

## Test And Validation Signals

Useful validation combines generated-header checks with hardware-facing tests:

- Build AMDGPU configurations that include NBIO 7.11 support to catch missing or renamed generated symbols.
- Run mechanical consistency checks over the assigned range: every complete field should have both a `__SHIFT` and `_MASK`, masks should match the intended bit positions, and repeated EPF2/EPF3 register layouts should match where the hardware template is expected to be identical.
- Cross-check field names against `nbio_7_11_0_offset.h` so every complete register family in this chunk has a matching address definition where expected.
- Exercise PCIe endpoint enumeration and resource programming on supported hardware: command/status bits, BAR/ROM BAR sizing, VF resizable BARs, MSI/MSI-X delivery, interrupt masking, and reset/FLR restore.
- Validate link and diagnostics paths: negotiated link speed/width, 16 GT/s equalization presets, link-control/status2 fields, lane margining command/status readback, and readiness-time reporting validity.
- Exercise error paths where hardware validation permits: AER correctable and uncorrectable status/mask/severity reporting, ECRC controls, first-error pointer, header-log capture, and TLP-prefix-log capture before status clear.
- Validate power and isolation features: power budget and DPA substate fields, ACS policy bits, PASID enable/width and privilege/execute controls, and ARI capability/control behavior.

## Chunk Boundary Notes

Line 29592 is already inside `BIF_CFG_DEV0_EPF1_0_LANE_4_EQUALIZATION_CNTL_16GT`; only the lane-4 DSP/USP 16 GT/s preset shift/mask lines are visible here. The register comment and any earlier lane-4 fields belong to the previous chunk.

Line 32042 stops after `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP__ARI_ACS_FUNC_GROUPS_CAP_MASK`. The remaining EPF3 ARI capability mask for `ARI_NEXT_FUNC_NUM`, the EPF3 ARI control register, and later EPF3 registers continue in the next chunk. Merge/reconciliation should stitch both boundaries before producing the final per-file research document.

### subset-b-003135: lines 32043-34496

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 32043-34496

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.11.0 register mask header. It begins at the tail of the `BIF_CFG_DEV0_EPF3_0` PCIe enhanced-capability area, fully covers the `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` address blocks, and ends inside the early `BIF_CFG_DEV0_EPF6_0` PCIe capability fields.

The covered register families include:

- Function 3 tail fields for ARI control and reset-time reporting (`PCIE_ARI_CNTL`, `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`).
- Function 4 and function 5 PCI configuration header fields, including vendor/device IDs, command/status, class/revision, BARs, ROM BAR, subsystem IDs, capability pointer, interrupt line/pin, and latency/grant fields.
- Function 4 and function 5 PCI power-management and PCIe capability fields, including device/link capabilities, control, status, capability version, payload/read-request sizing, FLR, ASPM-related link fields, LTR, OBFF, ten-bit tags, atomic operations, DRS, and equalization status.
- Function 4 and function 5 MSI and MSI-X capability fields, including message control, 32-bit and 64-bit address/data fields, mask and pending bits, table BIR/offset, PBA BIR/offset, and MSI-X enable/function-mask state.
- Function 4 and function 5 SATA capability and IDP index/data windows.
- Function 4 and function 5 PCIe vendor-specific, AER, BAR enhanced capability, power-budget, DPA, ACS, PASID, ARI, and RTR capability fields.
- Function 6 header, PM, base PCIe capability, device/link capability, control, and status fields through `LINK_CAP2`.

The file is a generated hardware register bitfield map. It defines C preprocessor constants only; this chunk contains no functions, structs, variables, storage, or executable control flow.

## Purpose

This header section provides the bit-level ABI used by AMDGPU NBIO code and other register consumers when composing or decoding NBIO 7.11.0 PCI configuration-space register values. Each field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field.

The sibling `nbio_7_11_0_offset.h` file supplies register addresses and base indices, such as `regBIF_CFG_DEV0_EPF4_0_DEVICE_CNTL`, `regBIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV0_EPF6_0_LINK_CAP2`. This file supplies the matching field layouts. Driver code normally consumes these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

The macro names identify NBIO device 0 endpoint functions. The repeated `EPF4`, `EPF5`, and `EPF6` blocks model separate PCIe endpoint-function configuration spaces with mostly identical PCI/PCIe capability layouts but distinct offsets and hardware instances.

## Important Macro Families

### PCI Configuration Header Fields

The `BIF_CFG_DEV0_EPF4_0_*`, `BIF_CFG_DEV0_EPF5_0_*`, and partial `BIF_CFG_DEV0_EPF6_0_*` header fields describe normal PCI configuration-space state:

- `VENDOR_ID` and `DEVICE_ID`.
- `COMMAND` bits for I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, SERR, fast back-to-back, and interrupt disable.
- `STATUS` bits for immediate readiness, interrupt status, capability-list presence, target/master aborts, and system-error reporting.
- Revision, programming interface, subclass, base class, cache line, latency, header type, device type, and BIST fields.
- Six `BASE_ADDR_*` BAR fields, `ROM_BASE_ADDR`, `ADAPTER_ID`, `ADAPTER_ID_W`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- `VENDOR_CAP_LIST` capability-header fields for vendor-defined capability ID, next pointer, and length.

These fields are the most conventional part of the chunk. They expose how the endpoint function appears to PCI enumeration and how the OS-visible PCI command/status and BAR state is represented in NBIO register space.

### Power Management and Base PCIe Capability

The PM capability group includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. It defines PM capability versioning, PME support, D1/D2 support, auxiliary current, immediate readiness on D0 return, power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data fields.

The base PCIe capability group includes `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for the full function 4 and 5 ranges. Function 6 is covered through `LINK_CAP2`.

Important encoded behavior includes:

- Max payload support and selected max payload size.
- Max read request size.
- Correctable, non-fatal, fatal, and unsupported-request reporting enables.
- Relaxed ordering, extended tags, phantom functions, no-snoop, auxiliary power PM, and FLR initiation/capability.
- Link speed, width, PM support, L0s/L1 latency, clock power management, link disable/retrain, common clock, extended sync, link bandwidth notification, autonomous bandwidth interrupt, DRS signaling, and DL active state.
- Completion-timeout range, timeout disable support/control, ARI forwarding support/control, atomic operation support/control, ID-based ordering, LTR, OBFF, ten-bit tags, end-to-end TLP prefixes, emergency power reduction, and FRS.
- Link-speed-generation support, crosslink support, SKP ordered-set support, RTM presence detection, DRS support, target link speed, compliance-mode controls, de-emphasis, equalization phase status, downstream component presence, and DRS message received.

These fields are integration points for PCIe bring-up, power management, reset, link diagnostics, and capability discovery. They are also easy to confuse because function 4 and 5 layouts are mechanically repeated.

### MSI and MSI-X Capabilities

Function 4 and 5 expose both MSI and MSI-X capability field macros:

- MSI list and message control fields include enable, multiple-message capable/enabled, 64-bit capability, per-vector masking capability, extended message data capability, and extended message data enable.
- MSI message address/data fields cover low/high address, data, extended data, 64-bit data variants, mask, and pending arrays.
- MSI-X fields include capability list, table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.

These definitions matter for interrupt delivery and masking. They describe hardware-visible MSI/MSI-X configuration-space fields, but interrupt setup sequencing is owned by PCI/AMDGPU code outside this generated header.

### SATA and IDP Capability Fields

Function 4 and 5 include SATA capability fields:

- `SATA_CAP_0` exposes capability ID, next pointer, major/minor revision, and reserved bits.
- `SATA_CAP_1` exposes BAR location and BAR offset.
- `SATA_IDP_INDEX` and `SATA_IDP_DATA` expose an indexed data path with index and data fields.

These are capability-structure definitions for endpoint functions that expose SATA-style or SATA-compatible capability state through PCI configuration space. The IDP index/data fields imply indirect access semantics; the header defines bit positions, not the ordering rules for safe indirect reads/writes.

### Vendor-Specific and Advanced Error Reporting

Function 4 and 5 define PCIe vendor-specific enhanced capability fields (`PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`). The list/header macros encode capability ID, version, next pointer, VSEC ID, VSEC revision, VSEC length, and scratch fields.

The AER group is larger and includes:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`.

Uncorrectable error bits include data-link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, and internal correctable error. The capability/control fields include first-error pointer, ECRC generation/check capabilities and enables, and multi-header record support.

These macros are central to PCIe RAS and diagnostics. The log fields carry captured TLP header and prefix data after AER events.

### BAR Enhanced Capability, Power Budget, DPA, ACS, PASID, ARI, and RTR

Function 4 and 5 include a dense set of PCIe extended capability definitions:

- `PCIE_BAR_ENH_CAP_LIST` plus `PCIE_BAR1_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL`, encoding supported BAR sizes, BAR index, total BAR count, selected size, and upper supported-size bits.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`, encoding selected power-budget table entry, base power, scale, PM sub-state, PM state, type, rail, and system allocation.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0..7`, encoding dynamic power allocation substates, transition latency units/values, power allocation scaling, substate status/control, and per-substate allocation values.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, encoding source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, egress control vector size, and their enables.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`, encoding PASID execute-permission support, privileged-mode support, max PASID width, and enables.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, encoding next function number, MFVC/ACS function group enables, and ARI function group.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, encoding reset-time reporting capability metadata plus reset, DL-up, FLR, and D3hot-to-D0 timing values.

These extended capabilities have direct implications for virtualization, IOMMU integration, peer-to-peer routing, power budgeting, reset delay handling, BAR sizing, and PCIe error containment.

## Control Flow and State Behavior

This chunk has no runtime control flow. It affects behavior at compile time by giving C code symbolic field positions for 32-bit MMIO or PCI configuration-space register values.

The state described by the macros is hardware state, not software state stored in the header. Examples include:

- PCI command/status and BAR configuration state for endpoint functions.
- PM capability status/control state, including current power state and PME status.
- PCIe device/link capability and control state, including negotiated link status and reset/FLR controls.
- MSI/MSI-X address, data, mask, pending, and enable state.
- AER status/mask/severity bits plus captured header and TLP prefix logs.
- ACS/PASID/ARI state that can affect requester identity, isolation, peer-to-peer routing, and function enumeration.
- Power-budget and DPA table/control state.
- Reset-time reporting values used to communicate reset, DL-up, FLR, and D3hot-to-D0 timing.

Some fields are durable configuration bits, some are live status bits, some are capability readouts, and some are action-oriented controls such as `INITIATE_FLR`, link retrain, link disable, compliance entry, MSI/MSI-X enable, PME enable, or ACS/PASID enables. The macros do not encode side effects, required polling, write-one-to-clear behavior, or ordering constraints; those rules must come from PCIe specification handling, AMD hardware documentation, and the owning driver paths.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_11_0_offset.h` provides register addresses and base indices for the same `BIF_CFG_DEV0_EPF*_0_*` names. The corresponding function 4, 5, and 6 address blocks use base index 5 and distinct register offsets.
- `nbio_7_11_0_sh_mask.h` provides only field shifts and masks.
- AMDGPU register helper macros combine the address and field layers to read, write, set, or extract fields without hard-coded bit positions.

Observed integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio_7_11_0_offset.h` and this mask header. That file primarily uses other NBIO 7.11.0 register groups for revision ID, memory size, doorbell apertures, HDP flush offsets, PCIE index/data offsets, interrupt handling, register remapping, and clock gating. It demonstrates the intended consumption pattern: read a register through a SOC15 or PCIE helper, update fields with `REG_SET_FIELD` or masks, and write the result back.

The exact `BIF_CFG_DEV0_EPF4/5/6` fields in this chunk are most likely consumed by PCIe capability, diagnostics, reset, RAS, virtualization, or firmware-facing paths rather than by the short NBIO bring-up helpers alone. They align with older generic BIF/PCIe mask families such as `PCIE_UNCORR_ERR_STATUS`, `PCIE_ACS_CAP`, and `PCIE_PASID_CAP`, but are specialized here for NBIO 7.11.0 endpoint-function configuration spaces.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can modify unrelated PCI configuration bits, causing broken enumeration, disabled bus mastering, incorrect BAR sizing, lost interrupts, link instability, bad reset behavior, or failed power management.
- Repetition across endpoint functions is mechanically fragile. Function 4 and function 5 are nearly identical, and function 6 starts the same pattern. Copying an `EPF4` mask into `EPF5` or `EPF6` code would target the wrong register namespace even when the field layout appears identical.
- PCIe AER fields include sticky status, masks, severity controls, and captured logs. Misinterpreting status bits as masks, or severity bits as status, can hide fatal errors or misclassify correctable/non-fatal/fatal events.
- MSI/MSI-X fields are interrupt-critical. Incorrect table offsets, BIRs, message data, masks, pending bits, or enable bits can produce missing, misrouted, or unmasked interrupts.
- ACS and PASID controls affect isolation and requester identity. Incorrect enablement can break IOMMU/PASID behavior, peer-to-peer routing constraints, or virtualization security assumptions.
- Link and FLR controls have side effects. `INITIATE_FLR`, retrain, link disable, compliance, DRS, and de-emphasis fields must be used with appropriate sequencing and polling.
- Power-budget and DPA fields can interact with platform power policy. Treating them as arbitrary debug fields can produce inconsistent advertised power state or substate information.
- The chunk starts mid-family at the end of function 3 and ends mid-family in function 6. A merged report must stitch this document to adjacent chunks to avoid presenting partial function 3 and function 6 coverage as complete.

## Test and Validation Signals

Useful validation is mostly build-time and hardware-integration coverage:

- Build AMDGPU with NBIO 7.11.0 support enabled to catch missing or renamed macros in code that includes `nbio_7_11_0_sh_mask.h`.
- PCI enumeration and lspci/config-space validation should confirm vendor/device IDs, command/status, BARs, class codes, capability pointers, PM capability, PCIe capability, MSI, MSI-X, AER, ACS, PASID, ARI, and RTR capability layouts match expected hardware.
- Interrupt tests should exercise MSI and MSI-X enablement, masking, pending bits, table/PBA offsets, and 32-bit versus 64-bit MSI message fields.
- PCIe RAS tests should inject or observe correctable and uncorrectable errors, verify AER status/mask/severity interpretation, and confirm header/TLP-prefix log capture.
- Reset and power-management tests should cover FLR initiation, D3hot-to-D0 timing, reset-time reporting, PME enable/status, power-state fields, and link recovery after retrain or reset.
- Virtualization/IOMMU tests should validate PASID width/enables, ACS capability/control behavior, ARI next-function and function-group fields, and peer-to-peer isolation expectations.
- Link-training diagnostics should verify negotiated speed/width, training status, DL active, bandwidth notifications, equalization phase status, target link speed, and compliance/de-emphasis controls.

## Unresolved Cross-Chunk References

This chunk begins after `BIF_CFG_DEV0_EPF3_0_PCIE_ARI_CAP` has already started, so the complete function 3 PCIe capability and AER/BAR/power-management context is in earlier chunks. It ends at `BIF_CFG_DEV0_EPF6_0_LINK_CAP2`; the remaining function 6 `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and RTR fields belong to the following chunk. The merge/reconciliation lane should combine adjacent chunk research before producing a complete per-file document.

### subset-b-003136: lines 34497-36940

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 34497-36940

## Scope

This chunk covers lines 34497-36940 of AMDGPU's generated NBIO 7.11.0 shift/mask header. The range is C preprocessor register metadata only: comments naming registers/address blocks and `#define` constants for bit shifts and already-positioned masks. It has no executable functions, structs, enums, allocation, locks, I/O, or direct runtime side effects.

The chunk starts inside the `BIF_CFG_DEV0_EPF6_0` PCIe configuration space block, covers the remainder of the EPF6 extended capability area, covers a full `BIF_CFG_DEV0_EPF7_0` endpoint-function PCI configuration block, then enters the `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` root-complex block through most of `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`.

## Purpose

`nbio_7_11_0_sh_mask.h` gives AMDGPU driver code symbolic field geometry for NBIO 7.11.0 registers. This specific slice describes PCI configuration and PCIe extended-capability fields for NBIF endpoint functions EPF6/EPF7 and the beginning of DEV1 RC0. Driver code pairs these macros with matching register address macros from the NBIO 7.11.0 offset/SMN headers and with helper macros such as `REG_GET_FIELD` or `REG_SET_FIELD` to decode status, compose read-modify-write values, and avoid hard-coded bit literals.

The covered fields map to standard and AMD-specific PCIe configuration concepts: command/status, BARs, MSI/MSI-X, PCI PM, PCIe device/link/slot/root capabilities and controls, Advanced Error Reporting, vendor-specific capabilities, resizable BAR controls, dynamic power allocation, ACS, PASID, ARI, routing ID interpretation, root-port bridge windows, virtual channels, serial number capability, and PCIe uncorrectable-error status/mask bits.

## Important APIs, Types, and Macros

There are no callable APIs or data types in this range. The generated public interface is the repeated macro form:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask shifted into register position.

Important register families in this chunk are:

- EPF6 tail registers: `BIF_CFG_DEV0_EPF6_0_LINK_CNTL2`, `LINK_STATUS2`, MSI and MSI-X capability registers, SATA capability and IDP registers, vendor-specific capability/header/scratch registers, AER status/mask/severity/capability/header-log/TLP-prefix-log registers, BAR enhanced capability and BAR1-BAR6 resize controls, power-budgeting registers, dynamic power allocation, ACS, PASID, ARI, and RTR capability/data fields.
- Full EPF7 standard PCI header fields: vendor/device IDs, command/status, revision/class codes, cache/latency/header/BIST, six BARs, adapter ID, ROM base, capability pointer, interrupt pin/line, min grant/max latency, and vendor/adapter capability aliases.
- EPF7 power-management and PCIe capability fields: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- EPF7 interrupt capability registers: MSI capability list/control/address/data/mask/pending fields and MSI-X capability list/control/table/PBA fields.
- EPF7 extended capabilities: SATA, vendor-specific, AER, resizable BAR, power budget, DPA, ACS, PASID, ARI, and RTR registers with the same field schemas as EPF6.
- DEV1 RC0 standard/root-port PCI configuration fields: command/status, class/header/BIST, BARs, secondary/subordinate bus numbers, bridge latency, I/O and memory base/limit windows, prefetchable upper base/limit, capability pointer, ROM base, interrupt fields, bridge control, and extended bridge control.
- DEV1 RC0 PCIe root-port capability fields: PM, PCIe capability, device/link/slot/root capability/control/status registers, second-generation device/link/slot registers, MSI capability, SSID and MSI-map capabilities, vendor-specific capability, virtual-channel capability and resource registers, device serial number, AER capability list, and uncorrectable-error status/mask fields.
- AER uncorrectable-error fields are repeated for EPF6, EPF7, and DEV1 RC0. They include DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked bits.
- Correctable-error fields for EPF6 and EPF7 include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal corrected, header-log overflow, and corrected internal/status mask bits.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. Its behavior is compile-time substitution of constants into driver code that performs PCI configuration-space or NBIO register accesses.

The implied hardware flows are:

1. PCI core or AMDGPU NBIO code reads and writes endpoint-function configuration registers using address macros and these masks to enable bus mastering, memory and I/O decoding, parity/SERR reporting, interrupts, and capability-specific controls.
2. Link-management code can inspect or program PCIe link capability/control/status fields, including negotiated width/speed, ASPM, retrain/link disable, extended sync, autonomous bandwidth, target link speed, compliance controls, equalization state, crosslink/RTM presence, and DRS indicators.
3. Interrupt setup code can interpret MSI/MSI-X capability list pointers, enable bits, multiple-message fields, 32-bit versus 64-bit message address/data layouts, table/PBA BAR indicators, masks, and pending bitmaps.
4. AER or RAS-adjacent PCIe error handling code reads status and masks, records header/TLP-prefix logs, checks severity, and programs ECRC and multi-header controls. The same uncorrectable-error bit layout appears for endpoint functions and the root-complex port.
5. Resizable BAR, DPA, ACS, PASID, ARI, power budget, and RTR paths use capability-list and control fields to expose or constrain PCIe features used by the OS, firmware, or GPU driver.
6. DEV1 RC0 root-port bridge fields describe subordinate bus routing, I/O and memory window apertures, bridge error controls, root-control interrupt enables, root status, slot controls, and VC resource negotiation.

The header does not order operations, clear sticky status bits, or enforce PCIe capability dependencies. Callers must still follow PCI/PCIe programming rules, NBIO access rules, and hardware reset/power sequencing requirements.

## State and Persistence

The file owns no software state and persists nothing. The represented state lives in NBIO/PCIe hardware registers and PCI configuration space.

State represented by this chunk includes:

- EPF6 and EPF7 endpoint capability state for link controls, interrupt delivery, PCIe errors, BAR sizing, power budgeting, DPA, ACS, PASID, ARI, routing ID interpretation, and vendor-specific scratch fields.
- EPF7 PCI identity/configuration state, including command/status enables, class information, BARs, ROM base, capability chain pointers, and interrupt routing.
- DEV1 RC0 bridge/root-port state, including bus-number windows, I/O/memory/prefetchable apertures, bridge control bits, PM/PCIe capabilities, device/link/slot/root controls and statuses, virtual-channel resource controls, serial number dwords, and AER status/mask latches.
- Sticky or latched hardware observation state in status registers such as PCI status, device/link/slot/root status, MSI pending bits, AER status, VC negotiation pending/status bits, and header/TLP-prefix logs.

Retention across GPU reset, function-level reset, BACO, suspend/resume, runtime power transitions, or PCI hot reset is not defined here. AMDGPU initialization and PCI core restore paths must reprogram non-retained control state and treat status retention according to NBIO/ASIC documentation.

## Dependencies and Integration Points

This chunk depends on the surrounding generated NBIO 7.11.0 register headers:

- `nbio_7_11_0_offset.h` for corresponding config/MMIO register offsets.
- `nbio_7_11_0_smn.h` for SMN-addressed registers where applicable.
- `nbio_7_11_0_default.h` for reset/default values.
- Adjacent chunks of `nbio_7_11_0_sh_mask.h`; this chunk starts after the first part of EPF6 and ends before the completion of the DEV1 RC0 uncorrectable-error mask and severity block.

Likely integration areas in the AMDGPU tree are:

- NBIO 7.11 setup and low-level access code that includes generated NBIO register metadata.
- SOC15-era register helpers that combine register offsets with `*_SHIFT` and `*_MASK` values.
- PCIe link setup, power-management, interrupt, resizable-BAR, PASID/ARI/ACS, and AER/error-reporting paths.
- Firmware or platform-management code that needs consistent views of PCIe capability layouts for endpoint functions and root-complex ports.
- Kernel PCI core interactions where AMDGPU or platform code mirrors standard PCI capability state through ASIC-specific register windows.

Because the symbols are generated, integration is primarily by exact name matching. A field macro must be paired with the correct register address macro for the same ASIC generation and register block.

## Risks

- Wrong shifts or masks can silently program unrelated PCI configuration bits. In this range that can affect memory decoding, bus mastering, interrupt enablement, link retraining, BAR sizing, AER masking, bridge windows, or root-port slot/root behavior.
- The chunk is highly repetitive across EPF6 and EPF7. Generator or copy/paste mistakes may only affect one function and can be missed if validation covers a single endpoint function.
- AER status, mask, and severity registers share very similar field names. Mixing status and mask macros can hide errors or report false faults.
- MSI/MSI-X layouts include overlapping offset behavior between 32-bit and 64-bit forms. Using the wrong `*_64` field set or address/data field can break interrupt delivery.
- Resizable BAR control fields are repeated for BAR1-BAR6. Programming an unsupported size or the wrong BAR control field can expose incorrect apertures to the PCI core.
- DEV1 RC0 bridge window fields control downstream I/O and memory routing. Incorrect base/limit composition can break enumeration, DMA reachability, or isolation.
- ACS, PASID, ARI, AtomicOp, IDO, LTR, OBFF, and TLP-prefix controls influence ordering, translation, routing, and isolation behavior. Incorrect enablement can create subtle interoperability or security issues.
- The work item ends mid-register at `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`: the final five mask definitions for ACS violation through poisoned-TLP egress blocked are inside this chunk, while the next chunk begins with the remaining mask fields and then the severity register. Merge/reconciliation should treat that as a chunking artifact, not an inherent source defect.

## Test and Validation Signals

Useful validation is mostly mechanical plus hardware/PCIe behavior testing:

- Build an AMDGPU configuration that includes NBIO 7.11.0 headers to catch malformed macro definitions and symbol-name drift.
- Run a generated-header consistency check that each complete register in this line range has paired `__SHIFT` and `_MASK` definitions, allowing the intentional boundary split at `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`.
- Cross-check register names against `nbio_7_11_0_offset.h` and defaults so the shift/mask register names have matching address/default definitions where expected.
- Compare repeated EPF6 and EPF7 capability schemas for symmetry in field positions, especially MSI/MSI-X, AER, BAR resize, power budget, DPA, ACS, PASID, ARI, and RTR registers.
- Exercise PCIe link setup on NBIO 7.11.0 hardware and confirm link status, equalization, target speed, retrain/autonomous-bandwidth, and link-capability fields decode correctly.
- Validate interrupt setup by enabling MSI and MSI-X and checking message address/data, mask, pending, table, and PBA behavior.
- Validate AER handling by injecting or provoking controlled correctable and uncorrectable PCIe errors where available, then checking status/mask/severity/header-log/TLP-prefix-log decoding for EPF and RC paths.
- Validate resizable BAR enumeration and resize flows for every BAR control register described here.
- Validate root-port bridge configuration by checking subordinate bus numbers, I/O/memory/prefetchable windows, slot/root status bits, and virtual-channel negotiation on systems that expose DEV1 RC0.

## Chunk Boundary Notes

The first line completes the preceding `BIF_CFG_DEV0_EPF6_0_LINK_CAP2` register by providing only `DRS_SUPPORTED_MASK`. The prior chunk owns most of that register's shifts and masks.

The range then continues through the rest of EPF6, the entire EPF7 configuration block, and the start of DEV1 RC0. The final visible register, `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`, is incomplete at the line boundary: this chunk includes shifts for all uncorrectable-error mask fields and masks through `ACS_VIOLATION_MASK_MASK`; subsequent masks and the following severity register are expected in the next chunk.

### subset-b-003137: lines 36941-39386

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 36941-39386

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,127 `#define` macros and 317 register/address-block comments over 2,446 source lines. There are no functions, structs, enums, globals, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK`, covers the tail of the `BIF_CFG_DEV1_RC0` root-complex PCIe capability block, transitions at `addressBlock: nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, then covers most of the `BIF_CFG_DEV1_EPF0_0` endpoint-function PCI/PCIe configuration block through lane 14 margining control. It ends immediately before `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_STATUS`, so adjacent chunks are required for both boundary register families.

Although this source mirror is under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control path.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.11.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or compose the field.

This chunk describes PCIe root-complex and endpoint-function configuration-space fields for device 1. The constants support AMDGPU code that needs to inspect or program PCIe error reporting, link negotiation, equalization, power-management, interrupt, virtual-channel, access-control, PASID, ARI, LTR, data-link feature, 16 GT/s PHY, and lane-margining registers without hard-coding bit positions at call sites.

## Important Macro Families

The opening `BIF_CFG_DEV1_RC0` section completes and extends a root-complex Advanced Error Reporting and secondary PCIe capability layout:

- AER uncorrectable error mask/severity bits for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked.
- Correctable error status/mask bits for receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, and internal correctable error.
- AER control and logging fields: first error pointer, ECRC generation/check capabilities and enables, multi-header receive controls, four TLP header log words, root error command/status, error source IDs, and four TLP prefix log words.
- Secondary PCIe enhanced capability fields: capability ID/version/next pointer, link control 3 equalization triggers, lane error status, per-lane 8 GT/s equalization controls for lanes 0-15, ACS capability/control, Data Link Feature capability/status, 16 GT/s enhanced capability, 16 GT/s link cap/control/status, local and retimer parity mismatch status, per-lane 16 GT/s equalization controls for lanes 0-15, margining port capability/status, per-lane margining control/status for lanes 0-15, and RTR capability/data registers.

The `BIF_CFG_DEV1_EPF0_0` section begins after the address-block marker and describes the endpoint-function configuration space:

- Conventional PCI identity and header registers: vendor/device ID, command/status, revision and class-code bytes, cache-line/latency/header/BIST fields, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, grant/latency, and adapter/vendor capability words.
- Power-management and USB-like timing fields: PMI capability/list/status/control, SBRN, FLADJ, and DBESL/DBESLD fields.
- PCIe capability fields: PCIe capability header, device capability/control/status, link capability/control/status, device/link capability 2 and control/status 2, MSI and MSI-X capability/control/address/data/mask/pending/table/PBA fields, SATA capability/index/data, vendor-specific enhanced capability words, and virtual-channel capability/control/status/resource fields for VC0 and VC1.
- Endpoint AER and BAR enhanced capabilities: uncorrectable/correctable error status/mask/severity, AER cap/control, header logs, TLP prefix logs, BAR1-BAR6 capability/control, power-budgeting, and dynamic power allocation substate fields.
- Endpoint secondary PCIe and isolation/translation features: secondary link control 3, lane error status, lanes 0-15 8 GT/s equalization controls, ACS capability/control, PASID capability/control, LTR capability, ARI capability/control, Data Link Feature capability/status, 16 GT/s link/retimer/parity/equalization fields, margining port capability/status, and lane 0 through lane 14 margining controls/statuses through the chunk boundary.

The repeated lane families use consistent four-field patterns. Equalization control entries expose downstream/upstream transmit presets and receive preset hints. Margining lane control/status entries expose receiver number, margin type, usage model, and payload fields. This regularity is useful for generated-header consistency checks and for driver code that iterates lane instances through tables or macro-expanded accessors.

## APIs, Types, And Functions

There are no callable APIs or C data types in this range. The public interface is the generated C preprocessor namespace. The macro values are integer literals, mostly with an `L` suffix, and encode field geometry only.

These definitions do not encode register addresses, reset values, access width, read/write permissions, write-one-to-clear behavior, firmware ownership, hardware sequencing rules, or side effects. Runtime code must combine these masks with sibling address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate NBIO/SMN/PCIe configuration access path for the target register.

## Control Flow

This header has no local runtime control flow. Runtime behavior is external:

1. AMDGPU or platform code selects a `BIF_CFG_DEV1_RC0_*` or `BIF_CFG_DEV1_EPF0_0_*` register from sibling generated offset/SMN metadata.
2. Code reads a hardware register and decodes fields using the `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated and reserved bits.
3. The decoded or programmed value affects PCIe enumeration, link training, link speed/width negotiation, equalization, lane margining, ASPM/power management, MSI/MSI-X routing, AER/DPC-style diagnostics, ACS/PASID/ARI/LTR policy, VC mapping, BAR sizing/control, and endpoint/root-complex error reporting.

Many fields represent asynchronous hardware or protocol state rather than ordinary software state: AER status latches, TLP header/prefix logs, root error receive bits, data-link feature exchange status, link equalization request/completion bits, lane error vectors, 16 GT/s parity mismatch reports, retimer presence, margining command completion, power-management event status, MSI pending bits, VC negotiation/pending flags, and link status readbacks.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe root-complex and endpoint-function configuration registers. Persistence is determined by the GPU reset domain, PCIe fundamental or hot reset, link retrain, power-state transitions, firmware/BIOS setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, read-only capability bits, readback status bits, policy masks, severity selectors, interrupt routing data, BAR controls, power-budget/DPA entries, link/equalization training state, lane margining commands and results, virtual-channel controls, ACS/PASID/ARI/LTR policy, and error/status logs. Some PCIe status fields are typically write-one-to-clear and some capability fields are read-only, but that access behavior is not visible in these shift/mask macros alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with companion metadata for the same IP version:

- `nbio_7_11_0_offset.h` and `nbio_7_11_0_smn.h` provide address metadata for matching registers.
- `nbio_7_11_0_default.h`, when present for the register family, provides reset/default values.
- AMDGPU SOC15/NBIO register access helpers and generic bitfield helper macros apply these masks at runtime.

Integration points include AMDGPU NBIO bring-up, PCIe endpoint and root-complex configuration, GPU reset and resume restore, PCIe capability discovery, link retrain/equalization code, 16 GT/s PHY diagnostics, margining diagnostics, AER logging, MSI/MSI-X programming, BAR setup, VC/ACS/PASID/ARI/LTR feature enablement, power budgeting/DPA handling, and low-level debug or RAS flows that collect PCIe error context.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing writes to the wrong PCIe configuration bits, which can break link training, interrupt delivery, BAR decode, traffic isolation, power management, or error reporting.
- The chunk starts inside `BIF_CFG_DEV1_RC0_PCIE_UNCORR_ERR_MASK` and ends after `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_CNTL`; whole-file research must reconcile adjacent chunks before treating either boundary family as complete.
- AER and PCIe status/log registers often have ordering-sensitive clear semantics. Software should capture source IDs, header logs, prefix logs, and lane status before clearing status bits.
- Link equalization, retraining, 16 GT/s controls, and lane margining are asynchronous hardware operations. Writers need timeouts and must handle non-converging training, link down events, reset races, and retimer-related parity/status behavior.
- ACS, PASID, ARI, LTR, VC, and BAR controls affect DMA routing, isolation, address translation, latency reporting, and resource decoding. Incorrect programming can create enumeration failures or security/isolation regressions in virtualized systems.
- MSI/MSI-X address/data/mask/pending fields are interrupt-routing sensitive. Stale restore values or incorrect masks can drop, duplicate, or misroute interrupts.
- The RC0 and EPF0_0 prefixes describe different PCIe roles. Reusing a mask across the wrong instance may appear type-compatible because all values are plain macros, but it can target unrelated register layouts.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols referenced by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should not overlap unexpectedly within a register, and repeated lane 0-15 families should match where the hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_11_0_offset.h`, `nbio_7_11_0_smn.h`, and default-value metadata so each field layout maps to the expected register address and reset value.
- On supported hardware, validate PCIe enumeration, BAR decode, MSI/MSI-X delivery, negotiated link speed/width, link retraining, equalization status, 16 GT/s link status, suspend/resume restore, and GPU reset recovery.
- Exercise diagnostic/error paths: AER correctable and uncorrectable reporting, root error command/status reporting, TLP header/prefix log capture, lane error status reads, retimer parity mismatch reporting, Data Link Feature status, and lane margining command/status readback.
- For any code that writes these fields, inspect register traces to ensure reserved bits are preserved, status/log fields are cleared only after capture, and RC0 versus EPF0_0 instance selection matches the intended PCIe role.

### subset-b-003138: lines 39387-41833

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

### subset-b-003139: lines 41834-44284

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 41834-44284

## Scope

This chunk is a generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 2,132 `#define` macros across 315 register-comment groups. There are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT`, covers the remainder of `BIF_CFG_DEV2_RC0` 16 GT/s lane equalization, PCIe margining, and readiness-to-return fields, then covers the complete `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp` endpoint-function block for `BIF_CFG_DEV2_EPF0_0`. It then begins the next address block, `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, and ends just after the first two `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2` shift definitions. Adjacent chunks are needed for the earlier lane-4 equalization shifts and the rest of `EPF1_0_DEVICE_CNTL2` and later `EPF1_0` capability fields.

Although this source mirror is under `sources/distributed-fs/ceph-client`, the file is AMD GPU PCIe/NBIO hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the generated bitfield-layout half of the NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the already shifted bit mask used to isolate, preserve, clear, or compose the field.

This chunk describes PCI Express configuration-space and extended-capability fields for NBIO device 2. The first part is root-complex port `RC0` metadata for 16 GT/s link equalization, lane margining, and readiness-to-return reporting. The second and largest part describes endpoint function `EPF0_0`: conventional PCI header fields, power-management capability fields, PCIe device/link controls and status, MSI/MSI-X, vendor-specific and virtual-channel capabilities, AER, BAR, power-budget, DPA, secondary PCIe equalization, ACS, PASID, LTR, ARI, data-link feature, 16 GT/s PHY/equalization, lane margining, and readiness-to-return registers. The final part begins the same PCI/PCIe capability layout for endpoint function `EPF1_0`.

These constants let AMDGPU code and bring-up/debug tooling decode or compose register words without hard-coding PCIe bit positions at call sites.

## Important Macro Families

The opening `BIF_CFG_DEV2_RC0` section covers root-complex link diagnostic and test-oriented fields:

- `BIF_CFG_DEV2_RC0_LANE_4_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` define downstream/upstream 16 GT/s TX preset fields. Lanes 5-15 are complete in this chunk; lane 4 starts with only the two mask lines because its shift lines are in the previous chunk.
- `BIF_CFG_DEV2_RC0_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, and `MARGINING_PORT_STATUS` expose the PCIe margining enhanced-capability header and port readiness/software-readiness bits.
- `BIF_CFG_DEV2_RC0_LANE_0_MARGINING_LANE_CNTL/STATUS` through lane 15 define the repeated receiver number, margin type, usage model, and margin payload fields for lane margining commands and status readback.
- `BIF_CFG_DEV2_RC0_PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2` describe readiness-to-return capability metadata and message timing/data fields.

The `BIF_CFG_DEV2_EPF0_0` address block is complete in this chunk and represents a full endpoint-function PCI configuration and enhanced-capability layout:

- Base PCI header fields: vendor/device ID, command/status, revision/class codes, cache line, latency, header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, and vendor capability pointers.
- Power-management and USB-style legacy fields: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- Core PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capabilities: MSI list/control/message address/data/mask/pending fields and MSI-X list/control/table/PBA fields.
- Vendor, virtual-channel, and SATA-like capability windows: vendor-specific enhanced capability headers/data, VC port/resource capability/control/status for VC0 and VC1, and SATA IDP index/data fields.
- Error and diagnostic fields: AER enhanced capability, uncorrectable/correctable error status/mask/severity, AER control, header logs, TLP prefix logs, lane error status, parity mismatch status for 16 GT/s, and readiness-to-return fields.
- Link tuning and isolation features: BAR enhanced capability controls, power budget, Dynamic Power Allocation, secondary PCIe link control/equalization for lanes 0-15, ACS, PASID, LTR, ARI, data-link feature capability/status, 16 GT/s PHY/equalization, margining, and per-lane margining command/status fields.

The `BIF_CFG_DEV2_EPF1_0` block begins at line 43917. This chunk covers its base PCI header, vendor and power-management capabilities, PCIe device/link capability/control/status fields, and all of `DEVICE_CAP2`. It ends immediately after the `CPL_TIMEOUT_VALUE` and `CPL_TIMEOUT_DIS` shift definitions for `DEVICE_CNTL2`, so the masks and remaining `DEVICE_CNTL2` fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor namespace. The macro values are untyped integer literals, mostly with an `L` suffix, and encode field geometry only.

These definitions do not provide register addresses, reset values, read/write permissions, access width, write-one-to-clear behavior, firmware ownership, or sequencing rules. Consumers must combine them with matching address macros from `nbio_7_11_0_offset.h`, defaults from any generated default metadata, and AMDGPU helper macros/functions such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

The ASIC implementation file `amdgpu/nbio_v7_11.c` includes both `nbio_7_11_0_offset.h` and this shift/mask header and uses the generated constants through SOC15 and PCIe-port register access helpers. A tree search in this snapshot shows direct NBIO 7.11 code using this header mostly for other NBIO fields; these `BIF_CFG_DEV2_*` PCIe configuration fields may be consumed by conditional paths, generated tooling, debug code, or downstream hardware-management code not visible in the sampled file.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes it:

1. Driver, firmware-facing, or diagnostic code selects a `regBIF_CFG_DEV2_*` address from `nbio_7_11_0_offset.h`.
2. The code reads the register, extracts fields with the `__SHIFT` and `_MASK` constants, or constructs an updated register value while preserving unrelated and reserved bits.
3. Hardware observes the write or returns status through PCIe configuration, link training, error-reporting, margining, interrupt, power-management, or routing logic.

Several represented fields imply asynchronous protocol flow even though the header does not implement it: link retraining and link-training status, data-link active reporting, MSI/MSI-X enable and pending state, AER status/log capture and clearing, DPA substate power allocation, secondary PCIe equalization phases and presets, ACS/PASID/ARI/LTR policy enablement, 16 GT/s parity mismatch reporting, lane margining command/status exchange, and readiness-to-return timing/message reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration registers. Persistence depends on PCIe reset, GPU reset domains, function-level reset, link reset/retrain, firmware/BIOS initialization, suspend/resume restore, power management, and explicit AMDGPU or platform writes.

Represented state includes PCI command/status bits, BAR and ROM decode fields, class and revision identity, capability-list pointers, interrupt routing values, power-management control/status, PCIe device and link capability/control/status, completion-timeout and atomic/ARI/LTR/OBFF controls, MSI/MSI-X configuration and masks, VC/ACS/PASID policy, AER status/masks/severity and captured logs, BAR and power-budget metadata, DPA status/control and substate allocations, per-lane equalization presets, 16 GT/s equalization and parity status, margining command/status payloads, and readiness-to-return timing fields.

Some fields are read-only capability values, some are writable policy controls, and some are status or log bits with protocol-specific clear semantics. That access behavior is not encoded by the shift/mask macros and must come from PCIe/NBIO hardware documentation and the surrounding driver sequence.

## Dependencies And Integration Points

This chunk depends on the rest of AMD's generated NBIO 7.11.0 register package:

- `nbio_7_11_0_offset.h` supplies the corresponding `regBIF_CFG_DEV2_*` register addresses and base indices.
- Other chunks of `nbio_7_11_0_sh_mask.h` supply the boundary fields before `RC0_LANE_4_EQUALIZATION_CNTL_16GT` and after `EPF1_0_DEVICE_CNTL2`.
- AMDGPU register helpers provide field packing/extraction and the actual MMIO, SOC15, or PCIe-port register access path.
- PCIe core policy, platform firmware setup, and GPU reset/suspend-resume paths determine when these fields are valid to read, write, restore, or clear.

Integration points include NBIO initialization, PCIe endpoint-function configuration, PCI enumeration support, BAR/ROM decode setup, MSI/MSI-X programming, link speed/width negotiation, link equalization diagnostics, lane margining support, AER and error-log handling, power management, DPA/power-budget reporting, ACS/PASID/ARI/LTR configuration for virtualization and memory-translation policy, and low-level hardware bring-up/debug flows.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while directing reads or writes to the wrong PCIe bit. Symptoms can include failed enumeration, broken BAR decode, misrouted interrupts, link-training failures, lost error reporting, or incorrect virtualization isolation.
- The chunk boundaries split real register groups. `RC0_LANE_4_EQUALIZATION_CNTL_16GT` and `EPF1_0_DEVICE_CNTL2` are incomplete here, so merged research must reconcile adjacent chunks before treating either boundary register as fully documented.
- Many PCIe status and AER fields are latch-like or write-one-to-clear in hardware. The shift/mask header does not mark those semantics, so code must capture associated header/TLP-prefix/source logs before clearing status bits.
- Link equalization, retraining, margining, readiness-to-return, DPA, PME, FLR, and reset-related controls can trigger asynchronous hardware state changes. Writers need bounded polling, timeout handling, and reset/power-state awareness.
- Reserved fields and capability readbacks should not be used as writable feature controls. Read-modify-write paths should preserve unrelated bits unless the hardware documentation says otherwise.
- Endpoint-function instances are mechanically repeated. Copy/paste or generator mistakes can affect `EPF0_0` and `EPF1_0` differently, making failures function-specific.
- Security-sensitive policy fields such as ACS, PASID, ARI, relaxed ordering, no-snoop, atomic operations, and LTR can change DMA routing, ordering, and isolation behavior if programmed incorrectly.

## Test Signals

- Build AMDGPU with NBIO 7.11 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks: each complete field should have a matching `__SHIFT` and `_MASK`, masks should align with their shifts, and repeated lane/function blocks should match where the hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_11_0_offset.h` so every `BIF_CFG_DEV2_RC0`, `BIF_CFG_DEV2_EPF0_0`, and visible `BIF_CFG_DEV2_EPF1_0` field maps to the expected register address and base index.
- On supported hardware or simulator traces, validate PCIe enumeration, BAR sizing/decode, ROM decode behavior, MSI/MSI-X delivery, negotiated link speed/width, link retraining, data-link-active reporting, and suspend/resume or reset restore.
- Exercise error and diagnostic paths: AER correctable/nonfatal/fatal status, AER masks/severity, captured header/TLP-prefix logs, 16 GT/s equalization completion and parity mismatch status, lane error status, and readiness-to-return status.
- For margining and equalization users, verify per-lane command/status payload encoding, receiver selection, margin type, usage model, 16 GT/s preset programming, hardware readiness bits, timeout behavior, and preservation of reserved bits during read-modify-write sequences.
- Merged per-file research should connect this document with adjacent chunks for the complete `nbio_7_11_0_sh_mask.h` register map rather than treating this line range as a standalone final report.

### subset-b-003140: lines 44285-46731

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 44285-46731

## Scope

This chunk is a generated AMDGPU NBIO 7.11 shift/mask header segment for PCI/PCIe configuration-space fields in the `BIF_CFG_DEV2` endpoint-function blocks. It contains 2,134 `#define` field-layout macros and 309 register/address-block comments. There are no functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms in this range.

The range starts inside `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, after the first two shift definitions for completion-timeout fields, covers the rest of endpoint function 1's PCIe capability and extended-capability tail, covers the complete `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` address block, and then enters `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp` through the first two `BIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL` shifts. Adjacent chunks are needed for the complete `EPF1_0_DEVICE_CNTL2` and `EPF3_0_PCIE_BAR5_CNTL` register definitions.

Although this repository mirror is under a `ceph-client` source tree, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.11 register interface. Each public macro follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK` gives the encoded mask in the raw register value.

This chunk describes PCI/PCIe configuration-space layout for secondary functions of NBIF device 2. The covered fields let AMDGPU code decode and compose endpoint PCI config registers for identity, command/status, BAR windows, capability lists, power management, PCIe link/device controls, MSI/MSI-X routing, SATA capability metadata, vendor-specific capabilities, Advanced Error Reporting, BAR enhanced capability controls, power-budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and RTR metadata.

The macros intentionally describe only field geometry. They do not provide register addresses, reset values, access permissions, legal value combinations, write-one-to-clear behavior, or sequencing rules.

## Important Macro Families

The endpoint-function 1 tail covers PCIe capability and extended-capability fields after `DEVICE_CAP2`:

- `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` define completion-timeout control, ARI/AtomicOp/IDO/LTR/OBFF/10-bit-tag/TLP-prefix controls, supported link speeds, compliance/de-emphasis settings, equalization-complete phase bits, crosslink state, downstream-component presence, and DRS message status.
- MSI and MSI-X groups define capability-list headers, message-control bits, 32-bit and 64-bit message address/data fields, per-vector mask and pending bit arrays, MSI-X table/PBA BIR and offsets, function mask, and enable bits.
- SATA capability and IDP groups expose SATA capability revision, BAR location/offset, indexed-data-port index, and data fields.
- Vendor-specific and AER groups define enhanced-capability headers, vendor-specific payload dwords, uncorrectable error status/mask/severity, correctable error status/mask, ECRC/multiple-header controls, header logs, and TLP prefix logs.
- BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR groups expose BAR size support/control, power-budget data select/data/capability, DPA substate power allocation and status/control fields, ACS capability/control, PASID capability/control, ARI next-function/group controls, and routing-data payload fields.

The endpoint-function 2 block is complete in this chunk and repeats a full type-0 endpoint configuration layout:

- Standard PCI config fields: vendor/device IDs, command/status, revision and class-code bytes, cache-line/latency/header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and adapter write field.
- Power-management fields: PM capability list, PM capability, status/control, PME support/status, data-select/scale, D-state, no-soft-reset, and B2/B3 support.
- PCIe capability fields: capability header, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- Interrupt fields: MSI and MSI-X capability, address/data/mask/pending/table/PBA fields.
- Extended-capability fields: SATA capability, vendor-specific capability, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, and RTR.

The endpoint-function 3 prefix begins the same generated pattern as endpoint-function 2:

- It covers standard identity, command/status, class/header/BAR, adapter/ROM/capability/interrupt fields.
- It includes PM capability/status, plus USB-oriented `SBRN`, `FLADJ`, and `DBESL_DBESLD` registers before the PCIe capability block.
- It then covers PCIe device/link capability and control, MSI/MSI-X, SATA, vendor-specific, AER, header/TLP-prefix logs, BAR enhanced capability headers, BAR1-BAR5 capability/control groups, and stops after the first two `PCIE_BAR5_CNTL` shift definitions.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. Constants are untyped integer literals, usually with an `L` suffix for masks, and encode the low-level layout of 8-bit, 16-bit, and 32-bit PCI/NBIO register fields.

Consumers must combine these field constants with the sibling generated offset header, for example `regBIF_CFG_DEV2_EPF2_0_VENDOR_ID` in `nbio_7_11_0_offset.h`, and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or PCI/NBIO accessors appropriate to the target register. This header alone cannot identify where a register lives or how it should be accessed safely.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_11_0_sh_mask.h`.
2. Driver code selects a matching address macro from `nbio_7_11_0_offset.h` or another generated NBIO address source.
3. The code reads a PCI/NBIO config register, extracts fields using `*_MASK` and `*__SHIFT`, or composes a new value while preserving unrelated bits.
4. Hardware, firmware, or PCI core behavior interprets the resulting config-space state.

The field names imply external hardware flows outside this header: PCIe link training and equalization, completion timeout behavior, MSI/MSI-X interrupt routing, power-management state transitions, Dynamic Power Allocation substate selection, AER logging and clearing, ACS/PASID/ARI routing and isolation, BAR sizing/enabling, and error-report containment/reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO 7.11 PCI/PCIe configuration registers. Persistence depends on GPU reset domains, PCI function reset, bus reset, FLR, suspend/resume restore, firmware/BIOS initialization, and explicit driver or PCI core writes.

Represented state includes endpoint identity and BAR apertures, command/status enables, interrupt configuration, power-management state, PCIe device/link capabilities and controls, MSI/MSI-X mask and pending arrays, AER status/mask/severity/log registers, BAR size negotiation controls, DPA and power-budget values, ACS/PASID/ARI enablement, and routing/vendor-specific metadata. Some fields are capability or status readbacks; others are writable controls whose persistence and side effects are defined by the PCIe specification and AMD hardware documentation, not by these macros.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11 register database and must remain synchronized with companion headers:

- `nbio_7_11_0_offset.h` supplies matching register addresses and base indices, including `regBIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2`, `regBIF_CFG_DEV2_EPF2_0_VENDOR_ID`, and `regBIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL`.
- Other generated NBIO 7.11 headers in the same directory provide related address/default metadata where present.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both the offset and shift/mask headers and is the direct AMDGPU NBIO 7.11 integration point. Display resource files include the offset header for DCN 3.5/3.5.1 address integration.

Semantic dependencies are the PCI and PCI Express specifications for endpoint configuration headers, PM capabilities, PCIe capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, BAR enhanced capability, power budgeting, DPA, and vendor-specific enhanced capabilities. The generated names mirror those architectural fields but do not enforce valid values or ordering.

## Risks And Edge Cases

- The chunk begins and ends mid-register. Whole-file reconciliation must include adjacent chunks before treating `BIF_CFG_DEV2_EPF1_0_DEVICE_CNTL2` or `BIF_CFG_DEV2_EPF3_0_PCIE_BAR5_CNTL` as complete.
- Generated shift/mask drift can compile cleanly while causing code to read or write the wrong PCIe config bit. The failure mode may surface as bad BAR sizing, broken interrupt delivery, incorrect power management, link instability, or silent loss of error reporting.
- Status fields in PCIe/AER/MSI/MSI-X capability space can have side effects or write-one-to-clear semantics. A mask definition does not imply read-modify-write is safe.
- ACS, PASID, and ARI controls affect isolation, address translation, function routing, and peer-to-peer behavior. Incorrect field programming can become a security or DMA-isolation issue, not just a device-local bug.
- AER mask/severity/status fields are highly repetitive and easy to miscompare in review. Misaligned masks can hide uncorrectable errors, escalate benign correctable errors, or log the wrong TLP/header data.
- BAR enhanced capability fields are repeated across BAR1-BAR6 and endpoint functions. Generation or copy drift can break only one BAR or one endpoint function, which makes runtime symptoms hardware-configuration dependent.
- Power-budget and DPA fields influence power/performance state choices. Bad values can cause incorrect power accounting, latency reporting, or substate allocation.
- Full-width masks such as `0xFFFFFFFFL` rely on existing AMDGPU helper types. New code should avoid ad hoc signed arithmetic or truncation-prone casts around these constants.

## Test Signals

- Build AMDGPU with NBIO 7.11 support enabled so include users such as `amdgpu/nbio_v7_11.c` catch missing or renamed macros.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should align with their shifts, repeated EPF2/EPF3 register families should match except where the hardware intentionally differs, and reserved fields should not overlap named fields.
- Cross-check this chunk against `nbio_7_11_0_offset.h` so each covered register has a matching `reg...` address and `_BASE_IDX`.
- On NBIO 7.11 hardware, compare decoded endpoint config space with `lspci -vvxxx`, PCI core dumps, or AMDGPU debug register reads for vendor/device IDs, BARs, PM state, link capabilities/status, MSI/MSI-X state, AER masks/status/logs, ACS/PASID/ARI state, DPA, and power-budget fields.
- Exercise suspend/resume, FLR or GPU reset, PCIe retraining, MSI/MSI-X enable/disable, and error-reporting paths to confirm that callers preserve reserved bits and restore expected config state.
- For AER-facing changes, inject or observe correctable and uncorrectable PCIe errors and verify that status, masks, severity, header logs, and TLP prefix logs decode to the intended bits.

### subset-b-003141: lines 46732-49193

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 46732-49193

## Purpose

This chunk is an auto-generated AMD NBIO 7.11.0 shift/mask header slice for PCIe configuration-space fields under the NBIF `BIF_CFG_DEV2` endpoint-function decode blocks. It starts in the tail of the `BIF_CFG_DEV2_EPF3_0` block, continues through the generated address blocks `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev2_epf5_bifcfgdecp`, and begins `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp`.

The file contains no executable driver logic. Its purpose is to expose preprocessor constants that decode and compose hardware register fields: each field has a `REGISTER__FIELD__SHIFT` bit position and a `REGISTER__FIELD_MASK` raw-value mask. Consumers combine these constants with register offsets from sibling NBIO headers and AMDGPU register access helpers.

## Public Surface In This Chunk

The exported API is the generated macro namespace for four adjacent PCIe endpoint-function regions:

- `BIF_CFG_DEV2_EPF3_0_*`: the end of the EPF3 block, covering BAR6 capability/control, power budget, dynamic power allocation, ACS, PASID, ARI, reset timing reporting, and related enhanced-capability list headers.
- `BIF_CFG_DEV2_EPF4_0_*`: a complete endpoint-function style PCI/PCIe config block, from vendor/device ID through reset timing reporting.
- `BIF_CFG_DEV2_EPF5_0_*`: a near-complete matching endpoint-function block, from vendor/device ID through reset timing reporting.
- `BIF_CFG_DEV2_EPF6_0_*`: the beginning of the next endpoint-function block, from vendor/device ID through the first `LINK_CAP` shift definitions. This requested range ends before the rest of `BIF_CFG_DEV2_EPF6_0_LINK_CAP` appears.

The register-family comments in the chunk identify 323 register blocks. The main repeated fields are standard PCI config header fields, PM capability fields, PCIe capability device/link fields, MSI/MSI-X fields, SATA capability/IDP fields, vendor-specific enhanced capability fields, AER fields, BAR enhanced capability fields, power budget and DPA fields, ACS/PASID/ARI fields, and reset timing reporting (`RTR`) fields.

## Important Register Families

The EPF3 tail contains late enhanced-capability groups. BAR6 capability/control defines supported BAR size and encoded BAR index/size fields. Power budget fields provide a selector, base power, scale, PM state/substate, type, power rail, and system allocation bit. DPA fields expose substate count, transition latency units/values, power allocation scale, active substate status, enable/control state, and eight per-substate power allocation bytes. ACS fields describe and control source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, P2P egress control, and direct translated P2P. PASID and ARI fields expose PASID width/permissions and ARI function-group/next-function controls. Reset timing reporting fields expose reset, DL-up, FLR, and D3hot-to-D0 timing plus a validity bit.

The EPF4 block is the fullest block in this slice. Its standard PCI header fields include vendor/device ID, command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), status bits, revision and class-code bytes, cache-line and latency timers, header/BIST fields, six base-address registers, subsystem IDs, ROM base address, capability pointer, interrupt line/pin, and min/max latency fields. It also includes a vendor capability list and writable adapter ID aliases.

EPF4 PM and PCIe capability fields define PM version/support, PME control/status/data, secondary bus revision number, frame-length adjustment, and DBESL/DBESLD bytes. PCIe device and link fields cover max payload support/size, extended tags, role-based error reporting, captured slot power limit/scale, FLR capability/initiation, correctable/nonfatal/fatal/unsupported error enables, relaxed ordering, no-snoop, max read request size, link speed/width, ASPM and clock PM, link disable/retrain, common clock, bandwidth interrupts, DRS signaling, current negotiated link state, and PCIe capability 2 fields such as completion-timeout control, ARI/AtomicOp/LTR/OBFF/10-bit tag/TLP-prefix capabilities, supported link speeds, equalization status, RTM presence, crosslink, and DRS support.

EPF4 interrupt and storage-capability fields include MSI capability/control, 32-bit and 64-bit MSI address/data, extended message data, mask and pending bits, MSI-X table/PBA descriptors, and SATA capability/IDP index/data registers. The MSI/MSI-X masks are full-width for vector mask/pending arrays, while message address/data fields expose the PCI-defined aligned address and 16-bit data fields.

EPF4 and EPF5 both include vendor-specific enhanced capabilities, AER, enhanced BAR, power budget, DPA, ACS, PASID, ARI, and RTR groups. AER fields cover uncorrectable status/mask/severity for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked conditions. Correctable AER status/mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, and internal correctable errors. AER capability/control fields expose first-error pointer, ECRC generation/check capability and enables, and multi-header recording. Header log and TLP prefix log registers are modeled as full 32-bit fields.

EPF5 mirrors the EPF4 layout for the same endpoint-function class, but the requested slice reaches it after EPF4 and continues through EPF5 reset timing reporting. The repeated structure is significant: any consumer code or generator change should treat EPF4 and EPF5 as independent hardware functions with similar layouts, not as aliases. Matching register names have distinct `EPF4` or `EPF5` prefixes and distinct offsets in `nbio_7_11_0_offset.h`.

The EPF6 portion starts a new address block and covers only the early configuration header and initial PCIe capability fields. It defines standard identification, command/status, class, BAR, subsystem, ROM, interrupt, vendor capability, PM capability/status-control, PCIe capability header, device capability/control/status, and the beginning of link capability fields. The chunk ends after `BIF_CFG_DEV2_EPF6_0_LINK_CAP__LINK_BW_NOTIFICATION_CAP__SHIFT`, so the remaining `LINK_CAP` shifts and all `LINK_CAP` masks are in the following chunk.

## Control Flow And State

There is no C control flow, no functions, and no data structure ownership in this range. Runtime behavior is supplied by code that includes this header, reads or writes a hardware register using a matching offset macro, and applies the generated mask/shift constants.

The relevant state lives in GPU NBIO/PCIe configuration registers. Some fields are static identification or capability descriptors, while others are mutable control and status. Mutable or side-effectful families include PCI command enables, PM/PME state, PCIe device control and status, link retraining and target speed controls, MSI/MSI-X routing state, AER status/mask/severity, BAR sizing/control, DPA control/status, ACS isolation controls, PASID and ARI enables, and RTR validity/timing fields. Status fields may be latched by hardware and may require PCIe-specified clear semantics outside this header.

## Dependencies And Integration Points

This header is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which is the NBIO 7.11 AMDGPU integration point for this generated register family. The shift/mask constants are paired with address macros in `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`; spot checks show corresponding offsets for representative registers such as `regBIF_CFG_DEV2_EPF4_0_PCIE_BAR1_CAP`, `regBIF_CFG_DEV2_EPF5_0_PCIE_UNCORR_ERR_STATUS`, and `regBIF_CFG_DEV2_EPF6_0_LINK_CAP`, all using base index 5.

The semantic dependencies are the PCI and PCI Express configuration specifications: standard type-0 header fields, PM capability, PCIe capability, MSI/MSI-X capabilities, SATA capability, vendor-specific enhanced capability, Advanced Error Reporting, Resizable/Enhanced BAR-style capability fields, Power Budgeting, Dynamic Power Allocation, Access Control Services, PASID, ARI, and Reset Timing Reporting. The generated macros name these fields but do not validate legal PCIe state transitions or safe write ordering.

## Risks And Maintenance Notes

- The requested range starts mid-block in EPF3 and ends mid-register in EPF6. Adjacent chunks are required for complete EPF3 and EPF6 analysis.
- These constants must stay synchronized with the generated NBIO 7.11.0 hardware database and sibling offset headers. A wrong mask or shift can silently decode the wrong bit or program unrelated PCIe controls.
- EPF4 and EPF5 are highly repetitive. Reviewers should watch for generator drift where one function's field width, mask, or register presence diverges unexpectedly from the matching function.
- Several controls affect isolation, DMA reachability, and interrupt delivery: `BUS_MASTER_EN`, memory access enables, ACS controls, PASID enables, ARI controls, MSI/MSI-X enables/masks, and BAR sizing/control.
- AER and device-status fields can be clear-on-write or otherwise side-effectful at the hardware level. The presence of full masks in this header does not mean read-modify-write is safe for every status register.
- Link and power fields can affect PCIe stability and resume behavior, including ASPM/clock PM, retraining, target speed, equalization status, DPA substates, power budget reporting, PME state, and reset timing.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` rely on the established AMDGPU unsigned register helper patterns; ad hoc signed arithmetic can create truncation or sign-extension mistakes.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units including `nbio_7_11_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`.
- Static checks that each complete field in this slice has a matching `*_SHIFT` and `*_MASK`, with masks aligned to shifts. The EPF6 `LINK_CAP` group should be exempted or reconciled with the next chunk because this range ends before its masks.
- Cross-header checks that every complete register block here has matching `regBIF_CFG_DEV2_EPF*_0_*` offset and base-index macros in `nbio_7_11_0_offset.h`.
- Hardware or simulator PCIe config dumps for NBIO 7.11 devices validating decoded vendor/device IDs, command/status bits, class codes, BAR values, PM state, PCIe link speed/width, MSI/MSI-X state, AER status/masks, ACS/PASID/ARI enables, DPA status, and reset timing values against these masks.
- Error-path tests around AER status/mask/severity decoding and clearing, including completion timeout, malformed TLP, ECRC, unsupported request, ACS violation, internal error, AtomicOp egress blocked, and TLP-prefix blocked conditions.
- Link and power-management tests covering FLR initiation, D3hot-to-D0 timing, PME behavior, ASPM/clock power management, link retraining, link bandwidth notifications, DPA substate control, and power-budget reporting.

### subset-b-003142: lines 49194-51624

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 49194-51624

## Purpose

This chunk is a generated AMD NBIO 7.11.0 shift/mask header segment. It exports preprocessor constants for bitfield positions and masks in NBIO PCIe configuration, RCC port decode, and BIF reset-control registers. The file is hardware metadata only: it has no functions, structs, variables, locks, allocations, or executable control flow.

The range starts mid-way through the `BIF_CFG_DEV2_EPF6_0` PCIe endpoint-function block at `LINK_CNTL`, continues through endpoint PCIe capability and enhanced-capability registers, covers RCC endpoint/downstream/downstream-port control blocks for devices 0-2, and then enters the `nbio_nbif0_bif_rst_bif_rst_regblk` reset block. It ends inside the `DEV2_PF2_FLR_RST_CTRL` field definitions, so adjacent chunks are needed for complete analysis of the preceding `BIF_CFG_DEV2_EPF6_0_LINK_CAP` register and the following `DEV2_PF2_FLR_RST_CTRL` masks plus later reset registers.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU ASIC register metadata and has no direct distributed-filesystem behavior.

## Public Surface

The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the raw register mask, usually as a C integer literal with an `L` suffix.

The macros are intended to be used with companion address metadata from `nbio_7_11_0_offset.h` and AMDGPU bitfield helpers such as `REG_GET_FIELD` or `REG_SET_FIELD`, plus the NBIO/SOC15 register access path selected by the caller. This header does not provide register addresses, reset defaults, read/write permissions, side-effect rules, or sequencing requirements.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both `nbio/nbio_7_11_0_offset.h` and this shift/mask header. Spot checks in the offset header show matching address entries for representative registers in this slice, including `regBIF_CFG_DEV2_EPF6_0_LINK_CNTL`, `regRCC_EP_DEV0_0_EP_PCIE_CNTL`, `regHARD_RST_CTRL`, and `regDEV2_PF2_FLR_RST_CTRL`. There is no sibling `nbio_7_11_0_default.h` in this tree, so default/reset-value validation for this NBIO version cannot rely on a local generated default header.

## Important Register Families

The `BIF_CFG_DEV2_EPF6_0` section describes one endpoint-function PCIe configuration space. It includes link control/status and PCIe 2.0 link/device capabilities: ASPM and PM control, link disable/retrain/common-clock/extended-sync controls, hardware autonomous width/speed disable bits, bandwidth interrupt enables/status, negotiated speed and width, DL active reporting, supported target link speeds, equalization status, de-emphasis, DRS signaling, RTM presence detection, AtomicOp/ARI/LTR/OBFF/10-bit-tag capability and enablement, completion-timeout controls, IDO enablement, emergency power reduction, and end-to-end TLP prefix support/blocking.

The same endpoint block then defines MSI and MSI-X capability layout: capability IDs and next pointers, MSI enablement, multi-message capability and enable fields, 64-bit address support, extended message data support, per-vector masking capability, message address/data registers for 32-bit and 64-bit forms, mask and pending-bit arrays, MSI-X table and PBA BIR/offset fields, table size, function mask, and MSI-X enable.

The endpoint enhanced-capability portion covers SATA capability/index/data registers, vendor-specific capability header/data fields, AER, BAR sizing/control, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and RTR capability blocks. AER fields include uncorrectable status/mask/severity for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields include receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow status/masks. The AER capability/control group exposes first-error pointer, ECRC generation/check support and enablement, multi-header receipt support/enablement, four TLP header log dwords, and four TLP prefix log dwords.

The BAR enhanced capability defines supported BAR sizes and per-BAR control for BAR1 through BAR6, including BAR index, size, upper supported-size bits, and total BAR count. Power budgeting fields describe selected power data, base power, data scale, PM state/substate, power rail, type, and whether the system allocates the power budget. DPA fields describe transition latency, power-allocation scale, maximum substate, current substate control/status, and substate power-allocation registers 0-7.

Isolation and address-translation capability groups include ACS capability/control fields for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, direct-translated P2P, and egress-control vector size. PASID fields expose max PASID width, execute permission and privileged mode support, and their enables. ARI fields expose next function number, MFVC/ACS function group capability, ARI function group value, and related enables. RTR is represented by an enhanced-capability header and two data registers.

The `RCC_*` sections describe endpoint and downstream port control blocks for devices 0, 1, and 2. Endpoint blocks include scratch registers, PCIe control and interrupt control/status, RX controls, bus/config controls, TX LTR control, DPA capability/control/substate power allocation, PME service timer, TX control/requester ID, error controls, and LC speed control. Fields control or report behavior such as malformed AtomicOp handling, unsupported-request reporting suppression, ignoring LTR invalid-message URs, immediate PMI behavior, hidden-register decode enables for Gen2 through Gen5, completion-timeout suppression, TPH disablement, relaxed/no-snoop override, requester ID bus/device/function, TX LTR private snoop and no-snoop requirements, flow-control checks for L1, PME service timing, and endpoint interrupt enables/status for correctable, non-fatal, fatal, miscellaneous, unsupported request, and power-state-change events.

The downstream and downstream-port `RCC_DWN_*`/`RCC_DWNP_*` blocks repeat a smaller control set for devices 0-2. They include reserved/scratch words, general downstream PCIe control, config control, RX control, bus control, config decode enables, error-control fields, LC speed/control fields, and LTR message information from the endpoint. These fields affect how the internal downstream-facing ports expose hidden registers, handle LTR and UR conditions, and manage link control/speed behavior.

The `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and `RCC_DEV0_EPF5_STRAP4` strap registers expose boot/configuration strap fields such as device ID, revision IDs, function enablement, D1/D2 support, legacy device type enablement, and strap-reserved or function-specific fields. These are hardware strap-derived configuration fields rather than ordinary runtime policy state.

The BIF reset section begins at `HARD_RST_CTRL`, `SELF_SOFT_RST`, `BIF_GFX_DRV_VPU_RST`, and `BIF_RST_MISC_CTRL*`, then defines FLR, D3hot-to-D0, power, instance-reset, and PF D-state interrupt status/mask registers. It also defines per-function FLR and D3hot-to-D0 reset controls for DEV0 PF0-PF7, DEV1 PF0-PF1, and the beginning of DEV2 PF0-PF2. Important fields include core/endpoint/downstream-port reset and sticky-reset controls, soft reset selectors, graphics/driver/VPU reset bits, miscellaneous reset policy, FLR interrupt status/masks, D3hot-to-D0 and power interrupt status/masks, D-state target/acknowledge/need-reset fields, PF/VF configuration and private reset enables, sticky reset enables, soft-PF and VF-VF reset domains, FLR twice-enable, FLR grace mode and timeout, DMA/host dummy response status selections, and soft PF PFCOPY private enablement where present.

## Control Flow

There is no local runtime control flow. Runtime use is external and follows the generated-register pattern:

1. AMDGPU code selects a register address from `nbio_7_11_0_offset.h`.
2. It reads or prepares a 16-bit or 32-bit register value through the appropriate NBIO/SOC15/PCIe config access helper.
3. It applies this header's `*_MASK` and `*__SHIFT` constants to extract a field or compose a new value while preserving unrelated bits.
4. The resulting value drives hardware behavior such as PCIe link management, interrupt routing, AER/DPA/ACS/PASID/ARI capability programming, RCC endpoint/downstream policy, or reset/FLR handling.

Several hardware flows are only implied by the field names: PCIe link training and retraining, equalization, MSI/MSI-X delivery, AER logging and clearing, DPA substate negotiation, LTR/PME signaling, hidden config-register decode, strap sampling, function-level reset, D3hot-to-D0 reset, power-state interrupt reporting, and reset-domain sticky behavior.

## State And Persistence Behavior

The header stores no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration, RCC control, strap, and reset registers. Persistence depends on the hardware reset domain, strap sampling, firmware/BIOS setup, PCIe reset, FLR, D3hot-to-D0 transitions, suspend/resume restore, power gating, and explicit AMDGPU writes.

Fields in this chunk include a mix of read-only capability bits, writable policy bits, latched status bits, interrupt status/mask bits, diagnostic log fields, and reset-control selectors. Status and log fields such as link status, AER status, MSI pending bits, interrupt status, D-state acknowledgements, and reset status may be live, latched, or write-one-to-clear depending on the hardware specification; this generated header does not encode those access semantics.

Strap registers should be treated as hardware-initialized configuration state. Reset-control fields can intentionally preserve or clear configuration/private/sticky domains across FLR or D3hot-to-D0 events. Code that writes them must understand which domain is being reset and whether firmware or another function owns the state.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database. The shift/mask header must stay synchronized with `nbio_7_11_0_offset.h`; representative matching offsets are present for the endpoint config block, RCC control blocks, and BIF reset block. Unlike several other NBIO generations in this tree, a local `nbio_7_11_0_default.h` is absent, so reset defaults are not available from a sibling generated file here.

The direct AMDGPU integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes this file with the matching offset header. Semantically, the fields integrate with PCI/PCIe standard capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, BAR sizing, power budgeting, DPA, SATA/VSEC vendor capability layout, endpoint/downstream RCC policy registers, and AMDGPU reset/FLR/D-state handling.

Consumers must rely on AMDGPU register helpers and PCIe/NBIO access paths for width, endianness, register-space selection, locking, ordering, polling, and side-effect handling. The macros alone do not protect reserved bits or enforce legal sequencing.

## Risks And Edge Cases

- The range starts and ends mid-family. Adjacent chunk research is required to reconstruct the complete `BIF_CFG_DEV2_EPF6_0_LINK_CAP` and `DEV2_PF2_FLR_RST_CTRL` definitions.
- Generated mask drift can compile cleanly but decode or program the wrong hardware bit, especially in repetitive DEV/PF and endpoint/downstream blocks.
- PCIe control fields for retraining, ASPM, target speed, AtomicOp, ARI, LTR, OBFF, PASID, ACS, MSI/MSI-X, AER, DPA, and BAR sizing can affect link stability, isolation, interrupt routing, error containment, power behavior, and address translation.
- Status and error-log fields may be write-one-to-clear or otherwise side-effectful. A read-modify-write using only masks from this header can be unsafe without the hardware access rules.
- Reset-control fields are high blast-radius. Incorrect PF/VF, soft-PF, sticky, FLR grace, or dummy-response programming can leave functions wedged, expose stale state after FLR, or reset domains still in use.
- RCC hidden-register decode and UR/LTR suppression fields can alter how internal config spaces respond to software and firmware. They should not be changed outside version-specific NBIO code.
- Strap fields should not be treated like ordinary writable runtime configuration without confirming access permissions and sampling behavior.
- Masks use untyped preprocessor integer literals, often with `L` suffixes and some full-width fields. Callers should keep the established AMDGPU register-helper types to avoid signedness, truncation, or width mistakes.

## Test Signals

- Build AMDGPU paths with NBIO 7.11 support enabled, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, to catch missing or renamed generated symbols.
- Run generated-header consistency checks: every field should have a matching shift and mask, masks should align with shifts, repeated DEV0/DEV1/DEV2 and PF blocks should match expected per-function differences, and reserved fields should not overlap defined fields.
- Cross-check register names in this chunk against `nbio_7_11_0_offset.h` so every shift/mask register maps to an address and base index.
- On NBIO 7.11 hardware, compare decoded endpoint PCIe config state against `lspci -vvxxx` or AMDGPU debug register dumps: link speed/width, MSI/MSI-X, AER masks/status, ACS/PASID/ARI, DPA, BAR capability, power-budget data, and vendor-specific capability headers should decode correctly.
- Exercise reset paths that use DEV/PF FLR and D3hot-to-D0 controls. Validate function recovery, interrupt status/mask behavior, D-state target/acknowledge fields, sticky reset preservation, and dummy-response behavior across FLR, hot reset, suspend/resume, and GPU reset.
- Validate RCC endpoint/downstream behavior with register traces around hidden config decode, LTR/PME handling, completion-timeout suppression, error interrupt enable/status, requester ID programming, and LC speed/link-control fields.
- For error handling, inject or observe AER/correctable/uncorrectable events where possible and verify the driver reports, masks, logs, and clears exactly the intended fields without disturbing unrelated status bits.

### subset-b-003143: lines 51625-54019

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 51625-54019

## Scope

This chunk covers generated shift and mask macros for AMD NBIO 7.11.0 register fields. The range starts in the middle of `DEV2_PF2_FLR_RST_CTRL` and continues through the end of `RCC_EP_DEV0_1_EP_PCIE_CNTL`; the following `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL` register belongs to the next chunk.

The covered area is concentrated around these address blocks and register families:

- Device 2 function reset and power-state controls: `DEV2_PF*_FLR_RST_CTRL`, `BIF_DEV2_PF*_DSTATE_VALUE`, `DEV2_PF*_D3HOTD0_RST_CTRL`, and port-level `BIF_PORT*_DSTATE_VALUE`.
- `nbio_nbif0_bif_misc_bif_misc_regblk`, including scratch registers, interrupt line polarity/enable, outstanding VC allocation, BIFC miscellaneous controls, BME error logs, DMA attribute override controls, PASID checks/status, SDP controls, performance counters, power-gating controls, SMN master controls, virtual-wire change controls, timeout detection, credit allocation, Z10 status, BDF controls, and common performance counter state.
- `nbio_nbif0_nbif_sion_SIONDEC`, covering SION client burst targets, time slots, pool-credit allocations, and global SION control.
- `nbio_nbif0_bif_ras_bif_ras_regblk`, covering central and leaf RAS controls/status plus RAS interrupt/vwire handoff fields.
- Initial RCC PCIe decode blocks for downstream, downstream-port, and endpoint device 0: `RCC_DWN_DEV0_1_*`, `RCC_DWNP_DEV0_1_*`, and `RCC_EP_DEV0_1_EP_PCIE_CNTL`.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It contains no C functions, structs, global variables, allocations, locks, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and NBIO 7.11.0 hardware registers. Each field is represented by the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, or compose that field.

The sibling `nbio_7_11_0_offset.h` header supplies register addresses and base indices. This file supplies the field layout used by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. The direct source-tree consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both the offset and mask headers for NBIO 7.11 register programming.

## Important Macro Families

### Device 2 Reset and D-State Controls

The chunk begins inside `DEV2_PF2_FLR_RST_CTRL` and then covers `DEV2_PF3_FLR_RST_CTRL` through `DEV2_PF6_FLR_RST_CTRL`. These registers expose per-PCI-function function-level reset policy bits:

- `PF_CFG_EN`, `PF_CFG_FLR_EXC_EN`, and `PF_CFG_STICKY_EN` describe configuration-space reset participation and sticky behavior.
- `PF_PRV_EN` and `PF_PRV_STICKY_EN` describe private register reset behavior.
- `FLR_GRACE_MODE`, `FLR_GRACE_TIMEOUT`, `FLR_DMA_DUMMY_RSPSTS`, and `FLR_HST_DUMMY_RSPSTS` describe reset grace handling and dummy response status behavior.

`BIF_DEV2_PF0_DSTATE_VALUE` through `BIF_DEV2_PF6_DSTATE_VALUE` expose target and acknowledged PCI power-state values for device 2 functions, plus `NEED_D3TOD0_RESET` bits that indicate whether a D3hot-to-D0 transition requires reset handling.

`DEV2_PF0_D3HOTD0_RST_CTRL` through `DEV2_PF6_D3HOTD0_RST_CTRL` provide a parallel reset-control family for D3hot-to-D0 transitions. These fields are narrower than the FLR reset controls and only cover config/private reset enables and sticky bits. `BIF_PORT0_DSTATE_VALUE`, `BIF_PORT1_DSTATE_VALUE`, and `BIF_PORT2_DSTATE_VALUE` expose target D-state and reset-needed bits at the port level.

### BIF Miscellaneous Control and Error Logging

The `nbio_nbif0_bif_misc_bif_misc_regblk` portion starts with simple scratch and interrupt-line controls:

- `MISC_SCRATCH` exposes a full 32-bit scratch field.
- `INTR_LINE_POLARITY` and `INTR_LINE_ENABLE` provide per-line control for interrupt line polarity and enable state.
- `OUTSTANDING_VC_ALLOC` records virtual-channel allocation limits and current outstanding count fields.

`BIFC_MISC_CTRL0` and `BIFC_MISC_CTRL1` are dense policy registers. They include fields for client response mode, FLR response behavior, reset clock gating, soft reset, GMI request class selection, pass-through behavior, read request ID selection, flush-on-reset behavior, interrupt acknowledgement, and GFX/VCN/SDMA display-related overrides. These fields are broad integration points because they influence how NBIF responds to PCIe, internal fabric, and reset events.

`BIFC_LC_TIMER_CTRL` provides a link-control timer field. `BIFC_RCCBIH_BME_ERR_LOG0` and `BIFC_RCCBIH_BME_ERR_LOG1` define captured Bus Master Enable error information, including error-valid, requester ID, client ID, subclient ID, attribute fields, address, and VF-related identifiers. These are diagnostic state registers used to identify illegal or unexpected DMA/BME activity.

### DMA Attributes, PASID, SDP, and Activity Controls

The chunk defines a large matrix of DMA attribute override registers:

- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV2_F6_F7` cover device/function pairs across devices 0, 1, and 2.
- Each register carries per-function override enables and replacement values for traffic class, snoop, relaxed ordering, PASID transaction attribute, and function ID.
- `BIFC_DMA_ATTR_CNTL2_DEV0`, `DEV1`, and `DEV2` add per-device default and override controls for destination indication, SP, PRIV, SEC, PASID address, and process address space behavior.

These macros are especially sensitive because DMA attributes affect PCIe ordering, snooping, security tagging, and PASID-based address translation.

`BIFC_PASID_CHECK_DIS`, `BIFC_PASID_STS`, `BIFC_ATHUB_ACT_CNTL`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, and `BIFC_SDP_CNTL_2` cover PASID validation controls/status, ATHUB activity gating or status policy, and SDP flow-control or response behavior. `BIF_PASID_ERR_LOG` has no field definitions in this slice, while `BIF_PASID_ERR_CLR` defines a broad set of clear bits for PASID error categories across clients and traffic types.

### Performance, Power, Clock, and Interrupt-Related Controls

Several small families expose NBIF telemetry and low-power behavior:

- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, and the low/high MMIO/DMA read/write counter registers define event selection, enable/clear bits, and split counter values.
- `NBIF_PERF_COM_COUNT_ENABLE`, `NBIF_BX_PERF_CNT_FSM`, and `NBIF_COM_COUNT_VALUE` expose common performance counting enable, FSM state, and count value fields.
- `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` cover power-gating master/slave handshakes, reset select, clock request overrides, and status selection.
- `NBIF_MGCG_CTRL_LCLK` and `NBIF_DS_CTRL_LCLK` cover medium-grain clock gating and light/deep sleep controls on LCLK-related logic.
- `NBIF_INTX_DSTATE_MISC_CNTL`, `NBIF_PENDING_MISC_CNTL`, `EP0_INTR_URGENT_CAP`, `EP1_INTR_URGENT_CAP`, `EP2_INTR_URGENT_CAP`, and `EP_PEND_BLOCK_MSK` describe interrupt/D-state wake behavior, pending-state handling, urgency capabilities, and endpoint pending-block masks.
- `NBIF_PWRBRK_REQUEST`, `OBFF_EMU_CFG`, `NBIF_VWIRE_CTRL`, `NBIF_SDP_VWR_VCHG_*`, and `NBIF_SHUB_TODET_*` support power-break requests, OBFF emulation, virtual-wire control/change/reset/trigger, and system hub timeout detection or sync-flood signaling.

The local `nbio_v7_11.c` driver code does not directly reference most names in this chunk, but it uses the same mask-header convention for NBIO initialization, doorbells, interrupt handling, memory access enablement, clock-gating, light-sleep, register remap, and PCIe-port access. These fields are available for the same NBIO 7.11 hardware block when future code or firmware-facing paths need them.

### SMN Master and GMI/SST/SDP Credit Controls

`SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define System Management Network master behavior and endpoint attributes. They include fields for request attributes, PASID, function ID, destination, address windowing, security/privilege attributes, poison/response handling, and endpoint-specific request shaping.

`BIF_GMI_WRR_WEIGHT`, `BIF_GMI_WRR_WEIGHT2`, and `BIF_GMI_WRR_WEIGHT3` expose weighted round-robin values. `BIFC_HRP_SDP_*`, `BIFC_GMI_SDP_*`, and `BIFC_GMI_SST_*` pool-credit allocation registers define request, data, read-response, and write-response credit counts. `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, and `BIFC_GSI_CNTL` add threshold, host arbitration, and global status interrupt policy fields.

These are hardware flow-control knobs. Incorrect programming can starve traffic, overrun pool credits, or perturb ordering/latency between PCIe, GMI, SDP, SST, and internal hub clients.

### SION Arbitration and Credit Shaping

The `nbio_nbif0_nbif_sion_SIONDEC` block is highly regular. For clients `CL0`, `CL1`, and `CL2`, it defines full-width fields for:

- Read-response burst target and time slot registers.
- Write-response burst target and time slot registers.
- Request burst target and time slot registers.
- Request, data, read-response, and write-response pool-credit allocation registers.

`SION_CNTL_REG0` contains many control fields: arbitration enablement, time-slot quantum, weight, client limit, response ordering, starvation-related controls, request/response gating, and debug/status selector fields. `SION_CNTL_REG1` adds a smaller set of control/status fields.

These masks describe the programmable arbitration contract for SION traffic. They are persistent hardware policy until reset or rewritten.

### BIF RAS Controls and Status

The `nbio_nbif0_bif_ras_bif_ras_regblk` section defines central and leaf reliability, availability, and serviceability controls:

- `BIFL_RAS_CENTRAL_CNTL` includes interrupt/event enable and propagation/stall controls.
- `BIFL_RAS_CENTRAL_STATUS` exposes event receive, fatal/nonfatal/correctable/error status, poison, parity, and propagation/stall status bits.
- `BIFL_RAS_LEAF0_CTRL`, `BIFL_RAS_LEAF1_CTRL`, and `BIFL_RAS_LEAF2_CTRL` each define error detection, poison/parity/receiver-error event enablement, stall enablement, generated and propagated error-event controls, debug enables, and RAS interrupt enablement.
- `BIFL_RAS_LEAF0_STATUS`, `LEAF1_STATUS`, and `LEAF2_STATUS` expose received error events, poison/parity detection, generated event status, egress stalled status, propagated event status, and propagated egress stalled status.
- `BIFL_IOHUB_RAS_IH_CNTL` and `BIFL_RAS_VWR_FROM_IOHUB` connect BIF RAS state to interrupt-handler and virtual-wire signaling.

RAS status fields are diagnostic and may be sticky or clear-on-write according to hardware behavior outside this header. The masks alone do not document the clear sequence, interrupt routing policy, or error containment rules.

### RCC PCIe Decode Blocks

The chunk ends with the first RCC PCIe decode blocks:

- `RCC_DWN_DEV0_1_DN_PCIE_RESERVED`, `SCRATCH`, `CNTL`, `CONFIG_CNTL`, `RX_CNTL2`, `BUS_CNTL`, and `CFG_CNTL` cover downstream decode behavior, hidden-register decode enables for PCIe generations 2 through 5, unsupported-request reporting, immediate PMI disable, AER completion timeout read-only behavior, LTR message UR behavior, and FLR extend mode.
- `RCC_DWNP_DEV0_1_PCIE_ERR_CNTL`, `RX_CNTL`, `LC_CNTL2`, and `LTR_MSG_INFO_FROM_EP` cover downstream-port error reporting, immediate error-message behavior, received-error clear bits, max-payload/traffic-class/short-prefix ignore controls, completion timeout disable, RCB FLR timeout disable, link-state and link-bandwidth notification disable, and captured LTR message information.
- `RCC_EP_DEV0_1_EP_PCIE_SCRATCH` and `RCC_EP_DEV0_1_EP_PCIE_CNTL` cover endpoint scratch, unsupported-request reporting disable, malformed atomic operations, and LTR-message unsupported-request ignore behavior.

The next chunk continues the endpoint PCIe interrupt, status, RX, bus, config, and LTR controls.

## Control Flow and State Behavior

This header chunk has no software control flow. It affects driver behavior at compile time by deciding which bits are read or written when code uses generated register helpers.

The state described by the macros is hardware state in the NBIO block. It includes reset policy, PCI power-state target/acknowledgement values, D3hot-to-D0 reset requirements, DMA attribute overrides, PASID validation and error clears, BME error logs, performance counter selection and split counter values, power-gating and clock-gating controls, SMN request attributes, virtual-wire triggers, timeout detection, arbitration weights, SION credit limits, RAS event controls/status, and RCC PCIe error/link/decode policy.

Some fields are durable configuration until reset or rewrite, such as DMA attribute overrides, SION arbitration limits, RAS event enables, hidden-register decode enables, and PCIe RX ignore controls. Other fields are status or diagnostic captures, such as D-state ack values, BME error logs, PASID status, performance counter values, RAS status, and LTR message information. A third class is command-like or clear-like, such as PASID error clear bits and downstream-port received-error clear bits. Code that writes these fields must respect hardware sequencing and avoid treating all masks as ordinary read-modify-write configuration.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_11_0_offset.h` provides the matching register addresses and base-index macros.
- `nbio_7_11_0_default.h`, where present for a register, provides reset/default values.
- AMDGPU helper macros compose and decode fields by naming the register and field, deriving the `__SHIFT` and `_MASK` constants from this header.

Observed source-tree integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` directly includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`. It uses the same generated masks to implement NBIO 7.11 operations: revision readout, memory-controller access enable/disable, doorbell ranges, interrupt-handler setup, HDP flush register offsets, clock-gating and light-sleep controls, register remap, and initial PCIe/NBIO tuning.
- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c` and `dcn351_resource.c` include the NBIO 7.11 offset header, so display resource code is aware of NBIO register addresses even though this mask chunk is not directly included there.
- Cross-generation NBIO and NBIF headers contain similarly named families for RCC PCIe, RAS, and device reset/D-state controls, but layouts are not guaranteed identical. Consumers must use the mask header matching the active IP version selected by the driver.

## Risks

- Bitfield drift is high impact. These macros encode a hardware contract; a wrong shift or mask can silently write the wrong bit in PCIe, reset, DMA, RAS, or power-management registers.
- Reset and D-state fields can affect FLR and D3hot-to-D0 recovery. Misprogramming can leave PCI functions partially reset, fail to preserve sticky state, or produce dummy responses in the wrong reset phase.
- DMA attribute and PASID override fields affect transaction ordering, snooping, privilege/security attributes, destination indications, and address-space semantics. Incorrect settings can cause data corruption, isolation failures, or hard-to-debug IOMMU/PASID faults.
- RAS enable/status fields interact with error containment and interrupt signaling. Enabling stalls or propagation incorrectly can turn recoverable fabric errors into hangs; disabling events can hide real hardware failures.
- SION, WRR, and credit allocation fields can perturb internal traffic fairness and liveness. Overly aggressive limits or weights can starve clients or trigger timeout paths.
- RCC PCIe controls can mask protocol errors, alter FLR timeout behavior, disable notifications, or expose hidden config spaces. These should be changed only when the matching hardware specification and platform policy require it.
- Many status/clear fields likely have special write semantics. Generic read-modify-write code can accidentally clear diagnostic state or fail to clear latched status if the field is write-one-to-clear.

## Test Signals

Useful validation for changes involving this chunk is mostly integration and hardware oriented:

- Build coverage: compile AMDGPU with NBIO 7.11 support to catch missing or misspelled generated macros in `nbio_v7_11.c` or other consumers.
- Header consistency: compare every touched register against the matching `nbio_7_11_0_offset.h` register names and any available default-header names; regenerated headers should preserve paired `__SHIFT` and `_MASK` definitions.
- Boot/probe smoke tests on NBIO 7.11 hardware: confirm AMDGPU probes, reads revision and memory size, enables MC access, configures doorbells, and initializes interrupt handling without PCIe AER regressions.
- Runtime reset tests: exercise FLR, suspend/resume, and D3hot-to-D0 transitions for affected device/function paths while watching for PCIe timeouts, dummy response errors, and device recovery failures.
- DMA/PASID tests: run KFD/ROCm or IOMMU/PASID workloads and monitor for PASID error logs, BME error logs, transaction faults, and data corruption.
- RAS tests: inject or observe correctable/nonfatal/fatal error paths if platform support exists, verifying RAS interrupt delivery and status reporting without unexpected fabric stalls.
- Performance/power tests: check NBIF performance counter readability, clock-gating/light-sleep behavior, and wake/pending interrupt behavior across idle, load, and resume.

### subset-b-003144: lines 54020-56559

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 54020-56559

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.11.0 shift/mask header. It defines bit-field geometry for NBIO/BIF/RCC/GDC registers used by the AMDGPU driver to program PCIe endpoint behavior, BIOS and SBIOS scratch registers, BIF interrupt and doorbell handling, HDP coherency flush signaling, PF mailbox registers, power-management controls, and per-engine doorbell range/fence registers.

The file is not executable logic. Its purpose is to provide C preprocessor constants that pair with `nbio_7_11_0_offset.h` register-address macros and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `RCC_EP_DEV0_1_*` and `RCC_EP_DEV0_2_*`: PCIe endpoint and downstream-port control fields. These cover correctable/nonfatal/fatal/user/misc/power-state interrupt enables and status bits, PASID/prefix/max-payload/TC completion-timeout receive error handling, hidden config-space decode enables for Gen2 through Gen5, LTR message values and requirements, DPA capabilities/control/substate power allocation, PME service timer, TX snoop/relaxed-ordering/TPH controls, requester ID fields, error-reporting disable, and immediate-error-message behavior.
- `BIF_BX0_*` and `BIF_BX1_*`: paired BIF instances with the same register shapes. They expose indirect PCIe index/data windows, SBIOS/BIOS scratch dwords, RLC/VCE/UVD interrupt control fields, GFX MMIO register CAM address/remap/CPL fields, BIF MM indirect access, bus coherency and flush-stall policy, reset and config-register routing controls, IH interrupt dummy-read setup, CLKREQ/PERST/PX/REF/PWRBRK pad controls, BIF feature/atomic controls, BIF doorbell control and doorbell interrupt/RAS status controls, framebuffer read/write enable, BACO entry/exit controls and timers, memory-type control, graphics address LUT control and entries, HDP remap controls, BIF ring-buffer control/base/pointers, mailbox index, and GPUIOV sizing.
- `BIF_BX_PF0_*` and `BIF_BX_PF1_*`: per-physical-function register fields. These include BME status, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate control addresses, per-engine HDP flush-only, invalidate-only, flush, and flush-done request masks, PF transaction-pending status, address-LUT bypass, four-dword transmit and receive mailbox buffers, mailbox valid/ack interrupt controls, and compact VM/HV mailbox data/valid/ack bits.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` and `RCC_STRAP2_RCC_DEV0_EPF0_STRAP0`: endpoint function strap fields for vendor/device identification, revision ID, subsystem vendor/device IDs, class code, function enable, legacy device type, and D1/D2 support. The NBIO 7.11 implementation reads revision ID from this strap family.
- `RCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN` and `RCC_DEV0_EPF0_0_RCC_CONFIG_MEMSIZE`: device-level doorbell aperture enable and config-space memory-size fields.
- `GDC0_*` and `GDC1_*`: graphics doorbell controller fields. This chunk covers queue FIFO arbitration priorities/modes, doorbell-sent status, per-engine doorbell range `OFFSET` and `SIZE` fields for SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE, VCN `NEED_DEDUCT` bits, ATDMA arbitration mode and VC weights, and doorbell fence enables for CP, SDMA, RLC, CSDMA, and VPE.

The macros in this chunk are consumed directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes `nbio_7_11_0_sh_mask.h` and its matching offset header.

## Control Flow and Runtime Behavior

This header has no runtime control flow. The runtime behavior is created by driver code that uses these constants in register read-modify-write operations.

Important implied flows include:

1. NBIO setup uses `BIF_BX1_BIF_FB_EN__FB_READ_EN_MASK` and `BIF_BX1_BIF_FB_EN__FB_WRITE_EN_MASK` to enable or disable memory-controller access through BIF.
2. Doorbell programming uses `GDC0_BIF_CSDMA_DOORBELL_RANGE`, `GDC0_BIF_VPE_DOORBELL_RANGE`, `GDC0_BIF_VCN0_DOORBELL_RANGE`, `GDC0_BIF_VCN1_DOORBELL_RANGE`, and `GDC0_BIF_IH_DOORBELL_RANGE` fields to set a doorbell base offset and range size, or to zero the size when a ring does not use doorbells.
3. Doorbell aperture setup uses `RCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN__BIF_DOORBELL_APER_EN` and PF self-ring aperture fields to expose CPU/GPU doorbell writes and self-ring behavior.
4. Interrupt setup uses `BIF_BX1_INTERRUPT_CNTL2__IH_DUMMY_RD_ADDR` and `BIF_BX1_INTERRUPT_CNTL` fields to program IH dummy-read and snoop behavior.
5. HDP flush handling uses `BIF_BX_PF1_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` offsets and masks to request coherency flushes and wait for the correct CP/SDMA engine completion bits.
6. PCIe indirect accesses use `BIF_BX1_PCIE_INDEX2`, `BIF_BX1_PCIE_DATA2`, `BIF_BX_PF1_RSMU_INDEX`, and `BIF_BX_PF1_RSMU_DATA` addresses from the offset header; this chunk defines field shapes for nearby index/data windows and PF support registers.
7. RAS and virtualization-related flows can use doorbell interrupt status/clear/disable bits, BME-low status bits, mailbox valid/ack fields, VM/HV mailbox fields, and transaction-pending fields.

The header does not enforce ordering. Callers must know when to disable a range before changing it, when to clear status bits, when to wait for HDP flush done, and when writes are safe during reset, BACO, suspend/resume, or SR-IOV transitions.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The represented state lives in NBIO 7.11 hardware registers.

State categories represented here include:

- PCIe endpoint policy state: interrupt enables/status, DPA capability/control/substate allocation, LTR message configuration, PME timer, requester ID, TX/RX error-handling controls, hidden configuration decode enables, and Gen2-Gen5 decode gating.
- Firmware and boot coordination state: SBIOS and BIOS scratch dwords, revision/device/class/subsystem strap fields, and memory-size reporting.
- BIF data-path and ordering state: bus coherency disables/enables, zero-byte enable policy, read/write stall controls, HDP flush stall controls, BIF feature disable bits, atomic outstanding limits, framebuffer read/write enables, BIF transaction pending fields, and address LUT entries/bypass.
- Interrupt and RAS-related state: IH dummy-read configuration, BIF doorbell/RAS/ATHUB interrupt status/clear/disable bits, RAS vector selection, BME-low status/clear bits, and doorbell monitor/intgen settings.
- Power-management state: BACO enable/power-off/mode/auto-exit bits, BACO exit timers, CLKREQB and other pad controls, D-state support straps, and DPA/LTR fields.
- Doorbell and ring-buffer state: global doorbell aperture enable, PF self-ring aperture base/control, GDC per-engine doorbell ranges, doorbell fence enables, GDC doorbell-sent status, BIF ring-buffer base/read/write pointers, and write-pointer host address fields.
- Mailbox state: PF transmit/receive mailbox data dwords, mailbox valid/ack controls, mailbox interrupts, and compact VM/HV mailbox payload/status bits.

Retention across GPU reset, PCI reset, BACO, suspend/resume, FLR, or SR-IOV PF/VF state changes is not described by the header. Those semantics depend on hardware and the AMDGPU initialization paths that rewrite these registers.

## Dependencies and Integration Points

Primary dependencies are adjacent generated NBIO 7.11 files:

- `nbio_7_11_0_offset.h` supplies `reg*` addresses and base indices for the registers whose fields are described here.
- `nbio_7_11_0_default.h`, if used by callers or validation scripts, supplies reset/default values.
- Adjacent chunks of this same `nbio_7_11_0_sh_mask.h` supply fields before `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL` and after `GDC1_BIF_DOORBELL_FENCE_CNTL`.

Concrete AMDGPU integration points observed in the source tree include:

- `amdgpu/nbio_v7_11.c` includes this header and uses its fields for MC access enable, doorbell range programming, VCN/VPE/CSDMA/IH doorbells, doorbell aperture enable, self-ring aperture setup, IH control, HDP flush register offsets/masks, memory-size reads, revision ID reads, and register remapping.
- `amdgpu/nbio_v7_7.c`, `amdgpu/nbio_v7_9.c`, `amdgpu/nbio_v7_2.c`, and `amdgpu/nbif_v6_3_1.c` use similarly named BIF/GDC/HDP doorbell and flush fields, giving useful comparison points for expected register geometry and behavior.
- Display resource code references `BIF_BX1_BIOS_SCRATCH_*` offsets for BIOS scratch state, so the scratch fields in this chunk are part of broader display/firmware integration even when the exact mask macros are simple full-dword definitions.
- SR-IOV and VM/HV mailbox paths in older NBIO/NBIF generations use the PF mailbox register family represented here. The field layout supports message-buffer dwords, valid/ack bits, and valid/ack interrupt enables.

Because this is generated hardware metadata, integration is by exact symbol naming. A caller must use a field macro whose register name matches the address macro passed to the SOC15/PCIE-port accessor.

## Risks

- Incorrect shifts or masks can silently program the wrong hardware bit. In this chunk, that can break PCIe error reporting, LTR/DPA power behavior, hidden config decode, doorbell routing, HDP coherency flush completion, interrupt delivery, or BACO exit behavior.
- `BIF_BX0` and `BIF_BX1`, and `PF0` and `PF1`, are near-duplicate register families. Using a PF0 mask with a PF1 address, or a BIF_BX0 field with a BIF_BX1 address, can compile but target the wrong instance.
- NBIO 7.11 code uses `PF1` for HDP flush, self-ring aperture, PCIe index/data, and memory-controller access in several places. Porting code from older generations that use PF0 can introduce subtle instance-selection bugs.
- Doorbell range fields have compact masks: offsets use bits 11:2 and most sizes use bits 20:16, while CSDMA uses a wider size field. Bad range values can overlap engines or disable rings.
- VCN doorbell range registers include `NEED_DEDUCT`, but the active NBIO 7.11 helper only programs `OFFSET` and `SIZE`. Callers changing VCN doorbell behavior need to preserve that bit correctly during read-modify-write.
- HDP flush request/done registers expose CP0-CP9, SDMA0/1, and many reserved engine bits. Reusing reserved bits as if they were new engines without matching hardware documentation can create false waits or missed flushes.
- Doorbell interrupt/RAS status registers combine status, clear, disable, and set-on-ring-enable bits. Write-one-to-clear and disable semantics must be handled carefully by driver code; this header only provides masks.
- BACO, DPA, LTR, PME, and CLKREQ/pad fields are power-management sensitive. Incorrect values can create resume, link-training, or low-power-state failures that may only appear under suspend/resume, runtime PM, or platform firmware flows.
- The chunk boundary splits the generated GDC1 family: it contains all of `GDC1_BIF_DOORBELL_FENCE_CNTL`, while `GDC1_S2A_MISC_CNTL` begins in the next chunk. Merge/reconciliation should not treat the absence of GDC1 S2A fields here as a source omission.

## Test and Validation Signals

Useful validation signals are mostly generated-header consistency checks plus hardware bring-up coverage:

- Build AMDGPU configurations that include `amdgpu/nbio_v7_11.c` to catch missing or malformed macros from this header.
- Mechanically verify every complete register in lines 54020-56559 has paired `__SHIFT` and `_MASK` definitions for each field. The only intentional chunk-boundary continuation is the next register after this chunk, `GDC1_S2A_MISC_CNTL`.
- Cross-check register names against `nbio_7_11_0_offset.h` so field macros used by `REG_SET_FIELD` and `REG_GET_FIELD` have matching address macros.
- Compare repeated `BIF_BX0` versus `BIF_BX1`, `PF0` versus `PF1`, `RCC_EP_DEV0_1` versus `RCC_EP_DEV0_2`, and `GDC0` versus `GDC1` field layouts for symmetry, allowing expected differences such as GDC0 having `S2A_MISC_CNTL` within this chunk while GDC1's starts in the next chunk.
- Exercise NBIO 7.11 boot and resume paths on supported ASICs and confirm memory-controller access, register remapping, HDP flush request/done polling, and interrupt dummy-read setup behave correctly.
- Validate CSDMA, VPE, VCN0/1, and IH doorbell programming by checking that ring writes reach the intended engine and that disabling a ring zeros only the `SIZE` field while preserving unrelated bits.
- Validate doorbell aperture and self-ring aperture programming with real doorbell writes, including high/low 64-bit base programming and aperture enable/disable transitions.
- Validate HDP coherency by issuing CP/SDMA work that requires HDP flushes and observing that the correct `GPU_HDP_FLUSH_DONE` mask bits are set before software proceeds.
- Run SR-IOV or virtualization mailbox coverage where applicable: mailbox valid/ack fields and interrupt enables should transition as expected without losing messages.
- Run RAS/doorbell interrupt tests or fault injection where available to confirm doorbell interrupt status, clear, and disable bits are read and written with the intended masks.

## Chunk Boundary Notes

This work item starts at `RCC_EP_DEV0_1_EP_PCIE_INT_CNTL`, after the previous endpoint PCIe section, and ends after the complete `GDC1_BIF_DOORBELL_FENCE_CNTL` register. The next line in the source starts `GDC1_S2A_MISC_CNTL`, so GDC1 S2A arbitration and 64-bit doorbell support fields belong to the following chunk, not this one.

### subset-b-003145: lines 56560-57899

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 56560-57899

## Scope

This chunk is the final generated AMDGPU NBIO 7.11.0 shift/mask header segment. It contains 1,107 `#define` field-layout macros over 1,340 source lines, covering 198 register names and 10 address-block comments. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the tail of `GDC1_BIF_DOORBELL_FENCE_CNTL`, continues through `GDC1_S2A_MISC_CNTL`, covers large BIF/RCC register groups for the `BX2`/`PF2` instance, and ends after the `GDC2_BIF_DOORBELL_FENCE_CNTL` masks and the file's closing `#endif`. Because this is the end of the header, no later chunk is needed to complete the final `GDC2` register group, but the first `GDC1_BIF_DOORBELL_FENCE_CNTL` register is split from the previous chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_11_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.11.0 register interface. For each hardware field it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This chunk describes NBIO BIF and RCC field geometry for PCIe index/data access, BIOS and SBIOS scratch storage, engine interrupt controls, MMIO remap CAMs, PCIe downstream and endpoint controls, Dynamic Power Allocation registers, reset/interrupt/pad controls, HDP coherency flush and invalidate handshakes, mailbox transport buffers, virtualization mailbox signaling, function doorbell aperture/memsize state, and the second GDC doorbell/fence block.

## Important Macro Families

The opening `GDC1` tail completes doorbell-fence masks for SDMA4/5, CSDMA, VPE, and one-shot trigger disable, then `GDC1_S2A_MISC_CNTL` exposes 64-bit doorbell support disable bits for SDMA0-5, CP, RLC, VPE, and CSDMA plus AXI host completion and arbitration-mode fields.

The `nbio_nbif0_bif_bx_SYSDEC` block defines indirect PCIe index/data registers (`BIF_BX2_PCIE_INDEX`, `DATA`, `INDEX2`, `DATA2`), SBIOS and BIOS scratch dwords, RLC/VCE/UVD BIF interrupt-control bits, UVD instance selection, and eight-entry GFX MMIO register CAM address/remap pairs with CAM enable and completion-value registers. These macros support firmware/driver scratch exchange, indexed PCIe access, interrupt event enabling, and address remapping around selected MMIO regions.

The downstream RCC blocks cover `RCC_DWN_DEV0_3_*` and `RCC_DWNP_DEV0_3_*` PCIe controls. Field names include hardware-init write lock, unsupported-request reporting disables, LTR message handling, PCIe config access settings, RX/TX and bus controls, error-control bits, link-speed control, link-control 2, and LTR message information from the endpoint.

The endpoint RCC block covers `RCC_EP_DEV0_3_*` registers for endpoint scratch, control, interrupt control/status, RX/BUS/CFG controls, TX LTR control, PME control, PCIe reserved/tx/requester/error/rx/link-speed controls, and PCIe Dynamic Power Allocation. DPA fields include function 1 substate power allocation entries 0-7 and function 0 DPA capability, latency indicator, control, and substate power allocation entries 0-7.

The BIF PF/SYS blocks define PF2 MM indirect access macros (`MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`), BIF MM indirect-access control, bus control, BIF scratch registers, reset enable/control, config-register control, interrupt controls, pad controls, feature controls, HDP atomic control, doorbell control and interrupt control, framebuffer enable, BIF interrupt control, VF master/slave transaction pending vectors, BACO control and exit timers, memory-type control, sixteen NBIF GFX address LUT entries, GFX reset control, remapped HDP flush controls, BIF ring-buffer base/read/write pointer registers, mailbox index, GPUIOV config size, and PERST/PX/REFPADKIN/CLKREQ/PWRBRK pad controls.

The PF2 BIFPFVF block covers bus-master-enable status, atomic error logging, doorbell self-ring GPA aperture base/control, HDP register and memory coherency flush controls, flush-only and invalidate-only request/done vectors for CP, SDMA, UVD, VCE, RLC, VPE, ACP, and reserved engines, BIF master/slave transaction-pending flags, address-LUT bypass, four transmit and four receive mailbox message-buffer dwords, mailbox valid/ack control, mailbox interrupt enables, and compact VM/HV mailbox data/valid/ack/intr bits.

The final endpoint-function block exposes `RCC_DEV0_EPF0_1_RCC_DOORBELL_APER_EN` and `RCC_CONFIG_MEMSIZE`, indicating per-function doorbell aperture enablement and memory-size configuration. The closing `GDC2` block mirrors the GDC doorbell theme with A2S queue FIFO arbitration, GFX doorbell-sent status, doorbell ranges for SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE, ATDMA arbitration/weight controls, and `GDC2_BIF_DOORBELL_FENCE_CNTL` enable bits for CP, SDMA0-5, RLC, CSDMA, VPE, and one-shot trigger disable.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. The constants are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, defaults, access widths, read/write permissions, reset domains, clear semantics, or sequencing. Consumers must use the matching generated address/default metadata, such as NBIO 7.11.0 offset/SMN/default headers, together with AMDGPU bitfield and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the appropriate PCI config, MMIO-indirect, SMN, NBIO, or mailbox access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU, firmware-facing, virtualization, PCIe, or power-management code selects a register address from companion NBIO generated metadata.
2. It reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or creates a write value by inserting field values while preserving unrelated and reserved bits.
3. The resulting values drive PCIe configuration, BIF reset and interrupt behavior, doorbell aperture and range programming, HDP coherency operations, mailbox handshakes, address remap/LUT decisions, power-management state, or transaction-pending polling.

The field names imply several asynchronous hardware flows outside this file: doorbell delivery and fencing, MMIO/PCIe indirect register access, firmware scratch exchange, engine command/hang/VM-busy interrupts, endpoint LTR/PME/DPA negotiation, BACO exit timing, HDP flush/invalidate request-done handshakes, GPU-to-host or VM/HV mailbox valid/ack protocols, and GDC queue arbitration.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO registers. Persistence depends on GPU reset domains, PCIe reset, BACO or power-gating transitions, firmware/BIOS initialization, PSP/SMU ownership, SR-IOV or hypervisor ownership, suspend/resume restore, and explicit driver writes.

Represented state includes BIOS/SBIOS and BIF scratch dwords, PCIe control and error-policy bits, interrupt enable/status fields, MMIO CAM address/remap entries, endpoint DPA power allocation records, reset/pad/power controls, BACO exit timers, memory-type and address-LUT programming, BIF ring-buffer pointers, mailbox payload and valid/ack bits, doorbell aperture and range definitions, HDP coherency request and completion vectors, and GDC arbitration/doorbell-fence controls.

Several names indicate status, latch, or handshake semantics (`INT_STATUS`, `TRANS_PENDING`, `FLUSH_REQ`, `FLUSH_DONE`, `VALID`, `ACK`, `BME_STATUS`, `DOORBELL_SENT`). The shift/mask header does not define how those bits clear, whether reads are destructive, or which bits are write-one-to-clear; callers must follow the hardware specification and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database and must stay synchronized with sibling headers that provide register addresses, default values, and access routing. It is intended to be included through AMDGPU ASIC register include stacks under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO/BIF code, PCIe config and link-management paths, firmware and SBIOS handoff paths, engine interrupt handling for RLC/VCE/UVD, GFX MMIO remapping, PCIe endpoint/root-complex controls, dynamic power-management, BACO reset/power transitions, SR-IOV or hypervisor mailbox paths, HDP cache/coherency flush logic, doorbell setup for CP/SDMA/IH/VCN/RLC/CSDMA/VPE, and GPUIOV configuration.

The PF2 mailbox and VM/HV mailbox fields are especially tied to virtualization and host-driver coordination. The HDP coherency request/done fields integrate with memory visibility between GPU engines and host-visible apertures. The GDC doorbell range and fence fields integrate with queue submission plumbing because incorrect doorbell routing can prevent work from reaching the intended engine.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while targeting the wrong hardware bit, causing PCIe configuration failures, reset hangs, missed interrupts, incorrect doorbell routing, or broken coherency flushes.
- This chunk begins mid-register with `GDC1_BIF_DOORBELL_FENCE_CNTL`; whole-file reconciliation must merge the preceding CP/SDMA/RLC fields from the previous chunk before treating that register as complete.
- Repeated scratch, CAM, DPA substate, LUT, mailbox-buffer, HDP engine-vector, and doorbell-range definitions are mechanically patterned. A single index mismatch can create function-, engine-, or instance-specific failures that are hard to reproduce.
- Doorbell range fields use offset and size masks with different widths for CSDMA compared with most other GDC2 ranges. Consumers must not assume every engine range has the same size encoding.
- HDP flush and invalidate request/done vectors span many named engines and reserved engines. Code must poll the correct done bit for the requested engine and avoid clearing or overwriting unrelated pending requests.
- Mailbox valid/ack fields require ordered handshakes. Writing message-buffer dwords without the expected valid/ack sequencing can drop messages, duplicate notifications, or wedge host/guest communication.
- Reset, BACO, pad-control, and clock/power fields can affect link availability or physical signaling. Writes need hardware-specific ordering and wait conditions not represented in this header.
- PCIe error-control, unsupported-request, LTR, PME, and DPA fields affect platform power and error reporting. Incorrect values can hide real faults, generate spurious PCIe errors, or break low-power transitions.
- BIOS/SBIOS scratch and firmware-owned registers may be shared with platform firmware. Driver updates must preserve ownership rules and avoid treating scratch state as stable across reset or suspend.
- Transaction-pending status and BME status are observations of in-flight hardware state. Polling code must include timeouts and reset-aware behavior.

## Test Signals

- Build AMDGPU with NBIO 7.11.0 support enabled. Compile-time coverage catches removed, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit 32-bit register width, repeated indexed groups should preserve stride/index naming, and boundary registers should be reconciled with adjacent chunks.
- Cross-check every register name in this chunk against NBIO 7.11.0 address/default headers so field layouts map to known registers and reset values.
- On supported hardware, validate PCIe enumeration, bus mastering, link speed changes, LTR/PME behavior, DPA state reporting, suspend/resume, BACO entry/exit, and GPU reset recovery.
- Exercise queue submission and doorbell paths for CP, SDMA0-5, IH, VCN0/1, RLC, CSDMA, and VPE; confirm doorbell ranges, aperture enables, sent status, and fence controls match expected engine behavior.
- Exercise HDP coherency flush and invalidate paths under CPU/GPU shared-memory workloads; trace request and done bits for selected engines and watch for stale data or timeout regressions.
- Exercise virtualization or host/guest mailbox flows where available, confirming message dwords, valid/ack bits, and mailbox interrupts progress in the documented order.
- Validate interrupt controls for RLC, VCE, and UVD command-complete, hang, and VM-busy events where hardware and test firmware support injection or observation.
- Check MMIO CAM and address-LUT programming with register traces to ensure remap and bypass settings preserve reserved bits and do not alias unrelated MMIO space.
