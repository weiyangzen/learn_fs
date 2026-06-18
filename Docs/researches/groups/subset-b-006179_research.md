# subset-b-006179 Research

Grouped research for Linux net/core files under `sources/distributed-fs/ceph-client`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev.h -->
# sources/distributed-fs/ceph-client/net/core/dev.h

Purpose: Internal net/core header for netdevice helpers that are shared by implementation files but intentionally not exposed as broad public UAPI. It declares NAPI lookup helpers, netdevice scoped lock iterators, address-list management, linkwatch hooks, RX queue memory-provider helpers, netdevice rename and namespace APIs, MTU/proto-down/carrier/group/queue-length helpers, RX-mode synchronization, NAPI runtime configuration accessors, XDP debug checks, and hardware timestamp helper prototypes.

Important APIs, types, and functions: `struct sd_flow_limit` stores RPS/RFS flow-limit bucket history under RCU. `struct netdev_name_node` links primary and alternate interface names to a `net_device`. `netdev_put_lock()`, `netdev_xa_find_lock()`, and the `for_each_netdev_lock_scoped()` cleanup macro provide netdevice iteration with automatic unlock. The ops-compat variants support call sites that need `netdev_lock_ops_compat`. Inline setters update `IFF_UP`, GSO/GRO maximum sizes, and per-device/per-NAPI values for `defer_hard_irqs`, `gro_flush_timeout`, and threaded NAPI mode. Prototypes such as `dev_change_name()`, `dev_change_flags()`, `dev_set_mac_address_user()`, `__dev_set_rx_mode()`, `netif_rx_mode_sync()`, `dev_set_hwtstamp_phylib()`, and `net_hwtstamp_validate()` are implemented by sibling net/core files.

Control flow and state: This header is mostly declarations plus lock-aware inlines. Netdevice state updates use `READ_ONCE()`/`WRITE_ONCE()` where values are read locklessly by datapath code, notably GSO/GRO limits and NAPI timer fields. `netif_set_up()` updates both exported flags and the internal `dev->up` field, acquiring the normal netdev lock only when ops locking is not required. The NAPI bulk setters write the device default, each current `napi_struct`, and persisted `napi_config[]` entries so future queue/NAPI construction inherits the same values.

Dependencies and integration points: It depends on `linux/netdevice.h`, `net/netdev_lock.h`, cleanup helpers, and configuration options such as `CONFIG_PROC_FS`, `CONFIG_NET_SHAPER`, `CONFIG_DEBUG_NET`, and `CONFIG_BPF_SYSCALL`. It is included by files such as `dev_api.c`, `dev_ioctl.c`, and `dev_addr_lists.c`. The declared APIs bridge RTNL, per-net namespace state, netlink extended acknowledgements, driver `net_device_ops`, NAPI, XDP, hardware timestamping, and page-pool memory providers.

Risks: Many helpers encode locking expectations rather than enforcing them at compile time. Misusing scoped netdevice iterators, changing fields without the matching `WRITE_ONCE()`, or updating only the device default but not `napi_config[]` can create lifetime races or inconsistent behavior across existing and future NAPI instances. The `napi_assert_will_not_race()` debug helper catches only best-effort scheduling hazards.

Test signals: Build coverage should include configurations with and without procfs, net shaper, BPF/XDP debug, and hardware timestamping. Runtime signals include successful netdevice rename, MTU, carrier, proto-down, RX-mode, threaded-NAPI, and timestamp ioctl/netlink paths without lockdep splats or data-race reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_addr_lists.c -->
# sources/distributed-fs/ceph-client/net/core/dev_addr_lists.c

Purpose: Implements netdevice hardware address lists for primary device addresses, secondary unicast addresses, and multicast addresses, plus RX filtering synchronization to drivers. Lists are backed by both an RCU list and an rbtree keyed by address and address type for ordered lookup and duplicate detection.

Important APIs, types, and functions: Core helpers include `__hw_addr_add_ex()`, `__hw_addr_del_ex()`, `__hw_addr_sync()`, `__hw_addr_sync_multiple()`, `__hw_addr_sync_dev()`, `__hw_addr_ref_sync_dev()`, `__hw_addr_unsync_dev()`, `__hw_addr_flush()`, and `__hw_addr_init()`. Public wrappers include `dev_addr_init()`, `dev_addr_mod()`, `dev_addr_add()`, `dev_addr_del()`, `dev_uc_add[_excl]()`, `dev_uc_del()`, `dev_uc_sync[_multiple]()`, `dev_uc_unsync()`, `dev_mc_add[_global/_excl]()`, `dev_mc_del[_global]()`, `dev_mc_sync[_multiple]()`, and `dev_mc_unsync()`. KUnit-exported snapshot helpers `__hw_addr_list_snapshot()` and `__hw_addr_list_reconcile()` support async RX-mode driver callbacks.

Control flow and state: Each `netdev_hw_addr` carries `refcount`, `global_use`, `synced`, and `sync_cnt`. Add paths either create a new entry or bump references; delete paths clear global/sync ownership, decrement references, and RCU-free the entry at zero. Sync paths treat `sync_cnt` as the number of driver or lower-device installations, with distinct one-destination and multiple-destination semantics. `dev_addr_mod()` temporarily removes the primary address from the rbtree, edits bytes in place, updates `dev_addr_shadow`, and reinserts it to preserve tree ordering.

RX-mode flow: Address list changes call `__dev_set_rx_mode()`. If the driver supports `ndo_set_rx_mode_async`, requires ops locking, or has RX flag changes, the device is queued on a global `rx_mode_list` protected by `rx_mode_lock` and processed by `rx_mode_work` under RTNL and `netdev_lock_ops()`. The async path snapshots UC/MC lists under `netif_addr_lock_bh()`, lets the driver update hardware from snapshots without holding that lock, then reconciles sync-count deltas back into the real lists. `netif_rx_mode_sync()` can steal queued work and run it inline so syscalls that need immediate visibility can force completion.

Dependencies and integration points: The file depends on `linux/netdevice.h`, RTNL, list/rbtree/RCU primitives, workqueues, `netdev_hold()` tracking, `net_device_ops` RX-mode callbacks, and helpers declared in `dev.h`. It integrates with notifier calls for primary address changes, layered devices that sync UC/MC lists to lower devices, and drivers that maintain hardware filter tables.

Risks: Correctness depends on address-list locks, RTNL, and netdev ops locks being nested as documented. Refcount and `sync_cnt` transitions are subtle, especially stale entries where `refcount == sync_cnt` represent addresses still programmed in hardware but no longer requested by users. Async snapshot reconciliation must handle concurrent add/remove without losing a needed unsync. RX-mode queue cleanup must release netdevice trackers under the spinlock and drop the device reference after ops unlock to avoid use-after-free.

Test signals: KUnit coverage in `dev_addr_lists_test.c` exercises primary address updates, add/delete semantics, exclusive UC adds, sync/unsync behavior, snapshot reconciliation for concurrent remove and re-add, and a snapshot benchmark. Additional integration signals are lockdep-clean multicast ioctls, layered-device UC/MC sync, async `ndo_set_rx_mode_async` drivers, and no leaked RX-mode references during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_addr_lists.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_addr_lists_test.c -->
# sources/distributed-fs/ceph-client/net/core/dev_addr_lists_test.c

Purpose: KUnit suite for `struct netdev_hw_addr_list` behavior and the netdevice address-list helpers implemented in `dev_addr_lists.c`. It validates both longstanding primary/secondary address operations and the newer snapshot/reconcile path used by async RX-mode updates.

Important APIs, types, and functions: `struct dev_addr_test_priv` records bitsets of addresses seen, synced, and unsynced by fake driver callbacks. `dev_addr_test_sync()` and `dev_addr_test_unsync()` model hardware programming callbacks. Fixture hooks allocate, register, unregister, and free an Ethernet netdevice. Test cases include `dev_addr_test_basic`, `dev_addr_test_sync_one`, `dev_addr_test_add_del`, `dev_addr_test_del_main`, `dev_addr_test_add_set`, `dev_addr_test_add_excl`, four snapshot-concurrency tests, and `dev_addr_test_snapshot_benchmark`.

Control flow and state: Each test takes RTNL around netdevice operations. Address bytes are simple repeated values so callbacks can map each address to one bit. Tests use `eth_hw_addr_set()`, `dev_addr_set()`, `dev_addr_add()`, `dev_addr_del()`, `dev_uc_add()`, `dev_uc_del()`, `dev_uc_add_excl()`, `__hw_addr_sync_dev()`, `__hw_addr_list_snapshot()`, and `__hw_addr_list_reconcile()` to assert list count, entry address, `sync_cnt`, `refcount`, and callback side effects.

Dependencies and integration points: The suite uses KUnit, Ethernet netdevice allocation, RTNL, and KUnit visibility exports from `dev_addr_lists.c`. It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace to reach snapshot and flush helpers that are not general kernel APIs.

Risks covered: The tests explicitly target deleting the primary address, duplicate exclusive adds, tree/list consistency after primary address mutation, stale synced entries, concurrent removal after snapshot sync, concurrent re-add during snapshot unsync, and unrelated concurrent removal while another address is synced. These are the highest-risk state transitions in the address-list implementation.

Risks not fully covered: The suite does not instantiate a real `ndo_set_rx_mode_async` driver, does not exercise `netif_rx_mode_queue()` workqueue lifetime, multicast-specific paths, `__hw_addr_ref_sync_dev()` reference-aware callbacks, allocation failures across all snapshot phases, or lockdep behavior under nested upper/lower device calls.

Test signals: Passing suite name `dev-addr-list-test` is the direct signal. The slow benchmark logs timing for 1024 addresses across 1000 snapshots, useful for catching pathological snapshot cost regressions but not a strict performance assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_addr_lists_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_api.c -->
# sources/distributed-fs/ceph-client/net/core/dev_api.c

Purpose: Provides exported netdevice management APIs that wrap lower-level `netif_*` helpers with the correct netdev lock or ops lock. These functions are common entry points for in-kernel callers and uAPI adapters that need to change names, flags, aliases, MAC addresses, MTU, carrier, promiscuity, allmulti state, XDP state, threaded NAPI mode, and device state notifications.

Important APIs, types, and functions: Key exports include `dev_set_alias()`, `dev_change_flags()`, `dev_set_mac_address_user()`, `dev_change_net_namespace()`, `dev_open()`, `dev_close()`, `dev_eth_ioctl()`, `dev_set_mtu()`, `dev_disable_lro()`, `dev_set_promiscuity()`, `dev_set_allmulti()`, `dev_set_mac_address()`, `dev_xdp_propagate()`, `netdev_state_change()`, and `dev_set_threaded()`. Internal wrappers also cover `dev_change_name()`, `dev_set_group()`, `dev_change_carrier()`, `dev_change_tx_queue_len()`, and `dev_change_proto_down()`.

Control flow and state: The file is deliberately thin. Each function acquires `netdev_lock_ops()` or `netdev_lock()` as appropriate, calls the corresponding `netif_*` operation, and releases the lock. Calls that alter RX filtering visibility, such as flags, promiscuity, and allmulti changes, call `netif_rx_mode_sync()` before unlocking so deferred async RX-mode work is completed before returning to userspace. `dev_set_mac_address_user()` additionally serializes through `dev_addr_sem` around MAC address changes.

Dependencies and integration points: It depends on `linux/netdevice.h`, `net/netdev_lock.h`, and declarations in `dev.h`. It is used by ioctl, rtnetlink, drivers, and other kernel subsystems that need a stable lock boundary without directly calling lower-level `netif_*` functions.

Risks: Because most logic lives below this layer, the main risks are missing lock coverage, using `netdev_lock()` where ops locking is required or vice versa, and forgetting RX-mode synchronization for APIs whose users expect filtering changes to be visible on return. `dev_eth_ioctl()` must guard driver callbacks with both ops presence and `netif_device_present()` to avoid invoking removed hardware.

Test signals: Functional signals include successful `ip link` flag, MTU, name, alias, MAC, carrier, proto-down, promisc/allmulti, XDP, and threaded-NAPI operations under lockdep. Async RX-mode drivers should observe that userspace-facing setters return only after `netif_rx_mode_sync()` has run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_ioctl.c -->
# sources/distributed-fs/ceph-client/net/core/dev_ioctl.c

Purpose: Implements classic network-device ioctl handling for interface queries and mutations. It translates `SIOCxIF*`, bonding, private device, MII, ethtool, WAN, multicast, and hardware timestamp commands into netdevice operations with the required user-copy, capability, RTNL, RCU, and netdev ops locking.

Important APIs, types, and functions: `dev_ifconf()` implements `SIOCGIFCONF` with compat handling. `dev_ioctl()` is the main dispatcher. Helper paths include `dev_ifname()`, `dev_ifsioc_locked()` for RCU-safe read-only queries, `dev_ifsioc()` for RTNL-serialized mutations, `dev_load()` for autoloading absent interfaces, `net_hwtstamp_validate()`, `dev_get_hwtstamp_phylib()`, `dev_set_hwtstamp_phylib()`, `generic_hwtstamp_get_lower()`, and `generic_hwtstamp_set_lower()`.

Control flow and state: `dev_ioctl()` normalizes interface names, strips alias suffixes after `:`, sets the caller's copyout flag, and dispatches by command class. Read-only queries use RCU or specialized helpers. Privileged mutating commands check `CAP_NET_ADMIN` in the target net namespace or global capability for legacy map/queue commands, then take `rtnl_net_lock()` and call `dev_ifsioc()`. Multicast add/delete wraps `dev_mc_add_global()` or `dev_mc_del_global()` with ops locking and `netif_rx_mode_sync()`. Unknown private ranges are delegated to driver callbacks if present.

Hardware timestamping flow: Set paths copy `hwtstamp_config` from userspace, convert to `kernel_hwtstamp_config`, validate flag/tx/rx enums, run DSA conduit validation, require `ndo_hwtstamp_set`, and call `dev_set_hwtstamp_phylib()` under ops lock. That helper gives phylib timestamping precedence unless the registered provider says netdev, supports `see_all_hwtstamp_requests`, and rolls back netdev changes if PHY programming fails. Get paths call `dev_get_hwtstamp_phylib()` and copy an updated config back unless an unconverted driver already copied to userspace.

Dependencies and integration points: The file integrates with inet `gifconf`, rtnetlink locking, netdevice ops, phylib/PTP timestamp providers, DSA validation, ethtool, wireless extensions, bridge and bonding ioctls, private driver commands, and module autoloading via `request_module()`.

Risks: The command matrix has legacy compatibility constraints. Incorrect capability checks can expose privileged mutations; missed compat layout handling can corrupt user data; missing `netif_device_present()` can call into removed hardware; timestamp rollback paths can leave NIC and PHY state inconsistent if driver get/set methods are incomplete. `dev_load()` may trigger module autoloading from interface names, so caller context and capabilities matter.

Test signals: Exercise `SIOCGIFCONF` in native and compat modes; `SIOCGIFFLAGS`, MTU, index, and txqlen reads; privileged MTU, name, flags, MAC, broadcast, multicast add/delete, and queue-length changes; timestamp get/set with netdev-only, phylib-only, and `see_all_hwtstamp_requests` devices; private/bonding/MII delegation; and lockdep-clean operation under RTNL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dev_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/devmem.c -->
# sources/distributed-fs/ceph-client/net/core/devmem.c

Purpose: Implements device-memory TCP support backed by dma-buf bindings. It maps a user-provided dma-buf to a network device DMA domain, exposes page-sized `net_iov` allocations through a gen_pool, binds those allocations to page-pool memory providers for RX queues, and supports TX lookups by binding id and virtual dma-buf offset.

Important APIs, types, and functions: The global `net_devmem_dmabuf_bindings` xarray maps binding ids to `struct net_devmem_dmabuf_binding`. Binding lifecycle is handled by `net_devmem_bind_dmabuf()`, `net_devmem_unbind_dmabuf()`, `net_devmem_lookup_dmabuf()`, `__net_devmem_dmabuf_binding_free()`, and percpu-ref release scheduling. Allocation APIs are `net_devmem_alloc_dmabuf()`, `net_devmem_free_dmabuf()`, `net_devmem_get_binding()`, and `net_devmem_get_niov_at()`. Page-pool provider hooks are `mp_dmabuf_devmem_init()`, `mp_dmabuf_devmem_alloc_netmems()`, `mp_dmabuf_devmem_destroy()`, `mp_dmabuf_devmem_release_page()`, `mp_dmabuf_devmem_nl_fill()`, and `mp_dmabuf_devmem_uninstall()`.

Control flow and state: Binding creation obtains the dma-buf, allocates a binding, initializes an xarray of bound RX queues and a percpu ref, attaches and maps the dma-buf to the DMA device, optionally allocates a TX virtual-address vector, creates a page-sized gen_pool, then walks the mapped sg table. Each DMA segment gets a `dmabuf_genpool_chunk_owner` with a `net_iov_area`, base virtual offset, base DMA address, and initialized `net_iov` array. The binding is inserted into the global xarray and the netlink socket's binding list. Unbind erases the id, waits for in-flight network readers with `synchronize_net()`, detaches RX queue memory providers, and kills the percpu ref; final cleanup is deferred to workqueue context after all users put references.

Dependencies and integration points: This code depends on dma-buf attach/map APIs, scatter-gather DMA metadata, genalloc, xarray, page-pool memory-provider hooks, `net_iov`/`netmem`, TCP socket dst lookup, and netdev RX queue leasing through `netif_mp_open_rxq()` and `netif_mp_close_rxq()`. Netlink code supplies the `netdev_nl_sock` private binding list and extack messages.

Risks: Lifetime is the primary hazard. TX skbs can hold `net_iov` references after userspace unbinds, so percpu refs must cover every path. The global xarray erase plus `synchronize_net()` protects lookup, but callers must put bindings reliably. DMA segment lengths are divided by `PAGE_SIZE`; non-page-aligned mappings or wrong DMA direction assumptions can break allocation. `mp_dmabuf_devmem_uninstall()` clears `binding->dev` when the last RX queue is removed, affecting TX reachability checks. Cleanup warns if the gen_pool is not fully returned before destruction.

Test signals: Useful tests include binding unsupported devices, invalid fds, RX and TX bindings, multiple RX queues, unbind while page-pool allocations are outstanding, TX lookup with expired route rebuild, TX lookup on a different dst device, `net_devmem_get_niov_at()` bounds/offset behavior, and page-pool release with expected refcount 1. KASAN, lockdep, and DMA API debug are valuable for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/devmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/devmem.h -->
# sources/distributed-fs/ceph-client/net/core/devmem.h

Purpose: Internal header for dma-buf backed network device memory. It defines the binding object shared by netlink, RX queue memory providers, TX lookup, and `net_iov` ownership, plus inline helpers and stubs for builds without `CONFIG_NET_DEVMEM`.

Important APIs, types, and functions: `struct net_devmem_dmabuf_binding` owns the dma-buf, attachment, sg table, associated net_device, gen_pool, bound RX queue xarray, binding id, DMA direction, TX vector, mutex, percpu ref, netlink list node, and deferred unbind work. `struct dmabuf_genpool_chunk_owner` ties gen_pool chunks to `net_iov_area` metadata and base DMA addresses. Inline helpers map `net_iov` values to owners, bindings, binding ids, virtual addresses, and percpu-ref get/put. Prototypes cover bind, queue bind, lookup, unbind, `net_iov` ref management, allocation/free, TX binding lookup, and virtual-address lookup.

Control flow and state: The header documents the intended lifetime: userspace holds a binding reference through netlink, each page pool holds a reference, and individual `net_iov` users can hold references so the dma-buf mapping outlives skbs in flight. Virtual addresses are synthetic offsets within the dma-buf, computed from owner base plus `net_iov_idx() << PAGE_SHIFT`; DMA addresses are derived in the C file from each chunk owner.

Dependencies and integration points: It depends on `net/netmem.h`, `net/netdev_netlink.h`, netlink extack types, dma-buf types, xarray, gen_pool, page-pool memory provider parameters, and sockets for TX binding lookup. With `CONFIG_NET_DEVMEM` disabled, it returns `-EOPNOTSUPP`, `NULL`, or no-op stubs so callers can compile without feature-specific ifdefs.

Risks: The binding struct is shared across asynchronous paths, so field ownership must be respected. `binding->dev` is protected by `binding->lock` for updates but read with `READ_ONCE()` in TX lookup. Stubs must preserve caller expectations: disabled builds should fail cleanly rather than silently allowing devmem behavior. Virtual address arithmetic assumes page-sized `net_iov` slots.

Test signals: Build coverage with `CONFIG_NET_DEVMEM=y` and disabled is essential. Runtime signals are correct netlink bind/unbind reporting, stable binding ids, correct `net_iov` to binding/id mapping, and no stale binding access when queue uninstallation clears the device pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/devmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/drop_monitor.c -->
# sources/distributed-fs/ceph-client/net/core/drop_monitor.c

Purpose: Implements the `NET_DM` generic-netlink drop monitor. It reports software packet drops from tracepoints and hardware drops from devlink trap reports, in either summary mode or packet mode, and exposes configuration and drop statistics through generic netlink.

Important APIs, types, and functions: Global state includes `trace_state`, `monitor_hw`, `net_dm_mutex`, `dm_hit_limit`, `dm_delay`, `dm_hw_check_delta`, `net_dm_alert_mode`, `net_dm_trunc_len`, and `net_dm_queue_len`. Per-CPU state is `struct per_cpu_dm_data`, containing a raw spinlock, either a summary skb or hardware entry table, a packet drop queue, work item, timer, and stats. `net_dm_alert_ops` selects summary or packet callbacks. Core paths include `net_dm_trace_on_set()`, `net_dm_trace_off_set()`, `net_dm_hw_monitor_start()`, `net_dm_hw_monitor_stop()`, `net_dm_cmd_config()`, `net_dm_cmd_trace()`, `net_dm_cmd_config_get()`, `net_dm_cmd_stats_get()`, and module init/exit.

Control flow and state: Starting software monitoring initializes per-CPU work/timers and summary skbs, registers `kfree_skb` and `napi_poll` trace probes, and holds a module reference. Summary software drops aggregate program counters into a per-CPU netlink alert skb and send after `dm_delay`. Packet software mode clones dropped skbs, records drop reason and PC in skb control buffer, queues up to `net_dm_queue_len`, and sends one `NET_DM_CMD_PACKET_ALERT` per clone. Hardware monitoring similarly registers the devlink trap tracepoint; summary mode aggregates trap names, while packet mode clones skbs and deep-copies trap metadata.

Dependencies and integration points: The module depends on generic netlink, tracepoints for `kfree_skb`, `napi_poll`, and optional `devlink_trap_report`, netdevice notifiers, drop-reason registries, per-CPU stats, timers, workqueues, and multicast group permissions. A netdevice notifier allocates `dev->dm_private` stats deltas so NAPI polling can infer hardware drops from `rx_dropped`.

Risks: Probe callbacks run in atomic contexts, so allocation uses `GFP_ATOMIC` and must fail safely. Packet mode can consume memory quickly; queue overflow is counted in per-CPU stats and clones are dropped. Metadata lifetime is delicate because hardware packet mode holds netdevice references in copied devlink metadata. Monitoring mode cannot be reconfigured while active, and tracepoint unregister must synchronize before freeing queued state. Summary mode stores program counters in netlink payloads and rejects architectures where pointers exceed 64 bits.

Test signals: Validate generic-netlink `CONFIG`, `START`, `STOP`, `CONFIG_GET`, and `STATS_GET`; software summary alerts on `kfree_skb`; packet alerts with drop reason, symbol, timestamp, input port, protocol, and truncation; queue overflow stats; hardware summary and packet alerts when devlink is enabled; clean start/stop cycles; netdevice register/unregister `dm_private` cleanup; and no alerts after stop returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/drop_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dst.c -->
# sources/distributed-fs/ceph-client/net/core/dst.c

Purpose: Protocol-independent destination cache core. It initializes, allocates, releases, destroys, and blackholes `struct dst_entry` objects, manages destination metrics copy-on-write, and allocates metadata destinations used by tunnels and XFRM.

Important APIs, types, and functions: Exports include `dst_discard_out()`, `dst_default_metrics`, `dst_init()`, `dst_alloc()`, `dst_dev_put()`, `dst_release()`, `dst_release_immediate()`, `dst_cow_metrics_generic()`, `__dst_destroy_metrics_generic()`, blackhole helpers, `metadata_dst_alloc()`, `metadata_dst_free()`, `metadata_dst_alloc_percpu()`, and `metadata_dst_free_percpu()`. Static `dst_blackhole_ops` supplies no-op or discard behavior for metadata and blackhole destinations.

Control flow and state: `dst_init()` takes a netdevice reference, installs default read-only metrics, default discard input/output, obsolete state, optional XFRM/lwt metadata, `rcuref`, uncached route list state, flags, and destination operation counters. `dst_alloc()` optionally invokes protocol GC before allocating from the protocol cache. `dst_release()` drops the rcuref, resets embedded metadata dst caches when needed, decrements dst counters, and destroys through RCU; `dst_release_immediate()` does synchronous destruction. Destruction calls protocol-specific destroy hooks, drops netdevice and lwt refs, frees metadata or slab storage, then releases XFRM child dsts.

Dependencies and integration points: The file depends on netdevice references, `dst_ops`, lightweight tunnels, XFRM, route metrics, RCU, slab caches, and optional `CONFIG_DST_CACHE`. Metadata destinations integrate with tunnel info (`METADATA_IP_TUNNEL`) and XFRM (`METADATA_XFRM`).

Risks: Destination lifetime is heavily concurrent. A stale dst must be marked dead and redirected to `blackhole_netdev` before device removal using `dst_dev_put()`. Metrics COW uses `cmpxchg()` and refcounted metrics; errors can leak or double-free metrics. Metadata dsts are allocated as flexible objects and use `DST_NOCOUNT`, so freeing must match metadata type. Synchronous release is unsafe where RCU readers may still observe the dst.

Test signals: Route allocation/release under device unregister, blackhole MTU behavior, metadata tunnel dst allocation/free with embedded dst_cache reset, XFRM metadata dst release, metrics COW races under parallel writers, protocol GC threshold behavior, and KASAN/RCU debug during route teardown are relevant validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dst_cache.c -->
# sources/distributed-fs/ceph-client/net/core/dst_cache.c

Purpose: Per-CPU cache for `dst_entry` pointers and associated source addresses. It lets tunnel and routing users cache a validated destination per CPU while supporting global reset and IPv4/IPv6 source-address retrieval.

Important APIs, types, and functions: `struct dst_cache_pcpu` stores refresh timestamp, cached dst, local BH lock, protocol cookie, and either IPv4 or IPv6 source address. Exports include `dst_cache_get()`, `dst_cache_get_ip4()`, `dst_cache_set_ip4()`, `dst_cache_set_ip6()`, `dst_cache_get_ip6()`, `dst_cache_init()`, `dst_cache_destroy()`, and `dst_cache_reset_now()`.

Control flow and state: Set paths take the current CPU's `local_lock_nested_bh()`, release any old cached dst, hold the new dst, store validation cookie, and save source address. Get paths take the same local lock, hold the cached dst for the caller, then validate it against `reset_ts`, `dst->obsolete`, and protocol `ops->check()` using the stored cookie. Invalid entries are cleared and released. `dst_cache_reset_now()` advances the global reset timestamp and clears all per-CPU dsts immediately.

Dependencies and integration points: The file depends on percpu allocation, local locks, softirq context expectations, IPv4 route tables, optional IPv6 fib cookies, and dst reference helpers. It is used by metadata tunnel destinations and tunnel protocols that repeatedly resolve similar routes.

Risks: Helpers warn if used outside softirq context for per-CPU dst manipulation. Missing dst holds or releases would leak routes or return freed routes. `reset_ts` validation is timestamp based, so callers that require immediate invalidation must use `dst_cache_reset_now()`. IPv6 correctness depends on storing and checking route cookies from `rt6_get_cookie()`.

Test signals: Validate cache hit/miss behavior per CPU, reset invalidation, obsolete dst `ops->check()` failure, IPv4 and IPv6 source-address return, destroy releasing all per-CPU references, and lockdep-clean use from BH/softirq contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/dst_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/failover.c -->
# sources/distributed-fs/ceph-client/net/core/failover.c

Purpose: Generic failover infrastructure for paravirtual networking and accelerated datapath live migration. It associates a failover master netdevice with Ethernet slave devices that share the same permanent MAC address and forwards slave registration, unregister, link-change, and name-change events to driver-provided failover operations.

Important APIs, types, and functions: Global state is `failover_list` protected by `failover_lock`. Public exports are `failover_register()`, `failover_unregister()`, and `failover_slave_unregister()`. Internal helpers include `failover_get_bymac()`, `failover_slave_register()`, `failover_slave_link_change()`, `failover_slave_name_change()`, `failover_event()`, and `failover_existing_slave_register()`.

Control flow and state: `failover_register()` validates an Ethernet master and ops table, allocates a `struct failover`, stores ops and master via RCU assignment, holds the master netdevice, marks it `IFF_FAILOVER`, inserts it in the global list, then scans existing devices in the same net namespace for MAC-matching slaves. Slave registration checks Ethernet type and matching master, calls optional pre-register, installs an RX handler, links the slave as an active-backup upper/lower relationship, marks `IFF_FAILOVER_SLAVE | IFF_NO_ADDRCONF`, then calls the driver's `slave_register()` hook. Failure unwinds upper link, flags, and RX handler. Unregister reverses the relationship and invokes driver hooks.

Dependencies and integration points: The module depends on netdevice notifiers, RTNL, Ethernet permanent addresses, LAG upper info, RX handler registration, upper/lower device links, `netdev_lock_ops()` during existing-slave scan, and driver-supplied `struct failover_ops`.

Risks: Matching by permanent MAC is simple but can bind unexpected devices if MAC assignment is wrong. Registration unwind must keep RX handler, upper link, and flags consistent. `failover_get_bymac()` returns a master without taking a new reference; callers rely on RTNL and failover list lifetime. Existing-slave scan locks RTNL and then per-device ops locks, so lock ordering must stay aligned with netdevice core rules.

Test signals: Register a failover master before and after slave creation; verify RX handler and upper link installation; exercise pre-register and register failure unwind; unregister slaves and masters in both orders; link/name change callbacks only when master is running; and module init/exit notifier registration without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/failover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/fib_notifier.c -->
# sources/distributed-fs/ceph-client/net/core/fib_notifier.c

Purpose: Per-network-namespace FIB notifier infrastructure. It lets route-family providers register dump and sequence callbacks, and lets consumers register notifier blocks after receiving a consistent dump of current FIB state.

Important APIs, types, and functions: `struct fib_notifier_net` stores the per-net list of `fib_notifier_ops` and an atomic notifier chain. Exports include `call_fib_notifier()`, `call_fib_notifiers()`, `register_fib_notifier()`, `unregister_fib_notifier()`, `fib_notifier_ops_register()`, and `fib_notifier_ops_unregister()`. Internal helpers `fib_seq_sum()`, `fib_net_dump()`, and `fib_dump_is_consistent()` implement dump-then-subscribe consistency.

Control flow and state: Route-family code registers a copied `fib_notifier_ops` template per net namespace. Consumers call `register_fib_notifier()`, which reads the aggregate sequence sum, asks all registered ops to dump current state into the notifier block, registers the block, then rechecks the sequence. If state changed during the dump, it unregisters, calls an optional cleanup callback, and retries up to `FIB_DUMP_MAX_RETRIES`. Events later use `atomic_notifier_call_chain()` and convert notifier return values to errno.

Dependencies and integration points: The file depends on pernet generic storage, RCU-protected ops lists, module owner references around family callbacks, atomic notifier chains, netlink extack reporting, and route-family implementations such as IPv4/IPv6 FIB rules or route tables.

Risks: Consistency relies on each provider's sequence counter changing for every state transition and dump output matching that sequence. `try_module_get()` failures skip a provider, so unload races need careful owner management. Registration can fail with `-EBUSY` under continuous FIB churn. Per-net exit warns if providers remain registered.

Test signals: Register providers for multiple families, register consumers during concurrent route changes, verify cleanup callback on retry, trigger max retry failure under artificial churn, unregister notifier blocks, unregister ops under RCU, and check pernet cleanup warnings remain silent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/fib_notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/fib_rules.c -->
# sources/distributed-fs/ceph-client/net/core/fib_rules.c

Purpose: Generic routing policy rule engine shared by address families. It stores per-net `fib_rules_ops` instances, parses rtnetlink rule add/delete/dump requests, performs rule lookup against `flowi`, maintains goto-rule targets, notifies FIB listeners, and tracks interface-name attachment as netdevices appear, disappear, or are renamed.

Important APIs, types, and functions: Exports include `fib_rule_matchall()`, `fib_default_rule_add()`, `fib_rules_register()`, `fib_rules_unregister()`, `fib_rules_lookup()`, `fib_rules_dump()`, `fib_rules_seq_read()`, `fib_newrule()`, and `fib_delrule()`. Major internal helpers include `lookup_rules_ops()`, `fib_rule_match()`, `call_fib_rule_notifiers()`, `rule_find()`, `fib_nl2rule()`, `fib_nl2rule_rtnl()`, `rule_exists()`, `fib_nl_fill_rule()`, `fib_nl_dumprule()`, `notify_rule_change()`, `attach_rules()`, and `detach_rules()`.

Control flow and state: Each net namespace owns an RCU list of `fib_rules_ops` protected for modification by `rules_mod_lock`. Each ops instance owns an ordered `rules_list`. Lookup walks rules under RCU, checks interface indices, marks, tunnel id, l3mdev, UID range, family-specific match callback, optional inversion, goto targets, action callback, and suppress callback. Successful results attach the matched rule to `fib_lookup_arg` with a reference unless lookup flags request no ref.

Netlink rule mutation flow: `fib_newrule()` looks up family ops, parses attributes under `fib_rule_policy`, builds a candidate rule with UID, mark, tunnel, ports, masks, l3mdev, goto, table, action, and family-specific payload, then under RTNL resolves interface names to indices and default priority. It rejects duplicates under `NLM_F_EXCL`, calls family configure, sends FIB add notifiers, inserts by priority, resolves pending goto rules, updates metadata-tunnel demand, notifies rtnetlink listeners, flushes route cache, and drops temporary refs. `fib_delrule()` builds a match template, finds the rule, rejects permanent rules, calls family delete, unlinks the rule, repairs goto targets, sends delete notifications, flushes caches, and frees the template.

Dependencies and integration points: The file depends on rtnetlink message handlers for `RTM_NEWRULE`, `RTM_DELRULE`, and `RTM_GETRULE`; pernet operations; netdevice notifier events; UID namespace conversion; l3mdev helpers; IP tunnel metadata demand; IPv4/IPv6 indirect call optimizations; and FIB notifier APIs. Family-specific `fib_rules_ops` supply match, configure, compare, fill, action, suppress, delete, nlmsg payload, and cache flush behavior.

Risks: Policy rules are order-sensitive and concurrently read under RCU. Goto rules can become unresolved; backward gotos are rejected to avoid loops, but target repair on deletion is complex. Interface name rules use `-1` detached indices and are reattached on register/rename, so stale names or l3mdev status changes can affect lookup. UID ranges require the caller to be in the target net user namespace. Port masks are valid only with single ports, not ranges. Notifier errors during add abort rule insertion, while delete notifiers are called after unlink. Route cache flushes must happen after every successful mutation.

Test signals: Validate add/delete/dump for IPv4 and IPv6 families; priority ordering and default priority selection; duplicate rejection; permanent-rule delete rejection; goto target resolution, unresolved dump flags, and target repair after delete; interface attach/detach on register, unregister, and rename; UID namespace permission checks; sport/dport ranges and masks; l3mdev/table mutual exclusion; FIB notifier sequence increments; and strict dump request validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/fib_rules.c -->
