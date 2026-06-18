<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl.c -->
# sources/distributed-fs/ceph-client/net/core/netdev-genl.c

## Purpose
Generic-netlink control plane for the netdev family. It exposes device capabilities, NAPI configuration, queue topology, queue statistics, dmabuf-backed netmem bindings, and dynamic RX queue leasing/creation to user space, and emits multicast notifications for netdev add/delete/change events.

## APIs, Types, and Functions
The dump cursor is `struct netdev_nl_dump_ctx`. Main command handlers include `netdev_nl_dev_get_doit/dumpit()`, `netdev_nl_napi_get_doit/dumpit()`, `netdev_nl_napi_set_doit()`, `netdev_nl_queue_get_doit/dumpit()`, `netdev_nl_qstats_get_dumpit()`, `netdev_nl_bind_rx_doit()`, `netdev_nl_bind_tx_doit()`, and `netdev_nl_queue_create_doit()`. Helpers fill nested netlink attributes for device XDP/XSK features, NAPI IRQ/threading/defer timers, RX/TX queue NAPI IDs, queue leases, memory providers, AF_XDP pools, and queue stats. `netdev_stat_queue_sum()` is exported for drivers to combine disabled queue counters into base stats.

## Control Flow, State, and Persistence
GET commands allocate a reply skb, lock the addressed netdev or NAPI object, serialize attributes, unlock, then reply. Dumps persist ifindex and queue/NAPI indexes in callback context. NAPI SET mutates threaded mode and defer/timeout knobs under the netdev lock. RX dmabuf bind parses a nested queue bitmap, verifies all selected queues share one DMA device, creates a `net_devmem_dmabuf_binding`, binds each queue, and stores socket-owned bindings in `struct netdev_nl_sock`. Queue creation validates a virtual destination device, resolves a physical lease device possibly in a peer netns, locks virtual then physical devices, creates an RX queue through driver `queue_mgmt_ops`, and links the virtual/physical RX queues. Socket-private destroy walks bindings and unbinds them with device locking.

## Dependencies and Integration
Depends on generated `netdev-genl-gen.h`, generic netlink, rtnetlink/netdev locks, `netdev_queue_mgmt_ops`, queue-stat ops, AF_XDP pool state, XDP metadata ops, dmabuf devmem support, page-pool memory-provider callbacks, network namespace peer IDs, and the netdevice notifier chain. `subsys_initcall()` registers both notifier and netlink family.

## Risks and Test Signals
High-risk areas are lock ordering across virtual and physical devices, rollback after partial dmabuf queue binding, dump cursor correctness, stats omission via all-`0xff` sentinel structs, namespace ID allocation in lease reporting, and driver callback failures during queue creation. Useful test signals include genetlink GET/DUMP coverage with small skb buffers, NAPI set/get round trips, queue lease across netns, dmabuf bind/unbind on socket close, `-EOPNOTSUPP` paths for devices without ops locks or netmem TX, and notifier delivery for register/unregister/XDP feature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_config.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_config.c

## Purpose
Queue-configuration renderer and validator for drivers using the netdev queue management API. It merges driver defaults with per-RX-queue memory-provider overrides and optionally asks the driver to validate the effective configuration.

## APIs, Types, and Functions
`netdev_queue_config()` is the exported read-side helper for drivers. `netdev_queue_config_validate()` is the validating variant used by queue reconfiguration paths. Internal `__netdev_queue_config()` selects either `ndo_validate_qcfg` or a no-op validator, zeroes `struct netdev_queue_config`, calls `ndo_default_qcfg`, overlays `rx_page_size` from `rxq->mp_params`, and validates after defaults and again after overrides.

## Control Flow, State, and Persistence
The function does not persist state itself; it derives an output config from `dev->queue_mgmt_ops` and the addressed RX queue each time. Validation is two-phase so invalid driver defaults and invalid memory-provider overrides are both caught with the same driver callback.

## Dependencies and Integration
Depends on `netdev_queue_mgmt_ops`, `struct netdev_rx_queue`, memory-provider params, and netlink extack for human-readable validation failures. It is used by RX queue restart/reconfiguration and memory-provider open/close logic.

## Risks and Test Signals
Risks are sparse: missing `queue_mgmt_ops` assumptions in callers, driver validators that are not idempotent, and overrides that only set `rx_page_size` while future config fields may need similar treatment. Test signals are driver default propagation, invalid default rejection, invalid memory-provider page-size rejection, and `netdev_queue_config()` fully zero-initializing unset fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_queues.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_queues.c

## Purpose
Shared queue utility code for DMA-device selection, queue-creation eligibility, queue-lease eligibility, and queue-busy checks used by the netdev generic-netlink queue control plane and memory-provider setup.

## APIs, Types, and Functions
`netdev_queue_get_dma_dev()` returns the DMA device for an RX or TX queue, following RX queue leases from virtual to physical devices when needed. `netdev_can_create_queue()` validates that a device is virtual and implements `ndo_queue_create`. `netdev_can_lease_queue()` validates that a lease source is a present physical device with queue management ops. `netdev_queue_busy()` rejects queues already used by AF_XDP, RX queue leasing, or a memory provider.

## Control Flow, State, and Persistence
The helpers are read-only except for extack messages. DMA-device lookup requires the caller to hold the netdev ops lock, handles leased RX queues by locking the physical device, and falls back to `dev->dev.parent` when the driver lacks `ndo_queue_get_dma_dev`.

## Dependencies and Integration
Depends on `netdev_queue_mgmt_ops`, RX queue lease helpers from `netdev_rx_queue.c`, AF_XDP `xsk_get_pool_from_qid()`, and device DMA mask validation. It feeds dmabuf binding, queue creation, and zero-copy memory-provider paths.

## Risks and Test Signals
Risks include returning NULL for devices with missing DMA masks, incorrect virtual/physical classification through `dev.parent`, and stale busy checks if future users can attach to TX queues. Test signals are AF_XDP rejection, leased RX queue rejection, memory-provider rejection, virtual-device queue creation acceptance, and leased RX DMA lookup returning the physical queue DMA device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_queues.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c

## Purpose
RX queue lease and memory-provider lifecycle support. It links virtual RX queues to physical RX queues, redirects memory-provider operations through leases, and restarts/reconfigures RX queues when provider settings change.

## APIs, Types, and Functions
Queue lease APIs are `netdev_rx_queue_lease()`, `netdev_rx_queue_unlease()`, `netif_rxq_is_leased()`, `netif_is_queue_leasee()`, and `__netif_get_rx_queue_lease()`. Memory-provider APIs are `netif_rxq_has_unreadable_mp()`, `netif_rxq_has_mp()`, `netif_mp_open_rxq()`, `netif_mp_close_rxq()`, `__netif_mp_uninstall_rxq()`, and `netif_rxq_cleanup_unlease()`. `netdev_rx_queue_restart()` is exported in the `NETDEV_INTERNAL` namespace.

## Control Flow, State, and Persistence
Leasing stores reciprocal `rxq->lease` pointers and holds the physical device with a tracker; unlease clears both sides and drops the hold after memory-provider cleanup. RX queue reconfig allocates new and old driver memory blobs, calls driver allocate/stop/start/free callbacks, and attempts to restore old state if starting the new queue fails. Memory-provider open validates HDS/TCP data split state, absence of XDP programs and AF_XDP pools, queue support for `rx_page_size`, then stores `rxq->mp_params`, validates effective queue config, and reconfigures the queue. Close verifies the old provider identity, clears params, and reconfigures back.

## Dependencies and Integration
Depends on netdev locks, `queue_mgmt_ops`, ethtool HDS config, XDP program counts, page-pool memory-provider validation, AF_XDP pool state, and page-pool private helpers. Lease cleanup integrates with queue unlease so a provider installed through a virtual queue is removed from the physical queue.

## Risks and Test Signals
Risks include failure recovery if `ndo_queue_start()` cannot restore old memory, WARN-only handling for provider identity mismatches, lease direction mistakes, races with device unregister, and policy coupling to TCP data split. Test signals are successful reconfiguration on running and down devices, injected callback failures with old queue restoration, provider open/close through leased queues, unlease cleanup of physical provider state, AF_XDP/XDP/HDS rejection paths, and restart behavior returning `-ENETDOWN` only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netevent.c -->
# sources/distributed-fs/ceph-client/net/core/netevent.c

## Purpose
Small exported notifier-chain wrapper for network events, historically used by neighbor and related networking subsystems to publish asynchronous events to registered listeners.

## APIs, Types, and Functions
The file owns `ATOMIC_NOTIFIER_HEAD(netevent_notif_chain)` and exports `register_netevent_notifier()`, `unregister_netevent_notifier()`, and `call_netevent_notifiers()`.

## Control Flow, State, and Persistence
Registered `notifier_block` instances persist in the atomic notifier chain until unregistered. `call_netevent_notifiers()` forwards the event value and opaque pointer through `atomic_notifier_call_chain()` without interpreting them.

## Dependencies and Integration
Depends on Linux notifier infrastructure and is included through `net/netevent.h`. It is suitable for contexts that require atomic notifier semantics rather than blocking notifier semantics.

## Risks and Test Signals
Risks are mostly consumer-side: notifier blocks must not be reused while registered, callbacks must tolerate atomic context, and event payload typing is implicit. Test signals are registration/unregistration return codes, callback ordering/counts, and safe behavior when no listeners exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netmem_priv.h -->
# sources/distributed-fs/ceph-client/net/core/netmem_priv.h

## Purpose
Private inline helpers for manipulating page-pool metadata stored in `netmem_ref` backing descriptors, including page-pool identity, DMA address fields, and compressed DMA index bits.

## APIs, Types, and Functions
Helpers include `netmem_get_pp_magic()`, `netmem_is_pp()`, `netmem_set_pp()`, `netmem_set_dma_addr()`, `netmem_get_dma_index()`, and `netmem_set_dma_index()`. They operate through `netmem_to_nmdesc()` and account for `NET_IOV` encoded references.

## Control Flow, State, and Persistence
State is stored directly in the netmem/page descriptor fields `pp`, `pp_magic`, and `dma_addr`. `netmem_is_pp()` clears the `NET_IOV` tag and casts to `struct page` because current `page_type` layout is shared between `struct page` and `struct net_iov`. DMA index helpers warn and no-op for net_iov references because the index side table is page-based.

## Dependencies and Integration
Depends on page-pool bit definitions such as `PP_DMA_INDEX_MASK` and `PP_DMA_INDEX_SHIFT`, PageNetpp flags, netmem conversion helpers, and the page-pool DMA mapping xarray in `page_pool.c`.

## Risks and Test Signals
Risks are layout-sensitive: comments explicitly note the cast relies on shared offsets between page and net_iov. DMA index overflow or misuse on net_iov should trigger WARNs. Test signals include PageNetpp set/clear on page-backed netmem, DMA index round trips preserving non-index magic bits, and no corruption when net_iov references pass through unsupported index helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netmem_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netpoll.c -->
# sources/distributed-fs/ceph-client/net/core/netpoll.c

## Purpose
Low-level UDP packet output and polling framework used by netconsole, crash/debug paths, and other code that must transmit while normal networking progress may be impaired. It maintains emergency skb pools, polls NAPI/driver controller hooks, and constructs Ethernet/IP/UDP packets directly.

## APIs, Types, and Functions
Exported APIs include `netpoll_poll_dev()`, `netpoll_poll_disable()`, `netpoll_poll_enable()`, `netpoll_send_skb()`, `netpoll_send_udp()`, `__netpoll_setup()`, `netpoll_setup()`, `__netpoll_free()`, `do_netpoll_cleanup()`, and `netpoll_cleanup()`. Helpers include `queue_process()`, `poll_one_napi()`, `find_skb()`, `__netpoll_send_skb()`, `push_ipv4()`, `push_ipv6()`, `push_udp()`, and `push_eth()`.

## Control Flow, State, and Persistence
Setup resolves the egress device by name or MAC under RTNL, rejects slave devices and devices with `IFF_DISABLE_NETPOLL`, opens the device if needed, auto-fills local IPv4/IPv6 when unset, initializes a per-netpoll skb pool, and attaches/refcounts a per-netdevice `netpoll_info`. Sending first tries immediate hard-start xmit with IRQs disabled and no local NAPI recursion; on congestion it queues to `npinfo->txq` and schedules delayed work. Polling uses `npinfo->dev_lock`, optional driver `ndo_poll_controller`, budget-zero NAPI polling, and completion-queue cleanup. Cleanup decrements the shared `npinfo` refcount, clears `dev->npinfo` under RCU, cancels work, purges queues, flushes the local skb pool, and releases the held netdev.

## Dependencies and Integration
Depends on netdevice TX locks, NAPI state, softnet completion queues, IPv4/IPv6 address configuration, UDP checksums, VLAN handling, workqueues, RTNL/RCU synchronization, and optional driver netpoll setup/cleanup/poll hooks. The `carrier_timeout` module parameter controls wait time after opening an interface.

## Risks and Test Signals
Risks include IRQ-state assumptions, driver poll/xmit lock recursion, stale queue mappings after queue-count changes, RCU lifetime of `npinfo`, IPv6 local address auto-detection, and correct fallback during OOM. Test signals are UDP packet construction for IPv4 and IPv6, send under stopped TX queue with later workqueue drain, setup/cleanup refcounting for multiple netpoll users, `netpoll_poll_disable()` blocking polling during device state changes, and no local IP overwrite when caller supplied an IPv6 address whose first four bytes are zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c -->
# sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c

## Purpose
Legacy cgroup subsystem that assigns per-cgroup, per-netdevice packet priority indexes and propagates a task's cgroup priority index into already-open sockets on attach.

## APIs, Types, and Functions
The subsystem object is `net_prio_cgrp_subsys`. Core helpers are `extend_netdev_table()`, `netprio_prio()`, `netprio_set_prio()`, cgroup callbacks `cgrp_css_alloc()`, `cgrp_css_online()`, `cgrp_css_free()`, `net_prio_attach()`, cftype handlers `read_prioidx()`, `read_priomap()`, `write_priomap()`, and device notifier `netprio_device_event()`.

## Control Flow, State, and Persistence
Each netdev may own an RCU-replaced `struct netprio_map` indexed by cgroup CSS ID. Online child cgroups inherit parent priorities for all init-net devices under RTNL. Writes to `ifpriomap` parse `ifname priority`, grow the device table only for nonzero writes or existing entries, and store the priority. Attach iterates each task's open files under task lock and updates socket cgroup priority metadata. Netdev unregister clears and RCU-frees the priomap.

## Dependencies and Integration
Depends on the legacy cgroup API, init network namespace devices, RTNL, RCU, socket cgroup data, fdtable iteration, and netdevice notifier registration at `subsys_initcall()`.

## Risks and Test Signals
Risks include init-net-only behavior, large CSS ID table growth up to `USHRT_MAX`, attach-time races with file table changes, and legacy interface semantics. Test signals are inherited parent priority on child online, zero writes avoiding allocation, readback via `prioidx` and `ifpriomap`, socket priority update after cgroup attach, and priomap cleanup on device unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/of_net.c -->
# sources/distributed-fs/ceph-client/net/core/of_net.c

## Purpose
Open Firmware/device-tree helpers for network drivers to parse PHY interface mode and MAC address data, including fallback to NVMEM cells.

## APIs, Types, and Functions
Exports `of_get_phy_mode()`, `of_get_mac_address_nvmem()`, `of_get_mac_address()`, and `of_get_ethdev_address()`. Private `of_get_mac_addr()` validates a named property as exactly `ETH_ALEN` bytes and a valid nonzero Ethernet address.

## Control Flow, State, and Persistence
`of_get_phy_mode()` reads `phy-mode` or `phy-connection-type`, compares case-insensitively against `phy_modes()`, and returns `PHY_INTERFACE_MODE_NA` plus an errno on failure. MAC lookup tries `mac-address`, then `local-mac-address`, then legacy `address`, then NVMEM. NVMEM lookup first uses a platform device associated with the node, then falls back to an OF NVMEM cell named `mac-address`, validates length/address, copies it, and frees the cell buffer. `of_get_ethdev_address()` writes the discovered address into `dev->dev_addr`.

## Dependencies and Integration
Depends on OF property APIs, platform-device lookup, NVMEM consumer APIs, Ethernet address validation, PHY mode tables, and netdevice address helpers. It is used by DT-aware Ethernet drivers during probe.

## Risks and Test Signals
Risks include accepting obsolete `address` when a board uses it for another meaning, NVMEM provider deferral/error propagation, and invalid zero MACs from boot firmware. Test signals are property precedence, invalid/all-zero MAC rejection, NVMEM fallback with correct buffer free, `-ENODEV` for unknown PHY strings, and successful `eth_hw_addr_set()` through `of_get_ethdev_address()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/of_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool.c -->
# sources/distributed-fs/ceph-client/net/core/page_pool.c

## Purpose
Core page-pool allocator/recycler for high-speed RX and XDP paths. It provides per-pool allocation caches, DMA mapping lifetime management, recycling rings, fragment allocation, memory-provider integration, delayed destruction, and optional statistics.

## APIs, Types, and Functions
Creation APIs are `page_pool_create_percpu()` and `page_pool_create()`. Allocation APIs are `page_pool_alloc_netmems()`, `page_pool_alloc_pages()`, `page_pool_alloc_frag_netmem()`, and `page_pool_alloc_frag()`. Return APIs are `page_pool_put_unrefed_netmem()`, `page_pool_put_unrefed_page()`, and `page_pool_put_netmem_bulk()`. Lifecycle and metadata APIs include `page_pool_destroy()`, `page_pool_update_nid()`, `page_pool_enable_direct_recycling()`, `page_pool_disable_direct_recycling()`, `page_pool_use_xdp_mem()`, `page_pool_set_pp_info()`, `page_pool_clear_pp_info()`, and netmem provider helpers for `net_iov`. Stats helpers are exported when `CONFIG_PAGE_POOL_STATS` is enabled.

## Control Flow, State, and Persistence
Initialization validates flags, DMA direction/sync requirements, ring size, high-order limits, memory-provider callbacks, stats allocation, and xarray setup for DMA mapping indexes. Allocation first uses the lockless alloc cache, refills from the ptr_ring with NUMA checks, and falls back to bulk page allocation or provider allocation. New pages are optionally DMA-mapped, tagged with PageNetpp/page-pool metadata, optionally initialized by callback, and counted in `pages_state_hold_cnt`. Return checks refcounts and pfmemalloc status, syncs for device if needed, recycles directly to the NAPI-local cache when safe, otherwise produces to the ptr_ring, and finally releases DMA/provider state and puts pages if recycling is impossible. Destruction disables direct recycling, drains fragment state, scrubs alloc cache/ring/DMA xarray, checks inflight count against release count, and retries with delayed work until outstanding pages return.

## Dependencies and Integration
Depends on DMA mapping APIs, `ptr_ring`, xarray, page flags, NAPI ownership, XDP memory IDs, netmem/net_iov abstractions, page-pool memory providers, netdev locks for provider-backed pools, tracepoints, and page-pool user listing from `page_pool_user.c`.

## Risks and Test Signals
Risks include refcount/inflight mismatches causing delayed destroy stalls, races between DMA sync and scrub, direct recycling under PREEMPT_RT or wrong NAPI context, compressed DMA address/index overflow, provider ops outside rodata, high-order allocation limitations, and fragment bias accounting errors. Test signals are fast/slow allocation stats, DMA map/unmap count balance, bulk return with mixed pools, fragment drain at page boundaries, NUMA update flushing alloc cache, destruction retry warnings for leaked pages, provider alloc/release paths, and error injection on `page_pool_alloc_netmems()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_priv.h -->
# sources/distributed-fs/ceph-client/net/core/page_pool_priv.h

## Purpose
Private declarations and inlines shared between page-pool core, page-pool netlink user exposure, and netdev RX queue memory-provider code.

## APIs, Types, and Functions
Declares `page_pools_lock`, `page_pool_inflight()`, `page_pool_list()`, `page_pool_detached()`, `page_pool_unlist()`, `page_pool_set_pp_info()`, `page_pool_clear_pp_info()`, and `page_pool_check_memory_provider()`. Provides `page_pool_set_dma_addr_netmem()` and `page_pool_set_dma_addr()` for DMA address storage, including 32-bit architecture compression for 64-bit DMA addresses.

## Control Flow, State, and Persistence
The DMA helper stores either the full address or a page-shifted compressed address in netmem descriptor state and returns true when compression cannot round-trip exactly. `CONFIG_PAGE_POOL` stubs make metadata and provider checks no-ops when the feature is unavailable.

## Dependencies and Integration
Depends on page-pool helper types, `netmem_priv.h`, DMA address width macros, and netdev/RX queue declarations. It is the private contract connecting `page_pool.c`, `page_pool_user.c`, and `netdev_rx_queue.c`.

## Risks and Test Signals
Risks are mostly ABI/layout and architecture related: incorrect compressed DMA storage on 32-bit systems with 64-bit DMA would corrupt mappings. Test signals include round-trip tests for page-aligned DMA addresses, failure on unrepresentable DMA addresses, build coverage with and without `CONFIG_PAGE_POOL`, and memory-provider validation calls from queue reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_user.c -->
# sources/distributed-fs/ceph-client/net/core/page_pool_user.c

## Purpose
User-visible registry and generic-netlink reporting for page pools. It assigns stable IDs, links pools to netdevices, reports inflight and stats data, sends page-pool multicast notifications, and preserves user visibility when devices unregister.

## APIs, Types, and Functions
Externally used functions are `page_pool_list()`, `page_pool_detached()`, `page_pool_unlist()`, and `page_pool_check_memory_provider()`. Netlink handlers include `netdev_nl_page_pool_get_doit/dumpit()` and `netdev_nl_page_pool_stats_get_doit/dumpit()`. Fill helpers are `page_pool_nl_fill()` and `page_pool_nl_stats_fill()`.

## Control Flow, State, and Persistence
Global `page_pools` xarray maps IDs to pools and `page_pools_lock` protects the xarray, per-device `page_pools` hlists, pool user fields, NAPI pointer visibility, and `slow.netdev`. Listing allocates a cyclic 32-bit ID, initializes the hlist node, links to the creating netdev when present, and sends add notifications. GET validates namespace and visibility before serializing ID, ifindex, NAPI ID, inflight page/memory counts, detach time, and provider-specific attributes. Dumps walk netdevs and their pool hlists under RTNL plus `page_pools_lock`. On netdev unregister, pools move to loopback as orphaned visible pools; loopback unregister wipes them invisible with poisoned netdev pointers.

## Dependencies and Integration
Depends on page-pool core stats/inflight APIs, generated netdev generic-netlink attributes, network namespaces, RTNL, netdevice notifier chain, memory-provider `nl_fill()`, and loopback device lifetime.

## Risks and Test Signals
Risks include lock ordering with RTNL, userspace-visible orphan semantics, stale provider binding validation in `page_pool_check_memory_provider()`, and stats behavior when `CONFIG_PAGE_POOL_STATS` is off. Test signals are ID allocation/list/unlist, get and dump namespace filtering, add/change/delete notifications, orphan move to loopback on device unregister, wipe on loopback unregister, stats `-EOPNOTSUPP` without stats config, and provider lookup matching queue index plus binding pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/pktgen.c -->
# sources/distributed-fs/ceph-client/net/core/pktgen.c

## Purpose
Kernel packet generator module for traffic generation and packet path testing. It creates per-network-namespace `/proc/net/pktgen` controls, per-online-CPU generator threads, and per-device generator configurations that can emit crafted IPv4/IPv6 UDP packets through hard-start-xmit, qdisc, or receive-path injection.

## APIs, Types, and Functions
Important types are `struct pktgen_net`, `struct pktgen_thread`, `struct pktgen_dev`, `struct flow_state`, `struct imix_pkt`, and on-wire `struct pktgen_hdr`. Control files use `pgctrl_write()`, `pktgen_thread_write()`, and `pktgen_if_write()`. Runtime functions include `pktgen_setup_dev()`, `pktgen_setup_inject()`, `mod_cur_headers()`, `fill_packet_ipv4()`, `fill_packet_ipv6()`, `pktgen_finalize_skb()`, `pktgen_xmit()`, `pktgen_thread_worker()`, `pktgen_add_device()`, `pktgen_remove_device()`, and pernet/module init/exit.

## Control Flow, State, and Persistence
Module init registers pernet state and a netdevice notifier. Each netns creates `/proc/net/pktgen/pgctrl` and one `kpktgend_N` file/thread per online CPU. Users add devices to a thread, then per-device proc writes configure sizes, IMIX weights, delays/rates, counts, flags, IPv4/IPv6 ranges, UDP ports, MAC iteration, MPLS, VLAN/SVLAN, queue mapping, SKB sharing, NUMA node, xmit mode, and optional IPsec. `start` posts `T_RUN`; worker threads initialize current addresses and counters, then repeatedly pick the next due device, build or reuse an skb, optionally wait until `next_tx`, transmit by the selected mode, update counters/sequence numbers, and stop when count is reached. Device unregister marks matching generators for removal; namespace exit stops threads and removes proc entries.

## Dependencies and Integration
Depends on procfs, pernet operations, kthreads, netdevice refs/notifiers, RCU-protected device lists, TX queue locks, skb allocation/frags, IPv4/IPv6/UDP checksum helpers, VLAN/MPLS header construction, random number helpers, high-resolution timers, NUMA allocation, and optional XFRM/IPsec. It directly exercises device start_xmit, `dev_queue_xmit()`, and `netif_receive_skb()`.

## Risks and Test Signals
Risks include a very broad proc parser surface, expected single-controller semantics, lock ordering between global thread lock and per-thread if lock, skb reuse/refcount bugs with `F_SHARED`, burst and clone constraints, generated header correctness for combinations of IPv6/MPLS/VLAN/IPsec/frags, device removal races, and CPU hotplug limitations because threads are created for online CPUs at namespace init. Test signals are proc command parsing and result strings, add/remove under notifier events, finite count completion with pps/bps results, xmit modes, shared/unshared skb behavior, queue mapping bounds correction, IMIX distribution counts, checksum modes, and cleanup on namespace/module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/pktgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ptp_classifier.c -->
# sources/distributed-fs/ceph-client/net/core/ptp_classifier.c

## Purpose
Classic BPF-based classifier and helpers for Precision Time Protocol packets. It identifies PTP event messages across Ethernet L2, UDP/IPv4, UDP/IPv6, and 802.1Q variants and provides helpers to parse headers and detect Sync messages.

## APIs, Types, and Functions
Exports `ptp_classify_raw()`, `ptp_parse_header()`, and `ptp_msg_is_sync()`. `ptp_classifier_init()` builds the static cBPF filter with `bpf_prog_create()` at init. The global `ptp_insns` holds the compiled program.

## Control Flow, State, and Persistence
The filter inspects Ethernet ethertype, IP protocol, IPv4 fragment bits, UDP destination port `PTP_EV_PORT`, VLAN encapsulation, and PTP message type bits, then returns a `PTP_CLASS_*` bitmask or none. `ptp_parse_header()` advances from MAC header through optional VLAN, IPv4/IPv6 plus UDP, or L2 payload, checks the full `struct ptp_header` is within the skb linear data, and returns a pointer. `ptp_msg_is_sync()` parses then compares the message type to `PTP_MSGTYPE_SYNC`.

## Dependencies and Integration
Depends on skbuff MAC header state, Linux classic BPF, `linux/ptp_classify.h`, VLAN/IP/UDP header constants, and init-time classifier setup. Network timestamping and PTP-capable drivers can use the exported classifier.

## Risks and Test Signals
Risks include fixed-offset parsing for IPv6 extension headers, non-linear skb header availability, VLAN depth limited to one tag in this filter, and BUG_ON if BPF creation fails during init. Test signals are classification for IPv4, IPv6, VLAN L2, VLAN IPv4/IPv6, fragment rejection, wrong-port rejection, general-message rejection for L2 cases, parse bounds checks on truncated skbs, and Sync-message detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ptp_classifier.c -->
