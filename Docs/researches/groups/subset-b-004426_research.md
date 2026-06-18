# Research: subset-b-004426

This grouped report covers the Fungible funeth Ethernet driver files and the Google gVNIC Kconfig, build, shared state, and admin queue protocol files listed in work item `subset-b-004426`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.h

## Purpose
Declares the funeth driver's devlink lifecycle API. The header is intentionally small: it exposes allocation, free, registration, and unregistration helpers so `funeth_main.c` can bind a PCI-backed `struct fun_ethdev`/`struct fun_dev` instance to Linux devlink before netdev ports are registered.

## APIs and Types
Exports `fun_devlink_alloc(struct device *dev)`, `fun_devlink_free(struct devlink *devlink)`, `fun_devlink_register(struct devlink *devlink)`, and `fun_devlink_unregister(struct devlink *devlink)`. It depends only on `<net/devlink.h>` and forward usage of `struct device` from included kernel headers.

## Control Flow and Integration
The header is consumed by the funeth probe/remove path. Probe allocates devlink first, retrieves the driver-private `fun_ethdev` via `devlink_priv()`, initializes the core PCI/admin device, creates netdev ports, restarts service work, and then registers devlink. Remove reverses that order by unregistering devlink before SR-IOV teardown, service stop, port destruction, device disable, and devlink free.

## State and Persistence
This header owns no persistent state itself. Its API implies devlink lifetime must dominate all devlink port objects attached to per-port netdevs. Incorrect lifetime ordering can leave registered `devlink_port` objects referring to freed private data.

## Dependencies and Risks
The implementation is elsewhere; this contract assumes allocation returns a devlink whose private area is sized for `struct fun_ethdev`. Risk centers on ordering: `fun_devlink_free()` must not run while registered ports or netdevices still reference the devlink. Test signals include PCI probe/remove with devlink visible under `devlink dev`, hot-unplug, and failure injection at each probe unwind label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ethtool.c

## Purpose
Implements the ethtool surface for funeth: link settings, pause/FEC, register dumps, interrupt coalescing, channel and ring sizing, RSS, timestamp capabilities, module EEPROM reads, and extensive per-queue/MAC statistics. It is the user-facing configuration and diagnostics layer over state maintained in `struct funeth_priv` and hardware admin port resources.

## Important APIs and Functions
`fun_set_ethtool_ops()` installs `fun_ethtool_ops`. Link helpers translate Fungible port capability bits to ethtool link modes and back (`fun_link_modes_to_ethtool()`, `fun_advert_modes()`, `fun_speed_to_link_mode()`). `fun_get_link_ksettings()` snapshots asynchronous link fields under `link_seq`; `fun_set_link_ksettings()`, `fun_set_pauseparam()`, `fun_restart_an()`, `fun_set_fecparam()`, and `fun_set_phys_id()` issue `fun_port_write_cmd()` updates. Queue controls include `fun_set_coalesce()`, `fun_set_channels()`, and `fun_set_ringparam()`, which call live queue replacement/resizing helpers in `funeth_main.c`. RSS is handled by `fun_get_rxfh()` and `fun_set_rxfh()` using `fun_config_rss()`.

## Control Flow
Most setters validate ethtool inputs against hardware capability bits before issuing admin commands. Channel changes call `fun_change_num_queues()` when the netdev is running, otherwise they update real queue counts directly. Ring depth changes require powers of two and minimum depth, then use `fun_replace_queues()` for live disruptive replacement before committing new depths to `fp`. RSS updates are applied immediately when the port is running and cached in `fp->rss_key`, `fp->indir_table`, and `fp->hash_algo` for later open.

## State and Persistence
Persistent driver state includes advertised link bits, RSS key/LUT, queue depths, coalescing values, message level, hardware timestamp config, and TLS counters. Statistics combine DMA-backed MAC counters (`fp->stats`) with synchronized per-queue `u64_stats_sync` counters and aggregate totals. The code assumes RTNL protection for ethtool callbacks that dereference live queue arrays.

## Dependencies and Integration Points
Depends on `fun_port.h` admin keys, `funeth_txrx.h` queue statistics, PCI BAR register layout compatible with NVMe register offsets, and ethtool kernel APIs. Integration with `funeth_main.c` is tight: queue resizing and RSS mutation rely on queue arrays and hardware RSS ids managed there.

## Risks and Test Signals
Key risks are partial live queue replacement failure, RSS indirection entries referencing removed queues, invalid FEC/pause capability combinations, stats string/count mismatches, and DMA stats area size consistency. Test with `ethtool -k/-c/-C/-l/-L/-g/-G/-x/-X/-S`, link mode and FEC changes on physical ports, virtual-port unsupported-operation paths, XDP enabled while collecting stats, and module EEPROM reads on physical ports only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.c

## Purpose
Implements optional kernel TLS transmit offload support for funeth when `CONFIG_TLS_DEVICE` is enabled. It creates a per-port hardware kTLS resource, registers `tlsdev_ops`, programs TLS contexts, removes them, and handles sequence resynchronization.

## Important APIs and Functions
`fun_ktls_init()` creates a `FUN_ADMIN_OP_KTLS` resource for `netdev->dev_port`, sets `fp->ktls_id`, installs `fun_ktls_ops`, and advertises `NETIF_F_HW_TLS_TX`. `fun_ktls_cleanup()` destroys the resource if present. `fun_ktls_add()` supports only TX direction, TLS 1.2, and AES-GCM-128; it sends key, IV, salt, record sequence, and TCP sequence via `FUN_ADMIN_SUBOP_MODIFY`. `fun_ktls_del()` sends a remove modify command. `fun_ktls_resync()` updates record sequence and TCP sequence for an existing hardware TLS id.

## Control Flow
Initialization is best-effort from `fun_create_netdev()`; failure leaves software TLS fallback. Add validates direction, protocol, and cipher, submits an admin command, zeroes key material with `memzero_explicit()`, then stores the returned hardware TLS id and `next_seq` in the socket driver context. Delete and resync are also admin modify commands keyed by `fp->ktls_id` and the per-socket `tlsid`.

## State and Persistence
Persistent state lives in `fp->ktls_id`, atomic TLS operation counters, and per-socket `struct fun_ktls_tx_ctx` (`tlsid`, `next_seq`). The Tx path in `funeth_tx.c` consumes this state to decide whether to tag a packet for hardware TLS or request/fallback to software encryption.

## Dependencies and Integration Points
Depends on Linux TLS device offload APIs and funeth admin command structures from `funeth.h`. It integrates with netdev features, `tls_driver_ctx()`, and Tx descriptor emission where `FUN_ETH_TX_TLS` and `struct fun_eth_tls` are appended.

## Risks and Test Signals
Risks include sequence tracking bugs causing plaintext/ciphertext mismatch, unsupported cipher fallback expectations, admin failure while feature bits are enabled, and key material lifetime. Test with TLS 1.2 AES-GCM-128 TX offload, out-of-order sequence resync, delete during socket close, module unload with active TLS sockets, and ethtool TLS counters (`tx_tls_ctx`, `tx_tls_del`, `tx_tls_resync`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.h

## Purpose
Defines the compile-time interface between funeth core/Tx code and optional kTLS transmit offload support.

## APIs and Types
Declares `struct fun_ktls_tx_ctx` with a big-endian hardware `tlsid` and host-order `next_seq`. When `CONFIG_TLS_DEVICE` is enabled, declares `fun_ktls_init()` and `fun_ktls_cleanup()`. Otherwise it supplies inline no-op stubs so the rest of the driver can call cleanup/init unconditionally.

## Control Flow and Integration
`funeth_main.c` initializes and cleans kTLS through this header; `funeth_tx.c` reads `struct fun_ktls_tx_ctx` via TLS core helpers when `tls_is_skb_tx_device_offloaded()` is true. The conditional stubs preserve build compatibility on kernels/configurations without TLS device offload.

## State and Persistence
The header defines per-TLS-socket offload state but does not allocate it. TLS core owns the memory for the driver context; funeth stores hardware ids and sequence cursor there.

## Dependencies and Risks
Depends on `<net/tls.h>` and the netdev type declarations available through kernel headers. The main risk is ABI mismatch between `TLS_DRIVER_STATE_SIZE_TX` expected by TLS core and the size required for `fun_ktls_tx_ctx`; the implementation must ensure the netdev advertises a compatible context size through TLS infrastructure. Test signals are successful builds with `CONFIG_TLS_DEVICE=y/m` and disabled, and runtime TLS offload add/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ktls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_main.c

## Purpose
Provides the core PCI/netdev driver for Fungible Ethernet devices. It manages PCI probe/remove, admin device enablement, port creation/destruction, netdev operations, link events, queue/IRQ lifecycle, RSS, XDP mode transitions, SR-IOV VF configuration, devlink ports, statistics DMA setup, and service-task reactions to resource changes.

## Important APIs and Functions
Netdev operations include `funeth_open()`, `funeth_close()`, `fun_start_xmit()`, stats, MTU/MAC changes, XDP setup/xmit, VF configuration, and hardware timestamp get/set. Admin helpers include `fun_port_write_cmds()`, `fun_port_read_cmds()`, `fun_config_rss()`, `fun_destroy_rss()`, `fun_port_create()`, `fun_vi_create()`, and `fun_create_and_bind_tx()`. Queue lifecycle helpers include `fun_alloc_queue_irqs()`, `fun_alloc_rings()`, `fun_advance_ring_state()`, `fun_up()`, `fun_down()`, `fun_replace_queues()`, and `fun_change_num_queues()`. PCI entry points are `funeth_probe()`, `funeth_remove()`, and `funeth_sriov_configure()`.

## Control Flow
Probe allocates devlink, enables the `fun_dev` admin core with admin SQ/CQ/RQ depths, queries port count, creates each netdev, restarts service work, and registers devlink. Netdev creation computes maximum/default queue counts, creates a port resource, binds port events to admin CQ, reads MAC/capabilities/advertising/MTU, initializes RSS/stats DMA, registers a devlink port, optionally enables kTLS, then registers the netdev. Open allocates IRQ-backed rings, creates hardware queues if needed, creates a VI, publishes queue arrays with RCU, enables IRQ/NAPI, binds RSS or single CQ, writes stats DMA and enable keys, then starts Tx queues. Close disables the port, carrier, Tx queues, RSS, VI, IRQs, and frees rings.

## State and Persistence
Key persistent state lives in `struct funeth_priv`: admin/device pointers, `netdev`, port id, queue arrays, IRQ XArray, queue depths, RSS DMA/config/hardware id, link snapshot fields protected by `seqcount_t`, stats DMA area, XDP program/count, kTLS id/counters, and SR-IOV vport state under `fun_ethdev.state_mutex`. Live Rx/XDP queue pointers use RCU publication and `synchronize_net()` during teardown or replacement.

## Dependencies and Integration Points
Depends on funeth admin protocol definitions, `fun_queue` SQ/CQ helpers, devlink, PCI/MSI-X, netdevice, XDP/BPF, TLS, SR-IOV, and ethtool. `fun_event_cb()` consumes async admin CQ notifications for link state and resource count changes; `fun_service_cb()` creates/destroys ports when the device reports resource changes.

## Risks and Test Signals
High-risk areas are live queue resizing with mixed old/new queues, IRQ state transitions, RCU queue pointer replacement, RSS table rollback on admin failure, XDP enter/exit ordering, probe unwind labels, and stats DMA allocation/free size symmetry. Test signals include probe/remove/hotplug, open/close loops, `ethtool -L/-G` while traffic runs, XDP attach/detach/redirect, SR-IOV enable/disable and VF MAC/VLAN/rate, link notifications, kdump one-queue mode, and fault injection in admin commands and allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_rx.c

## Purpose
Implements the funeth receive data path, Rx buffer/page management, CQE processing, XDP receive actions, GRO delivery, Rx queue allocation, and Rx device resource creation/destruction.

## Important APIs and Functions
Externally used functions are `fun_rxq_napi_poll()`, `fun_rxq_set_bpf()`, `funeth_rxq_create()`, `fun_rxq_create_dev()`, and `funeth_rxq_free()`. Internal helpers manage page cache reuse (`cache_offer()`, `cache_get()`, `refresh_refs()`), page allocation/freeing, packet gathering (`get_buf()`, `fun_gather_pkt()`), XDP execution (`fun_run_xdp()`), CQ phase handling, and packet handoff (`fun_handle_cqe_pkt()`).

## Control Flow
NAPI polling calls `fun_process_cqes()`, which checks CQ phase tags, uses `dma_rmb()` before reading descriptors, handles packets up to budget, then flushes pending XDP TX or redirect operations. Packet handling advances the CQ, gathers one or more page fragments from the RQ, optionally runs XDP when configured headroom matches, builds either a linear skb with `napi_build_skb()` or a frags skb with `napi_get_frags()`, sets hash/checksum/timestamp metadata, traces, and submits to GRO. RQ doorbells are written when enough buffers have been consumed.

## State and Persistence
`struct funeth_rxq` tracks CQ/RQ rings, DMA addresses, current buffer and offset, spare buffer, cached reusable buffers, headroom, XDP program, stats, phase, NAPI pointer, and hardware ids. The page reuse model takes a large batch of page references to avoid frequent refcount writes and only reuses pages when reference counts prove the stack no longer owns them.

## Dependencies and Integration Points
Depends on DMA mapping APIs, XDP, BPF, NAPI/GRO, hardware CQ/RQ structures, and queue creation helpers from `fun_queue`. It integrates with `funeth_main.c` for queue publication, IRQ/NAPI ownership, XDP program installation, and hardware timestamp configuration.

## Risks and Test Signals
Risks include page reference accounting errors, DMA sync direction mistakes, packet split/gather boundary bugs, PF_MEMALLOC handling, CQ phase races, XDP action fallback when page refs are not safe, and RQ doorbell starvation. Test with multi-fragment jumbo packets, GRO and checksum/hash metadata validation, XDP_PASS/DROP/TX/REDIRECT, low-memory allocation failures, timestamp-enabled receive, NAPI budget exhaustion, and queue teardown under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_trace.h

## Purpose
Defines tracepoints for funeth Tx enqueue, Tx reclaim, and Rx completion handling. These are low-overhead observability hooks for driver data-path debugging.

## APIs and Types
Declares `TRACE_SYSTEM funeth` and three `TRACE_EVENT`s: `funeth_tx`, `funeth_tx_free`, and `funeth_rx`. Events record netdev name, queue index, descriptor index/head, packet length, gather/list counts, hash, and classification vector. It includes `funeth_txrx.h` for queue structures and ends with `<trace/define_trace.h>`.

## Control Flow and Integration
`funeth_tx.c` emits `trace_funeth_tx()` after descriptor construction and `trace_funeth_tx_free()` during reclaim. `funeth_rx.c` defines `CREATE_TRACE_POINTS` before including this header and emits `trace_funeth_rx()` before GRO handoff.

## State and Persistence
Tracepoints do not persist state in the driver. They expose snapshots of queue state and descriptor metadata to ftrace/perf/BPF consumers.

## Dependencies and Risks
Depends on Linux tracepoint infrastructure and correct `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` values for generated trace headers. Risks are mostly build-time include path issues and trace fields reading invalid queue pointers after teardown; current usage is within active datapath code. Test signals include building with tracing enabled and capturing events under Tx/Rx traffic to verify queue names and descriptor indices progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_tx.c

## Purpose
Implements the funeth transmit path for skbs and XDP frames, including DMA mapping, hardware descriptor construction, checksum/TSO/USO/encapsulation offload metadata, kTLS descriptor extension, Tx completion reclaim, queue stop/wake flow control, and Tx queue resource lifecycle.

## Important APIs and Functions
Exported to the rest of funeth are `fun_start_xmit()`, `fun_txq_napi_poll()`, `fun_xdp_tx()`, `fun_xdp_xmit_frames()`, `funeth_txq_create()`, `fun_txq_create_dev()`, and `funeth_txq_free()`. Core helpers include `fun_map_pkt()`, `fun_write_gl()`, `write_pkt_desc()`, `fun_tls_tx()`, `fun_unmap_pkt()`, `fun_txq_reclaim()`, and purge/create/free helpers.

## Control Flow
`fun_start_xmit()` selects the queue from skb mapping, optionally checks kTLS sequence state, writes descriptors, advances `prod_cnt`, stops the netdev queue if space falls below worst-case, timestamps, and rings the SQ doorbell unless `xmit_more` defers it. Descriptor construction maps the linear area and frags, fills offload metadata for encapsulated TSO, TCP TSO, UDP LSO, or checksum partial, writes gather entries across ring wrap, and records the skb in per-descriptor state. NAPI reclaim reads hardware head writeback with barriers, unmaps packet segments, frees skbs, updates completed queue accounting, and wakes stopped queues when at least one quarter empty.

## State and Persistence
`struct funeth_txq` holds descriptor ring, info array, DMA address, hardware writeback pointer, doorbell, producer/consumer counters, queue stats, netdev queue, hardware SQ id, ETH id, IRQ pointer, and init state. XDP queues reuse the Tx queue structure but store `xdp_frame` pointers and may not have an IRQ-backed netdev queue.

## Dependencies and Integration Points
Depends on DMA mapping, skb and XDP APIs, TCP/IP header helpers, TLS device helpers, hardware Tx request structures, and SQ creation/binding from `fun_queue`/`funeth_main.c`. Integrates with ethtool stats through `funeth_txq_stats` and with Rx XDP_TX via `fun_xdp_tx()`.

## Risks and Test Signals
Risks include DMA unwind mistakes, descriptor ring wrap bugs, missing barriers around hardware head/writeback, offload metadata errors for encapsulated packets, TLS `next_seq` drift, XDP queue full handling, and purge after hardware queue destruction. Test with TSO/USO/checksum offload, tunneled GSO, fragmented skbs, kTLS fallback/resync, netdev queue stop/wake under saturation, XDP_TX/XDP_REDIRECT, and teardown while descriptors are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_txrx.h

## Purpose
Defines shared funeth Tx/Rx queue constants, state enums, queue statistics, queue data structures, IRQ wrapper, inline descriptor/doorbell helpers, and function prototypes used across `funeth_main.c`, `funeth_tx.c`, `funeth_rx.c`, `funeth_ethtool.c`, and tracepoints.

## APIs and Types
Important constants include descriptor sizes, max gather-list descriptors, CQE info offset, interrupt doorbell encodings, Rx tailroom, and XDP headroom. Enums describe queue init states (`DESTROYED`, `INIT_SW`, `INIT_FULL`) and IRQ states. Types include `funeth_txq_stats`, `funeth_rxq_stats`, `funeth_tx_info`, `funeth_txq`, `funeth_rxbuf`, `funeth_rx_cache`, `funeth_rxq`, and `fun_irq`. Macros `FUN_QSTAT_INC` and `FUN_QSTAT_READ` wrap synchronized 64-bit stats. Inline helpers locate Tx descriptors, ring SQ doorbells, and derive NUMA node from IRQ affinity.

## Control Flow and Integration
The state model lets main code allocate queues in software first, advance them to hardware resources, and later free down to a requested state. Tx and Rx datapaths use the stats and queue fields directly; ethtool relies on the same stat layouts for string/count ordering. IRQ structs bind NAPI to either Tx or Rx queues and hold MSI-X affinity state.

## State and Persistence
This header defines the in-memory persistent state of active queues. Counters are free-running until queues are freed, then selected totals are folded into `funeth_priv`. Ring producer/consumer counters and CQ phase/head fields are central to hardware synchronization.

## Dependencies and Risks
Depends on netdevice, XDP, and `u64_stats_sync`. Because this header fixes structure layout shared by many files, changes risk breaking stats ordering, cacheline assumptions, queue teardown, and tracepoint compilation. Test signals include 32-bit stat consistency, ethtool stat count/name matching, queue creation/free across all init states, XDP-enabled builds, and high-rate traffic to exercise doorbell and producer/consumer wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Kconfig

## Purpose
Adds the Google Ethernet vendor menu and the `GVE` driver configuration option for Google Virtual NIC support.

## APIs and Build Semantics
`NET_VENDOR_GOOGLE` is a boolean vendor gate defaulting to `y`. Under that gate, `GVE` is a tristate option labelled "Google Virtual NIC (gVNIC) support". It depends on MSI-X-capable PCI and either x86 or little-endian CPU support, plus optional PTP clock support via `PTP_1588_CLOCK_OPTIONAL`, and selects `PAGE_POOL`.

## Control Flow and Integration
Kconfig controls whether the `google/Makefile` descends into the `gve/` directory and whether the gve object is built-in or a module. The help text states the module name is `gve`.

## State and Persistence
No runtime state is stored here. It persists build-time feature selection and dependency constraints.

## Dependencies and Risks
The dependency on `PCI_MSI` is required by the driver's MSI-X model; `PAGE_POOL` is required by receive buffer management; PTP optional support aligns with conditional `gve_ptp.o`. Risks are misconfigured builds on unsupported endian/architecture targets or accidentally hiding the driver when `NET_VENDOR_GOOGLE=n`. Test signals include `allyesconfig`, `allmodconfig`, `GVE=m`, `GVE=y`, and builds with and without `CONFIG_PTP_1588_CLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Makefile

## Purpose
Connects the Google Ethernet vendor directory to the gVNIC driver subdirectory.

## APIs and Build Semantics
The only build rule is `obj-$(CONFIG_GVE) += gve/`, so the subdirectory is compiled when `CONFIG_GVE` is built-in or modular.

## Control Flow and Integration
This file is reached from the parent Ethernet driver Makefile. It delegates all object composition to `google/gve/Makefile`.

## State and Persistence
No runtime state. It persists the build graph edge from `CONFIG_GVE` to the gve driver directory.

## Dependencies, Risks, and Tests
Depends on Kbuild's directory recursion semantics. The main risk is omission from the build when Kconfig is enabled. Test with `make M=drivers/net/ethernet/google/gve` in a kernel tree or full kernel builds with `CONFIG_GVE=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/Makefile

## Purpose
Defines the object composition of the Google Virtual Ethernet driver module/built-in object.

## APIs and Build Semantics
`obj-$(CONFIG_GVE) += gve.o` creates the final driver object. `gve-y` includes core, GQI and DQO Tx/Rx paths, ethtool, admin queue, utilities, flow rules, and DQO buffer management. `gve-$(CONFIG_PTP_1588_CLOCK) += gve_ptp.o` conditionally adds PTP support.

## Control Flow and Integration
The Kbuild object list aligns with declarations in `gve.h`: adminq, ethtool, flow rule, buffer management, PTP, and both queue formats are compiled together into one driver.

## State and Persistence
No runtime state. Build-time state determines whether timestamp/clock code is linked.

## Dependencies, Risks, and Tests
Risks include missing object files for prototypes declared in `gve.h`, or building PTP references without `gve_ptp.o`. Test signals include modular and built-in builds, `CONFIG_PTP_1588_CLOCK=y/m/n`, and link checks for all exported symbols declared in `gve.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve.h

## Purpose
Central shared header for the Google gVNIC driver. It defines constants, queue formats, Tx/Rx ring state for GQI and DQO, QPL/page/buffer abstractions, notify blocks, RSS and flow-rule caches, PTP/timestamp state, service/reset flags, helper accessors, and cross-file prototypes.

## Important APIs and Types
Key types include `gve_priv`, `gve_tx_ring`, `gve_rx_ring`, `gve_notify_block`, `gve_queue_page_list`, queue config structs, QPL config, DQO pending packet/buffer states, RSS config, flow rule/cache structs, and `gve_ptp`. Inline helpers expose reset/admin/resource/NAPI state flags, queue format checks (`gve_is_gqi()`, `gve_is_dqo()`, `gve_is_qpl()`), queue/QPL id mapping, notify block mapping, XDP queue ids, and PTP availability. Prototypes cover admin queue users, Tx/Rx allocation and polling, XDP, reset/config adjustment, flow rules, RSS, PTP, and stats reporting.

## Control Flow and Integration
This header is the contract tying together `gve_main`, `gve_adminq`, Tx/Rx implementations, ethtool, flow steering, buffer management, and PTP. Queue format determines which union members in ring structs are active: GQI uses descriptor/data rings and QPL/raw addressing, while DQO uses completion/buffer queues, pending packet lists, page pools, header buffers, and miss/reinjection completion tracking.

## State and Persistence
`gve_priv` is the persistent per-device state. It stores PCI BAR mappings, MSI-X vectors, admin queue ring and counters, event counters, queue arrays/configs, QPL accounting, feature limits, stats report DMA, workqueue/timers/service flags, link speed, flow rules, RSS cache, NIC timestamp DMA, and PTP clock handles. Queue structs maintain free-running counters and synchronized stats for 32-bit architectures.

## Dependencies and Integration Points
Depends on Linux DMA, PCI, netdevice, ethtool netlink, PTP, page pool, XDP, and descriptor headers `gve_desc.h`/`gve_desc_dqo.h`. `gve_adminq.c` populates much of this state from device descriptors and options.

## Risks and Test Signals
Risks include using the wrong union member for a queue format, stale state flags after reset, QPL id collisions, mismatch between adminq feature negotiation and ring allocation, PTP stubs with optional builds, and stats races. Test with all queue formats supported by the device, XDP/XSK paths, reset during traffic, flow rule and RSS ethtool operations, PTP-enabled and disabled builds, and 32-bit stat-read validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.c

## Purpose
Implements the gVNIC admin queue control plane: admin queue allocation/release, command submission and completion polling, device descriptor and option parsing, queue/resource creation and destruction commands, QPL registration, stats/link/timestamp reports, PTYPE map retrieval, flow-rule configuration/query, and RSS configuration/query.

## Important APIs and Functions
Public functions include `gve_adminq_alloc/free/release()`, `gve_adminq_describe_device()`, resource configure/deconfigure, create/destroy Tx/Rx queues, register/unregister page lists, report stats/link/NIC timestamp, verify driver compatibility, get DQO ptype map, configure/query flow rules, and configure/query RSS. Internal command machinery includes `gve_adminq_issue_cmd()`, `gve_adminq_kick_and_wait()`, `gve_adminq_execute_cmd()`, `gve_adminq_execute_extended_cmd()`, and status mapping in `gve_adminq_parse_err()`.

## Control Flow
Allocation creates a DMA pool and one 4 KiB admin queue ring, programs revision-dependent BAR registers, initializes counters and lock, and marks admin queue OK. Synchronous command execution requires the queue to be empty, writes one command, rings the doorbell, waits for event counter advancement, then maps device statuses to errno. Batched queue create/destroy commands issue multiple entries under `adminq_lock` before one kick. Extended commands allocate coherent memory for payloads larger than the 56-byte inline command area.

## State and Persistence
Admin state is held in `gve_priv`: admin queue DMA memory, producer count/mask, per-op counters, fail/timeout counters, state flags, queue format, descriptor limits, feature limits, RSS sizes/cache mode, flow cache sync state, link speed, max pages, event counters, and timestamp support. Device descriptor parsing persists negotiated queue format and optional features into `gve_priv` and `net_device` feature flags.

## Dependencies and Integration Points
Depends on `gve_register.h` BAR register layout, `gve_adminq.h` command ABI, `gve.h` queue state, DMA coherent allocation, mutex locking, PCI device revision, and ethtool RSS structures. It is called by probe/configuration, queue setup/teardown, ethtool RSS/flow steering, stats reporting, reset paths, and PTP timestamp setup.

## Risks and Test Signals
Risks include admin queue timeout requiring reset, command ring overflow logic, endian conversion mistakes, descriptor option bounds, feature negotiation priority, coherent buffer lifetime around device DMA writes, extended command cleanup, flow/RSS descriptor length validation, and cache invalidation after flow changes. Test with descriptor options for GQI/DQO/RDA/QPL, queue create/destroy batches, QPL registration limits, admin status error injection, RSS set/query, flow rule add/delete/reset/query, link speed report, NIC timestamp report, and device reset/release handshakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.h

## Purpose
Defines the gVNIC admin queue ABI shared between the driver and device firmware. It enumerates opcodes/status codes, device descriptor/options, driver capability bits, command payload structures, flow/RSS/PTYPE/stat/timestamp formats, the 64-byte admin command union, and adminq function prototypes.

## Important APIs and Types
Important enums include admin opcodes, extended opcodes, status codes, device option ids, supported feature masks, driver capabilities, set-driver-parameter types, stat names, L3/L4 PTYPE values, flow config/query opcodes, flow types, and RSS hash types. Structures are guarded by `static_assert()` size checks to preserve ABI layout. The union `gve_adminq_command` is exactly 64 bytes and embeds all inline command payloads plus the extended command wrapper.

## Control Flow and Integration
`gve_adminq.c` fills these structures, converts fields to big endian, and submits them through the admin queue. Device descriptor and option structures drive probe-time feature negotiation; create/destroy queue commands bind driver-allocated rings and queue resources to device queues; report/query commands hand coherent DMA buffers to the device for output.

## State and Persistence
This header defines wire-format state, not runtime storage. Persistent driver state derived from it is stored in `gve_priv`: queue format, descriptor counts, max pages, RSS sizes, feature flags, flow limits, link speed, timestamp support, and admin counters.

## Dependencies and Risks
Depends on Linux fixed-width big-endian types, Ethernet address definitions, and `struct gve_flow_spec` from `gve.h` for flow-rule payloads. Risks are ABI drift, size/alignment changes, missing endian conversions, unsupported option-length compatibility, and command union overflow. Test signals include compile-time static asserts, admin command traces/status injection, probe against devices with old/new option lengths, and exercising every public adminq command path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.h -->
