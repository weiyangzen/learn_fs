# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 27411-29891

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.9.0 register bitfield header. The range starts at `PCIE0PortBExtNonFatal_ACTION_CONTROL` and ends at `BIF_CFG_DEV0_RC_PCIE_LANE_14_EQUALIZATION_CNTL`, with the lane 14 mask definitions continuing in the next chunk.

The chunk contains 2,142 `#define` entries across 276 register names. It is declarative hardware ABI data only: there are no C functions, structs, variables, allocations, branches, loops, locking operations, or direct register accesses in this section.

The covered register groups are:

- PCIe0 port B through G and NBIF1 port A RAS/AER action-control fields.
- Sync flood, NMI, poison, egress poison, APML status/control/trigger fields.
- NB device-indirect steering controls for PCIE0, NBIF1, and internal sideband windows.
- NB root-complex bridge indirect SMN index/data windows for PCIE0 and NBIF1.
- IOMMU L2A and L2B/indexed L2 control, cache, page-table cache, command processor, performance, power, parity, and error-rule fields.
- IOAPIC feature-enable fields.
- NBIF0 root-complex bridge PCI configuration-space fields for device 0, including PCI header, PM, PCIe, MSI, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, and lane equalization registers.

## Purpose

The purpose of this header section is to give NBIO 7.9.0 driver code named bit positions for hardware registers. Each register field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

Consumers use these definitions with the matching `nbio_7_9_0_offset.h` address macros and AMDGPU helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_SOC15_EXT`. The offset header tells the driver where a register is; this mask header tells it how to interpret or construct the 32-bit value at that address.

## Important Macro Families

### PCIe Port RAS Action Controls

The first region defines repeated `*_ACTION_CONTROL` layouts for PCIe0 ports B through G and NBIF1 port A. Each port/error-class register uses the same four logical fields:

- `APML_ERR_En` at bit 0.
- `IntrGenSel` at bits 2:1.
- `LinkDis_En` at bit 3.
- `SyncFlood_En` at bit 4.

The names distinguish SERR, internal fatal/nonfatal/correctable errors, external fatal/nonfatal/correctable errors, and parity errors. These fields define the action policy for fabric or PCIe error events: whether to signal APML, choose an interrupt generation mode, disable the link, or trigger sync flood. Because the layout repeats across many ports and severities, copy-generation correctness matters; using the wrong register name would route a policy to a different port or error class even though the bit layout is identical.

### Sync Flood, NMI, Poison, and APML

`SYNCFLOOD_STATUS` records sync-flood origins from RAS control, APML, pin, private, and MCA sources. `NMI_STATUS` exposes the pin-origin NMI bit. `APML_STATUS`, `APML_CONTROL`, and `APML_TRIGGER` expose APML-visible corrected, nonfatal, fatal, SERR, internal poison, and egress poison status bits plus NMI/sync-flood/output controls and a software NMI trigger bit.

The poison region covers both internal and egress poison handling:

- `POISON_ACTION_CONTROL` contains three action-policy groups: internal poison, egress poison low status, and egress poison high status. Each group has APML error enable, interrupt generation selection, link-disable enable, and sync-flood enable fields.
- `INTERNAL_POISON_STATUS` has eight one-bit internal poison status lanes, and `INTERNAL_POISON_MASK` masks those eight lanes.
- `EGRESS_POISON_STATUS_LO` and `EGRESS_POISON_STATUS_HI` each expose 32 individual status bits, giving 64 egress poison status bits across the low/high registers.
- `EGRESS_POISON_MASK_LO`, `EGRESS_POISON_MASK_HI`, `EGRESS_POISON_SEVERITY_DOWN`, and `EGRESS_POISON_SEVERITY_UPPER` are full-width 32-bit masks or severity maps.

This region is the direct NBIO hardware vocabulary for poison propagation, error escalation, and platform management signaling. The header does not encode clear-on-read or write-one-to-clear behavior; consumers must follow the register specification and owning RAS path when reading, clearing, masking, or escalating these events.

### Device-Indirect Steering and RC Bridge Indirect Windows

The `NB_PCIE0DEVINDCFG{0..6}_STEERING_CNTL`, `NB_NBIF1DEVINDCFG0_STEERING_CNTL`, and `NB_INTSBDEVINDCFG0_STEERING_CNTL` registers all expose:

- `ForceSteering` at bit 0.
- `SteeringValue` at bits 15:8.

These fields steer device-indirect configuration accesses for multiple PCIE0 instances, NBIF1, and the internal sideband path. Incorrect steering can send indirect config traffic to the wrong target instance.

The root-complex bridge indirect windows are grouped under address blocks for `PCIE0rcbdg_indcfg0` through `PCIE0rcbdg_indcfg6` and `NBIF1rcbdg_indcfg0`. Each window has:

- `RC_SMN_INDEX_EXTENSION`, an 8-bit index extension.
- `RC_SMN_INDEX`, a full 32-bit index.
- `RC_SMN_DATA`, a full 32-bit data register.

Together these fields define indexed SMN access paths through root-complex bridge configuration windows. Their integration depends on the matching offset macros such as `regNB_PCIE0RCBDG_INDCFG0_RC_SMN_INDEX_EXTENSION`, not on this mask header alone.

### IOMMU L2A and L2B Controls

The IOMMU region starts with `aid_nbio_iohub_iommu_l2a_l2acfg` and continues through `aid_nbio_iohub_iommu_l2indx_l2indxcfg`. It defines performance counters, cache controls, page-table cache controls, power controls, error-rule controls, and command/page-request controls for the NBIO IOMMU L2 block.

L2A-visible fields include:

- `L2_PERF_CNTL_0/1` and `L2_PERF_COUNT_0..3` for four performance-event selectors, upper count fields, and 32-bit count values.
- `L2_STATUS_0` as a full-width status register.
- `L2_CONTROL_0/1` for L1 cache response allowances, untranslated/address-translation exception side PTE behavior, large-page caching, input FIFO burst length, client priority, sequential invalidation burst limits, DBUS disable, and performance threshold.
- `L2_DTC_CONTROL`, `L2_ITC_CONTROL`, and `L2_PTC_A_CONTROL` for data/instruction/page-table cache behavior: parity enable/support, invalidation selection, soft invalidate, bypass, LRU priority, way count, entry count, and page-table-cache-specific separate storage, 2 MiB mode, overlapping-page invalidation, and guest fast invalidation.
- Hash and way-control registers for DTC, ITC, and PTCA, with address masks plus way disable and way access disable bitmaps.
- `L2A_UPDATE_FILTER_CNTL`, `L2_ERR_RULE_CONTROL_3..5`, `L2_L2A_CK_GATE_CONTROL`, `L2_L2A_PGSIZE_CONTROL`, `L2_PWRGATE_CNTRL_REG_0/3`, and `L2_ECO_CNTRL_0`.

The indexed/L2B region includes:

- `L2_STATUS_1` and `L2_SB_LOCATION` for status and sideband port/core location.
- `L2_CONTROL_5/6`, `L2_PDC_CONTROL`, `L2_PDC_HASH_CONTROL`, and `L2_PDC_WAY_CONTROL` for queue arbitration, flow-control disables, DTC update policy, partial page-table-cache control, page-directory cache parity/invalidation/bypass/way sizing, and related cache address masks.
- `L2_TW_CONTROL`, `L2_TW_CONTROL_1..3` for table-walker coherence, prefetch, filtering, error continuation, access-bit/AP-bit behavior, nested PTE caching, trace enable/no-wrap/force-disable/mask, and trace address low/high fields.
- `L2_CP_CONTROL`, `L2_CP_CONTROL_1..3` for command processor prefetch, flushing, request pass-through, outstanding-command limiting, read delay, L1-off controls, invalidation mode fields, wait-completion behavior, and scheduler/interlock timing fields.
- `L2_CREDIT_CONTROL_0/1`, `L2_ERR_RULE_CONTROL_0..2`, `L2_L2B_CK_GATE_CONTROL`, `PPR_CONTROL`, `L2_L2B_PGSIZE_CONTROL`, `L2_PERF_CNTL_2/3`, `L2_PERF_COUNT_4..7`, `L2B_SDP_PARITY_ERROR_EN`, and `L2_ECO_CNTRL_1`.

These fields are sensitive because they affect address translation caching, invalidation progress, page-request handling, parity/error behavior, performance counters, and clock/power gating. The header provides bit positions; the actual sequencing and ordering rules belong to the IOMMU/NBIO driver logic and hardware specification.

### IOAPIC Feature Enable

`FEATURES_ENABLE` under `aid_nbio_iohub_nb_ioapiccfg_ioapic_cfgdec` exposes feature toggles such as `FEATURE_ENABLED`, `LEGACY_REDIR`, `IOAPIC_ID`, and interrupt remapping selection bits. These fields are part of NBIO's IOAPIC configuration decode and interact with platform interrupt routing rather than GPU command submission.

### NBIF0 Root-Complex PCI Configuration Header

The `aid_nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` address block begins a root-complex bridge PCI configuration-space image for NBIF0 device 0.

The base PCI bridge header fields include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `BIF_CFG_DEV0_RC_COMMAND` bits for I/O space, memory space, bus master, parity/error response, SERR, fast back-to-back, interrupt disable, and reserved bits.
- `BIF_CFG_DEV0_RC_STATUS` bits for interrupt status, capability-list presence, 66 MHz capable, fast back-to-back capable, parity/abort/system-error status, DEVSEL timing, and detected parity.
- Cache-line, latency, header, BIST, base-address, bus-number/latency, I/O base/limit, memory base/limit, prefetchable memory base/limit, upper prefetchable address, high I/O base/limit, capability pointer, ROM base, interrupt line/pin, bridge control, and extended bridge control fields.

This section mirrors standard PCI-to-PCI bridge configuration concepts. A wrong mask here can affect enumeration-visible bridge resources, bus numbering, legacy VGA/ISA behavior, SERR propagation, or memory/I/O aperture decoding.

### Power Management, PCIe Capability, Slot, and Link Controls

The PM capability fields cover `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including version, PME support, D-state support, auxiliary current, power state, PME enable/status, data select/scale, bus power enable, and PM data fields.

The PCIe capability fields include:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device type, slot implemented, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for payload sizes, phantom functions, extended tags, relaxed ordering, no-snoop, error-report enables/status, role-based error reporting, captured slot power, FLR capability, auxiliary power, transactions pending, and emergency power reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed, link width, ASPM/PM control, link disable/retrain, common clock, extended sync, clock power management, bandwidth interrupts, DRS signaling, link training, slot clock config, and data-link active status.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` for hotplug, power controller, MRL sensor, attention/power indicators, slot power limit, physical slot number, command-completed interrupt, presence detection, electromechanical interlock, and data-link state change.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` for PME interrupt routing and root-port PME status/requester information.

The PCIe 2/secondary capability fields add completion timeout, ARI, atomic operation, IDO, LTR, OBFF, TLP prefix, emergency power reduction, FRS, target link speed, compliance/deemphasis controls, 8 GT/s equalization phase status, RTM presence, crosslink status, and DRS message receipt.

### MSI, Vendor-Specific, Virtual Channel, Serial Number, and AER

The MSI capability group defines capability-list fields, MSI enable, multi-message capability/enable, 64-bit addressing, per-vector masking capability, extended message-data capability/enable, MSI address low/high, data, extended data, and 64-bit message-data aliases.

The subsystem and vendor-specific capability fields include subsystem vendor/device IDs, vendor-specific enhanced capability headers, VSEC ID/revision/length, and two full-width vendor-specific data registers.

The virtual-channel group exposes VC enhanced capability headers, port VC capabilities, VC arbitration capability/table offsets, port arbitration capability, VC arbitration selection, load-table control/status, and VC0/VC1 resource capability/control/status fields. These fields can affect transaction-class to VC mapping and load-table state.

The device serial number registers expose two full 32-bit serial-number words. The AER region includes:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable, multicast blocked TLP, atomic-op egress blocked, TLP-prefix blocked, and poisoned-TLP egress-blocked events.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, header logs `HDR_LOG0..3`, root error command/status, error source IDs, and TLP prefix logs `TLP_PREFIX_LOG0..3`.

This AER region is one of the highest-risk parts of the chunk. It controls error visibility and severity classification for PCIe root-port errors, and also records diagnostic payload such as TLP headers, prefix logs, and source IDs.

### Secondary PCIe and Lane Equalization

The final region starts the secondary PCIe extended capability and lane equalization definitions:

- `PCIE_SECONDARY_ENH_CAP_LIST` defines the enhanced capability header.
- `PCIE_LINK_CNTL3` exposes perform equalization, link equalization request interrupt enable, and lower SKP ordered-set generation controls.
- `PCIE_LANE_ERROR_STATUS` exposes a 16-bit lane error bitmap.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_14_EQUALIZATION_CNTL` define per-lane downstream port 8 GT/s transmit preset, downstream receive preset hint, upstream transmit preset, and upstream receive preset hint fields.

Lane 14 starts in this chunk and its mask definitions continue in the next chunk. The merge lane should connect this report with the following chunk for the remaining lane 14 fields and later lane/register definitions.

## Control Flow and State Behavior

This chunk has no executable control flow. Its macros influence runtime behavior only after included C code expands them into bit manipulations and register I/O operations.

The state represented here is hardware state in NBIO, IOMMU L2, IOAPIC configuration, and PCIe root-complex configuration registers. Some fields are persistent configuration until reset or reprogramming, such as error-action policy bits, poison masks/severity maps, indirect steering values, IOMMU cache and clock-gating controls, PCI command/bridge aperture fields, PM controls, MSI programming, virtual-channel resource controls, AER masks/severities, and link-control settings. Other fields are status or command-like bits, such as sync-flood status, NMI status, poison status, APML status, IOMMU performance counters/status, PCIe device/link/slot/root/AER status, header/TLP logs, error source IDs, lane error status, retrain/equalization trigger bits, and soft-invalidate controls.

The header cannot describe side effects such as sticky status clearing, write-one-to-clear behavior, polling requirements, ordering requirements around invalidations, or reset-domain persistence. Those rules are supplied by the hardware specification and by driver code that uses the macros.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention and on the matching NBIO 7.9.0 register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies `reg*` addresses and base indices.
- Neighboring generated headers for NBIO defaults and IV source IDs supply reset values and interrupt source identifiers.
- AMDGPU register helper macros compose and extract fields using the `__SHIFT` and `_MASK` definitions from this file.

Direct include users observed in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c`, which includes this mask header with the 7.9.0 offset header and uses the standard SOC15 register access pattern for NBIO initialization, revision discovery, memory-controller access, doorbell aperture/range programming, and related NBIO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes the same generated headers while registering NBIO RAS interrupt sources. In the current file, the RAS handlers are dummy/no-op for the disabled BIF-ring path and do not directly reference the specific bitfield names in this chunk.

Likely integration areas for this chunk's fields include NBIO RAS policy setup, APML/NMI/sync-flood signaling, poison event handling, indirect register access routing, IOMMU cache and invalidation tuning, page-request/PPR interrupt coalescing, PCI bridge enumeration and resource windows, PCIe link training and status diagnostics, MSI programming, virtual-channel configuration, and PCIe AER reporting.

The macros are ASIC-generation-specific. Similar register names appear in other NBIO 7.x headers, but field presence and reserved-bit definitions can differ. Code must include matching 7.9.0 offset/mask/default headers rather than mixing definitions from neighboring ASIC versions.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write reserved bits, mask the wrong hardware status, set the wrong PCIe capability/control bit, or misdecode link/error state.
- Repeated action-control layouts make copy mistakes hard to spot. The same four fields are repeated for many ports and error severities; the register name, not just the mask value, determines which error path is affected.
- Poison, APML, NMI, and sync-flood bits are escalation paths. Incorrect masks can suppress critical hardware events, over-escalate recoverable events, disable links unexpectedly, or produce platform management signals at the wrong time.
- IOMMU L2 cache, invalidation, and table-walker controls affect address translation correctness. Misprogramming soft invalidation, bypass, parity, cache way, page size, credit, command processor, or table-walker fields can cause stale translations, hangs, performance loss, or false parity/error reporting.
- Clock and power gating fields can create timing-sensitive failures if changed outside the expected power-management sequence.
- PCI bridge header masks affect enumeration-visible state such as BARs, bus numbers, memory/I/O windows, ROM enable, interrupt routing, and bridge control. Wrong masks can break PCI resource assignment or legacy decode behavior.
- PCIe AER mask/severity/status fields are diagnostic and reliability-sensitive. Incorrect values can hide real errors, flood interrupts, misclassify fatal versus nonfatal errors, or corrupt captured header/TLP logs.
- Lane equalization fields are per-lane and repetitive. Lane-number or suffix mistakes can tune the wrong lane or misreport equalization state, especially at the chunk boundary where lane 14 continues into the next chunk.

## Test Signals

Useful validation signals for this generated header section include:

- Compile coverage for `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c`, proving the 7.9.0 offset and mask headers remain syntactically compatible with AMDGPU register helper macros.
- Static checks that every `__SHIFT` macro in this chunk has a matching `_MASK` macro for the same register/field, except where the chunk intentionally starts or ends mid-register.
- Generated-header comparison against the authoritative NBIO 7.9.0 register database for action-control, poison/APML, IOMMU L2, PCIe root bridge, AER, and lane equalization fields.
- Runtime smoke on NBIO 7.9.0 hardware or emulation that reads stable PCI configuration fields such as vendor/device/class IDs, link status, PM/PCIe capability IDs, MSI capability bits, and AER capability headers.
- RAS/error-injection or platform diagnostics that confirm poison status, APML status, sync-flood status, AER status/mask/severity, and root error status bits are decoded and cleared according to hardware expectations.
- IOMMU stress covering ATS/translation workloads, invalidation, page requests, and performance counters after any change to L2 cache, table-walker, command processor, or page-size masks.

## Cross-Chunk Notes

The source file is an oversized generated register header, so this document describes only lines 27411-29891. Adjacent chunks are needed for the whole-file report. This chunk begins after prior PCIe0 port B definitions and ends in the middle of the lane 14 equalization control register; the following chunk should contain the remaining `BIF_CFG_DEV0_RC_PCIE_LANE_14_EQUALIZATION_CNTL` masks and subsequent NBIO 7.9.0 register fields.
