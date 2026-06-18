# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cxgb2.c

## Purpose
`cxgb2.c` is the PCI and Linux netdevice front end for the Chelsio T1/T2 `cxgb` Ethernet driver. It binds supported PCI IDs, allocates one shared `struct adapter` plus one netdevice per physical port, wires netdevice and ethtool operations, starts and stops the shared DMA/interrupt hardware, and bridges link/MAC/PHY/SGE/TP/ESPI helpers into normal kernel networking operations.

## Important APIs, Types, and Functions
The key external entry points are the PCI driver's `init_one()` and `remove_one()`, exported through `module_pci_driver(cxgb_pci_driver)`. Netdevice operations are collected in `cxgb_netdev_ops`, with `cxgb_open()`, `cxgb_close()`, `t1_start_xmit()` from `sge.c`, `t1_get_stats()`, MTU/MAC/rx-mode setters, MII ioctl support, and feature negotiation. `t1_ethtool_ops` exposes driver info, register dumps, ring sizing, coalescing, EEPROM reads, link settings, pause parameters, and statistics.

Important internal helpers include `cxgb_up()` and `cxgb_down()` for card-wide hardware activation, `link_start()` and `t1_link_negotiated()` for MAC/PHY link transitions, `enable_hw_csum()` for TP checksum offload, `mac_stats_task()` for periodic MAC counter accumulation, and `t1_clock()`/`bit_bang()` for T1B clock programming through Elmer0 GPIO.

## Control Flow
Probe enables the PCI function, verifies BAR0 memory, sets a 64-bit DMA mask, requests regions, maps MMIO, determines board revision, initializes locks/work, allocates per-port netdevices, assigns features and ethtool/netdev ops, creates software modules through `t1_init_sw_modules()`, and registers each port. Open enables NAPI, performs first-use hardware initialization through `t1_init_hw_modules()`, requests a threaded IRQ, starts SGE, enables interrupts, starts the port MAC/PHY, and schedules MAC stats. Close stops the queue, disables NAPI and MAC directions, clears the port from `open_device_map`, cancels stats once all ports are down, and tears down SGE/IRQ/MSI when no port remains open. Remove unregisters registered netdevices, frees modules, unmaps MMIO, frees netdevices, releases PCI resources, disables the device, and performs a software reset through PCI config space.

## State and Persistence
State is runtime-only kernel driver state. `adapter->flags` tracks full hardware initialization, `open_device_map` tracks active ports, `registered_device_map` tracks successfully registered netdevices, `params` carries board/chip/SGE/PCI configuration, and `msg_enable` stores ethtool message level. Per-port link state lives in `struct port_info` and `struct link_config`; netdevice stats are recomputed from MAC counters. Module parameters `dflt_msg_enable`, `t1powersave`, and `disable_msi` influence runtime behavior but are not persisted by this file.

## Dependencies and Integration Points
This file depends on the Linux PCI, netdevice, ethtool, NAPI, IRQ, DMA, VLAN, MII, and workqueue APIs. Driver-internal dependencies include `common.h` for adapter/board state, `regs.h` register constants, `gmac.h` MAC operations, `cphy.h` PHY operations, `sge.h` DMA/interrupt/TX/RX, `tp.h` checksum offload, `espi.h` ESPI counters, and `elmer0.h` GPIO/TPI addresses. It integrates with `subr.c` for board discovery/module initialization/slow interrupt handling and with the MAC/PHY/SGE modules researched in this group.

## Risks
The main risks are shared-card lifecycle races across multiple netdevices, especially NAPI enable/disable and card-wide IRQ/SGE ownership while only some ports are open. Error unwinding in `init_one()` must free partially allocated per-port devices without leaking the first netdevice that embeds the adapter. Ettool ring sizing is rejected after `FULL_INIT_DONE`, so runtime resizing assumptions can fail. `t1_clock()` performs timing-sensitive GPIO serial programming under `tpi_lock`; interrupted or wrong-mode use can misprogram clocks. EEPROM read offsets rely on a small local buffer and must stay bounded by ethtool's length checks.

## Test Signals
Useful signals include PCI probe/remove, module load/unload, multi-port open/close permutations, MSI and shared-IRQ operation, NAPI traffic, link up/down reporting, ethtool stats/register/eeprom/ring/coalesce/link/pause operations, MTU and MAC address changes, VLAN feature toggles, netpoll if enabled, T1B power-save clock mode coverage, and fault-injection of probe failures after each allocation stage.
