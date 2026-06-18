# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/defines.h

## Purpose

This header is the central bit-field and constant catalog for e1000e hardware programming. It defines descriptor bits, register masks, advertised link modes, interrupt bits, flow-control constants, NVM commands and offsets, PHY IDs, PHY register fields, timeout bounds, power-management flags, timestamping bits, and error codes used by the driver implementation files.

## Important APIs, Types, and Functions

There are no functions or types, only macros. Important groups include descriptor definitions (`E1000_RXD_*`, `E1000_RXDEXT_*`, `E1000_TXD_*`), control/status bits (`E1000_CTRL_*`, `E1000_STATUS_*`, `E1000_RCTL_*`, `E1000_TCTL_*`), flow-control and VLAN masks (`E1000_FCRTH_RTH`, `E1000_FCRTL_RTL`, `E1000_VLAN_FILTER_TBL_SIZE`), interrupt masks (`E1000_ICR_*`, `E1000_IMS_*`, `IMS_ENABLE_MASK`, `IMS_OTHER_MASK`), NVM fields (`E1000_EECD_*`, `NVM_*`, `NVM_SUM`), PHY IDs and registers (`IGP01E1000_I_PHY_ID`, `M88E1111_I_PHY_ID`, `BME1000_E_PHY_ID_R2`, `M88E1000_*`, `GG82563_*`, `E1000_MDIC_*`), and PTP timestamping constants (`E1000_TSYNCTXCTL_*`, `E1000_TSYNCRXCTL_*`, `E1000_TIMINCA_*`).

## Control Flow

The file has no direct control flow, but it shapes almost every hardware branch in the driver. Runtime code tests these masks after MMIO or PHY reads, composes register writes from them, uses timeout macros to bound polling loops, and uses error-code macros for internal helper failures. Several compound masks, such as `E1000_RXD_ERR_FRAME_ERR_MASK`, `PCIE_NO_SNOOP_ALL`, and advertised speed sets, encode reusable policy.

## State and Persistence Behavior

Many macros name persistent or semi-persistent device state. NVM offsets and checksum constants affect EEPROM/flash contents that survive reboot. Wake, power, LED, flow-control, descriptor, and timestamp bits affect hardware register state until reset or reprogramming. The error-code constants are internal status values and are not persisted.

## Dependencies and Integration Points

`hw.h` includes this file after `regs.h`, making the constants globally available through `e1000.h`. Implementation files including `82571.c`, `ethtool.c`, MAC/PHY/NVM helpers, netdev paths, and PTP code depend on these definitions matching the hardware manuals. It also uses common kernel helpers such as `BIT()` and field macros through including contexts.

## Risks and Edge Cases

This file is high blast-radius despite containing no code. A wrong bit mask can produce silent hardware misprogramming, data corruption, interrupt loss, broken power management, invalid NVM checksums, or bad timestamp reporting. Timeout constants balance hardware latency against boot/probe delays. Some values intentionally encode unsupported behavior, such as no 1000 half-duplex advertisement, and should not be generalized.

## Test Signals

Compile coverage catches only syntax and missing macro issues. Stronger signals are ethtool register tests, EEPROM checksum tests, interrupt tests, loopback diagnostics, Wake-on-LAN tests, timestamping validation, speed/autoneg negotiation, VLAN filter tests, and reset/power-cycle stress across multiple e1000e MAC families.
