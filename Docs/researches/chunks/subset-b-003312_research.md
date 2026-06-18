# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 127986-130389

## Scope

This chunk covers generated shift and mask macros from the NBIO 7.7.0 AMD GPU register mask header. It begins at the tail of `BIFPLR4_2_PMI_STATUS_CNTL`, covers the main PCIe and extended capability bitfields for `BIFPLR4_2`, and then crosses into `nbio_pcie1` bridge configuration decode blocks for `BIFPLR0_3` through the start of `BIFPLR4_3`.

The covered register families are:

- `BIFPLR4_2` PCIe capability, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe Capability 2 registers.
- `BIFPLR4_2` MSI, subsystem ID, MSI-map, vendor-specific capability, virtual-channel, device serial number, AER, secondary PCIe, per-lane equalization, ACS, multicast, L1 PM sub-state, DPC/root-port PIO, ESM, and 16 GT/s / 32 GT/s link capability groups.
- `nbio_pcie1_bifplr0_cfgdecp` through `nbio_pcie1_bifplr3_cfgdecp`, each with bridge bus-number, I/O and memory window, secondary status, slot, slot2, and SSID fields.
- The start of `nbio_pcie1_bifplr4_cfgdecp`, through the first fields of `BIFPLR4_3_SECONDARY_STATUS`.

This is a generated hardware bitfield map. It contains C preprocessor constants only, with no functions, structs, variables, allocation, or executable control flow.

## Purpose

The purpose of this header range is to provide the bit-level ABI between AMDGPU/NBIO code and the NBIO 7.7.0 PCIe local-root configuration-space register images. Each field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field bit offset.
- `<REGISTER>__<FIELD>_MASK`, the field mask used to isolate, test, or compose the field value.

Driver code normally combines these definitions with matching register offset/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. This chunk supplies field layout knowledge for decoding bridge windows, PCIe capability state, interrupt capability state, AER/DPC diagnostics, link equalization status, ESM data-rate support, and access-control or multicast controls.

## Important Macro Families

### BIFPLR4_2 Base PCIe Capability

The first part of the chunk completes `BIFPLR4_2_PMI_STATUS_CNTL` masks and then defines the standard PCIe capability layout for `BIFPLR4_2`:

- `PCIE_CAP_LIST` and `PCIE_CAP` expose capability-list ID, next pointer, PCIe capability version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` cover max payload support/size, phantom functions, extended tags, relaxed ordering, no-snoop, aux power, error-reporting enables/status, FLR capability, transaction-pending status, and emergency power reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe supported and negotiated link speed/width, ASPM and PM controls, link disable/retrain, common clock, extended sync, link bandwidth interrupts, DRS signaling, data-link active status, and bandwidth-management status.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` expose hotplug, power-controller, attention/power indicators, MRL, interlock, presence detect, command complete, data-link state change, in-band presence disable, and physical-slot fields.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` define root-port SERR/PME/CRS controls and PME requester/status tracking.

These macros mirror PCIe root-port configuration-space semantics. Some fields are advertised capability bits, some are driver-programmed controls, and others are status or sticky event fields.

### PCIe Capability 2, MSI, SSID, VSEC, and VC

The `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` groups cover later PCIe features: completion-timeout ranges and disablement, ARI, atomic operations, IDO, LTR, OBFF, 10-bit tags, TLP prefixes, target link speed, compliance/de-emphasis controls, 8 GT/s equalization phases, RTM presence, crosslink state, and DRS messages.

Interrupt and identity capability groups include:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data words, and 64-bit MSI data fields.
- `SSID_CAP_LIST` and `SSID_CAP` for subsystem vendor and subsystem IDs.
- `MSI_MAP_CAP_LIST` and `MSI_MAP_CAP` for MSI mapping enable/fixed/type bits.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and scratch VSEC registers.

Virtual-channel support is represented by `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status registers, and `PCIE_VC0_RESOURCE_*` / `PCIE_VC1_RESOURCE_*` fields. These define external VC counts, arbitration table offsets and selectors, traffic-class-to-VC maps, VC IDs, enable bits, and negotiation/table status.

### AER and Error Logging

The AER capability section includes:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress block, TLP prefix block, and poisoned egress block fields.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for correctable error classes.
- `PCIE_ADV_ERR_CAP_CNTL`, header log registers, root error command/status, error source IDs, and TLP prefix log registers.

These masks are diagnostic integration points. The status fields may be sticky or write-one-to-clear depending on hardware semantics, while mask/severity/command fields determine what is reported upward as corrected, nonfatal, fatal, or system-error events.

### Link Equalization, ACS, Multicast, L1 PM, DPC, and ESM

`BIFPLR4_2_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` define secondary PCIe capability and per-lane preset/hint fields for downstream and upstream equalization.

`PCIE_ACS_CAP` and `PCIE_ACS_CNTL` cover source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, I/O request blocking, memory target access controls, and unclaimed request redirect control. These fields matter for peer-to-peer isolation and IOMMU-visible routing behavior.

`PCIE_MC_*` registers describe multicast maximum groups, enablement, base addresses, receive vectors, block-all and block-untranslated masks, and overlay BAR fields. `PCIE_L1_PM_SUB_*` exposes L1.1/L1.2 support and enablement, link activation, common-mode restore time, LTR threshold, and T-power-on values.

The DPC section defines capability, control, status, error-source, and root-port PIO status/mask/severity/system-error/exception fields, plus PIO header and prefix logs. It controls and reports downstream port containment and root-port PIO exception details for configuration, I/O, and memory request classes.

The ESM section defines ESM capability headers, status/control, and a long bitmap of supported data rates from 8.0 GT/s through 28.0 GT/s across `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. The nearby 16 GT/s and 32 GT/s link groups expose equalization status and 32 GT/s modified training sequence / precoding fields.

### nbio_pcie1 BIFPLR Bridge Blocks

The second half of the chunk starts `nbio_pcie1` bridge decode blocks. `BIFPLR0_3`, `BIFPLR1_3`, `BIFPLR2_3`, and `BIFPLR3_3` each define the same compact PCI-to-PCI bridge-style groups:

- `SUB_BUS_NUMBER_LATENCY` for primary, secondary, subordinate bus, and secondary latency timer.
- `IO_BASE_LIMIT` and `IO_BASE_LIMIT_HI` for lower and upper I/O base/limit windows.
- `SECONDARY_STATUS` for legacy PCI status bits including parity, target abort, master abort, system error, DEVSEL timing, and fast-back/66 MHz capability flags.
- `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, and `PREF_LIMIT_UPPER` for non-prefetchable and prefetchable bridge memory windows.
- `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` for hotplug, power, presence, MRL, interlock, in-band presence disable, and reserved Slot 2 state.
- `SSID_CAP_LIST` and `SSID_CAP` for subsystem identity.

The chunk then starts `nbio_pcie1_bifplr4_cfgdecp` with `BIFPLR4_3_SUB_BUS_NUMBER_LATENCY`, `BIFPLR4_3_IO_BASE_LIMIT`, and the first `BIFPLR4_3_SECONDARY_STATUS` shift definitions. The rest of the `BIFPLR4_3` bridge block continues in a later chunk.

## Control Flow and State Behavior

This header chunk has no runtime control flow. Its effect is compile-time: it lets C code generate the correct shifts and masks for hardware register reads and writes.

The persistent state represented by these macros lives in NBIO/PCIe configuration-space registers, not in this header. Important state includes:

- PCIe capability, link, slot, root, power-management, MSI, subsystem ID, VSEC, VC, and bridge-window configuration.
- Error and containment state in AER and DPC status, mask, severity, source-ID, header-log, and prefix-log registers.
- Link training and diagnostics state in equalization, 16 GT/s, 32 GT/s, lane error, RTM, and ESM capability/status fields.
- Isolation and routing state in ACS and multicast controls.
- `nbio_pcie1` local-root bridge bus, I/O, memory, prefetchable memory, hotplug, and subsystem identity state.

Some fields are read-only advertised capability bits, some are writable controls, some are status bits, and some may have command-like or write-one-to-clear behavior. The header does not encode those access semantics, so consumers must follow the NBIO hardware specification and existing AMDGPU access patterns when polling, clearing, or programming these fields.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbio_7_7_0_offset.h` supplies corresponding register addresses/base indices for the `BIFPLR*_2_*` and `BIFPLR*_3_*` names.
- `nbio_7_7_0_default.h`, where present, supplies reset/default values.
- AMDGPU SOC15/NBIO register helpers consume these macros to read, modify, and write field values without hard-coded bit positions.

Likely source-tree integration points include:

- NBIO and PCIe initialization paths that configure root ports, bridge windows, slot behavior, link targets, and power-management controls.
- PCIe error handling and diagnostics that decode AER, DPC, root error, PIO exception, header log, and TLP prefix log fields.
- Link-management and hardware diagnostic paths that inspect 8 GT/s, 16 GT/s, 32 GT/s equalization, per-lane presets, lane error, ESM data-rate, and DRS/RTM fields.
- Interrupt setup paths that interpret MSI capability, message address/data, multi-message, 64-bit, and extended data fields.
- IOMMU, peer-to-peer, or virtualization-sensitive flows that rely on ACS and multicast capability/control encodings.
- PCI enumeration/configuration logic that observes bridge bus-number, I/O, memory, prefetchable-memory, secondary-status, slot, and subsystem fields for `nbio_pcie1` local roots.

These definitions must be used with the matching NBIO 7.7.0 offset and default headers. Mixing masks from another NBIO generation could silently decode or write the wrong bits even when register names look similar.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can corrupt PCIe capability advertisement, link-control programming, bridge window decoding, MSI setup, AER/DPC handling, or slot state.
- AER and DPC fields are operationally sensitive. Treating sticky or write-one-to-clear status bits as normal read/write fields can lose fault evidence or fail to clear real errors.
- ACS and multicast fields affect routing and isolation. Incorrect capability advertisement or control programming can change peer-to-peer forwarding, translated P2P behavior, I/O blocking, or multicast address filtering.
- Link equalization and ESM fields are repetitive. Copy/paste mistakes across lane numbers or data-rate bits can make diagnostics report the wrong lane, phase, or supported rate.
- Bridge-window masks must align with PCI bridge configuration layout. Incorrect bus, I/O, memory, or prefetchable window fields can break downstream enumeration or expose an invalid address aperture.
- The chunk starts and ends mid-family: `BIFPLR4_2_PMI_STATUS_CNTL` shifts precede this chunk, and `BIFPLR4_3_SECONDARY_STATUS` plus the rest of `BIFPLR4_3` continue after line 130389. The final per-file merge must reconcile adjacent chunks before drawing whole-file conclusions.

## Test and Validation Signals

Useful validation is mostly build, register decode, and hardware integration coverage:

- Build AMDGPU/NBIO consumers that include `nbio_7_7_0_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- PCI configuration-space enumeration should confirm `BIFPLR4_2` capability-list, PCIe capability, MSI, SSID, VSEC, VC, AER, DPC, ESM, 16 GT/s, and 32 GT/s fields decode as expected on NBIO 7.7.0 hardware.
- Link diagnostics should verify reported link speed/width, retrain/training status, 8 GT/s, 16 GT/s, 32 GT/s equalization phase status, lane error status, per-lane presets, and ESM data-rate capability bits.
- Error-path tests should inject or observe correctable, uncorrectable, and DPC/PIO errors and confirm status, mask, severity, source ID, header log, and TLP prefix log fields decode correctly.
- Interrupt validation should verify MSI enable, multi-message, 64-bit address/data, extended data, and message address/data field handling.
- Isolation/routing tests should exercise ACS control behavior and multicast receive/blocking/overlay BAR fields with peer-to-peer or IOMMU-sensitive workloads.
- PCI bridge enumeration should verify `nbio_pcie1` `BIFPLR0_3` through `BIFPLR3_3` bus numbers, I/O windows, memory windows, prefetchable windows, secondary status, slot state, and subsystem IDs; adjacent chunk validation is needed for the complete `BIFPLR4_3` block.
