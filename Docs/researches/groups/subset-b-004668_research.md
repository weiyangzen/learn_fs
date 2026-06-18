# subset-b-004668 research

Grouped research for WangXun libwx Ethernet driver files. Each file section preserves the source path in its title and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.c

## Purpose
`wx_ethtool.c` implements shared ethtool operations for WangXun libwx based Ethernet devices. It exposes statistics strings and values, driver information, link settings through phylink, WOL, pause parameters, ring and interrupt coalescing controls, channel counts, RSS indirection/key/hash-field controls, debug message level, timestamp capability reporting, PTP timestamp statistics, and a reduced VF ethtool operation table.

## Important APIs, types, and functions
The local `struct wx_stats` maps ethtool stat names to offsets inside `struct wx`. `wx_gstrings_stats`, `wx_gstrings_fdir_stats`, and `wx_gstrings_rsc_stats` define global, Flow Director, and RSC counters. Exported APIs include `wx_get_sset_count`, `wx_get_strings`, `wx_get_ethtool_stats`, `wx_get_mac_stats`, `wx_get_pause_stats`, `wx_get_drvinfo`, `wx_nway_reset`, `wx_get_link_ksettings`, `wx_set_link_ksettings`, `wx_get_wol`, `wx_set_wol`, `wx_get_pauseparam`, `wx_set_pauseparam`, `wx_get_ringparam`, `wx_get_coalesce`, `wx_set_coalesce`, `wx_get_channels`, `wx_set_channels`, `wx_rss_indir_size`, `wx_get_rxfh_key_size`, `wx_get_rxfh`, `wx_set_rxfh`, `wx_get_rxfh_fields`, `wx_set_rxfh_fields`, `wx_get_msglevel`, `wx_set_msglevel`, `wx_get_ts_info`, `wx_get_ptp_stats`, and `wx_set_ethtool_ops_vf`.

## Control flow and behavior
Stats retrieval first calls `wx_update_stats()` and then copies counters from `struct wx` and per-ring `u64_stats` into the ethtool buffer in the same order used by `wx_get_strings()`. Link and pause operations delegate to `phylink_ethtool_*`. WOL writes `WX_PSR_WKUP_CTL` and updates PCI device wakeup state. Coalescing validation chooses per-MAC EITR limits, handles adaptive ITR mode, writes each q-vector EITR through `wx_write_eitr()`, and may reset the device if RSC must change. Channel changes update RSS/FDIR limits and call `wx->setup_tc()`. RSS changes update `wx->rss_indir_tbl`, `wx->rss_key`, or `wx->rss_flags` and push them to hardware through `wx_store_reta()`, `wx_store_rsskey()`, and `wx_config_rss_field()`.

## State and persistence
This file mutates persistent driver runtime state in `struct wx`: WOL flags, interrupt moderation settings, `adaptive_itr`, per-vector `itr`, ring feature limits, RSS indirection table, RSS key, RSS flow flags, debug message mask, and RSC enable flags. Values live in memory and hardware registers; they are not persisted across driver unload except where firmware or PCI wake state keeps WOL semantics.

## Dependencies and integration points
It depends on Linux ethtool, phylink, PCI, PTP clock, netdev feature, and `u64_stats` APIs. It integrates with `wx_hw.c` for RSS and stats programming, `wx_lib.c` for EITR writes and resource-level settings, and `wx_ptp.c` for timestamp clock state visible through `wx->ptp_clock` and timestamp counters. VF support is intentionally narrower and installs `wx_ethtool_ops_vf` on VF netdevices.

## Risks and edge cases
Stats ordering must remain synchronized between count, strings, and value generation or userspace will mislabel counters. `wx_get_coalesce()` assumes `wx->q_vector[0]` exists. Coalescing can silently switch adaptive mode and RSC, with reset side effects through `wx->do_reset`. RSS setters accept user indirection values without local range validation beyond ethtool core expectations. VF ethtool timestamp info uses `ethtool_op_get_ts_info`, not the PF PTP path. Channel changes depend on `other_count == 1`, so callers must provide the expected misc vector count.

## Test signals
Useful tests are `ethtool -S`, `ethtool -i`, `ethtool -c/-C`, `ethtool -l/-L`, `ethtool -x/-X`, `ethtool -n/-N rx-flow-hash`, WOL toggling with suspend/resume, and checking that RSC/LRO behavior changes only when coalescing thresholds require it. Kernel-level signals include no stat count mismatch warnings, successful q-vector EITR writes, and correct PTP `phc_index` when `wx_ptp_init()` registered a clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.h

## Purpose
`wx_ethtool.h` declares the shared ethtool-facing API implemented by `wx_ethtool.c` for PF and VF WangXun drivers. It is the contract other driver modules use to populate `struct ethtool_ops` tables without duplicating common libwx logic.

## Important APIs, types, and functions
The header exports prototypes for stats, driver info, link settings, WOL, pause configuration, ring parameters, coalescing, channels, RSS indirection and key access, RSS hash field controls, message level, timestamp info, PTP timestamp statistics, and VF ethtool-op installation. It uses kernel ethtool types such as `struct ethtool_link_ksettings`, `struct ethtool_rxfh_param`, `struct ethtool_rxfh_fields`, `struct kernel_ethtool_ts_info`, and `struct ethtool_ts_stats`.

## Control flow and behavior
There is no executable control flow in this header. Its declarations show which common operations are expected to be wired into device-specific PF ethtool ops, and which subset is available to VF devices through `wx_set_ethtool_ops_vf()`.

## State and persistence
The header owns no state. All declared operations act on `struct net_device` and reach driver state through `netdev_priv(netdev)` in the implementation.

## Dependencies and integration points
Consumers must include the appropriate Linux netdevice and ethtool definitions before or alongside this header. It integrates with `wx_hw.h` and `wx_lib.h` indirectly because several declared functions reconfigure RSS tables, EITR registers, or hardware stats.

## Risks and edge cases
Prototype drift between this header and `wx_ethtool.c` would break module builds. Because the header does not include all dependent type headers itself, include ordering in consumers matters. API compatibility also tracks kernel ethtool signatures, especially the newer `kernel_ethtool_*` and `netlink_ext_ack` parameters.

## Test signals
Build coverage is the main signal: all PF/VF drivers including this header should compile without incompatible-pointer warnings when assigning ethtool ops. Runtime smoke tests should verify every op pointer wired by consumers maps to a declared and exported implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.c

## Purpose
`wx_hw.c` is the common hardware programming layer for WangXun libwx devices. It covers MDIO access, interrupt masking, firmware and EEPROM host-interface commands, MAC address tables, multicast and VLAN filtering, SR-IOV/VMDq pool setup, Rx/Tx queue register configuration, RSS programming, reset/stop/start flows, flow control, and hardware statistics.

## Important APIs, types, and functions
MDIO helpers include `wx_phy_read_reg_mdi_c22`, `wx_phy_write_reg_mdi_c22`, `wx_phy_read_reg_mdi_c45`, and `wx_phy_write_reg_mdi_c45`. Firmware/NVM helpers include `wx_check_flash_load`, `wx_control_hw`, `wx_mng_present`, `wx_host_interface_command`, `wx_set_pps`, `wx_read_ee_hostif`, `wx_read_ee_hostif_buffer`, and `wx_init_eeprom_params`. Address/filter APIs include `wx_get_mac_addr`, `wx_init_rx_addrs`, `wx_mac_set_default_filter`, `wx_add_mac_filter`, `wx_del_mac_filter`, `wx_flush_sw_mac_table`, `wx_mta_vector`, `wx_set_mac`, `wx_set_rx_mode`, `wx_set_vfta`, `wx_vlan_rx_add_vid`, and `wx_vlan_rx_kill_vid`. Datapath and reset APIs include `wx_disable_rx`, `wx_configure_rx`, `wx_configure`, `wx_start_hw`, `wx_stop_adapter`, `wx_disable_pcie_master`, `wx_reset_mac`, `wx_reset_misc`, `wx_sw_init`, `wx_fc_enable`, `wx_update_stats`, and `wx_clear_hw_cntrs`.

## Control flow and behavior
Initialization typically runs through `wx_sw_init()` to fill PCI identity, RSS defaults, locks, state bitmaps, and MAC table storage, then hardware reset/setup calls such as `wx_start_hw()`, `wx_init_rx_addrs()`, and `wx_configure()`. `wx_configure()` sets packet buffers and flow-control thresholds, configures virtualization and VLAN TPIDs, applies current Rx mode and active VLANs, optionally configures Flow Director, then configures Tx rings, Rx rings, and the interrupt status block address. `wx_configure_rx()` disables Rx, programs parser/RSS/RSC/buffer sizes, configures every Rx ring, disables the security Rx path before enabling Rx, and then re-enables the security path. Stop/reset paths mask interrupts, disable Rx/Tx queues, flush writes, and disable PCIe master access.

## State and persistence
The file owns large parts of `struct wx` hardware state: PCI IDs, bus function, EEPROM metadata, RSS key/flags/tables, MAC filter table, active VLAN shadow table, multicast shadow table, flow-control thresholds/mode, stats accumulators, reset locks/state bitmaps, SR-IOV pool metadata, queue register indices, and adapter stopped state. Several shadow arrays exist because hardware tables are clear-on-read, write-only, or need errata workarounds. Hardware registers are the external persistent state until reset; in-memory state must be restored after reset.

## Dependencies and integration points
It depends on `wx_type.h` register definitions and core structs, `wx_lib.h` for Rx buffer refill during ring configuration, and SR-IOV/VF headers for VF multicast and pool state. Linux dependencies include PCI, netdevice, VLAN, etherdevice, PHY/MDIO, bitmaps, polling helpers, locks, and DMA register access helpers. It is called by open/close/reset paths in device-specific drivers, by ethtool paths for RSS/coalescing and stats, by PTP for PPS firmware commands, and by netdev ops for MTU/MAC/VLAN/Rx mode changes.

## Risks and edge cases
Register sequences are timing sensitive: MDIO, firmware mailbox, Rx/Tx queue enable/disable, security Rx path, and PCIe master disable all poll with finite timeouts. The host-interface command code has two protocols selected by `WX_FLAG_SWFW_RING`; incorrect flag state will talk to the wrong mailbox. MAC/VLAN table handling relies on shadow state and has capacity failures that fall back to promiscuous behavior. `wx_clear_vmdq()` appears to test `mpsar_lo`/`mpsar_hi` for zero after already returning when both are zero, so the later "last pool" clear path is effectively unreachable. Flow control depends on valid packet-buffer thresholds; bad MTU/traffic-class combinations can degrade to fallback thresholds. Stats are clear-on-read or wrap-sensitive and must stay under `hw_stats_lock`.

## Test signals
Hardware smoke tests should cover probe, open, reset, close, MTU change, MAC change, multicast list changes, promiscuous/allmulti/RXALL toggles, VLAN add/remove, SR-IOV enablement, RSS programming, link up/down, and flow-control changes. Useful observability includes timeout logs from MDIO/firmware/queue polling, `ethtool -S` monotonic stats, correct VLAN filtering with and without VMDq, no DMA activity after `wx_stop_adapter()`, and successful suspend/resume with WOL/NCSI-capable boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.h

## Purpose
`wx_hw.h` declares the common hardware-control API for libwx PF and VF-capable drivers. It is the public boundary for register programming, reset, filtering, VLAN, RSS, flow control, and statistics helpers implemented in `wx_hw.c`.

## Important APIs, types, and functions
The header declares MDIO clause 22 and 45 accessors, interrupt enable/disable, flash-load and management checks, firmware host-interface commands, PPS firmware setup, EEPROM reads, MAC address setup, MAC filter add/delete/flush, multicast hash vector calculation, netdev MAC/MTU/Rx-mode operations, Rx queue control, RSS table/key storage, full Rx/device configuration, reset/stop/start helpers, MSI-X count discovery, software initialization, VLAN filter operations, flow-control enablement, and stats update/clear functions.

## Control flow and behavior
There is no executable logic in the header. The declarations outline the expected lifecycle: initialize software state, inspect flash/NVM, reset/start hardware, configure queues/RSS/Rx mode, service netdev changes, update stats, and stop/reset on teardown.

## State and persistence
The header owns no data. Its APIs act on `struct wx`, `struct net_device`, `struct wx_ring`, `struct mii_bus`, and hardware registers through implementation-defined helpers.

## Dependencies and integration points
It includes `<linux/phy.h>` for MII/MDIO bus types and relies on prior visibility of `struct wx`, `struct wx_ring`, and netdevice types from libwx headers. It is included by ethtool, datapath, PTP, and device-specific code that need common hardware operations.

## Risks and edge cases
This header exposes a broad low-level surface; call ordering is critical but not encoded in types. For example, `wx_configure_rx()` assumes rings/resources exist, VLAN operations assume initialized shadow tables, and stats update assumes a running netdev outside reset. Kernel API drift around VLAN prototypes, netdev features, or MDIO signatures would surface here.

## Test signals
Compilation across PF and VF drivers is the baseline. Integration tests should validate each netdev op wired from this header is only called after required initialization and is not called after resources are freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.c

## Purpose
`wx_lib.c` is the common libwx datapath and resource-management layer. It decodes hardware packet types, manages Rx page-pool buffers and Tx DMA mappings, implements NAPI polling, interrupt vector allocation/configuration, ring allocation/freeing, netdev stats and feature handling, ring resizing, and service timer scheduling.

## Important APIs, types, and functions
Exported datapath/resource APIs include `wx_decode_ptype`, `wx_alloc_rx_buffers`, `wx_desc_unused`, `wx_xmit_frame`, `wx_napi_enable_all`, `wx_napi_disable_all`, `wx_reset_interrupt_capability`, `wx_clear_interrupt_scheme`, `wx_init_interrupt_scheme`, `wx_msix_clean_rings`, `wx_free_irq`, `wx_setup_isb_resources`, `wx_free_isb_resources`, `wx_misc_isb`, `wx_write_eitr`, `wx_configure_vectors`, `wx_clean_all_rx_rings`, `wx_clean_all_tx_rings`, `wx_free_resources`, `wx_setup_resources`, `wx_get_stats64`, `wx_set_features`, `wx_fix_features`, `wx_features_check`, `wx_set_ring`, `wx_service_event_schedule`, `wx_service_event_complete`, and `wx_service_timer`. Important internal helpers include RX descriptor processing, checksum/VLAN/RSS/PTP annotation, TX TSO/checksum context descriptor generation, MSI-X/MSI fallback, q-vector allocation, and page-pool setup.

## Control flow and behavior
RX flow starts with page-pool-backed descriptor refill in `wx_alloc_rx_buffers()`. NAPI `wx_poll()` cleans Tx completions, then receives packets with a per-ring budget. RX cleaning reads completed descriptors, syncs DMA, builds or extends an skb, handles non-EOP/RSC aggregation, validates headers, applies RSS hash/checksum/PTP/VLAN metadata, and submits to GRO. TX flow enters `wx_xmit_frame()`, selects a Tx ring from queue mapping, pads short packets, reserves descriptors, sets VLAN and timestamp flags, encodes packet type, creates TSO or checksum context descriptors, optionally feeds ATR/Flow Director, DMA maps the skb fragments, and rings the doorbell. Interrupt setup chooses queue counts, allocates MSI-X or falls back to MSI/INTx, creates q-vectors and rings, maps IVAR entries, and programs EITR values.

## State and persistence
Runtime state includes q-vectors, rings, descriptor DMA areas, page pools, SKB ownership, DMA mappings, Tx/Rx indices, per-ring and per-vector stats, interrupt moderation/DIM state, MSI-X entries, ISB DMA memory, feature flags, service scheduling bits, RSS/VMDq queue counts, and timestamp-in-progress state. All ring resources are in-memory plus DMA-coherent memory and must be paired with cleanup paths. Service scheduling persists through `WX_STATE_SERVICE_SCHED` until the service task calls complete.

## Dependencies and integration points
It depends on Linux networking core APIs for NAPI, GRO, SKBs, checksum offload, GSO/TSO, VLAN accel, page_pool, DMA mapping, IRQ vectors, DIM, RCU, workqueues, timers, and PCI. It integrates with `wx_hw.c` for hardware register configuration and stats, `wx_ptp.c` for Rx/Tx hardware timestamps, `wx_vf_lib.h` for VF EITR writes, and device-specific callbacks for ATR, queue count selection, and reset/open/close orchestration.

## Risks and edge cases
The highest-risk areas are DMA lifetime, ring index wraparound, and concurrent teardown. TX timestamping has a single in-flight SKB protected by `WX_STATE_PTP_TX_IN_PROGRESS`; error paths must clear it or future timestamps stall. RX page-pool recycling assumes descriptor and page offsets stay consistent across page sizes. `wx_clean_rx_ring()` syncs and returns pages between `next_to_clean` and `next_to_alloc`; partially initialized rings after allocation failures need careful unwind. Interrupt fallback disables VMDq/RSS, changing queue topology after an MSI-X allocation failure. Feature changes can reset hardware, toggle RSS, or force paired C-tag/S-tag VLAN capabilities. `wx_set_ring()` intentionally keeps old resources if new allocation fails, but callers must reconfigure hardware after successful resizing.

## Test signals
Exercise with traffic under multiple MTUs, VLAN C-tag/S-tag insertion/stripping/filtering, checksum offload on/off, TSO/GSO including encapsulated packets, PTP TX/RX timestamp traffic, RSS queue distribution, MSI-X and forced MSI fallback, ring resize via ethtool, feature toggles, and open/close/reset loops. Watch for DMA mapping errors, page-pool leaks, stuck subqueues, NAPI budget stalls, Tx timestamp timeout counters, stats consistency from `ip -s link` and `ethtool -S`, and absence of IRQ use-after-free during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.h

## Purpose
`wx_lib.h` declares the shared datapath, interrupt, resource, statistics, feature, ring, and service-timer API implemented by `wx_lib.c`. Device-specific WangXun drivers include it to reuse common netdev operations and lifecycle helpers.

## Important APIs, types, and functions
The declarations cover packet type decoding, RX buffer refill, descriptor accounting, transmit entry point, NAPI enable/disable, interrupt scheme reset/init/clear, MSI-X clean handler, IRQ free, ISB resource management, EITR writes, vector configuration, ring cleanup/resource setup/free, stats64 collection, netdev feature set/fix/check, ring resizing, and service event/timer helpers.

## Control flow and behavior
The header has no executable flow. Its exported functions imply the lifecycle used by consumers: initialize interrupt scheme, setup resources, configure hardware vectors, enable NAPI, transmit and poll, collect stats, handle feature changes, schedule service work, then disable NAPI and free resources/interrupts during close or reset.

## State and persistence
The header owns no state. All operations mutate `struct wx`, `struct wx_ring`, `struct wx_q_vector`, SKB/DMA resources, netdev features, or timer/workqueue state in the implementation.

## Dependencies and integration points
It relies on libwx core type definitions and Linux netdevice, IRQ, SKB, and feature types being visible to includers. It is a common boundary between the hardware layer (`wx_hw.c`), PTP layer (`wx_ptp.c`), VF helpers, and device-specific netdev ops.

## Risks and edge cases
Because the API exposes lifecycle-sensitive operations, consumers can misuse it by freeing resources while NAPI is enabled, resizing rings while queues are live, or configuring vectors before interrupt allocation. Kernel prototype changes for `ndo_features_check`, stats64, timer, or IRQ handlers would require matching updates here.

## Test signals
Build tests should catch prototype drift. Runtime validation should confirm each consumer calls setup/free pairs in the right order and that netdev ops wired to these prototypes survive reset, feature toggles, and close/open cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.c

## Purpose
`wx_mbx.c` implements the PF/VF mailbox transport used by WangXun SR-IOV devices. It provides lock, read, write, acknowledgment, reset detection, and posted-message polling helpers for both PF-to-VF and VF-to-PF directions.

## Important APIs, types, and functions
PF-side exports are `wx_write_mbx_pf`, `wx_read_mbx_pf`, `wx_check_for_rst_pf`, `wx_check_for_msg_pf`, and `wx_check_for_ack_pf`. VF-side exports are `wx_read_posted_mbx`, `wx_write_posted_mbx`, `wx_check_for_rst_vf`, `wx_check_for_msg_vf`, `wx_read_mbx_vf`, `wx_write_mbx_vf`, and `wx_init_mbx_params_vf`. Internal helpers acquire PF/VF ownership bits, read and cache VF mailbox cause bits, poll for ack/message completion, and clear interrupt cause registers.

## Control flow and behavior
PF write validates size, obtains PF ownership of the VF mailbox, clears stale msg/ack causes, writes dwords into `WX_PXMBMEM(vf)`, mirrors status in the final mailbox word, and sets `WX_PXMAILBOX_STS` to interrupt the VF. PF read obtains the same lock, copies mailbox dwords, mirrors ACK, and writes `WX_PXMAILBOX_ACK`. VF write obtains VFU ownership, clears stale PF status/ack bits, writes `WX_VXMBMEM`, and writes `WX_VXMAILBOX_REQ` to notify PF. VF read obtains the lock, copies `WX_VXMBMEM`, and writes `WX_VXMAILBOX_ACK`. Posted helpers add polling for message or ack using `mbx->udelay` and `mbx->timeout`.

## State and persistence
Mailbox state is split between hardware mailbox registers and `wx->mbx`. `wx->mbx.size`, `mailbox`, `udelay`, and `timeout` define VF transport parameters. `wx->mbx.mailbox` caches PF-to-VF bits so read-clear semantics do not lose reset/status/ack events before the driver consumes them. VF initialization allocates one `vf_data_storage` object and initializes mailbox limits.

## Dependencies and integration points
The file depends on `wx_type.h` register accessors and `wx_mbx.h` constants. It is used by SR-IOV PF code handling VF requests and by VF code negotiating/resetting with the PF. It also interacts with `wx_vf`/`wx_sriov` logic through message IDs declared in the header.

## Risks and edge cases
Mailbox lock acquisition retries only five times, so transient contention can surface as `-EBUSY`. PF operations trust the caller's VF index to address valid mailbox registers. Size handling differs by direction: writes reject oversize messages, reads truncate to mailbox size. Lost or stale ACK/STS bits can break request/response sequencing if callers do not check returns. Posted polling uses atomic polling and fixed microsecond delays; firmware or PF stalls become timeouts. `wx_init_mbx_params_vf()` allocates `vfinfo`, so teardown must free it elsewhere.

## Test signals
SR-IOV tests should cover VF reset notification, API negotiation, VF MAC/VLAN/multicast messages, PF notifications, posted writes with ACK, posted reads after PF status, oversize message rejection, mailbox contention, and PF reset while a VF is polling. Useful signals are absence of mailbox timeout logs, correct ACK/REQ interrupt cause clearing, and stable VF recovery after PF reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.h

## Purpose
`wx_mbx.h` defines the shared SR-IOV PF/VF mailbox register layout, message flags, mailbox protocol IDs, VF request opcodes, PF notification opcodes, queue-info fields, multicast mode enum, and mailbox helper prototypes.

## Important APIs, types, and functions
Key constants include `WX_VXMAILBOX_SIZE`, PF registers `WX_PXMAILBOX()` and `WX_PXMBMEM()`, VF registers `WX_VXMAILBOX` and `WX_VXMBMEM`, reset cause registers `WX_VFLRE()`/`WX_VFLREC()`, interrupt cause registers `WX_MBVFICR()`, mailbox ownership/status bits, and message type bits `WX_VT_MSGTYPE_ACK`, `NACK`, and `CTS`. `enum wx_pfvf_api_rev` captures supported PF/VF API versioning. `enum wxvf_xcast_modes` captures VF multicast/promiscuous modes. The prototypes expose PF and VF read/write/check helpers plus posted mailbox operations.

## Control flow and behavior
No executable flow exists in this header. The constants define the protocol consumed by `wx_mbx.c` and higher-level SR-IOV message handlers: VFs send opcodes such as reset, set MAC, set multicast, set VLAN, API negotiate, get queues, get RSS RETA/key, update xcast mode, get link state, and get firmware version; PFs answer with ACK/NACK/CTS and notification messages.

## State and persistence
The header owns no state. It defines hardware register addresses and bit assignments that persist in device mailbox registers until read/cleared by PF or VF logic.

## Dependencies and integration points
It relies on Linux bit macros such as `BIT()` and `GENMASK()` and on `struct wx` being visible for prototypes. It is included by mailbox transport and SR-IOV control-plane code.

## Risks and edge cases
Any mismatch between these constants and hardware/firmware protocol breaks PF/VF communication. Message size is fixed to 15 dwords of payload plus a mirrored status word, so new protocol messages must fit or define fragmentation elsewhere. The misspelled `WX_PF_NOFITY_*` names are ABI-internal but can propagate into call sites. API revision values must match VF expectations.

## Test signals
Build tests should catch missing prototypes and constants. Runtime SR-IOV tests should verify each declared VF opcode is encoded/decoded correctly, ACK/NACK/CTS bits are preserved, queue-info fields match PF allocation, and xcast mode requests result in expected receive filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.c

## Purpose
`wx_ptp.c` implements Precision Time Protocol hardware clock support for libwx devices. It registers a PHC, maintains cyclecounter/timecounter conversion, supports frequency and time adjustment, configures hardware timestamp filters, handles TX/RX timestamps, detects timestamp hangs, supports 1PPS/perout on capable MACs, and integrates timestamp stats with ethtool.

## Important APIs, types, and functions
Exported functions are `wx_ptp_check_pps_event`, `wx_ptp_reset_cyclecounter`, `wx_ptp_reset`, `wx_ptp_init`, `wx_ptp_suspend`, `wx_ptp_stop`, `wx_ptp_rx_hwtstamp`, `wx_hwtstamp_get`, and `wx_hwtstamp_set`. Important internal callbacks populate `struct ptp_clock_info`: `wx_ptp_adjfine`, `wx_ptp_adjtime`, `wx_ptp_gettimex64`, `wx_ptp_settime64`, `wx_ptp_do_aux_work`, and conditionally `wx_ptp_feature_enable`. Timestamp conversion uses `wx->hw_cc`, `wx->hw_tc`, and `wx->hw_tc_lock`. PPS support uses `wx_ptp_setup_sdp()`, `wx_ptp_trigger_calc()`, and firmware `wx_set_pps()`.

## Control flow and behavior
`wx_ptp_init()` initializes the seqlock, creates or reuses a PTP clock, clears timestamp counters, resets PTP hardware, and marks PTP running. `wx_ptp_reset()` reapplies timestamp mode, recalculates the cyclecounter increment for current MAC/link speed, clears SYSTIME registers, initializes the timecounter to real time, schedules auxiliary work, and re-enables SDP PPS if configured. TX timestamp flow begins in `wx_lib.c` when a TX SKB requests hardware timestamping; this file's aux worker polls `WX_TSC_1588_CTL_VALID`, reads timestamp registers, converts to hwtstamp, completes the SKB, or times out and clears state. RX timestamp flow is called from RX packet processing when a descriptor has the timestamp bit, reads latched registers if valid, and attaches the converted timestamp. Hardware timestamp set/get validate netdev running state and configure TX/RX filters.

## State and persistence
PTP state lives in `struct wx`: `ptp_clock`, `ptp_caps`, `hw_cc`, `hw_tc`, `hw_tc_lock`, `base_incval`, `tstamp_config`, `ptp_tx_skb`, `ptp_tx_start`, PPS fields, last overflow/RX check timestamps, PTP flags, and timestamp counters. Hardware state includes SYSTIME, increment, TX/RX timestamp control/message/filter registers, SDP target registers, and interrupt enables. Timecounter state is protected by a seqlock and must be refreshed periodically to avoid wrap issues.

## Dependencies and integration points
It depends on Linux PTP clock, clocksource/timecounter, timestamping, SKB hwtstamp, PCI, and ptp classifier constants. It integrates with `wx_lib.c` for TX and RX timestamp hooks, `wx_ethtool.c` for timestamp capability/stat reporting, and `wx_hw.c` firmware host-interface PPS command. Device-specific interrupt handlers must call `wx_ptp_check_pps_event()` when relevant PTP/PPS interrupt status is present.

## Risks and edge cases
Only one TX hardware timestamp can be in flight; concurrent timestamp requests increment skipped counters. If hardware never latches TX valid, `wx_ptp_tx_hang()` clears state after one second and increments timeouts. RX timestamp registers can latch after a dropped packet; `wx_ptp_rx_hang()` clears the high register after five seconds without RX progress. `wx_ptp_readtime()` retries high/low reads, but the second rollover path calls `ptp_read_system_prets()` twice, which should be reviewed against expected pre/post timestamp pairing. PPS supports only 1 second periods and no absolute phase; invalid duty cycle or phase requests fail. `wx_hwtstamp_get/set()` reject calls while the netdev is down.

## Test signals
Use `phc2sys`, `ptp4l`, `testptp`, and `hwstamp_ctl` to validate PHC registration, get/set/adjfine/adjtime behavior, TX and RX timestamp delivery, filter normalization, suspend/resume, reset after link speed changes, and PPS/perout on supported MACs. Watch ethtool PTP stats for `tx_hwtstamp_pkts`, skipped, timeout, error, and RX-cleared counters. Kernel logs should not show repeated timestamp hang clearing under normal PTP traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.h

## Purpose
`wx_ptp.h` declares the libwx PTP and hardware timestamp API implemented by `wx_ptp.c`. It lets datapath, ethtool, interrupt, suspend/resume, and device lifecycle code interact with PHC support without depending on implementation internals.

## Important APIs, types, and functions
The header declares PPS interrupt handling, cyclecounter reset, full PTP reset/init/suspend/stop, RX hardware timestamp attachment, and netdev hwtstamp get/set operations. It uses `struct wx`, `struct sk_buff`, `struct net_device`, `struct kernel_hwtstamp_config`, and `struct netlink_ext_ack`.

## Control flow and behavior
There is no executable flow. The declarations imply lifecycle order: initialize PTP after device state is ready, reset the cyclecounter on init/reset/link-speed change, call RX timestamp helper from packet receive, call PPS event helper from interrupt handling, suspend or stop PTP during power/device teardown, and expose hwtstamp get/set through netdev timestamp operations.

## State and persistence
The header owns no state. The implementation stores PHC, timestamp config, cyclecounter/timecounter, PPS, and TX/RX timestamp state in `struct wx`.

## Dependencies and integration points
Consumers need Linux networking and timestamping types. `wx_lib.c` calls `wx_ptp_rx_hwtstamp()` and schedules TX timestamp work through the registered PTP clock; ethtool code reports capabilities based on `wx->ptp_clock`; hardware code supplies PPS firmware programming.

## Risks and edge cases
Consumers must guard calls with correct device state. For example, hwtstamp get/set expects the netdev to be running, RX timestamp helper is meaningful only when descriptor timestamp bits are present, and stop/suspend must run before freeing resources that PTP work might touch. Prototype drift with kernel hwtstamp APIs would break netdev operation wiring.

## Test signals
Build tests should cover all includers. Runtime tests should validate PTP init/stop across open/close, hwtstamp configuration while up and rejection while down, RX timestamp delivery from the datapath, and PPS event handling from interrupt paths on capable hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_ptp.h -->
