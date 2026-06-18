# subset-b-004399 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.c

## Purpose
Implements Chelsio T4/T5/T6 ingress filter management for the `cxgb4` Ethernet driver. It validates user/kernel filter specifications, allocates filter IDs across high-priority TCAM, normal TCAM, server-filter, and T6 hash-filter regions, emits firmware/CPL work requests, handles asynchronous replies, maintains per-filter software state, and releases hardware-side resources such as L2T, SMT, CLIP, encapsulated MAC filters, ATIDs, and TIDs.

## Important APIs, Types, and Functions
The main public entry points are `cxgb4_set_filter`, `cxgb4_del_filter`, `__cxgb4_set_filter`, `__cxgb4_del_filter`, `cxgb4_get_free_ftid`, `cxgb4_get_filter_counters`, `is_filter_exact_match`, `set_filter_wr`, `delete_filter`, `clear_filter`, `clear_all_filters`, `filter_rpl`, `hash_filter_rpl`, `hash_del_filter_rpl`, and `init_hash_filter`.

Important data flows center on `struct ch_filter_specification` as the caller-facing match/action description, `struct filter_entry` as the driver-owned state record, `struct filter_ctx` as the optional completion/result carrier, and `struct tid_info` as the table/bmap owner for TCAM, HPFILTER, server-filter, ATID, hash TID, and active TID resources. Firmware and CPL integration uses `fw_filter_wr`/`fw_filter2_wr`, `cpl_set_tcb_field`, `cpl_act_open_req`, `cpl_act_open_req6`, `cpl_act_open_rpl`, `cpl_abort_req`, and `cpl_abort_rpl_rss`.

Key internal helpers include `validate_filter` for checking the requested fields against `tp.vlan_pri_map` or `tp.filter_mask`, `get_filter_steerq` for mapping direct-steer queue indices to absolute response-queue IDs, `fill_default_mask` for making nonzero values exact-match by default, `cxgb4_filter_prio_in_range` for TC priority ordering across HPFILTER/normal regions, `hash_filter_ntuple` for T6 compressed tuple construction, `configure_filter_tcb` for post-create TCB action programming, and `set_nat_params` for NAT rewrite TCB fields.

## Control Flow and State
TCAM filter creation enters through `__cxgb4_set_filter`, fills default masks, validates match/action fields, maps steering queues, chooses HPFILTER or normal `ftid_tab` based on `fs->prio`, checks IPv4/IPv6 slot alignment, reserves the corresponding bitmap bits, optionally acquires CLIP state for T6 IPv6, translates PF/VF or encapsulation VNI state into the firmware-visible outer VLAN fields, stores `f->fs`, `f->dev`, `f->ctx`, and the hardware TID, then calls `set_filter_wr`. `set_filter_wr` allocates L2T and/or SMT resources for switch-loopback rewrites, constructs a filter WR with match fields and actions, marks `f->pending`, and sends via `t4_ofld_send`.

Hash filter creation is selected when `fs->hash` is true and `is_hashfilter(adapter)` is enabled. `cxgb4_set_hash_filter` allocates a heap `filter_entry`, reserves an ATID with `cxgb4_alloc_atid`, optionally allocates L2T/SMT/MPS encapsulation/CLIP resources, builds a T6 active-open request for IPv4 or IPv6 with `TCAM_BYPASS_F | NON_OFFLOAD_F`, marks it pending, and sends it on the setup priority path. The reply arrives at `hash_filter_rpl`, which looks up by ATID, inserts the final TID into `tid_tab`, frees the ATID, configures TCB rewrite/count/action bits, sets `valid`, and completes the context; failure releases all resources and returns `-ENOSPC` for TCAM-full or `-EINVAL` otherwise.

Deletion has two distinct paths. TCAM deletion through `__cxgb4_del_filter` checks writability, clears the reserved ftid/hpftid bitmap immediately for valid entries, and sends a firmware delete WR. `filter_rpl` later finds the entry by returned TID, clears the full filter on `FW_FILTER_WR_FLT_DELETED`, marks added filters valid on `FW_FILTER_WR_FLT_ADDED`, or clears failed filters. Hash deletion through `cxgb4_del_hash_filter` rewrites TCB RSS info to the firmware event queue and appends abort request/reply CPLs; `hash_del_filter_rpl` then clears the entry, removes the TID, frees the heap record, and completes the caller.

Persistent state lives in adapter-owned in-memory tables and hardware tables rather than disk. `ftid_bmap`/`hpftid_bmap` track reserved TCAM slots, `ftid_tab`/`hpftid_tab` store fixed filter entries, `tid_tab` stores hash/offload TID owners, ATID free lists store pending hash filter opens, and `filter_entry` flags `valid`, `pending`, and `locked` serialize operations. Hardware persistence includes firmware filter table entries, LE hash table entries, TCB words, L2T/SMT rows, CLIP table references, and MPS encapsulation filters. Locks include `ftid_lock`, `win0_lock` for memory-window counter reads, and ATID/STID/TID locks provided by `cxgb4_main.c`.

## Dependencies and Integration Points
Depends on `cxgb4.h` for adapter/TID/filter data structures and helper macros, `t4_regs.h`, `t4_tcb.h`, `t4_values.h`, `t4_msg.h`, and `t4fw_api.h` for register/CPL/FW layouts, plus `clip_tbl.h`, `l2t.h`, and `smt.h` for rewrite-resource management. It uses adapter parameters initialized in `cxgb4_main.c`, including chip generation, filter base/counts, high-priority filter support, hash-filter enablement, TP ingress/filter masks, CLIP ranges, and firmware `FILTER2_WR` support.

`cxgb4_main.c` routes firmware event queue CPLs to `filter_rpl`, `hash_filter_rpl`, and `hash_del_filter_rpl`; allocates the backing `tid_info` layout in `tid_init`; initializes hash filter support in `adap_init0`; frees all filters in `remove_one`; and exposes server-filter helpers which call `set_filter_wr`, `delete_filter`, `writable_filter`, and `clear_filter`. TC flower, TC u32, ethtool ntuple, and offload code call the exported filter helpers to install and remove hardware rules.

## Risks and Test Signals
High-risk areas are asynchronous state transitions, early bitmap release before firmware delete completion, IPv6 multi-slot alignment differences between T5 and T6, hash filter heap lifetime, mismatched ATID/TID lookup, and TCB post-programming failures after a hash entry is already inserted. Resource unwind paths must release L2T, SMT, CLIP, encapsulated MAC filters, ATIDs, and bitmap reservations exactly once.

Feature risks include misinterpreting TP filter masks, PF/VF versus outer VLAN field overlap, VNI encapsulation limitations, NAT mode TCB word packing, unsupported T4 VLAN rewrite behavior, priority ordering across HPFILTER/hash/normal regions, and hash-filter exact-match requirements silently rejecting otherwise valid rules.

Test signals include `tc flower` replace/destroy/stats on IPv4 and IPv6, ethtool ntuple add/delete, hash exact-match rules on T6, HPFILTER priority ordering tests, direct-steer queue tests, NAT/rewrite switch-loopback tests, counter reads through `cxgb4_get_filter_counters`, module remove with live filters, firmware reply error injection, allocation-failure unwind, and race tests for concurrent add/delete on the same filter ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.h

## Purpose
Declares the internal `cxgb4` filter-management interface shared between the main adapter driver, filter implementation, ethtool filter support, TC offload modules, and firmware event dispatch. It also defines `WORD_MASK`, a convenience all-ones 32-bit TCB mask used by filter programming code.

## Important APIs, Types, and Functions
The header exposes asynchronous reply handlers `filter_rpl`, `hash_filter_rpl`, and `hash_del_filter_rpl`; direct filter state/resource helpers `clear_filter`, `set_filter_wr`, `delete_filter`, `writable_filter`, `clear_all_filters`, and `init_hash_filter`; exact-match capability probing through `is_filter_exact_match`; and ethtool filter lifecycle hooks `cxgb4_init_ethtool_filters` and `cxgb4_cleanup_ethtool_filters`.

Types are intentionally not defined here. The declarations rely on driver-wide structures from `cxgb4.h` and message structures from `t4_msg.h`, notably `struct adapter`, `struct filter_entry`, `struct ch_filter_specification`, `struct cpl_set_tcb_rpl`, `struct cpl_act_open_rpl`, and `struct cpl_abort_rpl_rss`.

## Control Flow and State
There is no runtime control flow in this header. It defines a narrow contract: callers may ask whether a filter entry is writable, submit or delete fixed-index filters, clear per-entry state, clear all adapter filters during teardown, and route firmware/CPL replies back into the filter state machine. Persistent state is owned by the implementation through adapter TID/filter tables and firmware hardware tables; this file only exposes the operations that mutate or reconcile that state.

## Dependencies and Integration Points
Includes `t4_msg.h` for CPL reply/request type declarations. It is included by `cxgb4_filter.c` for self-consistency and by `cxgb4_main.c` to dispatch firmware event queue replies, configure hash-filter capability during adapter init, install server filters for offload listeners, and clear filters on PCI remove. Other local modules use these declarations for ethtool and TC filter integration.

The ethtool declarations are implemented outside the listed file, so this header is also the compile-time bridge between generic filter handling and ethtool-specific rule bookkeeping.

## Risks and Test Signals
Risk is mostly interface drift: mismatched prototypes or incomplete declarations can break event dispatch or leave cleanup paths unable to release filter resources. Because several declared functions are called during teardown and interrupt/event handling, return semantics and sleepability assumptions must stay aligned with callers.

Test signals include full-driver builds with ethtool/TC offload enabled, `modpost` symbol/prototype checks, firmware event queue paths reaching the correct reply handlers, remove/shutdown cleanup calling `clear_all_filters`, and ethtool filter init/cleanup coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_main.c -->
