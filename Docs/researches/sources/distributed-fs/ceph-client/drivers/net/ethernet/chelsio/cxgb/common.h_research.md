# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/common.h

## Purpose
`common.h` is the central shared header for the Chelsio T1 `cxgb` driver. It defines adapter identity, board and chip enumerations, adapter/link/port parameter structures, feature macros, common inline helpers, and prototypes for TPI access, interrupts, link negotiation, EEPROM, and software/hardware module initialization.

## Important APIs, Types, and Constants
Important constants include `DRV_DESCRIPTION`, `DRV_NAME`, `CH_DEVICE`, max port/MTU/TCB sizes, invalid link markers, PM3393/VSC7326 max frame sizes, pause/loopback capability bits, board ids, Terminator chip versions, MAC/PHY ids, pause flags, and revision ids. Key types are `adapter_t`, `struct t1_rx_mode`, `struct sge_params`, `struct chelsio_pci_params`, `struct tp_params`, `struct mc5_params`, `struct adapter_params`, `struct link_config`, `struct port_info`, `struct adapter`, and `struct board_info`.

## Control Flow and Integration
This header underpins most T1 driver objects named by `cxgb/Makefile`. `struct adapter` ties PCI/MMIO, registered/open netdev maps, params, SGE/ESPI/TP submodules, NAPI, per-port MAC/PHY/link state, work/timer state, and locks into one driver object. Inline helpers classify ASIC/chip revisions, VLAN/TSO capability, 10G capability, port iteration, board info access, and core clock conversion. Function prototypes expose cross-module operations implemented in support files.

## State and Persistence
The structures describe runtime in-memory state for each adapter and port. Hardware state is accessed through MMIO registers, TPI operations, EEPROM reads, and submodule init functions. Persistent hardware/board data can be read from serial EEPROM, but this header only declares the access path.

## Dependencies and Risks
The header depends on Linux module, netdevice, PCI, ethtool, VLAN, MDIO, CRC32, slab, I/O, and PCI id APIs. Risks include shared struct layout changes affecting many driver modules, stale capability bit definitions relative to ethtool link modes, locking contract ambiguity between `tpi_lock`, `work_lock`, `mac_lock`, and `async_lock`, and revision helpers incorrectly gating offloads.

## Test Signals
Build all cxgb objects, probe supported board ids, exercise TPI read/write paths, link negotiation, EEPROM board revision reads, module init/free paths, VLAN/TSO capability on T1B versus later chips, stats timer/work behavior, and interrupt enable/disable/slow-handler paths.
