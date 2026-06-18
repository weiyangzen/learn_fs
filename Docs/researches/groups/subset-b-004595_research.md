# Research Group subset-b-004595

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.c

Purpose: Implements the Pensando Ionic receive-filter cache and firmware synchronization path for MAC, VLAN, MAC/VLAN, and packet-class steering filters. It keeps a local hash-table mirror of desired filters so netdev address-list changes can be batched, retried, replayed after reset, and reconciled with admin-queue filter IDs returned by firmware.

Important APIs and functions: `ionic_rx_filters_init()` initializes the per-LIF spinlock and `by_hash`/`by_id` hlist arrays; `ionic_rx_filters_deinit()` frees all cached filters. `ionic_rx_filter_save()` inserts or refreshes a filter from an `IONIC_CMD_RX_FILTER_ADD` admin context, indexing by match key and firmware `filter_id`. `ionic_rx_filter_by_vlan()`, `ionic_rx_filter_by_addr()`, and `ionic_rx_filter_rxsteer()` are lookup helpers. `ionic_lif_list_addr()` updates desired MAC-list state without immediately posting firmware commands. `ionic_lif_addr_add()`, `ionic_lif_addr_del()`, `ionic_lif_vlan_add()`, and `ionic_lif_vlan_del()` are public add/delete wrappers. `ionic_rx_filter_sync()` copies pending NEW/OLD entries into temporary lists, performs deletes first, then adds. `ionic_rx_filter_replay()` reissues saved add commands after device recovery and rebuilds the ID hash with newly assigned firmware IDs.

Control flow: Address-list changes mark filters `NEW`, `SYNCED`, or `OLD` under `lif->rx_filters.lock`, then set `IONIC_LIF_F_FILTER_SYNC_NEEDED`. Sync scans the ID-indexed cache, copies pending work to local `sync_item` lists, releases the lock, deletes OLD filters to make capacity, and then adds NEW filters. Add operations pre-create or pre-mark cache entries as `SYNCED` before posting the admin command so parallel add/delete requests have a local object to mutate; completion updates counters and stores the firmware filter ID. Delete removes the local object first, then sends `IONIC_CMD_RX_FILTER_DEL` unless the object was never successfully synced.

State and persistence behavior: The persistent state is only in memory on `struct ionic_lif`: the two hlist indexes, filter state, firmware filter IDs, per-kind counters (`nvlans`, `nucast`, `nmcast`), and discovered `max_vlans`. Replay assumes the saved `ionic_rx_filter_add_cmd` is authoritative and replaces filter IDs after firmware recreation. Recoverable admin-queue failures such as `-ENOSPC`, `-ENXIO`, `-ETIMEDOUT`, `-EAGAIN`, and `-EBUSY` generally leave filters pending for later sync instead of surfacing hard errors.

Dependencies and integration points: Depends on Ionic admin queue helpers (`ionic_adminq_post_wait*`, `ionic_adminq_netdev_err_print`), LIF state bits, netdev logging, Linux `hlist` and spinlock APIs, firmware command structures from the Ionic device interface, and Ethernet helpers such as `is_multicast_ether_addr()`. It integrates with netdev unicast/multicast/VLAN list management and with reset/recovery paths through replay.

Risks: Several hash keys use `*(u32 *)addr` on MAC addresses, which relies on unaligned access tolerance and hashes only the first four bytes; correctness is preserved by full `memcmp`, but bucket distribution can collide. Counter updates happen when add/delete paths believe firmware state changed; unusual races where an add is requested while a delete is pending are handled by state checks but remain high-risk. Capacity handling for VLANs learns `max_vlans` only after firmware reports `-ENOSPC`, so the first overflow path is intentionally speculative. `ionic_rx_filter_sync()` allocates temporary sync items with `GFP_ATOMIC`; allocation failure truncates the local snapshot and leaves remaining filters pending.

Test signals: Exercise netdev MAC and VLAN add/delete under concurrent address-list updates, reset/replay after filters are installed, firmware `-ENOSPC` for VLAN and MAC filter limits, transient admin-queue failures, multicast versus unicast counters, and deletion of never-synced filters. Useful instrumentation includes dynamic debug hex dumps in replay and `netdev_dbg/info` messages in add/delete failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.h

Purpose: Declares the Ionic receive-filter data model, hash-table sizing, state machine, and public filter-management entry points used by the LIF and netdev address/VLAN paths.

Important APIs and types: `enum ionic_filter_state` defines `SYNCED`, `NEW`, and `OLD` for desired-versus-firmware state reconciliation. `struct ionic_rx_filter` stores local flow ID, firmware filter ID, target RX queue index, state, saved add command, and two hlist nodes. `struct ionic_rx_filters` stores a spinlock plus 1024-bucket `by_hash` and `by_id` indexes. The header declares init/deinit, save, lookup, replay, sync, list-address, and VLAN add/delete functions. `IONIC_RXQ_INDEX_ANY` is the wildcard RX queue selector.

Control flow: The header establishes that callers use lookup helpers for local cache checks, update filter state through `ionic_lif_list_addr()` or add/delete wrappers, and rely on `ionic_rx_filter_sync()` to reconcile pending state with firmware. The two indexes allow lookups both by logical match key and by firmware deletion ID.

State and persistence behavior: State is in-memory only and owned by `struct ionic_lif`. The saved `struct ionic_rx_filter_add_cmd` inside each entry is the replay source after reset. Hash constants define fixed-size tables using `hash_32()` and low bits of firmware IDs.

Dependencies and integration points: Requires `struct ionic_lif`, `struct ionic_admin_ctx`, `struct ionic_rx_filter_add_cmd`, hlist, and spinlock definitions from surrounding Ionic/Linux headers. It is included by the implementation and by LIF code that needs address/VLAN filter management.

Risks: Any change to firmware command layout or match-type enumeration affects the cached `cmd` member. The fixed hash-table size is simple but does not prevent long collision chains. Callers must respect locking expectations around local list mutation.

Test signals: Compile coverage for all declared functions, lockdep under address-list churn, and reset tests that confirm cached add commands are replayable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.c

Purpose: Provides the Ionic ethtool statistics group implementation. It defines ordered stat descriptors for LIF software counters, port hardware counters, TX queues, and RX queues, then exposes functions for ethtool string, count, and value retrieval through `ionic_stats_groups`.

Important APIs and functions: Descriptor arrays include `ionic_lif_stats_desc`, `ionic_port_stats_desc`, `ionic_tx_stats_desc`, and `ionic_rx_stats_desc`. `ionic_get_lif_stats()` aggregates per-queue software counters plus netdev `rtnl_link_stats64` error/drop counters. `ionic_sw_stats_get_count()` calculates total rows, adding extra hardware timestamp queues when present. `ionic_sw_stats_get_strings()` emits ethtool names in the same order values are read. `ionic_sw_stats_get_values()` copies aggregated LIF stats, little-endian port stats, TX queue stats, and RX queue stats. `ionic_stats_groups[]` exports the group interface.

Control flow: Count, strings, and values share one strict ordering: aggregate LIF stats, port stats, all normal TX queues, optional hwstamp TX queue, all normal RX queues, optional hwstamp RX queue. The value path first aggregates LIF stats from `lif->txqstats` and `lif->rxqstats`, calls `ionic_get_stats64()` for netdev error counters, then reads port stats from `lif->ionic->idev.port_info->stats`.

State and persistence behavior: This file does not own counters; it reads live in-memory queue statistics and device-shared port statistics. There is no persistence or reset logic here. The stat descriptors store byte offsets into target structures, so the ABI is the descriptor order plus ethtool string names.

Dependencies and integration points: Depends on ethtool string helpers, `ionic_lif`, queue stats structures, port stats layout, `ionic_get_stats64()`, and macros from `ionic_stats.h`. The exported group is consumed by Ionic ethtool code that iterates stats groups.

Risks: Descriptor order must stay aligned between names and values; adding a counter in one array changes ethtool output shape. Offset-based reads assume every descriptor names a `u64` or `__le64` field of the matching structure. Optional hwstamp queues can duplicate indices outside `real_num_tx_queues`, so consumers must accept variable counts.

Test signals: Validate `ethtool -S` count and names against values, with and without hardware timestamp queues, after TX/RX/XDP traffic. Exercise endian conversion of port stats and check that netdev drop/error counters map to the expected LIF software stat names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.h

Purpose: Defines the small descriptor and interface layer used by Ionic statistics providers to expose ethtool strings, counts, and values.

Important APIs and types: `struct ionic_stat_desc` stores an ethtool stat name and byte offset. `IONIC_*_STAT_DESC()` macros build descriptors for port, LIF, TX, RX, queue, CQ, interrupt, and NAPI structures. `struct ionic_stats_group_intf` defines callbacks for group-specific string/value/count retrieval. `IONIC_READ_STAT64()` and `IONIC_READ_STAT_LE64()` read native and little-endian 64-bit counters via descriptor offsets. `ionic_stats_groups` and `ionic_num_stats_grps` are exported.

Control flow: The header does not implement runtime control flow; it provides the generic offset-table mechanism used by `ionic_stats.c` and potentially other stats groups.

State and persistence behavior: No state is stored here beyond descriptor constants compiled into the driver. The macros intentionally bind field names to offsets at compile time.

Dependencies and integration points: Requires `offsetof`, `ETH_GSTRING_LEN`, and the target stats structure definitions to be visible where descriptors are built. It is part of the Ionic ethtool integration boundary.

Risks: Offset-based generic reading bypasses type checking after descriptor construction; using a descriptor with the wrong base structure silently reads the wrong memory. `IONIC_READ_STAT64()` assumes alignment and `u64` field width.

Test signals: Compile-time coverage for descriptor field names, ethtool stats smoke tests, and checks that native versus little-endian read macros are used for the correct backing structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.c

Purpose: Implements the Ionic fast path for transmit, receive, XDP, DMA mapping, completion cleanup, RX ring refill, NAPI polling, interrupt coalescing feedback, TSO/checksum offload, VLAN insertion/stripping, and hardware timestamp queues.

Important APIs and functions: Public entry points are `ionic_start_xmit()`, `ionic_xdp_xmit()`, `ionic_rx_fill()`, `ionic_rx_empty()`, `ionic_tx_empty()`, `ionic_tx_flush()`, `ionic_rx_service()`, `ionic_rx_napi()`, `ionic_tx_napi()`, and `ionic_txrx_napi()`. Key helpers include `ionic_txq_post()` with `dma_wmb()` ordering, doorbell poke workarounds, RX page-pool buffer helpers, `ionic_run_xdp()`, `ionic_rx_clean()`, `ionic_tx_map_skb()`, `ionic_tx_clean()`, `ionic_tx_descs_needed()`, `ionic_tx_tso()`, `ionic_tx_calc_csum()`, and `ionic_tx_calc_no_csum()`.

Control flow: RX NAPI services CQ entries with color checking and completion-index validation, cleans one queue descriptor per completion, optionally runs XDP first, then either drops/redirects/transmits the XDP frame or builds/copybreaks an SKB for GRO. After polling, it refills the RX ring from the page pool and flushes pending XDP redirects. TX starts by selecting the netdev queue, calculating needed descriptors, maybe stopping the queue, mapping the SKB, programming either TSO or checksum/no-checksum descriptors, posting with doorbell semantics, and later freeing DMA/SKB state from TX completions. Combined TXRX NAPI services TX completions first, then RX completions, and returns RX work done to the NAPI core.

State and persistence behavior: Runtime state lives in Ionic queues, completion queues, page-pool buffers, descriptor-info arrays, per-queue stats, queue indices, doorbell deadlines, NAPI structures, and optional hwstamp queues. There is no disk persistence. Buffer ownership transitions are critical: RX pages move from page pool to descriptors, to XDP/SKB/GRO, then are recycled or unlinked; TX mappings are retained in descriptor info until completion cleanup.

Dependencies and integration points: Depends on Linux networking core (`netdev_txq_maybe_stop`, GRO, SKB offloads), XDP APIs, page-pool DMA helpers, NAPI, DIM (`net_dim`), DMA mapping APIs, VLAN helpers, checksum helpers, Ionic queue/CQ layout, CMB ring support, PHC timestamp conversion, and interrupt credit routines.

Risks: This is a high-risk concurrency and ownership file. DMA ordering before doorbells, map/unmap symmetry, page-pool recycling, XDP fragmented-frame handling, and queue stop/wake thresholds must remain exact. `ionic_tx_tso()` walks mapped buffers across synthetic descriptors; descriptor-info bookkeeping intentionally keeps only the first TSO descriptor owning the SKB/mappings. The XDP path must unlink RX buffers only when ownership transfers to TX or redirect. Hardware timestamp traffic uses a separate TX queue and drops when it cannot post immediately, which is intentional but observable.

Test signals: Run normal TCP/UDP traffic, checksum offload, VLAN TX/RX, TSO/GSO with fragmented SKBs, jumbo MTU, RX copybreak boundary, XDP PASS/DROP/TX/REDIRECT including fragmented XDP frames, page-pool recycling, queue full/backpressure, reset cleanup, combined and split interrupt modes, DIM/coalescing behavior, and hardware timestamp TX/RX. Watch per-queue stats (`dma_map_err`, `alloc_err`, XDP counters, checksum counters, hwstamp counters) and queue stop/wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.h

Purpose: Declares the Ionic TX/RX fast-path entry points used by queue setup, netdev operations, NAPI registration, XDP ndo hooks, and reset/teardown code.

Important APIs: Declares RX management (`ionic_rx_fill`, `ionic_rx_empty`, `ionic_rx_service`), TX management (`ionic_tx_flush`, `ionic_tx_empty`, `ionic_start_xmit`), NAPI pollers (`ionic_rx_napi`, `ionic_tx_napi`, `ionic_txrx_napi`), and XDP transmit (`ionic_xdp_xmit`). It forward-declares `struct bpf_prog` so RX fill can account for XDP headroom without forcing BPF includes into all users.

Control flow: Callers wire these functions into netdev and NAPI operations: TX packets enter through `ionic_start_xmit`, external XDP frames through `ionic_xdp_xmit`, interrupts schedule one of the NAPI pollers, and teardown invokes empty/flush helpers.

State and persistence behavior: No state is stored in the header. It defines module boundaries over `struct ionic_queue`, `struct ionic_cq`, `struct napi_struct`, and netdev objects.

Dependencies and integration points: Integrates the Ionic implementation with Linux netdev, NAPI, and XDP APIs. Include order must provide Ionic queue/CQ structures to callers.

Risks: Signature changes affect netdev/NAPI hook registration across the driver. The presence of both split and combined NAPI pollers means setup code must bind the correct one for the interrupt mode.

Test signals: Build coverage and runtime smoke tests for queue bring-up/teardown, NAPI mode selection, and XDP ndo registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Kconfig

Purpose: Defines Kconfig menu entries for QLogic/Marvell Ethernet drivers under `NET_VENDOR_QLOGIC`, including NetXen, QLA3XXX, QLCNIC, QED core, QEDE, and related feature toggles.

Important options: `NET_VENDOR_QLOGIC` gates the vendor submenu and depends on PCI. `QLA3XXX`, `QLCNIC`, `NETXEN_NIC`, `QED`, and `QEDE` are driver tristates. `QLCNIC_SRIOV`, `QLCNIC_DCB`, `QLCNIC_HWMON`, and `QED_SRIOV` are feature bools with dependency/select logic. `QED` selects compression/checksum/devlink helpers; `QEDE` depends on `QED` and optional PTP support.

Control flow: Build configuration flow is hierarchical: disabling `NET_VENDOR_QLOGIC` hides all child prompts; enabling specific tristates controls whether subdirectories and modules are built by Makefiles.

State and persistence behavior: Kconfig state persists in kernel `.config`, not in the driver. Selected symbols determine compile-time feature inclusion.

Dependencies and integration points: Integrates with kernel PCI, firmware loader, DCB, HWMON, PCI_IOV, PTP, devlink, and Makefile `obj-$(CONFIG_...)` rules.

Risks: Dependency mistakes can expose drivers without required subsystems or hide valid hardware support. `default y` vendor/feature toggles influence distro kernel footprint.

Test signals: Kconfig matrix builds with QLogic vendor disabled, individual drivers built-in/module/disabled, and feature dependencies such as `QLCNIC=y` with `HWMON=m` to validate the explicit HWMON guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Makefile

Purpose: Connects QLogic Kconfig symbols to driver objects or subdirectories in the kernel build.

Important build rules: `obj-$(CONFIG_QLA3XXX) += qla3xxx.o`, `obj-$(CONFIG_QLCNIC) += qlcnic/`, `obj-$(CONFIG_NETXEN_NIC) += netxen/`, `obj-$(CONFIG_QED) += qed/`, and `obj-$(CONFIG_QEDE)+= qede/`.

Control flow: Kbuild includes object files or descends into subdirectories based on resolved `.config` symbols.

State and persistence behavior: No runtime state. Build artifacts depend on Kconfig values.

Dependencies and integration points: Integrates the vendor directory with top-level kernel networking Kbuild and the per-driver Makefiles.

Risks: Symbol/rule mismatch would silently omit a configured driver or build the wrong directory. The `CONFIG_QEDE` assignment has no space before `+=`, which is valid make syntax but easy to overlook in style checks.

Test signals: Build with each QLogic symbol as module and built-in; verify expected modules and objects are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/Makefile

Purpose: Defines the NetXen NIC module composition for `CONFIG_NETXEN_NIC`.

Important build rules: `obj-$(CONFIG_NETXEN_NIC) := netxen_nic.o` creates the module/built-in object. `netxen_nic-y` links `netxen_nic_hw.o`, `netxen_nic_main.o`, `netxen_nic_init.o`, `netxen_nic_ethtool.o`, and `netxen_nic_ctx.o`.

Control flow: Kbuild compiles and links all listed component objects into one `netxen_nic` driver when the symbol is enabled.

State and persistence behavior: No runtime state. The file defines static composition of the driver.

Dependencies and integration points: Integrates the files researched here with the rest of the NetXen implementation (`hw`, `main`, `init`).

Risks: Missing a component breaks unresolved symbols or removes required feature surfaces such as ethtool or context setup.

Test signals: Module build for `CONFIG_NETXEN_NIC=m`, built-in build for `=y`, and modpost symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic.h

Purpose: Central NetXen NIC driver header. It defines driver versioning, descriptor layouts, ring/context structures, firmware command ABI, board/flash constants, adapter state, minidump structures, function pointer hooks, lock helpers, and exported cross-file prototypes.

Important APIs and types: TX/RX descriptors include `cmd_desc_type0`, `rcv_desc`, and `status_desc` plus bitfield access macros for status and LRO completions. Host ring types include `nx_host_tx_ring`, `nx_host_rds_ring`, `nx_host_sds_ring`, and `netxen_recv_context`. Firmware context ABI types include `nx_hostrq_rx_ctx_t`, `nx_cardrsp_rx_ctx_t`, `nx_hostrq_tx_ctx_t`, and `nx_cardrsp_tx_ctx_t`. `struct netxen_adapter` is the main per-device object, combining PCI/netdev pointers, hardware context, ring configuration, callbacks, stats, firmware state, work items, coalescing config, and minidump state. Exported prototypes connect init, main, hardware, context, firmware, RX/TX, and ethtool modules.

Control flow: The header defines the contracts used by runtime files: main/init code allocates `netxen_adapter`, setup code fills callbacks and ring counts, context code allocates hardware rings and issues firmware context commands, data path uses descriptor macros, and ethtool reads/modifies fields through exported functions.

State and persistence behavior: Runtime persistent state is concentrated in `struct netxen_adapter`: link state, firmware version, flags/state bits, reset ownership, stats, ring counts, context IDs, DMA addresses, work items, MAC/IP lists, and minidump buffers. Flash/ROM constants identify persistent firmware and board data regions, but this header only names them.

Dependencies and integration points: Includes Linux PCI/netdevice/SKB/firmware/ethtool headers plus `netxen_nic_hdr.h` and `netxen_nic_hw.h`. It is the shared ABI between all NetXen source files and firmware CRB/CDRP interfaces.

Risks: Many structures are hardware/firmware ABI with explicit endian fields and alignment requirements; changing layout is dangerous. The header contains large sets of magic constants for board revisions, flash offsets, firmware commands, dump commands, and descriptor bitfields. Function pointers in `netxen_adapter` make revision-specific behavior indirect; setup must initialize them before use. `netxen_tx_avail()` relies on ring counters and a memory barrier.

Test signals: Compile all NetXen objects together, probe supported board revisions, create/destroy contexts, exercise TX/RX descriptors, firmware command paths, minidump setup/dump, ethtool operations, ring resize, and reset flows. Static checks should pay special attention to endian annotations and packed/aligned structure sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ctx.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ctx.c

Purpose: Implements NetXen firmware command submission, minidump template setup, PHY/MTU firmware commands, RX/TX firmware context creation/destruction, legacy P2 context initialization, and coherent hardware ring allocation/free.

Important APIs and functions: `netxen_issue_cmd()` serializes CDRP firmware commands under `netxen_api_lock()`, writes signature/arguments to CRB registers, polls for response, and optionally reads response arguments. Minidump helpers query template size, fetch the template via DMA, verify checksum, endian-convert it, and initialize `adapter->mdump`. `nx_fw_cmd_create_rx_ctx()` and `nx_fw_cmd_create_tx_ctx()` allocate DMA request/response blocks and issue create-context commands. `netxen_alloc_hw_resources()` allocates hardware context, TX descriptors, RX descriptor rings, status rings, and creates firmware contexts. `netxen_free_hw_resources()` destroys firmware/legacy contexts and frees coherent memory.

Control flow: Newer non-P2 devices allocate rings, set `__NX_FW_ATTACHED`, then create RX context followed by TX context through firmware. Firmware responses provide CRB addresses for producer/consumer and interrupt-mask registers, which are translated to MMIO pointers. P2 devices instead populate `struct netxen_ring_ctx`, write its physical address and signature into per-port CRB registers, and skip CDRP create commands. Free reverses this: destroy contexts or write D3 reset signature, wait 20 ms for DMA drain, then free coherent allocations.

State and persistence behavior: Updates adapter fields such as `recv_ctx->state`, `context_id`, `virt_port`, `tx_context_id`, ring CRB pointers, `recv_ctx->hwctx`, `tx_ring->hw_consumer`, `__NX_FW_ATTACHED`, and minidump fields. No disk persistence, but firmware context state persists on the card until destroyed/reset.

Dependencies and integration points: Depends on `NXRD32/NXWR32`, PCI coherent DMA allocation, firmware CRB constants, semaphore locks, revision checks, ring counts from adapter setup, and NetXen main reset paths. Public functions are called from device open/close, MTU/link operations, ethtool dump setup, and PHY access paths.

Risks: Firmware command polling can block up to `NX_OS_CRB_RETRY_COUNT` milliseconds and maps firmware failures to Linux errors inconsistently (`NX_RCODE_*` versus `-EIO`). Error unwinding relies on `netxen_free_hw_resources()` handling partially allocated rings. CDRP request/response structures are DMA ABI; size, endian, and physical-address split mistakes break hardware bring-up. `netxen_get_minidump_template()` returns 0 even after logging a failed fetch unless callers inspect resulting state, so template validity depends heavily on checksum/setup flow.

Test signals: Probe/open/close on P2 and P3 hardware or emulation, forced allocation-failure unwinds, firmware timeout/fail responses, MTU command with inactive and active contexts, PHY read/write, minidump setup with unsupported firmware, context reset, and repeated open/close to verify DMA memory and `__NX_FW_ATTACHED` state do not leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ethtool.c

Purpose: Implements the NetXen ethtool operations surface: driver info, link settings, register dumps, EEPROM reads, ring sizing, pause parameters, diagnostics, stats, Wake-on-LAN, interrupt coalescing, and firmware minidump control/data extraction.

Important APIs and functions: `netxen_nic_get_drvinfo()` reports driver, version, firmware, and PCI bus info. Link operations map board type, port type, module type, and firmware capabilities into `ethtool_link_ksettings`, and set GBE link settings through `nx_fw_cmd_set_gbe_port()`. Register and EEPROM functions read CRB/MMIO/ROM data. Ringparam set validates power-of-two descriptor counts and calls `netxen_nic_reset_context()`. Pause operations read/write NIU registers. Diagnostics run register and link tests. Stats use offset descriptors against `struct netxen_adapter`. Coalesce operations configure P3 firmware coalescing. Dump operations enable/disable/force firmware dumps, change capture masks, and copy template plus captured dump data to ethtool.

Control flow: The exported `netxen_nic_ethtool_ops` table binds all callbacks. Most getters read adapter state and hardware registers directly. Mutating operations validate revision/port/capability, update adapter fields or registers, then sometimes restart the interface (`set_link_ksettings`) or reset context (`set_ringparam`). Dump extraction is single-consumer: after `get_dump_data()` copies data it frees `md_capture_buff` and clears `fw_mdump_rdy`.

State and persistence behavior: Reads and writes adapter link settings, ring counts, coalescing config, WOL register bits, minidump enable/capture-mask/readiness, and firmware reset owner flag. EEPROM reads expose flash contents but do not modify them. Ring changes persist in adapter memory and take effect through context reset.

Dependencies and integration points: Depends on Linux ethtool API, PCI name/device IDs, NetXen CRB/MMIO helpers, board constants, firmware command helpers, reset/open/stop netdev ops, ROM read helpers, and minidump state initialized by context/init code.

Risks: Many operations are hardware-revision specific; unsupported P2/P3 paths must reject cleanly. Ringparam validation rounds values and immediately updates adapter counts before reset, so reset failure handling in main code matters. Register dump assumes the adapter is up before reading most state. Dump control exposes force-reset keys through ethtool flags and must not leave stale dump buffers. Stats offset reads assume field sizes are exactly `u32` or `u64`.

Test signals: Run `ethtool -i`, `-k`-independent link queries, `ethtool -s` on supported GBE firmware, `ethtool -d`, `-e`, `-g/-G`, `-a/-A`, `-t`, `-S`, `-s wol`, `-c/-C`, and `--get-dump/--set-dump` across P2 and P3 devices, down/up netdev states, SFP module variations, and firmware dump ready/not-ready states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hdr.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hdr.h

Purpose: Provides the low-level NetXen hardware register map, CRB address mapping constants, PCI window constants, flash/ROMUSB instruction registers, NIU MAC/PHY registers, link-status helpers, firmware state registers, semaphore offsets, interrupt vector definitions, and legacy interrupt configuration structures.

Important APIs and definitions: Defines `netxen_crbword_t`, hub/agent IDs, CRB hub address macros, PCI CRB window mapping, NIU GB/XG/AP register address macros, MIU/SIU test-agent offsets, link-state and P3 speed macros, firmware version/capability registers, CDRP command registers, WOL and port-mode registers, DIMM capability decoders, device-state values, firmware error decoders, PCI semaphore offsets, and `NX_LEGACY_INTR_CONFIG`.

Control flow: This header has no executable control flow; other files use its constants to compute MMIO/CRB addresses and decode hardware register values. It is foundational for context setup, ethtool register reads, link tests, pause control, flash access, firmware command submission, and interrupt setup.

State and persistence behavior: Names hardware and firmware state locations rather than storing state. Registers named here can represent persistent flash data, live firmware status, interrupt state, port mode, WOL config, and device reset/error state.

Dependencies and integration points: Included by `netxen_nic.h` and hardware access code. It bridges driver code to NetXen ASIC register layout and PCI memory-window rules.

Risks: Constants are hardware ABI; an incorrect address can corrupt device state or read misleading diagnostics. Many macros compose addresses through large window offsets, so 32-bit/64-bit address assumptions and PCI function indexing are important. Legacy interrupt table values must match hardware function routing.

Test signals: Hardware smoke tests for register access, link-state decode, pause register writes, CDRP firmware commands, flash/ROM reads, interrupt delivery for all PCI functions, WOL configuration, and ethtool register dump consistency. Static review should verify address macros used by source files point into intended CRB windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hdr.h -->
