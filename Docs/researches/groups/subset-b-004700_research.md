# subset-b-004700

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slip.c -->
# sources/distributed-fs/ceph-client/drivers/net/slip/slip.c

Purpose: implements the kernel SLIP line discipline and virtual net_device bridge between a TTY byte stream and the IP networking stack. It handles SLIP byte stuffing, optional CSLIP header compression, optional printable SLIP6 encoding, optional keepalive/outfill timers, dynamic `sl%d` netdev allocation, and module registration of the `N_SLIP` line discipline.

Important APIs/functions: `slip_init` allocates the global `slip_devs` table and registers `sl_ldisc`; `slip_exit` hangs up active lines, unregisters devices, and removes the line discipline. `slip_open`, `slip_close`, `slip_hangup`, `slip_receive_buf`, `slip_write_wakeup`, and `slip_ioctl` are the TTY line-discipline entry points. Netdev operations are `sl_open`, `sl_close`, `sl_xmit`, `sl_change_mtu`, `sl_get_stats64`, and `sl_tx_timeout`. Buffer helpers `sl_alloc_bufs`, `sl_realloc_bufs`, and `sl_free_bufs` maintain receive, transmit, and optional CSLIP compression buffers. Framing helpers are `slip_esc`, `slip_unesc`, and, under `CONFIG_SLIP_MODE_SLIP6`, `slip_esc6`/`slip_unesc6`.

Control flow: attaching the line discipline requires `CAP_NET_ADMIN`, serializes under RTNL, recycles hung-up channels with `sl_sync`, allocates a new `slip`/netdev pair if needed, allocates MTU-sized buffers, and registers the netdev. Rx bytes arrive through `slip_receive_buf`, which filters TTY error flags, decodes SLIP or SLIP6 framing, and calls `sl_bump` on a completed frame. `sl_bump` optionally handles CSLIP adaptive/compressed headers, creates an skb, marks it as `ETH_P_IP`, and injects it with `netif_rx`. Tx starts in `sl_xmit`, stops the netdev queue, SLIP-escapes the skb into `xbuff`, writes to `tty->ops->write`, and uses `TTY_DO_WRITE_WAKEUP` plus `tx_work` to drain `xleft` bytes later. Close clears `tty->disc_data` via RCU, flushes pending work, deletes timers, and unregisters the netdev.

State and persistence: persistent module state is the `slip_devs` array sized by the `slip_maxdev` module parameter. Per-channel state lives in `struct slip`: TTY and netdev pointers, lock, work item, frame buffers and counters, MTU/buffer size, mode flags, optional compression state, optional SLIP6 bit accumulator, optional keepalive/outfill timer values, lease flag, and owner pid. There is no disk persistence. Synchronization uses RTNL for channel allocation and device registration, `spin_lock_bh` for channel fields, RCU for `tty->disc_data` readers, workqueue flushing on close, and timer deletion for smart mode.

Dependencies and integration: depends on TTY line-discipline APIs, net_device registration, skb allocation/injection, rtnetlink, `if_slip` ioctls, optional `net/slhc_vj.h` CSLIP compression, and optional timers. The device presents point-to-point, no-ARP, multicast-capable interfaces with MTU range 68..65534 and type `ARPHRD_SLIP + mode`.

Risks: TTY lifetime and async write wakeups are subtle; missed `TTY_DO_WRITE_WAKEUP` ordering can wedge Tx, and close must synchronize RCU/work before freeing state. MTU reallocation is atomic but can drop in-flight Tx/Rx data if the new buffer is smaller. Rx framing drops frames after TTY parity/overrun errors or buffer overflow until the next END. CSLIP adaptive mode changes behavior based on packet headers and can ignore compressed packets when CSLIP is disabled. `slip_exit` notes asynchronous hangup limitations. Smart keepalive can hang up the TTY if no frames clear `SLF_KEEPTEST`.

Test signals: attach/detach `N_SLIP` on a pseudo-TTY, verify `sl%d` creation/removal and `SIOCGIFNAME`. Send escaped END/ESC sequences and malformed oversized frames, checking `rx_packets`, `rx_over_errors`, and drops. Exercise partial TTY writes and `write_wakeup` drain behavior. Change MTU while traffic is active. Under relevant configs, test CSLIP adaptive enablement, SLIP6 printable frames, keepalive timeout hangup, outfill END writes, and lease ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slip.h -->
# sources/distributed-fs/ceph-client/drivers/net/slip/slip.h

Purpose: defines private SLIP driver constants and `struct slip`, the shared state block used by `slip.c` for each serial-line network channel.

Important APIs/types/functions: `SL_INCLUDE_CSLIP` gates CSLIP support when both `CONFIG_INET` and `CONFIG_SLIP_COMPRESSED` are enabled. `SL_MODE_DEFAULT`, `SL_NRUNIT`, and `SL_MTU` provide default mode/count/MTU. Protocol byte constants `END`, `ESC`, `ESC_END`, and `ESC_ESC` define standard SLIP framing. `struct slip` contains the TTY/netdev association, locking, Tx work, optional CSLIP state, Rx/Tx buffers, MTU and buffer sizing, optional SLIP6 bit state, flags, mode, lease/pid metadata, and optional smart timers. Flag bits include `SLF_INUSE`, `SLF_ESCAPE`, `SLF_ERROR`, `SLF_KEEPTEST`, and `SLF_OUTWAIT`; mode bits include raw SLIP, CSLIP, SLIP6, CSLIP6, AX25, and adaptive.

Control flow: the header has no executable flow, but its fields are directly consumed by open/close, Rx unescaping, Tx encapsulation, ioctl mode selection, timers, and buffer allocation in `slip.c`.

State and persistence: `struct slip` is the per-channel persistent in-kernel state while the line discipline/device exists. Buffer pointers are owned by the channel and freed during netdev uninit or open failure. No fields persist beyond device lifetime.

Dependencies and integration: relies on kernel config symbols, TTY and net_device structures, optional `struct slcompress`, workqueue and timer types, and UAPI mode semantics from `linux/if_slip.h`.

Risks: `SL_NRUNIT` controls the default global allocation size and can be overridden by module parameter in `slip.c`. Mode bits are mixed into ARP hardware type, so unsupported config combinations must be rejected by ioctl. The `END` macro is explicitly undefined first because some architectures define it for assembly.

Test signals: compile matrix with and without CSLIP, SLIP6, and smart options; verify `sizeof(struct slip)` and mode defaults; confirm ioctl mode values map to expected netdev types and fields are initialized before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/sungem_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/sungem_phy.c

Purpose: provides MII PHY probing and per-chip operation tables for the sungem Ethernet MAC driver, including Broadcom BCM52xx/54xx, Marvell 88E1101/88E1111, and a generic MII fallback.

Important APIs/functions: exported `sungem_phy_probe` resets a PHY, reads `MII_PHYSID1/2`, selects a `mii_phy_def`, and stores it in `phy->def`. MDIO wrappers `sungem_phy_read/write` and `__sungem_phy_read/write` call driver-supplied MDIO callbacks. Initialization/suspend functions include `bcm5201_init`, `bcm5221_init`, `bcm5241_init`, `bcm5400_init`, `bcm5401_init`, `bcm5411_init`, `bcm5421_init`, `marvell88e1111_init`, and `generic_suspend`. Negotiation functions include `genmii_setup_aneg`, `genmii_setup_forced`, `bcm54xx_setup_aneg`, `bcm54xx_setup_forced`, `marvell_setup_aneg`, and `marvell_setup_forced`. Link functions include `genmii_poll_link/read_link`, `bcm54xx_read_link`, `bcm5421_poll_link/read_link`, `bcm5461_poll_link/read_link`, and `marvell_read_link`. Fiber controls are `bcm5421_enable_fiber` and `bcm5461_enable_fiber`.

Control flow: probe sets `phy->mii_id`, calls `reset_one_mii_phy` to clear isolate/power-down and wait for reset completion, reads the 32-bit PHY ID, scans `mii_phy_table`, and installs the matched definition. Later the sungem MAC calls the selected ops to initialize chip-specific registers, configure autonegotiation or forced speed/duplex, poll link status, and read resolved link parameters. Broadcom gigabit paths program standard advertise registers and 1000Base-T control, then use aux status/link tables. Marvell paths configure auto-MDIX and use PHY-specific status resolution. Fiber-capable Broadcom paths switch shadow/config registers before polling or reading link.

State and persistence: persistent state is in caller-owned `struct mii_phy`: selected definition, MII ID, speed, duplex, pause, autoneg, and advertising. This file maintains only static const operation/definition tables. Hardware state is written through MDIO registers and persists in the PHY until reset/power cycle or reconfiguration.

Dependencies and integration: includes `linux/sungem_phy.h`, MII/ethtool constants, Open Firmware helpers for PowerMac low-power quirks, and MDIO callbacks supplied by the MAC driver. It exports only `sungem_phy_probe`; the rest is selected through `mii_phy_def.ops`.

Risks: many initialization sequences are hardware-specific magic values borrowed from Apple/Open Firmware/Darwin behavior, so incorrect changes can break old PowerMac hardware. Some suspend paths are intentionally disabled. Autoneg advertisement uses older `SUPPORTED_`/`ADVERTISED_` bit conventions. Reset polling can fail and returns `-ENODEV`. Marvell/Broadcom gigabit forced settings contain comments about uncertain datasheet interpretation.

Test signals: probe each supported PHY ID and generic fallback with mocked MDIO reads. Validate reset timeout handling, autoneg register writes for advertised modes, forced 10/100/1000 behavior, pause resolution, and fiber/copper mode detection. Hardware smoke tests should cover link up/down transitions, suspend/resume, and PowerMac low-power device-tree cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/sungem_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/tap.c -->
# sources/distributed-fs/ceph-client/drivers/net/tap.c

Purpose: implements the common TAP character-device/socket library used by virtual netdev drivers to expose Ethernet frames to userspace, including multiqueue support, virtio-net headers, offload negotiation, zero-copy send, XDP-buffer send, and exported helpers for cdev/minor management.

Important APIs/functions: exported queue/device helpers are `tap_del_queues`, `tap_handle_frame`, `tap_get_minor`, `tap_free_minor`, `tap_get_socket`, `tap_get_ptr_ring`, `tap_queue_resize`, `tap_create_cdev`, and `tap_destroy_cdev`. File operations are `tap_open`, `tap_release`, `tap_read_iter`, `tap_write_iter`, `tap_poll`, and `tap_ioctl`. Data movement helpers are `tap_get_user`, `tap_put_user`, `tap_do_read`, `tap_sendmsg`, `tap_recvmsg`, `tap_get_user_xdp`, and `tap_alloc_skb`. Queue lifecycle helpers include `tap_set_queue`, `tap_enable_queue`, `tap_disable_queue`, `tap_put_queue`, and `tap_get_queue`.

Control flow: a backend driver registers a TAP cdev with `tap_create_cdev` and obtains minors for individual `tap_dev` instances. Opening a TAP device resolves the major/minor to a `tap_dev`, allocates a `tap_queue` socket and `ptr_ring`, initializes raw-socket-like ops, enables zerocopy when underlying features allow it, and attaches the queue under RTNL. Rx from the lower netdev enters `tap_handle_frame`, chooses a queue by hash/rxq/fallback, optionally GSO-segments or checksum-fixes packets according to virtio/offload settings, enqueues skbs into the queue ring, and wakes readers. Userspace reads via `tap_do_read`/`tap_put_user`; writes via `tap_get_user` build an skb from iovecs, parse optional virtio headers, handle zerocopy, adjust VLAN network header depth, and transmit with `dev_queue_xmit`. Socket ops mirror the file path and can also send XDP buffers.

State and persistence: global state is `major_list`, containing registered cdev majors and an IDR of minors protected by spinlock/RCU. Per-file state is `struct tap_queue`, referenced by the file and the attached `tap_dev` sock reference. Per-device state is in caller-owned `struct tap_dev`: queue array, queue list, feature callbacks, minor, and drop counters. Lifetime relies on RTNL for attach/detach, RCU for queue/device dereferences, `sock_hold/sock_put`, `synchronize_rcu`, and `ptr_ring` cleanup in `tap_sock_destruct`.

Dependencies and integration: integrates with `if_tap`, `if_tun`, `tun_vnet.h`, virtio-net headers, ptr_ring, skbuff/GSO/checksum helpers, XDP, cdev/idr, net namespaces, rtnetlink, and exported `NETDEV_INTERNAL` symbols. Backend drivers provide `tap_dev`, feature update callbacks, and drop counters.

Risks: queue lifetime is intentionally loose-coupled; missing RTNL/RCU discipline can leave stale queue-to-device pointers. Ring full paths drop packets and must update backend counters. Offload semantics invert some TUN userspace expectations and can expose oversized/GSO frames if negotiated incorrectly. Zero-copy requires careful `ubuf_info` completion. `set_offload` appears to compare `feature_mask` against `TUN_F_USO*` flag bits in one condition, which is a code path worth reviewing because `feature_mask` contains netdev feature bits. Minor allocation is limited by `MINORBITS`.

Test signals: open/close TAP files while deleting the backing netdev; attach/detach queues with `TUNSETQUEUE`; run multiqueue Rx hash/rxq selection; fill rings to test drops; exercise `TUNSETIFF`, `TUNGETIFF`, `TUNGETFEATURES`, `TUNSETOFFLOAD`, vnet header size ioctls, MAC get/set, blocking and nonblocking reads, socket sendmsg/recvmsg, XDP send, VLAN tag reconstruction, GSO segmentation, checksum-help fallback, and cdev create/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/tap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/team/Kconfig

Purpose: declares Kconfig options for the Ethernet team driver and its selectable transmit modes.

Important APIs/types/functions: `NET_TEAM` is a tristate menuconfig for the core `team` module. Mode options are `NET_TEAM_MODE_BROADCAST`, `NET_TEAM_MODE_ROUNDROBIN`, `NET_TEAM_MODE_RANDOM`, `NET_TEAM_MODE_ACTIVEBACKUP`, and `NET_TEAM_MODE_LOADBALANCE`, each depending on `NET_TEAM` and mapping to its own module.

Control flow: build-time selection controls whether the core team driver and optional mode modules are compiled built-in, as modules, or omitted. Help text documents `ip link add ... type team` for core device creation and describes each mode's selection behavior.

State and persistence: no runtime state. Configuration persists in the kernel build config and controls module availability/autoloading.

Dependencies and integration: integrates with the drivers/net Kconfig tree and the Makefile in the same directory. Runtime mode autoload relies on module aliases from the corresponding `team_mode_*.c` files.

Risks: load-balance mode depends on userspace-supplied BPF hash configuration, while active-backup deliberately does not rewrite port MACs and pushes that responsibility to userspace. Building the core without needed mode modules leaves `team_change_mode` unable to find those modes unless modules can be requested.

Test signals: build all y/m/n combinations that make sense, verify generated modules exist, and confirm `request_module("team-mode-%s")` can load each mode selected as module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/team/Makefile

Purpose: builds the team core composite object and optional team mode modules.

Important APIs/types/functions: `team-y := team_core.o team_nl.o` links generated netlink glue with the core implementation. `obj-$(CONFIG_NET_TEAM)` builds `team.o`. Each `CONFIG_NET_TEAM_MODE_*` builds a standalone `team_mode_*.o` module/object.

Control flow: Kbuild includes objects according to Kconfig tristate values. Core and generated netlink code are inseparable within `team.o`; modes remain independently loadable providers registered with `team_mode_register`.

State and persistence: no runtime state; build graph only.

Dependencies and integration: depends on Kbuild and the Kconfig symbols from `team/Kconfig`. Mode modules integrate with the core through exported symbols from `team_core.c`.

Risks: omitting `team_nl.o` from `team-y` would break generic-netlink family registration. Mode objects built without matching aliases would not autoload for mode changes.

Test signals: inspect `modules.order` or built-in objects for selected configs; load `team` and each mode module; run `modinfo` to confirm aliases such as `team-mode-broadcast`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_core.c

Purpose: implements the Ethernet team virtual net_device, port lifecycle, mode registry, options framework, data path dispatch, rtnetlink link operations, generated generic-netlink command handlers, event notifications, and module registration.

Important APIs/functions: exported mode/option helpers include `team_mode_register`, `team_mode_unregister`, `team_options_register`, `team_options_unregister`, `team_options_change_check`, `team_option_inst_set_change`, `team_modeop_port_enter`, and `team_modeop_port_change_dev_addr`. Port operations are centered on `team_port_add`, `team_port_del`, `team_port_enable/disable`, `team_port_enable_rx/tx`, `team_upper_dev_link`, and `team_handle_frame`. Netdev operations include `team_init`, `team_uninit`, `team_xmit`, `team_select_queue`, address/multicast/MTU/VLAN operations, slave add/delete, feature fixing, carrier override, stats, and ethtool link reporting. Rtnetlink integration is `team_link_ops`; generic-netlink handlers are `team_nl_noop_doit`, `team_nl_options_get_doit`, `team_nl_options_set_doit`, and `team_nl_port_list_get_doit`.

Control flow: module init registers a netdevice notifier, the rtnl link kind `team`, and the generic-netlink family. Creating a team netdev initializes per-CPU stats, port lists, Tx-index hash lists, queue-override lists, built-in options, and a no-mode dummy dispatch. Userspace sets the `mode` option over generic netlink; `team_change_mode` refuses changes while ports exist, autoloads `team-mode-<kind>`, installs mode ops, and initializes mode private state. Adding a port validates topology/type/VLAN/open state, preserves original MTU/MAC, lets the mode enter the port, opens the lower dev, mirrors VLANs/promisc/allmulti, registers the Rx handler, links the lower device as a master upper, adds per-port option instances, enables the port, sends netlink change events, and recomputes features. Tx first tries queue override based on skb queue mapping and per-port `queue_id`, then calls the mode transmit op. Rx is intercepted by the lower device handler, checks per-port Rx enablement, calls the mode receive op, updates per-CPU stats, and retargets accepted skbs to the team dev.

State and persistence: per-team state lives in `struct team`: current mode and copied ops, mode private area, port list, enabled port counts, Tx-index hash table, queue override lists, option and option-instance lists, delayed work state for peer notifications/multicast rejoins, user carrier flag, notifier recursion guard, and per-CPU stats. Per-port state includes original device properties, enablement, link state, priority, queue ID, Tx index/hash membership, mode private area, and netlink change flags. All state is in memory and removed on netdev uninit. RTNL serializes configuration, RCU protects fast path port/mode reads, per-CPU `u64_stats_sync` protects counters, and delayed work retries when RTNL is busy.

Dependencies and integration: integrates with net_device master/lower APIs, rtnetlink, generic netlink, ethtool, VLAN syncing, netpoll, notifier chains, qdisc queue mapping, generated `team_nl` policy/ops, and UAPI `linux/if_team.h`. Mode modules call exported registration and option APIs.

Risks: mode changes are only safe with no ports; bypassing that invariant would race data path callbacks. Port add/remove has many unwind steps; ordering around rx_handler, upper link, netpoll, VLAN sync, MTU/MAC restore, and RCU free is important. Queue override depends on stable queue IDs and priority ordering. Generic-netlink option lists are mutable and mark changed/removed state while sending events. Lower-device notifier events can recurse through feature recomputation, requiring `notifier_ctx`. User carrier override suppresses automatic carrier checks. Underlay MTU/type changes are blocked unless initiated by team code.

Test signals: create/delete team links; set invalid and valid modes; verify module autoload for modes; add/remove ports with invalid loopback, already enslaved, upper/lower cycles, VLAN-challenged, and up devices. Exercise Tx/Rx enable toggles, user linkup overrides, priority and queue_id options, peer/mcast delayed notifications, MTU/MAC/VLAN propagation and unwind, feature changes, lower NETDEV_UP/DOWN/CHANGE/UNREGISTER/PRECHANGEMTU events, netlink options get/set/event multicast, port list events, per-CPU stats, netpoll config, and rtnl validation of addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_activebackup.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_activebackup.c

Purpose: implements the team active-backup mode, where a single configured active port handles Tx/Rx and other ports remain backups.

Important APIs/functions: `ab_init_module`/`ab_cleanup_module` register/unregister `ab_mode`. Mode ops are `ab_init`, `ab_exit`, `ab_receive`, `ab_transmit`, and `ab_port_leave`. The mode-specific option `activeport` is implemented by `ab_active_port_init`, `ab_active_port_get`, and `ab_active_port_set`.

Control flow: mode init registers the `activeport` option. Userspace sets `activeport` to a port ifindex; the setter finds that port and stores it in `ab_priv.active_port` using RCU assignment. Tx dereferences the active port under BH RCU context and queues to it, dropping if none exists or xmit fails. Rx accepts frames only from the active port; frames from backups use exact delivery. When the active port leaves, the pointer is cleared and the option instance is marked changed.

State and persistence: state is `struct ab_priv` in `team->mode_priv`, containing an RCU active-port pointer and the option instance used for change notification. It is in-memory only and reset on mode exit/change.

Dependencies and integration: depends on team core mode registration, option APIs, `team_dev_queue_xmit`, RCU pointer access, and generic-netlink option propagation through team core. It advertises `NETDEV_LAG_TX_TYPE_ACTIVEBACKUP`.

Risks: if userspace does not set `activeport`, all Tx packets are dropped. The mode intentionally does not rewrite slave MAC addresses, matching Kconfig help, so userspace must ensure appropriate MAC configuration. Active port removal must notify userspace or stale configuration can persist externally.

Test signals: set active port by ifindex, transmit and receive only through that port, remove the active port and verify option change and Tx drop behavior, try setting nonexistent ifindex, and verify backup-port Rx is exact-delivered rather than accepted by the team device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_activebackup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_broadcast.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_broadcast.c

Purpose: implements team broadcast mode, transmitting every packet through all currently txable ports.

Important APIs/functions: `bc_transmit` clones and sends skbs across ports. `bc_mode_ops` provides transmit plus shared team helpers for port enter and device-address changes. Module init/exit register/unregister `bc_mode`.

Control flow: Tx iterates the RCU port list, remembers the last txable port, clones the skb for previously selected ports, and sends the original skb on the final port to avoid an extra clone. The return value reports success if any queued transmission succeeds.

State and persistence: no private mode state. Port MAC state is managed through core helper ops that set port MACs to the team device address on entry/address change.

Dependencies and integration: uses team core registration and `team_dev_queue_xmit`, skb cloning, RCU port iteration, and LAG type `NETDEV_LAG_TX_TYPE_BROADCAST`.

Risks: clone allocation failures reduce the set of transmitted copies but do not abort the whole send. Broadcast multiplies traffic by the number of txable ports. No custom receive op is provided, so team core dummy receive path is used unless Rx is disabled/handled elsewhere.

Test signals: with several txable ports, verify one original and N-1 clones are queued, return success if at least one port succeeds, behavior with zero txable ports, MAC propagation to ports, and clone allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_broadcast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_loadbalance.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_loadbalance.c

Purpose: implements team load-balance mode using a userspace-supplied classic BPF hash function, selectable hash-to-port method, optional explicit hash bucket mapping, and per-hash/per-port Tx byte statistics.

Important APIs/functions: `lb_transmit` hashes each skb and selects a port. `lb_bpf_func_set/get/free` manage the BPF hash program. `lb_tx_method_set/get` chooses `hash` or `hash_to_port_mapping`. `lb_tx_hash_to_port_mapping_set/get/init` manages 256 hash-bucket mappings. `lb_stats_refresh` periodically aggregates per-CPU hash and port stats into option-visible snapshots. `lb_port_enter/leave` allocate/free per-port stats, and `lb_port_tx_disabled` clears bucket mappings for disabled ports. Module init/exit register/unregister `lb_mode`.

Control flow: mode init installs the default `hash` selector, allocates an extension block and per-CPU hash stats, initializes delayed stats refresh, and registers options. Userspace may load a BPF socket filter as `bpf_hash_func`; `lb_get_skb_hash` runs it and folds the 32-bit result to 8 bits. The selected method maps the hash either by modulo enabled Tx port count or through a 256-entry RCU mapping with fallback to modulo. Tx queues to the chosen port and updates per-CPU hash and port byte counters. Stats refresh runs under RTNL, snapshots all CPUs for each hash and port, compares with last snapshots, marks changed option instances, emits team option events, and reschedules based on tenths-of-second interval.

State and persistence: `struct lb_priv` in `team->mode_priv` stores the RCU BPF program pointer, RCU selector function pointer, per-CPU hash stats, and extension pointer. `lb_priv_ex` stores the original filter copy, 256 hash bucket mappings and option instance pointers, refresh interval/work, and aggregate stat snapshots. Each port has `struct lb_port_priv` with per-CPU stats and option metadata. All state is in memory and freed on mode exit/port leave.

Dependencies and integration: depends on team core options/mode APIs, Linux classic BPF creation/destruction, RCU, delayed work, per-CPU stats with `u64_stats_sync`, skb hashing by BPF, and LACP slow-protocol receive handling. It advertises `NETDEV_LAG_TX_TYPE_HASH`.

Risks: without a BPF program, hashes collapse to 0 and traffic may concentrate on one port unless mappings compensate. BPF replacement must synchronize before destroying the old program. Hash-to-port mappings are invalidated when a port is Tx-disabled, but userspace must observe change events and reconfigure. Stats refresh can generate many option events because there are 256 hash buckets. `lb_receive` exact-delivers LACPDU slow-protocol frames so control traffic is not absorbed by the team device.

Test signals: load/unload valid and invalid BPF filters; verify hash folding and modulo selection; set `lb_tx_method`; map buckets to enabled ports and test disabled-port invalidation; transmit traffic across multiple hashes and validate per-hash/per-port stats after refresh; test interval 0 cancellation; verify LACPDU exact delivery; remove ports and change modes while refresh work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_loadbalance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_random.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_random.c

Purpose: implements team random mode, choosing a random enabled Tx port for each outgoing packet.

Important APIs/functions: `rnd_transmit` selects a random index with `get_random_u32_below`, resolves it through team core Tx index helpers, and queues the skb. Module init/exit register/unregister `rnd_mode`.

Control flow: Tx reads `team->tx_en_port_count`, selects a random index, resolves the indexed port, falls forward to the first txable port if needed, and transmits. It drops the skb if no usable port exists or returns failure if lower xmit fails.

State and persistence: no private mode state. Port address behavior uses team core helper ops to set port MACs to the team device address.

Dependencies and integration: depends on team core Tx index maintenance, RCU lookups, random number generation, and `team_dev_queue_xmit`. It advertises `NETDEV_LAG_TX_TYPE_RANDOM`.

Risks: if `tx_en_port_count` changes concurrently, the selected index may not resolve, hence the fallback/drop path. Distribution is random per packet, not flow-stable, so packet reordering is expected.

Test signals: transmit with one and multiple enabled ports, verify distribution over many packets, disable ports during traffic, confirm drop behavior with zero txable ports, and verify MAC propagation on port enter/address change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_roundrobin.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_roundrobin.c

Purpose: implements team round-robin mode, selecting successive enabled Tx ports based on a packet counter.

Important APIs/functions: `rr_transmit` increments `rr_priv.sent_packets`, maps the count to a port index with `team_num_to_port_index`, resolves the port, and transmits. Module init/exit register/unregister `rr_mode`.

Control flow: for each packet, the mode increments a counter, converts it into a current enabled-port index, finds that port and the first txable port from there, then queues the skb. If no port is usable, the skb is dropped.

State and persistence: `struct rr_priv` in `team->mode_priv` stores only `sent_packets`. It is reset when entering the mode and discarded on mode exit.

Dependencies and integration: depends on team core mode APIs, Tx index helpers, RCU port access, and shared port MAC helper ops. It advertises `NETDEV_LAG_TX_TYPE_ROUNDROBIN`.

Risks: packet-level round robin can reorder flows. `sent_packets` is a plain unsigned integer used on the Tx path, so exact distribution under concurrent Tx is best-effort. Port enable/disable changes alter the modulo mapping.

Test signals: transmit across N ports and verify cycling, disable a port midstream and verify fallback, test zero-port drop behavior, and check counter reset after mode re-entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_mode_roundrobin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_nl.c -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_nl.c

Purpose: generated generic-netlink policy and operation table for the team UAPI described by `Documentation/netlink/specs/team.yaml`.

Important APIs/functions: defines `team_attr_option_nl_policy`, `team_item_option_nl_policy`, `team_nl_policy`, and `team_nl_ops`. The ops table binds `TEAM_CMD_NOOP`, `TEAM_CMD_OPTIONS_SET`, `TEAM_CMD_OPTIONS_GET`, and `TEAM_CMD_PORT_LIST_GET` to handler functions implemented in `team_core.c`.

Control flow: generic-netlink family registration in `team_core.c` references these policy and op arrays. Incoming messages are validated with non-strict legacy validation and dispatched to the corresponding `doit` handler; mutating/get/list commands require `GENL_ADMIN_PERM` except NOOP.

State and persistence: static const policy/ops tables only; no mutable state.

Dependencies and integration: includes netlink/genetlink headers, `team_nl.h`, and UAPI `linux/if_team.h`. Must stay synchronized with the YAML spec and the handler prototypes.

Risks: file is generated and marked "Do not edit directly"; manual edits may be overwritten or diverge from UAPI. Non-strict validation preserves compatibility but shifts deeper validation to handlers.

Test signals: regenerate from YAML and diff; run generic-netlink commands for noop, options get/set, and port list get; verify permission checks and malformed nested attributes are rejected by policy or core handler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_nl.h -->
# sources/distributed-fs/ceph-client/drivers/net/team/team_nl.h

Purpose: generated header exposing the team generic-netlink policy arrays, ops table, and handler prototypes to `team_core.c` and `team_nl.c`.

Important APIs/types/functions: declares `team_attr_option_nl_policy`, `team_item_option_nl_policy`, `team_nl_policy`, `team_nl_ops[4]`, and the four handler prototypes `team_nl_noop_doit`, `team_nl_options_set_doit`, `team_nl_options_get_doit`, and `team_nl_port_list_get_doit`.

Control flow: no executable flow. It provides compile-time linkage between generated netlink tables and core handler implementations.

State and persistence: no mutable state; extern declarations only.

Dependencies and integration: includes netlink/genetlink headers and UAPI `linux/if_team.h`. Generated from `Documentation/netlink/specs/team.yaml`.

Risks: prototype or array-size drift between this header, generated `team_nl.c`, and `team_core.c` will break build or dispatch. Manual edits are discouraged by the generated-file notice.

Test signals: full build of `team.o`; YNL regeneration diff; compile failures for handler signature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/team/team_nl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Kconfig

Purpose: declares the `USB4_NET` driver option for networking over USB4 and Thunderbolt cables using the ThunderboltIP/USB4NET protocol.

Important APIs/types/functions: `USB4_NET` is a tristate depending on `USB4 && INET`. Help text describes interoperability with Apple ThunderboltIP hosts, including Windows and macOS, and names the module `thunderbolt_net`.

Control flow: build-time config controls whether the Thunderbolt networking driver is built in, modular, or omitted.

State and persistence: no runtime state; kernel configuration only.

Dependencies and integration: integrates with the Thunderbolt/USB4 subsystem and IPv4/INET networking availability required by the driver.

Risks: disabling `INET` or `USB4` hides the driver. Built as a module, users need service-driver matching or manual load for Thunderbolt network services.

Test signals: build with `USB4_NET=y/m`, verify `thunderbolt_net` module or built-in object, and confirm dependency constraints in Kconfig resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Makefile

Purpose: builds the Thunderbolt/USB4 networking driver.

Important APIs/types/functions: `obj-$(CONFIG_USB4_NET) := thunderbolt_net.o` creates the driver object; `thunderbolt_net-objs := main.o trace.o` links implementation and tracepoint definition; `CFLAGS_trace.o := -I$(src)` lets tracepoint generation include local `trace.h`.

Control flow: Kbuild compiles the composite object according to `CONFIG_USB4_NET` and applies the include path only for tracepoint compilation.

State and persistence: no runtime state; build graph only.

Dependencies and integration: depends on Kbuild composite-object semantics and local tracepoint header layout.

Risks: omitting `trace.o` would leave tracepoint definitions unresolved; omitting `CFLAGS_trace.o` can break `TRACE_INCLUDE_PATH .` lookup.

Test signals: build with tracing enabled, run `modinfo thunderbolt_net`, and verify trace events under the `thunderbolt_net` system are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/main.c

Purpose: implements the USB4NET/ThunderboltIP Ethernet driver over Thunderbolt XDomain services, including login/logout control protocol, DMA path/ring setup, NAPI receive reassembly, transmit frame fragmentation/checksum handling, ethtool reporting, power management, and service-driver registration.

Important APIs/functions: module entry/exit are `tbnet_init` and `tbnet_exit`. Service lifecycle is `tbnet_probe`, `tbnet_remove`, `tbnet_shutdown`, `tbnet_suspend`, and `tbnet_resume`. Netdev operations are `tbnet_open`, `tbnet_stop`, `tbnet_start_xmit`, `tbnet_get_stats64`, and `eth_mac_addr`. Control protocol helpers include `tbnet_fill_header`, `tbnet_login_request/response`, `tbnet_logout_request/response`, `tbnet_handle_packet`, `start_login`, `stop_login`, `tbnet_login_work`, `tbnet_connected_work`, and `tbnet_tear_down`. Data-plane helpers include `tbnet_alloc_rx_buffers`, `tbnet_alloc_tx_buffers`, `tbnet_free_buffers`, `tbnet_poll`, `tbnet_check_frame`, `tbnet_get_tx_buffer`, `tbnet_tx_callback`, `tbnet_xmit_csum_and_map`, and `tbnet_kmap_frag`.

Control flow: module init publishes a Thunderbolt property directory named `network`, advertises protocol/version/status flags, and registers the `thunderbolt-net` service driver. Probe allocates an Ethernet device, initializes work items/locks/atomics, generates a locally administered MAC from route/local UUID, enables TSO/GRO/checksum features, adds NAPI, registers a Thunderbolt protocol handler for the service UUID, and registers the netdev. Opening the netdev allocates Tx/Rx rings and HopIDs, enables NAPI, and starts login retries. Login succeeds when local request/remote response and remote request/local response have both occurred; connected work allocates the remote input HopID, starts rings, primes Rx buffers, allocates Tx buffers, enables XDomain DMA paths, turns carrier on, and starts the queue. Rx ring callbacks schedule NAPI; polling unmaps frames, validates ThunderboltIP fragment headers, builds or extends an skb across fragments, GRO-delivers the completed Ethernet packet, updates stats, and refills buffers. Tx fragments an skb into 4 KiB Thunderbolt frames with per-frame headers, handles paged frags through local kmap, fills total frame count and optional checksum, syncs buffers for DMA, submits frames, increments frame IDs when supported, and consumes the skb. Stop/suspend/remove tear down login, DMA paths, rings, buffers, protocol handlers, and netdev registration.

State and persistence: `struct tbnet` stores service/XDomain pointers, protocol handler, netdev/NAPI, software stats, in-progress Rx skb/header, command/frame atomics, login flags, local/remote HopIDs, connection mutex, retry counter, work items, and Rx/Tx software rings. Rings store 256 `tbnet_frame` entries with pages, DMA addresses, ring descriptors, and producer/consumer counters. State is runtime only and reset on stop/remove/suspend.

Dependencies and integration: integrates with the Thunderbolt XDomain service/property/protocol APIs, NHI rings, DMA mapping, net_device, NAPI/GRO, ethtool, checksum helpers, VLAN/IP/IPV6/TCP/UDP headers, workqueues, module params, and local tracepoints. It depends on peer-advertised `prtcstns` flags for E2E flow control and fragment ID support.

Risks: login is asynchronous and bidirectional; races are guarded by `connection_lock`, but teardown must stop work before freeing rings. DMA path enablement order is important: Rx must be primed before paths open. Fragment validation must reject CRC/overrun, bad sizes, mismatched IDs/counts, missing indices, and MTU overflow or reassembly can corrupt packets. Tx error rollback subtracts only `frame_index` from `cons`, which is subtle because frame 0 may already be reserved; this path merits focused review. Checksum completion manually edits copied packet headers and must handle VLAN, IPv4, IPv6, TCP, UDP, and GSO correctly. Stats are plain counters without per-CPU synchronization.

Test signals: Thunderbolt/USB4 peer login/logout interoperability; retries/timeouts; open/stop cycles; suspend/resume while running; remove during login; DMA path enable/disable failure injection; Rx malformed fragment headers, CRC/overrun flags, multi-fragment reassembly, MTU limits, GRO delivery; Tx large TSO/GSO packets, paged frags, VLAN, IPv4/IPv6 TCP/UDP checksums, ring-full `NETDEV_TX_BUSY`, Tx callback queue wake; ethtool speed mapping for link speed/width; module parameter `e2e`; tracepoint emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.c

Purpose: instantiates the Thunderbolt networking tracepoints declared in `trace.h`.

Important APIs/functions: defines `CREATE_TRACE_POINTS` before including `trace.h`, causing the tracepoint storage/definitions for the `thunderbolt_net` trace system to be emitted in this compilation unit.

Control flow: no runtime logic beyond tracepoint definition generation at build/load time.

State and persistence: tracepoint static state is generated by the tracing framework; this file adds no driver state.

Dependencies and integration: depends on `trace.h`, the kernel tracepoint infrastructure, and the Makefile include path that lets `TRACE_INCLUDE_PATH .` resolve.

Risks: if included in more than one compilation unit with `CREATE_TRACE_POINTS`, duplicate definitions occur; if omitted from the composite object, trace calls in `main.c` lack definitions.

Test signals: build/link `thunderbolt_net.o`; inspect available events under tracing for `thunderbolt_net`; enable frame/skb trace events while sending traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.h

Purpose: declares tracepoints for Thunderbolt/USB4 networking frame allocation/free, ThunderboltIP frame headers, and skb Tx/Rx lifecycle.

Important APIs/types/functions: trace system is `thunderbolt_net`. Event classes are `tbnet_frame`, `tbnet_ip_frame`, and `tbnet_skb`. Concrete events are `tbnet_alloc_rx_frame`, `tbnet_alloc_tx_frame`, `tbnet_free_frame`, `tbnet_rx_ip_frame`, `tbnet_invalid_rx_ip_frame`, `tbnet_tx_ip_frame`, `tbnet_rx_skb`, `tbnet_tx_skb`, and `tbnet_consume_skb`.

Control flow: `main.c` calls these tracepoints around DMA buffer allocation/free, invalid/valid Rx frame processing, Tx frame preparation, Rx skb delivery, Tx skb start, and Tx skb consumption. The header ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `<trace/define_trace.h>` for standard tracepoint generation.

State and persistence: trace events capture transient fields: ring index, page pointer, DMA address, DMA direction, ThunderboltIP frame size/id/index/count, skb address, length, data length, and fragment count. No driver state is owned by the header.

Dependencies and integration: depends on Linux tracepoint macros, DMA direction names, skbuff helpers, and local include behavior from the Makefile. Included normally by `main.c` and with `CREATE_TRACE_POINTS` by `trace.c`.

Risks: tracepoint field types must match call-site argument types; header path macros require the file to remain in the expected directory. Pointer and DMA address tracing is diagnostic and may be sensitive in production traces.

Test signals: compile tracepoints, enable each event in ftrace/perf, verify allocation/free pairs, observe invalid Rx frame traces on injected bad descriptors, and correlate `tbnet_tx_skb`/`tbnet_tx_ip_frame`/`tbnet_consume_skb` during large-packet Tx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/thunderbolt/trace.h -->
