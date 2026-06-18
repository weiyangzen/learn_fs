# subset-b-004395 research

Grouped research for Chelsio T3 `cxgb3` driver sources under `sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.c

## Purpose

`cxgb3_offload.c` implements the Chelsio T3 offload service layer used by upper-layer protocol clients such as iSCSI and RDMA. It manages offload client registration, active offload device registration, TID/STID/ATID tables, CPL opcode dispatch, neighbor/redirect notifications, RDMA/iSCSI control queries, and activation/deactivation of per-adapter offload state. It is the main software bridge between the generic Ethernet adapter in `cxgb3_main.c`, the firmware work-request protocol, the L2 table in `l2t.c`, and external protocol clients.

## Important APIs, types, and functions

- Client registry: `cxgb3_register_client()`, `cxgb3_unregister_client()`, `cxgb3_add_clients()`, `cxgb3_remove_clients()`, and `cxgb3_event_notify()` maintain `client_list` and call client `add`, `remove`, and `event_handler` callbacks under `cxgb3_db_lock`.
- Device registry: `register_tdev()`, `unregister_tdev()`, `cxgb3_adapter_ofld()`, and `cxgb3_adapter_unofld()` maintain `ofld_dev_list`, initialize `struct t3cdev` callbacks, set dummy receive/neigh handlers before activation, and assign T3A/T3B/T3C type from adapter revision.
- Activation: `cxgb3_offload_activate()` allocates `struct t3c_data`, queries `tdev->ctl` for limits/ranges/MTUs/L2T capacity, allocates `l2t_data`, initializes TID tables, installs RCU L2 data, switches `dev->recv` to `process_rx`, sets `dev->neigh_update`, registers the netevent notifier once, and adds the adapter to `adapter_list`.
- Deactivation: `cxgb3_offload_deactivate()` removes the adapter from the global adapter list, unregisters the netevent notifier when no adapters remain, frees TID maps, clears `T3C_DATA`, removes RCU L2 data with `call_rcu()`, frees reserve skb and `struct t3c_data`.
- Control dispatch: `cxgb_offload_ctl()` handles firmware work-request sizes, TID/STID ranges, L2T capacity, MTUs, MAC-to-interface lookup, DDP params, port list, iSCSI params, RDMA params/context ops/memory/MIB, RX page info, iSCSI IPv4 address, and embedded firmware/TP versions.
- TID services: `cxgb3_alloc_atid()`, `cxgb3_free_atid()`, `cxgb3_insert_tid()`, `cxgb3_remove_tid()`, `cxgb3_queue_tid_release()`, and `t3_process_tid_release_list()` allocate active-open IDs, install hardware TID contexts, and send deferred `CPL_TID_RELEASE` work requests.
- CPL dispatch: `t3_register_cpl_handler()`, `process_rx()`, `do_stid_rpl()`, `do_hwtid_rpl()`, `do_cr()`, `do_act_open_rpl()`, `do_act_establish()`, `do_abort_req_rss()`, `do_term()`, `do_trace()`, and simple write-reply handlers map firmware CPL opcodes to per-client handlers or built-in replies.
- Neighbor integration: `nb_callback()`, `cxgb_neigh_update()`, `cxgb_redirect()`, `set_l2t_ix()`, and `is_offloading()` map netevent neighbor/redirect notifications to L2T updates and optional client redirect callbacks.

## Control flow

At module initialization, `cxgb3_offload_init()` fills every CPL opcode slot with `do_bad_cpl()` and registers built-in dispatch handlers for SMT/L2T/RTE replies, passive/active open, established/close/abort/data/RDMA/iSCSI/trace events. During PCI probe, `cxgb3_adapter_ofld()` registers an inactive `t3cdev` with dummy receive and neighbor callbacks. During `offload_open()` in `cxgb3_main.c`, `cxgb3_offload_activate()` builds offload runtime state and then `cxgb3_add_clients()` notifies all registered clients.

Receive flow enters `process_rx()` through `t3cdev.recv`. The SGE path has encoded the CPL opcode in `skb->csum` and the hardware TID in `skb->priority`; `process_rx()` indexes `cpl_handlers`, invokes the selected handler, logs unknown TIDs when validation is enabled, and frees the skb if the handler returns `CPL_RET_BUF_DONE`. Most CPL handlers look up a `struct t3c_tid_entry` in the active, server, or hardware TID tables and then call the corresponding client handler with the stored context. If no client/context/handler exists, the packet is logged as clientless and treated as a bad message.

Transmit/control flow uses `cxgb3_ofld_send()`, which disables bottom halves around `dev->send()`. TID release is usually sent immediately from `cxgb3_remove_tid()` for non-T3A adapters; if atomic allocation fails, the TID entry is chained through `ctx` into `tid_release_list` and `t3_process_tid_release_list()` later emits `CPL_TID_RELEASE` work requests using a reserve skb if needed.

Neighbor flow is driven by the kernel netevent notifier. `NETEVENT_NEIGH_UPDATE` calls `t3_l2t_update()` for devices belonging to offloading adapters. `NETEVENT_REDIRECT` allocates a new L2T entry for the redirected destination, walks all active hardware TIDs, asks each client `redirect()` callback whether to update the TCB, and sends `CPL_SET_TCB_FIELD` with the new L2T index when requested.

## State and persistence behavior

Global volatile state includes `client_list`, `ofld_dev_list`, `adapter_list`, `cxgb3_db_lock`, and `adapter_list_lock`. Per-active-offload state is stored in `struct t3c_data` via `T3C_DATA(tdev)`, including MTU table pointer, work-request limits, `struct tid_info`, TID-release work item/list/lock, reserve skb, and `l2opt` RCU pointer to `struct l2t_data`. TID maps are allocated as one `kvzalloc()` block partitioned into hardware TID, server TID, and active-open TID arrays with free lists for STIDs/ATIDs. No state persists across driver unload or offload deactivation; hardware-visible TID/L2T/TCB state is programmed through firmware work requests and discarded/reset through adapter lifecycle.

Concurrency uses a mutex for client/device callbacks, rwlock for adapter lookup from netdevice, per-TID free-list spinlocks, `tid_release_lock`, RCU for L2T pointer replacement, atomics for active hardware TID count, and bottom-half disabling around offload send paths.

## Dependencies and integration points

This file depends on `common.h`/`t3cdev.h` adapter definitions, `regs.h` register constants, `cxgb3_ctl_defs.h` control request structs, `cxgb3_defs.h`, `l2t.h`, `t3_cpl.h` CPL layouts/opcodes, and `firmware_exports.h` work-request opcodes and queue/TID constants. It integrates with Linux neighbour and redirect netevents, VLAN/bond upper-device lookup, sk_buff control blocks, workqueues, vmalloc-backed allocation, RCU cleanup, and exported symbols consumed by offload protocol modules.

## Risks and edge cases

- Client callbacks are invoked while `cxgb3_db_lock` is held; callbacks must not re-enter registration paths or block indefinitely.
- CPL opcode extraction depends on SGE-specific use of `skb->priority` and `skb->csum`; changes in receive plumbing must preserve this contract.
- `process_rx()` trusts `cpl_handlers[opcode]`; opcode validity depends on `NUM_CPL_CMDS` and encoded values from SGE/firmware.
- `cxgb_redirect()` scans every hardware TID under redirect events, which can be expensive for large TCAM sizes.
- `set_l2t_ix()` uses `GFP_ATOMIC`; allocation failure logs and drops the TCB update, leaving clients with software redirect state but stale hardware L2T index.
- `cxgb3_offload_deactivate()` assumes offload clients have been removed and release work flushed by the caller. Lifetime bugs could leave client contexts referenced in TID tables during `free_tid_maps()`.
- `cxgb3_remove_tid()` uses `cmpxchg()` only for T3A; other revisions clear `ctx` after sending or queueing release, so ordering with delayed client CPL processing is part of the documented race model.
- `get_iff_from_mac()` handles VLAN and bond master lookup under RCU, but returns a `net_device *` without taking a reference; callers must respect expected transient lifetime.

## Test signals

Validation should cover offload activate/deactivate loops, client register/unregister before and after activation, CPL dispatch for every built-in opcode class, clientless/bad CPL logging, ATID exhaustion and free-list reuse, TID removal under GFP_ATOMIC allocation failure, deferred release work flushing, iSCSI/RDMA control requests when offload is stopped vs running, netevent neighbor update and redirect behavior, RCU teardown under concurrent lookup, and `cxgb3_ofld_send()` behavior from process and softirq contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.h

## Purpose

`cxgb3_offload.h` defines the public in-driver interface for the Chelsio T3 offload layer. It declares activation/deactivation functions, client registration callbacks, event IDs, CPL handler signatures and return flags, TID table structures, `struct t3c_data`, and helper accessors used by upper-layer offload clients and sibling driver files. It is the contract that allows `cxgb3_main.c`, `cxgb3_offload.c`, `l2t.c`, and protocol clients to share T3 offload state safely.

## Important APIs, types, and functions

- Lifecycle declarations: `cxgb3_offload_init()`, `cxgb3_adapter_ofld()`, `cxgb3_adapter_unofld()`, `cxgb3_offload_activate()`, `cxgb3_offload_deactivate()`, and `cxgb3_set_dummy_ops()`.
- Device conversion: `dev2t3cdev()` maps a netdevice to its owning T3 offload device.
- Client management: `cxgb3_register_client()`, `cxgb3_unregister_client()`, `cxgb3_add_clients()`, `cxgb3_remove_clients()`, and `cxgb3_event_notify()`.
- `struct cxgb3_client`: client name, adapter add/remove callbacks, CPL handler vector, redirect callback, list node, and event callback.
- Event enum: `OFFLOAD_STATUS_UP`, `OFFLOAD_STATUS_DOWN`, `OFFLOAD_PORT_DOWN`, `OFFLOAD_PORT_UP`, `OFFLOAD_DB_FULL`, `OFFLOAD_DB_EMPTY`, and `OFFLOAD_DB_DROP`.
- TID APIs: `cxgb3_alloc_atid()`, `cxgb3_free_atid()`, `cxgb3_insert_tid()`, `cxgb3_queue_tid_release()`, and `cxgb3_remove_tid()`.
- CPL dispatch contract: `cxgb3_cpl_handler_func`, `cpl_handler_func`, `cplhdr()`, `t3_register_cpl_handler()`, priority constants, and return flags `CPL_RET_BUF_DONE`, `CPL_RET_BAD_MSG`, and `CPL_RET_UNKNOWN_TID`.
- TID storage: `struct t3c_tid_entry`, `union listen_entry`, `union active_open_entry`, `struct tid_info`, and `struct t3c_data`.
- Accessor macro: `T3C_DATA(dev)` stores a `struct t3c_data *` in `t3cdev.l4opt`.

## Control flow

The header itself has no executable control flow beyond `cplhdr()`, but it defines the expected sequence for offload consumers. A client registers a `struct cxgb3_client`; when an adapter activates, the driver calls the client's `add()` callback with a `struct t3cdev *`. The client allocates ATIDs or inserts TIDs through the TID APIs, sends work requests through `cxgb3_ofld_send()` declared in `l2t.h`, and receives firmware CPLs through handler vectors indexed by CPL opcode. During connection teardown the client calls `cxgb3_remove_tid()` or release helpers, and during adapter or port events it receives event notifications.

## State and persistence behavior

The main state schema is `struct t3c_data`, which is per-active `t3cdev` and contains work-request limits, MTU table references, TID maps, release-work state, reserve skb, and release-incomplete flag. `struct tid_info` partitions dynamic TID storage into hardware TIDs, server/listen TIDs, and active-open TIDs, with atomics and spinlocks for concurrent use. This header defines volatile runtime state only; it does not describe any on-disk persistence. The `T3C_DATA()` macro is type-punning storage over `t3cdev.l4opt`, so layout compatibility with `struct t3cdev` is essential.

## Dependencies and integration points

The header includes Linux list and skb definitions, `l2t.h`, `t3cdev.h`, and `t3_cpl.h`. It integrates with `cxgb3_offload.c` as the implementation, `cxgb3_main.c` as lifecycle caller, `l2t.c` for L2 table operations, and external protocol modules that register `cxgb3_client` instances. It also exposes exported functions implemented in `cxgb3_offload.c`.

## Risks and edge cases

- Client handler arrays must be sized and indexed according to `NUM_CPL_CMDS`; the header does not enforce bounds for client vectors.
- `T3C_DATA()` uses pointer casting into `t3cdev.l4opt`; changes to `t3cdev` type or constness can silently break this accessor.
- `ctx` in `struct t3c_tid_entry` is overloaded by the release queue implementation as a next pointer after client removal, so clients must not access released entries.
- The cacheline alignment choices in `struct tid_info` are performance and correctness hints for concurrent allocation; refactoring field order could affect lock contention.
- Event IDs are unversioned enum values; external clients must be recompiled together with the driver if values change.

## Test signals

Header-level validation is compile-time: all offload clients should build without type warnings, handler signatures should match, exported symbols should resolve, and sparse/lockdep review should check use of TID APIs in softirq and process contexts. ABI-sensitive changes should be tested by building iSCSI/RDMA clients that use `cxgb3_client`, `T3C_DATA()`, CPL handler arrays, and TID allocation/removal paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/firmware_exports.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/firmware_exports.h

## Purpose

`firmware_exports.h` defines the firmware-facing constants used by the T3 driver and offload clients: work-request opcodes, management opcodes, maximum WR size/count, firmware queue/context ranges, reserved TID/token starts, and firmware version bitfield helpers. It is a shared hardware/firmware ABI description, not an implementation file.

## Important APIs, types, and functions

- Work-request opcodes: `FW_WROPCODE_FORWARD`, `FW_WROPCODE_BYPASS`, tunnel TX/RX, ULPTX data/memory/packet/invalidate, offload close/abort/TX data/ACK/get-TCB, RDMA operations, management, and SGE egress context read.
- Management opcode: `FW_MNGTOPCODE_PKTSCHED_SET`, used by `cxgb3_main.c` packet scheduler binding.
- WR sizing: `FW_WR_SIZE`, `FW_T3_WR_NUM`, `FW_N3_WR_NUM`, and selected `FW_WR_NUM`.
- Firmware context ranges: `FW_TUNNEL_NUM`, `FW_TUNNEL_SGEEC_START`, `FW_TUNNEL_TID_START`, `FW_CTRL_NUM`, `FW_CTRL_SGEEC_START`, `FW_CTRL_TID_START`, `FW_OFLD_NUM`, `FW_OFLD_SGEEC_START`, `FW_RI_NUM`, `FW_RI_SGEEC_START`, `FW_RI_TID_START`, `FW_RX_PKT_NUM`, `FW_RX_PKT_TID_START`, and `FW_WRC_NUM`.
- Version fields: `S_`, `M_`, `V_`, and `G_` macros for firmware type, major, minor, and micro components.

## Control flow

This header has no runtime control flow. Its constants are consumed when other files construct firmware work requests. For example, `cxgb3_main.c` uses `FW_WROPCODE_FORWARD` for SMT/L2T/RTE/TCB management CPLs and `FW_WROPCODE_MNGT` plus `FW_MNGTOPCODE_PKTSCHED_SET` for scheduler commands; `cxgb3_offload.c` uses offload abort and RDMA context constants; `l2t.c` uses `FW_WROPCODE_FORWARD` for L2 table writes.

## State and persistence behavior

The header defines static ABI values only. Those values become hardware/firmware state when written into SGE contexts, work-request headers, or version parsing logic. No mutable or persistent software state is declared here.

## Dependencies and integration points

It is included by `cxgb3_main.c`, `cxgb3_offload.c`, and `l2t.c`. It also aligns with firmware binaries requested by `cxgb3_main.c` and with CPL/work-request structures in `t3_cpl.h`. The queue and TID constants must match firmware expectations exactly because hardware completions and offload clients depend on these numeric ranges.

## Risks and edge cases

- Several macro names contain historical spelling mistakes such as `FW_WROPOCDE_ULPTX_DATA_SGL` and `FW_WROPOCDE_RSVD`; code must use the existing spellings or compatibility aliases would be needed.
- Changing any opcode or context start value is firmware ABI-breaking and can misroute completions or corrupt hardware context state.
- `FW_WR_NUM` varies under `N3`; builds must verify the intended firmware target.
- Version extraction macros assume packed 32-bit version fields with fixed bit widths; mismatched firmware encoding would produce misleading ethtool driver info and upgrade checks.

## Test signals

Validation is primarily integration-based: compile all users, inspect generated work requests for correct opcodes, run firmware version reporting through ethtool, verify packet scheduler management requests, RDMA control QP setup using `FW_RI_*`, and confirm offload queue/TID ranges match observed firmware behavior on T3/N3 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/firmware_exports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.c

## Purpose

`l2t.c` implements the Chelsio T3 Layer 2 Table used by offload connections to map next-hop IPv4 neighbours to hardware L2 table indices. It allocates and reuses L2T entries, tracks neighbour MAC/VLAN/SMT state, queues offload packets while ARP/neighbor resolution is pending, emits `CPL_L2T_WRITE_REQ` firmware work requests, and updates entries on kernel neighbour events.

## Important APIs, types, and functions

- `t3_init_l2t()` allocates a flexible `struct l2t_data` with `l2t_capacity` entries, initializes entry state, locks, queues, indices, free count, and rover.
- `t3_l2t_get()` looks up or allocates an L2T entry for a `dst_entry`/destination address/netdevice. It hashes by IPv4 neighbour primary key and ifindex, accounts for SMT port, takes a neighbour reference, inserts new entries into the hash chain, and sets initial `RESOLVING` state.
- `t3_l2t_send_slow()` handles non-VALID entries: revalidates STALE entries, queues packets for RESOLVING entries, triggers `neigh_event_send()`, and on successful resolution writes hardware state then drains the queued packets.
- `t3_l2t_update()` handles host neighbour changes: finds matching entries, replaces neighbour references, transitions state based on NUD flags, writes new L2T hardware entries when MAC changed or resolution completed, and handles failed resolution queues.
- `t3_l2e_free()` releases neighbour references when refcount reaches zero and increments free entry count.
- Helpers: `setup_l2e_send_pending()`, `alloc_l2e()`, `reuse_entry()`, `handle_failed_resolution()`, `neigh_replace()`, `arpq_enqueue()`, `arp_hash()`, and `vlan_prio()`.

## Control flow

A client obtains an entry with `t3_l2t_get()`, usually while preparing an offload connection or redirect. If the entry is already in the hash table for the same destination/ifindex/SMT port, `l2t_hold()` increments the refcount and `reuse_entry()` refreshes state on a 0-to-1 transition. If no entry exists, `alloc_l2e()` scans for a zero-ref entry, removes stale hash membership if necessary, and returns it for initialization.

When sending through `l2t_send()` from `l2t.h`, VALID entries go directly to `cxgb3_ofld_send()`. Other states enter `t3_l2t_send_slow()`: STALE entries kick neighbour revalidation and then optimistically become VALID, RESOLVING entries enqueue the skb and trigger ARP/neighbor resolution. Once resolution is available, `setup_l2e_send_pending()` builds a `CPL_L2T_WRITE_REQ`, copies the neighbour MAC into both software and firmware request state, sends the control request, drains `arpq`, and marks the entry VALID.

Neighbour notifications from `cxgb3_offload.c` call `t3_l2t_update()`. On NUD failure, queued packets are moved to a local queue and each skb's optional `arp_failure_handler` is invoked; if no failure handler exists, the packet is sent anyway. On connected/stale neighbour states, the hardware table is written and pending packets are sent.

## State and persistence behavior

All state is volatile and bound to an active `t3cdev` via the RCU `l2opt` pointer. `struct l2t_data` contains the table size, allocation rover, free count, table rwlock, RCU head, and flexible array of `struct l2t_entry`. Each entry stores software state (`VALID`, `STALE`, `RESOLVING`, `UNUSED`), hardware index, IPv4 address, ifindex, SMT index, VLAN TCI or `VLAN_NONE`, neighbour pointer with held reference, hash-chain pointers, pending skb queue, spinlock, refcount, and cached destination MAC. There is no disk persistence; hardware state is synchronized by firmware work requests.

The locking hierarchy is documented in the file: table rwlock nests outside entry locks. Lookups/allocations take the table lock; entry mutation takes the entry spinlock; updates can take the table lock as reader while multiple entries update in parallel. Refcounts and `nfree` are atomic, but correctness still depends on obeying the table/entry lock ordering.

## Dependencies and integration points

`l2t.c` depends on Linux `sk_buff`, `net_device`, VLAN helpers, Jenkins hash, `struct neighbour`, Chelsio `common.h`, `t3cdev.h`, `cxgb3_defs.h`, `l2t.h`, `t3_cpl.h`, and `firmware_exports.h`. It integrates with `cxgb3_offload.c` for neighbour events, `cxgb3_ofld_send()` for firmware work-request transmission, and offload clients that attach ARP failure handlers in skb control blocks.

## Risks and edge cases

- Hashing uses `d->nentries - 1` as a mask, so L2T capacity is expected to be a power of two. Non-power-of-two capacities would bias or truncate buckets.
- `addr = *(u32 *)neigh->primary_key` assumes IPv4-sized neighbour keys; this table is not a generic IPv6 neighbour map.
- If allocation of the CPL L2T write skb fails during resolution, queued packets remain pending until another packet retries or a neighbour update arrives.
- `handle_failed_resolution()` sends packets without a failure handler even after ARP failure; the comment questions whether this should be abandoned.
- `t3_l2e_free()` increments `nfree` after refcount reaches zero, while entries may remain in the hash table for reuse; allocation and hold paths must preserve the documented locking protocol.
- VLAN handling stores VLAN ID but `vlan_prio()` reads priority bits from `e->vlan`; current initialization from `vlan_dev_vlan_id()` does not include priority bits.

## Test signals

Tests should exercise entry allocation/reuse/free, hash collision chains, zero-ref stale hash removal, send path through VALID/STALE/RESOLVING states, ARP success and failure with and without skb failure handlers, neighbour MAC changes, VLAN and non-VLAN devices, redirect-driven L2T references, memory allocation failure for control skb, concurrent lookup/update/free under lockdep, and teardown through RCU after offload deactivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.h

## Purpose

`l2t.h` declares the Chelsio T3 offload Layer 2 Table data structures and helper API. It defines entry states, table/entry layout, skb ARP-failure callback storage, RCU accessor, TCB bitfield macros for the L2T index, function prototypes implemented in `l2t.c`, and fast inline send/hold/release helpers used by offload clients and redirect logic.

## Important APIs, types, and functions

- Entry states: `L2T_STATE_VALID`, `L2T_STATE_STALE`, `L2T_STATE_RESOLVING`, and `L2T_STATE_UNUSED`.
- `struct l2t_entry`: state, hardware index, IPv4 address, ifindex, SMT index, VLAN, neighbour pointer, hash bucket/chain links, pending ARP queue, entry lock, refcount, and destination MAC.
- `struct l2t_data`: number of entries, allocation rover, free count, table rwlock, RCU head, and flexible `l2tab[]`.
- `struct l2t_skb_cb` and `set_arp_failure_handler()` store an optional ARP failure callback in `skb->cb`.
- `L2DATA(cdev)` dereferences `t3cdev.l2opt` under RCU.
- TCB L2T index macros: `W_TCB_L2T_IX`, `S_TCB_L2T_IX`, `M_TCB_L2T_IX`, and `V_TCB_L2T_IX()`.
- Main functions: `t3_l2e_free()`, `t3_l2t_update()`, `t3_l2t_get()`, `t3_l2t_send_slow()`, `t3_init_l2t()`, and `cxgb3_ofld_send()`.
- Inline helpers: `l2t_send()`, `l2t_release()`, and `l2t_hold()`.

## Control flow

The header establishes the intended fast path: callers use `l2t_send()`, which sends immediately through `cxgb3_ofld_send()` when `e->state` is VALID and otherwise delegates to `t3_l2t_send_slow()`. References are managed with `l2t_hold()` on acquisition/reuse and `l2t_release()` on completion. `l2t_release()` enters an RCU read section, fetches current L2 data, decrements the entry refcount, and calls `t3_l2e_free()` when the refcount reaches zero and table data still exists.

## State and persistence behavior

The header defines volatile in-memory state only. L2T entries mirror hardware table entries but are not persistent. Lifetime is managed by atomic refcounts and RCU around the table pointer. The pending ARP queue is stored per entry as an skb queue and can hold offload packets until neighbour resolution completes or fails.

## Dependencies and integration points

It includes Linux spinlock and atomic definitions plus `t3cdev.h`. It forward-declares `struct neighbour` and `struct sk_buff`, and it is included by `cxgb3_offload.h`, `cxgb3_offload.c`, and `l2t.c`. Offload protocol clients use these declarations to bind connections to L2 entries and to release them safely.

## Risks and edge cases

- `l2t_send()` reads `e->state` without taking the entry lock for speed; state transitions must tolerate racing into the slow path.
- `l2t_release()` can call into free logic while only under RCU plus atomic refcount transition; table teardown must keep `l2t_data` alive through `call_rcu()`.
- `L2T_SKB_CB()` overlays `skb->cb`; callers must not conflict with other control-block users for the same skb.
- `l2t_hold()` decrements `nfree` only on a 0-to-1 transition; incorrect external refcount manipulation would corrupt free accounting.
- The flexible array uses `__counted_by(nentries)`, so compiler and allocation helpers must agree on the table length.

## Test signals

Build coverage should ensure all users agree on inline prototypes and that skb control block size is sufficient. Runtime tests should verify fast-path `l2t_send()`, slow-path delegation, hold/release free accounting, RCU teardown, ARP failure callback invocation, and lockdep-clean concurrent neighbour updates with active sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/mc5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/mc5.c

## Purpose

`mc5.c` initializes and handles interrupts for the Chelsio T3 MC5 TCAM block used by the TCP offload engine for connection/filter/server/routing lookup state. It detects TCAM part type and size, programs TCAM command registers for supported IDT parts, clears and masks TCAM arrays, partitions TCAM regions, enables parity/MBus mode, and escalates fatal MC5 parity errors to adapter reset.

## Important APIs, types, and functions

- TCAM command helpers: `mc5_cmd_write()`, `dbgi_wr_data3()`, and `mc5_write()` issue DBGI-mode TCAM commands and wait for completion through MC5 response status.
- Array initialization: `init_mask_data_array()` clears data array entries, initializes mask array entries, and applies special masks at the server/routing region boundary.
- Part-specific setup: `init_idt52100()` configures IDT 75P52100 latency, command opcodes, DBGI mode, LAR, SSRs, GMRs, SCR, and arrays. `init_idt43102()` configures IDT 75N43102 latency, commands, GMRs, SCR, and arrays.
- Mode switching: `mc5_dbgi_mode_enable()` puts MC5 into DBGI mode for direct TCAM programming; `mc5_dbgi_mode_disable()` restores M-Bus mode with compare/parity settings.
- Public init: `t3_mc5_init()` validates requested server/filter/route counts, resets TCAM, writes routing/filter/server partition registers, enables parity, selects part-specific init, and restores M-Bus mode.
- Interrupt handling: `t3_mc5_intr_handler()` reads MC5 interrupt cause, logs and increments stats for parity/search/region/unknown-command conditions, calls `t3_fatal_err()` on fatal parity classes, and clears causes.
- Preparation: `t3_mc5_prep()` reads `A_MC5_DB_CONFIG`, derives part type and TCAM size, adjusts for 144-bit mode, and stores adapter/mode/type/size in `struct mc5`.

## Control flow

`t3_mc5_prep()` runs during adapter preparation to populate static MC5 metadata from hardware registers. Later, `t3_mc5_init()` is called once protocol/offload sizing is known. It rejects unsupported route counts and overcommitted TCAM partition requests, resets the TCAM and waits for `F_TMRDY`, writes region boundary registers from the top of TCAM downward, primes DBGI address high registers to zero, enters DBGI mode, invokes the setup routine matching `mc5->part_type`, then exits DBGI mode. The part setup routines program different IDT command encodings and global mask registers but share the array clearing/masking helper.

During runtime, MC5 interrupts are delivered to `t3_mc5_intr_handler()`. Nonfatal counters are accumulated in `mc5->stats`; fatal parity causes trigger `t3_fatal_err()` on the adapter, which leads to traffic suspension and reset handling in `cxgb3_main.c`.

## State and persistence behavior

Software state lives in `struct mc5` fields supplied by `common.h`: adapter pointer, mode, part type, TCAM size, parity-enabled flag, and stats counters. Hardware state includes TCAM command registers, mask/data arrays, GMR/SCR/LAR/SSR registers, region boundary registers, parity and M-Bus configuration, and interrupt cause bits. All state is volatile hardware/driver runtime state; no disk persistence is involved.

## Dependencies and integration points

`mc5.c` includes `common.h` for adapter/MC5 types and hardware helper functions, and `regs.h` for MC5 register offsets/bitfields. It integrates with adapter initialization in lower-level common code and with fatal error handling in `cxgb3_main.c` via `t3_fatal_err()`. It also supports user-visible filter/server sizing controlled by `cxgb3_main.c` sysfs attributes before full initialization.

## Risks and edge cases

- Only part types `IDT75P52100` and `IDT75N43102` are supported; unknown TCAM types cause `-EINVAL`.
- `init_mask_data_array()` iterates over the entire TCAM in 72-bit units, so initialization time scales with TCAM size and any timeout leaves partially initialized arrays.
- `mc5_write()` returns `-1` rather than a standard errno on timeout; callers convert some but not all failures to `-EIO`.
- Region boundaries are calculated from `tcam_size - nroutes - nfilters - nservers`; wrong counts can overlap server/filter/route/TID spaces and break offload.
- Fatal parity errors immediately escalate to adapter fatal error handling. Tests that inject parity must expect reset side effects.
- `t3_mc5_prep()` indexes `tcam_part_size` by `G_TMPARTSIZE(cfg)` with fixed known encodings; unexpected register values can misrepresent capacity.

## Test signals

Validation should cover both supported TCAM part types, 72-bit and 144-bit modes, boundary validation for `nservers`, `nfilters`, and `nroutes`, TCAM reset timeout, DBGI write timeout, full array initialization, unsupported part handling, interrupt counters for every cause bit, fatal parity escalation, and user sysfs changes to filter/server counts before full init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/mc5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/regs.h

## Purpose

`regs.h` is the Chelsio T3 hardware register map and bitfield macro header. It provides symbolic register offsets (`A_*`), bit shifts (`S_*`), masks (`M_*`), value constructors (`V_*`), flags (`F_*`), and field extractors (`G_*`) for the SGE, PCI/PCIe, GPIO/debug, MC7 memory controllers, CIM, TP, ULP RX/TX, PM, MPS, CPL switch, SMB/I2C/MI/SF, PL, MC5, and XGMAC blocks. Driver implementation files use it as the authoritative MMIO programming vocabulary.

## Important APIs, types, and functions

This header declares macros rather than C functions or types. Major covered blocks include:

- SGE registers: `A_SG_CONTROL`, doorbells, GTS, context command/data/masks, response queue credits, interrupt cause/enable, queue thresholds, timer tick, and context bases.
- PCI/PCIe registers: `A_PCIX_*`, `A_PCIE_*`, PEX controls/errors, parity and bus error flags.
- Debug/GPIO: `A_T3DBG_GPIO_EN`, interrupt enable/cause, active-low controls used by LED/PHY interrupt handling and ethtool physical ID.
- MC7 memory controller: config, mode, DLL/ref timings, ECC, BIST, interrupt cause/enable, and base aliases for PMRX/PMTX/CM regions.
- CIM: boot, SDRAM, host interrupt, host access, and IBQ debug registers.
- TP: ingress/out config, TCP options, page manager, timers, RSS, MTU, traffic manager, PIO, reset, MIB, interrupt, trace/drop/proxy/embedded fields.
- ULP RX/TX: iSCSI/DDP/STag/RQ/PBL/TPT bounds, page-size fields, DMA weights, and interrupt bits.
- PM/MPS/CPL: packet memory RX/TX errors, MPS port config/parity, CPL switch interrupts and mapping.
- Management buses and PL: SMB, I2C, MI1, serial flash, top-level interrupt enable/cause/reset/revision.
- MC5: DB config, partition indexes, latency, interrupt bits, DBGI command/address/data/response, and TCAM command registers.
- XGMAC: TX/RX controls, exact match/hash filters, interrupt/status, FIFO config, SERDES/XAUI/RGMII, packet size, reset, port config, stats, and second MAC base.

## Control flow

There is no executable control flow. Control flow in implementation files is expressed by reading, writing, masking, and testing these macros through helpers such as `t3_read_reg()`, `t3_write_reg()`, and `t3_set_reg_field()`. For example, `cxgb3_main.c` uses `A_XGM_*` and `F_*` bits to enable MACs and clear link faults, `A_SG_*` for doorbells and interrupt causes, `A_TP_*` for offload/RSS/MTU/scheduler setup, and `A_PL_*` for top-level interrupt masking. `mc5.c` uses `A_MC5_*` and `V_/F_` helpers for TCAM initialization.

## State and persistence behavior

The header itself has no mutable state. Its macros address volatile MMIO hardware state. Some registers represent persistent-ish hardware configuration across driver runtime, such as queue contexts, TCAM partitions, memory bounds, and MAC settings, but they are reprogrammed by initialization and are not persisted by this header. Register reads may have side effects in hardware; users such as `get_regs()` in `cxgb3_main.c` intentionally avoid clear-on-read MAC statistics.

## Dependencies and integration points

`regs.h` is included by most low-level cxgb3 driver files, including `cxgb3_main.c`, `cxgb3_offload.c`, and `mc5.c`. It depends only on preprocessor constants and the SPDX license line. Its names must match the hardware manuals and the `common.h` helper code that performs register access. It is also indirectly part of user-observable diagnostics because ethtool register dumps and error logs derive offsets and flags from this map.

## Risks and edge cases

- A wrong shift, mask, flag, or offset can silently program hardware incorrectly; there is no type checking.
- Macro names are global within the translation unit and many are short (`S_ADDR`, `S_BUSY`, `S_DATA`), so include-order conflicts are possible.
- Some register offsets are block-relative or aliased, such as TP PIO table offsets and XGMAC second-port bases; callers must know when to add per-block offsets.
- Field constructors do not mask input values, so callers must validate ranges before using `V_*` macros.
- Hardware side effects are not visible in this header. Callers must know which registers are clear-on-read, write-one-to-clear, busy-waited, or reset-sensitive.
- Updating this file for a new chip revision risks breaking older revisions because many bits are revision-specific but not encoded in the macro names.

## Test signals

Validation should include compile coverage for all users, hardware smoke tests for SGE queue setup, interrupt enable/cause handling, TP RSS/MTU/offload setup, MC5 initialization, XGM link transitions, ethtool register dumps, and fault injection for parity/error bits. Static checks can compare `A_*` offsets and `S_/M_/V_/G_` fields against vendor register specifications and assert that value constructors are only fed bounded inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/regs.h -->
