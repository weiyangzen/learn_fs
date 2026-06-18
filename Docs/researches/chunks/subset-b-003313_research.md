# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 130390-132799

## Scope

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask register header. It contains 2,172 preprocessor definitions covering 236 register names. The range begins in the tail of the `nbio_pcie1_bifplr4_cfgdecp` root-port configuration decode block and then covers most of `nbio_pcie1_bifplr5_cfgdecp`.

The source is not executable C logic. Its interface is a generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.

The chunk starts after the first fields of `BIFPLR4_3_SECONDARY_STATUS`; it then owns the remaining `BIFPLR4_3` bridge aperture, hotplug, slot, and SSID definitions. It introduces `// addressBlock: nbio_pcie1_bifplr5_cfgdecp` and covers `BIFPLR5_1_VENDOR_ID` through the first four fields of `BIFPLR5_1_LANE_12_MARGINING_LANE_CNTL`. Lane 12 margining status and lanes 13-15 continue after this chunk.

## Purpose

`nbio_7_7_0_sh_mask.h` describes bitfield geometry for NBIO 7.7 hardware registers. This slice focuses on PCIe root-port configuration decode registers: the end of port instance `BIFPLR4_3` and nearly all of port instance `BIFPLR5_1`. Driver code includes this header with `nbio_7_7_0_offset.h` so it can read, decode, set, or preserve hardware register fields without embedding raw bit positions.

The `BIFPLR5_1` block mirrors PCI/PCIe configuration and extended-capability layout for a PCIe bridge/root-port-like function. It includes conventional PCI identity and bridge registers, power-management capability fields, PCIe device/link/slot/root control and status, MSI, subsystem ID, vendor-specific capability headers, virtual-channel resources, device serial number, AER, secondary PCIe link capability, ACS, multicast, L1 PM substates, DPC, root-port PIO error reporting, ESM, data link feature, 16 GT/s physical-layer capability, and PCIe lane margining definitions.

Although the repository path is under a Ceph client source mirror, these definitions are GPU driver hardware metadata. They do not participate in Ceph filesystem control flow or distributed-storage persistence.

## Important APIs, Types, And Macro Groups

There are no functions, structs, typedefs, enums, variables, or inline helpers in this range. The important API is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

Important groups in this chunk:

- `BIFPLR4_3_*` tail: bridge memory and prefetchable-memory base/limit registers, upper 32-bit prefetchable base/limit registers, high I/O base/limit, slot capability/control/status, slot capability/control/status 2 reserved placeholders, and subsystem ID capability list/data fields.
- `BIFPLR5_1_VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, class-code, cache-line, latency, header, and BIST fields: conventional PCI identity and header metadata.
- `BIFPLR5_1_COMMAND` and `STATUS`: I/O enable, memory enable, bus master enable, SERR, interrupt disable, capability list, parity and abort status, devsel timing, and related PCI status/control bits.
- `BIFPLR5_1_SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`: bridge bus numbering and downstream aperture decode fields.
- `BIFPLR5_1_CAP_PTR`, `ROM_BASE_ADDR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `EXT_BRIDGE_CNTL`, `VENDOR_CAP_LIST`, and `ADAPTER_ID_W`: capability-chain, legacy ROM/interrupt, bridge-control, and vendor identity fields.
- `BIFPLR5_1_PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`: PCI power-management capability ID, next pointer, PME support, D-state selection, PME enable/status, data select/scale, and bus-power/clock-related bits.
- `BIFPLR5_1_PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`: core PCIe capability fields for device/link/slot/root behavior.
- `BIFPLR5_1_DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`: second-generation PCIe capability extension fields such as completion timeout, atomic ops, LTR, OBFF, target link speed, equalization controls, lane equalization status, and reserved placeholders.
- `BIFPLR5_1_MSI_*`, `SSID_*`, and `MSI_MAP_*`: MSI capability, message address/data fields, subsystem ID, and AMD MSI mapping capability fields.
- `BIFPLR5_1_PCIE_VENDOR_SPECIFIC*`: PCIe vendor-specific enhanced capability header and two vendor-specific data registers.
- `BIFPLR5_1_PCIE_VC_*`: virtual-channel enhanced capability list, port VC capability/control/status, and VC0/VC1 resource capability/control/status definitions.
- `BIFPLR5_1_PCIE_DEV_SERIAL_NUM_*`: enhanced capability header plus two dwords of device serial number.
- `BIFPLR5_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG0..3`: AER capability, status/mask/severity, logs, and root error command/status/source fields.
- `BIFPLR5_1_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`: secondary PCIe capability and per-lane equalization controls.
- `BIFPLR5_1_PCIE_ACS_*`: access-control service capability and control fields for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, and enhanced direct translated P2P behavior.
- `BIFPLR5_1_PCIE_MC_*`: multicast enhanced capability, control, base address, receive, block-all, block-untranslated, and overlay BAR fields.
- `BIFPLR5_1_PCIE_L1_PM_SUB_*`: L1 PM substate capability/control fields, including L1.1/L1.2 support, common-mode restore time, power-on scale/value, enable bits, ASPM/PCI-PM L1.2 enables, and timing values.
- `BIFPLR5_1_PCIE_DPC_*`: downstream port containment capability, control, status, and error source ID fields.
- `BIFPLR5_1_PCIE_RP_PIO_*`: root-port PIO status, mask, severity, sys-error, exception, header log, and prefix log fields.
- `BIFPLR5_1_PCIE_ESM_*`: ESM enhanced capability metadata, status/control, and a dense set of link-speed capability bits from 8.0 GT/s style naming through 28.0 GT/s in `PCIE_ESM_CAP_1..7`.
- `BIFPLR5_1_DATA_LINK_FEATURE_*`: data link feature capability/status fields such as scaled flow control and data-link-exchange support/status.
- `BIFPLR5_1_PCIE_PHY_16GT_*`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, parity mismatch status, and `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`: PCIe 16 GT/s PHY/equalization field layout.
- `BIFPLR5_1_PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_CNTL/STATUS` through the start of `LANE_12_MARGINING_LANE_CNTL`: PCIe lane margining port/lane control and status fields.

## Control Flow

There is no local control flow in this header. Runtime sequencing lives in code that includes the generated register map.

For NBIO 7.7, `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`. That implementation uses the generated `reg*` offsets and `*_MASK`/`__SHIFT` constants through AMDGPU register accessors to manage NBIO revision ID extraction, memory-controller access, SDMA/VCN/IH doorbell ranges, doorbell apertures, interrupt control, HDP flush offsets, PCIe index/data offsets, register remapping, and NBIO clock-gating/light-sleep state.

The typical external flow is:

1. Select a register offset from `nbio_7_7_0_offset.h`, such as a `regBIFPLR5_1_*` register or another NBIO register.
2. Read a 32-bit value through the appropriate AMDGPU accessor.
3. Use `REG_GET_FIELD`, `REG_SET_FIELD`, or direct mask/shift arithmetic with the macros in this header.
4. Write back only when the hardware field is writable and the access path is correct for that register.

The `BIFPLR5_1` fields in this chunk are mostly PCIe configuration/capability definitions. They are likely to be decoded by diagnostics, firmware/driver bring-up flows, or PCIe register access paths rather than touched by the common NBIO helper on every boot. However, their writable classes are operationally important: command bits, bridge apertures, PM control, device/link/slot/root control, MSI state, VC controls, AER masks/severity/commands, ACS controls, multicast controls, L1 PM substate controls, DPC controls, RP PIO masks/severity/sys-error/exception controls, ESM control, data-link feature controls, 16 GT/s link/equalization controls, and lane margining controls.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes bit positions for state stored in NBIO/PCIe hardware registers and PCIe configuration-space shadows.

State represented by this range includes:

- Static or firmware-initialized identity and capability-chain data: vendor/device IDs, revision/class fields, capability IDs, capability next pointers, PCIe capability versions, serial number dwords, and subsystem IDs.
- PCI bridge decode state: primary/secondary/subordinate bus numbers, I/O and memory aperture base/limit fields, prefetchable upper-base/upper-limit dwords, bridge control, and ROM base enable/address fields.
- Link, slot, and root-port state: link speed/width capability and status, link retrain/disable/common-clock/extended-synch controls, slot power/hotplug indicators, presence and command-completed status, root PME controls/status, and downstream link state indicators.
- Interrupt state: legacy interrupt line/pin, interrupt disable, MSI enable/multiple-message/address/data fields, and MSI mapping capability.
- Power-management state: PM capability advertisement, current power state, PME enable/status, data select/scale, L1 PM substate enable/timing controls, and 16 GT/s link control/status.
- Error and diagnostic state: conventional PCI status bits, secondary status bits, AER status/masks/severity/logs, DPC trigger/reason/interruption status, root-port PIO status/masks/severity/sys-error/exception/logs, lane error status, parity mismatch status, and margining per-lane status.
- Routing/isolation/resource policy: VC resource controls, ACS controls, multicast address/receive/block/overlay settings, and ESM/link-speed capability/control fields.

Persistence across warm reset, hot reset, FLR-like operations, GPU reset, suspend/resume, runtime power management, or PCIe link retraining is not specified by this header. Those semantics depend on PCIe config-space rules, NBIO reset domains, platform firmware, and AMDGPU restore paths. Generated masks must therefore be treated as field geometry only, not as reset policy or access-type documentation.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h` supplies the matching `regBIFPLR5_1_*` and other NBIO register offsets. For example, the offset header maps `regBIFPLR5_1_VENDOR_ID`, `regBIFPLR5_1_COMMAND`, bridge aperture registers, capability registers, and later enhanced-capability registers to base-indexed NBIO addresses.

Notable absence:

- This tree has `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`; it does not show same-named `nbio_7_7_0_default.h` or `nbio_7_7_0_smn.h` siblings in the NBIO include directory. Consumers should not assume reset defaults or SMN addresses are available from matching generated files for this revision.

In-tree integration points:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and uses NBIO 7.7 masks with SOC15/PCIE access helpers for NBIO setup.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` selects `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg` for `IP_VERSION(7, 7, 0)` and `IP_VERSION(7, 7, 1)`.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h` exposes the NBIO 7.7 function tables used by discovery and later AMDGPU device setup.
- The kernel PCI/PCIe stack defines many semantics for fields represented here: command/status, bridge apertures, PM, MSI, PCIe link/slot/root capabilities, AER, ACS, DPC, L1 PM substates, lane margining, and related enhanced capabilities.

## Risks And Edge Cases

- ASIC revision mismatch is the main risk. These masks are for NBIO 7.7.0 register layout. Using them with another NBIO generation or incompatible IP version can silently decode or program the wrong bit.
- The chunk starts and ends inside logical register groups. `BIFPLR4_3_SECONDARY_STATUS` begins before this range, and `BIFPLR5_1_LANE_12_MARGINING_LANE_CNTL` continues after it. Any final per-file analysis must reconcile adjacent chunks before treating either group as complete.
- `BIFPLR5_1` is one instance in a repeated PCIe root-port family. Similar blocks for other `BIFPLR*` instances can hide generator drift or copy skew if validation exercises only one port.
- Many fields are status bits with hardware side effects or PCIe-defined write-one-to-clear behavior. A careless read-modify-write against AER, DPC, RP PIO, slot status, root status, lane error, or margining status fields can lose diagnostic information or clear latched errors.
- Control fields can affect device reachability. Misprogramming command enables, bridge aperture base/limit values, link disable/retrain controls, slot power controls, root control, ACS, VC, multicast, DPC, L1 substates, ESM, 16 GT/s equalization, or lane margining can break enumeration, DMA, interrupt delivery, isolation, link training, or error containment.
- Full-width masks such as header logs, TLP prefix logs, message addresses, serial-number dwords, and overlay/address fields are not a guarantee that arbitrary writes are harmless. Access type and ownership are hardware-defined outside this file.
- Reserved placeholder macros for `DEVICE_STATUS2`, slot capability/control/status 2, and other reserved fields should not be interpreted as functional feature support.
- ESM speed-capability fields are dense and regular. A one-bit shift error in generated speed masks could produce plausible-looking but incorrect link capability reporting.

## Test And Validation Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware observation:

- Build AMDGPU with NBIO 7.7 support enabled. This catches missing or malformed macro names referenced by `nbio_v7_7.c` and related code.
- Cross-check every register in this range against `nbio_7_7_0_offset.h` so shift/mask definitions and register offsets remain aligned.
- Run generated-header sanity checks: each field should have matching `__SHIFT` and `_MASK`; masks should match their shift/width; repeated lane equalization and margining groups should be structurally consistent across lanes; repeated root-port groups should match the hardware database where intended.
- Verify chunk-boundary reconciliation: preceding research must supply the beginning of `BIFPLR4_3_SECONDARY_STATUS`, and following research must complete `BIFPLR5_1_LANE_12_MARGINING_LANE_CNTL` plus remaining lane margining definitions.
- On matching hardware, validate PCIe enumeration and `lspci -vvv` style readback for bridge apertures, PM, MSI, PCIe device/link/slot/root capabilities, AER, ACS, L1 PM substates, DPC, data link feature, 16 GT/s capability, and lane margining where visible.
- Exercise suspend/resume, GPU reset, and runtime power-management paths to confirm bridge decode, link control/status, interrupt delivery, and error-reporting state are preserved or restored as expected by firmware and AMDGPU.
- For error reporting, compare AER/DPC/RP PIO decoded values against injected or platform-reported PCIe errors, and ensure status clearing is deliberate rather than a side effect of mask use.
- For link and signal-integrity features, validate equalization, ESM capability reporting, 16 GT/s status, parity mismatch reporting, and lane margining controls/status against hardware diagnostics on a platform that exposes the relevant port.

## Chunk Boundary Notes

Line 130390 enters after `BIFPLR4_3_SECONDARY_STATUS__DEVSEL_TIMING__SHIFT`, so this document covers only the rest of that register and the following `BIFPLR4_3` tail. Line 130525 introduces `nbio_pcie1_bifplr5_cfgdecp`, and the chunk then owns the `BIFPLR5_1` block through the first four `LANE_12_MARGINING_LANE_CNTL` definitions. The next chunk must finish lane 12 margining and the remaining lane margining registers before the `BIFPLR5_1` port can be treated as fully documented.
