# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 95299-97677

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.0 register mask header. It begins inside the `BIFPLR3_2_PCIE_DPC_CAP_LIST` register field definitions, completes the `BIFPLR3_2` Downstream Port Containment, root-port PIO, and ESM capability groups, then enters the `addressBlock: nbio_pcie0_bifplr4_cfgdecp` section. The `BIFPLR4_2` portion covers a root-port/bridge PCI configuration decoder from standard PCI header fields through PCIe capabilities, MSI, vendor-specific capabilities, virtual channels, device serial number, Advanced Error Reporting, secondary PCIe lane equalization, ACS, multicast, L1 PM substates, DPC, root-port PIO diagnostics, and the ESM capability bitmap through part of `PCIE_ESM_CAP_6`.

The file is a generated hardware register bitfield contract. This chunk defines preprocessor constants only. It does not define functions, structs, variables, storage, or executable behavior.

## Purpose

The purpose of this header range is to expose the bit-level ABI for NBIO 7.0 PCIe root-port configuration and diagnostic registers. Each hardware field is represented in the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to extract or compose the field.

Driver code pairs these constants with register offset definitions from the matching NBIO offset header and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, or SOC15 register-access wrappers. The constants are not policy by themselves; they are the encoding map that lets runtime code interpret PCIe capability, link, power, isolation, and error-reporting register values correctly.

## Important Macro Families

### BIFPLR3 DPC and Root-Port PIO Tail

The opening part finishes the `BIFPLR3_2` Downstream Port Containment capability group. `BIFPLR3_2_PCIE_DPC_CAP_LIST` advertises DPC interrupt message number, root-port extension support, poisoned-TLP egress blocking support, software-trigger support, RP PIO log size, and data-link-active error-corrected signaling support. `BIFPLR3_2_PCIE_DPC_CNTL` exposes writable containment controls such as trigger enable, completion control, interrupt enable, corrected-error enable, poisoned-TLP egress blocking enable, software trigger, and data-link-active error-corrected enable. `BIFPLR3_2_PCIE_DPC_STATUS` carries containment status, trigger reason, interrupt status, root-port busy state, trigger reason extension, and the first RP PIO error pointer. `BIFPLR3_2_PCIE_DPC_ERROR_SOURCE_ID` contains the source ID associated with a DPC event.

The `BIFPLR3_2_PCIE_RP_PIO_*` registers define root-port PIO completion failure handling. `STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` share field names for configuration, I/O, and memory unsupported requests, completer aborts, and completion timeouts. Their identical field layout is intentional, but their semantics differ: status reports observed events, mask controls reporting, severity classifies events, sys-error maps events to system error signaling, and exception maps events to exception handling. `HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` are whole-dword log registers for captured TLP header, implementation-specific, and TLP prefix information.

### BIFPLR3 ESM Capability

The `BIFPLR3_2_PCIE_ESM_*` group defines an Equalization/ESM-style extended capability block. `CAP_LIST`, `HEADER_1`, and `HEADER_2` provide capability ID, version, next pointer, vendor ID, capability revision, capability length, and nested capability ID fields. `ESM_STATUS` exposes minimum time in EI value and scale fields. `ESM_CTRL` has enable and data-rate selector bits, including Gen3 and Gen4 data-rate controls.

`BIFPLR3_2_PCIE_ESM_CAP_1` through `BIFPLR3_2_PCIE_ESM_CAP_7` are dense bitmaps of supported ESM rates. The naming increments in tenths of GT/s style units, beginning at `ESM_8P0G` and continuing through `ESM_28P0G` by the end of the `BIFPLR3_2` block. Each rate has a one-bit shift and mask. Consumers should treat these as capability bits, not as numeric field values.

### BIFPLR4 Standard PCI Bridge Header

The `addressBlock: nbio_pcie0_bifplr4_cfgdecp` marker introduces a separate root-port bridge instance. `BIFPLR4_2_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` define the standard PCI configuration header. The `COMMAND` register covers I/O access, memory access, bus mastering, special cycles, memory-write-and-invalidate, VGA palette snoop, parity response, wait-cycle control, SERR enable, fast back-to-back enable, and interrupt disable. `STATUS` reports interrupt state, capability-list presence, 66 MHz support, fast back-to-back capability, parity and abort conditions, DEVSEL timing, and detected parity error.

The bridge routing and aperture registers include `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`. These encode primary/secondary/subordinate bus numbers, secondary latency timer, I/O base and limit, memory base and limit, and 64-bit prefetchable memory range bounds. A wrong bitfield in these macros would affect PCI enumeration and downstream address decoding.

`CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL` complete the bridge header. Bridge-control fields cover parity response, SERR, ISA/VGA routing, VGA 16-bit decode, secondary bus reset, fast back-to-back enable, and discard timer/error controls. The extended bridge control includes the port-80 enable bit used by platform routing/debug behavior.

### Power Management and Base PCIe Capability

`BIFPLR4_2_PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define the PCI Power Management capability. They cover capability list linkage, PM version, PME clock, device-specific initialization, auxiliary current, D1/D2 support, PME support bitmap, current power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus power/clock control enable, and PM data.

`BIFPLR4_2_PCIE_CAP_LIST` and `PCIE_CAP` expose the PCIe capability header, device type, slot-implemented bit, and interrupt message number. `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe and control endpoint/root-port PCIe behavior: maximum payload, phantom functions, extended tags, L0s/L1 latency, role-based error reporting, function-level reset, error-reporting enables, relaxed ordering, max payload size, extended tag enable, phantom function enable, auxiliary PM, no-snoop, max read request, bridge configuration retry enable, corrected/nonfatal/fatal/unsupported-request status, AUX power, and transaction-pending state.

`LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover PCIe link advertisement and live state. Important fields include supported link speeds, maximum link width, ASPM support and control, L0s/L1 exit latency, clock power management, surprise-down reporting, data-link-layer active reporting, bandwidth notification support, port number, read completion boundary, link disable, retrain, common clock configuration, extended sync, hardware autonomous width disable, bandwidth interrupt enables, current link speed and width, link training, slot clock configuration, data-link-layer active, and bandwidth-management status.

### Slot, Root, Capability 2, and MSI

`SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` map hotplug and slot-management fields, including attention button, power controller, MRL sensor, attention/power indicators, hotplug surprise and capability bits, slot power limit and scale, interlock, command completed support, physical slot number, event enables, indicator controls, power control, electromechanical interlock control, data-link-state change enable, and presence/interlock/data-link-change status bits.

`ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` define root-port error and PME handling: SERR on correctable/nonfatal/fatal errors, PME interrupt enable, CRS software visibility, PME requestor ID, PME status, and PME pending.

`DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` cover second-generation PCIe features. These include completion timeout ranges and controls, ARI forwarding, atomic-op routing and blocking, ID-based ordering, LTR, TPH completer support, OBFF, extended format and end-to-end TLP prefix support, emergency power reduction, 10-bit tags, lower SKP OS generation, target link speed, compliance mode, hardware autonomous speed disable, selectable de-emphasis, transmit margin, enter modified compliance, compliance SOS, equalization controls and phase-success bits, current de-emphasis level, retimer presence, emergency power reduction initialization, and associated status flags.

The MSI and subsystem groups are `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MSG_DATA_64`, `SSID_CAP_LIST`, and `SSID_CAP`. They provide MSI enablement, multiple-message capability and enable fields, 64-bit address capability, per-vector masking support, MSI address/data payloads, and subsystem vendor/device IDs. `MSI_MAP_*` maps MSI translation capability and address registers.

### Vendor-Specific, Virtual Channel, Serial Number, and AER

`BIFPLR4_2_PCIE_VENDOR_SPECIFIC_*` defines a PCIe vendor-specific extended capability list entry, vendor-specific header fields, and two vendor-specific data dwords. `PCIE_VC_*`, `PCIE_PORT_VC_*`, and `PCIE_VC0/VC1_RESOURCE_*` define virtual-channel capability, arbitration, status, traffic class mapping, VC IDs, VC enable state, load table controls, arbitration selection, negotiation pending, and table status fields.

`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2` expose the device serial number capability and two 32-bit serial-number dwords.

`PCIE_ADV_ERR_RPT_ENH_CAP_LIST` starts Advanced Error Reporting. `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` share uncorrectable error fields for data link protocol error, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, uncorrectable internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory nonfatal, correctable internal error, and header-log overflow.

`PCIE_ADV_ERR_CAP_CNTL` provides first-error pointer, ECRC generation/check capability and enables, multiple header recording, and TLP prefix log presence. `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` are full 32-bit captured log dwords. `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID` define root-port AER reporting enable bits, received and multiple error status, first uncorrectable fatal classification, advanced error interrupt message number, and correctable/uncorrectable source IDs.

### Secondary PCIe, Equalization, ACS, Multicast, and L1 PM

`PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS` define the secondary PCIe extended capability and lane-error bitmap. `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` repeat the same four fields per lane: downstream port transmitter preset, downstream port receiver preset hint, upstream port transmitter preset, and upstream port receiver preset hint. This regularity is important for code that iterates over lanes during equalization or diagnostics.

`PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services fields: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability, and egress control vector size. These fields integrate with peer-to-peer routing and isolation policy.

`PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, `PCIE_MC_RCV0/1`, `PCIE_MC_BLOCK_ALL0/1`, `PCIE_MC_BLOCK_UNTRANSLATED_0/1`, and `PCIE_MC_OVERLAY_BAR0/1` define the PCIe multicast capability. They include multicast group count, multicast enable, base address, receive masks, block-all masks, untranslated-block masks, and overlay BAR size/address fields.

`PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` define L1 PM substate support and controls. The fields cover PCI-PM L1.2/L1.1 support, ASPM L1.2/L1.1 support, L1 PM substate support, common-mode restore time, power-on scale/value, L1.2/L1.1 enable bits, LTR L1.2 threshold value/scale, and T_POWER_ON timing controls.

### BIFPLR4 DPC, RP PIO, and ESM

`BIFPLR4_2_PCIE_DPC_ENH_CAP_LIST`, `DPC_CAP_LIST`, `DPC_CNTL`, `DPC_STATUS`, and `DPC_ERROR_SOURCE_ID` mirror the `BIFPLR3_2` DPC layout for this root-port instance. These fields control and report containment behavior for severe downstream PCIe errors.

`BIFPLR4_2_PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` repeat the same config/I/O/memory unsupported-request, completer-abort, and completion-timeout fields used by `BIFPLR3_2`. `HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` again expose captured TLP context as whole-register dwords.

The final section defines `BIFPLR4_2_PCIE_ESM_*`. `CAP_LIST`, `HEADER_1`, `HEADER_2`, `STATUS`, and `CTRL` provide ESM capability metadata, minimum time-in-EI fields, and enable/data-rate controls. `ESM_CAP_1` through the covered portion of `ESM_CAP_6` provide one-bit capability entries from `ESM_8P0G` through `ESM_24P4G`. The adjacent following chunk continues the remaining `ESM_CAP_6` masks and later ESM capability registers.

## Control Flow

There is no runtime control flow in this header chunk. The only structure is generated ordering: register comments followed by `#define` constants for shifts and masks. Runtime control flow lives in code that includes this header and decides when to read, write, or decode the associated PCIe/NBIO registers.

The implicit access pattern for writable fields is read-modify-write: read the register, clear a field using its mask, shift the desired value by the field's `__SHIFT`, apply the mask, and write the composed value. For status and log registers, consumers typically read and decode the field, then clear or preserve it according to hardware access rules that are not encoded in this file.

## State and Persistence Behavior

The macros are compile-time constants and have no state or persistence. The hardware registers they describe represent several state classes:

- Configuration identity and capability advertisement, such as vendor/device IDs, class codes, PCIe capability headers, serial number, ACS capability, DPC capability, ESM capability, and multicast capability.
- Writable policy and control state, including PCI command bits, bridge apertures, MSI enable and message fields, device/link/slot/root controls, VC controls, ACS controls, multicast controls, L1 PM controls, DPC controls, AER masks/severity, and ESM controls.
- Volatile status state, including link training, negotiated speed/width, slot events, root PME state, AER status, DPC trigger and busy state, RP PIO status, secondary lane error status, and ESM status.
- Diagnostic capture state, including AER TLP header/prefix logs, RP PIO TLP header/prefix logs, implementation-specific PIO logs, DPC error source ID, and AER source ID.

Resets, secondary bus reset, link retraining, power-state transitions, firmware reinitialization, DPC containment, and hardware error events can change the backing register values. This header does not describe reset values; those are kept in matching generated default headers.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 register-address headers for the corresponding `BIFPLR3_2` and `BIFPLR4_2` registers. The mask names are useful only when paired with the matching register address and the correct root-port instance. Other generated files in the same directory provide default values and offsets; newer NBIO variants may have similar names but not identical fields.

Important integration areas include:

- PCI enumeration and bridge-resource setup using command/status, bus number, I/O window, memory window, and prefetchable window fields.
- PCIe link management using link capability/control/status, Link Control 2/3, lane error status, per-lane equalization controls, and ESM rate capability/control fields.
- Power management using PMI fields and L1 PM substate support/timing/control fields.
- Interrupt and message setup using MSI capability, MSI mapping, root error command/status, DPC interrupt fields, and advanced-error interrupt message number fields.
- Error handling and diagnostics using AER status/mask/severity, header and prefix logs, DPC status/source ID, RP PIO status/mask/severity/sys-error/exception, and PIO logs.
- Isolation and routing policy using ACS, virtual channels, ARI-adjacent capability data from neighboring chunks, and multicast capability/control registers.
- Hotplug and root-port service paths using slot capability/control/status and root PME/error fields.

## Risks

The primary risk is bitfield drift from the hardware specification or generated register database. Incorrect shifts or masks can silently corrupt read-modify-write operations or misdecode hardware state. The highest-risk fields are writable controls and error/security policy bits: bridge aperture fields, bus-master and memory-enable bits, AER masks/severity, DPC controls, ACS controls, multicast routing bits, L1 PM controls, link retrain/disable controls, and per-lane equalization presets.

The repeated naming is another risk. `BIFPLR3_2` and `BIFPLR4_2` contain many identical field names with different register prefixes. Accidentally using a macro from the wrong root-port prefix can compile cleanly while addressing the wrong port's register layout. The same issue applies across NBIO versions such as `nbio_7_0` and `nbio_7_7_0`, where similar blocks may gain or lose fields.

Several registers intentionally have confusing names such as `*_MASK__*_MASK_MASK`, because the register is itself a mask register and the field is also named `MASK`. Automated cleanup should not simplify these names. Status, mask, severity, sys-error, and exception registers often share identical field names but have different write/read semantics.

Whole-register log fields use shift zero and `0xFFFFFFFFL` masks. They should be treated as raw captured dwords, not as packed subfields defined by this header. Conversely, multi-bit fields such as link speed, link width, bridge apertures, slot power limit, completion timeout, equalization presets, LTR thresholds, and ESM status fields require both the mask and shift; testing only single-bit flags would miss width or offset errors.

This chunk ends mid-register in `BIFPLR4_2_PCIE_ESM_CAP_6`: it includes all shifts and masks only through `ESM_24P4G_MASK`. Merge/reconciliation must combine it with the adjacent chunk before making whole-register statements about `ESM_CAP_6`.

## Test Signals

Useful validation signals for this chunk are mostly generated-header and hardware integration checks:

- Kernel or AMDGPU build coverage that includes this header and catches missing or renamed macros.
- Static checks that each field has a matching `__SHIFT` and `_MASK` entry, with special attention to the chunk boundary in `BIFPLR4_2_PCIE_ESM_CAP_6`.
- Diffs against the authoritative NBIO 7.0 register source for all `BIFPLR3_2` and `BIFPLR4_2` fields in this range.
- PCIe enumeration tests on NBIO 7.0 hardware validating bridge identity, bus numbers, memory/I/O apertures, MSI capability, link capability, slot/root capability, and subsystem IDs.
- Link-management and power-management tests covering negotiated link speed/width, link retrain, equalization presets, ESM capability decode, ASPM/L1 substates, and resume latency.
- AER/DPC fault-injection or observation tests confirming uncorrectable/correctable error status, masks, severity, source IDs, TLP logs, DPC trigger/status/source ID, and RP PIO logs decode correctly.
- Isolation/routing tests for ACS, virtual channels, multicast, and peer-to-peer scenarios, especially where IOMMU, hotplug, or multi-function routing behavior depends on these fields.
