# Research Report: subset-b-005217

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_sys.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_sys.c

Purpose: implements the common qeth ccwgroup-device sysfs surface shared by layer 2 and layer 3 qeth disciplines. It exposes adapter identity, state, input-buffer sizing, recovery, layer selection, queueing policy, isolation, hardware trap, switch attributes, and BLKT timing knobs.

Important APIs and functions: `qeth_dev_groups` publishes three attribute groups; show/store handlers use `dev_get_drvdata()` to reach `struct qeth_card`. Key stores are `qeth_dev_portno_store()`, `qeth_dev_prioqing_store()`, `qeth_dev_bufcnt_store()`, `qeth_dev_layer2_store()`, `qeth_dev_isolation_store()`, `qeth_hw_trap_store()`, and `qeth_dev_blkt_store()`. Integration calls include `qeth_resize_buffer_pool()`, `qeth_schedule_recovery()`, `qeth_clone_netdev()`, `qeth_remove_discipline()`, `qeth_setup_discipline()`, `qeth_setadpparms_set_access_ctrl()`, `qeth_query_switch_attributes()`, and `qeth_hw_trap()`.

Control flow: read-only attributes format card fields with `sysfs_emit()`. Most writes parse user text with `kstrto*()` or `sysfs_streq()`, take `conf_mutex` or `discipline_mutex`, validate the card is down when changing structural parameters, then update cached card state or issue a hardware command if reachable. Layer switching clones a fresh netdev, removes the current discipline, frees the old netdev, and installs the requested discipline.

State and persistence: settings live in `struct qeth_card` fields such as `options.layer`, `options.isolation`, `qdio.do_prio_queueing`, `qdio.default_out_queue`, `qdio.in_buf_pool.buf_count`, `info.hwtrap`, and `info.blkt`. These are runtime kernel settings, not disk-persistent configuration; they persist for the live device instance and are replayed by normal qeth setup paths where relevant.

Dependencies and integration: depends on the qeth core model, ccwgroup device sysfs, netdevice flags/carrier state, qdio queue geometry, diag assist, and adapter parameters. It is the common control plane consumed by qeth L2/L3 modules and by userspace tools writing sysfs.

Risks: accepting changes only while down is critical because queue counts, port numbers, layer mode, and BLKT timing affect allocation and hardware setup. Layer switching is high risk because it swaps disciplines and netdev lifetime under `discipline_mutex`. `performance_stats` resets counters without per-counter locking, which is acceptable for statistics but can race with live updates. Hardware trap and isolation writes must keep cached state aligned with hardware command failures.

Test signals: sysfs read/write tests for accepted and rejected values, down-vs-up enforcement, layer switch between L2 and L3, buffer pool resize boundaries, recovery scheduling, isolation on unsupported card types, hw_trap arm/disarm/capture error paths, and switch attribute formatting for no hardware, unknown capabilities, and multiple capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_core_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_ethtool.c

Purpose: provides the qeth `ethtool_ops` implementation for driver information, link settings, queue stats, channel counts, IQD transmit coalescing, timestamp capability, ring parameters, and RX copybreak tuning.

Important APIs and functions: `qeth_ethtool_ops` wires callbacks for stats, strings, channels, coalescing, tunables, and link ksettings. `qeth_stats` descriptors map display names to offsets in `struct qeth_card_stats` and `struct qeth_out_q_stats`. Helpers `qeth_add_stat_data()` and `qeth_add_stat_strings()` build ethtool arrays. Coalescing flows through `__qeth_set_coalesce()`, `qeth_set_coalesce()`, `qeth_get_per_queue_coalesce()`, and `qeth_set_per_queue_coalesce()`.

Control flow: stats count is computed as card stats plus per-output-queue stats. Stats reads copy current u64 values from card and queue structures. Channel changes validate nonzero queue counts, enforce hardware queue limits, reject priority queueing conflicts, and impose IQD minimum/downgrade rules before calling `qeth_set_real_num_tx_queues()`. Link mode reporting builds supported and advertised bitmaps from cached link speed, port, duplex, and link mode.

State and persistence: no standalone persistence. It reads and updates live qeth state: queue coalescing fields, `qeth_priv.rx_copybreak`, wanted TX queue count, link info, and queue statistics. `WRITE_ONCE()` is used for coalescing and copybreak values that can be read concurrently by datapath code.

Dependencies and integration: integrates with Linux ethtool netlink/ioctl paths, qeth qdio output queues, netdev queue configuration, and standard ethtool link-mode helpers. IQD-only features return `-EOPNOTSUPP` on non-IQD devices.

Risks: queue count changes can disrupt flow mapping, especially IQD multicast queue conventions, so downgrades while running are blocked. Coalescing rejects both knobs being zero to avoid disabling all wakeup triggers. Stats use offsets into structures; changes to stats structure type or field width must keep the u64 assumption valid.

Test signals: `ethtool -S` string/count alignment, per-queue stat ordering across queue counts, `ethtool -L` failures for zero/too many queues and priority queueing, IQD coalescing global and per-queue set/get, RX copybreak set/get, and link-mode output for TP/fibre speeds and unknown ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2.h

Purpose: declares the layer 2 qeth discipline interface shared by L2 main code and L2 sysfs code.

Important APIs and types: exports `qeth_l2_attr_groups`, BridgePort operations (`qeth_bridgeport_query_ports()`, `qeth_bridgeport_setrole()`, `qeth_bridgeport_an_set()`), VNIC characteristic operations (`qeth_l2_vnicc_set_state()`, `qeth_l2_vnicc_get_state()`, `qeth_l2_vnicc_set_timeout()`, `qeth_l2_vnicc_get_timeout()`), and `qeth_bridgeport_allowed()`. `struct qeth_mac` is the cached multicast/unicast MAC entry with hash node and disposition flag.

Control flow: the header has no executable control flow beyond `qeth_bridgeport_is_in_use()`, which centralizes the test for active BridgePort role, reflected promiscuous mode, or host notification.

State and persistence: describes L2 runtime state stored in `struct qeth_card`: BridgePort options, VNIC characteristic options, and the `rx_mode_addrs` hash table entries represented by `struct qeth_mac`.

Dependencies and integration: depends on `qeth_core.h` for the core card model, enum definitions, and qeth disposition flags. It is consumed by `qeth_l2_main.c` and `qeth_l2_sys.c`.

Risks: `qeth_bridgeport_is_in_use()` is a policy gate used to enforce mutual exclusion. Any new BridgePort mode must update this helper or sysfs and VNICC can become simultaneously configurable in invalid combinations.

Test signals: compile coverage for L2 sysfs/main users, and behavior tests that enabling role, reflect-promisc, or host notification makes VNICC and learning_sync paths reject conflicting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_main.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_main.c

Purpose: implements the qeth layer 2 discipline: MAC/VLAN registration, TX header construction, rx-mode synchronization, BridgePort control and notifications, switchdev learning_sync support, VNIC characteristics, netdevice setup, online/offline transitions, and IPA control-event consumption.

Important APIs and functions: the exported discipline is `qeth_l2_discipline`. Netdev operations are `qeth_l2_iqd_netdev_ops` and `qeth_l2_osa_netdev_ops`. MAC/VLAN helpers include `qeth_l2_send_setdelmac()`, `qeth_l2_register_dev_addr()`, `qeth_l2_set_mac_address()`, `qeth_l2_vlan_rx_add_vid()`, and `qeth_l2_vlan_rx_kill_vid()`. Bridge/switchdev paths include `qeth_l2_pnso()`, `qeth_l2_dev2br_an_set()`, `qeth_l2_bridge_setlink()`, `qeth_bridgeport_query_ports()`, `qeth_bridgeport_setrole()`, and `qeth_bridgeport_an_set()`. VNICC flows use `qeth_l2_vnicc_query_chars()`, `qeth_l2_vnicc_set_state()`, and `qeth_l2_vnicc_init()`.

Control flow: online setup detects dev-to-bridge support, queries BridgePort commands, registers the device MAC, initializes VNICC, transitions to `CARD_STATE_SOFTSETUP`, enables qeth threads, and registers or reattaches the netdev. TX maps the skb to an output queue, fills an L2 or L2 TSO qeth header, marks VLAN/cast/checksum flags, and delegates to `qeth_xmit()`. Rx mode work snapshots netdev unicast/multicast lists, compares them with the cached hash table, issues add/delete MAC IPA commands, and updates promiscuous mode.

State and persistence: live state is stored in `card->info.dev_addr_is_registered`, `card->rx_mode_addrs`, `card->options.sbp`, `card->options.vnicc`, `card->info.pnso_mode`, qdio queues, and `qeth_priv.brport_features`. Desired VNICC and BridgePort values can be cached while offline and recovered on next online setup; MAC/rx-mode caches are drained offline.

Dependencies and integration: integrates with qeth IPA commands, adapter parameters, CHSC PNSO, switchdev notifiers, bridge port attributes, workqueues, qdio, NAPI, netdevice VLAN and MAC callbacks, and userspace uevents for BridgePort host notifications.

Risks: BridgePort, VNICC, and learning_sync are mutually exclusive and guarded across sysfs/netlink paths; missed checks can produce invalid hardware state. PNSO address notification overflow requires flushing bridge FDB state and re-enabling notifications, with stale workqueue entries called out as a recovery risk. MAC registration errors can leave the netdev unable to validate addresses. Work items hold netdev references for bridge learning updates and must release them on every path.

Test signals: L2 bring-up/offline/recovery, MAC address changes including duplicate/unauthorized errors, VLAN add/delete errors, multicast list churn, promiscuous mode fallback through BridgePort reflect, switchdev learning_sync enable/disable and overflow recovery, BridgePort role and host notification uevents, VNICC set/get/timeout recovery, IQD queue selection, and TSO/checksum/VLAN header inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_sys.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_sys.c

Purpose: exposes L2-only sysfs controls for BridgePort role/state/host notifications/reflected promiscuous mode and VNIC characteristics.

Important APIs and functions: `qeth_l2_attr_groups` publishes a BridgePort group and a `vnicc` group. BridgePort handlers call `qeth_bridgeport_allowed()`, `qeth_bridgeport_query_ports()`, `qeth_bridgeport_setrole()`, and `qeth_bridgeport_an_set()`. VNICC handlers convert attribute names with `qeth_l2_vnicc_sysfs_attr_to_char()` and call `qeth_l2_vnicc_get_state()`, `qeth_l2_vnicc_set_state()`, `qeth_l2_vnicc_get_timeout()`, and `qeth_l2_vnicc_set_timeout()`.

Control flow: BridgePort stores parse string or boolean values, lock `conf_mutex` and `sbp_lock`, reject conflicts with VNICC or learning_sync, optionally issue hardware commands if reachable, and otherwise cache desired settings. VNICC stores parse booleans or timeout values under `conf_mutex` and delegate policy and hardware checks to L2 main code.

State and persistence: sysfs stores update `card->options.sbp` and `card->options.vnicc`. Offline writes are cached in memory and applied by L2 online recovery where supported. There is no disk persistence.

Dependencies and integration: depends on L2 main exported functions, qeth card locks, sysfs device attributes, BridgePort hardware support, and VNICC IPA support. User-visible strings such as `n/a (VNIC characteristics)` and `n/a (BridgePort)` encode mutual exclusion state.

Risks: locking order (`conf_mutex` then `sbp_lock`) must stay consistent with notification work. Reflect-promisc deliberately forbids direct role manipulation once active. Attribute-name-to-character mapping returns zero for unknown names, so adding attributes requires updating the mapper.

Test signals: sysfs role/state read formatting, role write while offline and online, hostnotification uevents, reflect-promisc conflict with explicit role, VNICC attributes returning `n/a` on unsupported or BridgePort-active devices, timeout set/get, and invalid input handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l2_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3.h

Purpose: declares the layer 3 qeth address model and L3 sysfs/main cross-file interfaces.

Important APIs and types: `enum qeth_ip_types` distinguishes normal IPs, VIPA, and RXIP. `struct qeth_ipaddr` represents IPv4/IPv6 addresses, multicast flag, disposition flag, IP takeover status, reference count, masks/prefix lengths, and hash linkage. `struct qeth_ipato_entry` stores takeover prefix entries. Inline helpers initialize, compare, and hash addresses. Exports include routing setters, IPATO add/delete/update, HSUID modification, and RXIP/VIPA modification.

Control flow: inline matching separates by-IP matching from full matching. Full matching requires equal type and mask/prefix and is used after locating an address by hash. The hash chooses IPv4 or IPv6 hash helpers by protocol.

State and persistence: describes runtime address state in `card->ip_htable`, multicast state in `card->rx_mode_addrs`, and takeover entries in `card->ipato.entries`. Refcounts allow duplicate normal-address notifier events without duplicate hardware registrations.

Dependencies and integration: depends on `qeth_core.h`, Linux hashtables, IPv6 helpers, and L3 main/sysfs users. It is the shared contract for inet notifier, sysfs VIPA/RXIP/IPATO, and online recovery paths.

Risks: comparing only by IP for lookup means full-match validation is mandatory before deleting or coalescing normal addresses with different masks. Any new address type must preserve takeover and refcount semantics.

Test signals: unit-style checks for IPv4/IPv6 hash/match behavior, duplicate normal address refcounts, VIPA/RXIP duplicate rejection, and IPATO prefix matching against masks and inversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_main.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_main.c

Purpose: implements qeth layer 3 networking: IP address registration, IP takeover, routing assists, multicast synchronization, ARP private ioctls, sniffer/diagnostic trace integration, L3 transmit header construction, netdevice setup, online/offline transitions, and IPv4/IPv6 address notifiers.

Important APIs and functions: exported discipline is `qeth_l3_discipline`. Address management centers on `qeth_l3_add_ip()`, `qeth_l3_delete_ip()`, `qeth_l3_modify_ip()`, `qeth_l3_register_addr_entry()`, and `qeth_l3_deregister_addr_entry()`. Routing uses `qeth_l3_setrouting_v4()` and `qeth_l3_setrouting_v6()`. IPATO uses `qeth_l3_update_ipato()`, `qeth_l3_add_ipato_entry()`, and `qeth_l3_del_ipato_entry()`. TX uses `qeth_l3_hard_start_xmit()`, `qeth_l3_xmit()`, and `qeth_l3_fill_header()`. Notifier entry points are `qeth_l3_ip_event()` and `qeth_l3_ip6_event()`.

Control flow: adding an address looks up by hash/IP, refcounts duplicate normal addresses, rejects conflicting masks/types, marks takeover if covered by IPATO, caches offline addresses with `QETH_DISP_ADDR_ADD`, or issues IPA set-IP commands online. Online setup starts adapter assists, routing, qeth threads, recovers cached IPs, then registers or reattaches the netdev. Multicast rx-mode work rebuilds desired multicast addresses from IPv4/IPv6 device lists and VLANs, then sends set/delete multicast IPA commands based on disposition flags.

State and persistence: address state is runtime in `card->ip_htable`, `card->rx_mode_addrs`, `card->ipato`, and route/sniffer/HSUID options. Offline/recovery keeps address objects with `disp_flag` to replay after hardware returns. IPv6 notifier work is queued to `card->cmd_wq` to avoid doing heavier modifications directly in notifier context.

Dependencies and integration: depends on qeth core IPA helpers, qdio/NAPI, Linux inet and inet6 address notifiers, VLAN iteration, ARP private ioctl ABI, Fibre/IUCV protocol constants for IQD special cases, and diag assist for HiperSockets traffic analyzer mode.

Risks: user-visible IP state must stay coherent across notifier callbacks, sysfs VIPA/RXIP changes, offline transitions, and recovery. ARP query copies variable hardware records into a user buffer and must preserve bounds and protocol matching. L3 TX rewrites skb headroom for IPv4/IQD and fixes checksum/GSO fields; incorrect headroom or protocol handling can corrupt packets. Sniffer and CQ modes are mutually constrained by sysfs.

Test signals: IPv4/IPv6 address add/delete notifier flows including duplicate refcounts, offline recovery replay, IPATO enable/invert/prefix matching, VIPA/RXIP add/delete, multicast list changes and VLAN multicast, ARP ioctl query/add/remove/flush/set-count including permission and buffer-size failures, L3 TX for IPv4/IPv6/AF_IUCV/VLAN/GSO/checksum, IQD sniffer drops, and online/offline with carrier states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_sys.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_sys.c

Purpose: exposes L3-specific sysfs controls for routing mode, HiperSockets sniffer mode, HSUID, IP address takeover prefixes, VIPA addresses, and RXIP takeover addresses.

Important APIs and functions: `qeth_l3_attr_groups` publishes base L3, `ipa_takeover`, `vipa`, and `rxip` groups. Route handlers call `qeth_l3_setrouting_v4()` and `qeth_l3_setrouting_v6()`. IPATO handlers parse `addr/mask` with `qeth_l3_parse_ipatoe()` and call add/delete/update helpers. VIPA/RXIP handlers parse addresses and call `qeth_l3_modify_rxip_vipa()`. HSUID calls `qeth_configure_cq()` and `qeth_l3_modify_hsuid()`.

Control flow: route stores parse symbolic router/connector values, update cached route type under `conf_mutex`, and issue hardware routing updates if reachable, rolling back on failure. Sniffer and HSUID require IQD and down state. IPATO enable requires down state, while invert and prefix updates take `ip_lock` and recompute takeover flags. VIPA/RXIP stores directly modify the L3 address table through main-code helpers.

State and persistence: writes update runtime `card->options.route4/route6`, `card->options.sniffer`, `card->options.hsuid`, `card->ipato`, and address tables. Offline settings remain in memory until device removal. HSUID is converted to EBCDIC for storage and copied to `dev->perm_addr`.

Dependencies and integration: depends on sysfs, qeth L3 main exports, Linux address parsers, EBCDIC conversion, CQ configuration, and qeth card locks. User-visible route strings reflect broadcast echo capability with a `+` suffix.

Risks: `qeth_l3_parse_ipatoe()` temporarily writes a NUL into the sysfs buffer at the slash; callers must pass mutable buffers from sysfs. VIPA accepts multicast unless main/hardware rejects it, while RXIP explicitly rejects multicast. Some IPATO changes can happen while online and only affect cached takeover flags for future hardware operations.

Test signals: route value parsing and rollback, unsupported route modes on IQD vs OSA, sniffer enable when hardware advertises `CHSC_AC2_SNIFFER_AVAILABLE`, HSUID add/delete and CQ transitions, IPATO prefix add/delete/show including duplicate and invalid masks, VIPA/RXIP IPv4/IPv6 add/delete and multicast rejection for RXIP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/qeth_l3_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.c

Purpose: implements the z/VM IUCV special-message core driver. It connects to `*MSG`, receives CP SMSG traffic, dispatches messages by prefix to registered callbacks, and exports callback registration APIs.

Important APIs and functions: exports `smsg_register_callback()` and `smsg_unregister_callback()`. IUCV callbacks are `smsg_path_pending()` and `smsg_message_pending()` in `smsg_handler`. Module lifecycle is `smsg_init()` and `smsg_exit()`.

Control flow: module init requires `machine_is_vm()`, registers an IUCV bus driver and handler, allocates/connects an IUCV path to `*MSG`, then issues `SET SMSG IUCV`. Incoming paths are accepted only from `*MSG`. Incoming messages are received into a DMA-capable buffer, converted from EBCDIC to ASCII, split into sender and payload, trimmed for sender whitespace, and dispatched to the first callback whose prefix matches the payload.

State and persistence: global state consists of `smsg_path` and a spinlock-protected callback list. It is runtime only; module exit disables SMSG delivery with `SET SMSG OFF`, unregisters IUCV, and unregisters the driver.

Dependencies and integration: depends on z/VM, IUCV core, CP command support, EBCDIC conversion, and consumers such as `smsgiucv_app.c`. Exported symbols allow other modules to receive prefixed SMSGs.

Risks: callbacks run while `smsg_list_lock` is held in message context, so callback implementations must be non-blocking and avoid re-entering registration. Only the first prefix match is invoked. Allocation failure rejects the IUCV message. Prefix pointers are not copied, so callers must keep prefix storage valid until unregister.

Test signals: module load outside z/VM returns protocol unsupported, successful path connect issues SMSG mode, callback registration/unregistration ordering, EBCDIC sender trimming, prefix dispatch, receive allocation failure path, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.h

Purpose: provides the small public interface for the SMSGIUCV core driver.

Important APIs and types: defines `SMSGIUCV_DRV_NAME` as the IUCV driver name and declares `smsg_register_callback()` and `smsg_unregister_callback()`. The callback signature receives sender and mutable message text.

Control flow: no executable logic.

State and persistence: consumers depend on the core module retaining callback registrations until explicit unregister or module unload.

Dependencies and integration: included by `smsgiucv.c` and `smsgiucv_app.c`; the driver name is used by the app module to find the core IUCV driver.

Risks: there is no include guard in this header. It is currently simple enough not to matter in existing includes, but repeated inclusion could redeclare prototypes harmlessly and macro identically.

Test signals: compile coverage for core/app modules and symbol linkage for out-of-file callback users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv_app.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv_app.c

Purpose: bridges z/VM CP SMSGs with prefix `APP` into userspace uevents on a synthetic IUCV device, optionally filtering by sender.

Important APIs and functions: module parameter `sender` restricts accepted z/VM user IDs. `smsg_app_callback()` is registered with `smsg_register_callback()`. `smsg_app_event_alloc()` builds uevent environment strings, `smsg_event_work_fn()` emits queued `KOBJ_CHANGE` events, and lifecycle functions allocate/register/unregister the app device.

Control flow: init requires z/VM and the SMSGIUCV core driver, allocates an IUCV device, registers it, uppercases configured sender, and registers the `APP` callback. The callback filters sender, skips the prefix and leading whitespace, ignores empty text, allocates an event, appends it to a spinlock-protected queue, and schedules work. The work function takes a device reference, splices the queue locally, emits each uevent, and frees each event.

State and persistence: global runtime state includes `smsg_app_dev`, `sender`, and the queued event list. Events persist only until the work function emits them. Exit unregisters the callback, cancels work, flushes any queued events by calling the worker, and unregisters the device.

Dependencies and integration: depends on the SMSGIUCV exported API, IUCV bus device allocation, workqueues, kobject uevents, and z/VM environment. Userspace observes `SMSG_SENDER`, `SMSG_ID`, and `SMSG_TEXT`.

Risks: callback allocation uses `GFP_ATOMIC`; under memory pressure messages can be silently dropped. Sender filtering is case-sensitive after the configured value is uppercased, relying on the core sender format. Message text is included in the uevent environment, so length and content can stress userspace consumers. Exit deliberately emits queued events after cancelling work, so teardown can still notify userspace.

Test signals: module load without core driver, sender filter acceptance/rejection, empty message drop, environment formatting, workqueue queue splicing under multiple messages, device reference handling, and exit with pending events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv_app.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/Makefile

Purpose: defines how the s390 zfcp SCSI/FCP driver is built.

Important APIs and functions: `zfcp-objs` lists all object files linked into `zfcp.o`, including the researched `zfcp_aux.o`, `zfcp_ccw.o`, and `zfcp_dbf.o`. `obj-$(CONFIG_ZFCP) += zfcp.o` connects the composite driver to kernel configuration.

Control flow: kbuild compiles and links the listed objects when `CONFIG_ZFCP` is enabled.

State and persistence: no runtime state; the file controls build composition.

Dependencies and integration: integrates zfcp auxiliary, ccw, debug, ERP, Fibre Channel, FSF, QDIO, SCSI, sysfs, unit, and diagnostic components into one module or built-in driver.

Risks: missing an object from `zfcp-objs` yields unresolved symbols or disabled functionality. Object ordering can matter for initcall/linkage expectations in rare cases, though this file uses conventional composite object linkage.

Test signals: `CONFIG_ZFCP=m` and `CONFIG_ZFCP=y` builds, link checks for all zfcp symbols, and ensuring researched objects are included in `zfcp.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_aux.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_aux.c

Purpose: provides zfcp module initialization/exit and core adapter/port allocation helpers, low-memory buffer pools, status-read refill scheduling, initial device configuration, and service-level reporting.

Important APIs and functions: module entry/exit are `zfcp_module_init()` and `zfcp_module_exit()`. Initial device parsing flows through `zfcp_init_device_setup()` and `zfcp_init_device_configure()`. Runtime helpers include `zfcp_get_port_by_wwpn()`, `zfcp_status_read_refill()`, `zfcp_adapter_enqueue()`, `zfcp_adapter_unregister()`, `zfcp_adapter_release()`, and `zfcp_port_enqueue()`.

Control flow: module init creates aligned slab caches, attaches the FC transport, reserves per-device transport data, registers the ccw driver, and optionally configures a boot-specified `device=busid,wwpn,lun`. Adapter enqueue takes a ccw device reference, allocates and initializes all adapter subsystems, creates mempools/workqueues/debugfs/sysfs/Fibre Channel GS state, starts ERP support, and stores adapter drvdata. Failure unwinds broadly through cancellation and subsystem teardown. Port enqueue rejects duplicates under adapter locking, registers a child device, links it into the adapter port list, and marks it running.

State and persistence: allocates the live `struct zfcp_adapter` graph, mempools, request list, debug feature state, FC stats, work items, ERP queues, and `struct zfcp_port` children. Module parameters and runtime objects persist until unregister/remove or module exit.

Dependencies and integration: integrates with ccw driver registration, SCSI FC transport, zfcp FSF/QDIO/ERP/FC/SCSI/sysfs/diag/debug subsystems, kernel device model, mempools, workqueues, and service-level reporting.

Risks: adapter setup has many partial-initialization points; incomplete unwind can leak work, device references, pools, or debug registrations. `zfcp_allocate_low_mem_buffers()` returns immediately on failure and relies on later broad cleanup. Initial device parsing must reject malformed boot parameters without leaving devices online incorrectly. Port list locking and device references protect lookup/enqueue races.

Test signals: module load/unload, failure injection at each allocation/setup step, boot `device=` parsing valid/invalid inputs, adapter online allocation then remove, duplicate port enqueue rejection, status-read refill miss counter and reopen trigger, and sysfs/debug/resource cleanup after failed enqueue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ccw.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ccw.c

Purpose: binds zfcp to the s390 common I/O ccw bus, manages adapter references, handles online/offline/remove/notify/shutdown callbacks, and declares supported FCP device IDs.

Important APIs and functions: `zfcp_ccw_driver` is the registered ccw driver. Adapter reference helpers are `zfcp_ccw_adapter_by_cdev()` and `zfcp_ccw_adapter_put()`. Lifecycle callbacks include `zfcp_ccw_probe()`, `zfcp_ccw_remove()`, `zfcp_ccw_set_online()`, `zfcp_ccw_set_offline()`, `zfcp_ccw_notify()`, and `zfcp_ccw_shutdown()`. `zfcp_ccw_activate()` centralizes reopen, ERP wait, and port scan flush.

Control flow: probe defers allocation. First set-online enqueues an adapter, resets request numbering, activates ERP reopen, waits for random-backoff port scanning, then forces an unconditional scan for no-auto-rescan cases. Set-offline shuts down the adapter through ERP and waits. Remove sets the device offline, detaches unit and port device lists under locks, unregisters child devices, and unregisters the adapter. Notify maps CIO events to adapter shutdown or reopen.

State and persistence: adapter lifetime is tied to ccw device drvdata and kref references guarded by a spinlock. Online/offline transitions update adapter status through ERP helpers rather than directly freeing structures. Child port/unit lists are spliced for safe unregister outside locks.

Dependencies and integration: depends on s390 ccw bus IDs, CIO event types, zfcp ERP, FC port scan work, request-list invariants, and adapter allocation/unregister helpers from `zfcp_aux.c`.

Risks: reference management is central; missing `zfcp_ccw_adapter_put()` can leak adapters, while premature release can race ccw callbacks. `BUG_ON(!zfcp_reqlist_isempty())` assumes no outstanding requests on online. Remove must avoid unregistering child devices while still on shared lists. Notify returns 1 even when handled to indicate event processing to CIO.

Test signals: ccw online/offline cycles, first-online allocation and second-online reuse, CIO_GONE/NO_PATH/OPER/BOXED notifications, remove with populated ports/units, shutdown path, adapter kref under concurrent callbacks, and request-list empty invariant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_ccw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.c -->
# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.c

Purpose: implements zfcp debug feature tracing for HBA/FSF events, recovery, SAN requests/responses, SCSI command/error handling, and payload records.

Important APIs and functions: module parameters `dbfsize` and `dbflevel` size and filter debug areas. HBA tracing includes `zfcp_dbf_hba_fsf_res()`, `zfcp_dbf_hba_fsf_fces()`, `zfcp_dbf_hba_fsf_reqid()`, `zfcp_dbf_hba_fsf_uss()`, `zfcp_dbf_hba_bit_err()`, and `zfcp_dbf_hba_def_err()`. Recovery tracing includes `zfcp_dbf_rec_trig()`, `zfcp_dbf_rec_trig_lock()`, `zfcp_dbf_rec_run_lvl()`, and `zfcp_dbf_rec_run_wka()`. SAN/SCSI tracing includes `zfcp_dbf_san_req()`, `zfcp_dbf_san_res()`, `zfcp_dbf_san_in_els()`, `zfcp_dbf_scsi_common()`, and `zfcp_dbf_scsi_eh()`. Adapter registration uses `zfcp_dbf_adapter_register()` and `zfcp_dbf_adapter_unregister()`.

Control flow: each trace path checks debug level where useful, locks the matching per-area spinlock, zeroes a reusable record buffer, fills common and event-specific fields, optionally emits payload chunks through `zfcp_dbf_pl_write()`, and calls `debug_event()`. SAN response logging caps GPN_FT directory-service payloads after the last advertised entry to avoid logging stale scatterlist data. Adapter registration allocates one `struct zfcp_dbf`, initializes locks, registers rec/hba/pay/san/scsi debug areas, sets views and levels, and attaches it to the adapter.

State and persistence: per-adapter debug state contains debug area handles, reusable record buffers, and spinlocks. Debug records are retained in s390 debug feature buffers sized by module parameter, not persistent storage. Payload counters split long records across multiple debug events.

Dependencies and integration: depends on s390 `debug_register()` infrastructure, zfcp FSF/QDIO/FC/SCSI data structures, scatterlists, Fibre Channel CT/GPN_FT formats, adapter ERP locks, and SCSI command/FCP response layouts.

Risks: trace functions run in error and interrupt-adjacent contexts, so locking and bounded copying are important. Record buffers are shared per adapter and must be protected by the correct spinlock. Payload copying from scatterlists assumes valid mapped entries. GPN_FT cap logic is format-specific; incorrect matching can over-truncate or expose stale response bytes. Debug registration failure must unregister all earlier areas.

Test signals: debug area registration/unregistration, dbflevel filtering, long payload chunking and counters, FSF response payload log offsets, unsolicited status with and without payload, recovery traces with ERP lock held and lock wrapper, SAN request/response payloads including GPN_FT cap cases, SCSI command and TMF traces with/without FSF response, and failure injection for partial debug area registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_dbf.c -->
