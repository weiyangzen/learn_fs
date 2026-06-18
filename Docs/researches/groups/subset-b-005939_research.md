# Research: subset-b-005939

Grouped research for Linux networking headers under `sources/distributed-fs/ceph-client/include/net`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cfg802154.h -->
# sources/distributed-fs/ceph-client/include/net/cfg802154.h

Read `sources/distributed-fs/ceph-client/include/net/cfg802154.h` completely for this pass (605 lines, 17077 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/cfg802154.h_research.md`.

Purpose: declares the cfg802154 internal/public kernel interface for IEEE 802.15.4 WPAN PHYs and WPAN netdevs. It defines driver callback contracts, supported-capability descriptors, PHY/device state, MAC addressing, scan/beacon/association requests, optional link-layer security tables, and registration helpers used by the 802.15.4 and 6LoWPAN stacks.

Important APIs/types/functions: `struct cfg802154_ops` is the main driver operation table, covering virtual interface add/delete, suspend/resume, channel and CCA setup, TX power and ED threshold, PAN/short address updates, CSMA retry/backoff parameters, LBT and default ACK-request settings, scan/beacon control, association/disassociation, and experimental LLSEC operations. `struct wpan_phy_supported`, `struct wpan_phy_cca`, `enum wpan_phy_flags`, `struct wpan_phy`, `struct ieee802154_addr`, `struct ieee802154_coord_desc`, `struct ieee802154_pan_device`, `struct cfg802154_scan_request`, `struct cfg802154_beacon_request`, `struct cfg802154_mac_pkt`, `struct wpan_dev_header_ops`, and `struct wpan_dev` are the key data contracts. Inline helpers include `wpan_phy_supported_bool()`, `wpan_phy_cca_cmp()`, `wpan_phy_net()`, `wpan_phy_net_set()`, `ieee802154_chan_is_valid()`, `wpan_dev_hard_header()`, `wpan_phy_set_dev()`, `wpan_phy_priv()`, `wpan_phy_put()`, and `wpan_phy_name()`. Exported prototypes include `wpan_phy_new/register/unregister/free/find/for_each`, `ieee802154_configure_durations()`, association queries, association limit setting, and short-address allocation.

Control flow: a low-power wireless driver allocates a `wpan_phy` with `wpan_phy_new()`, fills capability and PIB fields, sets the parent device, then registers it. nl802154/cfg802154 code validates user requests against `supported` bitmaps/ranges and calls the appropriate `cfg802154_ops` method. WPAN devices hold per-interface MAC state such as PAN ID, short/extended addresses, sequence counters, backoff/retry values, LBT, ACK defaulting, parent/children association lists, and header creation ops. Scan and beacon requests carry a target `wpan_dev` and `wpan_phy` into driver callbacks. The association helpers inspect and mutate the parent/children lists under the association lock.

State and persistence: the header itself persists no data, but it defines runtime object state owned by the 802.15.4 core and driver: registered PHY devices, namespace binding, TX queue hold/ongoing counters, filtering level, supported channel masks, current channel/page, LLSEC keys/devices/security levels, and per-WPAN association topology. This state lasts until unregister/free or interface teardown and is rebuilt after driver reload.

Dependencies and integration points: depends on Linux IEEE 802.15.4 definitions, netdevice, spinlocks, namespace `possible_net_t`, nl802154 enums, and optional LLSEC structures behind `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`. It integrates with 6LoWPAN, nl802154 netlink, cfg802154 core, WPAN netdev header creation, device model registration, network namespaces, and MAC security management.

Risks: capability validation is easy to get subtly wrong, especially channel bitmasks by page, CCA mode/option pairing, signed TX power/ED values, and boolean support tri-state handling. Association state requires mutex discipline. LLSEC callbacks expose key and frame-counter state and are config gated. Deprecated virtual-interface callbacks coexist with newer callbacks. `wpan_dev_hard_header()` assumes `dev->ieee802154_ptr` and `header_ops->create` are valid.

Test signals: compile with IEEE802154, 6LOWPAN, and experimental LLSEC combinations; register/unregister a mock PHY; validate channel/page rejection, CCA comparisons, and supported bool states; exercise nl802154 add/delete interface, channel/TX-power/ED/backoff/retry/LBT/ACK settings; run scan/beacon/associate/disassociate paths; verify namespace moves, header creation, LLSEC key/device/seclevel mutations, short-address allocation, and teardown without leaked PHY/device references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cfg802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/checksum.h -->
# sources/distributed-fs/ceph-client/include/net/checksum.h

Read `sources/distributed-fs/ceph-client/include/net/checksum.h` completely for this pass (191 lines, 4961 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/checksum.h_research.md`.

Purpose: provides generic networking checksum helpers for copying data while checksumming, one's-complement checksum arithmetic, incremental checksum updates, protocol checksum replacement, remote checksum adjustment, and checksum negation. Architecture-specific implementations can override several helpers.

Important APIs/types/functions: fallback `csum_and_copy_from_user()`, `csum_and_copy_to_user()`, and `csum_partial_copy_nocheck()` combine copying with `csum_partial()`. Arithmetic helpers include `csum_add()`, `csum_sub()`, `csum16_add()`, `csum16_sub()`, `csum_shift()`, `csum_block_add()`, `csum_block_sub()`, `csum_unfold()`, `csum_replace_by_diff()`, `csum_replace4()`, `csum_replace2()`, `csum_replace()`, `csum_from32to16()`, `remcsum_adjust()`, `remcsum_unadjust()`, and `wsum_negate()`. External protocol-aware helpers are `inet_proto_csum_replace4()`, `inet_proto_csum_replace16()`, and `inet_proto_csum_replace_by_diff()`. `CSUM_MANGLED_0` represents UDP-style zero checksum mangling.

Control flow: callers build or update packets by computing partial sums over copied buffers, adding/subtracting one's-complement sums, folding 32-bit sums to 16-bit header checksums, or replacing header fields incrementally rather than recomputing whole packets. `inet_proto_csum_replace*()` updates skb checksum metadata when pseudo-header or payload checksum fields change. `remcsum_adjust()` removes an outer prefix contribution, writes a derived checksum at an offset, and returns a delta later consumed by `remcsum_unadjust()`.

State and persistence: no persistent state is stored. The functions mutate caller-provided checksums, packet memory, and sometimes skb checksum metadata through external helpers. User-copy fallbacks return zero on copy fault, so callers must treat zero as a failure signal in these contexts.

Dependencies and integration points: depends on asm checksum primitives, byte order helpers, `linux/uaccess.h` for fallbacks, `struct sk_buff`, and the IP/TCP/UDP/XFRM/tunnel stack. It is used across IPv4/IPv6, transport protocols, encapsulation, NAT, segmentation, and checksum-offload adjustment paths.

Risks: one's-complement arithmetic has non-obvious carry and zero-mangling rules. `csum_shift()` must match odd-byte alignment semantics. Incremental update helpers require old/new fields in network-endian typed forms. `inet_proto_csum_replace2()` intentionally packs 16-bit values into a 32-bit replacement path. Remote checksum helpers assume valid offsets into writable packet data. Copy-and-checksum fallbacks collapse copy faults to zero, which can be ambiguous if callers ignore error conventions.

Test signals: checksum selftests over odd/even offsets, endian variants, carry wraparound, RFC 1624 replacement cases, IPv4 header TOS/TTL/NAT changes, IPv6 pseudo-header replacement, remote checksum offload adjust/unadjust round trips, user-copy fault injection, and comparisons with architecture-specific checksum implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cipso_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/cipso_ipv4.h

Read `sources/distributed-fs/ceph-client/include/net/cipso_ipv4.h` completely for this pass (308 lines, 7597 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/cipso_ipv4.h_research.md`.

Purpose: declares the IPv4 CIPSO/NetLabel interface for Commercial IP Security Option labels, including DOI mapping objects, standard level/category translation tables, cache/sysctl knobs, socket/request/skbuff label operations, and option validation.

Important APIs/types/functions: constants define DOI/tag/map types and local/remote level/category limits. `struct cipso_v4_doi` stores a DOI number, map type, standard mapping table pointer, accepted tag list, refcount, DOI list node, and RCU callback. `struct cipso_v4_std_map_tbl` maps CIPSO remote levels/categories to local LSM values and marks invalid entries with the high bit. With `CONFIG_NETLABEL`, exported APIs include `cipso_v4_doi_add/free/remove/getdef/putdef/walk`, `cipso_v4_cache_invalidate()`, `cipso_v4_cache_add()`, `cipso_v4_error()`, `cipso_v4_getattr()`, socket/request/skbuff set/delete/get helpers, `cipso_v4_optptr()`, and `cipso_v4_validate()`. Without NetLabel, most operations return `-ENOSYS`, `NULL`, or no-op values while the fallback validator still performs basic wire-format checks.

Control flow: NetLabel management creates DOI definitions and mapping tables, registers them in an RCU/refcounted DOI list, and caches decoded option-to-security-attribute mappings. Socket/request/skbuff paths attach, remove, or read CIPSO options by converting between NetLabel LSM security attributes and CIPSO option tags. Incoming IPv4 option processing validates option length, nonzero DOI, and tag lengths before extracting attributes. Error paths can send CIPSO-related IPv4 errors when enabled.

State and persistence: DOI definitions and mapping tables are runtime kernel state protected by refcounts, lists, and RCU. The label cache is runtime state controlled by sysctl variables such as cache enabled/bucket size and RBM formatting/validation flags. Socket/request/skbuff labels live with those objects and are not durable across reloads.

Dependencies and integration points: depends on NetLabel, LSM security attributes, request sockets, skbuffs, IPv4 options, RCU, refcounting, unaligned big-endian reads, and audit metadata. It integrates labeled networking with SELinux/LSM policy, IPv4 socket setup, request sockets for connection establishment, and packet receive/transmit option handling.

Risks: DOI and mapping lifetimes are security-sensitive; stale RCU objects or bad refcounts can expose wrong labels. Level/category translation must handle invalid sentinel bits and table bounds. Fallback behavior differs when `CONFIG_NETLABEL` is disabled, so callers must tolerate `-ENOSYS`. Option validation only checks structural format and must not be mistaken for policy acceptance. Incorrect socket locking in `cipso_v4_sock_setattr()` callers can race label changes.

Test signals: build with and without NetLabel; add/remove/walk DOI definitions; validate pass-through/translated/local mappings; parse valid and malformed options with short length, zero DOI, truncated tag, and zero tag length; exercise socket/request/skbuff label set/get/delete; invalidate and populate cache; run LSM/NetLabel interoperability tests and audit/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cipso_ipv4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cls_cgroup.h -->
# sources/distributed-fs/ceph-client/include/net/cls_cgroup.h

Read `sources/distributed-fs/ceph-client/include/net/cls_cgroup.h` completely for this pass (88 lines, 2086 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/cls_cgroup.h_research.md`.

Purpose: defines the net_cls cgroup classifier interface used by traffic control to obtain class IDs from the current task or from a socket's cgroup data.

Important APIs/types/functions: when `CONFIG_CGROUP_NET_CLASSID` is enabled, `struct cgroup_cls_state` embeds `cgroup_subsys_state` plus a `classid`. `task_cls_state()` returns a task's classifier state. Inline helpers `task_cls_classid()`, `sock_update_classid()`, `__task_get_classid()`, and `task_get_classid()` retrieve or snapshot class IDs. With the config disabled, `sock_update_classid()` is a no-op and `task_get_classid()` returns zero.

Control flow: socket creation/update paths call `sock_update_classid()` to copy the current task's classid into `sock_cgroup_data`. TC classifier paths call `task_get_classid()`: in process context it reads the current task's classid; in softirq context it avoids using `current` and instead tries to recover a full socket from the skb and read the socket's saved classid.

State and persistence: the classid is stored in cgroup subsystem state and optionally copied into socket cgroup data. No additional persistence exists in this header; values change as tasks move cgroups or sockets are updated.

Dependencies and integration points: depends on Linux cgroup, hardirq/softirq state, RCU, sockets, inet sockets, skb-to-socket helpers, and TC classifier code. It bridges cgroup net_cls policy to qdisc/classifier decisions.

Risks: context detection matters: using `current` in softirq would misclassify packets. RCU protection is required around task CSS access. Sockets that are absent or not full sockets fall back to classid zero in softirq paths. The feature disappears at compile time when `CONFIG_CGROUP_NET_CLASSID` is disabled.

Test signals: compile both config variants; move tasks between net_cls cgroups and verify classid lookup; create sockets and confirm `sock_cgroup_data` snapshots; send packets from process and softirq-like paths; validate zero fallback for interrupt context, missing sockets, and disabled config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/cls_cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel.h -->
# sources/distributed-fs/ceph-client/include/net/codel.h

Read `sources/distributed-fs/ceph-client/include/net/codel.h` completely for this pass (167 lines, 6002 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel.h_research.md`.

Purpose: declares common data types for the CoDel controlled-delay active queue management algorithm: time representation, tunable parameters, runtime variables, statistics, and callback types used by qdisc implementations.

Important APIs/types/functions: `codel_time_t` and `codel_tdiff_t` encode a 1024 ns tick in 32-bit arithmetic. `codel_get_time()`, `codel_time_after/before/after_eq/before_eq`, and `codel_time_to_us()` implement wrap-safe time handling. `struct codel_params` holds `target`, `ce_threshold`, `interval`, `mtu`, ECN enable, and optional DS field selector/mask for CE threshold marking. `struct codel_vars` stores count, lastcount, dropping state, reciprocal inverse square root, first-above time, next-drop time, and latest delay. `struct codel_stats` records max packet, drop counts/bytes, ECN marks, and CE marks. Callback typedefs abstract skb length, enqueue time, drop, and dequeue operations.

Control flow: qdiscs initialize params/vars/stats via helpers in `codel_impl.h`, timestamp packets with `codel_qdisc.h`, and pass callbacks into `codel_dequeue()`. The algorithm compares packet sojourn time against target for at least one interval, then enters a dropping/marking state whose interval is controlled by `interval / sqrt(count)`.

State and persistence: CoDel state is per queue or per flow in the owning qdisc. `codel_params` is configured by qdisc settings, `codel_vars` evolves while a queue remains active, and `codel_stats` accumulates runtime telemetry. Nothing is durable beyond qdisc lifetime.

Dependencies and integration points: depends on ktime, skbuffs, kernel type checking, and qdisc implementations such as CoDel/FQ-CoDel/CAKE-style users that provide callbacks and storage.

Risks: time arithmetic wraps after roughly 2199 seconds and must use provided signed-serial comparisons. Misconfigured `mtu` can suppress drops when backlog is below or equal to MTU. `ce_threshold` and DS field selector settings can mark more or fewer packets than intended. Stats use direct/WRITE_ONCE updates but broader qdisc locking remains the caller's responsibility.

Test signals: validate default target/interval conversions, wrap-safe time comparisons, time-to-us conversion, queue below/above target transitions, MTU suppression, ECN/CE threshold behavior, and stats updates in qdisc selftests or packetdrill/netem scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel_impl.h -->
# sources/distributed-fs/ceph-client/include/net/codel_impl.h

Read `sources/distributed-fs/ceph-client/include/net/codel_impl.h` completely for this pass (273 lines, 8799 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel_impl.h_research.md`.

Purpose: implements the generic CoDel algorithm as static helpers parameterized by skb callbacks, allowing multiple qdisc implementations to reuse the same controlled-delay dequeue/drop/mark logic.

Important APIs/types/functions: `codel_params_init()` sets default interval 100 ms, target 5 ms, disabled CE threshold, no selector mask, and ECN off. `codel_vars_init()` zeros runtime state. `codel_stats_init()` resets max packet. `codel_Newton_step()` updates `rec_inv_sqrt` using a fixed-point reciprocal square-root iteration. `codel_control_law()` computes next drop time. `codel_should_drop()` evaluates sojourn delay, backlog, first-above time, and packet size. `codel_dequeue()` is the main algorithm entry point.

Control flow: `codel_dequeue()` obtains a packet from the caller's dequeue callback, computes current time, and calls `codel_should_drop()`. If already dropping, it leaves dropping state when delay falls below target or loops while now has passed `drop_next`, dropping or ECN-marking packets and scheduling the next drop using the control law. If not dropping and the queue has stayed above target for an interval, it drops/marks one packet, initializes or reuses the drop count, enters dropping state, and schedules the next drop. At the end it optionally CE-marks surviving packets whose delay exceeds `ce_threshold` and whose DS field matches the selector/mask.

State and persistence: mutates caller-owned `codel_vars`, `codel_stats`, and queue backlog through callbacks. `count`, `lastcount`, `dropping`, `first_above_time`, `drop_next`, and `ldelay` persist for the lifetime of the qdisc queue/flow and directly affect future drop cadence.

Dependencies and integration points: includes `net/inet_ecn.h` for ECN marking and uses `skb_get_dsfield()` for selector matching. It is included by qdisc code rather than compiled as a standalone object, so all functions are static and caller-specific.

Risks: `backlog` must reflect bytes queued after drops/dequeues or CoDel may overdrop/underdrop. Callback contracts are strict: dequeue must return the head packet and drop must free/account it exactly once. ECN marking path skips actual drops when marking succeeds, changing stats. `codel_stats_init()` only resets `maxpacket`; callers needing zeroed drop counters must clear the structure first. Fixed-point reciprocal square-root logic is sensitive to count initialization.

Test signals: qdisc tests with sustained queue delay, delay recovery, ECN-enabled and ECN-disabled flows, large backlog requiring multiple drops in one dequeue call, DS-field-gated CE threshold, drop count reuse after quick re-entry, empty queue resets, and callback accounting consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel_qdisc.h -->
# sources/distributed-fs/ceph-client/include/net/codel_qdisc.h

Read `sources/distributed-fs/ceph-client/include/net/codel_qdisc.h` completely for this pass (77 lines, 3024 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel_qdisc.h_research.md`.

Purpose: provides the qdisc-specific skb control block layout and helpers needed by CoDel users to timestamp packets at enqueue and recover enqueue time at dequeue.

Important APIs/types/functions: `struct codel_skb_cb` stores `enqueue_time` and `mem_usage` inside the qdisc private control block. `get_codel_cb()` validates private qdisc control block size and returns a typed pointer. `codel_get_enqueue_time()` reads the timestamp, and `codel_set_enqueue_time()` stores `codel_get_time()`.

Control flow: a qdisc using the CoDel plugin calls `codel_set_enqueue_time()` when enqueuing an skb. Later, the CoDel callback passed as `codel_skb_time_t` calls `codel_get_enqueue_time()` so `codel_dequeue()` can compute sojourn delay.

State and persistence: timestamp and optional memory usage live in `skb->cb` for the time the skb is queued. This metadata is transient and must not collide with other qdisc private data.

Dependencies and integration points: depends on `net/codel.h`, `net/pkt_sched.h`, qdisc skb control block helpers, and the owning qdisc's enqueue/dequeue code.

Risks: qdiscs must reserve enough private control-block space or `qdisc_cb_private_validate()` will catch misuse. Any other code that overwrites qdisc CB data while the skb is queued will corrupt CoDel delay measurement. Timestamps must be set at the correct enqueue point, after any requeue semantics are considered.

Test signals: enqueue/dequeue unit tests verifying timestamp storage, private CB size validation, sojourn delay calculation through callbacks, and interactions with qdiscs that also track `mem_usage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/codel_qdisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/compat.h -->
# sources/distributed-fs/ceph-client/include/net/compat.h

Read `sources/distributed-fs/ceph-client/include/net/compat.h` completely for this pass (95 lines, 2535 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/compat.h_research.md`.

Purpose: declares 32-bit compatibility network ABI structures and conversion helpers used when a compat userspace process invokes socket, message, routing, or multicast APIs on a wider kernel.

Important APIs/types/functions: ABI structures include `struct compat_msghdr`, `struct compat_mmsghdr`, `struct compat_cmsghdr`, `struct compat_rtentry`, `struct compat_group_req`, `struct compat_group_source_req`, and `struct compat_group_filter`. Conversion/helper prototypes include `__get_compat_msghdr()`, `get_compat_msghdr()`, `put_cmsg_compat()`, and `cmsghdr_from_user_compat_to_kern()`.

Control flow: compat syscall paths copy user-provided 32-bit message headers and control messages into native kernel `msghdr`/iov structures, then native socket send/receive code proceeds. On receive, ancillary data can be emitted in compat `cmsghdr` form. Routing and multicast option handlers use packed compat structures so user ABI alignment matches 32-bit layout.

State and persistence: no persistent state is stored. The structures describe transient syscall buffers and conversion outputs. Pointers are represented as `compat_uptr_t` and must be translated through compat user access code.

Dependencies and integration points: depends on `linux/compat.h`, `struct sock`, `struct msghdr`, sockaddr storage, multicast group APIs, route ioctls, and ancillary data handling.

Risks: structure packing/alignment is ABI-critical. `compat_group_filter` uses a union to support historical one-element and flexible-array layouts. Incorrect pointer conversion or control-message length validation can cause user memory faults, truncation, or information leaks. Route metric comment notes binary compatibility quirks.

Test signals: 32-bit userspace socket sendmsg/recvmsg/recvmmsg tests on a 64-bit kernel, ancillary data round trips, malformed controllen/iovlen faults, route ioctl compatibility, multicast group source/filter option tests, and ABI layout checks against 32-bit headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/datalink.h -->
# sources/distributed-fs/ceph-client/include/net/datalink.h

Read `sources/distributed-fs/ceph-client/include/net/datalink.h` completely for this pass (26 lines, 590 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/datalink.h_research.md`.

Purpose: defines the small protocol descriptor used by legacy INET datalink/LLC integration to bind a link-layer protocol type, SAP, header length, receive callback, and header request callback.

Important APIs/types/functions: `struct datalink_proto` contains an 8-byte type field, `struct llc_sap *sap`, `header_length`, `rcvfunc()` for receive delivery, `request()` for building/requesting a datalink header into an skb, and a list node.

Control flow: datalink protocol registration code links descriptors onto a list. Receive paths call `rcvfunc()` with skb, input device, packet type, and original device. Transmit/header-building paths call `request()` with the datalink protocol, skb, and destination address bytes.

State and persistence: descriptors are list-managed runtime registrations. The header defines no allocator or lifecycle; owner modules must keep callback and SAP storage valid while registered.

Dependencies and integration points: depends on LLC SAPs, netdevices, packet types, skbuffs, and legacy IP-over-LLC/datalink code.

Risks: callbacks are raw function pointers with lifetime requirements. The fixed 8-byte `type` field and separate `header_length` must match the protocol's actual header layout. List membership must be synchronized by the owner.

Test signals: protocol registration/removal tests, receive callback dispatch, header construction for LLC/SNAP-like payloads, module unload while registered, and malformed destination/header length cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/datalink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dcbevent.h -->
# sources/distributed-fs/ceph-client/include/net/dcbevent.h

Read `sources/distributed-fs/ceph-client/include/net/dcbevent.h` completely for this pass (39 lines, 766 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dcbevent.h_research.md`.

Purpose: declares the DCB event notifier interface used to publish Data Center Bridging application events to interested kernel listeners.

Important APIs/types/functions: `enum dcbevent_notif_type` currently defines `DCB_APP_EVENT`. With `CONFIG_DCB`, APIs are `register_dcbevent_notifier()`, `unregister_dcbevent_notifier()`, and `call_dcbevent_notifiers()`. Without DCB, inline stubs return zero.

Control flow: DCB code or drivers register notifier blocks, then DCB application changes call the notifier chain with an event value and payload pointer. Consumers react to `DCB_APP_EVENT` or ignore unknown values. Disabled builds compile callers but perform no notification.

State and persistence: notifier list state is owned by the DCB subsystem when enabled. This header stores none. Registrations last until explicit unregister or module teardown.

Dependencies and integration points: depends on Linux notifier blocks and `CONFIG_DCB`. It integrates DCB app table changes with consumers such as drivers or protocol code needing priority/app updates.

Risks: stubs silently succeed when DCB is disabled, so tests must cover real DCB-enabled behavior. Notifier payload typing is by convention. Modules must unregister before unloading.

Test signals: DCB-enabled register/call/unregister ordering, multiple notifier return behavior, app-change notifications, disabled-config no-op compilation, and module unload safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dcbevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dcbnl.h -->
# sources/distributed-fs/ceph-client/include/net/dcbnl.h

Read `sources/distributed-fs/ceph-client/include/net/dcbnl.h` completely for this pass (136 lines, 5104 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dcbnl.h_research.md`.

Purpose: declares the kernel-side DCB netlink helper API and driver operation table for IEEE 802.1Qaz, CEE DCBX, app priority mappings, rewrite mappings, buffer configuration, apptrust, and notifications.

Important APIs/types/functions: `struct dcb_app_type` stores ifindex, `struct dcb_app`, list node, and DCBX mode. Helper APIs include rewrite operations `dcb_getrewr/setrewr/delrewr`, app table operations `dcb_setapp/getapp`, IEEE app operations `dcb_ieee_setapp/delapp/getapp_mask`, map extractors for PCP/DSCP priority and rewrite masks, `dcb_ieee_getapp_default_prio_mask()`, and notify functions `dcbnl_ieee_notify()` and `dcbnl_cee_notify()`. `struct dcbnl_rtnl_ops` is the large per-netdevice callback table for ETS, maxrate, QCN, PFC, app tables, CEE PG/PFC, capabilities, DCBX mode, peer app data, buffers, apptrust, and rewrite add/delete.

Control flow: userspace sends DCB netlink requests; dcbnl core validates and dispatches to a netdevice's `dcbnl_rtnl_ops`, updates shared app/rewrite tables through helpers, then notifies listeners. Drivers implement only supported callbacks. App priority map helpers summarize table state into masks indexed by TC or DSCP.

State and persistence: DCB app/rewrite state is runtime per netdevice/ifindex state. Driver callbacks may reflect hardware or firmware state for ETS/PFC/DCBX/buffers. The header defines contracts; persistent storage, if any, is device-specific.

Dependencies and integration points: depends on `linux/dcbnl.h`, netdevices, DCB netlink families, IEEE 802.1Qaz/CEE data structures, DCBX, and driver ethtool/netlink control paths.

Risks: callback support is sparse and drivers must return consistent errors for unsupported operations. Priority masks and selectors for DSCP/PCP/apptrust are easy to misinterpret. Shared app tables must remain synchronized with hardware DCBX state. Notifications need correct event/cmd/seq/pid values to keep userspace consistent.

Test signals: dcbtool/iproute2 DCB operations for ETS/PFC/app tables, rewrite add/delete, DSCP/PCP map extraction, apptrust setting, buffer settings, peer CEE/IEEE reads, DCBX mode changes, notification observation, and driver unsupported-callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dcbnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/devlink.h -->
# sources/distributed-fs/ceph-client/include/net/devlink.h

Read `sources/distributed-fs/ceph-client/include/net/devlink.h` completely for this pass (2163 lines, 77890 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/devlink.h_research.md`.

Purpose: declares the kernel devlink driver API for exposing physical/networking device management over generic netlink: device/port registration, reload, flash, params, resources, shared buffers, dpipe, traps, health reporters, regions/snapshots, rates, linecards, nested devlinks, and compatibility helpers.

Important APIs/types/functions: core objects include opaque `struct devlink`, `struct devlink_port`, `struct devlink_rate`, `struct devlink_port_attrs`, PCI PF/VF/SF attribute structs, `struct devlink_linecard_ops`, DPIPE field/header/match/action/value/entry/table structures, resource sizing and occupancy callback types, `union devlink_param_value`, `struct devlink_param`, `struct devlink_param_item`, flash/update structs, region ops, health reporter ops/state, trap metadata/policer/group/trap descriptors, and `struct devlink_ops`/`struct devlink_port_ops`. Helper macros define generic params (`DEVLINK_PARAM_GENERIC*`), driver params, generic info version names, generic traps/groups/policers, and typed `devlink_fmsg_put()`. Exported APIs cover alloc/register/unregister/free, locking (`devl_lock` family), shared devlink lookup, port init/register/type/attrs/function/rate/linecard helpers, shared-buffer/dpipe/resource/param/region/info/fmsg/health/trap registration, flash status notifications, refcount get/put, and compat version/flash/phys-port/switch-id helpers.

Control flow: a driver allocates a devlink instance with its `devlink_ops`, stores private data, registers it, then registers ports, params, resources, health reporters, traps, regions, linecards, and other objects. Userspace netlink requests are serialized by the devlink instance lock and dispatched through `devlink_ops` or `devlink_port_ops`. Reload calls down/up callbacks with requested actions/limits. Flash update receives firmware and optional component/overwrite parameters. Traps are registered with contexts, then drivers report trapped skbs via `devlink_trap_report()`. Health reporters collect reports, dumps, diagnoses, tests, and recovery attempts.

State and persistence: devlink maintains runtime object registries, locks, refs, parameter runtime/driverinit/default values, trap action/policer settings, resource sizes and occupancy callbacks, region snapshots, health reporter state, port types/attrs/rates, linecard provisioning/activation state, reload failure status, and nested relationships. Some operations affect persistent device state, especially flash updates, stored firmware, permanent params, and linecard provisioning.

Dependencies and integration points: depends on netdevice, net namespaces, generic netlink UAPI, xarray, firmware loader, flow offload cookies, devlink UAPI enums, ethtool-compatible version data, PCI function modeling, DCB/DSA/QED/Mellanox-style driver management, and optional `CONFIG_NET_DEVLINK` compatibility stubs.

Risks: locking discipline is central: APIs prefixed `devl_` expect the instance lock while non-prefixed helpers often acquire it internally. Driver callbacks must validate extack-visible user requests and hardware capability. Flash and permanent params can alter persistent device state. Trap IDs/names/groups must stay documented and stable. Port attributes must match physical/PCI topology or userspace naming breaks. Region snapshot memory ownership depends on destructor callbacks. The visible `struct devlink_ops` has many optional callbacks, so null handling and unsupported errors must be consistent.

Test signals: devlink netlink selftests for alloc/register/free, port registration and phys names, PCI PF/VF/SF attrs, reload down/up action accounting, flash update with component/overwrite masks, param get/set/default/driverinit flows, resource size/occupancy, region snapshot/read/destructor, health report/recover/dump/diagnose/test, trap group/policer/action/report, linecard provision/fail/activate/deactivate, rate hierarchy, nested devlinks, compat helpers, and disabled `CONFIG_NET_DEVLINK` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason-core.h -->
# sources/distributed-fs/ceph-client/include/net/dropreason-core.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason-core.h` completely for this pass (637 lines, 20902 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason-core.h_research.md`.

Purpose: defines the core `enum skb_drop_reason` namespace and helper macros used to annotate packet drops throughout the network stack for tracing, diagnostics, and reason-aware freeing.

Important APIs/types/functions: `DEFINE_DROP_REASON(FN, FNe)` is the master macro list for core reasons. `enum skb_drop_reason` starts with `SKB_NOT_DROPPED_YET` and `SKB_CONSUMED`, then expands detailed core reasons covering sockets, TCP, UDP, IP, XFRM, BPF, neighbor, qdisc, backlog, XDP/TC, skb/GSO/copy errors, device readiness/ring fullness, ICMP/IP validation, fragmentation, IPv6 NDISC/extension headers, TC cookie/chain/reclassify, VXLAN/tunnel, bridge, CAN, PFMEMALLOC, PSP, and recursion limit. `SKB_DROP_REASON_SUBSYS_MASK` reserves high bits for subsystem-specific reasons. Macros `SKB_DR_INIT`, `SKB_DR`, `SKB_DR_SET`, and `SKB_DR_OR` simplify local reason variables.

Control flow: packet-processing code initializes a reason variable, updates it when a specific failure is discovered, and passes the reason to drop/free paths. `SKB_DR_OR()` preserves the first specific reason unless the current value is unspecified or not-dropped. Tracing code uses the enum values and generated reason strings to expose drop diagnostics.

State and persistence: no runtime state is stored. The enum values are ABI/trace-facing identifiers and must remain stable enough for tooling. Local reason variables live only within packet-processing paths.

Dependencies and integration points: included by `dropreason.h`, qdisc drop reasons, kfree skb tracing, protocol receive/transmit paths, TC/XDP/netfilter/tunnel/bridge/CAN/PSP code, and monitoring tools consuming drop reason strings.

Risks: inserting/renumbering reasons can affect trace consumers. `SKB_DROP_REASON_MAX` is not a real drop reason. Reason selection must avoid overwriting more specific earlier failures. Core reasons overlap broad domains; using a generic reason where a specific reason exists reduces observability.

Test signals: compile-time generation of reason strings, tracepoint output for representative TCP/IP/qdisc/XDP/netfilter/tunnel drops, first-reason preservation with `SKB_DR_OR()`, subsystem mask handling, and userspace tooling compatibility with enum/string updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h -->
# sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h` completely for this pass (114 lines, 3761 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h_research.md`.

Purpose: defines traffic-control qdisc-specific drop reasons as a subsystem-encoded extension of skb drop reasons, enabling detailed diagnostics for queueing discipline drops.

Important APIs/types/functions: `DEFINE_QDISC_DROP_REASON(FN, FNe)` lists qdisc reasons. `enum qdisc_drop_reason` starts at `QDISC_DROP_UNSPEC`, defines `__QDISC_DROP_REASON` as `SKB_DROP_REASON_SUBSYS_QDISC << SKB_DROP_REASON_SUBSYS_SHIFT`, then enumerates `QDISC_DROP_GENERIC`, `OVERLIMIT`, `CONGESTED`, `MAXFLOWS`, `FLOOD_PROTECTION`, `BAND_LIMIT`, `HORIZON_LIMIT`, `FLOW_LIMIT`, `L4S_STEP_NON_ECN`, and `QDISC_DROP_MAX`.

Control flow: qdisc implementations select a qdisc-specific reason when enqueue/dequeue algorithms drop packets. Tracepoints can combine the reason with qdisc handle/name and map it through the qdisc drop reason list registered for the subsystem.

State and persistence: no state is stored. Values are part of the diagnostic reason namespace and should remain stable for tracing.

Dependencies and integration points: depends on `net/dropreason.h` for subsystem tagging. It integrates with TC qdisc algorithms such as CoDel/PIE/RED/FQ/SFQ/CAKE/DualPI2 and qdisc tracepoints.

Risks: `QDISC_DROP_UNSPEC` is a sentinel like not-dropped, not a valid final reason. Reasons must stay below subsystem bounds and must have matching registered strings. Algorithm-specific drops should choose the most precise reason to preserve observability.

Test signals: qdisc trace tests for overlimit, active congestion, flow-table exhaustion, flood protection, band/flow/horizon limits, DualPI2 non-ECN L4S drops, string mapping registration, and fallback to generic where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason-qdisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason.h -->
# sources/distributed-fs/ceph-client/include/net/dropreason.h

Read `sources/distributed-fs/ceph-client/include/net/dropreason.h` completely for this pass (49 lines, 1347 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dropreason.h_research.md`.

Purpose: ties core and subsystem-specific skb drop reason namespaces together and declares the RCU-protected registry used to map subsystem IDs to reason string lists.

Important APIs/types/functions: `enum skb_drop_reason_subsys` defines subsystem IDs for core, mac80211 unusable frames, Open vSwitch, qdisc, and the subsystem count. `struct drop_reason_list` stores a reason string array and count. `drop_reasons_by_subsys[]` is an RCU-protected global registry. `drop_reasons_register_subsys()` and `drop_reasons_unregister_subsys()` publish or remove subsystem reason lists.

Control flow: core drop reasons are always defined by `dropreason-core.h`. Subsystems with extended reason ranges register their string list under a subsystem ID. Tracing/diagnostic code decodes the subsystem bits from a drop reason and looks up the corresponding list under RCU.

State and persistence: registry entries are runtime pointers to static or module-owned reason lists. Access must be under RCU; modules must unregister before the list storage disappears.

Dependencies and integration points: depends on core drop reasons and RCU. It integrates with mac80211, Open vSwitch, qdisc, and any trace or drop-monitor path decoding `enum skb_drop_reason`.

Risks: subsystem lists have module lifetime constraints. Missing registration yields undecodable extended reasons. Subsystem count and IDs must stay synchronized with reason producers. Registry access outside RCU can race unregister.

Test signals: register/unregister subsystem reason lists under RCU, decode core and qdisc reason values, module unload races, missing-list fallback behavior, and trace/drop-monitor output for subsystem-encoded reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dropreason.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsa.h -->
# sources/distributed-fs/ceph-client/include/net/dsa.h

Read `sources/distributed-fs/ceph-client/include/net/dsa.h` completely for this pass (1414 lines, 43043 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dsa.h_research.md`.

Purpose: declares the Distributed Switch Architecture core API and data model for Ethernet switch chips: tagging protocols, switch trees, ports, LAG/bridge/FDB/VLAN state, switch driver operations, devlink integration, phylink/ethtool/DCB/switchdev/TC/PTP hooks, and registration helpers.

Important APIs/types/functions: `enum dsa_tag_protocol` and `struct dsa_device_ops` describe CPU-port taggers. Topology/state types include `struct dsa_lag`, `struct dsa_switch_tree`, `struct dsa_port`, `struct dsa_link`, `struct dsa_db`, `struct dsa_mac_addr`, `struct dsa_vlan`, and `struct dsa_switch`. Inline helpers and macros iterate ports/trees, classify port types, resolve upstream/routing ports, compare bridge/LAG/tree ownership, get devlink private switch data, test whether a netdev uses DSA, and generic-flow-dissect DSA tags. `struct dsa_switch_ops` is the driver callback surface for setup/teardown, PHY/phylink, stats, WoL, timestamping, MAC merge, DCB, port enable/disable, bridge/VLAN/FDB/MDB/switchdev, RXNFC, TC flower/mirror/policer, cross-chip operations, PTP, devlink params/resources/SB/info, MTU, LAG, HSR, MRP, tag_8021q, and conduit state changes. Exported APIs include devlink wrappers, FDB/MDB conflict helpers, simple HSR helpers, switch register/unregister/shutdown/find/suspend/resume, workqueue flush, user-dev check, enqueue, phylink MAC change, and EEE support.

Control flow: a switch driver fills `struct dsa_switch` and `dsa_switch_ops`, then calls `dsa_register_switch()`. DSA builds a switch tree, assigns CPU/DSA/user ports, chooses/connects tag protocols, registers user netdevices/devlink ports, and dispatches netdev, switchdev, bridge, VLAN, FDB/MDB, TC, PTP, ethtool, DCB, and devlink operations to the driver. Data-plane packets on CPU ports are tagged by `xmit()` and decoded by `rcv()`; flow dissectors can locate the real EtherType through generic tag offsets.

State and persistence: DSA runtime state is rich: switch trees, topology route tables, tag ops, LAG ID mappings, bridge membership/refcounts, port type/setup flags, conduit admin/oper state, VLAN filtering/learning, address and VLAN lists, phylink state, devlink ports/resources/regions, FDB/MDB refcounts, and switch private data. Hardware state persists in the switch until explicitly programmed or reset; software state is rebuilt at probe.

Dependencies and integration points: depends on netdevice, PHY/phylink, ethtool, timestamping, OF/platform data, devlink, switchdev, TC flow offload, DCB, LAG/bonding, bridge, HSR/MRP, PTP, and per-vendor tagger modules. It is the central contract between switch chip drivers and Linux networking.

Risks: DSA has many concurrency and ownership boundaries: bitfields are only safe at probe or under RTNL, address/VLAN lists have separate locks, and port/conduit lifetime uses trackers. Topology helpers assume `dsa_to_port()` returns valid ports. Tagger headroom/tailroom and flow dissection must match wire layout. Cross-chip, LAG, FDB isolation, and bridge offload semantics are subtle and can leak or misroute traffic. Devlink and switchdev callbacks must match userspace-visible topology.

Test signals: register/unregister multi-port and multi-chip switches; exercise all port-type iterators and upstream routing; send/receive through taggers; bridge join/leave, VLAN filtering, STP/MST, FDB/MDB add/delete/dump, LAG join/leave/change, HSR/MRP, TC flower/mirror/policer, DCB DSCP/app mappings, PTP timestamping, phylink link changes, devlink params/resources/regions/SB/info, suspend/resume, MTU changes, EEE, and teardown under RTNL/module-unload stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsa_stubs.h -->
# sources/distributed-fs/ceph-client/include/net/dsa_stubs.h

Read `sources/distributed-fs/ceph-client/include/net/dsa_stubs.h` completely for this pass (48 lines, 1314 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dsa_stubs.h_research.md`.

Purpose: provides a small DSA stub interface for code outside the DSA core to call optional DSA functionality, currently conduit hardware timestamp validation, while still compiling cleanly when DSA is disabled.

Important APIs/types/functions: with `CONFIG_NET_DSA`, `struct dsa_stubs` contains `conduit_hwtstamp_validate()`, and `extern const struct dsa_stubs *dsa_stubs` points to registered DSA core stubs. `dsa_conduit_hwtstamp_validate()` checks `netdev_uses_dsa()`, asserts RTNL, and delegates to the DSA stub. Without DSA, the inline helper returns zero.

Control flow: netdevice timestamping configuration code can call `dsa_conduit_hwtstamp_validate()`. Non-DSA devices immediately succeed. DSA conduit devices are validated by DSA core while RTNL prevents stubs from being unregistered concurrently with conduit teardown.

State and persistence: the only state is the global stub table pointer while DSA core is loaded. No per-device state is stored here.

Dependencies and integration points: depends on netdevice, net timestamp config, DSA core, RTNL locking, and `netdev_uses_dsa()` from `dsa.h`.

Risks: callers must hold RTNL for DSA devices. The helper silently succeeds for non-DSA and disabled DSA builds. Stub pointer lifetime is safe only under the documented RTNL condition.

Test signals: compile with and without DSA; validate timestamp config on normal and DSA conduit devices; assert RTNL coverage; unload DSA core after conduit teardown; verify disabled builds do not reject timestamp settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsa_stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dscp.h -->
# sources/distributed-fs/ceph-client/include/net/dscp.h

Read `sources/distributed-fs/ceph-client/include/net/dscp.h` completely for this pass (76 lines, 3252 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dscp.h_research.md`.

Purpose: centralizes numeric Differentiated Services Code Point constants and pool documentation for IPv4/IPv6 DS field classification.

Important APIs/types/functions: defines standardized DSCP codepoints: class selectors `DSCP_CS0` through `CS7`, `DSCP_DF`, assured forwarding `DSCP_AF11` through `AF43`, expedited forwarding `DSCP_EF`, `DSCP_VOICE_ADMIT`, lower-effort `DSCP_LE`, and `DSCP_MAX` as 64. Comments document Pool 1, Pool 2, and Pool 3 assignment rules.

Control flow: no executable control flow. Classifiers, DCB, qdiscs, tunnels, and packet marking code include these constants to compare or assign the six-bit DSCP portion of a DS field.

State and persistence: no state. Constants are compile-time API.

Dependencies and integration points: self-contained aside from include guards. It integrates with DS field helpers, TC flower/u32/BPF classifiers, DCB DSCP priority mappings, qdisc CE-threshold selectors, and QoS policy code.

Risks: constants are six-bit DSCP values, not full 8-bit DS fields including ECN. Callers must shift/mask correctly when operating on IPv4 TOS or IPv6 traffic class bytes. IANA registry changes may add future constants.

Test signals: compile-time assertions for known values, DSCP-to-DS-field shift/mask tests, DCB DSCP mapping tests, TC/qdisc selector tests, and documentation checks against the IANA/RFC codepoint registry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dscp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsfield.h -->
# sources/distributed-fs/ceph-client/include/net/dsfield.h

Read `sources/distributed-fs/ceph-client/include/net/dsfield.h` completely for this pass (53 lines, 1147 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dsfield.h_research.md`.

Purpose: provides inline helpers to read and modify the Differentiated Services field in IPv4 and IPv6 headers while preserving ECN bits and maintaining the IPv4 header checksum.

Important APIs/types/functions: `ipv4_get_dsfield()` returns `iph->tos`. `ipv6_get_dsfield()` extracts the IPv6 traffic class from the first 16 bits of the header. `ipv4_change_dsfield()` applies `(old_tos & mask) | value`, incrementally adjusts the IPv4 header checksum, and stores the new TOS. `ipv6_change_dsfield()` updates the traffic-class bits in the IPv6 version/traffic-class/flow-label word.

Control flow: packet marking or QoS code reads current DS field, computes a masked replacement value, and calls the appropriate IPv4/IPv6 changer. IPv4 uses one's-complement adjustment instead of recomputing the full header checksum; IPv6 has no header checksum.

State and persistence: mutates packet headers in-place. No separate state is stored.

Dependencies and integration points: depends on Linux IP/IPv6 header definitions and byteorder helpers. It is used by TC, netfilter, tunnel, qdisc, and QoS code that marks DSCP/ECN bits.

Risks: the `mask` argument preserves bits where set and `value` must already be positioned in DS field bits; misuse can overwrite ECN or DSCP unintentionally. IPv4 checksum math is sensitive to carry handling. IPv6 helper writes through the first 16-bit word and must preserve version and flow-label bits.

Test signals: IPv4 and IPv6 DSCP/ECN rewrite tests, checksum validation after IPv4 changes, masks that preserve ECN bits, zero/full mask cases, and packet capture verification of traffic-class fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dsfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst.h -->
# sources/distributed-fs/ceph-client/include/net/dst.h

Read `sources/distributed-fs/ceph-client/include/net/dst.h` completely for this pass (621 lines, 16177 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst.h_research.md`.

Purpose: defines the protocol-independent destination cache entry (`dst_entry`) and inline helpers for metrics, references, skb dst ownership, tunnel receive scrubbing, neighbor lookup, output/input dispatch, XFRM lookup integration, PMTU updates, and blackhole routes.

Important APIs/types/functions: `struct dst_entry` stores output device, `dst_ops`, metrics pointer with low-bit flags, expiry, optional XFRM state, input/output callbacks, flags, obsolete state, header/trailer lengths, `rcuref`, use/lastuse, RCU callback, error, traffic class ID, lwtunnel state, device tracker, and uncached route links. `struct dst_metrics` holds RTAX metrics plus refcount. Helpers manage metrics (`dst_metrics_read_only`, `dst_metrics_write_ptr`, `dst_init_metrics`, `dst_copy_metrics`, `dst_metric_raw`, `dst_metric`, `dst_metric_advmss`, `dst_metric_set`, `dst_feature`, `dst_mtu`, `dst4_mtu`, `dst_metric_rtt`, `dst_metric_locked`), references (`dst_hold`, `dst_clone`, `dst_release`, `skb_dst_drop/copy/force`, `dst_hold_safe`), tunnel RX cleanup, `dst_tclassid`, allocation/init/device put, neighbor lookup/confirm/link failure, expiry, device overhead, `dst_output`, `dst_input`, `dst_check`, XFRM lookup wrappers, PMTU update helpers, device/net accessors, and blackhole dst operations.

Control flow: route lookup returns a `dst_entry` and attaches it to an skb. Transmit calls `dst_output()` which indirect-calls the route's output function; receive delivery can call `dst_input()`. Users clone/hold/release dst references as skbs are copied or consumed. If `obsolete` is set, `dst_check()` invokes the protocol check callback. Tunnel receive helpers reset skb metadata before reinjection. XFRM lookup may wrap/replace dsts when IPsec policy applies. PMTU and neighbor operations delegate through `dst_ops`.

State and persistence: dst entries are runtime route cache objects with reference-counted lifetimes, per-entry metrics, expiry, last-use counters, device trackers, lwtunnel/XFRM attachments, and uncached-route links. They are not durable, but are performance-critical shared state.

Dependencies and integration points: depends on `dst_ops`, netdevice, rtnetlink, RCU/refcount/rcuref, jiffies, neighbor subsystem, lwtunnels, XFRM, skb dst encoding, indirect call wrappers, IPv4/IPv6 route functions, and tunnel/PMTU code.

Risks: reference semantics are subtle: skb dst may be no-ref and `skb_dst_force()` requires RCU read lock. `__rcuref` cacheline placement is enforced for performance. Metrics pointer low bits encode flags and require aligned storage. Output/input indirect calls assume a valid skb dst. Device/lwtunnel access under RCU must use RCU accessors. XFRM-disabled stubs bypass policy entirely. PMTU updates and neighbor callbacks are protocol-specific and may be absent.

Test signals: route lookup/clone/release stress, no-ref skb dst forcing under RCU, metrics copy-on-write/read-only/refcounted behavior, IPv4/IPv6 MTU/advmss metrics, obsolete route checking, tunnel receive scrubbing/accounting, output/input dispatch, PMTU update with and without confirmation, neighbor lookup/confirm/link failure, XFRM enabled/disabled builds, blackhole route behavior, and KASAN/KCSAN checks around teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_cache.h -->
# sources/distributed-fs/ceph-client/include/net/dst_cache.h

Read `sources/distributed-fs/ceph-client/include/net/dst_cache.h` completely for this pass (109 lines, 3043 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_cache.h_research.md`.

Purpose: declares a per-CPU destination cache used by tunnels and similar paths to cache route lookups plus source addresses without global contention.

Important APIs/types/functions: `struct dst_cache` stores a per-CPU `dst_cache_pcpu` pointer and a `reset_ts` invalidation timestamp. APIs include `dst_cache_get()`, `dst_cache_get_ip4()`, `dst_cache_set_ip4()`, optional IPv6 `dst_cache_set_ip6()` and `dst_cache_get_ip6()`, `dst_cache_reset()`, `dst_cache_reset_now()`, `dst_cache_init()`, and `dst_cache_destroy()`.

Control flow: a caller initializes the cache, disables local BH, attempts a per-CPU `dst_cache_get*()`, performs a route lookup on miss, then stores the result with `dst_cache_set*()`. `dst_cache_reset()` lazily invalidates entries by updating `reset_ts`; the next per-CPU access drops stale dsts. `dst_cache_reset_now()` frees entries immediately when the caller guarantees no concurrent users.

State and persistence: per-CPU cache entries hold dst references and optional IPv4/IPv6 source addresses. `reset_ts` provides lazy global invalidation. State is runtime only and must be destroyed on owner teardown.

Dependencies and integration points: depends on jiffies, dst entries, IPv4 rtables, optional IPv6 fib types, local BH discipline, and tunnel metadata (`ip_tunnel_info` embeds a dst cache).

Risks: callers must disable local BH around get/set. Immediate reset/destroy require no concurrent users. Forgetting destroy leaks dst references/per-CPU memory. IPv6 APIs are config gated. Cached dsts must be invalidated when route-affecting metadata changes.

Test signals: cache hit/miss for IPv4 and IPv6, local-BH assertions or lockdep coverage, lazy reset freeing on next access, immediate reset with no users, destroy leak checks, route change invalidation, and tunnel transmit performance/regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_metadata.h -->
# sources/distributed-fs/ceph-client/include/net/dst_metadata.h

Read `sources/distributed-fs/ceph-client/include/net/dst_metadata.h` completely for this pass (280 lines, 6779 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_metadata.h_research.md`.

Purpose: defines metadata destinations used to attach non-routing metadata to skbs, especially tunnel receive/transmit metadata, hardware port mux information, MACsec SCI data, and XFRM lwtunnel metadata.

Important APIs/types/functions: `enum metadata_type` distinguishes IP tunnel, hardware port mux, MACsec, and XFRM metadata. `struct metadata_dst` embeds a `dst_entry` flagged with `DST_METADATA` and a union of `ip_tunnel_info`, `hw_port_info`, `macsec_info`, or `xfrm_md_info`. Helpers include `skb_metadata_dst()`, `skb_tunnel_info()`, `lwt_xfrm_info()`, `skb_xfrm_md_info()`, `skb_valid_dst()`, `skb_metadata_dst_cmp()`, `metadata_dst_alloc/free`, per-CPU alloc/free, `tun_rx_dst()`, `tun_dst_unclone()`, `skb_tunnel_info_unclone()`, IPv4 `__ip_tun_set_dst()`/`ip_tun_rx_dst()`, and IPv6 `__ipv6_tun_set_dst()`/`ipv6_tun_rx_dst()`.

Control flow: tunnel receive paths allocate a metadata dst, initialize tunnel key fields from the outer IPv4/IPv6 header and tunnel flags/id, attach it to the skb, and pass the decapsulated packet onward. Transmit/external-mode tunnel paths retrieve metadata via `skb_tunnel_info()`. If a metadata dst must be modified, `tun_dst_unclone()` copies tunnel info, reinitializes embedded dst cache if present, replaces skb dst, and drops the old dst. Comparison helpers let flow paths decide whether two skbs carry identical metadata.

State and persistence: metadata dsts are per-skb transient dst objects. They may include embedded `dst_cache` state inside `ip_tunnel_info`, tunnel options of variable length, XFRM original dst pointers, or device pointers. They persist only while referenced by the skb or per-CPU metadata allocation.

Dependencies and integration points: depends on skbuff dst handling, IP/IPv6 header helpers, tunnel key APIs, MACsec SCI types, `dst.h`, optional `CONFIG_DST_CACHE`, and lwtunnel state. It is central to collect-metadata tunnels, OVS/TC tunnel offloads, MACsec, and XFRM lwtunnel paths.

Risks: `skb_valid_dst()` deliberately rejects metadata dsts as real routes. `skb_metadata_dst_cmp()` assumes both skb dsts are metadata when present and compares variable tunnel options by `options_len`. Unclone must preserve and reinitialize embedded dst cache correctly. Tunnel allocation is GFP_ATOMIC and can fail under pressure. Metadata dsts are not route dsts; passing them to normal output as routes is wrong.

Test signals: IPv4/IPv6 tunnel metadata allocation from outer headers, DF flag propagation, tunnel option compare, unclone with and without dst cache, external-mode tunnel transmit requiring metadata, MACsec/XFRM metadata retrieval, invalid metadata type compare, skb dst replacement/refcount tests, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_ops.h -->
# sources/distributed-fs/ceph-client/include/net/dst_ops.h

Read `sources/distributed-fs/ceph-client/include/net/dst_ops.h` completely for this pass (73 lines, 2116 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_ops.h_research.md`.

Purpose: declares the protocol-specific operation table backing `dst_entry` objects and small helpers for per-protocol destination cache accounting.

Important APIs/types/functions: `struct dst_ops` contains address family, GC threshold, callbacks for GC, route validation, default advertised MSS, MTU, metrics copy-on-write, destroy, device ifdown, negative advice, link failure, PMTU update, redirect, local output, neighbor lookup, neighbor confirmation, the dst slab cache, and a per-CPU entry counter. Helpers are `dst_entries_get_fast()`, `dst_entries_get_slow()`, `dst_entries_add()`, `dst_entries_init()`, `dst_entries_destroy()`, plus `DST_PERCPU_COUNTER_BATCH`.

Control flow: IPv4, IPv6, blackhole, and other route implementations fill a `dst_ops` table. Generic dst code delegates route validation, output properties, metrics COW, teardown, PMTU, redirect, and neighbor lookup through these callbacks. Allocation/destruction paths update the per-CPU entry counter.

State and persistence: `dst_ops` instances are usually per protocol/netns static or long-lived runtime objects. The per-CPU counter tracks approximate/summed live dst entries; the kmem cache pointer owns allocation backing.

Dependencies and integration points: depends on percpu counters, cache alignment, netdevice, skb, sock, and net namespace types. It is paired with `dst.h` and IPv4/IPv6 route implementations.

Risks: missing callbacks can crash callers that do not null-check, while optional callbacks must be checked by helpers. Counter initialization/destruction must match netns/protocol lifecycle. `dst_entries_get_fast()` is approximate; policy decisions requiring exact counts should use the slow sum. Callback semantics must match protocol expectations for PMTU/redirect/neigh lookup.

Test signals: protocol route allocation/destruction counter tests, callback coverage for IPv4/IPv6/blackhole dsts, GC threshold behavior, metrics COW, PMTU/redirect callbacks, neighbor lookup error normalization, and netns teardown with percpu counter destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/dst_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/eee.h -->
# sources/distributed-fs/ceph-client/include/net/eee.h

Read `sources/distributed-fs/ceph-client/include/net/eee.h` completely for this pass (35 lines, 832 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/eee.h_research.md`.

Purpose: defines a small kernel-internal Energy Efficient Ethernet configuration structure and conversion helpers to/from ethtool EEE configuration.

Important APIs/types/functions: `struct eee_config` stores `tx_lpi_timer`, `tx_lpi_enabled`, and `eee_enabled`. `eeecfg_mac_can_tx_lpi()` returns true only when EEE is globally enabled and TX LPI is enabled. `eeecfg_to_eee()` copies internal config to `struct ethtool_keee`; `eee_to_eeecfg()` copies ethtool config back.

Control flow: drivers keep `eee_config` internally, expose it through ethtool get/set paths using the conversion helpers, and use `eeecfg_mac_can_tx_lpi()` to decide whether MAC low-power idle transmission may be enabled.

State and persistence: the structure is runtime driver configuration; hardware or firmware may persist equivalent settings separately. This header has no storage.

Dependencies and integration points: depends on Linux types and ethtool EEE structures. It is used by Ethernet drivers, phylink/PHY EEE paths, and DSA switch EEE support.

Risks: `eee_enabled` is the master switch; enabling TX LPI alone is insufficient. Helpers copy only three fields, so drivers must manage advertised/supported/link-partner EEE state elsewhere. Missing include context for `struct ethtool_keee` relies on users including ethtool headers.

Test signals: ethtool EEE get/set round trips, MAC TX LPI gating, disabled master with TX LPI enabled, DSA/PHY EEE propagation, and driver suspend/resume preserving EEE config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/eee.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/erspan.h -->
# sources/distributed-fs/ceph-client/include/net/erspan.h

Read `sources/distributed-fs/ceph-client/include/net/erspan.h` completely for this pass (321 lines, 9251 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/erspan.h_research.md`.

Purpose: implements ERSPAN header constants and inline builders for GRE-encapsulated mirrored packets, covering Type II/version 1 and Type III/version 2 ERSPAN metadata.

Important APIs/types/functions: constants define ERSPAN versions, masks for VLAN/COS/encapsulation/session/index and v2 SGT/P/FT/HWID/DIR/GRA/O fields, metadata sizes, and offsets. `enum erspan_encap_type` describes original encapsulation. `struct erspan_base_hdr` is bitfield-packed for endian-specific base header layout. Helpers include `set_session_id()`, `get_session_id()`, `set_vlan()`, `get_vlan()`, `set_hwid()`, `get_hwid()`, `erspan_hdr_len()`, `tos_to_cos()`, `erspan_build_header()`, `erspan_get_timestamp()`, `enum erspan_bso`, `erspan_detect_bso()`, and `erspan_build_header_v2()`.

Control flow: tunnel/mirroring transmit code reserves and pushes ERSPAN metadata before the mirrored Ethernet frame. Version 1 builder derives COS from outer IP TOS/traffic class, detects 802.1Q in-frame VLAN preservation, sets session ID and truncation bit, and writes the 20-bit index. Version 2 builder similarly sets base fields, detects short/oversized BSO, writes timestamp in 100-usec granularity, SGT/P/FT/direction/granularity/O fields, and HWID. Header length helper tells GRE/tunnel code how much metadata follows.

State and persistence: no stored state. Builders mutate skb headroom in-place and encode current wall-clock timestamp for v2 metadata. Session ID, index, direction, hwid, and truncation are caller-provided.

Dependencies and integration points: depends on IP/IPv6/skbuff helpers, Ethernet/VLAN header layout, ktime, byteorder bitfields, and UAPI `linux/erspan.h` for `struct erspan_md2`. Integrates with GRE/ERSPAN tunnel devices, TC mirred/sample, and packet capture/monitoring systems.

Risks: bitfield layout is endian-sensitive. Builders assume enough skb headroom and that `skb->data` points at the mirrored Ethernet frame before push. Version 1 and 2 metadata sizes differ. VLAN detection only checks 802.1Q EtherType at the expected position. Timestamp wraps in about four days. BSO cannot detect bad FCS/alignment because FCS is absent from skb data.

Test signals: packet capture decode for ERSPAN v1/v2, endian build checks, VLAN and non-VLAN mirrored frames, IPv4/IPv6 COS derivation, session/VLAN/HWID round trips, truncation and direction bits, short/oversized BSO classification, timestamp granularity/wrap behavior, and skb headroom failure tests in tunnel code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/erspan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/esp.h -->
# sources/distributed-fs/ceph-client/include/net/esp.h

Read `sources/distributed-fs/ceph-client/include/net/esp.h` completely for this pass (50 lines, 1209 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/esp.h_research.md`.

Purpose: declares shared ESP/IPsec helpers and per-packet output state for IPv4 and IPv6 ESP processing.

Important APIs/types/functions: `ip_esp_hdr()` returns the ESP header at the skb transport header. `esp_output_fill_trailer()` fills optional traffic-flow-confidentiality padding, ESP padding bytes 1..N, pad length, and next-header protocol. `struct esp_info` carries ESP header pointer, 64-bit sequence number, TFC length, tail length, padding length, crypto length, total length, fragment count, next protocol, and in-place crypto flag. Function prototypes cover `esp_output_head()`, `esp_output_tail()`, `esp_input_done2()`, and IPv6 variants `esp6_output_head()`, `esp6_output_tail()`, `esp6_input_done2()`.

Control flow: XFRM ESP output prepares `esp_info`, builds head/tail space, fills trailers, performs encryption/authentication, and finalizes skb output. Input async completion paths call `esp_input_done2()`/`esp6_input_done2()` after crypto processing. The same state shape supports IPv4 and IPv6 ESP implementations.

State and persistence: `esp_info` is per-packet transient state. `esp_output_fill_trailer()` mutates skb tailroom. Persistent IPsec SA state lives in `struct xfrm_state`, not in this header.

Dependencies and integration points: depends on skbuffs, ESP wire header declarations, and XFRM state. It integrates with IPv4/IPv6 ESP modules, crypto API callbacks, NAT-T/tunnel paths, and IPsec sequence/TFC/padding handling.

Risks: trailer filling assumes `plen >= 2` and enough writable tailroom. Padding bytes and pad length must match ESP RFC expectations. In-place versus non-in-place crypto affects skb fragment handling. Sequence number and TFC lengths must match XFRM/SA state or peers reject packets.

Test signals: IPv4/IPv6 ESP tunnel and transport mode, padding length boundaries, TFC padding, async crypto completion, fragmented skb handling, in-place/non-in-place paths, sequence number encoding, decryption/authentication failure handling, and interop with strongSwan/libreswan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/esp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/espintcp.h -->
# sources/distributed-fs/ceph-client/include/net/espintcp.h

Read `sources/distributed-fs/ceph-client/include/net/espintcp.h` completely for this pass (40 lines, 972 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/espintcp.h_research.md`.

Purpose: declares the ESP-in-TCP upper-layer protocol context and queueing APIs used to carry ESP/IKE traffic over TCP.

Important APIs/types/functions: initialization/API functions are `espintcp_init()`, `espintcp_push_skb()`, `espintcp_queue_out()`, and `tcp_is_ulp_esp()`. `struct espintcp_msg` tracks an skb, `sk_msg`, offset, and length for partial transmission. `struct espintcp_ctx` embeds a `strparser`, IKE and output skb queues, current partial message, saved socket callbacks (`data_ready`, `write_space`, `destruct`), work item, and `tx_running` flag. `espintcp_getctx()` retrieves the context from `inet_csk(sk)->icsk_ulp_data`.

Control flow: init registers the ULP. When a TCP socket uses ESP ULP, receive data is parsed by strparser and queued as IKE/ESP records; transmit paths queue skbs or partial sk_msgs and schedule work while preserving original socket callbacks for chaining/restoration. `tcp_is_ulp_esp()` lets callers detect sockets using this ULP.

State and persistence: per-socket `espintcp_ctx` persists while the ULP is attached. It owns receive/output queues, partial send progress, saved callbacks, and worker state. No durable state exists beyond socket lifetime.

Dependencies and integration points: depends on TCP inet connection sockets, strparser, skmsg, skbuff queues, workqueues, ESP/IPsec users, and diagnostic paths that may read `icsk_ulp_data` under RCU.

Risks: socket callback save/restore and ULP data lifetime are race-prone. Partial sk_msg progress must be resumed correctly after backpressure. Queue ordering between IKE and ESP data matters. `espintcp_getctx()` trusts the socket has the ESP ULP; callers must check. Comments note RCU is only needed for diag, so normal paths depend on socket locking/ownership.

Test signals: attach/detach ULP, IKE and ESP record receive parsing, transmit queueing under write-space backpressure, partial message resume, callback restoration on close, `tcp_is_ulp_esp()` detection, concurrent diag reads, and IPsec NAT/firewall traversal interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/espintcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ethoc.h -->
# sources/distributed-fs/ceph-client/include/net/ethoc.h

Read `sources/distributed-fs/ceph-client/include/net/ethoc.h` completely for this pass (23 lines, 439 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/ethoc.h_research.md`.

Purpose: defines platform data for the OpenCores Ethernet MAC driver.

Important APIs/types/functions: `struct ethoc_platform_data` contains a hardware MAC address array `hwaddr`, signed `phy_id`, Ethernet clock frequency `eth_clkfreq`, and `big_endian` flag.

Control flow: board/platform code supplies this structure to the ethoc driver at probe. The driver uses the MAC address, PHY identifier, bus clock, and endian mode to initialize registers and PHY attachment.

State and persistence: platform data is static or firmware-derived configuration that persists for the device lifetime. The header has no runtime logic.

Dependencies and integration points: depends on `linux/if.h` and basic types. It integrates platform device registration with the ethoc network driver.

Risks: wrong endianness or clock frequency prevents register access/timing from working. Invalid `phy_id` can bind the wrong PHY or fail link setup. MAC address validation is the driver's responsibility.

Test signals: platform probe with fixed MAC/PHY/clock values, big-endian and little-endian register access, invalid/missing MAC fallback, PHY attach/link tests, and device-tree/platform-data compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/ethoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/failover.h -->
# sources/distributed-fs/ceph-client/include/net/failover.h

Read `sources/distributed-fs/ceph-client/include/net/failover.h` completely for this pass (37 lines, 1210 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/failover.h_research.md`.

Purpose: declares the generic netdevice failover coordination API used by master failover devices to manage standby/primary slave netdevices.

Important APIs/types/functions: `struct failover_ops` contains callbacks for slave pre-register/register/pre-unregister/unregister, slave link/name changes, and RX frame handling. `struct failover` stores list membership, RCU pointer to the failover netdev with tracker, and RCU pointer to ops. APIs are `failover_register()`, `failover_unregister()`, and `failover_slave_unregister()`.

Control flow: a failover master registers with a netdev and ops. As matching slave devices appear, change link state, change names, receive frames, or unregister, the failover core calls the relevant callbacks so the master can bind/unbind and route traffic. Unregister tears down the relationship and trackers.

State and persistence: runtime state includes registered failover instances, RCU-protected master device pointer, ops pointer, and netdevice tracker. No durable state is stored.

Dependencies and integration points: depends on netdevice, RCU conventions, RX handlers, and users such as netvsc/virtio-net failover patterns.

Risks: slave/master lifetime and RCU pointer dereference must be synchronized. Callback failures in pre-register paths must roll back cleanly. RX handler must return correct `rx_handler_result_t`. Name/link-change ordering can race with unregister.

Test signals: register/unregister master, hotplug slaves, pre-register failure rollback, slave link/name changes, RX handler forwarding/consume/pass behavior, concurrent slave unregister, and netdevice tracker leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/failover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fib_notifier.h -->
# sources/distributed-fs/ceph-client/include/net/fib_notifier.h

Read `sources/distributed-fs/ceph-client/include/net/fib_notifier.h` completely for this pass (51 lines, 1390 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/fib_notifier.h_research.md`.

Purpose: declares the FIB notifier API used to publish route, rule, nexthop, and multicast VIF changes to listeners per network namespace and address family.

Important APIs/types/functions: `struct fib_notifier_info` carries address family and extack pointer. `enum fib_event_type` includes entry replace/append/add/delete, rule add/delete, nexthop add/delete, and VIF add/delete. `struct fib_notifier_ops` registers family-specific sequence read and full dump callbacks plus module owner and RCU node. APIs include `call_fib_notifier()`, `call_fib_notifiers()`, `register_fib_notifier()`, `unregister_fib_notifier()`, `fib_notifier_ops_register()`, and `fib_notifier_ops_unregister()`.

Control flow: route/rule/nexthop code emits events through `call_fib_notifiers()`. Listeners register notifier blocks and may request an initial dump through family-specific `fib_dump()` when registering. Sequence reads let consumers detect missed updates and resync.

State and persistence: notifier blocks and `fib_notifier_ops` registrations are runtime per-netns/family state protected by notifier and RCU mechanisms. No route state is stored here; it references FIB state owned elsewhere.

Dependencies and integration points: depends on notifier chains, net namespaces, modules, RCU, netlink extack, IPv4/IPv6 FIB/rules/nexthop/multicast code, and offload consumers such as switchdev/driver route offload.

Risks: listeners must handle missed events and dump/resync correctly. Module owner lifetime matters for `fib_notifier_ops`. Event payloads extend `fib_notifier_info` by embedding, so consumers must cast based on event/family. Registration error extacks must be propagated.

Test signals: route/rule/nexthop add/delete event delivery, initial dump during registration, sequence mismatch resync, unregister during concurrent events, module unload safety, extack on dump/register errors, and per-netns isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fib_notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fib_rules.h -->
# sources/distributed-fs/ceph-client/include/net/fib_rules.h

Read `sources/distributed-fs/ceph-client/include/net/fib_rules.h` completely for this pass (225 lines, 6137 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/fib_rules.h_research.md`.

Purpose: declares the generic policy routing rule framework used by IPv4/IPv6 and other families to match flows against ordered rules and dispatch lookups to routing tables.

Important APIs/types/functions: `struct fib_rule` stores match keys and action state: iif/oif indexes/names, mark/mask, flags, table/action/l3mdev/proto/ip_proto, goto target/ctarget, tunnel ID, netns, refcount, priority, suppressors, UID range, sport/dport ranges and masks, L3 master flags, and RCU node. `struct fib_lookup_arg` carries family lookup callbacks/results/rule/table/flags. `struct fib_rules_ops` is the family operation table for action, suppress, match, configure, delete, compare, fill, nlmsg payload, flush cache, rules list, owner, netns, and sequence. Helpers cover refcounting, table extraction with L3 master support, netlink table attr extraction, port range set/inrange/match/valid/compare/is-range, and field-dissect requirement detection. APIs include register/unregister, `fib_rules_lookup()`, default rule add, match-all test, dump/seq read, newrule/delrule netlink handlers, and indirect-call declarations for IPv4/IPv6 actions/matches/suppressors.

Control flow: families register `fib_rules_ops` per netns. Netlink rule add/delete creates or removes ordered `fib_rule` objects and flushes route cache. Lookup iterates rules in priority order, matching flow keys and optional dissected ports, performing actions/gotos/table lookups through family callbacks, and applying suppressors. Notifier integration reports rule changes.

State and persistence: rule lists, unresolved goto counts, sequence counters, and per-rule refs are runtime netns state. Rules are configured by userspace and persist until netns teardown or deletion, but are not stored by this header.

Dependencies and integration points: depends on fib_rules UAPI, netdevice, flow keys/dissection, rtnetlink, fib_notifier, refcount/RCU, indirect call wrappers, IPv4/IPv6 rule implementations, VRF/L3 master support, and route cache flushing.

Risks: port range matching combines masks and ranges; invalid zero/0xffff ranges must be rejected. Flow dissection is required only for non-loopback rules with ip_proto or ports; missing dissection can skip intended matches. Goto rules and unresolved targets can create loops or stale ctargets if not managed. Refcount/RCU teardown must be exact. L3 master table selection differs by config.

Test signals: add/delete/dump rules with priorities, tables, marks, iif/oif, UID range, tunnel ID, ip_proto, sport/dport ranges and masks; goto target resolution; suppress prefix/interface rules; L3 master/VRF behavior; route cache flush; notifier events; IPv4/IPv6 indirect action/match paths; invalid netlink attrs and extack messages; concurrent lookup/delete RCU tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/fib_rules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/firewire.h -->
# sources/distributed-fs/ceph-client/include/net/firewire.h

Read `sources/distributed-fs/ceph-client/include/net/firewire.h` completely for this pass (27 lines, 599 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/firewire.h_research.md`.

Purpose: defines pseudo link-layer address and header formats for IP over IEEE 1394 FireWire networking.

Important APIs/types/functions: `FWNET_ALEN` is 16 bytes. `union fwnet_hwaddr` exposes raw bytes and an RFC2734/RFC3146 hardware-address layout containing EUI-64 `uniq_id`, max receive size `max_rec`, speed `sspd`, and six-byte FIFO address. `FWNET_HLEN` is 18 bytes. `struct fwnet_header` contains a 16-byte destination pseudo address and 16-bit protocol field.

Control flow: FireWire network code uses the pseudo hardware address for neighbor/ARP-like addressing and emits/parses `fwnet_header` before the network-layer payload.

State and persistence: no state is stored. The address values are per-node/interface runtime identifiers derived from FireWire bus properties.

Dependencies and integration points: depends only on Linux integer types. It integrates with the FireWire net driver, RFC2734 IPv4-over-1394, RFC3146 IPv6-over-1394, and generic netdevice header/address handling.

Risks: packed layout and big-endian fields are wire ABI. The pseudo address is not an Ethernet MAC and must not be treated as 6 bytes. FIFO/speed/max_rec values must match FireWire node capabilities.

Test signals: FireWire net header encode/decode, address length reporting, IPv4/IPv6 over 1394 interop, endian checks for EUI-64/protocol field, MTU/max_rec handling, and neighbor resolution with 16-byte addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/firewire.h -->
