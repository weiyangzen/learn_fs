<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/devinet.c -->
# sources/distributed-fs/ceph-client/net/ipv4/devinet.c

## Purpose
`devinet.c` is the IPv4 per-device address and configuration manager. It creates and destroys `struct in_device` objects for netdevices, owns `struct in_ifaddr` IPv4 address lifetime and hash/list membership, implements the IPv4 address rtnetlink and legacy ioctl APIs, exposes IPv4 per-interface sysctl/netconf state, and notifies FIB, ARP, multicast, SCTP, netfilter, and other consumers when addresses or device IPv4 configuration change.

## Important APIs, Types, and Functions
The central state objects are `struct in_device`, its `cnf` `struct ipv4_devconf`, and its `ifa_list` of `struct in_ifaddr`. Per-net state includes `net->ipv4.inet_addr_lst`, `devconf_all`, `devconf_dflt`, `addr_chk_work`, and the IPv4 netconf/sysctl registrations.

Lookup and selection helpers exported to other IPv4 subsystems include `__ip_dev_find()`, `inet_lookup_ifaddr_rcu()`, `inetdev_by_index()`, `inet_ifa_byprefix()`, `inet_select_addr()`, and `inet_confirm_addr()`. Notification APIs are `register_inetaddr_notifier()`, `unregister_inetaddr_notifier()`, `register_inetaddr_validator_notifier()`, and `unregister_inetaddr_validator_notifier()`.

Address mutation is centered on `inet_alloc_ifa()`, `__inet_insert_ifa()`, `__inet_del_ifa()`, `inet_insert_ifa()`, `inet_set_ifa()`, `inet_rtm_newaddr()`, `inet_rtm_deladdr()`, and `devinet_ioctl()`. Rtnetlink serialization is handled by `inet_fill_ifaddr()`, `inet_dump_addr()`, `inet_dump_ifaddr()`, `inet_dump_ifmcaddr()`, and `rtmsg_ifa()`.

Device and namespace lifecycle entry points are `inetdev_init()`, `inetdev_destroy()`, `inetdev_event()`, `devinet_init_net()`, `devinet_exit_net()`, and `devinet_init()`. Configuration exposure is implemented through `inet_fill_link_af()`, `inet_set_link_af()`, `inet_netconf_get_devconf()`, `inet_netconf_dump_devconf()`, `inet_netconf_notify_devconf()`, and, under `CONFIG_SYSCTL`, the `devinet_sysctl` table and handlers such as `devinet_conf_proc()`, `devinet_sysctl_forward()`, and `ipv4_doint_and_flush()`.

## Control Flow
Netdevice registration calls `inetdev_event(NETDEV_REGISTER)`, which allocates an `in_device`, copies default IPv4 configuration, allocates ARP neighbour parameters, registers per-device sysctls, initializes multicast state, and finally publishes `dev->ip_ptr` with RCU. Loopback devices receive `NOXFRM` and `NOPOLICY`, and on `NETDEV_UP` get a host-scope `127.0.0.1/8` address if possible.

Address creation through rtnetlink begins in `inet_rtm_newaddr()`. It validates prefix length and mandatory `IFA_LOCAL`, converts attributes into a new `in_ifaddr`, either inserts it or replaces lifetime/metric/protocol on an existing address, optionally joins IPv4 multicast groups for `IFA_F_MCAUTOJOIN`, and emits `RTM_NEWADDR`. Legacy ioctl changes follow the same lower-level delete/insert path after translating `ifreq` and BSD alias labels.

`__inet_insert_ifa()` strips IPv6-only flags, determines primary versus secondary status by mask and prefix, calls validator notifiers before committing, links the address into `in_dev->ifa_list`, inserts it into the per-net address hash, schedules lifetime checking, sends rtnetlink notification, and then calls the blocking address notifier chain. `__inet_del_ifa()` handles primary deletion, optional secondary promotion, silent FIB route removal and re-add for promoted subnets, hash removal, `RTM_DELADDR`, and notifier delivery.

`check_lifetime()` periodically scans the per-net address hash under RCU. It batches expired or deprecated finite-lifetime addresses, takes the per-net RTNL lock only when a change is needed, deletes addresses whose valid lifetime expired, marks preferred-lifetime expirations with `IFA_F_DEPRECATED`, notifies via `RTM_NEWADDR`, and reschedules itself using addressconf fuzz windows.

Read paths are mostly RCU-protected. Address dumps validate strict dump requests, optionally target another net namespace through `IFA_TARGET_NETNSID`, iterate devices and addresses with resumable dump context, and use `inet_base_seq()` to make netlink dump consistency depend on both address generation and device list changes.

Device events coordinate IPv4 address state with multicast, ARP, sysctl, and route behavior. `NETDEV_DOWN` drops multicast state; MTU below IPv4 minimum or unregister destroys the `in_device`; rename rewrites address labels and sysctl paths; address or peer notifications can send gratuitous ARP when `ARP_NOTIFY` is enabled.

## State and Persistence Behavior
State is runtime kernel state scoped to each network namespace and device. Address objects are kept in both per-device RCU lists and a per-net hash keyed by local IPv4 address. Lifetime fields are `ifa_valid_lft`, `ifa_preferred_lft`, `ifa_tstamp`, `ifa_cstamp`, and `IFA_F_PERMANENT` / `IFA_F_DEPRECATED`.

Reference and memory lifetime is RCU-heavy. `inet_alloc_ifa()` takes an `in_device` reference; `inet_free_ifa()` uses `call_rcu_hurry()` so the `in_device` and netdevice reference are released promptly after readers quiesce. `in_device` destruction clears `dev->ip_ptr`, unregisters sysctls, releases ARP parameters, tears down multicast, and frees after RCU once references drain.

Configuration state lives in `devconf_all`, `devconf_dflt`, and per-device `in_dev->cnf`. Sysctl writes mark explicit per-field state bits, may copy default values to devices that have not overridden a field, may flush route cache for policy-affecting fields, and notify `RTNLGRP_IPV4_NETCONF`. No durable storage is written by this file.

## Dependencies and Integration Points
The file depends on rtnetlink, net namespaces, RCU, netdevice notifiers, ARP, IGMP, neighbour parameters, IPv4 route/FIB helpers, l3mdev/VRF helpers, netconf, sysctl, workqueues, and user-copy helpers. It calls FIB helpers indirectly through notifier consumers and directly in promotion paths through `fib_add_ifaddr()`, `fib_del_ifaddr()`, and `fib_modify_prefix_metric()`.

External consumers include route source address selection, ARP validation, bridge and bonding address confirmation, SCTP and mac80211 address notifiers, netfilter masquerade cleanup, IPv4 multicast autjoin, and userspace via `RTM_NEWADDR`, `RTM_DELADDR`, `RTM_GETADDR`, `RTM_GETMULTICAST`, `RTM_GETNETCONF`, `IFLA_INET_CONF`, and legacy `SIOCGIF*` / `SIOCSIF*` ioctls.

## Risks and Edge Cases
Primary/secondary address promotion is delicate because FIB routes must be removed and restored while the device address list still contains enough context to preserve preferred source behavior. Regressions can leave stale local or broadcast routes, mis-promote aliases, or notify listeners in an order that causes route restoration races.

Lifetime handling mixes RCU reads, delayed work, RTNL mutation, and jiffies arithmetic. Important edge cases include zero preferred lifetime, finite valid lifetime, permanent addresses, batched expiry, and avoiding too-frequent rescheduling.

Input validation must preserve historical behavior while enforcing modern netlink strictness. Risks include accepting IPv6-only flags on IPv4 addresses, non-contiguous masks in ioctl paths, unsupported strict dump attributes, invalid net namespace IDs, multicast autojoin failure rollback, and sysctl device names that cannot be registered safely.

Locking assumptions are strict: list/hash address mutations require RTNL, lookup helpers require RCU or RTNL, sysctl forwarding changes may restart the syscall if RTNL cannot be acquired, and notifier callbacks run after visible state changes.

## Test Signals
Useful tests include rtnetlink add/delete/replace of primary and secondary addresses, `NLM_F_EXCL` and `NLM_F_REPLACE`, `IFA_CACHEINFO` finite lifetime expiry/deprecation, `IFA_F_MCAUTOJOIN` success and rollback, invalid prefix and missing-local errors, strict dump filtering by ifindex and target netns, and netconf get/dump for all/default/device scopes.

Lifecycle tests should cover device register/up/down/unregister, MTU below IPv4 minimum, loopback auto-address creation, rename label preservation, gratuitous ARP on notify events, sysctl unregister/re-register, namespace initialization with each `net_inherit_devconf()` mode, and teardown with pending lifetime work. Source selection tests should cover VRF/l3mdev master selection, `route_localnet`, loopback preference, and wildcard `inet_confirm_addr()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/devinet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/esp4.c -->
# sources/distributed-fs/ceph-client/net/ipv4/esp4.c

## Purpose
`esp4.c` implements the IPv4 Encapsulating Security Payload transform for the XFRM/IPsec stack. It registers the IPv4 ESP protocol handler and XFRM type, initializes crypto state for ESP security associations, encrypts outbound packets, decrypts inbound packets, handles ESP NAT-T and optional ESP-in-TCP encapsulation, processes ICMP errors for PMTU/redirects, and exports common ESP helpers used by offload code.

## Important APIs, Types, and Functions
The XFRM type is `esp_type`, with `.init_state = esp_init_state`, `.destructor = esp_destroy`, `.input = esp_input`, and `.output = esp_output`. IPv4 protocol registration is `esp4_protocol`, whose receive handler is `xfrm4_rcv`, input handler is `xfrm_input`, and error handler is `esp4_err()`.

Scratch state is stored in `struct esp_skb_cb` in `skb->cb`, with temporary crypto request memory allocated by `esp_alloc_tmp()`. `struct esp_output_extra` stores ESN high sequence bits and the ESP header offset while ESN temporarily moves header fields for AEAD associated data.

Exported helpers are `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`. Internal helpers include `esp_output_encap()`, `esp_output_udp_encap()`, `esp_output_tcp_encap()`, `esp_output_done()`, `esp_output_done_esn()`, `esp_input_set_header()`, `esp_input_done_esn()`, `esp_remove_trailer()`, `esp_init_aead()`, and `esp_init_authenc()`.

## Control Flow
Outbound processing starts in `esp_output()`. It records the original next-header protocol from `skb_mac_header()`, marks the packet as ESP, computes optional traffic-flow-confidentiality padding, block-size padding, authentication length, ciphertext length, and trailer length, then calls `esp_output_head()` to make tailroom or append a page fragment and fill the ESP trailer. The function then writes SPI and sequence number, adjusts skb data to include the network header, and calls `esp_output_tail()` for AEAD encryption.

`esp_output_head()` handles encapsulation first if `x->encap` is set. UDP encapsulation writes a UDP header and updates the outer protocol field when appropriate; TCP encapsulation validates the associated ESP-in-TCP socket and writes the length field. The function then tries low-copy trailer placement in skb tailroom or a new page frag, falling back to `skb_cow_data()` when cloned, fragmented, or lacking space.

`esp_output_tail()` builds scatterlists over the ESP header, IV, payload, trailer, and ICV. For ESN it moves the ESP header backward by four bytes so high sequence bits become associated data, sets a completion callback that restores the header, derives the IV from the 64-bit sequence value, and calls `crypto_aead_encrypt()`. Synchronous completion restores ESN headers and frees scratch memory; asynchronous completion resumes XFRM output or hands ESP-in-TCP packets to the TCP ULP path.

Inbound processing starts in `esp_input()`. It validates that the skb contains the ESP header and IV, computes encrypted length, ensures writable linear/frags as needed, allocates scratch request memory, moves ESN headers when required, builds a scatterlist over the whole ESP packet, clears checksum state, and calls `crypto_aead_decrypt()`. Completion flows through `esp_input_done2()`, which frees scratch memory, removes and validates padding/trailer, handles NAT-T source mapping changes through `km_new_mapping()`, adjusts checksum semantics for transport-mode encapsulation, pulls the ESP header/IV, resets the transport header for tunnel/IPTFS, and drops dummy `IPPROTO_NONE` packets.

State initialization selects either native AEAD (`esp_init_aead()`) or authenc composition (`esp_init_authenc()`), allocates a `crypto_aead`, sets key and ICV size, computes XFRM header and trailer lengths, and validates encapsulation types. Module init registers the XFRM type and IPv4 protocol in order; exit deregisters both.

## State and Persistence Behavior
Per-SA crypto state is kept in `x->data` as a `struct crypto_aead *` and freed by `esp_destroy()`. Packet-local state is in skb control blocks and temporary allocations that hold IVs, AEAD requests, scatterlists, and optional ESN metadata. The file does not persist state outside memory.

Sequence numbers come from `XFRM_SKB_CB(skb)->seq.output` for normal output and `XFRM_SKB_CB(skb)->seq.input` for ESN input. Encapsulation parameters are read under `x->lock` to avoid races with SA updates. ESP-in-TCP output may consume the skb asynchronously and return `-EINPROGRESS`.

## Dependencies and Integration Points
The implementation depends on the kernel crypto AEAD API, scatterlist helpers, skb frag/page reference management, XFRM core, IPv4 protocol registration, UDP/TCP encapsulation headers, ESP-in-TCP ULP support, PF_KEY/netlink algorithm descriptions, ICMP PMTU/redirect handling, and route cache update helpers.

It integrates with offload code through exported `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`. It integrates with key management through `km_new_mapping()` when NAT-T peer mapping changes. ICMP errors are mapped to `ipv4_update_pmtu()` and `ipv4_redirect()` after locating the matching XFRM state by SPI.

## Risks and Edge Cases
The highest-risk areas are skb geometry and crypto scatterlist construction. Cloned skbs, shared frags, frag lists, insufficient tailroom, page-frag recycling, non-inplace output, asynchronous AEAD completion, and ESP-in-TCP consumption all have distinct memory ownership paths.

ESN handling is subtle because the code temporarily rewrites the ESP header to include high sequence bits in AEAD associated data and must restore it before the packet continues. Bad restoration would corrupt SPI/sequence fields or break replay protection.

Input validation must reject too-short ESP packets, invalid encrypted length, garbage padding, missing IV, dummy packets, and malformed encapsulation. NAT-T accepts source address/port changes by notifying key management, which is intentional but security-sensitive.

Crypto initialization must reject missing algorithms, overlong generated algorithm names, invalid authenc ICV sizes, unsupported encapsulation, and key/authsize setup failure while ensuring sensitive composed keys are freed with `kfree_sensitive()`.

## Test Signals
Test vectors should cover AEAD and authenc SAs, tunnel/transport/BEET/IPTFS header length accounting, ESN and non-ESN encryption/decryption, async crypto completion, NAT-T UDP encapsulation, ESP-in-TCP enabled and unavailable cases, PMTU ICMP handling, redirects, page-frag trailer allocation, `skb_cow_data()` fallback, and malformed padding/truncated packets.

Regression signals include no leaks of crypto scratch memory, correct skb ownership on `-EINPROGRESS`, checksum state after NAT-T transport mode, correct protocol restoration after decrypt, proper `IPPROTO_NONE` dummy drop, and successful module register/unregister rollback when protocol registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/esp4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/esp4_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv4/esp4_offload.c

## Purpose
`esp4_offload.c` adds IPv4 ESP GRO, GSO, and XFRM type offload support. It lets decrypted ESP packets participate in GRO, segments ESP GSO packets according to XFRM outer mode, and prepares outbound ESP packets for hardware crypto offload or software fallback.

## Important APIs, Types, and Functions
The file registers `esp4_offload` with `inet_add_offload(IPPROTO_ESP)` and `esp_type_offload` with `xfrm_register_type_offload(AF_INET)`. Important callbacks are `esp4_gro_receive()`, `esp4_gso_segment()`, `esp_input_tail()`, `esp_xmit()`, and `esp4_gso_encap()`.

Segmentation helpers are `xfrm4_tunnel_gso_segment()`, `xfrm4_transport_gso_segment()`, `xfrm4_beet_gso_segment()`, and `xfrm4_outer_mode_gso_segment()`. The file reuses normal ESP helpers from `esp4.c`: `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`.

## Control Flow
GRO receive starts at `esp4_gro_receive()`. It pulls to the GRO offset, parses SPI and sequence, ensures or creates a security path, looks up the inbound XFRM state unless crypto offload already marked the skb `CRYPTO_DONE`, rejects states for the wrong direction, stores the state in the secpath, marks `XFRM_GRO`, records SPI metadata, detects UDP encapsulation, and invokes `xfrm_input()`. GRO returns `ERR_PTR(-EINPROGRESS)` because XFRM owns completion.

GSO segmentation starts at `esp4_gso_segment()`. It requires `xfrm_offload()` metadata and `SKB_GSO_ESP`, validates SPI against the last secpath state, pulls the ESP header and IV, adjusts feature masks when hardware ESP or hardware ESP checksum support is unavailable, marks `XFRM_GSO_SEGMENT`, and dispatches by XFRM outer mode. Tunnel mode calls Ethernet/IP segmentation for the inner family, transport mode calls the next protocol offload, and BEET mode accounts for BEET pseudo headers or IPv6 extension headers before invoking the inner protocol segmenter.

Outbound offload transmit starts at `esp_xmit()`. It checks whether the skb device matches the SA offload device and whether `NETIF_F_HW_ESP` is available. If not, it sets `CRYPTO_FALLBACK` and uses the software `esp_output_head()` / `esp_output_tail()` path. If hardware offload is available, it computes padding and sequence information, updates the ESP and IPv4 headers, attaches `SKB_EXT_SEC_PATH`, marks `XFRM_XMIT`, and returns with encryption deferred to the device.

`esp_input_tail()` is used for inbound offloaded packets after hardware crypto. It validates the ESP header and IV, clears checksum state unless `CRYPTO_DONE` is present, and feeds the packet into `esp_input_done2()` for common trailer removal and post-decrypt processing.

## State and Persistence Behavior
State is packet-local and runtime-only. The callbacks read and update `struct xfrm_offload` flags such as `CRYPTO_DONE`, `XFRM_GRO`, `XFRM_GSO_SEGMENT`, `CRYPTO_FALLBACK`, `XFRM_XMIT`, and sequence fields. They use the skb secpath to find the active `struct xfrm_state` and may attach `SKB_EXT_SEC_PATH` for hardware transmit.

No durable state is written. Device capabilities, `x->xso.dev`, `skb->dev->gso_partial_features`, and netdevice feature masks determine whether packets take hardware offload or software fallback.

## Dependencies and Integration Points
The file depends on IPv4 inet offload registration, generic GRO/GSO helpers, XFRM offload metadata, secpath management, skb extension support, crypto AEAD properties for IV/auth lengths, IPv4 header checksum helpers, and mode-specific XFRM semantics. It integrates with `esp4.c` through shared post-crypto helpers and with device drivers through `NETIF_F_HW_ESP` and `NETIF_F_HW_ESP_TX_CSUM`.

## Risks and Edge Cases
GRO must restore the skb offset and mark flush/no-same-flow on parse or lookup failure. Missing `secpath_reset()` on failures would leak state. Direction checks are important because wrong-direction offloaded SAs should fall back to normal error/audit behavior.

GSO risks include incorrect feature masking, wrong inner protocol selection for BEET, mishandling IPv6 inner headers, accepting mismatched SPI, or pulling too little data for IV length. Hardware UDP-encapsulated ESP is special because the code must correct the IPv4 protocol field outside the normal XFRM stack path.

Transmit fallback must preserve sequence accounting across GSO segments, update high sequence bits on wrap, linearize when device features require it, and reset secpath after software crypto. Hardware transmit must attach secpath extension successfully or fail without sending malformed packets.

## Test Signals
Useful tests include GRO with normal and `CRYPTO_DONE` packets, invalid SPI parsing, wrong-direction SA rejection, secpath depth exhaustion, UDP-encapsulated GRO, GSO segmentation for tunnel/transport/BEET, BEET IPv4 pseudo-header and IPv6 inner cases, feature masks with and without hardware ESP checksum, fallback software encryption, GSO sequence increment by `gso_segs`, sequence wrap high-bit increment, hardware UDP encapsulation protocol correction, and module init/exit registration ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/esp4_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_frontend.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_frontend.c

## Purpose
`fib_frontend.c` is the IPv4 FIB frontend. It owns per-namespace FIB table setup, route rtnetlink and legacy route ioctl parsing, address-type queries, source validation/reverse-path filtering, automatic route creation and deletion from interface addresses, route dumps, netdevice/address event handling, and IPv4 FIB pernet initialization.

## Important APIs, Types, and Functions
Table management APIs are `fib_new_table()`, `fib_get_table()`, `fib_replace_table()`, `fib_unmerge()`, and `fib_flush()`. Address type APIs are `inet_addr_type_table()`, `inet_addr_type()`, `inet_dev_addr_type()`, and `inet_addr_type_dev_table()`.

Source validation is implemented by `fib_validate_source()` and `__fib_validate_source()`. Route user interfaces are `ip_rt_ioctl()`, `rtentry_to_fib_config()`, `rtm_to_fib_config()`, `inet_rtm_newroute()`, `inet_rtm_delroute()`, `ip_valid_fib_dump_req()`, and `inet_dump_fib()`.

Address-derived route manipulation is handled by `fib_magic()`, `fib_add_ifaddr()`, `fib_modify_prefix_metric()`, and `fib_del_ifaddr()`. Lifecycle hooks are `fib_inetaddr_event()`, `fib_netdev_event()`, `fib_disable_ip()`, `ip_fib_net_init()`, `ip_fib_net_exit()`, `fib_net_init()`, `fib_net_exit()`, `fib_net_exit_batch()`, and `ip_fib_init()`.

## Control Flow
Per-net initialization registers fib notifiers, allocates the FIB table hash, creates default tables/rules, initializes `fib_semantics` hashes, creates a `NETLINK_FIB_LOOKUP` socket, and initializes proc entries. In non-multiple-table builds the local and main trie tables are created directly. In multiple-table builds `fib_new_table()` lazily allocates trie tables, records main/default RCU shortcuts, and aliases local to main until custom rules force `fib_unmerge()`.

Route add/delete through rtnetlink parses `struct rtmsg` and attributes into `struct fib_config`, validates DSCP/TOS, prefix length and host bits, gateway versus via exclusivity, nexthop-id exclusivity, lwtunnel encap types, table selection, and route type. Add creates the target table and calls `fib_table_insert()`; delete verifies nexthop ID existence and calls `fib_table_delete()`.

Legacy `SIOCADDRT` and `SIOCDELRT` ioctls translate `struct rtentry` into the same `fib_config` model. The conversion preserves historical quirks such as metric minus one, classful mask defaults from userspace, alias labels choosing preferred source, gateway scope inference, and metrics mapping to `RTAX_ADVMSS`, `RTAX_WINDOW`, and `RTAX_RTT`.

Source validation builds a reverse lookup flow from packet source/destination, l3mdev, optional mark, DSCP, ports from early flow dissection when required by rules, and RPF settings. It fast-paths common cases without custom local routes/rules, treats IPsec-secpath packets as exempt from rp_filter, rejects invalid local/broadcast sources, and returns drop reasons such as `SKB_DROP_REASON_IP_RPFILTER`.

Interface address events call `fib_add_ifaddr()` and `fib_del_ifaddr()` to create or delete local, prefix, and broadcast routes. Device events synchronize nexthop state, flush route cache, update MTU exceptions, and disable IP on unregister or last-address removal. Route dumps iterate the FIB table hash with resumable callback args and strict dump filters for table and output device.

## State and Persistence Behavior
State is runtime and per-net. `net->ipv4.fib_table_hash` contains `struct fib_table` objects; optional RCU shortcuts point at main/default tables. Flags such as `fib_has_custom_local_routes` and `fib_has_custom_rules` influence source validation. `dev_addr_genid` changes when addresses affect routes.

Address-derived route state is stored in normal FIB tables, not separately. Route cache and nexthop state are flushed or marked dead/linkdown on address and device changes. The `NETLINK_FIB_LOOKUP` socket exists per namespace and is released during net exit.

## Dependencies and Integration Points
The file depends on trie table operations from `fib_trie.c`, shared fib_info semantics from `fib_semantics.c`, policy rules from `fib_rules.c`, notifier setup from `fib_notifier.c`, rtnetlink, lwtunnel, nexthop objects, l3mdev/VRF, XFRM/IPsec, ARP, IPv4 route cache, flow dissector data, procfs, and netdevice/inetaddr notifier chains.

It integrates with `devinet.c` through address notifiers and direct calls from address insertion/deletion paths. It integrates with `route.c` through lookup, source validation, and path selection. Userspace integration is through `RTM_NEWROUTE`, `RTM_DELROUTE`, `RTM_GETROUTE`, route ioctls, and the legacy FIB lookup netlink family.

## Risks and Edge Cases
Rules and table aliasing are subtle. `fib_unmerge()` must split local and main tables before custom rules can expose different semantics. Failure can leak local routes into the wrong table or break local route dumps.

Route parser risks include invalid DSCP with ECN bits, nonzero host bits for prefixes, mutually exclusive gateway/via/nexthop specifications, IPv6 gateway via `RTA_VIA`, lwtunnel validation, and preserving compatibility for old ioctls.

Source validation is security-sensitive because it implements martian-source and reverse-path filtering decisions. Custom rules, VRF/l3mdev, IPsec exemptions, local addresses in containers, marks, and flow-dissected port selectors all affect whether packets are dropped.

Device/address synchronization must avoid deleting shared broadcast/local routes still used by other addresses and must flush routes when preferred source addresses disappear. Net exit destroys tables in reverse order because the local table can reference main-table data.

## Test Signals
Test route netlink add/delete/dump with main, local, default, custom tables, nexthop IDs, multipath, `RTA_VIA`, lwtunnel encap, invalid prefixes, invalid DSCP, and strict dump filters. Test route ioctl add/delete for gateway, reject, device alias, and metrics.

Lifecycle tests should cover address add/delete generating local/prefix/broadcast routes, secondary address promotion, metric replacement through address replace, device up/down/change/unregister, MTU change exception updates, VRF upper changes, and namespace teardown ordering. Source-validation tests should cover rp_filter modes, IPsec secpath exemption, custom local routes/rules, accept_local, src_valid_mark, l3mdev, and port-matching rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_frontend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_lookup.h -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_lookup.h

## Purpose
`fib_lookup.h` is the internal IPv4 FIB lookup contract shared by trie lookup, frontend, rules, and semantics code. It defines the route alias node stored under trie leaves, the route property table shape, and prototypes for creating, matching, serializing, notifying, and releasing shared `fib_info` objects.

## Important APIs, Types, and Functions
`struct fib_alias` represents one route alias for a prefix. It links through `fa_list`, points to shared `fa_info`, stores DSCP selector, route type, state flags, suffix length, table ID, default-route selection cache, offload flags, trap/offload-failure flags, and RCU head.

`fib_alias_accessed()` lazily sets `FA_S_ACCESSED` with `READ_ONCE()` and `WRITE_ONCE()` to avoid unnecessary cacheline writes on lookup. `fib_result_assign()` assigns a `struct fib_info` and first nexthop common pointer to a lookup result without refcount games because readers use RCU.

The header declares `fib_release_info()`, `fib_create_info()`, `fib_nh_match()`, `fib_metrics_match()`, `fib_dump_info()`, `rtmsg_fib()`, `fib_nlmsg_size()`, and the global `fib_props[]` table mapping route types to scope and error semantics.

## Control Flow
`fib_trie.c` allocates and orders `fib_alias` instances under trie leaves, calls `fib_create_info()` to deduplicate nexthop/metric state, and uses `rtmsg_fib()` plus notifier helpers to advertise route changes. Lookup paths return a `fib_result` by selecting a matching alias and assigning its shared `fib_info` through `fib_result_assign()`.

`fib_semantics.c` implements the declared functions and uses `fib_alias` metadata when dumping and notifying routes. `fib_frontend.c` and `fib_rules.c` depend on the result contract for table lookup, source validation, and rule action callbacks.

## State and Persistence Behavior
`fib_alias` is runtime route-table state owned by trie leaves and freed with RCU. It does not own the nexthop payload; `fa_info` points to refcounted shared `fib_info`. Offload flags reflect runtime driver or switchdev state and are included in route notifications/dumps.

## Dependencies and Integration Points
The header depends on generic list/RCU types, DSCP helpers, IPv4 FIB public definitions, and nexthop objects. It is internal to the IPv4 FIB implementation and is the bridge between prefix trie nodes and shared route semantics.

## Risks and Edge Cases
Because lookup readers are RCU-based, `fib_result_assign()` must not take references and writers must keep `fib_info` alive until grace periods finish. `fib_alias_accessed()` deliberately avoids writes unless the accessed bit is absent; changing that could add lookup-path cacheline contention.

The route alias fields are compact and visible to multiple subsystems. DSCP, table ID, offload state, and default-route cache semantics must remain aligned with trie insertion, dump, and path-selection logic.

## Test Signals
Coverage comes from route add/delete/lookup/dump tests that create multiple aliases for the same prefix with different priorities, DSCP selectors, route types, and tables; default-route selection tests; route offload flag update tests; and RCU stress tests around deleting routes while lookups and dumps run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_lookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_notifier.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_notifier.c

## Purpose
`fib_notifier.c` adapts IPv4 FIB and rule state to the generic fib notifier framework. It tags events as `AF_INET`, maintains an IPv4 FIB sequence counter, combines route and rule sequence state for listeners, dumps current rules and routes to new notifier clients, and registers/unregisters per-net notifier operations.

## Important APIs, Types, and Functions
`call_fib4_notifier()` calls a single notifier block after setting `info->family = AF_INET`. `call_fib4_notifiers()` broadcasts to all registered listeners, asserts RTNL, sets the family, increments `net->ipv4.fib_seq`, and calls the generic notifier fanout.

`fib4_seq_read()` returns the IPv4 route sequence plus `fib4_rules_seq_read()` so listeners can detect changes in both routes and rules. `fib4_dump()` first dumps IPv4 rules through `fib4_rules_dump()` and then dumps routes through `fib_notify()`.

Per-namespace lifecycle is `fib4_notifier_init()` and `fib4_notifier_exit()`, which register and unregister an instance of `fib4_notifier_ops_template`.

## Control Flow
During FIB per-net initialization, `fib4_notifier_init()` resets the route sequence counter and registers notifier ops for the namespace. Route or nexthop changes later call `call_fib4_notifiers()`, which increments the sequence before dispatching. A consumer registering with the generic notifier framework can request a dump; `fib4_dump()` emits rules first and then route entries so consumers see policy and table contents.

## State and Persistence Behavior
State is limited to the runtime per-net `fib_seq` counter and `net->ipv4.notifier_ops` pointer. The counter uses `WRITE_ONCE()` paired with `READ_ONCE()` in `fib4_seq_read()` to avoid torn reads for lockless sequence checks. No durable state exists.

## Dependencies and Integration Points
The file depends on rtnetlink locking, generic `fib_notifier` infrastructure, IPv4 rule dump/sequence helpers, and route dump support from `fib_notify()`. It is used by FIB table/trie and nexthop state changes, including notifier calls from `fib_semantics.c` when nexthops become dead or alive.

## Risks and Edge Cases
Sequence accounting must include both route and rule changes; otherwise hardware offload or monitoring clients can miss updates. `call_fib4_notifiers()` requires RTNL, so callers that mutate FIB state outside RTNL would violate notifier ordering.

Dump ordering matters for clients reconstructing state. If route dump succeeds after rule dump failure or vice versa, callers need the returned error to avoid accepting partial state.

## Test Signals
Tests should register a fib notifier, add/delete IPv4 routes and rules, verify `AF_INET` family tagging, sequence changes for both route and rule mutations, dump ordering of rules before routes, and clean per-net unregister during namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_rules.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_rules.c

## Purpose
`fib_rules.c` implements IPv4 policy routing rules for the generic FIB rules engine. It defines IPv4-specific rule selectors, validates and serializes rule netlink attributes, initializes default local/main/default rules, performs rule-driven lookup, and tracks whether custom rules require slower packet flow dissection.

## Important APIs, Types, and Functions
`struct fib4_rule` embeds `struct fib_rule` and adds IPv4 source/destination prefix lengths, masks and addresses, DSCP/TOS selector state, and optional route class ID. Exported helpers include `fib4_rule_default()`, `fib4_rules_dump()`, `fib4_rules_seq_read()`, and `__fib_lookup()`.

Rule callbacks in `fib4_rules_ops_template` are `fib4_rule_action()`, `fib4_rule_suppress()`, `fib4_rule_match()`, `fib4_rule_configure()`, `fib4_rule_delete()`, `fib4_rule_compare()`, `fib4_rule_fill()`, `fib4_rule_nlmsg_payload()`, and `fib4_rule_flush_cache()`. Namespace lifecycle is `fib4_rules_init()` and `fib4_rules_exit()`.

## Control Flow
`__fib_lookup()` updates the flow for l3mdev devices, calls `fib_rules_lookup()` with the IPv4 rules ops, copies class ID from the matching rule when enabled, and maps `-ESRCH` to `-ENETUNREACH`.

Rule matching checks source and destination masked prefixes, then DSCP/TOS semantics. Full DSCP selector rules compare the complete DSCP field with a mask; legacy TOS rules use masked legacy behavior. It then checks IP protocol and source/destination port ranges, which may require earlier flow dissection by callers.

Rule action handles table lookup and non-table actions. `FR_ACT_TO_TBL` selects the table from the rule and calls `fib_table_lookup()`. `FR_ACT_UNREACHABLE`, `FR_ACT_PROHIBIT`, and blackhole/unsupported actions return the route error directly. Suppression rejects otherwise matching results when the prefix length is too small or the nexthop device is in a suppressed interface group.

Configuration rejects IPv6 flowlabel attributes, validates TOS/DSCP, handles optional DSCP masks, forces `fib_unmerge()` so local/main table aliasing cannot hide custom rule behavior, allocates an empty table for unspecified table rules when needed, stores source/destination masks, increments class ID users, increments flow-dissect requirement counters for port/protocol selectors, and marks the namespace as having custom rules.

## State and Persistence Behavior
Rules are runtime per-net objects managed by the generic fib rules framework. IPv4-specific state is in each `fib4_rule` plus per-net `rules_ops`, `fib_has_custom_rules`, and `fib_rules_require_fldissect`. Optional class ID rules update `fib_num_tclassid_users`.

No state is durable. Adding or deleting rules flushes route cache through the rules ops and updates rule sequence via the generic framework. Default rules are recreated for each namespace during init.

## Dependencies and Integration Points
The file depends on the generic `fib_rules` framework, IPv4 FIB table lookup, l3mdev, DSCP helpers, nexthop/table state, route cache flush, and optional route class ID support. It integrates with `fib_frontend.c` for initialization and `fib_notifier.c` for rule dump/sequence reporting. `route.c`, `fib_frontend.c`, and netfilter use `fib4_rules_early_flow_dissect()` decisions through per-net counters set here.

## Risks and Edge Cases
DSCP/TOS compatibility is subtle: legacy TOS cannot express high-order DSCP bits, while new DSCP plus mask must be internally consistent and mutually exclusive with TOS. Incorrect validation can change policy routing behavior for existing users.

`fib_unmerge()` is required before custom rule changes; failure to split tables would cause rule-visible local/main lookup differences to be wrong. The flow-dissect counter must be incremented and decremented exactly for rules needing ports or protocol, or lookup callers will either miss selectors or pay unnecessary cost.

Suppression releases `fib_info` unless `FIB_LOOKUP_NOREF` is set. Refcount behavior must stay aligned with lookup flags. Rule delete marks `fib_has_custom_rules` true even after deletion, preserving conservative source-validation behavior.

## Test Signals
Test default rule creation, lookup through local/main/default tables, unreachable/prohibit/blackhole rule actions, source/destination prefix rules, legacy TOS versus DSCP/mask selectors, invalid flowlabel rejection, port/protocol rules and flow-dissect requirement counters, suppression by prefix length and interface group, class ID accounting, table auto-allocation, cache flush on rule change, and notifier sequence changes for rule mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_rules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_semantics.c -->
# sources/distributed-fs/ceph-client/net/ipv4/fib_semantics.c

## Purpose
`fib_semantics.c` implements shared IPv4 route semantics below tables and rules. It owns `fib_info` allocation, deduplication, refcounting, metrics, nexthop initialization and validation, preferred source validation and caching, route netlink serialization, nexthop/device down-up synchronization, PMTU exception updates, default and multipath path selection, and per-net fib_info hash lifecycle.

## Important APIs, Types, and Functions
The route-type property table is `fib_props[]`, mapping `RTN_*` types to default error and scope. Core lifetime APIs are `fib_create_info()`, `fib_release_info()`, `free_fib_info()`, `fib_nh_common_release()`, and `fib_nh_release()`.

Nexthop creation and validation APIs include `fib_nh_common_init()`, `fib_nh_init()`, `fib_check_nh()`, `fib_check_nh_v4_gw()`, `fib_check_nh_v6_gw()`, `fib_check_nh_nongw()`, `fib_get_nhs()`, `fib_nh_match()`, `fib_metrics_match()`, and `fib_rebalance()`.

Serialization and notification APIs include `fib_nlmsg_size()`, `rtmsg_fib()`, `fib_nexthop_info()`, `fib_add_nexthop()`, and `fib_dump_info()`. Runtime synchronization APIs are `ip_fib_check_default()`, `fib_sync_down_addr()`, `fib_nhc_update_mtu()`, `fib_sync_mtu()`, `fib_sync_down_dev()`, `fib_sync_up()`, `fib_select_path()`, `fib_select_multipath()`, and `fib_result_prefsrc()`.

## Control Flow
Route creation begins in `fib_create_info()`. It validates route type, scope, forbidden flags, nexthop ID existence, multipath array structure, and metrics. It allocates a flexible `fib_info`, initializes metrics, fills direct nexthops or attaches a nexthop object, rejects invalid route-type combinations, validates host-scope restrictions, validates gateways/devices through `fib_check_nh()`, validates preferred source, computes source-address cache, rebalances multipath weights, deduplicates against existing `fib_info`, and finally links the object into hash tables and per-device nexthop lists.

Gateway validation recursively checks reachability. Onlink IPv4 gateways require an output device, up carrier semantics, and a unicast gateway address on that device. Non-onlink IPv4 gateways are looked up in the route table or full rules path with increased scope and must resolve to unicast/local with an egress device. IPv6 gateways delegate to IPv6 nexthop initialization. Nongateway nexthops require a valid up IPv4 device and reject pervasive/onlink flags.

Deletion goes through `fib_release_info()`: when trie references drain, it removes the object from hash tables, preferred-source hash, nexthop object lists or per-device nexthop hashes, marks `fib_dead` with `WRITE_ONCE()`, and releases the final client reference through RCU. `free_fib_info_rcu()` releases nexthop objects or embedded nexthops, route metrics, cached rtable exceptions, per-CPU output routes, lwtunnel state, and netdevice references.

Route dumps compute a conservative netlink size, write `rtmsg`, table, destination, priority, metrics, preferred source, nexthop ID, single or multipath nexthop attributes, lwtunnel encap, class IDs, and offload/trap flags. `rtmsg_fib()` packages trie alias metadata with `fib_dump_info()` and sends notifications to `RTNLGRP_IPV4_ROUTE`.

Device/address synchronization marks route state rather than always deleting objects. `fib_sync_down_addr()` marks routes with a removed preferred source as dead. `fib_sync_down_dev()` marks nexthops and whole `fib_info` objects `LINKDOWN` and/or `DEAD`, calls fib notifiers for nexthop delete events, and rebalances multipath. `fib_sync_up()` clears those flags when devices return and emits nexthop add events. `fib_sync_mtu()` updates PMTU exceptions attached to nexthops.

Path selection uses multipath hashing when multiple paths exist, nexthop objects when attached, neighbor reachability if `fib_multipath_use_neigh` is enabled, source-address affinity scoring, weighted upper bounds, and default-route probing through neighbor state. `fib_select_path()` also fills `flowi4.saddr`, respecting l3mdev source selection.

## State and Persistence Behavior
Per-net state includes `fib_info_hash`, `fib_info_hash_bits`, and `fib_info_cnt`. The hash has two halves: primary `fib_info` deduplication buckets and preferred-source lookup buckets. It grows when the object count reaches the current bucket count.

`fib_info` objects are shared runtime route payloads referenced by trie aliases and lookup results. They hold route metrics, type/scope/protocol/table/priority, preferred source, flags, embedded nexthops or a nexthop object reference, and route cache/exception state. Embedded nexthops are also linked into `dev->fib_nh_head` for device event scans.

Preferred source cache is stored per IPv4 nexthop as `nh_saddr` plus `nh_saddr_genid`, invalidated by `dev_addr_genid`. Multipath upper bounds are atomics updated by `fib_rebalance()`. No durable route state is persisted here.

## Dependencies and Integration Points
The file depends on IPv4 and IPv6 nexthop helpers, ARP/ND neighbor tables, lwtunnel state, rtnetlink metrics, TCP congestion-control metric keys, netdevice refs/trackers, XFRM-independent route cache objects, fib notifiers, DSCP helpers, address selection from `devinet.c`, and trie aliases from `fib_lookup.h`.

It is called by `fib_trie.c` for route insert/delete/dump, by `fib_frontend.c` for address/device lifecycle and route selection, by redirect logic through `ip_fib_check_default()`, and by notifier/offload consumers through route and nexthop event notifications.

## Risks and Edge Cases
Nexthop validation is historically complex. Gateways can be local, directly connected, recursively reachable, forced onlink, IPv6 via IPv4 routes, or hidden behind lwtunnels. Incorrect scope or device validation can accept unreachable routes or reject valid policy/VRF routes.

Lifetime and refcounting are high risk. Lookup readers are RCU-based, while writers remove from hash/list structures under RTNL and defer freeing. The code must avoid freeing alive `fib_info`, leaking netdevice/lwtunnel/metrics references, or leaving embedded nexthops in device hashes.

Multipath behavior depends on weights, linkdown flags, neighbor state, source address affinity, nexthop objects, and sequence wrap. Rebalance errors can skew traffic or select dead nexthops. Device down/up notifier transitions must emit correct add/delete events only when a nexthop becomes externally visible or hidden.

Route serialization must size messages correctly for metrics, nexthop IDs, multipath, IPv6 `RTA_VIA`, lwtunnel encap, offload flags, and nexthop compatibility mode. `-EMSGSIZE` here is treated as a bug in size calculation.

## Test Signals
Creation tests should cover unicast/local/broadcast/throw/unreachable/prohibit route types, invalid scopes, forbidden `DEAD`/`LINKDOWN` flags, preferred source validation, IPv4 and IPv6 gateways, onlink gateways, down devices, missing devices, lwtunnel encap, nexthop IDs, duplicate route deduplication, metrics matching, and multipath attribute validation.

Lifecycle tests should cover route deletion under concurrent lookup, RCU freeing, per-device nexthop hash cleanup, address preferred-source removal, device down/change/unregister/up, PMTU exception update rules, net namespace hash init/exit, and class ID accounting. Path tests should cover weighted ECMP distribution, linkdown ignore, neighbor-aware selection, source-affinity preference, default-route fallback, nexthop objects, and l3mdev source address selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv4/fib_semantics.c -->
