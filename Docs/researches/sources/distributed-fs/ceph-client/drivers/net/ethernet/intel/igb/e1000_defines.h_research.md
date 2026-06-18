# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/e1000_defines.h

## Purpose
Central register-bit and constant catalog for the IGB shared e1000 hardware code.

## Important APIs, Types, And Functions
Defines constants for descriptor multiples, wake-on-LAN, `CTRL`/`CTRL_EXT`, RX/TX controls, PCS/SerDes, link speeds, advertised capabilities, LEDs, DMA coalescing, interrupt causes/masks, NVM access and offsets, semaphores, PHY IDs and registers, MDIC/MDICNFG, EEE, thermal sensors, VLAN filters, Qav, and management pass-through fields.

## Control Flow
No executable control flow. The file supplies named masks and shifts used by all IGB hardware manipulation paths.

## State And Persistence
The definitions describe persistent device state in PCI config, MMIO registers, NVM words, PHY pages, and descriptor fields. They do not allocate runtime state.

## Dependencies And Integration
Included by `e1000_hw.h` and shared modules such as MAC, PHY, NVM, 82575-family, and I210 code. Many values are part of the hardware contract and must match datasheet-defined fields.

## Risks
Duplicate or wrong masks can silently program wrong hardware bits. NVM offsets and checksum constants are especially sensitive because they affect persistent flash/EEPROM contents. Interrupt and wake masks affect system power management and packet delivery.

## Test Signals
Broad compile coverage, link setup, WOL, NVM read/write/validate, PHY identification, interrupt enable/disable, VLAN filtering, EEE, PTP/time-sync, and Qav tests validate consumers of these definitions.
