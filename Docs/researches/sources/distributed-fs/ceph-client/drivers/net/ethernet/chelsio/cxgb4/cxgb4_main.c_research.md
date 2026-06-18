# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_main.c

## Purpose
Implements the core Chelsio T4/T5/T6 PCI Ethernet driver. It owns module registration, PCI probe/remove/shutdown, firmware negotiation and configuration-file loading, adapter resource discovery, netdevice creation and operations, SGE queue and interrupt setup, RSS and MAC filter programming, TID/STID/ATID table management for upper-layer offload drivers, TC offload entry points, tunnel port programming, PTP/TLS/IPsec hooks, SR-IOV management, EEH recovery, and teardown.

## Important APIs, Types, and Functions
Module and PCI integration is provided through `cxgb4_init_module`, `cxgb4_cleanup_module`, `cxgb4_driver`, `init_one`, `remove_one`, and `shutdown_one`. Adapter initialization flows through `t4_get_chip_type`, `adap_init0`, `adap_init0_config`, `adap_init0_tweaks`, `adap_init1`, `cfg_queues`, `enable_msix`, `setup_fw_sge_queues`, `setup_sge_queues`, `setup_rss`, `init_rss`, `setup_memwin`, and `setup_memwin_rdma`.

Netdevice operations are collected in `cxgb4_netdev_ops` and include `cxgb_open`, `cxgb_close`, `t4_start_xmit`, `cxgb_select_queue`, stats, RX mode, MAC address, feature, ioctl, MTU, TC setup, feature checks, and hardware timestamp get/set. SR-IOV management uses `cxgb4_iov_configure` and the management netdev ops when `CONFIG_PCI_IOV` is enabled.

Exported services for upper-layer drivers include `cxgb4_alloc_atid`, `cxgb4_free_atid`, `cxgb4_alloc_stid`, `cxgb4_alloc_sftid`, `cxgb4_free_stid`, `cxgb4_remove_tid`, `cxgb4_create_server`, `cxgb4_create_server6`, `cxgb4_remove_server`, `cxgb4_create_server_filter`, `cxgb4_remove_server_filter`, MTU selectors, port channel/VI/index helpers, TCP stats, EQ flush/sync, TPTE reads, SGE timestamp reads, and BAR2 SGE queue register mapping.

Important local structures are `struct adapter`, `struct port_info`, `struct sge`, `struct tid_info`, `struct msix_info`, `struct hash_mac_addr`, firmware command structures, and netdev/tls/xfrm/udp-tunnel ops tables.

## Control Flow and State
PCI probe begins by reserving PCI regions, enabling the device, mapping BAR0, allocating `struct adapter`, identifying chip generation and PF, creating the workqueue, preparing the adapter, mapping BAR2 for T5/T6, setting up memory windows, and calling `adap_init0`. `adap_init0` connects to firmware, optionally updates firmware, loads host/flash/default configuration files, initializes HMA and firmware, discovers PF resources, port vectors, SGE ranges, filter ranges, CLIP ranges, active-filter/offload ranges, firmware feature support, capabilities, TID/STID/ATID sizes, RDMA/iSCSI/crypto resources, MTU tables, SGE parameters, and TP parameters.

After firmware/resource discovery, `init_one` allocates netdevices for each port, assigns hardware features and ops, initializes ethtool dump support, calls `t4_port_init`, configures queues, allocates SMT/L2T/CLIP/scheduler/TID state, initializes TC and ethtool offload subsystems, selects MSI-X/MSI/INTx, initializes MPS ref entries, RSS, non-data interrupt allocation, and the firmware event queue, registers netdevices, creates debugfs, enables ULDs, and initializes PTP/thermal support when available.

Runtime open goes through `cxgb_open`: if the adapter is not fully initialized, it calls `cxgb_up`, which allocates SGE queues, programs RSS, requests interrupts, enables NAPI/RX, starts SGE, enables hardware interrupts, sets `CXGB4_FULL_INIT_DONE`, and notifies ULDs. The port then refreshes port info, programs RX mode/MAC/link, starts mirror queues when configured, and starts TX queues. Close stops TX/carrier, disables the port, resets DCB, and tears down mirror queues. Adapter-down paths stop SGE, cancel work, free queues, and clear the full-init flag.

The firmware event queue handler `fwevtq_handler` dispatches egress updates, firmware messages, L2T/SMT write replies, filter replies (`filter_rpl`, `hash_filter_rpl`, `hash_del_filter_rpl`), and SRQ replies. This is the central asynchronous completion path for filter programming declared in `cxgb4_filter.h`.

Persistent state is a mix of kernel memory, firmware resources, and hardware tables. In memory, `adapter` tracks flags, PF/mbox identity, port list, SGE queue maps, `tid_info`, L2T/SMT/CLIP/scheduler tables, MSI-X bitmap, MAC hash list, VF info, work items, debugfs, HMA pages, and ULD handles. Hardware/firmware state includes VIs, MAC filters, RSS tables, SGE queues, filter and TID tables, firmware configuration, HMA mappings, tunnel match-all filters, PTP state, SR-IOV VFs, and offload resources. Locks include `uld_mutex`, RTNL in netdev/EEH paths, per-table spinlocks, `win0_lock`, `stats_lock`, MSIX bitmap lock, and queue doorbell locks.

## Dependencies and Integration Points
The file depends heavily on the Linux PCI, netdevice, NAPI, interrupt, firmware loader, debugfs, workqueue, notifier, UDP tunnel, XFRM, TLS, SR-IOV, and ethtool infrastructure. Local dependencies include `cxgb4.h`, `cxgb4_filter.h`, `t4_regs.h`, `t4_values.h`, `t4_msg.h`, `t4fw_api.h`, `t4fw_version.h`, DCB, SRQ, debugfs, CLIP, L2T, SMT, scheduler, TC u32/flower/mqprio/matchall, PTP, and CUDBG modules.

Filter-specific integration is broad. `adap_init0` discovers `FILTER_START/END`, `HPFILTER_START/END`, `ACTIVE_FILTER_START/END`, `FILTER2_WR`, hash-filter capability, TID/hash table bases, and server-filter partitioning. `tid_init` lays out `hpftid_tab`, `ftid_tab`, bitmaps, ATID/STID tables, and `tid_tab`. `fwevtq_handler` routes filter replies. `cxgb4_create_server_filter` and `cxgb4_remove_server_filter` let offload listeners use hardware filters to redirect SYN packets. `remove_one` calls `clear_all_filters` before general teardown.

ULD integration is exposed through exported symbols and `adapter_list`/`uld_list`, with state notifications for up/down/detach/fatal/recovery. TC integration enters through `ndo_setup_tc` and dispatches to u32, flower, matchall, and mqprio modules. Tunnel integration programs VXLAN/GENEVE UDP ports and raw match-all MAC filters. TLS and IPsec netdev hooks delegate to crypto ULDs under `uld_mutex`.

## Risks and Test Signals
Probe and teardown have high blast radius: partial initialization must unwind PCI regions, BAR mappings, workqueues, firmware references, netdevices, queue maps, MSI state, ULD memory, L2T/SMT/CLIP/TID tables, TC/ethtool state, filters, debugfs, PTP, thermal, and HMA without double-freeing or leaving hardware active. The `func != ent->driver_data` early path disables the device and saves state for non-owner PFs, so SR-IOV/multi-PF behavior is sensitive.

Concurrency risks include firmware event completions racing with teardown, doorbell full/drop work touching queues after shutdown, TID release work holding stale `tid_tab` pointers, ULD callbacks under `uld_mutex`, notifier lifetime for netevent and IPv6 CLIP, and RTNL/adapter lock ordering in EEH recovery. Resource-sizing risks include queue count reduction after limited MSI-X allocation, kdump mode disabling offload, firmware capability differences, and filter/server-filter partitioning changing `nftids`.

Hardware feature risks include chip-generation conditionals for T4/T5/T6, firmware configuration-file fallbacks, hash filter plus offload support, high-priority filter support, CLIP absence, raw tunnel MAC filters, HMA allocation/mapping, SR-IOV management netdev lifetime, TLS/IPsec ULD availability, and PTP timestamping behavior.

Test signals include successful module load/unload on T4/T5/T6, firmware update/configuration-file paths, one-port and multi-port probe, MSI-X/MSI/INTx fallback, open/close cycles, suspend/EEH recovery, `tc` flower/u32/matchall/mqprio offload, ethtool ntuple filters, ULD RDMA/iSCSI/TLS/IPsec attach/detach, VXLAN/GENEVE tunnel port add/remove, SR-IOV enable/disable with VF management operations, kdump probe path, forced allocation failures in probe, and remove while filters/offloads/queues are active.
