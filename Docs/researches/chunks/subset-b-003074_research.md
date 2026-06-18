# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 14815-17235

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.0 register mask header. It starts in the tail of the `BIF_CFG_DEV1_EPF2_0` endpoint-function PCIe Advanced Error Reporting log area and continues through endpoint-function enhanced capability fields for BAR sizing, power budget, dynamic power allocation, ACS, and ARI. The range then enters the `nbio_pcie0_bifplr0_cfgdecp` address block and defines most of the `BIFPLR0_0` root-port/bridge PCI configuration bitfields, including base PCI bridge header fields, PCI power management, PCIe capability, link/slot/root controls, MSI and vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, lane equalization, ACS, multicast, L1 PM substates, DPC, RP PIO logging, and ESM capability fields. The final portion starts `nbio_pcie0_bifplr1_cfgdecp` and covers the beginning of the matching `BIFPLR1_0` root-port bridge definitions through the first `SLOT_CAP` fields.

The file is a generated hardware register bitfield contract. This chunk contains preprocessor constants only: no functions, structs, variables, storage allocation, or executable control flow are defined here.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU code when reading, composing, or decoding NBIO/PCIe configuration registers for NBIO 7.0 hardware. Every register field is represented in the conventional AMD register-header form:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field.

The sibling NBIO offset header supplies register addresses; this `*_sh_mask.h` file supplies the field positions and masks for those addresses. Driver code typically consumes these definitions through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, SOC15 register accessors, or PCI/NBIO wrapper functions. Because the constants mirror hardware layout, their main value is stable, exact register encoding rather than local algorithmic behavior.

## Important Macro Families

### Endpoint Function PCIe Extended Capabilities

The opening lines finish the `BIF_CFG_DEV1_EPF2_0_PCIE_HDR_LOG*` and `BIF_CFG_DEV1_EPF2_0_PCIE_TLP_PREFIX_LOG*` groups. These expose full 32-bit TLP header and prefix log dwords used after AER events. The fields all start at shift zero with `0xFFFFFFFFL` masks, indicating whole-register payload capture rather than packed subfields.

`BIF_CFG_DEV1_EPF2_0_PCIE_BAR_ENH_CAP_LIST` and `BAR1_CAP/CNTL` through `BAR6_CAP/CNTL` define a PCIe enhanced BAR capability block for endpoint function 2. The common fields are capability ID, version, next pointer, supported BAR size bitmap, BAR index, total BAR count, and selected BAR size. These constants matter to enumeration and resizable/enhanced BAR handling, where confusing `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE` encodings can expose the wrong resource aperture.

`BIF_CFG_DEV1_EPF2_0_PCIE_PWR_BUDGET_*` maps PCIe power budget capability fields. It includes data selection, base power, scale, power-management state/substate, budget type, power rail, and whether the budget is system allocated. Consumers must interpret these fields as firmware/platform-advertised capability data, not as generic power-control knobs.

`BIF_CFG_DEV1_EPF2_0_PCIE_DPA_*` maps dynamic power allocation capability fields. It defines maximum substates, transition latency units/values, power allocation scale, latency indicator bits, current substate status, substate-control enable, substate-control selection, and per-substate power allocations for substates 0 through 7. The status/control split is important: status fields report hardware-selected state, while `DPA_CNTL` fields encode software control of substate policy.

`BIF_CFG_DEV1_EPF2_0_PCIE_ACS_*` defines Access Control Services capability/control fields for source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size. `BIF_CFG_DEV1_EPF2_0_PCIE_ARI_*` follows with Alternative Routing-ID Interpretation capability/control fields, including MFVC function groups, ACS function groups, next function number, MFVC enable, ACS enable, and function group selection.

### BIFPLR0 PCI Bridge Header

The `addressBlock: nbio_pcie0_bifplr0_cfgdecp` marker introduces the first PCIe bridge/root-port configuration decoder block. `BIFPLR0_0_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` provide the standard PCI configuration header field layout. `COMMAND` carries I/O access, memory access, bus master, special cycle, write-and-invalidate, VGA palette snoop, parity response, wait cycle, SERR, fast back-to-back, interrupt disable, and reserved bits. `STATUS` exposes interrupt status, capability-list presence, 66 MHz capability, fast back-to-back capability, parity and abort/error status, DEVSEL timing, and detected parity.

The bridge-window registers define routing aperture fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`. These encode primary/secondary/subordinate bus numbers, I/O base/limit, non-prefetchable memory base/limit, and 64-bit prefetchable memory bounds. Bugs in these bit positions can misrepresent bridge apertures and break downstream device enumeration or address routing.

`CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL` complete the basic bridge area. Notable control fields include parity response, SERR, ISA/VGA routing, secondary bus reset, fast back-to-back enable, and I/O port 80 enable.

### Power Management and Core PCIe Capability

`BIFPLR0_0_PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define the PCI Power Management capability. The fields cover capability ID/next pointer, PM capability version, PME clock, device-specific init, auxiliary current, D1/D2 support, PME support, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data. These fields are used when the driver or PCI core reasons about device power states, wake support, and reset expectations.

`BIFPLR0_0_PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` define the base PCI Express capability. The capability fields include device type, slot implemented, interrupt message number, maximum payload support/size, max read request size, relaxed ordering, extended tag, no-snoop, auxiliary power PM, function-level reset capability, error reporting enables, and error/transaction-pending status. These masks are central to PCIe link bring-up and error policy because they encode both advertised hardware capability and writable control bits.

`BIFPLR0_0_LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover negotiated link behavior: speed, width, ASPM/PM support, L0s/L1 latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification, port number, retrain/link disable controls, common clock configuration, extended sync, autonomous width disable, link bandwidth interrupt enables, current speed/width, link training, slot clock configuration, data-link active, and bandwidth-management status.

Slot/root capability groups add hotplug and PME/error paths. `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` include attention button, power controller, MRL sensor, indicators, surprise/hotplug capability, slot power limit/scale, interlock, command-completed support, physical slot number, hotplug interrupt enables, indicator controls, power control, presence detect, and data-link-state change status. `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` carry SERR-on-error enables, PM interrupt enable, CRS software visibility, PME requestor ID, PME status, and pending state.

### PCIe Capability 2, MSI, SSID, Vendor, and Virtual Channels

`BIFPLR0_0_DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` cover the second-generation PCIe capability registers. They include completion timeout support/control, ARI forwarding, atomic operation support, LTR, TPH completer support, OBFF, extended format/end-to-end prefix support, emergency power reduction, ID-based ordering, 10-bit tag support, lower SKP OS generation, link target speed, compliance mode, hardware autonomous speed disable, selectable de-emphasis, transmit margin, equalization control/status, current de-emphasis level, equalization phase success bits, retimer presence, and emergency power-reduction controls.

The MSI group defines capability-list linkage, MSI enable, multiple-message capability/enable, 64-bit address capability, per-vector masking capability, message address low/high, and message data fields. `SSID_CAP_LIST` and `SSID_CAP` define subsystem vendor/device IDs. `MSI_MAP_*` maps MSI translation capability fields and MSI mapping address low/high registers.

The vendor-specific and virtual-channel groups are higher-level PCIe extended capabilities. `PCIE_VENDOR_SPECIFIC_*` exposes capability ID/version/next pointer, vendor-specific ID/revision/length, and vendor-specific dwords. `PCIE_VC_*`, `PCIE_PORT_VC_*`, and `PCIE_VC0/VC1_RESOURCE_*` define virtual-channel count, arbitration capabilities, control/status, traffic-class to virtual-channel mapping, VC IDs, VC enable bits, negotiation status, and arbitration-table controls.

### AER, Error Logging, and Root-Port Error Reporting

`BIFPLR0_0_PCIE_DEV_SERIAL_NUM_*` exposes a 64-bit device serial number through two dwords. `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` starts the Advanced Error Reporting capability. The AER groups define uncorrectable error status, mask, and severity fields for data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked conditions.

Correctable error status and mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, internal correctable error, and header-log overflow. `PCIE_ADV_ERR_CAP_CNTL` includes first-error pointer, ECRC generation/check capabilities and enables, multi-header recording, and TLP prefix log presence. `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` expose captured AER packet context.

Root-port specific AER registers include `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID`. They enable reporting for correctable, nonfatal, and fatal errors; record received/multiple error state; mark first uncorrectable fatal state; report fatal/nonfatal message receipt; carry the advanced-error interrupt message number; and record source IDs. These fields are integration points for PCIe AER interrupt handling and diagnostic dumps.

### Secondary PCIe, Lane Equalization, ACS, Multicast, L1 PM, and DPC

`BIFPLR0_0_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` define the secondary PCIe extended capability. The per-lane equalization controls repeat the same downstream transmit preset, downstream receive preset hint, upstream transmit preset, and upstream receive preset hint fields for all 16 lanes. This regular structure is important for link-training code that must index lanes without shifting the wrong preset field.

`BIFPLR0_0_PCIE_ACS_*` mirrors the ACS capability/control pattern for the root port. `PCIE_MC_*` defines PCIe multicast capability, control, base addresses, receive masks, block-all masks, block-untranslated masks, and overlay BAR fields. These fields affect peer-to-peer isolation and multicast routing; incorrect programming can create security or routing faults.

`PCIE_L1_PM_SUB_*` maps L1 PM substates. It defines capability fields for PCI-PM L1.2, PCI-PM L1.1, ASPM L1.2, ASPM L1.1, L1 PM substate support, common-mode restore time, power-on scale/value, and control fields for L1.2/L1.1 enables, common-mode restore time, LTR L1.2 threshold, timing scale, and power-on value. These constants are tied to low-power link-state policy and resume latency.

`PCIE_DPC_*` defines Downstream Port Containment capability, control, status, and error source ID. It includes trigger capability/enable, routing support, RP extension support, poisoned TLP egress blocking support/enable, software trigger, interrupt enable/status, trigger reason/extension, RP busy state, first PIO error pointer, and source ID. DPC fields are safety-critical for isolating a failing downstream device after severe PCIe errors.

### RP PIO and ESM Diagnostics

`BIFPLR0_0_PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` define root-port PIO error classes for configuration, I/O, and memory completions: unsupported request, completer abort, and completion timeout. `PCIE_RP_PIO_HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` expose captured TLP context for those failures. These are diagnostic/status fields with write/clear semantics determined by hardware and PCIe capability rules, so callers should avoid treating masks and status fields interchangeably.

`BIFPLR0_0_PCIE_ESM_*` defines the start of an ESM extended capability. It includes capability list/header fields, minimum time-in-EI value/scale, ESM Gen3/Gen4 data rate controls, an enable bit, and capability bitmaps for many supported data rates. The covered capability registers enumerate rates from 8.0 GT/s through the later ESM capability dwords before the block transitions to `BIFPLR1_0`. These definitions are part of link-speed/equalization related capability discovery rather than ordinary runtime storage.

### BIFPLR1 Opening Bridge Block

The final third of the chunk introduces `addressBlock: nbio_pcie0_bifplr1_cfgdecp` and begins a second root-port/bridge instance. The early `BIFPLR1_0` definitions mirror `BIFPLR0_0`: standard PCI bridge identity/header fields, command/status, bridge bus numbering, I/O and memory aperture fields, interrupt line/pin, bridge control, port 80 control, PM capability/status, PCIe capability, device capability/control/status, and link capability/control/status.

The chunk ends inside `BIFPLR1_0_SLOT_CAP`, after attention button, power controller, MRL sensor, and attention indicator present fields. The remainder of `BIFPLR1_0_SLOT_CAP` and subsequent `BIFPLR1_0` registers are outside this chunk and must be reconciled by adjacent chunk reports.

## Control Flow

There is no runtime control flow in this header range. The only structure is the generated ordering of register comments followed by `#define` constants. Runtime control flow appears in external AMDGPU/NBIO/PCIe code that chooses when to read or write these registers. For example, link-management paths may read link status fields before deciding whether to retrain a link, AER/DPC handlers may read status/log fields after an interrupt, and power-management paths may update PM or L1 substate controls.

The implicit access pattern for writable fields is read-modify-write: read a register value, clear a field with its mask, shift a new value by the field's `__SHIFT`, mask it, and write the resulting register value. For status and log fields, consumers generally read, decode, and sometimes clear according to hardware-defined write-one-to-clear or capability-specific semantics that are not encoded in this header.

## State and Persistence Behavior

This chunk defines names for hardware state; it does not persist anything in memory or on disk. The underlying registers represent several kinds of state:

- PCI configuration identity and capability advertisement, which are usually hardware/firmware initialized and persistent across normal driver reads until reset.
- Writable PCIe controls such as command bits, bridge windows, PM state controls, error-reporting enables, link controls, slot controls, ACS controls, VC controls, L1 substate controls, and DPC controls.
- Volatile status bits such as link training/data-link active state, slot events, PME pending, device error flags, AER correctable/uncorrectable status, DPC trigger status, RP busy, and PIO error status.
- Diagnostic capture registers such as TLP header logs, TLP prefix logs, root-port PIO logs, and error source IDs, which preserve context from hardware error events until cleared or overwritten by hardware.

Reset, bus reset, D3 transitions, function-level reset, DPC containment, or firmware reinitialization can change the backing hardware state. The macros themselves are compile-time constants and have no lifecycle.

## Dependencies and Integration Points

This header depends on consumers including the correct NBIO 7.0 ASIC register headers. It is normally paired with an offset header that names register addresses and with AMDGPU register helper macros that know how to combine `__SHIFT`/`_MASK` constants. The `BIF_CFG_DEV1_EPF2_0`, `BIFPLR0_0`, and `BIFPLR1_0` prefixes are part of the generated naming scheme and must match the hardware IP block, instance, and PCIe function/root-port layout used by the driver.

Important integration areas include:

- PCI enumeration and bridge-resource setup for command/status, bus numbering, and I/O/memory/prefetchable aperture fields.
- PCIe link management for link capability/control/status, Link Control 2/3, equalization, lane error, and ESM data-rate fields.
- Power management for PMI status/control and L1 PM substate fields.
- Error handling for AER status/mask/severity, root error command/status/source ID, DPC status/control/source ID, and RP PIO logging.
- Hotplug/root-port support for slot capability/control/status and root PME fields.
- Isolation and routing policy for ACS, multicast, virtual channels, ARI, and BAR capability fields.
- Diagnostics and debug tooling that dumps TLP header/prefix logs, PIO logs, serial number fields, device/link status, and error masks.

## Risks

The main risk is bitfield drift from hardware documentation. A wrong shift or mask can silently corrupt read-modify-write operations, decode status incorrectly, or advertise unsupported capability state. The highest-risk groups are writable controls and error/security-related fields: bridge apertures, bus-master/memory-enable bits, AER masks/severity, DPC controls, ACS controls, multicast routing, link retrain/disable bits, L1 substate controls, and per-lane equalization fields.

Generated-name similarity is another risk. Many fields repeat across `BIF_CFG_DEV1_EPF2_0`, `BIFPLR0_0`, and `BIFPLR1_0`; using a macro from the wrong prefix may compile but target the wrong register layout or port instance. The `*_MASK_MASK` naming pattern in error mask registers is intentional: the register is named `*_MASK` and the field is also named `*_MASK`. Automated scripts and human reviewers should avoid "simplifying" those names.

Whole-register log fields use `0xFFFFFFFFL` masks and shift zero. They should be handled as raw captured dwords, not as scalar values with further implied interpretation in this header. Conversely, multi-bit fields such as bridge apertures, link width/speed, equalization presets, and power budget scales require both mask and shift; testing only single-bit flags would miss off-by-one or width errors.

Status, mask, severity, and control registers often share nearly identical field names. AER and RP PIO code must not confuse status bits with mask or severity bits, since a status read/clear path has different semantics from an enable/mask update path. Some status bits may be write-one-to-clear or hardware-cleared; this header does not encode those access rules.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Kernel/driver build coverage with this header included by AMDGPU NBIO/PCIe code, catching missing or renamed macros.
- Static checks that every field has a matching `__SHIFT` and `_MASK` pair, except where generated conventions intentionally omit one.
- Register-generation diffs against the authoritative NBIO 7.0 register database or vendor header source, especially for repeated `BIFPLR0_0`/`BIFPLR1_0` field families.
- PCIe enumeration tests on NBIO 7.0 hardware that verify bridge bus numbers, memory windows, BAR capabilities, link speed/width, MSI, PM capability, and slot/root-port capability decode correctly.
- AER/DPC fault-injection or error-observation tests that confirm uncorrectable/correctable status, masks, severity, root error status/source ID, TLP logs, DPC status, and RP PIO logs decode as expected.
- Link power-management tests covering ASPM/L1 substates and resume latency, plus link retrain/equalization tests that validate Link Control 2/3, lane error, and per-lane equalization macros.
- Security/isolation checks for ACS, ARI, multicast, and virtual-channel programming, particularly in peer-to-peer, IOMMU, and multi-function scenarios.
