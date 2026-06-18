# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_main.c

## Purpose

`cxgb3_main.c` is the primary Linux PCI/netdevice driver for Chelsio T3 1/10GbE adapters. It owns module registration, PCI probe/remove, netdev creation, SGE queue setup, interrupt strategy selection, link/MAC/PHY state transitions, firmware and TP SRAM loading, sysfs/ethtool/private ioctl control surfaces, periodic health work, fatal-error recovery, and the bridge from normal Ethernet ports to the T3 offload device. In this distributed-fs source tree it is infrastructure code: Ceph does not call it directly, but any workload using these NICs depends on its link stability, DMA setup, interrupt recovery, and optional TCP/iSCSI/RDMA offload behavior.

## Important APIs, types, and functions

- Module and PCI registration: `cxgb3_init_module()`, `cxgb3_cleanup_module()`, `driver`, and `cxgb3_pci_tbl[]` register the `pci_driver` and supported Chelsio PCI IDs.
- Probe/remove lifecycle: `init_one()` enables the PCI function, requests BARs, sets a 64-bit DMA mask, maps MMIO registers, allocates `struct adapter` plus per-port `struct net_device`/`struct port_info`, calls `t3_prep_adapter()`, registers netdevs, initializes iSCSI MAC aliases, selects MSI-X/MSI/INTx, sizes queue sets, and creates sysfs attributes. `remove_one()` reverses registration, offload state, SGE resources, MSI state, mappings, and allocations.
- Netdev operations: `cxgb_netdev_ops` wires `cxgb_open()`, `cxgb_close()`, `t3_eth_xmit`, `cxgb_get_stats()`, `cxgb_set_rxmode()`, `cxgb_ioctl()`, `cxgb_siocdevprivate()`, MTU/MAC/features handlers, and optional netpoll support.
- Adapter bring-up/tear-down: `cxgb_up()` performs one-time hardware init, firmware/TP version checks and upgrades, SGE qset allocation, RSS, NAPI, interrupts, TP parity initialization, and packet scheduler binding. `cxgb_down()` stops SGE, disables interrupts, releases IRQs, and quiesces NAPI.
- Link and PHY handling: `link_start()`, `t3_os_link_changed()`, `t3_os_link_fault()`, `t3_os_phymod_changed()`, `check_link_status()`, `ext_intr_task()`, `t3_os_ext_intr_handler()`, and `t3_os_link_fault_handler()` translate hardware/PHY events into MAC enable/disable, carrier updates, PHY power, TX FIFO drain mode, and logs.
- Offload entry points: `offload_open()`, `offload_close()`, `offload_tx()`, `init_smt()`, `write_smt_entry()`, `bind_qsets()`, `send_pktsched_cmd()`, and calls into `cxgb3_adapter_ofld()`, `cxgb3_offload_activate()`, `cxgb3_add_clients()`, `cxgb3_event_notify()`, and `cxgb3_offload_deactivate()`.
- User control surfaces: sysfs attributes `cam_size`, `nfilters`, `nservers`, offload scheduler attributes `sched0` through `sched7`, ethtool ops for stats/registers/EEPROM/link/rings/coalescing/pause, and `SIOCCHIOCTL` private ioctls for queue sets, firmware loading, MTU table, PM memory, memory readout, and trace filters.
- Error recovery: PCI EEH callbacks `t3_io_error_detected()`, `t3_io_slot_reset()`, `t3_io_resume()`, plus `t3_fatal_err()`, `fatal_error_task()`, `t3_adapter_error()`, `t3_reenable_adapter()`, and `t3_resume_ports()`.

## Control flow

The cold path starts in `cxgb3_init_module()`, which initializes the offload CPL dispatch layer and registers the PCI driver. `init_one()` is invoked per PCI function and constructs adapter/port state without fully initializing the chip for traffic. Full hardware initialization is deferred until the first port or offload device opens. During `cxgb_open()`, if `open_device_map` is empty, `cxgb_up()` checks firmware/TP SRAM versions, upgrades if needed, calls `t3_init_hw()`, configures DDP page size, allocates SGE queue sets, applies VLAN mode, sets RSS, adds NAPI once, starts SGE timers, requests IRQs, enables NAPI/SGE/interrupts, initializes TP parity on eligible offload adapters, and binds queue sets to packet schedulers. The port then starts MAC/PHY link, enables port interrupts, starts TX queues, schedules periodic work, and notifies offload clients.

The close path clears port state and only tears down adapter-wide resources when no port and no offload device remain open. `__cxgb_close()` disables XGM/port interrupts, stops TX, powers down PHY, clears carrier, disables MAC, clears the port bit in `open_device_map`, cancels adapter check work if no ports remain, and calls `cxgb_down()` only when the device map is zero. `offload_open()` and `offload_close()` use a separate `OFFLOAD_DEVMAP_BIT` in the same bitmap, so Ethernet and offload lifecycle are interlocked.

Periodic work runs through the private `cxgb3_wq` to avoid rtnl/linkwatch deadlocks. `t3_adap_check_task()` polls link for PHYs without IRQ support, accumulates MAC stats, applies a T3B2 MAC watchdog reset path, records RX FIFO overflow and freelist-empty events, and reschedules itself while any port is active. External PHY interrupts are deferred from interrupt context to `ext_intr_task()` because MDIO operations can sleep under a mutex.

## State and persistence behavior

Persistent kernel state is held in `struct adapter`, per-port `struct port_info`, `open_device_map`, `registered_device_map`, adapter flags such as `FULL_INIT_DONE`, `NAPI_INIT`, `USING_MSIX`, `USING_MSI`, `QUEUES_BOUND`, and `TP_PARITY_INIT`, SGE queue parameters, MAC stats, link config, and MC5/TP parameters. Firmware and TP SRAM images are loaded through the kernel firmware API and written to hardware, but this file does not persist driver state to disk beyond optional EEPROM/VPD writes via ethtool. `set_eeprom()` requires the expected `EEPROM_MAGIC`, handles unaligned writes by read-modify-write, disables SEEPROM write protection, writes PCI VPD, then restores protection.

Runtime state is concurrency-sensitive: rtnl serializes most user-visible configuration changes, `work_lock` synchronizes work tasks and interrupt mask updates, `stats_lock` protects MAC and firmware/version stat reads, NAPI disable waits for RX handlers, and the private workqueue serializes deferred tasks. A `nofail_skb` reserve buffer is maintained for management requests in memory-pressure paths.

## Dependencies and integration points

This file depends heavily on `common.h` hardware helpers (`t3_*`), `regs.h` register offsets/bitfields, `cxgb3_ioctl.h` command structs, `cxgb3_offload.h` offload lifecycle, `cxgb3_ctl_defs.h`, `t3_cpl.h`, and `firmware_exports.h`. It integrates with kernel PCI, netdevice, ethtool, MDIO, VLAN, firmware loader, workqueue, NAPI, netpoll, rtnetlink, sysfs, and PCI error recovery APIs. It declares firmware names under `cxgb3/` and expects matching T3 firmware, TP SRAM, and EDC firmware blobs.

## Risks and edge cases

- Probe cleanup uses shared labels; any future allocation inserted into `init_one()` must be added to all failure paths in reverse order.
- `cxgb_open()` returns immediately if `netif_set_real_num_rx_queues()` fails after setting the port open bit and possibly starting adapter/offload state; this is a notable partial-open risk to audit if behavior changes.
- Firmware/TP upgrade failure is logged but `cxgb_up()` continues after version checks unless later hardware init fails; compatibility assumptions depend on lower-level `t3_*` checks.
- Many ioctls require `FULL_INIT_DONE` to be clear before queue/memory sizing changes. Missing this guard in new controls could corrupt live DMA or offload contexts.
- Offload and Ethernet share `open_device_map`; bugs in bit clearing can leave interrupts/SGE resources active or tear them down under users.
- Private ioctls expose raw firmware load and memory read paths gated by capabilities, so copy bounds and privilege checks are critical.
- `get_regs()` intentionally skips clear-on-read MAC statistics; test expectations should not assume full register dumps include those counters.
- Fatal-error recovery stops DMA and queues reset work; regressions here can deadlock with rtnl, workqueue flushing, or PCI error callbacks.

## Test signals

Useful validation includes PCI probe/remove on T3 hardware or emulation, open/close cycles across all ports and offload enabled/disabled, MSI-X/MSI/INTx fallback coverage, ethtool stats/register/EEPROM/link/ring/coalesce paths, sysfs filter/server/scheduler attributes, MTU/MAC/VLAN feature changes while running, firmware missing/corrupt/upgrade cases, forced link fault and PHY interrupt events, netpoll if configured, private ioctl boundary tests, and injected SGE/MC5/TP fatal errors to verify reset and port resume behavior.
