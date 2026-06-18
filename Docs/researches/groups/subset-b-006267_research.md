# subset-b-006267 net/sched action research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_mark.c -->
# sources/distributed-fs/ceph-client/net/sched/act_meta_mark.c

## Purpose

`act_meta_mark.c` registers the IFE metadata handler for `skb->mark`. It lets the `ife` tc action carry a packet mark across an Inter-FE encapsulation and restore it on decode.

## Important APIs, types, and functions

The file is built around one `struct tcf_meta_ops`, `ife_skbmark_ops`, with `metaid = IFE_META_SKBMARK`, `metatype = NLA_U32`, and user-facing name `skbmark`. `skbmark_encode()` reads `skb->mark` and delegates wire formatting to `ife_encode_meta_u32()`. `skbmark_decode()` reads a network-order 32-bit value and writes `skb->mark`. `skbmark_check()` delegates optional presence/value checks to `ife_check_meta_u32()`. Module init and exit call `register_ife_op()` and `unregister_ife_op()`.

## Control flow

When an IFE action is configured to export this metadata, the core IFE code invokes `check_presence`, then `encode`, and later `decode` on a receiving endpoint. The module itself has no packet scheduling decision; it is a metadata codec plugged into the IFE action registry.

## State and persistence

Persistent state is only the registered `tcf_meta_ops` module object. Per-packet state is the `skb->mark` value and the temporary encoded metadata payload supplied by the IFE core. There is no per-net IDR, RCU parameter block, or durable configuration in this file.

## Dependencies and integration points

It depends on `net/tc_act/tc_ife.h` helpers for allocation, validation, encode/decode support, and module aliasing through `MODULE_ALIAS_IFE_META("skbmark")`. Integration is with the tc `ife` action and consumers that classify, route, firewall, or policy-route based on `skb->mark`.

## Risks and edge cases

The decode path assumes the IFE core has validated the metadata length and alignment before handing `data` to the codec. Endianness is the primary correctness detail: encoded values are interpreted in network order with `ntohl()`. Regressions can silently alter downstream policy decisions because `skb->mark` is widely reused by netfilter, routing, and tc classifiers.

## Test signals

Useful coverage is `tc action ife encode type skbmark` paired with decode on another interface, checking that `skb->mark` survives encapsulation. Negative tests should cover invalid metadata length through the IFE core, module autoload via the `skbmark` alias, and filter behavior that proves the restored mark is visible to later tc or netfilter rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_skbprio.c -->
# sources/distributed-fs/ceph-client/net/sched/act_meta_skbprio.c

## Purpose

`act_meta_skbprio.c` is the IFE metadata codec for `skb->priority`. It allows traffic-control priority metadata to be exported in an IFE frame and restored on the receiving path.

## Important APIs, types, and functions

`ife_prio_ops` is the registered `struct tcf_meta_ops` with `metaid = IFE_META_PRIO`, `metatype = NLA_U32`, and name `skbprio`. `skbprio_check()` uses `ife_check_meta_u32()`, `skbprio_encode()` serializes `skb->priority` through `ife_encode_meta_u32()`, and `skbprio_decode()` writes the network-order decoded value back to `skb->priority`. The module entry points are `ifeprio_init_module()` and `ifeprio_cleanup_module()`.

## Control flow

The module participates only when the IFE action asks for `skbprio` metadata. The IFE core owns netlink parsing, metadata buffer allocation, and packet encapsulation; this file supplies the priority-specific get/check/encode/decode callbacks.

## State and persistence

There is no action instance state here. The only persistent kernel object is the globally registered metadata operations table. Runtime state is the per-packet `skb->priority`, which commonly feeds qdisc class selection and socket priority behavior after decode.

## Dependencies and integration points

The module depends on common IFE helpers from `net/tc_act/tc_ife.h` and the tc action UAPI IDs from `tc_ife.h`. It integrates with the qdisc/classifier stack through the meaning of `skb->priority`; any later classful qdisc, filter, or socket-priority logic observes the restored value.

## Risks and edge cases

The ops table omits explicit `.release` and `.validate` callbacks unlike the mark and tc_index codecs, relying on generic u32 helper behavior through `.alloc` and `.get`. The data path is small, but wrong byte order or accepting malformed metadata would cause priority/class selection drift that may be hard to detect except by observing queue placement.

## Test signals

Validate module autoload with the `skbprio` IFE metadata alias and use tc filters before and after an IFE hop to prove priority preservation. Tests should exercise zero and nonzero priorities, classful qdisc selection from restored priority, and malformed metadata rejection in the shared IFE parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_skbprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_skbtcindex.c -->
# sources/distributed-fs/ceph-client/net/sched/act_meta_skbtcindex.c

## Purpose

`act_meta_skbtcindex.c` provides the IFE metadata codec for `skb->tc_index`. It preserves the legacy tc index/classification field across IFE encapsulation.

## Important APIs, types, and functions

`ife_skbtcindex_ops` registers `metaid = IFE_META_TCINDEX`, `metatype = NLA_U16`, name `tc_index`, and alias `tcindex`. `skbtcindex_encode()` reads `skb->tc_index` and encodes it with `ife_encode_meta_u16()`. `skbtcindex_decode()` stores an `ntohs()` decoded value back into `skb->tc_index`. `skbtcindex_check()` delegates presence checks to `ife_check_meta_u16()`.

## Control flow

The IFE action core selects this codec when configured for tc index metadata. Encode runs before the IFE frame is emitted; decode runs after metadata parsing on the receiving side and mutates the skb field for subsequent tc processing.

## State and persistence

The module owns only the registered `tcf_meta_ops`. The persistent packet metadata is carried externally in the IFE payload; after decode, state is just the 16-bit `skb->tc_index` value. No per-action parameters or per-net namespaces are allocated here.

## Dependencies and integration points

It uses the common IFE u16 helper set and participates in the tc action module registry. The restored value integrates with filters and legacy classifiers that still inspect `skb->tc_index`.

## Risks and edge cases

The encoder casts the field through a local `u32` while using u16 IFE helpers; correctness depends on the helper truncating/validating according to the u16 metadata type. As with the other metadata codecs, malformed payload length must be rejected by shared IFE validation before `decode` dereferences `data`.

## Test signals

Configure IFE metadata `tcindex`, send packets with a known `tc_index`, and confirm a receiver-side classifier sees the restored value. Include values near the 16-bit boundary, metadata omission cases, and module autoload by alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_meta_skbtcindex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_mirred.c -->
# sources/distributed-fs/ceph-client/net/sched/act_mirred.c

## Purpose

`act_mirred.c` implements the tc `mirred` action: packet mirror or redirect to another netdevice or to all ports in a tc block. It supports egress and ingress targets and maps software actions to hardware offload `FLOW_ACTION_*` entries.

## Important APIs, types, and functions

The main action ops object is `act_mirred_ops`. `tcf_mirred_init()` parses `TCA_MIRRED_PARMS` and optional `TCA_MIRRED_BLOCKID`, validates egress/ingress mirror/redirect modes, allocates or replaces the action in the per-net IDR, and stores either an RCU-protected target `net_device` or a block id. `tcf_mirred_act()` is the hot path. `tcf_mirred_to_dev()` handles cloning, loop checks, MAC/network header positioning, netfilter conntrack reset, `skb_iif` updates, and forwarding through `dev_queue_xmit()`, `netif_rx()`, or `netif_receive_skb()`. `tcf_blockcast_*()` fan out to block ports. `mirred_device_event()` clears target devices on unregister. `tcf_mirred_offload_act_setup()` maps modes to redirect/mirror flow actions.

## Control flow

Configuration starts with IDR lookup/create, control-action validation, then either `dev_get_by_index()` plus `netdev_tracker_alloc()` or block-id storage. Runtime first updates lastuse and byte stats, checks the per-CPU mirred recursion limit, handles block fanout if configured, otherwise dereferences the target device. Redirects may consume the original skb when called from ingress and the return action permits reinsertion; mirrors clone instead. Header positioning is adjusted because ingress actions expect network-header data while some egress devices expect MAC-header data.

## State and persistence

Each action persists `tcfm_dev`, `tcfm_blockid`, `tcfm_eaction`, `tcfm_mac_header_xmit`, tc common counters, and list membership in the global `mirred_list`. Device lifetime is protected by RCU plus explicit netdev tracking and a notifier that nulls devices on `NETDEV_UNREGISTER`. Recursion state lives in `softnet_data.xmit` or `current->net_xmit` on PREEMPT_RT.

## Dependencies and integration points

It integrates with tc action IDR/per-net registration, tc blocks, netdevice lifecycle notifiers, qdisc transmit/receive helpers, conntrack reset, flow offload, and classifier control actions including goto chains.

## Risks and edge cases

High-risk areas are redirect loops, recursive mirred nesting, stale device references during unregister, block fanout excluding the source ifindex, and correct skb ownership when redirecting without clone. Header push/pull mistakes can corrupt packets or confuse target devices. Down devices, carrier loss, and missing block ports increment overlimit stats rather than always changing the configured control action.

## Test signals

Use tc selftests with egress/ingress mirror and redirect between veth pairs, including same-device loop attempts, blockcast fanout, target device unregister, down target devices, and hardware offload dumps. Packet counters, overlimit/drop qstats, `skb_iif`, conntrack clearing, and observed packet delivery on ingress versus egress are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_mirred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_mpls.c -->
# sources/distributed-fs/ceph-client/net/sched/act_mpls.c

## Purpose

`act_mpls.c` implements tc MPLS manipulation actions: pop, push, MAC push, modify label stack entry fields, and decrement TTL. It also exposes supported actions to flow offload.

## Important APIs, types, and functions

`tcf_mpls_act()` is the packet path. `tcf_mpls_init()` parses `TCA_MPLS_*` netlink attributes, validates action-specific combinations, creates an RCU `tcf_mpls_params`, and installs control action state. `tcf_mpls_get_lse()` composes a new label stack entry from optional label, TTL, traffic class, and BOS fields. `valid_label()` enforces MPLS label bounds and rejects implicit-null. `tcf_mpls_dump()` serializes the current params. `tcf_mpls_offload_act_setup()` maps push/pop/modify to `FLOW_ACTION_MPLS_*` and rejects `dec_ttl` and `mac_push` offload.

## Control flow

Initialization validates different rules per action: pop requires an 802.3 protocol and rejects label/TTL/TC/BOS; push/mac_push require a label and an MPLS ethertype if protocol is supplied; push defaults TTL from `net->mpls.default_ttl` or 255; modify rejects protocol; dec_ttl rejects all field attributes. Runtime temporarily pushes the MAC header for ingress, then calls `skb_mpls_pop()`, `skb_mpls_push()`, `skb_mpls_update_lse()`, or `skb_mpls_dec_ttl()`. Ingress packets are pulled back before returning the configured action.

## State and persistence

The action stores one RCU-replaced `tcf_mpls_params` block with mode, label, ttl, tc, bos, protocol, and control action. Per-net state is standard tc action IDR storage. The module itself has no external durable state, but push default TTL can depend on namespace MPLS settings.

## Dependencies and integration points

It depends on MPLS skb helpers, VLAN helper behavior for `MAC_PUSH` with accelerated VLAN tags, tc action APIs, optional `CONFIG_MPLS`, and flow offload. `MODULE_SOFTDEP("post: mpls_gso")` highlights integration with MPLS segmentation support.

## Risks and edge cases

Header position at ingress, VLAN-tag materialization before `MAC_PUSH`, default TTL selection, BOS auto-setting when pushing onto non-MPLS packets, and unsupported offload modes are the sensitive areas. Packet mutation failures drop with `TC_ACT_SHOT`; callers need to distinguish configured action from mutation failure.

## Test signals

Exercise pop, push, mac_push, modify, and dec_ttl on Ethernet and ingress paths; validate invalid label/protocol combinations; verify default TTL behavior with and without namespace MPLS TTL; inspect tc dumps; and verify offload conversion accepts only push/pop/modify.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_mpls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_nat.c -->
# sources/distributed-fs/ceph-client/net/sched/act_nat.c

## Purpose

`act_nat.c` implements a stateless IPv4 tc NAT action. It rewrites source or destination addresses matching an old-address/mask pair and updates IP, TCP, UDP, and selected ICMP error checksums.

## Important APIs, types, and functions

`tcf_nat_init()` parses `TCA_NAT_PARMS`, allocates or replaces a `struct tcf_nat_parms`, validates the tc control action, and installs params under RCU. `tcf_nat_act()` is the packet path. `tcf_nat_dump()` reports old/new address, mask, flags, and timing. `tcf_nat_cleanup()` frees RCU params.

## Control flow

Runtime reads params, rejects configured `TC_ACT_SHOT`, pulls the IPv4 header, chooses `iph->saddr` for egress mode or `iph->daddr` for ingress mode, and checks `(old_addr ^ addr) & mask`. On match it makes the IP header writable, rewrites only masked bits, and fixes the IPv4 checksum. For TCP and UDP first fragments it updates L4 checksums; for ICMP errors it rewrites the embedded inner address in the reverse direction and updates the ICMP checksum. Nonmatching non-ICMP packets and later fragments pass through unchanged.

## State and persistence

Action state is a single RCU parameter block containing old/new address, mask, flags, and control action. Statistics live in tc common action counters. No connection table is kept; the action is explicitly stateless and cannot remember flows or ports.

## Dependencies and integration points

The code depends on IPv4, TCP, UDP, ICMP, checksum, skb writability, and tc action IDR APIs. It integrates as a software tc action only; there is no `offload_act_setup` in this file.

## Risks and edge cases

It is IPv4-only and only handles L4 checksum updates for TCP/UDP plus ICMP error wrappers. Inner checksums inside ICMP errors are explicitly not fixed beyond the ICMP checksum. Fragment handling is limited, and `skb_try_make_writable()` failures drop. Because no conntrack state exists, reverse-path consistency must be supplied by symmetric tc rules.

## Test signals

Use IPv4 TCP, UDP with zero and nonzero checksums, ICMP errors, unmatched prefixes, fragments, ingress versus egress flags, and non-linear skbs. Verify address rewrite masks, checksums, drops on insufficient writable data, and tc dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_nat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_pedit.c -->
# sources/distributed-fs/ceph-client/net/sched/act_pedit.c

## Purpose

`act_pedit.c` is the generic packet editor tc action. It applies one or more 32-bit masked writes or additions at fixed or computed offsets in Ethernet, network, IPv4, IPv6, TCP, or UDP headers.

## Important APIs, types, and functions

`tcf_pedit_init()` parses legacy and extended `TCA_PEDIT_*` attributes, validates key counts and offsets, copies `tc_pedit_key` arrays, parses optional extended key metadata with `tcf_pedit_keys_ex_parse()`, and RCU-installs `tcf_pedit_parms`. `tcf_pedit_act()` applies edits. `pedit_skb_hdr_offset()` and `pedit_l4_skb_offset()` locate selected headers, using `ipv6_find_hdr()` for IPv6 L4 offsets. `offset_valid()` bounds positive offsets against skb length and negative offsets against headroom. `tcf_pedit_offload_act_setup()` converts keys to `FLOW_ACTION_MANGLE` or `FLOW_ACTION_ADD`.

## Control flow

At init, every key is checked for 32-bit alignment unless it has an `offmask`; shifts are clamped; and a maximum offset hint is computed to preflight writability. Runtime ensures the relevant skb region is writable, then for each key resolves the base header, optionally reads an `at` byte to adjust the offset, validates bounds and alignment, reads a 32-bit word through `skb_header_pointer()`, computes either a SET or ADD value, applies the mask expression, and writes back with `skb_store_bits()` when using a scratch buffer.

## State and persistence

Persistent action state is an RCU parameter block with flags, key count, offset hint, key arrays, optional extended key array, and control action. Old parameter blocks are freed by `tcf_pedit_cleanup_rcu()`. Stats use the tc common action counters; bad edits increment overlimit qstats but return the configured action.

## Dependencies and integration points

It integrates with tc action IDR, classifier control actions, IPv4/IPv6 header parsing, skb non-linear access helpers, and flow offload. Extended keys are part of the tc UAPI for hardware-aware pedit actions.

## Risks and edge cases

Computed offsets, negative offsets into headroom, IPv6 extension-header traversal, non-linear skb writes, and mixed command offload validation are the main risks. The action does not recalculate protocol checksums after arbitrary edits; users must combine it with checksum-aware actions or edit fields where checksums are irrelevant.

## Test signals

Exercise legacy and extended keys, SET and ADD commands, Ethernet/network/TCP/UDP header bases, IPv6 extension headers, offmask/at computed offsets, invalid alignment, non-linear skbs, dump round trips, and offload rejection for mixed commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_pedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_police.c -->
# sources/distributed-fs/ceph-client/net/sched/act_police.c

## Purpose

`act_police.c` implements the tc policing action. It enforces MTU, byte-per-second, peak-rate, packet-per-second, and estimator-based average-rate limits, returning different control actions for conforming and exceeding traffic.

## Important APIs, types, and functions

`tcf_police_init()` parses `TCA_POLICE_*`, handles rate tables and 64-bit rate attributes, installs estimators, validates fallback actions, initializes token state, and RCU-replaces `tcf_police_params`. `tcf_police_act()` performs MTU and token-bucket checks. `tcf_police_mtu_check()` handles GSO-aware length validation. `tcf_police_act_to_flow_act()` and `tcf_police_offload_act_setup()` translate policing configuration to `FLOW_ACTION_POLICE`. Dump and stats hooks serialize rates, bursts, pps fields, and estimator settings.

## Control flow

Initialization supports byte-rate/peak-rate policers or packet-per-second policers, but rejects mixing pps and byte rate in one action. Runtime first updates stats, checks EWMA average rate if configured, then validates MTU. If no rate limiter is present, conforming packets return `tcfp_result`. Otherwise it computes elapsed nanoseconds, refills normal, peak, or packet tokens under `tcfp_lock`, subtracts packet cost, and returns `tcfp_result` when enough tokens remain. Exceeded packets increment overlimit stats and return the configured exceed action.

## State and persistence

Each action has RCU configuration params plus mutable token state in `tcfp_t_c`, `tcfp_toks`, `tcfp_ptoks`, and `tcfp_pkttoks`, serialized by `tcfp_lock`. Optional rate estimator state is attached to the action's basic stats. Per-net lifecycle is standard tc action storage.

## Dependencies and integration points

It depends on qdisc rate tables, packet scheduler time conversion, GSO validation, generic rate estimators, tc action control-action validation, and flow offload.

## Risks and edge cases

Token arithmetic is timing-sensitive, especially with peak and pps modes. Estimator-only policing requires an active estimator. GSO MTU validation differs from normal packet length. Fallback `goto chain` is forbidden, and offload support depends on conform/exceed action translation. Misconfigured bursts can cause systematic drops or unintended pass-through.

## Test signals

Cover byte-rate, peak-rate, pps, estimator average rate, MTU-only, GSO MTU, conform/exceed actions, invalid mixed pps/byte-rate config, dump round trips, overlimit/drop qstats, and hardware offload translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_police.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_sample.c -->
# sources/distributed-fs/ceph-client/net/sched/act_sample.c

## Purpose

`act_sample.c` implements the tc packet sampling action. It randomly sends selected packets and metadata to the psample subsystem while returning the configured tc control action for the original packet.

## Important APIs, types, and functions

`tcf_sample_init()` parses `TCA_SAMPLE_PARMS`, required sample `RATE`, required `PSAMPLE_GROUP`, and optional truncation size, then obtains a `psample_group` reference and stores it under RCU. `tcf_sample_act()` performs random sampling with `get_random_u32_below()`, builds `psample_metadata`, copies an optional tc user cookie, and calls `psample_sample_packet()`. `tcf_sample_dev_ok_push()` decides whether ingress MAC headers may be temporarily pushed. Offload hooks expose `FLOW_ACTION_SAMPLE` and transfer a psample group reference.

## Control flow

Runtime updates stats and reads the action result. If a psample group exists and the random draw hits, it fills ingress and egress ifindexes depending on tc direction. On ingress for Ethernet-like devices it temporarily pushes the MAC header so psample sees the full frame, copies the action cookie under RCU, sets truncation length, samples the packet, and then restores the skb data pointer.

## State and persistence

Persistent state includes sample rate, psample group number, truncation flag/size, and an RCU-protected `psample_group` reference. Cleanup drops the group reference. Packet cookies are stored in the common tc action and read transiently.

## Dependencies and integration points

The module integrates tc actions with `net/psample`, flow offload, netdevice ARP type checks, tc cookies, and per-net action registration.

## Risks and edge cases

Rate zero is rejected; missing group/rate is invalid. Temporary ingress header push must be balanced, and tunnel/none device types are excluded from that push. Cookie copying is bounded by `TC_COOKIE_MAX_SIZE`. Sampling is probabilistic, so tests must account for randomness or use rate 1.

## Test signals

Use sample rate 1 for deterministic psample events, verify group reference lifecycle, truncation size, user cookie propagation, ingress/egress ifindexes, ingress MAC-header restoration, invalid rate/group handling, and offload conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_simple.c -->
# sources/distributed-fs/ceph-client/net/sched/act_simple.c

## Purpose

`act_simple.c` is a small example tc action. It stores a user string, logs that string with the packet count whenever the action runs, and returns the configured tc control action.

## Important APIs, types, and functions

`tcf_simp_init()` parses `TCA_DEF_PARMS` and required `TCA_DEF_DATA`, allocates or replaces a `tcf_defact`, and validates the control action. `alloc_defdata()` allocates the fixed `SIMP_MAX_DATA` string buffer. `reset_policy()` updates existing actions. `tcf_simp_act()` updates lastuse and basic stats under `tcf_lock`, logs `simple: <data>_<packets>`, and returns `tcf_action`. `tcf_simp_dump()` serializes params, string, and timing.

## Control flow

Create requires a data string and action parameters. Existing actions require replace mode and rewrite the stored policy string under lock. Runtime is intentionally simple: lock, update stats, print, unlock, return.

## State and persistence

State is the common tc action plus a heap-allocated `tcfd_defdata` string of up to 32 bytes. Cleanup frees that string. Unlike many other actions in this group, it does not use RCU parameter replacement.

## Dependencies and integration points

It uses tc action IDR/per-net registration, netlink string parsing, kernel logging, and standard control-action handling. It serves mostly as an example and diagnostic action rather than a performance-focused datapath primitive.

## Risks and edge cases

The hot path takes a spinlock and emits `pr_info()` per packet, so it is unsuitable for high-rate production traffic. Missing data is rejected. Tests should be careful not to depend on unbounded kernel log availability.

## Test signals

Create, replace, dump, and delete the action; confirm the log includes the configured string and monotonically increasing packet count; verify missing `TCA_DEF_DATA` fails and configured control actions are returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_skbedit.c -->
# sources/distributed-fs/ceph-client/net/sched/act_skbedit.c

## Purpose

`act_skbedit.c` edits skb metadata rather than packet bytes. It can set priority, inherit DSCP into priority, choose queue mapping, set mark with a mask, and set packet type.

## Important APIs, types, and functions

`tcf_skbedit_init()` parses `TCA_SKBEDIT_*`, validates selected operations, creates an RCU `tcf_skbedit_params`, and installs control action state. `tcf_skbedit_act()` applies metadata edits. `tcf_skbedit_hash()` distributes queue mapping across a configured range using `skb_get_hash()`. `tcf_skbedit_dump()`, `tcf_skbedit_get_fill_size()`, and `tcf_skbedit_offload_act_setup()` support netlink dump sizing and hardware offload mapping.

## Control flow

Initialization builds a flags mask from supplied attributes and pure flags. Receive-side `queue_mapping` is allowed only for hardware-only use unless skip-sw is set. Hash-based queue ranges require both min and max queue mappings and valid ordering. Runtime updates stats, reads params under RCU, then applies priority, DS field inheritance for IPv4/IPv6, queue mapping with egress txqueue skip, masked mark update, and packet type update. If DS field headers cannot be pulled, the packet is dropped.

## State and persistence

Persistent action state is an RCU params block containing flags, priority, queue mapping/range, mark, mask, packet type, and action. The action also uses common tc stats and optional hardware stats updates.

## Dependencies and integration points

It depends on IP/IPv6 DS field helpers, skb hash and queue mapping APIs, netdevice tx queue limits, tc action infrastructure, and flow offload. It integrates with qdisc queue selection and later classifiers through skb metadata.

## Risks and edge cases

Queue mapping has direction-specific behavior and hardware-only constraints. DS field inheritance requires sufficient network header data and can drop malformed packets. Masked mark writes preserve bits outside the mask. Offload supports only one option shape at a time and rejects transmit queue mapping and inherit-DS-field modes.

## Test signals

Test priority set, IPv4/IPv6 DSCP inheritance, mark/mask writes, packet type validation, queue mapping range hashing, ingress skip-sw validation, dump round trips, and offload mapping/rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_skbedit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_skbmod.c -->
# sources/distributed-fs/ceph-client/net/sched/act_skbmod.c

## Purpose

`act_skbmod.c` modifies packet header data in common skb cases: destination MAC, source MAC, Ethernet type, MAC address swap, or ECN congestion marking.

## Important APIs, types, and functions

`tcf_skbmod_init()` parses `TCA_SKBMOD_*`, derives exactly one supported flag mode, creates an RCU `tcf_skbmod_params`, and installs it. `tcf_skbmod_act()` ensures the editable header area is writable, mutates Ethernet fields or calls `INET_ECN_set_ce()`, and returns the configured action. Dump and cleanup hooks serialize/free params.

## Control flow

Init accepts a combination of DMAC/SMAC/ETYPE, or overrides with `SKBMOD_F_SWAPMAC`, or overrides with `SKBMOD_F_ECN`. Runtime drops immediately if configured action is `TC_ACT_SHOT`. For ECN it accepts IPv4/IPv6 packets and includes network-header length in the writable range; for MAC edits it requires an Ethernet device. After `skb_ensure_writable()`, it performs the selected edits and returns the configured action.

## State and persistence

State is an RCU params block with flags, optional Ethernet addresses, optional ethertype, and control action. Old params are freed after an RCU grace period. No per-packet state is retained beyond changed skb contents.

## Dependencies and integration points

It depends on Ethernet header helpers, ECN helpers, skb writability, tc action registration, and per-net action IDR storage.

## Risks and edge cases

Flag precedence is important: swapmac and ECN replace any attribute-derived MAC/etype combination. MAC operations silently no-op on non-Ethernet devices, while writability failures drop. ECN only operates on IPv4/IPv6 packets; other protocols pass unchanged. There is no flow offload hook in this file.

## Test signals

Exercise each mode, combined DMAC/SMAC/ETYPE, swap precedence, ECN on IPv4/IPv6 and non-IP packets, non-Ethernet devices, non-linear skb writable failure, dump output, and replace semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_skbmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_tunnel_key.c -->
# sources/distributed-fs/ceph-client/net/sched/act_tunnel_key.c

## Purpose

`act_tunnel_key.c` implements tc tunnel metadata actions. It can release tunnel metadata from an skb or attach transmit metadata describing IPv4/IPv6 tunnel endpoints, key id, destination port, checksum/DF flags, TOS/TTL, and Geneve/VXLAN/ERSPAN options.

## Important APIs, types, and functions

`tunnel_key_act()` drops or sets `skb_dst` with metadata dsts. `tunnel_key_init()` parses `TCA_TUNNEL_KEY_*`, validates set/release modes, allocates `metadata_dst` using `__ip_tun_set_dst()` or `__ipv6_tun_set_dst()`, initializes optional dst cache, parses encapsulation options, and installs `tcf_tunnel_key_params` under RCU. Option helpers include `tunnel_key_copy_geneve_opt()`, `tunnel_key_copy_vxlan_opt()`, `tunnel_key_copy_erspan_opt()`, `tunnel_key_copy_opts()`, and `tunnel_key_opts_set()`. Dump helpers serialize addresses and options. `tcf_tunnel_key_offload_act_setup()` maps set/release to tunnel encap/decap flow actions.

## Control flow

For `SET`, init handles optional key id, checksum default-on with `NO_CSUM` override, optional no-frag, dst port, tunnel options length validation, TOS/TTL, and exactly one IPv4 or IPv6 source/destination pair. It then stores options and marks the tunnel info as TX metadata. Runtime for release calls `skb_dst_drop()`. Runtime for set drops the existing dst and installs a clone of the prepared metadata dst.

## State and persistence

Each action persists an RCU params block containing the tcft action, control action, and optional metadata dst. Metadata dsts own dst-cache and tunnel-info option memory; cleanup releases the dst before freeing params. Per-net storage is the normal tc action IDR.

## Dependencies and integration points

It integrates tc actions with tunnel metadata used by tunnel netdevices and flower offload, plus Geneve, VXLAN, ERSPAN, IPv4/IPv6 tunnel info, dst cache, and flow offload.

## Risks and edge cases

The parser must reject mixed or duplicate option types, empty options, oversize Geneve options, invalid ERSPAN version-specific fields, and missing address pairs. Metadata dst lifetime is subtle on error paths and replace paths. `CONFIG_INET` gates option setting. Existing skb dst is always dropped before release or set.

## Test signals

Cover release, IPv4 set, IPv6 set, key id, no-csum, no-frag, dst port, TOS/TTL, Geneve/VXLAN/ERSPAN options, invalid mixed options, dump round trips, dst-cache cleanup, and offload tunnel info copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_tunnel_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_vlan.c -->
# sources/distributed-fs/ceph-client/net/sched/act_vlan.c

## Purpose

`act_vlan.c` implements tc VLAN and Ethernet header manipulation actions: pop VLAN, push VLAN, modify VLAN tag, pop Ethernet header, and push Ethernet header.

## Important APIs, types, and functions

`tcf_vlan_init()` parses `TCA_VLAN_*`, validates action-specific required attributes, creates an RCU `tcf_vlan_params`, and installs control action state. `tcf_vlan_act()` executes skb VLAN/Ethernet helpers. `tcf_vlan_dump()` reports current parameters. `tcf_vlan_offload_act_setup()` maps actions to `FLOW_ACTION_VLAN_*` entries, including push/pop Ethernet.

## Control flow

Init accepts pop without extra fields; push/modify require VLAN ID, validate VID range, default protocol to 802.1Q, and allow only 802.1Q or 802.1AD protocols; push_eth requires source and destination MAC addresses. Runtime pushes the MAC header for ingress before using VLAN helpers. Modify is a no-op if no VLAN tag exists; otherwise it extracts an accelerated or in-payload tag, changes VID and optionally priority, then stores the tag as hardware-accelerated metadata. It restores ingress data position, resets MAC length, and returns the configured action.

## State and persistence

Persistent state is an RCU params block containing VLAN action, VID, priority, priority-exists flag, protocol, optional push_eth MACs, and control action. Stats are common tc action counters. Old params are RCU-freed on replace or cleanup.

## Dependencies and integration points

It depends on Linux VLAN skb helpers, Ethernet push/pop helpers, tc action infrastructure, and flow offload. The action is commonly paired with flower filters and hardware offload drivers.

## Risks and edge cases

Ingress header push/pull must be balanced. Modify behavior differs for accelerated versus in-payload tags and silently no-ops on untagged packets. VLAN ID range and protocol validation protect UAPI misuse. Offload must preserve priority existence semantics, especially for modify.

## Test signals

Test pop, push, modify with and without existing tags, hardware-accelerated tags, push_eth/pop_eth, ingress and egress paths, invalid VID/protocol/missing MACs, dump round trips, qstats on helper failure, and offload action mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/act_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/bpf_qdisc.c -->
# sources/distributed-fs/ceph-client/net/sched/bpf_qdisc.c

## Purpose

`bpf_qdisc.c` exposes `struct Qdisc_ops` as a BPF struct-ops target. It lets BPF programs implement qdisc enqueue, dequeue, init, reset, and destroy callbacks with verifier restrictions, helper kfuncs, prologue/epilogue code, and registration through the normal qdisc registry.

## Important APIs, types, and functions

`bpf_Qdisc_ops` is the `struct bpf_struct_ops` descriptor. `bpf_qdisc_verifier_ops` supplies access checks, BTF struct write rules, and generated prologue/epilogue. `bpf_qdisc_is_valid_access()` gives enqueue programs trusted access to a `bpf_sk_buff_ptr` for `to_free`. `bpf_qdisc_btf_struct_access()` limits writable fields in `Qdisc` and `sk_buff`. Kfuncs include `bpf_skb_get_hash()`, `bpf_kfree_skb()`, `bpf_qdisc_skb_drop()`, `bpf_qdisc_watchdog_schedule()`, `bpf_qdisc_bstats_update()`, plus hidden init/reset/destroy hooks. `bpf_qdisc_init_member()` forces `priv_size`, default `peek`, and validates `id`. `bpf_qdisc_reg()` and `bpf_qdisc_unreg()` call `register_qdisc()` and `unregister_qdisc()`.

## Control flow

Late init registers qdisc kfunc IDs, skb destructor kfuncs, and the BPF struct-ops type. Loading a BPF qdisc validates required callbacks, initializes selected members, and registers a qdisc ops instance. The generated init prologue initializes a `qdisc_watchdog` in BPF private data and rejects unsupported parents except root or mq. Reset/destroy epilogues cancel the watchdog. Kfunc filtering restricts enqueue-only helpers, dequeue-only helpers, and common helpers according to the attached `Qdisc_ops` member.

## State and persistence

The kernel-side private data for each BPF qdisc is `struct bpf_sched_data`, currently a `qdisc_watchdog`. The BPF link pins the registered `Qdisc_ops` lifetime; unregister removes it from the qdisc registry. BPF program-owned queue state lives in BPF maps or qdisc private memory exposed through struct ops, while skb drops may be deferred through the qdisc to-free list.

## Dependencies and integration points

It depends on BPF verifier, BTF IDs, struct_ops, qdisc core, qdisc watchdogs, skb dynptr support, kfunc registration, and qdisc registration APIs. It is an integration point between tc/qdisc scheduling and BPF program lifecycle.

## Risks and edge cases

Verifier access boundaries are critical: only selected `Qdisc` and `sk_buff` fields are writable. Kfunc filtering must prevent enqueue/dequeue helpers in the wrong callback. Prologue/epilogue generation must preserve context registers and guarantee watchdog init/cancel even for BPF implementations. Parent qdisc validation prevents unsupported non-root use, with a special case for mq defaults not yet in the qdisc hash.

## Test signals

Build and load BPF struct-ops qdiscs with all required callbacks, missing callbacks, invalid `priv_size`, invalid ids, root and mq parents, and unsupported parents. Exercise enqueue drop/free helpers, dequeue stats updates, watchdog scheduling/canceling, verifier rejection for disallowed field writes and wrong-context kfuncs, and qdisc unregister through BPF link teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sched/bpf_qdisc.c -->
