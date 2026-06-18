# subset-b-003956 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib.h

## Purpose
`ipoib.h` is the shared contract for the IP-over-InfiniBand driver. It defines the packet header layout, device-private state, path/multicast/neighbour caches, connected-mode state, constants for queue sizing and MTU calculations, and cross-file function prototypes used by the netdev, RDMA verbs, multicast, CM, VLAN, netlink, ethtool, and debugfs implementations.

## Important APIs, Types, And Functions
Core constants include `IPOIB_HARD_LEN`, `IPOIB_UD_HEAD_SIZE`, UD/CM MTU and ring sizes, queue limits, work-completion batch sizes, multicast queue limits, and flag bit indices. `IPOIB_OP_RECV` and `IPOIB_OP_CM` tag work-request IDs so CQ polling can dispatch to UD or connected-mode handlers. `IPOIB_QPN()` extracts the 24-bit queue-pair number from an InfiniBand link-layer address.

Important types are `struct ipoib_dev_priv`, `struct ipoib_path`, `struct ipoib_mcast`, `struct ipoib_neigh`, `struct ipoib_ah`, `struct ipoib_rx_buf`, `struct ipoib_tx_buf`, and the connected-mode `struct ipoib_cm_rx`, `struct ipoib_cm_tx`, and `struct ipoib_cm_dev_priv`. `ipoib_priv()` unwraps the RDMA netdev private pointer. `skb_add_pseudo_hdr()` adjusts received packets so the Linux networking stack sees the expected pseudo-header shape.

## Control Flow And State
The header encodes the driver state model. `ipoib_dev_priv` owns runtime device state: InfiniBand device/port/P_Key/GID, QP/CQ/PD resources, NAPI instances, TX/RX rings, path and multicast rbtrees, neighbour RCU hash table, child interfaces, and multiple ordered/delayed work items. Flags such as `IPOIB_FLAG_ADMIN_UP`, `IPOIB_FLAG_OPER_UP`, `IPOIB_PKEY_ASSIGNED`, `IPOIB_FLAG_ADMIN_CM`, and `IPOIB_FLAG_DEV_ADDR_SET` gate open/close, multicast joins, path use, connected mode, and address control.

Connected mode is conditionally compiled under `CONFIG_INFINIBAND_IPOIB_CM`; otherwise the header provides no-op stubs so the rest of the driver builds in datagram-only mode. Multicast state uses flags for found/send-only/busy/attached, with comments documenting the join-state interpretation.

## Dependencies And Integration Points
The file depends on Linux netdevice/skbuff/workqueue/kref/mutex/RCU facilities, neighbour and qdisc infrastructure, and RDMA core headers (`ib_verbs`, `ib_pack`, `ib_sa`). It declares integration points exported among implementation files: NAPI poll handlers, RDMA event handling, multicast join/flush/restart APIs, path lookup/flush APIs, verbs setup, VLAN creation/deletion, netlink registration, sysfs mode and umcast setters, and ethtool setup.

## Risks And Test Signals
Risk concentrates in lifetime and locking contracts: `priv->lock` nests inside TX locking, RCU protects the neighbour hash, AHs are kref-managed and reaped after sends pass `last_send`, and workqueue ordering assumptions are critical. Tests or review signals should cover builds with and without `CONFIG_INFINIBAND_IPOIB_CM` and `CONFIG_INFINIBAND_IPOIB_DEBUG`, queue-size clamping, RX/TX completion dispatch by WR ID flags, P_Key/GID changes, child interface operations, multicast joins/leaves, and CM mode switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_cm.c

## Purpose
`ipoib_cm.c` implements IPoIB connected mode over reliable-connected QPs. It creates passive receive-side CM listeners, accepts remote REQs, builds active transmit connections per neighbour/path, handles CM RX/TX completions, manages shared receive queue fallback behavior, exposes the sysfs `mode` attribute, and performs stale connection and cleanup work.

## Important APIs, Types, And Functions
The module parameter `max_nonsrq_conn_qp` limits non-SRQ connected receive QPs. Receive helpers include `ipoib_cm_alloc_rx_skb()`, `ipoib_cm_post_receive_srq()`, `ipoib_cm_post_receive_nonsrq()`, `ipoib_cm_create_rx_qp()`, `ipoib_cm_modify_rx_qp()`, `ipoib_cm_req_handler()`, `ipoib_cm_rx_handler()`, and `ipoib_cm_handle_rx_wc()`. Transmit helpers include `ipoib_cm_create_tx()`, `ipoib_cm_tx_start()`, `ipoib_cm_tx_init()`, `ipoib_cm_send_req()`, `ipoib_cm_rep_handler()`, `ipoib_cm_send()`, `ipoib_cm_handle_tx_wc()`, `ipoib_cm_destroy_tx()`, and `ipoib_cm_tx_reap()`. Device lifecycle is handled by `ipoib_cm_dev_init()`, `ipoib_cm_dev_open()`, `ipoib_cm_dev_stop()`, and `ipoib_cm_dev_cleanup()`.

## Control Flow And State
Initialization creates CM work items and, where supported, an SRQ plus receive buffers. `ipoib_cm_dev_open()` creates an RDMA CM ID and listens on `IPOIB_CM_IETF_ID | priv->qp->qp_num`. Passive REQs allocate an `ipoib_cm_rx`, create an RC QP, move it INIT/RTR/RTS, optionally allocate per-QP receive buffers, enqueue the connection in `passive_ids`, and send REP private data containing QPN and MTU. Receive completions decode the WR ID, replace or reuse RX buffers, copy small packets below `IPOIB_CM_COPYBREAK`, restore the pseudo-header, update stats, and pass packets into the stack.

Active transmit starts when neighbour/path logic calls `ipoib_cm_create_tx()`. A work item pulls entries from `start_list`, snapshots the SA path record, creates a TX QP/CM ID, sends REQ, and on REP moves the QP to RTR/RTS, marks it operational, and requeues neighbour packets. `ipoib_cm_send()` validates MTU/frags, maps DMA, updates global TX ring accounting, posts sends, and stops/wakes the netdev queue around ring pressure. Completion errors detach the neighbour and move the TX object to `reap_list`.

Receive teardown is deliberately staged. RX connections move from `passive_ids` to `rx_error_list`, then to `rx_flush_list` on `IB_EVENT_QP_LAST_WQE_REACHED`, then through a drain WR to `rx_drain_list`/`rx_reap_list`, then are destroyed. `ipoib_cm_stale_task()` ages unused passive IDs. `ipoib_cm_skb_too_long()` queues packets for asynchronous IPv4/IPv6 packet-too-big feedback.

## Dependencies And Integration Points
This file uses RDMA CM (`ib_cm_*`), verbs QP/SRQ/CQ operations, DMA mapping helpers from `ipoib_ib.c`, path/neighbour APIs from `ipoib_main.c`, sysfs mode handling through `ipoib_set_mode()`, and netdevice queue/stat APIs. It relies on `priv->wq`, `priv->lock`, NAPI CQ polling, and shared `priv->tx_wr`/SGE construction from `ipoib_build_sge()`.

## Risks And Test Signals
Primary risks are teardown races across CM callbacks, QP last-WQE events, CQ drain completions, and neighbour references; MTU/private-data validation; global TX ring accounting shared with UD; and SRQ versus non-SRQ error paths. Test signals include connected/datagram sysfs switching, large MTU unicast with multicast drop warning, SRQ and no-SRQ devices, CM REQ/REP/REJ/DREQ events, TX completion failures, PMTU ICMP generation, stale connection reap, and module builds with CM disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ethtool.c

## Purpose
`ipoib_ethtool.c` supplies the driver's ethtool operations: driver/firmware identity, RX coalescing configuration, selected netdev statistics, link state, and link speed reporting derived from the active InfiniBand port attributes.

## Important APIs, Types, And Functions
`struct ipoib_stats` maps ethtool stat names to `struct rtnl_link_stats64` offsets. `ipoib_get_drvinfo()` fills firmware, bus, and driver strings. `ipoib_get_coalesce()` and `ipoib_set_coalesce()` read/write `priv->ethtool` and call `rdma_set_cq_moderation()` for the receive CQ. `ipoib_get_ethtool_stats()`, `ipoib_get_strings()`, and `ipoib_get_sset_count()` expose eight global stats. `ipoib_get_link_ksettings()` maps InfiniBand active speed and width into ethtool speed/duplex fields. `ipoib_set_ethtool_ops()` installs the static ops table.

## Control Flow And State
Coalescing state is persisted only in `priv->ethtool` for the lifetime of the netdev and is reapplied by user request, not stored externally. `set_coalesce` rejects values beyond `u16`, tolerates `-EOPNOTSUPP` from devices that cannot moderate CQs, and otherwise records the requested values. Link settings return unknown speed/duplex if carrier is down; otherwise they query the RDMA port and multiply lane speed by active width.

## Dependencies And Integration Points
The file depends on Linux ethtool/netdevice APIs and RDMA helpers (`ib_get_device_fw_str`, `ib_query_port`, `ib_width_enum_to_int`, `rdma_set_cq_moderation`). It is wired from `ipoib_setup_common()` in `ipoib_main.c`, and uses `ipoib_priv()` plus `priv->ca`, `priv->port`, and `priv->recv_cq` from the shared device state.

## Risks And Test Signals
Notable risks are offset-based stat reads from a legacy `dev->stats` view, hardware that reports unsupported speed/width values, and coalescing devices that partially accept moderation parameters. Test signals include `ethtool -i`, `ethtool -c/-C`, `ethtool -S`, carrier-down reporting, active speed/width changes, and devices returning `-EOPNOTSUPP` from CQ moderation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_fs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_fs.c

## Purpose
`ipoib_fs.c` implements optional debugfs visibility for IPoIB multicast groups and path records when debug support is enabled. It provides read-only seq_file views under a driver-level `ipoib` debugfs directory.

## Important APIs, Types, And Functions
`format_gid()` renders an InfiniBand GID as colon-separated 16-bit words. The multicast seq operations call `ipoib_mcast_iter_init()`, `ipoib_mcast_iter_next()`, and `ipoib_mcast_iter_read()` to show MGID, creation time, queue length, completion, and send-only state. The path seq operations call `ipoib_path_iter_init()`, `ipoib_path_iter_next()`, and `ipoib_path_iter_read()` to show DGID, completion, DLID, SL, and rate. `ipoib_create_debug_files()` creates per-netdev `<name>_mcg` and `<name>_path` files; `ipoib_delete_debug_files()` removes them; `ipoib_register_debugfs()` and `ipoib_unregister_debugfs()` manage the root directory.

## Control Flow And State
The file does not own driver state; it snapshots state through iterator helpers implemented in `ipoib_main.c` and `ipoib_multicast.c`. Each seq start allocates an iterator and advances to the requested offset. Iterators are freed when next reaches EOF; the stop methods intentionally do nothing. Per-device dentry pointers are stored in `priv->mcg_dentry` and `priv->path_dentry`.

## Dependencies And Integration Points
Dependencies are debugfs, seq_file, and the debug-only iterator APIs declared in `ipoib.h`. Registration is triggered by module init and netdev notifier events in `ipoib_main.c`, creating/removing files as IPoIB netdevices register, rename, and unregister.

## Risks And Test Signals
Risk is mostly diagnostic correctness and iterator lifetime. Because stop does not free the current iterator, the next/start EOF paths are relied on to free allocations; review should verify seq_file lifetime behavior for early close paths. Test signals include building with `CONFIG_INFINIBAND_IPOIB_DEBUG`, inspecting `/sys/kernel/debug/ipoib/*_mcg` and `*_path`, renaming netdevices, and unregistering devices while debugfs files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ib.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ib.c

## Purpose
`ipoib_ib.c` owns the default datagram-mode RDMA datapath and device event flushing. It creates/destroys address handles, posts UD receives and sends, maps/unmaps DMA, handles send/receive CQ completions through NAPI, opens/stops the IB datapath, drains CQs during teardown, reacts to P_Key/GID/LID/port events, and cleans verbs resources.

## Important APIs, Types, And Functions
Address-handle lifecycle is `ipoib_create_ah()`, `ipoib_free_ah()`, `ipoib_reap_ah()`, and reaper helpers. RX uses `ipoib_alloc_rx_skb()`, `ipoib_ib_post_receive()`, `ipoib_ib_post_receives()`, and `ipoib_ib_handle_rx_wc()`. TX uses shared `ipoib_dma_map_tx()`, `ipoib_dma_unmap_tx()`, `ipoib_send()`, `ipoib_ib_handle_tx_wc()`, and `ipoib_qp_state_validate_work()`. CQ entry points are `ipoib_rx_poll()`, `ipoib_tx_poll()`, `ipoib_ib_rx_completion()`, and `ipoib_ib_tx_completion()`. Lifecycle functions include `ipoib_ib_dev_open_default()`, `ipoib_ib_dev_stop_default()`, `ipoib_ib_dev_open()`, `ipoib_ib_dev_stop()`, `ipoib_ib_dev_up()`, `ipoib_ib_dev_down()`, `ipoib_drain_cq()`, `ipoib_queue_work()`, and `ipoib_ib_dev_cleanup()`.

## Control Flow And State
Open checks P_Key presence, starts the AH reaper, initializes the QP, posts receives, opens CM listening if available, enables NAPI, marks initialized, and starts multicast joining. RX completions validate WR IDs/status, replace receive buffers before passing packets up, classify host/broadcast/multicast from GRH DGID, drop multicast loopback from the same QP/LID when appropriate, set checksum state if supported, and deliver through GRO. TX validates GSO, MTU, fragment count, DMA maps the skb, posts either UD SEND or LSO, updates `tx_head`/`global_tx_head`, and uses CQ notifications plus NAPI to reopen stopped queues.

Stop disables NAPI, stops CM, moves the QP to error, drains CQ completions as flush errors, waits up to five seconds for sends/receives, force-frees if hardware is wedged, resets the QP, and re-arms the receive CQ. Flush work has three levels: light invalidates paths and multicast state, normal downs/ups the IB device, and heavy also refreshes P_Key state and restarts QPs. Parent flushes recurse into child interfaces.

## Dependencies And Integration Points
The file integrates with RDMA verbs (`ib_post_recv`, `ib_post_send`, QP/CQ/DMA APIs), netdevice/NAPI/queue APIs, multicast/path/neighbour functions from `ipoib_main.c` and `ipoib_multicast.c`, CM dispatch from `ipoib_cm.c`, and lower-level `rdma_netdev` operations through `priv->rn_ops`. `ipoib_event()` is registered from `ipoib_main.c` and converts RDMA events into flush work.

## Risks And Test Signals
Key risks are CQ drain and teardown races, queue accounting under both UD and CM, DMA unmap correctness on partial failures, AH destruction after last send, multicast loopback filtering, and P_Key/GID change handling while devices are up or down. Test signals include RX/TX under stress, GSO and checksum offload paths, queue stop/wake transitions, TX timeout recovery, port active/error/LID/P_Key/GID events, child interface flush propagation, and simulated CQ/QP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_main.c

## Purpose
`ipoib_main.c` is the central netdevice and module implementation for IPoIB. It registers the RDMA client, creates one IPoIB netdevice per IB-capable port, wires netdev operations, handles open/stop/MTU/mode/MAC/sysfs behavior, resolves unicast paths through the subnet administrator, manages neighbour caching, supports child P_Key interfaces, and coordinates module init/exit.

## Important APIs, Types, And Functions
Public entry points include `ipoib_open()`, `ipoib_intf_init()`, `ipoib_intf_alloc()`, `ipoib_intf_free()`, `ipoib_set_mode()`, `__path_find()`, `ipoib_flush_paths()`, `ipoib_mark_paths_invalid()`, `ipoib_neigh_get()`, `ipoib_neigh_alloc()`, `ipoib_neigh_free()`, `ipoib_del_neighs_by_gid()`, `ipoib_set_umcast()`, `ipoib_add_pkey_attr()`, `ipoib_add_umcast_attr()`, and `ipoib_setup_common()`. Internal high-value logic includes `ipoib_start_xmit()`, `neigh_add_path()`, `unicast_arp_send()`, `path_rec_completion()`, `path_rec_start()`, `ipoib_dev_init()`, `ipoib_ndo_init()`, `ipoib_add_port()`, `ipoib_add_one()`, `ipoib_remove_one()`, `ipoib_init_module()`, and `ipoib_cleanup_module()`.

## Control Flow And State
Module init clamps queue-size module parameters, validates CM copybreak assumptions, registers debugfs, creates the global flush workqueue, registers the SA client and IB client, registers rtnl link ops, and optionally debug netdevice notifiers. `ipoib_add_one()` scans RDMA ports and calls `ipoib_add_port()`, which allocates/initializes the netdev, registers the IB event handler, queues a heavy flush to sync P_Key state, registers the netdev, installs sysfs attributes, and stores the per-device list in RDMA client data.

Netdev open sets admin-up, opens verbs resources through `ipoib_ib_dev_open()`, starts multicast joins, brings child interfaces up, and starts the queue. Stop clears admin-up, stops queues, downs/stops the IB datapath, and brings children down. MTU changes differ by mode: connected mode permits up to CM MTU and warns above multicast MTU; datagram mode clamps to the multicast/admin MTU and tells lower `rn_ops` when available. `ipoib_set_mode()` toggles `IPOIB_FLAG_ADMIN_CM`, updates features/MTU/queue count, and flushes paths.

Transmit builds on the pseudo-header inserted by `ipoib_hard_header()`. Multicast destinations are validated and sent through `ipoib_mcast_send()`. Unicast IP/IPv6/TIPC packets use the neighbour hash; misses create an SA path record and queue packets until completion. Unicast ARP/RARP always path-resolve. `path_rec_completion()` creates an AH from the SA path record, updates all neighbours waiting on the path, optionally starts CM, and requeues pending skbs. Neighbours are stored in an RCU hash sized from ARP GC thresholds, reaped after two GC intervals, and flushed synchronously during uninit.

## Dependencies And Integration Points
The file integrates Linux netdevice, rtnl, sysfs, notifier, RCU, ARP/IPv6 address lookup, and RDMA client/SA/cache APIs. It calls into `ipoib_ib.c` for verbs open/stop/flush, `ipoib_multicast.c` for multicast membership, `ipoib_cm.c` for connected-mode creation, `ipoib_vlan.c` for legacy child sysfs, `ipoib_netlink.c` for rtnl link ops, and `ipoib_fs.c` for debug files. Lower hardware-specific behavior is delegated through `rdma_netdev` ops retained in `priv->rn_ops`.

## Risks And Test Signals
The highest-risk areas are lock ordering across rtnl/netdev/TX/spin locks, async work during unregister, path completion after flush, neighbour refcount/RCU removal, child interface lifetime, mode switching while packets are queued, and MAC/GID/P_Key changes. Test signals include module load/unload, IB device add/remove, parent and child open/stop, sysfs `create_child`/`delete_child`/`mode`/`umcast`, rtnl-created child links, path resolution success/failure, duplicate IP matching for RDMA clients, TX timeout recovery, and debug builds with netdev rename/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_multicast.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_multicast.c

## Purpose
`ipoib_multicast.c` manages InfiniBand multicast membership for IPoIB. It joins the mandatory broadcast group, synchronizes netdevice multicast addresses with IB multicast groups, supports send-only multicast groups for transmit-only traffic, attaches/detaches QPs, creates AHs for multicast sends, controls carrier-on after broadcast join, and flushes/restarts multicast state around device events.

## Important APIs, Types, And Functions
Scheduling and lifecycle helpers include `__ipoib_mcast_schedule_join_thread()`, `ipoib_mcast_join_task()`, `ipoib_mcast_start_thread()`, `ipoib_mcast_stop_thread()`, `ipoib_mcast_dev_flush()`, and `ipoib_mcast_restart_task()`. Membership operations include `ipoib_mcast_alloc()`, `__ipoib_mcast_find()`, `__ipoib_mcast_add()`, `ipoib_mcast_join()`, `ipoib_mcast_join_complete()`, `ipoib_mcast_join_finish()`, `ipoib_mcast_leave()`, `ipoib_mcast_remove_list()`, and `ipoib_check_and_add_mcast_sendonly()`. Transmit entry is `ipoib_mcast_send()`. Debug iterators are compiled when debug is enabled.

## Control Flow And State
The join task waits for `IPOIB_FLAG_OPER_UP`, active port state, and a valid device address. If no broadcast group exists, it allocates one keyed from `dev->broadcast + 4`; until that group is attached, all other joins are deferred. Successful broadcast join updates cached multicast MTU, admin MTU when appropriate, Q_Key, traffic class/rate/SL/flow/hop values, and `rn->mtu`, attaches the QP, creates an AH, schedules carrier-on work, and restarts the join task for non-broadcast memberships.

The multicast list mirrors the netdev multicast address list. Restart clears found flags, validates IPoIB multicast addresses against the broadcast template, ignores userspace-direct groups when `umcast` is enabled and SA records exist, replaces send-only entries with full entries when subscribed, and removes absent non-send-only groups. Send-only groups are created on transmit, queue packets up to `IPOIB_MAX_MCAST_QUEUE`, and retry joins with capped exponential backoff; repeated send-only failure drops queued packets but leaves the group cached for future sends.

Flush removes all multicast groups and broadcast state from rbtrees/lists under lock, waits for in-flight joins, detaches QPs, frees multicast SA handles, drops queued packets, releases AHs, and removes neighbour entries tied to MGIDs.

## Dependencies And Integration Points
The file depends on IB SA multicast APIs, RDMA AH construction, netdevice multicast address APIs, rtnl for carrier-on safety, and lower `rdma_netdev` `attach_mcast`/`detach_mcast`/`send` ops. It is called from `ipoib_ib.c` during up/down/flush, from `ipoib_main.c` transmit and set-rx-mode paths, and from neighbour GC to clean send-only groups.

## Risks And Test Signals
Risks include races between multicast restart/flush/join callbacks, carrier-on during stop/unregister, queued packet drops on join failure, correctness of broadcast-derived MTU/Q_Key values, send-only behavior with subnet managers that reject send-only joins, and userspace-direct multicast filtering. Test signals include broadcast join before carrier, IPv4/IPv6 multicast joins and leaves, send-only transmit to unsubscribed groups, `umcast` toggling, port inactive/active transitions, backoff/retry behavior, group flush during unregister, and debugfs multicast iterator output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_multicast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_netlink.c

## Purpose
`ipoib_netlink.c` registers the rtnl link type `ipoib` so userspace can create, delete, inspect, and change IPoIB child links through netlink instead of the legacy sysfs child interface.

## Important APIs, Types, And Functions
`ipoib_policy` defines `IFLA_IPOIB_PKEY`, `IFLA_IPOIB_MODE`, and `IFLA_IPOIB_UMCAST` as `u16` attributes. `ipoib_fill_info()` emits P_Key, connected/datagram mode, and umcast state. `ipoib_changelink()` applies mode and umcast changes. `ipoib_new_child_link()` validates `IFLA_LINK`, rejects child-of-child creation, initializes the new netdev with `ipoib_intf_init()`, calls `__ipoib_vlan_add()` with `IPOIB_RTNL_CHILD`, and then applies optional attributes. `ipoib_del_child_link()` queues child unregister. `ipoib_get_link_ops()`, `ipoib_netlink_init()`, and `ipoib_netlink_fini()` expose and register the static `rtnl_link_ops`.

## Control Flow And State
Newlink resolves the parent by ifindex in the target link netns, defaults the child P_Key to the parent P_Key when not specified, and uses the same child add core as VLAN/sysfs creation but with `IPOIB_RTNL_CHILD` so duplicate P_Keys are allowed and proprietary sysfs child attributes are skipped. Changelink delegates mode strings to `ipoib_set_mode()`, which may temporarily drop/reacquire rtnl, and toggles umcast directly. `fill_info` serializes the current state from `priv->pkey` and flag bits.

## Dependencies And Integration Points
The file depends on rtnetlink, netdevice lookup, IPoIB constants from `if_link.h`, and driver APIs from `ipoib.h`. It is registered at module init in `ipoib_main.c` and used by child creation in both the generic rtnl path and `ipoib_add_port()` where the ops pointer/priv size can be adjusted to match lower RDMA netdev private size.

## Risks And Test Signals
Risks include parent lookup across namespaces, child-of-child rejection, cleanup when `ipoib_changelink()` fails after registration, duplicate P_Key semantics differing from legacy sysfs, and `ipoib_set_mode()` lock behavior under rtnl. Test signals include `ip link add link ib0 name ib0.X type ipoib pkey ...`, `ip link set type ipoib mode connected/datagram umcast`, `ip -d link show`, duplicate RTNL child P_Keys, deletion of children, and invalid parent/type/attribute values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_verbs.c

## Purpose
`ipoib_verbs.c` wraps the low-level RDMA verbs setup for the default IPoIB UD transport. It attaches/detaches multicast groups, transitions the UD QP through INIT/RTR/RTS, creates CQs and the QP, initializes send/receive work-request templates, tears resources down, and maps IB asynchronous events to IPoIB flush levels.

## Important APIs, Types, And Functions
`ipoib_mcast_attach()` checks/refreshes P_Key assignment, optionally sets Q_Key on the QP, and calls `ib_attach_mcast()`. `ipoib_mcast_detach()` calls `ib_detach_mcast()`. `ipoib_init_qp()` moves the QP through INIT, RTR, and RTS with Q_Key, port, P_Key index, and PSN fields, resetting on failure. `ipoib_transport_dev_init()` initializes CM support, sizes receive/send CQs, creates CQs on alternating completion vectors, creates the UD QP with capability-driven flags, arms CQs, initializes SGE/WR templates, and enables SG features. `ipoib_transport_dev_cleanup()` destroys QP and CQs. `ipoib_event()` routes RDMA events to light, normal, or heavy flush work.

## Control Flow And State
Transport init first tries `ipoib_cm_dev_init()`, and if CM is available expands receive CQ sizing for CM send and receive completions. It chooses completion vectors with a static atomic counter, creates the receive CQ then send CQ, requests notifications, and creates a UD QP with flags such as IPoIB UD LSO, block multicast loopback, netif QP, and OPA netdev use based on device/kernel capabilities cached in `priv`. It then sets DMA lkeys and WR defaults used by the datapath.

Event handling is intentionally coarse grained: client reregister and GID changes without a user-controlled address trigger light flushes; port error/active/LID changes trigger normal flushes; P_Key changes trigger heavy flushes that may restart QPs and update parent/child P_Key state.

## Dependencies And Integration Points
The file depends on RDMA verbs and multicast APIs, `ipoib_cm.c` for connected-mode initialization/cleanup, `ipoib_ib.c` for flush work, and `ipoib_multicast.c` for attach/detach callers. It is invoked from default netdev init/uninit in `ipoib_main.c`, and its `ipoib_event()` handler is registered per parent port.

## Risks And Test Signals
Risks include CQ size calculations when CM is enabled with or without SRQ, failure unwinding that must destroy only created resources, capability flag mismatches on older HCAs, QP state transition failures leaving stale state, and event storms causing repeated flushes. Test signals include devices with/without CM, SRQ, TSO, checksum offload, managed flow steering, OPA support, multicast attach failures, P_Key absence/change, and IB async events for port state, LID, GID, and client reregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_vlan.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_vlan.c

## Purpose
`ipoib_vlan.c` implements legacy sysfs P_Key child interface creation/deletion and the shared child-registration helper also used by rtnetlink. In IPoIB these "VLAN" children represent P_Key partition interfaces rather than Ethernet 802.1Q VLANs.

## Important APIs, Types, And Functions
`parent_show()` exposes the parent device name for legacy children. `is_child_unique()` enforces legacy uniqueness by P_Key while allowing RTNL children to duplicate P_Keys. `__ipoib_vlan_add()` is the shared registration core: it sets the private destructor, validates P_Key, links parent/P_Key/type state, checks uniqueness, registers the netdevice, and adds legacy sysfs attributes. `ipoib_vlan_add()` handles CAP_NET_ADMIN, rtnl locking, legacy interface naming, allocation, and registration. `ipoib_vlan_delete()` finds a matching legacy child and queues `ipoib_vlan_delete_task()` to unregister it from the global workqueue.

## Control Flow And State
Legacy creation is driven by the parent sysfs `create_child` attribute in `ipoib_main.c`. It constructs a name like `<parent>.%04x`, allocates an IPoIB netdev for the same HCA/port, assigns `rtnl_link_ops`, and registers it as `IPOIB_LEGACY_CHILD`. During registration, normal netdev init links the child into `ppriv->child_intfs`, inherits parent GID/MTU properties, and sets `IPOIB_FLAG_SUBINTERFACE`.

Deletion is asynchronous to avoid sysfs/rtnl deadlock. The sysfs callback takes rtnl with trylock only long enough to locate and remove the child from the parent's list, then queues work. The work item later takes rtnl and unregisters the device if it is still registered.

## Dependencies And Integration Points
The file depends on Linux capability checks, rtnl/netdevice registration, the global `ipoib_workqueue`, and shared allocation/init/free paths from `ipoib_main.c`. It is called by sysfs `create_child`/`delete_child` handlers and by netlink child creation through `__ipoib_vlan_add()`.

## Risks And Test Signals
Risks include double-free or destructor mismatches on registration failure, races with parent unregister, list removal before asynchronous unregister, legacy duplicate P_Key ambiguity, and rtnl/sysfs deadlocks. Test signals include creating/deleting legacy children, invalid P_Key values (`0`, `0x8000`, out of range), duplicate legacy P_Keys, duplicate RTNL P_Keys, parent removal while delete work is queued, and register_netdevice failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Kconfig

## Purpose
`iser/Kconfig` declares the kernel configuration option for the iSCSI Extensions for RDMA initiator transport over InfiniBand/RDMA.

## Important APIs, Types, And Functions
The file defines `config INFINIBAND_ISER` as a tristate option named "iSCSI Extensions for RDMA (iSER)". It depends on `SCSI`, `INET`, and `INFINIBAND_ADDR_TRANS`, and selects `SCSI_ISCSI_ATTRS`. The help text describes iSER as iSCSI over RDMA/InfiniBand and points to RFC 5046 and the InfiniBand Annex iSER specification.

## Control Flow And State
There is no runtime control flow or persistent state in this file. Its only state effect is build configuration: when enabled as built-in or module, it allows the Makefile to build the `ib_iser` object and ensures required SCSI iSCSI attribute support is selected.

## Dependencies And Integration Points
The dependencies express that iSER requires the SCSI midlayer, IP networking, and RDMA address translation. The selected `SCSI_ISCSI_ATTRS` integrates the driver with Linux iSCSI transport attributes. The Makefile in the same directory consumes `CONFIG_INFINIBAND_ISER`.

## Risks And Test Signals
Risks are configuration-level: missing dependencies prevent build selection, while incorrect `select` usage could omit iSCSI sysfs/session attributes. Test signals include Kconfig visibility under valid/invalid dependency combinations, built-in and module builds, and confirming `ib_iser.ko` is produced when `CONFIG_INFINIBAND_ISER=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Makefile

## Purpose
`iser/Makefile` defines how the iSER initiator driver is built when `CONFIG_INFINIBAND_ISER` is enabled.

## Important APIs, Types, And Functions
The key rule is `obj-$(CONFIG_INFINIBAND_ISER) += ib_iser.o`, which emits the driver as built-in or module according to the Kconfig value. `ib_iser-y` lists the component objects linked into `ib_iser.o`: `iser_verbs.o`, `iser_initiator.o`, `iser_memory.o`, and `iscsi_iser.o`.

## Control Flow And State
There is no runtime control flow. Build state flows from Kconfig into kbuild: enabled configurations compile the listed source objects and link them into one driver object; disabled configurations compile none of them.

## Dependencies And Integration Points
The file integrates with Linux kbuild and the `INFINIBAND_ISER` Kconfig option. The object list indicates the driver is split into RDMA verbs handling, initiator/session logic, memory registration, and the iSCSI transport binding.

## Risks And Test Signals
Risks are limited to build composition: omitted objects would produce missing symbols or incomplete protocol behavior, and stale object names would break builds. Test signals include `CONFIG_INFINIBAND_ISER=y` and `m` builds, clean module link of `ib_iser.o`, and dependency builds that compile all four listed implementation objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Makefile -->
