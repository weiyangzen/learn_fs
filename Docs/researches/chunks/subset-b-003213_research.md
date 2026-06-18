# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 128754-131174

## Scope

This chunk covers a generated section of the AMD NBIO 7.2.0 shift/mask header. It starts at the last mask for `BIF_CFG_DEV1_RC1_DEVICE_CNTL`, then defines the remainder of the `BIF_CFG_DEV1_RC1` PCI/PCIe root-complex configuration capability space, and then begins the `addressBlock: nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp` section for `BIF_CFG_DEV2_RC1`. The range ends in the middle of `BIF_CFG_DEV2_RC1_PCIE_LANE_11_EQUALIZATION_CNTL`; that register's remaining mask definitions and later DEV2 lane/equalization/margining fields continue in the next chunk.

The chunk contains 2,151 preprocessor definitions across 268 register comment blocks. It is entirely declarative: there are no C functions, structs, storage objects, persistence code, or executable control flow. Each field is exposed through the normal generated AMD register pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

## Purpose

The purpose of this header section is to provide the bitfield ABI for NBIO PCIe configuration-space registers on ASICs using the `nbio_7_2_0` register map. The sibling `nbio_7_2_0_offset.h` file provides register addresses such as `regBIF_CFG_DEV*_RC1_*`; this file provides the bit offsets and masks needed to isolate, test, or compose fields in those registers.

In the local tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this header together with `nbio_7_2_0_offset.h`. Runtime code uses the generated values through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. This specific chunk mostly documents PCIe config-capability fields; many of the constants are consumed indirectly by generic register access/debug paths or future hardware enablement rather than by explicit direct references in `nbio_v7_2.c`.

## Major Register Families

### `BIF_CFG_DEV1_RC1` PCIe Capability Space

The DEV1 portion begins after the `DEVICE_CNTL` field list and covers PCIe device, link, slot, and root-port status/control registers:

- `DEVICE_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` expose error bits, pending transaction state, completion-timeout capabilities/control, atomic operation support/enables, ID ordering, LTR, OBFF, E2E TLP prefix, emergency power reduction, function-level reset, and 10-bit tag requester/completer controls.
- `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` define speed, width, ASPM/PM, retrain, common clock, DL active, bandwidth notifications, target link speed, equalization, compliance, de-emphasis, autonomous speed disable, transmit margin, modified TS usage, and crosslink fields.
- `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, plus the sparse `*_2` registers define hotplug, power-controller, presence-detect, attention/power indicator, MRL, command-complete, data-link-state-change, and physical-slot-number fields.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` define root-port SERR/PME behavior, CRS software visibility, PME requestor ID, PME status, and PME pending state.

These fields mirror standard PCI Express capability layout, so the risk is less algorithmic and more ABI-oriented: a wrong shift or mask can cause the driver to report the wrong PCIe link state, clear the wrong status bit, or enable an unintended root-port control.

### MSI and Identity Capabilities

The chunk includes DEV1 and DEV2 MSI capability fields:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` define capability IDs, next pointers, MSI enable, multi-message capability/enable, 64-bit address support, per-vector masking, function mask, and MSI-X enable.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MSG_DATA_64`, and `MSI_EXT_MSG_DATA_64` expose message address/data payload fields.
- `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP` define subsystem identity and MSI mapping capability metadata.

These definitions are integration points for interrupt setup and config-space introspection. They do not allocate interrupt state themselves; they let caller code read or compose register values consistently.

### Vendor-Specific, VC, and Serial-Number Capabilities

The DEV1 and DEV2 sections define enhanced capability-list headers and fields for:

- Vendor-specific capability headers and vendor payload registers.
- Virtual channel capability/control/status for port VC plus VC0/VC1 resource capability/control/status.
- Device serial number enhanced capability list and two serial-number DWORDs.

Virtual channel fields include extended VC count, low-priority VC count, reference clock, arbitration table offset/size, arbitration select, TC-to-VC maps, load-table strobes, and negotiation-pending status. These fields matter for PCIe traffic-class routing and QoS-style behavior if supported by the hardware and firmware policy.

### Advanced Error Reporting

Both DEV1 and DEV2 include PCIe Advanced Error Reporting definitions:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` gives capability ID/version/next-pointer metadata.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, poison-TLP egress blocked, and deferred-error fields.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, corrected internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC check capability/enable, multi-header record capability/enable, TLP prefix log presence, and completion-timeout logging capability.
- `PCIE_HDR_LOG0..3`, `PCIE_TLP_PREFIX_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID` support root-port AER reporting, captured TLP headers/prefixes, interrupt message number, and source IDs.

These fields are status-heavy and often include write-one-to-clear or hardware-updated semantics at the register level. The header does not encode those semantics, so callers must rely on PCIe/AER rules and ASIC programming guides when writing them.

### Equalization, 16 GT/s, ACS, DLF, and Margining

The DEV1 section includes per-lane and high-speed PCIe support:

- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` define 8 GT/s equalization request/interrupt bits, lane error status, downstream/upstream Tx presets, and Rx preset hints.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services support/control bits: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` expose data-link feature exchange and local/remote feature support.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, parity mismatch status registers, and `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` define 16 GT/s supported rate, equalization control/status, local/remote parity mismatch, and per-lane 16 GT/s coefficient/preset fields.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_CNTL/STATUS` through `LANE_15_MARGINING_LANE_CNTL/STATUS` define PCIe lane margining receiver selection, margin type, usage model, payload, ready/software-ready/status bits, and independent left/right voltage/timing margin support.

The DEV2 portion repeats the 8 GT/s equalization definitions through lane 11 in this chunk. The lane-11 register is incomplete at the chunk boundary, so reconciled per-file research should pair this chunk with the following chunk before making whole-register claims for DEV2 lane 11 and beyond.

### `BIF_CFG_DEV2_RC1` PCI Header and Bridge Configuration

After line 130075, the chunk starts the DEV2 root-complex address block. It covers conventional PCI/PCI-to-PCI bridge configuration fields before repeating the PCIe capability families described above:

- Identity/class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, and `BIST`.
- Command/status fields: `COMMAND` and `STATUS` define I/O, memory, bus-master, parity/SERR, VGA palette snooping, interrupt disable, capability list, transaction abort, signaled error, parity detected, and devsel timing fields.
- Resource/window fields: `BASE_ADDR_1`, `BASE_ADDR_2`, `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, `IO_BASE_LIMIT_HI`, and `ROM_BASE_ADDR`.
- Interrupt and bridge controls: `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL`.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define PM capability metadata, PME support, current power state, no-soft-reset, PME enable/status, bridge PM extension, B2/B3 support, and PMI data/scale/select fields.

These definitions make DEV2 visible to code that enumerates or manages secondary NBIO root-complex instances. They are not persisted in software; the authoritative state lives in hardware registers and may reset with the device, function, or link depending on platform power/reset sequencing.

## Control Flow and State Behavior

There is no local control flow in this chunk. Runtime flow is supplied by consumers:

1. Caller obtains a register address from `nbio_7_2_0_offset.h` or through `SOC15_REG_OFFSET`.
2. Caller reads the register with an AMDGPU MMIO/PCIE helper.
3. Caller extracts a field with a `*_MASK` and `*_SHIFT`, normally via `REG_GET_FIELD`, or composes a write value with `REG_SET_FIELD`.
4. Caller writes the new register value back only when the field is writable and hardware sequencing allows it.

The state described by these macros is hardware-owned. Some fields are static capability bits, some are driver-programmable controls, and many are live status or sticky error bits. Persistence is therefore hardware-defined: capability fields usually reflect ASIC straps/fuses/configuration, control fields persist until reset or overwritten, and error/status fields can be updated or cleared by PCIe hardware events.

## Dependencies and Integration Points

- Depends on the C preprocessor and AMD's generated register naming convention; no standalone build artifact is produced by this header section.
- Paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies the corresponding register addresses.
- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which provides NBIO 7.2 callbacks for memory controller access, doorbell aperture setup, interrupt handling, clock/power gating, PCIE index/data register selection, and max-read-request-size programming.
- Indirectly supports PCIe/AER/MSI/hotplug/link-training/debug tooling by making standard and AMD-specific PCIe configuration fields available to driver code.
- Sibling generated headers such as `nbio_7_2_0_default.h` provide reset/default values for the same register families on related NBIO maps; those defaults should be kept consistent with shift/mask names if regenerated.

## Risks

- Generated-header drift is the main risk. If a mask or shift does not match the ASIC register specification, all callers using `REG_SET_FIELD`/`REG_GET_FIELD` can silently read or write the wrong bits.
- PCIe status and AER registers include sticky and clear-on-write behavior that is not represented by these macros. Treating every masked field as ordinary read/write state can clear diagnostics or lose error provenance.
- Link equalization, 16 GT/s, and lane margining fields are timing-sensitive hardware controls. Incorrect writes can destabilize link training or make diagnostics misleading.
- MSI/MSI-X and root error command fields affect interrupt delivery. Wrong enable bits or message-number extraction can break interrupt routing or error reporting.
- The chunk boundary splits `BIF_CFG_DEV2_RC1_PCIE_LANE_11_EQUALIZATION_CNTL`; automated analysis must not assume the register is fully covered by this chunk alone.
- Macro names are very long and highly repetitive across DEV1/DEV2 and lane numbers, so copy/paste mistakes are hard to spot by review unless generated-output diffing or register-spec comparison is used.

## Test Signals

- Build signal: compile the AMDGPU driver code that includes `nbio_7_2_0_sh_mask.h`; preprocessor or naming drift will usually surface as undefined macro or duplicate-definition failures.
- Static signal: compare this generated header against the matching AMD register database/spec and `nbio_7_2_0_offset.h` to confirm every register has matching address and field definitions.
- Runtime smoke signal: boot hardware using NBIO 7.2.x paths and confirm `nbio_v7_2.c` initialization can read revision ID, memory size, configure doorbells/interrupts, and access PCIE index/data ports without MMIO faults.
- PCIe signal: verify link speed/width/status reporting, AER counters/logs, MSI delivery, and root-port error reporting on supported hardware.
- High-speed link diagnostic signal: exercise equalization and lane margining debug paths where available, checking that per-lane fields map to the expected physical lane and do not corrupt adjacent lane controls.
