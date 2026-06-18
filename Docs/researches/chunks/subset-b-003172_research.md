# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 29355-31792

## Scope

This chunk is a generated AMD NBIO 7.2.0 register field header segment. It contains C preprocessor constants only: `__SHIFT` values and `_MASK` values for fields in PCIe bridge/config-space register blocks. There are no functions, structs, runtime branches, memory allocations, or direct MMIO accesses in the chunk. The macros become meaningful when paired with the matching address macros in `nbio_7_2_0_offset.h`, for example `cfgBIFPLR5_PCIE_DLF_ENH_CAP_LIST` at `0x0400` and `cfgBIFPLR6_PCIE_ESM_CAP_1` at `0x03d4`.

The requested range starts inside `BIFPLR5_PCIE_ESM_CAP_7`, beginning with the `ESM_25P7G` field, and ends inside `BIFPLR6_PCIE_ESM_CAP_5`, at `ESM_20P5G__SHIFT`. Adjacent chunks therefore own the beginning of `BIFPLR5_PCIE_ESM_CAP_7` and the rest of `BIFPLR6_PCIE_ESM_CAP_5`/later BIFPLR6 PCIe capability masks.

## Purpose

The header gives AMDGPU/NBIO code stable symbolic names for bit positions and bit masks in NBIO PCIe port register layouts. This lets driver code read, modify, and decode PCIe configuration and enhanced capability fields without hard-coding numeric bit constants inline. In this range the covered register surfaces are:

- Tail of BIFPLR5 ESM advertised data-rate capability bits.
- BIFPLR5 PCIe Data Link Feature, 16 GT/s PHY, lane equalization, lane margining, CCIX, CCIX ESM, and CCIX transaction capability/control fields.
- Start of `addressBlock: nbio_pcie0_bifplr6_cfgdecp`, covering BIFPLR6 PCI/PCIe config header fields, standard PCIe capability fields, MSI/SSID/MSI map capabilities, vendor-specific and virtual-channel enhanced capabilities, device serial number, AER, secondary PCIe, lane equalization, ACS, multicast, L1 PM substates, DPC/RP PIO, and ESM capability fields through part of ESM cap 5.

## Important APIs, Types, And Macros

This file exposes macros rather than APIs or types. The naming pattern is consistent:

- `BIFPLR*_REGISTER__FIELD__SHIFT` gives the least-significant bit index for a field.
- `BIFPLR*_REGISTER__FIELD_MASK` gives the pre-shifted mask for the same field.
- Register comments such as `//BIFPLR6_PCIE_UNCORR_ERR_STATUS` delimit logical hardware registers.
- The `BIFPLR5` and `BIFPLR6` prefixes identify separate PCIe bridge/root-port logical register blocks.

Important BIFPLR5 macro groups in this chunk:

- `BIFPLR5_PCIE_ESM_CAP_7`: ESM capability bits for 25.7 GT/s through 28.0 GT/s in the visible portion of the register.
- `BIFPLR5_PCIE_DLF_ENH_CAP_LIST`, `BIFPLR5_DATA_LINK_FEATURE_CAP`, `BIFPLR5_DATA_LINK_FEATURE_STATUS`: PCIe Data Link Feature capability list/header, local DLF support, remote DLF support, valid state, scaled flow-control support, and DLF exchange enable.
- `BIFPLR5_PCIE_PHY_16GT_ENH_CAP_LIST`, `BIFPLR5_LINK_STATUS_16GT`, parity mismatch status registers, and `BIFPLR5_LANE_0_EQUALIZATION_CNTL_16GT` through lane 15: 16 GT/s capability, equalization completion/phase status, link equalization request, parity status, and per-lane DSP/USP TX presets.
- `BIFPLR5_PCIE_MARGINING_ENH_CAP_LIST`, `BIFPLR5_MARGINING_PORT_CAP`, `BIFPLR5_MARGINING_PORT_STATUS`, and lane 0-15 margining control/status registers: software-ready state plus receiver number, margin type, usage model, and payload fields per lane.
- `BIFPLR5_PCIE_CCIX_*` and `BIFPLR5_ESM_LANE_*_EQUALIZATION_CNTL_20GT/25GT`: CCIX capability headers, CCIX ESM required/optional/status/control fields, 20 GT/s and 25 GT/s ESM lane presets, and CCIX transaction capability/control bits.

Important BIFPLR6 macro groups in this chunk:

- PCI header and bridge fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class/revision fields, bus numbering, IO/memory/prefetchable windows, ROM base, interrupt pins, bridge control, and capability pointer.
- Power management and PCIe core capability fields: `PMI_*`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_*`, `ROOT_*`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt and identity capabilities: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data registers, `SSID_*`, and `MSI_MAP_*`.
- Enhanced capabilities: vendor-specific, virtual channel, device serial number, AER, secondary PCIe/link equalization, ACS, multicast, L1 PM substates, DPC, RP PIO error/logging, and ESM.
- Error reporting macros include uncorrectable/correctable status, masks, severity, advanced error capability/control, header logs, TLP prefix logs, root error command/status, and error source IDs.
- BIFPLR6 ESM coverage includes `PCIE_ESM_CAP_LIST`, ESM headers/status/control, ESM cap 1-4, and the first part of cap 5. These fields advertise supported ESM speeds in 0.1 GT/s increments, with masks laid out as one bit per supported rate.

## Control Flow

There is no executable control flow in this chunk. The effective driver flow around these definitions is external:

1. AMDGPU/NBIO code selects a register address from an offset header such as `cfgBIFPLR6_PCIE_UNCORR_ERR_STATUS`.
2. It reads or writes the register through the driver register-access helpers for config/MMIO space.
3. It extracts or modifies fields using the `*_MASK` and `*__SHIFT` macros from this header.
4. Hardware state changes, posted writes, write-one-to-clear fields, and capability negotiation are governed by PCIe/NBIO hardware semantics, not by this header.

The chunk is therefore a compile-time schema for bitfields. Any sequencing requirements, polling loops, reset behavior, interrupt handling, or link training logic live in source files that include these macros.

## State And Persistence Behavior

The header itself holds no state and persists nothing. It describes stateful hardware registers whose contents can be volatile, strap/configuration-derived, firmware-programmed, driver-programmed, or write-one-to-clear depending on the register class.

Stateful hardware surfaces represented here include:

- Link training and equalization status for 8 GT/s, 16 GT/s, 20 GT/s, and 25 GT/s related capabilities.
- Per-lane equalization presets and lane margining command/status values.
- PCI bridge windows, command/status bits, power-management state, MSI enable/address/data fields, and slot/root status.
- AER/DPC/RP PIO error status, masks, severity, source IDs, captured headers, and prefix logs.
- ACS, virtual channel, multicast, L1 PM substate, Data Link Feature, CCIX, and ESM capability/control state.

Because these macros are raw masks, they do not encode access type. Callers must know whether a field is read-only, read/write, sticky, clear-on-write, write-one-to-clear, or reserved.

## Dependencies And Integration Points

Primary dependencies and integration points:

- `nbio_7_2_0_offset.h` supplies register offsets that pair with the masks in this file.
- AMDGPU NBIO, PSP/firmware initialization, PCIe link-management, error-handling, and debug code may include this header through ASIC-specific register headers.
- Kernel PCI/PCIe concepts are mirrored in these registers: command/status, capability lists, MSI, power management, AER, ACS, DPC, virtual channels, L1 PM substates, lane margining, and equalization.
- The generated format likely depends on AMD internal register databases. Hand editing one macro without updating sibling offset/mask headers risks ABI drift against hardware and against other ASIC revisions such as `nbio_7_7_0_sh_mask.h`.

This chunk also marks a structural transition from BIFPLR5 to BIFPLR6 at `// addressBlock: nbio_pcie0_bifplr6_cfgdecp`. Consumers must use the prefix that matches the physical/logical port they are accessing; BIFPLR5 masks should not be combined with BIFPLR6 offsets unless the hardware documentation explicitly aliases the layouts.

## Risks

- Incorrect mask or shift values can silently corrupt adjacent hardware fields during read-modify-write sequences.
- Several fields cover status/error registers. Using masks without understanding write-one-to-clear or sticky semantics can lose diagnostic evidence or fail to clear interrupts.
- Reserved fields are represented in places as full-register masks, such as `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `DEVICE_STATUS2`, and slot 2 fields. Callers should avoid programming reserved bits unless the hardware programming guide requires it.
- The chunk begins and ends mid-register group. Research or automated processing that assumes complete register ownership for this chunk can miss `BIFPLR5_PCIE_ESM_CAP_7` fields before line 29355 and `BIFPLR6_PCIE_ESM_CAP_5` mask fields after line 31792.
- BIFPLR5 and BIFPLR6 contain many repeated lane macros. Copy/paste or generated-data errors can be hard to see visually; lane index, register offset, and field prefix should be checked together.
- CCIX and ESM fields are specialized high-speed interconnect/link-training surfaces. Misprogramming them could affect link bring-up, equalization, interoperability, or performance rather than producing an obvious compile-time failure.

## Test Signals

Useful validation signals for changes involving this chunk:

- Build coverage: AMDGPU code including NBIO 7.2.0 headers compiles without undefined macro or duplicate definition errors.
- Static consistency: every `__SHIFT` field has the expected companion `_MASK`, masks line up with shifts and field widths, and lane 0-15 repeated groups advance consistently.
- Offset/header consistency: names in this `*_sh_mask.h` range match `cfg*` names and address ordering in `nbio_7_2_0_offset.h`.
- Runtime PCIe signals: link speed/width, equalization completion, DLF exchange status, L1 PM substate behavior, MSI delivery, AER/DPC reporting, and lane margining/debug outputs behave as expected on NBIO 7.2.0 hardware.
- Error-path signals: AER uncorrectable/correctable status bits, masks, severity registers, RP PIO logs, and DPC status/source IDs can be decoded correctly in diagnostic paths.
- Register-dump comparison: decoded field names and masks should match vendor register documentation or known-good dumps from the same ASIC generation.
