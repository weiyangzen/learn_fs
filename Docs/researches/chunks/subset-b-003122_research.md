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
