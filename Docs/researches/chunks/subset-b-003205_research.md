# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 109354-111781

## Scope

This chunk is generated register-field metadata for the AMD NBIO 7.2.0 PCIe bridge/link register space. It contains only preprocessor constants: each field is represented by a `__SHIFT` value and a `__MASK` value that downstream code can use to extract or compose MMIO/PCI configuration register fields. There are no C functions, structs, executable control flow, allocation paths, or persistent software data structures in this range.

The range begins at the tail of `BIFPLR0_1_LINK_CNTL` (`DRS_SIGNALING_CONTROL_MASK`) and then covers most of the `BIFPLR0_1` PCIe capability and extended capability mask set. Near the end it transitions at line 111541 to `addressBlock: nbio_pcie0_bifplr1_cfgdecp`, beginning the `BIFPLR1_1` bridge configuration decode block.

## Purpose

The constants map PCIe capability, advanced error reporting, equalization, margining, CCIX/ESM, MSI, ACS, DPC, multicast, and bridge configuration fields for AMDGPU/NBIO code. They are the low-level schema for register programming and diagnostics: call sites can read a register value, mask the relevant bits, shift them into field units, or update fields while preserving unrelated bits.

The header is intended to stay synchronized with the ASIC register specification. Its value is in exact bit positions and masks rather than behavior. A one-bit drift here would misprogram PCIe link control, error handling, power management, interrupt routing, or bridge windows.

## Register Families Covered

The first `BIFPLR0_1` section describes PCIe link and slot capabilities for the port:

- `BIFPLR0_1_LINK_STATUS` exposes current link speed, negotiated width, training state, slot clock, data-link active state, and bandwidth notification status.
- `BIFPLR0_1_SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` cover attention/power indicators, hotplug, presence detection, electromechanical interlock, command-completed interrupt, and data-link-state-change reporting.
- `BIFPLR0_1_ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` provide root-port SERR/PME/CRS visibility controls and PME requestor/status bits.

The PCIe capability v2 block follows:

- `BIFPLR0_1_DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` cover completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, ten-bit tags, OBFF, end-to-end TLP prefix handling, and emergency power reduction fields.
- `BIFPLR0_1_LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported speeds, target speed, equalization controls, retimer/RTM presence, crosslink status, DRS messaging, transmit margin, compliance, selectable de-emphasis, and downstream-component presence.
- `BIFPLR0_1_SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` are reserved-field placeholders in this chunk.

The conventional capability list and message-signaled interrupt area includes:

- `BIFPLR0_1_MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, and `MSI_MSG_DATA_64` for MSI capability discovery, enable/multiple-message settings, 64-bit addressing support, MSI address, and MSI payload data.
- `BIFPLR0_1_SSID_CAP_LIST`/`SSID_CAP` and `MSI_MAP_CAP_LIST`/`MSI_MAP_CAP` for subsystem IDs and MSI mapping capability state.

Several PCIe extended capability headers use the standard `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields. In this chunk they include vendor-specific capability, virtual channel, device serial number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substate, DPC, ESM, data-link feature, 16 GT/s PHY, margining, and CCIX capability headers.

## Error, Isolation, And Diagnostics Fields

The Advanced Error Reporting portion is a major integration surface:

- `BIFPLR0_1_PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` enumerate uncorrectable error bits such as data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.
- `BIFPLR0_1_PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` enumerate receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable error, and header-log overflow.
- `BIFPLR0_1_PCIE_ADV_ERR_CAP_CNTL` provides first-error pointer, ECRC check capability/enable, multiple-header receive capability/enable, TLP prefix log presence, and completion-timeout logging capability.
- `BIFPLR0_1_PCIE_HDR_LOG0..3`, `PCIE_TLP_PREFIX_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID` support root error command/status reporting and captured TLP/header diagnostics.

Downstream Port Containment and root-port PIO diagnostics are also represented:

- `BIFPLR0_1_PCIE_DPC_CAP_LIST`, `DPC_CNTL`, `DPC_STATUS`, and `DPC_ERROR_SOURCE_ID` define DPC interrupt message number, root-port extensions, poisoned TLP egress blocking, software trigger support, PIO log size, trigger enables, completion control, interrupt/correctable signaling enables, software trigger, busy/status bits, trigger reason, and source ID.
- `BIFPLR0_1_PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` share the same config/IO/memory unsupported-request, completer-abort, and completion-timeout bit layout.
- `BIFPLR0_1_PCIE_RP_PIO_HDR_LOG0..3` and `PCIE_RP_PIO_PREFIX_LOG0..3` provide captured TLP header/prefix log fields for PIO errors.

ACS fields (`BIFPLR0_1_PCIE_ACS_CAP` and `PCIE_ACS_CNTL`) advertise and control source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress vector size. These bits are important for IOMMU isolation and peer-to-peer routing behavior.

## Link Training, Equalization, And Margining

The chunk contains several repeated per-lane register groups for x16 links:

- `BIFPLR0_1_PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL` define downstream/upstream TX preset and RX preset-hint fields for the secondary PCIe capability lane equalization area.
- `BIFPLR0_1_LINK_STATUS_16GT` reports 16 GT/s equalization completion, phase success, and link equalization request bits. `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT` expose 16-bit parity mismatch status vectors.
- `BIFPLR0_1_LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` provide 16 GT/s downstream/upstream TX preset fields per lane.
- `BIFPLR0_1_MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_CNTL/STATUS` through `LANE_15_MARGINING_LANE_CNTL/STATUS` describe PCIe margining receivers, independent timing/voltage margining capability, sample reporting method, max timing/voltage offset, margin payloads, and lane-specific status.

The ESM/CCIX portion adds higher-rate capability and training fields:

- `BIFPLR0_1_PCIE_ESM_HEADER_1`, `HEADER_2`, `STATUS`, `CTRL`, and `CAP_1..7` describe ESM capability identity, status/control, and supported data-rate bitmaps. The `CAP_1..7` bitmaps span rates from 2.5 GT/s through 28.0 GT/s in 0.1 GT/s style increments.
- `BIFPLR0_1_PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1`, `HEADER_2`, `PCIE_CCIX_CAP`, `PCIE_CCIX_ESM_REQD_CAP`, `PCIE_CCIX_ESM_OPTL_CAP`, `PCIE_CCIX_ESM_STATUS`, and `PCIE_CCIX_ESM_CNTL` describe CCIX vendor/capability metadata, ESM mode support, reach length, recalibration requirement, calibration time, quick equalization timeout, required data-rate support at 2.5/5/8/16/20/25 GT/s, current data rate, calibration complete, data-rate programming, ESM enable, extended equalization timeouts, link reach target, retimer presence, and timeout select.
- `BIFPLR0_1_ESM_LANE_0_EQUALIZATION_CNTL_20GT` through `LANE_15...20GT` and `BIFPLR0_1_ESM_LANE_0_EQUALIZATION_CNTL_25GT` through `LANE_15...25GT` provide per-lane downstream/upstream TX preset masks for ESM operation at 20 GT/s and 25 GT/s.
- `BIFPLR0_1_PCIE_CCIX_TRANS_CAP` and `PCIE_CCIX_TRANS_CNTL` expose support and enable bits for CCIX optimized TLP format.

## Bridge Decode Tail: `BIFPLR1_1`

At line 111541 the chunk starts `addressBlock: nbio_pcie0_bifplr1_cfgdecp`. This tail covers the beginning of the `BIFPLR1_1` PCI/PCIe bridge configuration decode space:

- Identification and class-code fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- Bridge window and bus-number fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, `IO_BASE_LIMIT_HI`, and `ROM_BASE_ADDR`.
- Interrupt and bridge controls: `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL`.
- Capability-list entries and adapter/power-management data: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, and the first fields of `PMI_STATUS_CNTL` through `DATA_SELECT_MASK` at the chunk boundary.

This tail is incomplete by design: subsequent chunks should continue `BIFPLR1_1_PMI_STATUS_CNTL` and later `BIFPLR1_1` capability registers.

## APIs, Types, And Usage Pattern

There are no callable APIs or C types in this chunk. The important interface is the macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the right-shift amount for the field.
- `REGISTER__FIELD_MASK` or `REGISTER__FIELD__MASK` gives the unshifted bitmask in register position. Most macros in this file use `REGISTER__FIELD_MASK`; a few generated names whose field already ends in `MASK` produce double `...MASK_MASK` names, such as AER mask fields.

Typical consumers combine these with AMDGPU register helpers or generic field helpers:

```c
field = (reg_value & BIFPLR0_1_LINK_STATUS__NEGOTIATED_LINK_WIDTH_MASK) >>
        BIFPLR0_1_LINK_STATUS__NEGOTIATED_LINK_WIDTH__SHIFT;
```

For writes, the mask should be used to clear only the intended field before OR-ing the shifted new value. Full-width masks such as `0xFFFFFFFFL` indicate entire-register payload/log fields, while `RESERVED` entries should normally not be used to invent new software semantics.

## Control Flow And State

This header has no runtime control flow. Control flow exists in consumers that select registers, read or write values, and branch on fields such as link training, data-link active, DPC trigger state, AER error status, PME status, margining status, or ESM calibration complete.

Hardware state is represented by the named registers, not stored by this file. Many fields are hardware-latched status or capability bits; others are control bits that software can program through MMIO/config-space writes. Persistent effects are hardware/firmware visible only after a caller writes the corresponding register. The header itself creates no persistence and performs no synchronization.

## Dependencies And Integration Points

This file belongs to the AMDGPU ASIC register include hierarchy under `drivers/gpu/drm/amd/include/asic_reg/nbio`. It is expected to be included by AMD NBIO/PCIe management code together with companion offset headers that provide register addresses. The masks here are useless without matching address definitions and register accessors.

Important integration points include:

- PCIe link management and bring-up code that checks negotiated speed/width, training state, retimer presence, equalization status, and 16 GT/s/ESM training fields.
- Power-management code using LTR, L1 PM substate, PME, OBFF, emergency power reduction, and clock/power-management bits.
- Interrupt setup using MSI capability fields and DPC/root error interrupt enable bits.
- Error reporting and recovery paths using AER, DPC, root error, RP PIO, and header/prefix log fields.
- Isolation and topology code that depends on ACS, bridge I/O/memory/prefetchable windows, bus numbers, and class/header fields.
- Diagnostics tooling that decodes serial number, link status, margining payload/status, ESM data rates, and captured TLP logs.

## Risks

The main risk is register schema drift. These macros encode hardware ABI details; incorrect masks or shifts can silently corrupt unrelated fields or misread status. High-risk areas in this chunk include AER/DPC error bits, ACS controls, link equalization/margining controls, CCIX/ESM data-rate programming, and bridge memory/IO window masks.

Double-`MASK_MASK` macro names are generated but easy to misuse in hand-written code. A developer may also confuse capability bits with control bits, reserved placeholders with usable fields, or status bits that are write-one-to-clear in hardware with ordinary read-only status. This document cannot determine access semantics; callers must consult the register spec or existing AMDGPU access patterns.

Per-lane groups are repetitive and susceptible to copy/paste lane-number errors. Code that programs lanes should avoid hard-coded ad hoc substitutions unless no table-driven alternative exists. Boundary risk also exists at the start and end of this chunk: line 109354 is only the final mask for `BIFPLR0_1_LINK_CNTL`, and line 111781 stops mid-register in `BIFPLR1_1_PMI_STATUS_CNTL`.

## Test Signals

Useful validation signals for consumers of these masks include:

- Build coverage: all included macros compile without redefinition or missing companion address symbols.
- Register decode tests or debugfs output showing sane PCIe link speed/width, link active/training state, and slot/root status on known hardware.
- AER/DPC fault-injection or error-recovery testing that confirms the expected status, mask, severity, root status, source ID, and header-log bits are decoded.
- PCIe topology/IOMMU tests confirming ACS control bits and bridge bus/window fields match expected isolation and resource routing.
- MSI interrupt smoke tests confirming address/data/control fields are not shifted incorrectly.
- Power-management tests covering L1 PM substate, LTR, PME, OBFF, and emergency power reduction behavior across suspend/resume and runtime PM.
- High-speed link tests on 16 GT/s, 20 GT/s, or 25 GT/s capable systems checking equalization completion, per-lane presets, margining status payloads, and ESM calibration/current-rate fields.
