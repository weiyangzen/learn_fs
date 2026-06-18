# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_hw.h

## Purpose
`rocker_hw.h` defines the hardware ABI for the Rocker PCI switch device. It contains device IDs, BAR/register layout, MSI-X vector allocation, DMA ring registers and descriptor structures, TLV command/event/RX/TX schemas, OF-DPA flow and group encodings, and general switch control registers.

## Important APIs, Types, And Constants
Return-code constants mirror errno-like hardware results. `PCI_DEVICE_ID_REDHAT_ROCKER`, `ROCKER_PCI_BAR0_SIZE`, and `ROCKER_FP_PORTS_MAX` describe device identity and size bounds. MSI-X macros map command, event, test, and per-port TX/RX vectors. DMA definitions include `enum rocker_dma_type`, ring register offsets, size limits/defaults, `struct rocker_desc`, and `ROCKER_DMA_DESC_COMP_ERR_GEN`. `struct rocker_tlv` is the packed TLV header. The many TLV enums define command types, port settings/statistics, events, RX flags, TX offload/frags, and OF-DPA flow fields. OF-DPA table/group enums and `ROCKER_GROUP_*` macros encode group IDs.

## Control Flow Role
This header has no code paths but dictates all command and data-plane protocol between driver and device. Core code programs DMA rings through the register macros, consumes events using event TLVs, builds TX/RX metadata TLVs, and programs OF-DPA flows/groups using command TLVs. Group ID macros are used by the OF-DPA layer to derive hardware group identifiers from VLAN, port, and index data.

## State And Persistence
DMA descriptors and TLV buffers are hardware-shared runtime state. Register offsets represent MMIO state in BAR0. Group IDs and flow cookies may persist in the device forwarding tables until explicitly deleted or device reset. No host-side durable persistence is defined.

## Dependencies And Integration Points
The header depends on Linux types and bit macros through included kernel headers in users. It integrates tightly with `rocker.h`, `rocker_main.c`, `rocker_tlv.c`, and `rocker_ofdpa.c`, and externally with PCI, switchdev, bridge, neighbour, and FIB subsystems.

## Risks
This file is an ABI contract: changing enum values, TLV IDs, descriptor layout, register offsets, or group encoding breaks compatibility with the Rocker device/emulator. `struct rocker_desc` uses fixed-width fields and expected alignment. The `ROCKER_GROUP_VLAN_GET()` macro references `ROCKER_GROUP_VLAN_ID_MASK`/`SHIFT`, while the file defines `ROCKER_GROUP_VLAN_MASK`/`SHIFT`; that should be checked because it may be a latent macro-name defect unless provided elsewhere. TX fragment and ring-size limits must match the device. TLV length/type parsing must defend against malformed hardware data.

## Test Signals
Tests should exercise PCI BAR size checks, reset/control registers, MSI-X vector count for multiple port counts, DMA ring reset/head/tail/credit handling, command TLV round trips, event TLV parsing for link and MAC/VLAN events, RX checksum/offload flags, TX checksum/TSO/fragments up to `ROCKER_TX_FRAGS_MAX`, OF-DPA flow add/mod/del/stats, group ID encode/decode, and build coverage of all macros.
