# subset-b-004685

Grouped research for netdevsim, netkit, nlmon, NTB netdev, and selected ovpn source files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/fib.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/fib.c

Purpose: implements netdevsim's simulated FIB, rule, and nexthop offload engine. It lets tests exercise devlink resource accounting, route offload flags, nexthop notifier behavior, resilient nexthop bucket updates, and route/nexthop failure injection without real hardware.

Important APIs/types/functions: `struct nsim_fib_data` owns notifier blocks, route and nexthop rhashtables, workqueues, debugfs controls, and devlink resource callbacks. `nsim_fib_create()`/`nsim_fib_destroy()` manage lifetime. `nsim_fib_event_nb()` receives FIB/rule events, `nsim_fib_event_work()` applies queued route changes, and `nsim_nexthop_event_nb()` handles nexthop changes synchronously under `nh_lock`. `nsim_fib_get_val()` exposes current/max resource values to the rest of netdevsim.

Control flow: create initializes debugfs, rhashtables, locks, work items, resource maxima from devlink, nexthop notifier, FIB notifier, and occupancy getters. Route replace/delete notifications account resources in notifier context, hold referenced route objects, enqueue events, and later update rhashtables and route hardware flags from workqueue context. IPv4 tracks `fib_info`; IPv6 groups sibling `fib6_info` entries into one simulated route and can append/delete subsets. Dump inconsistency flushes queued work and clears programmed state. Destroy unregisters callbacks, cancels work, drains rhashtables, and removes debugfs.

State and persistence: all state is in memory: atomic counters for IPv4/IPv6 FIB and rule occupancy, a nexthop occupancy counter, route/nexthop hash tables, a queued event list, and debugfs booleans. Route and nexthop objects hold kernel references until destroyed. No disk persistence exists.

Dependencies and integration: integrates with `fib_notifier`, `nexthop` notifiers, `devlink` resources, `debugfs`, IPv4/IPv6 route hardware flag helpers, `rhashtable`, workqueues, and the enclosing `nsim_dev`. Debugfs files inject failures for route offload, route deletion, resilient nexthop-group replace, nexthop bucket replace, and bucket activity.

Risks: accounting must stay consistent when queued work later fails; several paths intentionally decrement counts after replace detection. The event queue uses GFP_ATOMIC allocation and schedules a flush on failed delete preparation. `nsim_crypto` is not involved, but RCU/reference lifetimes of `fib_info` and `fib6_info` are critical. Failure injection can leave the kernel FIB with offload-failed flags by design.

Test signals: useful tests create/delete IPv4/IPv6 routes and rules with tight devlink resource sizes, verify trap/offload_failed flags, exercise multipath IPv6 append/delete, resilient nexthop bucket activity, debugfs failure knobs, notifier unregister teardown, and inconsistent dump recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/fib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/health.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/health.c

Purpose: provides devlink health reporter fixtures for netdevsim. One reporter is intentionally empty, while the dummy reporter emits structured diagnostic/dump content and supports recovery failure injection.

Important APIs/types/functions: `nsim_dev_health_init()` creates `empty` and `dummy` reporters plus debugfs files. `nsim_dev_dummy_reporter_recover()`, `_dump()`, and `_diagnose()` implement the dummy reporter. `nsim_dev_health_break_write()` triggers `devlink_health_report()` using a caller-provided break message. `nsim_dev_health_exit()` releases debugfs, saved messages, and reporters.

Control flow: initialization creates reporters before debugfs. Writing `break_health` copies a user string, strips a trailing newline, passes it as private context to devlink health reporting, and frees it. Recovery optionally fails when `fail_recover` is set; otherwise it stores the recovered message. Dump and diagnose populate fmsg fields with scalar, binary, nested, and array data sized by `binary_len`.

State and persistence: `struct nsim_dev_health` stores reporter handles, debugfs root, last recovered message, binary payload length, and the `fail_recover` toggle. State is volatile and freed on exit.

Dependencies and integration: depends on devlink health reporter APIs, debugfs, random bytes, and `nsim_dev`. It is a test integration point for fmsg formatting, recovery callbacks, and devlink health userspace tooling.

Risks: the dummy fmsg builder allocates user-controlled `binary_len` bytes with `__GFP_NOWARN`; very large values can force `-ENOMEM`. Recovery stores only the last break message. The file intentionally lets tests force reporter recovery failure.

Test signals: write `break_health`, inspect devlink health dump/diagnose output, vary `binary_len`, toggle `fail_recover`, and verify reporter destruction leaves no saved message or debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/health.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/hwstats.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/hwstats.c

Purpose: simulates hardware offload extended statistics for selected netdevices, currently L3 stats, with debugfs control over tracked ifindexes and enable failure.

Important APIs/types/functions: `struct nsim_dev_hwstats` owns debugfs, an L3 tracked-device list, a netdevice notifier, lock, and periodic traffic work. `struct nsim_dev_hwstats_netdev` stores a referenced netdev, accumulated `rtnl_hw_stats64`, and flags. `nsim_dev_hwstats_init()`/`exit()` manage the subsystem. `nsim_dev_hwstats_event_off_xstats()` handles enable, disable, report-used, and report-delta notifications.

Control flow: init registers a netdevice notifier, creates `hwstats/l3/{enable_ifindex,disable_ifindex,fail_next_enable}`, and starts delayed traffic work. Enabling by ifindex grabs a netdev reference and adds an entry; if kernel offload stats are already enabled, it enables and notifies immediately. The work bumps counters every 100 ms for enabled entries. Disable pushes pending deltas when needed, notifies, removes the entry, and releases the netdev.

State and persistence: tracked devices are held in an in-memory list protected by `hwsdev_list_lock`. Stats are accumulated until reported as a delta or disabled, then reset. `fail_enable` causes exactly one enable callback to fail and is then cleared.

Dependencies and integration: uses netdevice notifier events, `netdev_offload_xstats_*` helpers, RTNL, debugfs auxiliary file data, delayed work, and `nsim_dev_net()`.

Risks: lock ordering crosses RTNL and the hwstats mutex in debugfs paths; notifier paths take only the mutex. If a tracked ifindex unregisters, the notifier must remove it before stale netdev use. The synthetic traffic schedule continues until explicit exit.

Test signals: enable an ifindex through debugfs, request offload xstats used/delta, verify periodic increments and reset-after-delta, inject `fail_next_enable`, unregister tracked devices, and confirm delayed work cancellation on module/device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/hwstats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/ipsec.c

Purpose: implements a simulated XFRM/IPsec hardware offload table for netdevsim and a debugfs reader for installed security associations.

Important APIs/types/functions: `nsim_ipsec_init()` attaches `xfrmdev_ops`, advertises ESP offload features, and creates the debugfs `ipsec` file. `nsim_ipsec_add_sa()` validates and installs SAs, `nsim_ipsec_del_sa()` removes them, and `nsim_ipsec_tx()` validates outbound skb security path state against the simulated table.

Control flow: adding an SA rejects unsupported protocols, compression, and non-crypto offload. It finds a free slot, validates AEAD as RFC4106 AES-GCM with 128-bit auth and a 128-bit key plus optional salt, records direction/address/key material, marks `xso.offload_handle` with `NSIM_IPSEC_VALID`, and increments count. Tx checks secpath, input xfrm state, slot bounds, slot use, and protocol before incrementing a tx counter.

State and persistence: `struct nsim_ipsec` stores up to 33 SAs, a debugfs dentry, install count, and tx count in netdev private memory. State is volatile and should be empty by teardown; teardown logs if SAs remain.

Dependencies and integration: depends on XFRM device offload APIs, crypto AEAD metadata, netdev feature flags, debugfs, and the netdevsim transmit path in `netdev.c`, which calls `nsim_ipsec_tx()` before forwarding.

Risks: delete trusts the offload handle index after masking; malformed or stale handles could report invalid slots. The code simulates metadata validation only; it does not encrypt/decrypt payloads. Key parsing casts key bytes to `u32 *`, so assumptions about key buffer alignment follow kernel XFRM allocation behavior.

Test signals: add inbound/outbound ESP/AH offload states, reject unsupported algorithms/auth sizes/offload types, inspect debugfs output, transmit with missing or invalid secpath, and verify teardown warning when SAs are leaked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/ipsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/macsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/macsec.c

Purpose: exposes a minimal simulated MACsec offload implementation for netdevsim, tracking SecY and RXSC objects and validating callback ordering.

Important APIs/types/functions: `nsim_macsec_init()` installs `macsec_ops` and advertises `NETIF_F_HW_MACSEC`. The callback table covers add/update/delete for SecY, RXSC, RXSA, and TXSA. Helpers `nsim_macsec_find_secy()` and `nsim_macsec_find_rxsc()` locate tracked SCI entries.

Control flow: SecY add checks capacity, finds a free entry, stores SCI, resets RXSC count, and increments global count. SecY update/delete require a matching SCI; delete clears the entry and count. RXSC add/update/delete first locate the parent SecY, then manage the per-SecY RXSC table. RXSA/TXSA operations mostly validate that the related SecY/RXSC exists and log debug messages.

State and persistence: `struct nsim_macsec` holds three SecY slots and one RXSC per SecY. It stores SCI and used/count flags only; SA key material and packet transforms are not simulated. State is reset at init and volatile.

Dependencies and integration: depends on `net/macsec.h`, netdev MACsec offload hooks, and netdev feature flags. Called from `netdev.c` PF device initialization and teardown.

Risks: it is intentionally shallow and validates object relationships rather than performing MACsec. Capacity constants are small, so tests must expect `-ENOSPC`. Teardown is empty, relying on MACsec core to have deleted offloaded objects before device destruction.

Test signals: create more than three SecYs or more than one RXSC, update/delete nonexistent SCI values, exercise RXSA/TXSA callbacks without parent objects, and confirm feature exposure after device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdev.c

Purpose: implements the core simulated Ethernet net_device for netdevsim, including PF/VF netdev ops, peer forwarding, NAPI queues, page pools, XDP/BPF hooks, VLAN tracking, queue reset testing, and module registration.

Important APIs/types/functions: `nsim_create()`/`nsim_destroy()` allocate and free devices. `nsim_start_xmit()` forwards packets to a peer or loopback path after IPsec/PSP checks. `nsim_open()`/`nsim_stop()` manage NAPI and carrier. `nsim_queue_*` functions implement receive queue allocation and queue-management restart scenarios. Netdev ops include VF configuration, MTU, TC/BPF, VLAN add/kill, stats, and shaper stubs.

Control flow: PF initialization creates a mock PHC, UDP tunnel info, receive queues, BPF/MACsec/IPsec hooks, registers the netdevice, initializes PSP, and optional debug notifier. Transmit selects loopback or RCU peer, validates PSP/IPsec, maps skb to a receive queue, linearizes when configured HDS disallows nonlinear data, timestamps, queues to peer NAPI, starts a short hrtimer, and updates stats. NAPI drains queued skbs, optionally runs generic XDP, GRO-receives, and wakes peer tx queues. Destroy disconnects peers, unregisters, tears down feature modules, frees queues, validates VLAN cleanup, releases held page-pool page, and frees netdev.

State and persistence: `struct netdevsim` stores peer RCU pointer, queues, feature substructures, VF config references, VLAN bitmaps, debugfs dentries, page-pool hold state, and counters. All state is volatile per simulated device.

Dependencies and integration: integrates with net core, RTNL/netdev locking, NAPI, page_pool, XDP, BPF, TC, UDP tunnel offload, MACsec, IPsec, PSP, ethtool, devlink port assignment, debugfs, and rtnl link registration under kind `netdevsim`.

Risks: peer forwarding relies on RCU and queue count compatibility; queue-reset debugfs intentionally exercises unusual NAPI add/delete ordering. Page-pool hold/debug paths require running device state. Feature teardown ordering is important because several modules store netdev pointers or debugfs entries.

Test signals: create PF/VF ports, connect peers, run loopback and peer traffic, attach XDP/BPF, exercise queue reset modes 0-3, hold/release page-pool pages, add/remove VLAN filters, change MTU under XDP constraints, configure VFs, and verify destroy warnings for leaked VLANs/pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdevsim.h -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdevsim.h

Purpose: central internal header for netdevsim, defining shared constants, private structures, feature state, resource IDs, and cross-file function prototypes.

Important APIs/types/functions: defines `struct netdevsim`, `struct nsim_dev`, `struct nsim_dev_port`, `struct nsim_bus_dev`, IPsec/MACsec/VLAN/ethtool/queue structs, devlink resource enums, and prototypes for device, bus, FIB, BPF, health, hwstats, psample, UDP tunnel, IPsec, MACsec, PSP, and TC integration. It also provides config-dependent inline stubs for optional features.

Control flow: the header does not execute logic directly, but it defines object ownership and module boundaries. `struct nsim_dev` represents the simulated devlink/bus device; `struct nsim_dev_port` binds devlink ports to netdevs; `struct netdevsim` is per-netdev private state; optional feature helpers compile to no-ops when dependencies are disabled.

State and persistence: declares volatile in-kernel state: BPF maps/program lists, devlink health/hwstats, FIB and trap data, UDP port arrays, VF configs, peer RCU pointers, PSP stats, IPsec/MACsec tables, VLAN bitmaps, and debugfs dentries. No persistent format is defined.

Dependencies and integration: includes kernel network headers for devlink, ethtool, UDP tunnels, XDP, MACsec, PTP mock, debugfs, netdevice, and list/bitmap support. It is the contract tying `netdev.c`, `fib.c`, feature modules, and bus/devlink files together.

Risks: this header has broad reach; layout or field ownership changes can affect many modules. Optional stub behavior must match real feature error semantics, such as IPsec tx returning true when XFRM offload is disabled and BPF hooks returning `-EOPNOTSUPP`.

Test signals: build coverage across configs with and without `CONFIG_BPF_SYSCALL`, `CONFIG_XFRM_OFFLOAD`, `CONFIG_MACSEC`, `CONFIG_INET_PSP`, and `CONFIG_PSAMPLE`; compile-time coverage catches prototype/field drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdevsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/psample.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/psample.c

Purpose: generates synthetic psample packets and metadata from netdevsim through a debugfs-controlled delayed-work producer.

Important APIs/types/functions: `struct nsim_dev_psample` stores work, psample group, sampling parameters, metadata fields, and active state. `nsim_dev_psample_init()` creates debugfs controls. `nsim_dev_psample_enable()`/`disable()` start and stop reporting. `nsim_dev_psample_report_work()` builds and emits sample packets.

Control flow: init allocates state, initializes delayed work, creates `psample` debugfs directory, and exposes rate, group number, truncation size, in/out ifindex, output traffic class, occupancy max, latency max, and enable. Enabling obtains a psample group in the devlink netns and schedules work. Each work tick builds a fake Ethernet/IPv4/UDP skb with random L4 ports, fills metadata, calls `psample_sample_packet()`, consumes the skb, and reschedules after 100 ms.

State and persistence: debugfs values control volatile reporting behavior. Active state holds a psample group reference until disable or exit. Randomized metadata is not persisted.

Dependencies and integration: depends on `CONFIG_PSAMPLE`, devlink netns lookup, psample group APIs, debugfs, delayed work, random helpers, and IP/UDP header construction.

Risks: `out_tc_occ_max` and `latency_max` are used in bitmask expressions assuming useful power-of-two-like ranges; zero disables each field. Enable returns `-EBUSY` if already active and `-EINVAL` if the group cannot be acquired. Exit must cancel work before putting the group.

Test signals: toggle enable, observe psample netlink packets, change metadata debugfs fields, validate busy/invalid paths, and unload while active to ensure delayed work and group references are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/psample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/psp.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/psp.c

Purpose: simulates PSP device support for netdevsim, including association registration, fake encapsulation/receive handling, stats, and debugfs re-registration.

Important APIs/types/functions: `nsim_psp_init()` creates a `psp_dev` and debugfs `psp_rereg`; `nsim_do_psp()` handles transmit-side PSP encapsulation and simulated peer receive; `nsim_psp_handle_ext()` restores PSP skb extensions after forwarding; `nsim_psp_uninit()` unregisters the PSP device. `nsim_psp_ops` implements config, SPI allocation, key add/delete, key rotate, and stats.

Control flow: transmit retrieves an skb PSP association, verifies it belongs to the sending netdevsim, encapsulates the packet, then either simulates peer PSP receive and marks the skb decrypted or leaves UDP/PSP headers in place with a repaired UDP checksum. SPI allocation increments per-device SPI state and encodes generation into the returned key. Association add stores driver private data and increments a counter; delete clears it. Debugfs reregister unregisters and creates a new PSP device under a mutex.

State and persistence: `netdevsim.psp` stores RCU PSP device pointer, stats with `u64_stats_sync`, debugfs dentry, re-registration mutex, SPI counter, and association count. It is volatile.

Dependencies and integration: depends on `CONFIG_INET_PSP`, PSP core APIs, skb extensions, checksum helpers, RCU, debugfs, and netdevsim forwarding in `netdev.c`.

Risks: driver-private association pointer checks are central to preventing another simulated device from using the key. Stats updates happen in the transmit path and must use sync protection. Re-registration must avoid UAF by clearing the RCU pointer, synchronizing, and unregistering.

Test signals: configure PSP associations, transmit to peers with/without PSP capability, verify decapsulation and UDP checksum fallback, read PSP stats, exercise `psp_rereg`, and ensure association leak warnings fire during uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/tc.c

Purpose: supplies netdevsim's `ndo_setup_tc` handling for selected qdiscs and clsact/block offload tests.

Important APIs/types/functions: `nsim_setup_tc()` dispatches TC setup types. `nsim_setup_tc_taprio()` handles TAPRIO replace/destroy/stats. `nsim_setup_tc_ets()` handles ETS replace/destroy/stats. `nsim_setup_tc_block_cb()` forwards flow-block callbacks into the BPF offload helper. A global `nsim_block_cb_list` tracks simple block callbacks.

Control flow: TAPRIO and ETS accept replace/destroy commands as no-ops and return synthetic zero stats for stats requests. Block setup calls `flow_block_cb_setup_simple()` with the netdevsim private pointer as callback state. Unsupported setup types return `-EOPNOTSUPP`.

State and persistence: the only state in this file is the global block callback list. Qdisc settings themselves are not persisted in netdevsim.

Dependencies and integration: integrates with packet scheduler/qdisc APIs, flow block setup, BPF TC offload hooks from `netdevsim.h`, and `netdev.c` net_device ops.

Risks: it is a test stub, so successful replace does not imply real scheduling behavior. Block callback lifetime relies on `flow_block_cb_setup_simple()` bookkeeping. Stats are intentionally zeroed, which tests must treat as simulated output.

Test signals: attach/destroy TAPRIO and ETS qdiscs, query stats, attach TC flower/BPF blocks, disable `NETIF_F_HW_TC`, and verify unsupported setup types fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/udp_tunnels.c -->
# sources/distributed-fs/ceph-client/drivers/net/netdevsim/udp_tunnels.c

Purpose: simulates UDP tunnel port offload tables for netdevsim and exposes debugfs knobs for reset, injected errors, and device-level mode flags.

Important APIs/types/functions: `nsim_udp_tunnel_info` defines two tables: VXLAN and Geneve/VXLAN-GPE. `nsim_udp_tunnel_set_port()`, `unset_port()`, and `sync_table()` update simulated table arrays. `nsim_udp_tunnels_info_create()` allocates per-device info and debugfs entries; `destroy()` frees them; `nsim_udp_tunnels_debugfs_create()` exposes global mode toggles.

Control flow: create rejects incompatible shared+open_only, selects per-netdev or shared arrays, creates debugfs arrays for both tables, installs reset and `inject_error`, duplicates the static info, then adapts callbacks and flags for sync-all, open-only, IPv4-only, shared, and static IANA VXLAN modes. Set/unset consume one injected error then update packed `(port,type)` entries. Reset clears arrays and notifies the UDP tunnel core.

State and persistence: table values are volatile `u32` arrays either per `netdevsim` or shared in `nsim_dev`. Debugfs toggles are mutable runtime state and affect subsequently created devices.

Dependencies and integration: uses `udp_tunnel_nic_info`, netdev `udp_tunnel_nic_info`, debugfs u32 arrays, and netdevsim device/port structures.

Risks: dynamically duplicating what normal drivers keep static is intentional for testing but requires explicit kfree. Shared mode couples multiple devices to the same arrays. Error injection is one-shot and negates the stored value into a return code.

Test signals: add/delete tunnel ports, force errors, reset registered devices, validate table debugfs contents, create devices with sync_all/open_only/ipv4_only/shared/static_iana_vxlan modes, and reject shared+open_only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netdevsim/udp_tunnels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netkit.c -->
# sources/distributed-fs/ceph-client/drivers/net/netkit.c

Purpose: implements the `netkit` rtnl link type, a BPF-programmable virtual network device that can run as a paired device or single device and supports BPF multi-program attachment, queue leasing, XSK delegation, and peer forwarding.

Important APIs/types/functions: `struct netkit` stores peer RCU pointer, active BPF multi-program entry, policy, scrub mode, bundle, mode, pairing, primary flag, and headroom. `netkit_xmit()` is the fast path. `netkit_new_link()`, `netkit_del_link()`, `netkit_change_link()`, and `netkit_fill_info()` implement rtnl behavior. `netkit_prog_attach()`, `netkit_prog_detach()`, `netkit_prog_query()`, and `netkit_link_attach()` expose BPF attach/link APIs.

Control flow: transmit validates peer/up state, prepares skb for cross-netns forwarding, sets peer packet type/device, runs attached BPF programs until PASS/DROP/REDIRECT/NEXT, then injects into peer with `__netif_rx()`, redirects, or drops with stats. Newlink parses mode, pairing, policies, scrub, peer info, headroom/tailroom, creates/registers a peer when paired, initializes bundles, sets carrier, and links peers by RCU. BPF attach/detach/update operates under RTNL, updates active entries with RCU synchronization, and commits multi-program changes. Uninit releases all programs/links and unleases queues.

State and persistence: all state is netdev private and volatile. BPF programs are refcounted or held through `bpf_link`; active entry pointers are RCU-protected. Queue leases are stored in netdev RX queue lease pointers.

Dependencies and integration: uses rtnl link ops, BPF mprog/link APIs, TCX action compatibility, netdev queue leasing, XDP socket delegation, netdevice notifier for physical-device unregister, netfilter egress skip, and standard netdev stats/features.

Risks: peer lifetime, unregister batching, and queue leases require careful RTNL/RCU ordering. Only primary paired devices can be management targets for BPF APIs. Single mode disallows peer-specific attributes and enables XSK support differently. BPF return codes must stay ABI-compatible with TCX.

Test signals: create paired and single devices, attach multiple BPF programs and links with replace/relative/revision flags, update/detach links, change policies, forward/drop/redirect traffic, lease queues to physical devices, test XSK setup/wakeup, unregister leased physical devices, and dump rtnl attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/netkit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/nlmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/nlmon.c

Purpose: implements the `nlmon` virtual netdevice used to monitor netlink traffic through the netlink tap infrastructure.

Important APIs/types/functions: `struct nlmon` wraps `struct netlink_tap`. `nlmon_open()` registers the tap with `netlink_add_tap()`, `nlmon_close()` removes it, `nlmon_xmit()` accounts and frees transmitted skbs, and `nlmon_setup()` configures netdev type, features, stats, MTU bounds, and ops.

Control flow: module init registers rtnl link kind `nlmon`. Creating a device calls setup. Opening stores the netdev and module in the tap and adds it to netlink. Closing removes it. Captured/tapped packets are delivered through the netdev infrastructure, while explicit transmit on the device only updates length stats and drops the skb. Module exit unregisters the rtnl link ops.

State and persistence: per-device state is only the tap object in netdev private memory and per-CPU lstats. No persistent state exists.

Dependencies and integration: integrates with `netlink_add_tap()`/`netlink_remove_tap()`, rtnl link ops, ethtool link reporting, ARPHRD_NETLINK, and netdevice stats.

Risks: address assignment is rejected because the device is not Ethernet. The MTU is a soft netlink-message size default, not a hardware constraint. The tap must be removed on close to avoid stale module/netdev references.

Test signals: create `nlmon`, bring it up/down, observe netlink traffic with packet capture, verify `IFLA_ADDRESS` validation fails, check stats after traffic, and unload while devices are closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/nlmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ntb_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ntb_netdev.c

Purpose: provides an Ethernet netdevice over PCIe Non-Transparent Bridge transport queue pairs, exposing NTB links as network interfaces.

Important APIs/types/functions: `struct ntb_netdev` owns the pci/client device, netdev, queue count, and queue array. `struct ntb_netdev_queue` stores a transport QP, qid, and tx reaper timer. `ntb_netdev_probe()`/`remove()` manage device lifetime. `ntb_netdev_open()`/`close()`, `ntb_netdev_start_xmit()`, RX/TX handlers, MTU change, and ethtool channel ops implement data path and configuration.

Control flow: probe allocates an Ethernet netdev with up to 64 queues, creates default QPs, sets real queues and MTU from transport max size, registers the netdev, and stores drvdata. Open fills each QP with RX buffers, initializes timers, stops tx, and brings NTB links up. RX handler converts completed buffers into skbs for `netif_rx()` and immediately posts replacements. TX enqueues skb data to the QP and stops/wakes subqueues based on free descriptors, tx timer, and link events. Channel changes create or free QPs and resize real queues, with rollback on failure.

State and persistence: queue/QP pointers, timers, queue count, and netdev stats are volatile. Module parameters `tx_time`, `tx_start`, and `tx_stop` tune queue wake/stop thresholds.

Dependencies and integration: depends on NTB transport client APIs, PCI device metadata, netdev and ethtool ops, timers, and Ethernet helpers. It registers as an NTB transport client in late init.

Risks: RX buffer refill failures can leave the device short of buffers or inoperable after MTU growth failure. TX flow control relies on memory barriers around free-entry checks. Channel resize while running must coordinate subqueue state, QP link state, timers, and queue publication order.

Test signals: probe with NTB transport, open/close links, transmit under descriptor pressure, force link events, change MTU below/above transport max, increase/decrease ethtool combined channels while running, and verify removal frees QPs and timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ntb_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/Makefile

Purpose: declares the kernel build composition for the OpenVPN data channel offload module.

Important APIs/types/functions: `obj-$(CONFIG_OVPN) := ovpn.o` builds the module when enabled. `ovpn-y` lists component objects: bind, crypto, AEAD crypto, main, io, netlink, generated netlink, peer, packet ID, socket, stats, TCP, and UDP.

Control flow: Kbuild links the listed objects into `ovpn.o`; there is no runtime logic in this file. Object ordering makes core pieces and generated netlink code part of the same module image.

State and persistence: no state. It defines build-time module membership only.

Dependencies and integration: integrates the ovpn directory with the kernel `CONFIG_OVPN` option and includes both hand-written and generated sources. The selected files in this work item are only a subset of the module.

Risks: omitting a required object breaks unresolved symbols across the module; adding generated code requires keeping `netlink-gen.*` synchronized with the YAML spec and hand-written netlink handlers.

Test signals: compile with `CONFIG_OVPN=m` and built-in, check all listed objects link into `ovpn.o`, and verify module load resolves init/exit and netlink references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.c

Purpose: implements allocation and replacement of OpenVPN peer transport bindings, which record remote endpoint addresses.

Important APIs/types/functions: `ovpn_bind_from_sockaddr()` allocates an `ovpn_bind` from IPv4 or IPv6 `sockaddr_storage`. `ovpn_bind_reset()` replaces a peer's binding under the peer lock and frees the old binding with RCU.

Control flow: binding creation validates address family, chooses sockaddr length, allocates with `GFP_ATOMIC`, copies the remote address, and returns either a pointer or `ERR_PTR`. Reset asserts the caller holds `peer->lock`, uses `rcu_replace_pointer()` to publish the new binding, and schedules the old object through `kfree_rcu()`.

State and persistence: a binding stores remote sockaddr, local IP union fields populated elsewhere, and an RCU head. It is volatile per peer.

Dependencies and integration: depends on `ovpn_peer`, RCU pointer discipline, socket address types, and the receive-side matching helpers in `bind.h`.

Risks: only AF_INET and AF_INET6 are accepted. Allocation uses atomic context, so callers must handle `-ENOMEM`. Reset must be called under the correct peer lock; otherwise RCU replacement lockdep assumptions are invalid.

Test signals: create IPv4 and IPv6 bindings, reject unsupported families, replace peer binding under lock, verify old binding is safe for RCU readers, and run endpoint-floating tests that reset bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.h

Purpose: defines ovpn binding data structures and inline packet-source matching for peer remote endpoints.

Important APIs/types/functions: `union ovpn_sockaddr` wraps IPv4/IPv6 sockaddr forms. `struct ovpn_bind` stores remote sockaddr, local IPv4/IPv6 endpoint, and RCU cleanup head. `ovpn_bind_skb_src_match()` compares an skb's source IP and UDP source port against the binding remote address. It also declares bind allocation/reset functions.

Control flow: the inline matcher rejects null bindings, branches on `skb->protocol`, verifies the stored family, compares IPv4 or IPv6 source address, then compares UDP source port. Non-IP protocols fail.

State and persistence: the header defines per-peer volatile binding state. RCU cleanup is part of the structure contract.

Dependencies and integration: uses IP, IPv6, UDP, skb, spinlock, and RCU headers. It is used by peer receive and endpoint lookup logic to validate packet source addresses.

Risks: matcher assumes UDP header access is valid for the skb shape provided by callers. It matches only remote endpoint, not local endpoint. Any protocol other than IPv4/IPv6 UDP fails.

Test signals: feed IPv4/IPv6 UDP skbs with matching and mismatching source address/port, null bind, wrong family, and non-IP protocol cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/bind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.c

Purpose: manages OpenVPN per-peer crypto key-slot state, including primary/secondary slot reset, deletion, swapping, lookup, config reporting, and RCU-safe destruction.

Important APIs/types/functions: `ovpn_crypto_state_reset()` installs a new AEAD key slot. `ovpn_crypto_key_slot_delete()`, `ovpn_crypto_kill_key()`, and `ovpn_crypto_key_slots_swap()` mutate slot state. `ovpn_crypto_config_get()` reports non-secret config. `ovpn_crypto_state_release()` drops both slots during peer release. `ovpn_crypto_key_slot_release()` defers slot destruction through RCU.

Control flow: reset validates slot selector, creates a key slot through `ovpn_aead_crypto_key_slot_new()`, replaces the selected primary or secondary RCU pointer under spinlock, then puts the old slot. Delete and kill similarly replace matching slots with NULL and put old refs. Swap flips `primary_idx` under lock rather than moving pointers. Config get maps logical primary/secondary to physical index, dereferences under RCU, and reports cipher/key id.

State and persistence: `struct ovpn_crypto_state` contains two RCU slot pointers, a primary index, and a spinlock. Key slots are kref-counted and RCU-freed. State is volatile and owned by a peer.

Dependencies and integration: relies on AEAD slot creation/destruction in `crypto_aead.c`, packet ID state in slots, UAPI key slot/cipher enums, spinlocks, krefs, and RCU.

Risks: `ovpn_crypto_kill_key()` dereferences slot pointers before checking for NULL, so callers should ensure slots exist or this path may be fragile. Slot swap does not validate that a secondary key exists. Readers must hold refs via helper functions before async crypto use.

Test signals: install primary/secondary keys, delete each slot, swap slots, kill by key id, query missing and present configs, run concurrent encrypt/decrypt lookups under RCU, and release peers with active slot references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.h

Purpose: declares ovpn crypto configuration and runtime key-slot structures plus inline helpers for RCU/kref-safe slot lookup.

Important APIs/types/functions: `struct ovpn_key_direction`, `ovpn_key_config`, and `ovpn_peer_key_reset` carry netlink-provided key settings. `struct ovpn_crypto_key_slot` stores AEAD transforms, nonce tails, packet ID send/receive state, refcount, and RCU head. `struct ovpn_crypto_state` stores two slots and primary index. Inline helpers initialize state, hold/put slots, find by key id, and get the primary slot.

Control flow: `ovpn_crypto_key_id_to_slot()` reads primary then secondary under RCU, validates key id, and kref-holds the slot unless its refcount is already zero. `ovpn_crypto_key_slot_primary()` fetches the current primary similarly. Mutation APIs are declared for `crypto.c`.

State and persistence: all state is per peer and volatile. Packet ID state is cacheline-aligned to reduce contention between transmit and receive.

Dependencies and integration: includes packet ID and protocol definitions, kernel kref/RCU patterns, crypto AEAD handles, and UAPI ovpn enums.

Risks: callers must put held slots. The primary index and slot pointers are read locklessly under RCU; writers must use the spinlock and RCU replacement helpers. Key material pointers in config are input views, not owned by this header.

Test signals: build with lockdep/RCU diagnostics, exercise slot lookup under concurrent reset/delete/swap, ensure missing key ids return NULL, and check reference balancing through async crypto completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.c

Purpose: implements OpenVPN AEAD encryption/decryption for data channel packets and creates/destroys AEAD-backed crypto key slots.

Important APIs/types/functions: `ovpn_aead_encrypt()` encapsulates and encrypts skb payloads. `ovpn_aead_decrypt()` authenticates and decrypts received packets. `ovpn_aead_crypto_key_slot_new()` allocates transforms and initializes nonce/packet-id state. `ovpn_aead_crypto_key_slot_destroy()` frees transforms. Helpers compute temporary buffer layout for IV, request, and scatterlist.

Control flow: encryption ensures headroom and writable skb data, allocates an atomic temporary crypto buffer, maps payload into scatterlist, reserves auth tag, obtains next packet ID, builds nonce from packet ID and transmit nonce tail, prepends wire nonce and DATA_V2 opcode, sets AAD, and submits `crypto_aead_encrypt()` with `ovpn_encrypt_post` callback. Decryption validates packet length, pulls AAD/tag, maps payload and tag, reconstructs IV from wire nonce plus receive nonce tail, sets AAD, and submits decrypt with `ovpn_decrypt_post`.

State and persistence: key slots hold encrypt/decrypt `crypto_aead` transforms, nonce tails, key id, packet ID xmit/recv replay state, refcount, and RCU head. Per-packet temporary buffers are recorded in skb control block and freed by post callbacks.

Dependencies and integration: uses Linux crypto AEAD API, skbuff scatterlist helpers, ovpn protocol constants, packet ID helpers, peer state, and async completion functions in `io.c`. Supported algorithms are AES-GCM and ChaCha20-Poly1305.

Risks: error paths after temporary allocation must be paired with post-callback cleanup; early returns from mapping or packet-id errors leave cleanup responsibility delicate. Nonce exhaustion returns `-ERANGE` and higher layers kill the key. AEAD IV size is assumed to be 12 bytes.

Test signals: encrypt/decrypt valid packets with both algorithms, reject unsupported ciphers or nonce sizes, test fragmented/nonlinear skbs, force packet ID exhaustion, authentication failure, short packets, async completion, and key-slot destroy after in-flight refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.h

Purpose: declares the AEAD crypto operations used by ovpn transmit/receive and crypto state management.

Important APIs/types/functions: exports `ovpn_aead_encrypt()`, `ovpn_aead_decrypt()`, `ovpn_aead_crypto_key_slot_new()`, `ovpn_aead_crypto_key_slot_destroy()`, and `ovpn_aead_crypto_alg()`.

Control flow: this header has no runtime logic; it defines the interface between generic key-slot management in `crypto.c`, packet I/O in `io.c`, and AEAD implementation in `crypto_aead.c`.

State and persistence: no direct state; all state is passed through `struct ovpn_peer`, `struct ovpn_crypto_key_slot`, and `struct sk_buff`.

Dependencies and integration: includes `crypto.h`, kernel integer types, and skbuff declarations. It is a narrow boundary around the AEAD implementation.

Risks: prototypes expose async crypto semantics through callbacks hidden in `crypto_aead.c`; callers must set up skb control block expectations and hold peer/key references as done in `io.c`.

Test signals: compile interface users, verify encrypt/decrypt callers link, and run key-slot creation/destruction coverage for supported and unsupported algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/crypto_aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/io.c

Purpose: implements ovpn packet I/O: netdev transmit, peer receive, AEAD completion handling, keepalive detection/sending, GSO segmentation, peer selection, stats, and transport handoff.

Important APIs/types/functions: `ovpn_net_xmit()` is the net_device transmit entry. `ovpn_recv()` starts decrypt for received transport packets. `ovpn_encrypt_post()` and `ovpn_decrypt_post()` complete async crypto. `ovpn_xmit_special()` sends keepalive or other out-of-band payloads. `ovpn_netdev_write()` injects decrypted IP packets into the ovpn interface.

Control flow: transmit resets conntrack, validates IP protocol, finds the peer by destination, drops dst, segments GSO skbs, share-checks each segment, updates VPN tx stats, then encrypts each segment with the peer primary key. Encrypt completion frees crypto temp data, handles nonce exhaustion by killing the key and notifying userspace, sends encrypted skb via UDP or TCP socket, updates link tx stats and `last_sent`, and drops on failure. Receive records link rx stats, selects a key by packet key id, starts AEAD decrypt, validates replay packet ID in completion, updates endpoints for UDP floating, strips ovpn header/tag, detects keepalive/null packets, validates encapsulated IP and RPF, then injects into GRO cells and updates VPN/device rx stats.

State and persistence: uses peer crypto, stats, last send/receive timestamps, skb control block crypto temp/peer/key references, and ovpn GRO cells. State is volatile.

Dependencies and integration: integrates with ovpn peer lookup, bind endpoint updates, AEAD crypto, packet ID replay, TCP/UDP transport senders, generic segmentation, GRO cells, device dstats, netfilter conntrack reset, and netlink key-swap notification.

Risks: async crypto makes reference balancing crucial: peer and key refs are released in completion callbacks. Early decrypt/encrypt failures must free temp buffers only when allocated. RPF and keepalive classification happen after successful authentication. GSO segmentation errors and share-check failures must avoid double-freeing skb lists.

Test signals: send IPv4/IPv6 payloads in P2P and MP modes, no-peer drops, GSO segmentation, key-missing receive, replay rejection, keepalive receive, endpoint floating, RPF drops, TCP/UDP transport send, nonce exhaustion key kill notification, and async crypto completion cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/io.h

Purpose: defines ovpn I/O constants and function prototypes shared by the netdev, crypto, peer, and transport paths.

Important APIs/types/functions: `OVPN_HEAD_ROOM` computes required encapsulation headroom for DATA_V2 AEAD plus UDP/TCP and IPv4/IPv6 headers. `OVPN_MAX_PADDING`, `OVPN_KEEPALIVE_SIZE`, `ovpn_keepalive_message`, `ovpn_net_xmit()`, `ovpn_recv()`, `ovpn_xmit_special()`, `ovpn_encrypt_post()`, and `ovpn_decrypt_post()` form the public I/O interface.

Control flow: no runtime logic in the header; it establishes sizing assumptions used by netdev setup and AEAD skb headroom checks.

State and persistence: no state, except declaration of the keepalive byte sequence defined in `io.c`.

Dependencies and integration: depends on ovpn protocol constants and transport header sizes. Used by `main.c` to set MTU/headroom/tailroom and by `crypto_aead.c` for encryption headroom.

Risks: if OpenVPN header/tag sizes or transport assumptions change, `OVPN_HEAD_ROOM` must stay synchronized or encryption may fail with insufficient headroom. Tailroom and padding constants affect advertised netdev limits.

Test signals: compile-time users, MTU/headroom validation, encryption on skbs near headroom limits, and keepalive-size consistency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/main.c

Purpose: registers and configures the `ovpn` rtnl link type and module lifecycle for OpenVPN data channel offload.

Important APIs/types/functions: `ovpn_setup()` initializes netdev properties. `ovpn_newlink()` sets mode, initializes private state, keepalive work, carrier, and registers the device. `ovpn_dellink()` cancels keepalive work and frees peers. `ovpn_net_init()`/`uninit()` manage GRO cells and MP peer container allocation. `ovpn_dev_is_valid()` identifies ovpn devices. `ovpn_init()`/`ovpn_cleanup()` handle module registration.

Control flow: module init registers rtnl link ops, registers the ovpn generic netlink family, and initializes TCP support. Device setup configures ARPHRD_NONE, point-to-point/noarp flags, no queue, dst retention, features, MTU bounds adjusted by `OVPN_HEAD_ROOM`, and tailroom. Newlink accepts P2P or MP mode, initializes locks and work, sets MP carrier on or P2P carrier off, then registers the netdev. Delling frees peers with teardown reason before unregistering.

State and persistence: `struct ovpn_priv` stores dev pointer, mode, lock, peer collection pointer, GRO cells, and keepalive work. MP mode allocates hash tables for peer lookups; P2P uses simpler peer state elsewhere. State is volatile.

Dependencies and integration: integrates with rtnl link ops, generic netlink registration, GRO cells, IPv4 redirect sysctl adjustment for MP mode, peer management, TCP/UDP transports, and ethtool.

Risks: MP allocation disables redirects on the interface and globally for the netns, which is intentional but broad. Peer cleanup and delayed keepalive cancellation must precede unregister. `netns_refund = false` affects namespace ref behavior.

Test signals: create P2P and MP ovpn links, inspect rtnl mode fill-info, verify carrier behavior, allocate/free MP peer tables, check MTU/headroom values, register/unregister netlink family, and teardown with active peers/keepalive work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/main.h

Purpose: declares the minimal public device-identification helper for the ovpn module.

Important APIs/types/functions: `ovpn_dev_is_valid()` returns whether a net_device is backed by ovpn netdev ops.

Control flow: header only; implementation lives in `main.c`.

State and persistence: no state.

Dependencies and integration: used by netlink or peer-management code that receives an ifindex/netdev and must reject non-ovpn devices before accessing `struct ovpn_priv`.

Risks: correctness depends on comparing the expected `netdev_ops`; any future alternate ovpn ops table would need this helper updated.

Test signals: call through netlink pre-doit on ovpn and non-ovpn devices, and compile all users against the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.c -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.c

Purpose: generated YNL kernel source for the ovpn generic netlink family: attribute policies, split operation table, multicast groups, and family descriptor.

Important APIs/types/functions: exports nested policy arrays for key config, key direction, peer attributes, and command inputs. `ovpn_nl_ops` maps commands `PEER_NEW`, `PEER_SET`, `PEER_GET` do/dump, `PEER_DEL`, `KEY_NEW`, `KEY_GET`, `KEY_SWAP`, and `KEY_DEL` to hand-written handlers. `ovpn_nl_family` defines family name/version, netns support, parallel ops, ops, and peer multicast group.

Control flow: genetlink core uses the policies to validate incoming attributes, then invokes generated ops entries with `ovpn_nl_pre_doit()`/`post_doit()` around hand-written command handlers where configured. Dump peer get uses a separate dumpit op and policy.

State and persistence: static const policies and a `__ro_after_init` family descriptor. No runtime mutable state except genetlink registration state handled elsewhere.

Dependencies and integration: generated from `Documentation/netlink/specs/ovpn.yaml`; includes UAPI `linux/ovpn.h`, generic netlink, and prototypes from `netlink-gen.h`. It must match hand-written `netlink.c` handlers and UAPI enum values.

Risks: manual edits would be overwritten and can desynchronize from the YAML spec. Attribute range limits, max slot/key id/cipher values, and nested policy bounds are ABI-sensitive. Parallel ops require handlers to perform their own object locking.

Test signals: regenerate from YAML and compare, register family, validate malformed attributes are rejected, exercise all commands, test peer dump, and subscribe to the peers multicast group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.h -->
# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.h

Purpose: generated YNL header declaring ovpn generic netlink policies, command handlers, multicast group indexes, and family object.

Important APIs/types/functions: declares `ovpn_*_nl_policy` arrays, pre/post doit hooks, peer/key command handler prototypes, `OVPN_NLGRP_PEERS`, and `extern struct genl_family ovpn_nl_family`.

Control flow: no runtime logic. It forms the compile-time contract between generated `netlink-gen.c` and hand-written `netlink.c` plus registration code.

State and persistence: no state in the header; it declares generated static data defined in `netlink-gen.c`.

Dependencies and integration: includes generic netlink headers and UAPI `linux/ovpn.h`. The file is generated from `Documentation/netlink/specs/ovpn.yaml` and should not be manually edited.

Risks: prototype or policy declaration drift breaks build or command dispatch. Because this is generated, fixes should be made in the YAML/spec or generator inputs, then regenerated.

Test signals: compile ovpn netlink sources, regenerate and diff, verify all declared handlers are implemented, and load the module to ensure family registration links against the declared `ovpn_nl_family`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.h -->
