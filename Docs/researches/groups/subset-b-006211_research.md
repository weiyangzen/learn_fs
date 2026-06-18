<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ah6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ah6.c

## Purpose
Implements IPv6 IPsec Authentication Header (AH) transformation support for XFRM. It registers an IPv6 XFRM type and protocol handler for `IPPROTO_AH`, authenticates outbound packets, validates inbound packets, normalizes mutable IPv6 fields during Integrity Check Value (ICV) computation, and handles AH-related ICMPv6 PMTU/redirect errors.

## Important APIs, Types, and Functions
Key structures are `struct ah_skb_cb`, which stores async hash scratch state in `skb->cb`, and `struct tmp_ext`, which saves mutable/restorable IPv6 addresses and extension headers. Core helpers include `ah_alloc_tmp()`, `zero_out_mutable_opts()`, `ipv6_clear_mutable_options()`, `ah6_output()`, `ah6_input()`, `ah6_output_done()`, `ah6_input_done()`, `ah6_err()`, `ah6_init_state()`, and `ah6_destroy()`. The module exports behavior through `struct xfrm_type ah6_type` and `struct xfrm6_protocol ah6_protocol`.

## Control Flow
Outbound processing reserves writable skb data, saves the first IPv6 header bytes and extension headers, zeros mutable fields/options, writes AH SPI/sequence metadata, builds scatterlists over packet data plus optional ESN high sequence bits, and runs `crypto_ahash_digest()`. Synchronous completion restores saved headers and copies the truncated ICV; asynchronous completion follows the same path in `ah6_output_done()`. Inbound processing validates AH length, copies the original ICV, zeros the in-packet ICV and mutable fields, hashes the packet plus optional ESN high bits, compares via `crypto_memneq()`, removes the AH header, restores the original IPv6 header chain, and resumes XFRM input.

## State and Persistence
Per-SA state is `struct ah_data` stored in `x->data`, including the crypto ahash transform and full/truncated ICV lengths. Per-packet temporary allocations hold saved header bytes, original authentication data, computed ICV, ahash request, and scatterlists. No on-disk persistence exists; module lifetime state is limited to protocol/type registration.

## Dependencies and Integration Points
Depends on XFRM, crypto ahash, IPv6 routing/error handling, scatterlist/skbuff helpers, PF_KEY algorithm descriptions, and optional Mobile IPv6 Home Address Option handling. AH integrates with IPv6 receive dispatch through `xfrm6_rcv`, XFRM input/output resume paths, `ip6_update_pmtu()`, and `ip6_redirect()`.

## Risks and Test Signals
Risk concentrates in extension-header normalization, malformed mutable options, ESN byte-order handling, async crypto lifetime, skb linearization/cow failures, and MIPv6 address rearrangement. Useful tests include AH transport/tunnel/BEET vectors, inbound bad-ICV rejection, ESN wrap cases, packets with routing/destination/hop options, async crypto providers, PMTU ICMP handling, and KASAN/KCSAN coverage around temporary buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ah6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/anycast.c -->
# sources/distributed-fs/ceph-client/net/ipv6/anycast.c

## Purpose
Provides IPv6 anycast address membership support for sockets and network devices. It lets privileged sockets join/drop anycast addresses, maintains per-device anycast lists, installs/removes associated IPv6 routes and solicited-node multicast memberships, exposes lookups for source/address validation, and optionally reports state through `/proc/net/anycast6`.

## Important APIs, Types, and Functions
The global hash table `inet6_acaddr_lst` indexes `struct ifacaddr6` objects by network namespace and anycast address. Socket-facing APIs include `ipv6_sock_ac_join()`, `ipv6_sock_ac_drop()`, `ipv6_sock_ac_close()`, and `__ipv6_sock_ac_close()`. Device APIs include `__ipv6_dev_ac_inc()`, `__ipv6_dev_ac_dec()`, `ipv6_ac_destroy_dev()`, `ipv6_chk_acast_addr()`, and `ipv6_chk_acast_addr_src()`. Procfs support uses `ac6_seq_ops`.

## Control Flow
Joining validates `CAP_NET_ADMIN`, rejects multicast addresses, resolves or chooses a device, checks host/router prefix rules, allocates a socket membership entry, and increments the device anycast object. Device increment either bumps `aca_users` or allocates a route-backed `ifacaddr6`, links it under `idev->lock`, publishes it into the RCU hash, inserts the route, joins solicited-node multicast, and sends RTNL notification. Drop/close paths unlink socket entries and decrement device usage; the last user removes hash membership, leaves solicited multicast, deletes the route, notifies RTNL, and frees via RCU.

## State and Persistence
State is in per-socket `np->ipv6_ac_list`, per-device `idev->ac_list`, the global RCU hash, refcounted `ifacaddr6` objects, and route references (`aca_rt`). It is runtime-only and scoped by network namespace/device lifetime.

## Dependencies and Integration Points
Depends on addrconf, IPv6 route allocation/deletion, netdevice reference tracking, RTNL multicast notifications, procfs seq files, RCU, and namespace hashing. Datagram send control uses `ipv6_chk_acast_addr_src()` to permit anycast source addresses.

## Risks and Test Signals
Risks include device lifetime races, mismatched socket/device refcounts, route insertion/deletion failures, host/router behavior differences, and RCU/hash cleanup leaks. Test signals include privileged/unprivileged join/drop, link-local and global anycast checks, device teardown cleanup, `/proc/net/anycast6` output, RTM_NEWANYCAST/RTM_DELANYCAST notifications, and `ipv6_anycast_cleanup()` empty-hash warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/anycast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/calipso.c -->
# sources/distributed-fs/ceph-client/net/ipv6/calipso.c

## Purpose
Implements the IPv6 CALIPSO security label option from RFC 5570 for NetLabel. It manages Domain of Interpretation (DOI) definitions, maps MLS levels/categories to CALIPSO hop-by-hop options, validates and parses packet labels, attaches/removes labels from sockets, request sockets, and skbs, and provides a small label mapping cache.

## Important APIs, Types, and Functions
Important global state includes `calipso_doi_list`, `calipso_doi_list_lock`, `calipso_cache`, `calipso_cache_enabled`, and `calipso_cache_bucketsize`. DOI APIs are `calipso_doi_add()`, `calipso_doi_remove()`, `calipso_doi_getdef()`, `calipso_doi_putdef()`, and `calipso_doi_walk()`. Cache APIs include `calipso_cache_check()`, `calipso_cache_add()`, and `calipso_cache_invalidate()`. Option helpers include `calipso_validate()`, `calipso_genopt()`, `calipso_opt_insert()`, `calipso_opt_del()`, `calipso_opt_getattr()`, and skb/socket/request accessors. `struct netlbl_calipso_ops ops` binds the file to NetLabel.

## Control Flow
Initialization allocates cache buckets and registers NetLabel ops. DOI add/remove updates an RCU list and emits audit records. Option generation aligns CALIPSO at 4n+2, writes DOI/level/category bitmap, pads to IPv6 option alignment, and computes CRC-CCITT. Receive validation verifies CRC and DOI existence, then decodes level/categories through DOI mapping, optionally using the cache. Socket/request setters rebuild IPv6 hop options with CALIPSO inserted or replaced. SKB setters grow or shrink packet header space, update payload length, add/remove hop-by-hop headers when needed, and preserve surrounding options.

## State and Persistence
Runtime state is DOI definitions with refcounts and RCU lifetime, mapping-cache buckets with activity-based list ordering, socket/request `ipv6_txoptions`, and mutated skb hop options. Cache invalidation happens on DOI final put and exit. There is no persistent storage.

## Dependencies and Integration Points
Depends on NetLabel LSM security attributes, audit logging, IPv6 option helpers, CRC-CCITT, RCU/spinlocks, skb copy-on-write, TCP request sockets, and `ipv6_renew_options()`. `exthdrs.c` calls `calipso_validate()` when parsing hop-by-hop options.

## Risks and Test Signals
Risks include option length/alignment errors, stale cache entries after DOI changes, duplicate cache keys, checksum/CRC mismatches, skb header growth/shrink corner cases, and partial SYN-cookie request-socket limitations. Test signals include DOI add/remove audit logs, cache hit/miss behavior, valid/invalid CRC packets, large category maps near option limits, socket label set/get/delete, request-socket inheritance, skb label insertion/removal, and NetLabel policy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/calipso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/datagram.c -->
# sources/distributed-fs/ceph-client/net/ipv6/datagram.c

## Purpose
Contains common IPv6 datagram socket support shared by UDP and raw sockets. It handles connected datagram routing state, IPv4-mapped connect compatibility, asynchronous ICMP/local error queue delivery, path-MTU notification delivery, receive ancillary control messages, send ancillary control parsing, and `/proc` socket display formatting.

## Important APIs, Types, and Functions
Core exported functions include `ip6_datagram_dst_update()`, `ip6_datagram_release_cb()`, `__ip6_datagram_connect()`, `ip6_datagram_connect()`, `ip6_datagram_connect_v6_only()`, `ipv6_icmp_error()`, `ipv6_local_error()`, `ipv6_local_rxpmtu()`, `ipv6_recv_error()`, `ipv6_recv_rxpmtu()`, `ip6_datagram_recv_ctl()`, `ip6_datagram_send_ctl()`, and `__ip6_dgram_sock_seq_show()`.

## Control Flow
Connect builds a `flowi6` from socket state, handles AF_INET fallback for IPv4-mapped destinations, resolves scope IDs, saves old peer state, performs route lookup with source selection, updates socket source/receive addresses, caches the dst, marks reuseport connection state, and sets the socket established. Error producers clone or allocate skbs with `sock_extended_err` metadata; consumers dequeue via `MSG_ERRQUEUE`, copy payload, attach timestamps, offender addresses, IPv6/IP control messages, and return copied length. Send control parsing iterates cmsghdrs for pktinfo, flowinfo, hop/destination/routing headers, hoplimit, traffic class, and dontfrag, validating sizes, capabilities, address ownership, and option ordering.

## State and Persistence
State is socket-local: cached dst/cork flow, `np->saddr`, `sk_v6_daddr`, receive source, flow label, `np->rxpmtu`, error queue skbs, and transient `ipcm6_cookie` options. No persistent storage exists.

## Dependencies and Integration Points
Depends on route lookup, flowlabel lookup, XFRM/security flow classification, IPv4 datagram fallback, anycast address validation, IPv6 extension option formats, socket error queue helpers, timestamp/cmsg code, and procfs seq output. UDP/raw send paths call `ip6_datagram_send_ctl()`.

## Risks and Test Signals
Risks include inconsistent socket state after failed connect, incorrect scope/device checks, ancillary option length bugs, capability bypass for raw extension headers, stale dst refresh behavior, and mismatched RFC4884/error cmsg formatting. Test signals include v4-mapped connect, scoped link-local connect, pktinfo source validation including anycast, route invalidation release callbacks, `MSG_ERRQUEUE` reads, `IPV6_RECVPATHMTU`, old RFC2292 cmsgs, and malformed cmsghdr rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/datagram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/esp6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/esp6.c

## Purpose
Implements software IPv6 IPsec Encapsulating Security Payload (ESP) for XFRM. It performs outbound encryption/authentication, inbound decryption/authentication, padding/trailer handling, ESN header manipulation, UDP and optional TCP ESP encapsulation, error handling, and XFRM type/protocol registration.

## Important APIs, Types, and Functions
Key structures are `struct esp_skb_cb` and `struct esp_output_extra`. Allocation/layout helpers include `esp_alloc_tmp()`, `esp_tmp_iv()`, `esp_tmp_req()`, and `esp_req_sg()`. Output path functions are `esp6_output()`, exported `esp6_output_head()`, exported `esp6_output_tail()`, encapsulation helpers, and async callbacks. Input path functions are `esp6_input()`, exported `esp6_input_done2()`, `esp_remove_trailer()`, and ESN restore/set helpers. State setup uses `esp_init_aead()`, `esp_init_authenc()`, and `esp6_init_state()`.

## Control Flow
Outbound ESP selects inner protocol, computes TFC/padding/auth trailer lengths, optionally adds UDP/TCP encapsulation, appends trailer in skb tailroom or page frags, writes SPI/sequence, handles ESN by temporarily shifting the ESP header, builds source/destination scatterlists, derives IV from sequence, runs AEAD encryption, fixes encapsulation checksum, and resumes XFRM or queues ESP-in-TCP. Inbound ESP validates minimum header/IV, ensures writable data, shifts ESN high bits into associated data when needed, decrypts in place, removes auth/padding/trailer, processes NAT-T source updates, adjusts checksum state, pulls ESP header/IV, and returns next header or drops dummy packets.

## State and Persistence
Per-SA state is the `crypto_aead` transform in `x->data`, header/trailer length metadata in `x->props`, optional `x->xfrag` page-frag cache, encapsulation template, and replay sequence information from XFRM control blocks. Per-packet temporary memory holds IV, AEAD request, ESN extra, and scatterlists.

## Dependencies and Integration Points
Depends on XFRM, crypto AEAD/authenc, skbuff scatterlists, IPv6 routing/error updates, UDP/TCP ESP encapsulation, inet6 socket lookup for ESP-in-TCP, and exported helpers consumed by `esp6_offload.c`.

## Risks and Test Signals
Risks include scatterlist sizing, page-frag lifetime, ESN header restore on sync/async errors, checksum handling for UDP NAT-T, ESP-in-TCP queue ownership, padding validation, and offload interop. Test signals include AEAD and authenc SAs, ESN wrap, transport/tunnel/BEET/IPTFS modes, UDP and TCP encapsulation, async crypto providers, malformed pad length, NAT mapping notification, PMTU redirect handling, and XFRM stats on protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/esp6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/esp6_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv6/esp6_offload.c

## Purpose
Adds IPv6 ESP GRO/GSO and hardware offload support. It registers ESP as an IPv6 net offload protocol and as an XFRM type offload, enabling receive aggregation, segmentation, hardware transmit marking, and software fallback through the normal `esp6.c` helpers.

## Important APIs, Types, and Functions
Core callbacks are `esp6_gro_receive()`, `esp6_gso_segment()`, `esp6_input_tail()`, `esp6_xmit()`, and `esp6_gso_encap()`. Mode-specific segmentation helpers include `xfrm6_tunnel_gso_segment()`, `xfrm6_transport_gso_segment()`, and `xfrm6_beet_gso_segment()`. Registration is through `struct net_offload esp6_offload` and `struct xfrm_type_offload esp6_type_offload`.

## Control Flow
GRO receive pulls to the ESP offset, parses SPI/sequence, ensures a secpath and XFRM state, records offload metadata, stores next-header offset information, and invokes `xfrm_input()` asynchronously, returning `-EINPROGRESS` to GRO. GSO validates `SKB_GSO_ESP`, strips ESP header/IV for segmentation, adjusts feature masks depending on hardware ESP capabilities, marks `XFRM_GSO_SEGMENT`, and dispatches by outer XFRM mode. Transmit computes ESP trailer sizes, prepares headers for GSO or non-GSO packets, updates offload sequence numbers, fixes IPv6 payload length, either marks the skb for hardware XFRM transmit or falls back to `esp6_output_tail()`.

## State and Persistence
Uses per-packet `struct xfrm_offload`, secpath entries, skb GSO flags, XFRM SA offload device metadata (`x->xso.dev`), and sequence counters in `xo->seq`. No persistent storage exists.

## Dependencies and Integration Points
Depends on `esp6.c` exported output/input helpers, XFRM offload core, IPv6 inet offload tables, GRO/GSO infrastructure, hardware feature bits such as `NETIF_F_HW_ESP`, and mode-specific inner protocol offloads.

## Risks and Test Signals
Risks include wrong next-header offset detection through extension headers, secpath leaks on GRO failure, sequence increments for GSO segment counts, feature-mask mismatch causing bad checksums, BEET IPv4/IPv6 header offset mistakes, and software fallback divergence from normal ESP. Test signals include GRO on ESP and ESP-in-UDP, GSO transport/tunnel/BEET, hardware ESP with and without TX checksum, fallback path, ESN sequencing across GSO, and invalid SPI/state direction rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/esp6_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs.c -->
# sources/distributed-fs/ceph-client/net/ipv6/exthdrs.c

## Purpose
Implements IPv6 extension-header receive handlers and outbound option construction. It parses hop-by-hop and destination TLVs, handles router alert, IOAM, jumbogram, CALIPSO, Mobile IPv6 HAO, routing headers including SRv6 and RPL source routing, registers inbound protocol handlers, and provides exported helpers for building and renewing transmit options.

## Important APIs, Types, and Functions
Receive-side functions include `ip6_parse_tlv()`, `ipv6_parse_hopopts()`, `ipv6_destopt_rcv()`, `ipv6_rthdr_rcv()`, `ipv6_srh_rcv()`, `ipv6_rpl_srh_rcv()`, `ipv6_hop_ra()`, `ipv6_hop_ioam()`, `ipv6_hop_jumbo()`, and `ipv6_hop_calipso()`. Registration uses `ipv6_exthdrs_init()`/`ipv6_exthdrs_exit()`. Outbound helpers include `ipv6_push_nfrag_opts()`, `ipv6_push_frag_opts()`, `ipv6_dup_options()`, `ipv6_renew_options()`, `__ipv6_fixup_options()`, and `__fl6_update_dst()`.

## Control Flow
Hop/destination parsing pulls enough header bytes, enforces sysctl length/count limits, validates padding, and dispatches known TLVs while applying unknown-option action bits. Routing-header processing validates destination and source-route policy, handles SRH/RPL segment advancement with route relookup and loopback recursion, decapsulates inner IPv4/IPv6 when segments are exhausted, and records offsets in `IP6CB`. Outbound helpers push headers in reverse order for TCP-style output, copy or replace socket options into a new `ipv6_txoptions`, and adjust flow destination when source-routing is configured.

## State and Persistence
Packet state is recorded in `struct inet6_skb_parm` (`IP6CB`) flags and offsets. Socket transmit options are refcounted `struct ipv6_txoptions` allocated from socket memory. Runtime behavior depends on per-net/per-device sysctls for option limits and SRv6/RPL/IOAM enablement.

## Dependencies and Integration Points
Depends on IPv6 protocol registration, addrconf, routing, ICMPv6 parameter problems, CALIPSO validation, IOAM namespaces/events, SRv6 HMAC, RPL compression helpers, XFRM Mobile IPv6 checks, and skb checksum adjustment. Datagram and routing code consume the exported option helpers.

## Risks and Test Signals
Risks include malformed TLV length/padding handling, option-count DoS limits, cloned skb mutation, checksum updates for SRH, RPL compression arithmetic, route-loop recursion, and source-routing policy bypass. Test signals include hop/destination fuzzing, sysctl max option limits, unknown TLV action bits, jumbogram validation, CALIPSO/IOAM/SRv6/RPL packets, MIPv6 HAO, outbound option replacement, and cmsg visibility of parsed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs_core.c -->
# sources/distributed-fs/ceph-client/net/ipv6/exthdrs_core.c

## Purpose
Provides small reusable IPv6 extension-header parsing primitives that are needed by both full IPv6 and static/library users. It classifies extension-header protocol numbers, skips extension header chains, locates TLVs, and finds a requested header or terminal protocol.

## Important APIs, Types, and Functions
Exports `ipv6_ext_hdr()`, `ipv6_skip_exthdr()`, `ipv6_find_tlv()`, and `ipv6_find_hdr()`. `ipv6_skip_exthdr()` reports final next header and fragment offset. `ipv6_find_hdr()` supports flags such as `IP6_FH_F_FRAG`, `IP6_FH_F_AUTH`, and `IP6_FH_F_SKIP_RH`.

## Control Flow
`ipv6_ext_hdr()` performs fixed protocol classification. `ipv6_skip_exthdr()` walks known extension headers from a caller-provided offset, bounds the number of parsed headers, treats non-first fragments as the end of parseable data, handles AH length specially, and returns `-1` for truncation or `NEXTHDR_NONE`. `ipv6_find_tlv()` validates an option header span and scans TLVs with PAD1/PADN semantics. `ipv6_find_hdr()` optionally starts at an inner IPv6 header, walks headers until the target or terminal protocol is found, handles fragments specially, and returns precise errno for malformed or absent headers.

## State and Persistence
No persistent state. All state is local parse cursor data and caller-provided output fields for offsets, fragment offsets, and flags.

## Dependencies and Integration Points
Depends on skb header accessors, IPv6/AH/fragment header formats, and exported symbols for ICMPv6, netfilter, XFRM, tunnels, and packet classifiers. `icmp.c`, `fou6.c`, `esp6.c`, and other IPv6 subsystems use these helpers to avoid open-coded parsing.

## Risks and Test Signals
Risks include semantic shortcuts that intentionally scan past headers despite RFC ordering concerns, truncated header handling, non-first fragment interpretation, AH stop conditions, and extension-header count limits. Test signals include packets with chained hop/destination/routing/AH/fragment headers, truncated skbs, nested IPv6 offsets, first and later fragments, `NEXTHDR_NONE`, and callers requesting target and terminal modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs_offload.c -->
# sources/distributed-fs/ceph-client/net/ipv6/exthdrs_offload.c

## Purpose
Registers IPv6 routing, destination-options, and hop-by-hop extension headers with the IPv6 offload table so GSO/GRO code recognizes them as extension headers during segmentation processing.

## Important APIs, Types, and Functions
Defines three `struct net_offload` instances, `rthdr_offload`, `dstopt_offload`, and `hbh_offload`, all with `INET6_PROTO_GSO_EXTHDR`. The sole function is `ipv6_exthdrs_offload_init()`, which registers offloads for `IPPROTO_ROUTING`, `IPPROTO_DSTOPTS`, and `IPPROTO_HOPOPTS`.

## Control Flow
Initialization registers routing-header offload first, destination-options second, and hop-by-hop third. On failure, it unwinds already registered entries in reverse dependency order and returns the registration error. There is no explicit exit function in this file; it is part of the IPv6 offload initialization lifecycle.

## State and Persistence
State is limited to entries installed in the global IPv6 offload registry. No per-packet or persistent storage is created here.

## Dependencies and Integration Points
Depends on `inet6_add_offload()`, `inet6_del_offload()`, `net/protocol.h`, and local `ip6_offload.h`. It integrates indirectly with transport GSO/GRO and XFRM offload paths that must step across IPv6 extension headers.

## Risks and Test Signals
Risks are mostly registration-order and cleanup bugs; missing registration would make segmentation treat extension headers incorrectly. Test signals include GSO packets carrying hop-by-hop, destination, and routing headers, module/init failure injection around each registration step, and offload table inspection through packet behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/exthdrs_offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fib6_notifier.c -->
# sources/distributed-fs/ceph-client/net/ipv6/fib6_notifier.c

## Purpose
Connects IPv6 FIB tables and policy rules to the generic FIB notifier framework. It provides IPv6-specific wrappers that tag events with `AF_INET6`, combines rule/table sequence counters, dumps current IPv6 routing state, and installs per-net notifier operations.

## Important APIs, Types, and Functions
Exports `call_fib6_notifier()` and `call_fib6_notifiers()`. Internal helpers include `fib6_seq_read()` and `fib6_dump()`. Per-net lifecycle is handled by `fib6_notifier_init()` and `fib6_notifier_exit()` using `fib6_notifier_ops_template`.

## Control Flow
Event wrappers set `info->family = AF_INET6` before calling generic notifier functions. The dump path emits IPv6 rules first via `fib6_rules_dump()` and then route tables via `fib6_tables_dump()`. Network namespace init registers a copy of the notifier ops template and stores it in `net->ipv6.notifier_ops`; exit unregisters it.

## State and Persistence
State is per-network-namespace `net->ipv6.notifier_ops`. Sequence values are derived from live FIB table and rule sequence counters. No persistent storage exists.

## Dependencies and Integration Points
Depends on generic `fib_notifier`, IPv6 FIB table/rule dump APIs, network namespace lifecycle, and module ownership. Consumers include switchdev/offload/listener components that need coherent IPv6 routing snapshots and change notifications.

## Risks and Test Signals
Risks include stale notifier ops during namespace teardown, incomplete dumps if rules or tables fail, and sequence mismatches causing missed resyncs. Test signals include namespace create/destroy, notifier registration, route/rule add/delete events, dump ordering, and simulated dump errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fib6_notifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fib6_rules.c -->
# sources/distributed-fs/ceph-client/net/ipv6/fib6_rules.c

## Purpose
Implements IPv6 routing policy rules. It extends generic `fib_rules` with IPv6 source/destination prefix, DSCP/TOS, flowlabel, protocol, port-range, l3mdev, suppressor, and source-address-selection behavior, while optimizing the default local/main-table lookup case.

## Important APIs, Types, and Functions
`struct fib6_rule` embeds `struct fib_rule` and adds `rt6key` source/destination selectors plus flowlabel/DSCP masks. Exported or externally used functions include `fib6_lookup()`, `fib6_rule_lookup()`, `fib6_rule_default()`, `fib6_rules_dump()`, `fib6_rules_seq_read()`, `fib6_rules_init()`, and `fib6_rules_cleanup()`. Rule ops include `fib6_rule_match()`, `fib6_rule_action()`, `fib6_rule_suppress()`, `fib6_rule_configure()`, `fib6_rule_delete()`, `fib6_rule_compare()`, and `fib6_rule_fill()`.

## Control Flow
Lookup bypasses the generic rules engine when no custom rules exist, checking local then main tables. With custom rules, it updates l3mdev flow fields and calls `fib_rules_lookup()` using either table lookup or policy lookup callbacks. Rule matching tests destination/source prefixes, deferred source selection via `FIB_RULE_FIND_SADDR`, DSCP, flowlabel, protocol, and ports. Rule actions select a table, return special blackhole/prohibit/unreachable routes, or ask the selected table/policy lookup for a route, then apply source-prefix and suppressor checks. Netlink configure/compare/fill paths validate DSCP masks, flowlabel masks, table IDs, and prefix attributes.

## State and Persistence
State lives per namespace in `net->ipv6.fib6_rules_ops`, `fib6_has_custom_rules`, and `fib6_rules_require_fldissect`. Default local/main rules are installed at namespace init. Rule contents are runtime netlink state, not persistent by this file.

## Dependencies and Integration Points
Depends on generic FIB rules, IPv6 FIB tables/routes, DSCP helpers, netlink attributes, l3mdev, route cache generation IDs, and namespace lifecycle. Route lookups, nft fib modules, and notifier dumps depend on these APIs.

## Risks and Test Signals
Risks include incorrect no-custom fast path, source-address deferral loops, DSCP/TOS ambiguity, invalid flowlabel masks, refcount handling on suppressed routes, field-dissector requirement leaks, and namespace batch unregister races. Test signals include `ip -6 rule` add/delete/dump/lookup, DSCP mask validation, flowlabel matching, sport/dport rules, l3mdev VRF rules, suppress prefix/group behavior, unreachable/prohibit/blackhole actions, and source-prefix rules without preset source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fib6_rules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fou6.c -->
# sources/distributed-fs/ceph-client/net/ipv6/fou6.c

## Purpose
Provides IPv6 tunnel encapsulation operations for Foo-over-UDP (FOU) and Generic UDP Encapsulation (GUE), when `CONFIG_IPV6_FOU_TUNNEL` is enabled. It builds UDP outer headers for IPv6 tunnel packets and routes ICMPv6 errors back to the encapsulated protocol handlers.

## Important APIs, Types, and Functions
Important functions are `fou6_build_udp()`, `fou6_build_header()`, `gue6_build_header()`, `gue6_err()`, `gue6_err_proto_handler()`, `ip6_tnl_encap_add_fou_ops()`, and `ip6_tnl_encap_del_fou_ops()`. Registration uses `struct ip6_tnl_encap_ops fou_ip6tun_ops` and `gue_ip6tun_ops`.

## Control Flow
Header build first calls common FOU/GUE builders to create the encapsulation-specific header and source port/GSO type, then pushes an IPv6 UDP header, sets ports and length, computes or suppresses UDP checksum according to tunnel flags, and changes the next protocol to UDP. Error handling validates that enough bytes are present, parses GUE version/control/options, supports direct IPv4/IPv6 encapsulation for version 1, rejects unsupported control/UDP-recursive cases, temporarily rewinds transport header relative to the ICMPv6 header, and calls the encapsulated protocol's registered IPv6 error handler.

## State and Persistence
State is limited to registered encapsulation ops. Per-packet state is skb header positions and tunnel encapsulation parameters. If the config is disabled, registration functions are no-ops.

## Dependencies and Integration Points
Depends on common FOU/GUE helpers, IPv6 tunnel encapsulation registry, UDP checksum helpers, IPv6 protocol table, and ICMPv6 error delivery. Integrates with `ip6_tunnel` and protocol-specific error handlers such as IPIP/IPV6.

## Risks and Test Signals
Risks include incorrect UDP checksum flag semantics, GUE option length validation, transport-header restoration after errors, recursion through UDP encapsulation, and config-dependent silent no-op behavior. Test signals include IPv6 FOU and GUE tunnel transmit, checksum/no-checksum modes, GSO tunnel type flags, ICMPv6 PMTU/error delivery for GUE direct IPv4/IPv6 and full GUE headers, malformed GUE versions/options, and module registration failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/fou6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/icmp.c -->
# sources/distributed-fs/ceph-client/net/ipv6/icmp.c

## Purpose
Implements ICMPv6 protocol receive, transmit, error generation, echo replies, upper-protocol notifications, per-net sysctls, and error-code conversion. It is the IPv6 control-message hub for PMTU, redirects, destination/time/parameter errors, neighbor discovery dispatch, ping sockets, and raw socket error reporting.

## Important APIs, Types, and Functions
Global state is per-CPU `ipv6_icmp_sk` control sockets. Main functions include `icmp6_send()`, `icmpv6_param_prob_reason()`, `ip6_err_gen_icmpv6_unreach()`, `icmpv6_echo_reply()`, `icmpv6_notify()`, `icmpv6_rcv()`, `icmpv6_flow_init()`, `icmpv6_init()`, `icmpv6_cleanup()`, `icmpv6_err_convert()`, and sysctl helpers `ipv6_icmp_sysctl_init()`/`ipv6_icmp_sysctl_table_size()`. Internal routing/rate helpers include `icmpv6_route_lookup()`, `icmpv6_xrlim_allow()`, and `icmpv6_global_allow()`.

## Control Flow
Receive validates XFRM policy, checksum, and header availability, updates ICMP stats, then dispatches echo requests to reply generation, echo replies to ping sockets, errors to `icmpv6_notify()`, and NDISC/MLD messages to their subsystems. `icmp6_send()` enforces RFC rules against replying to ICMP errors, multicast/anycast restrictions, source validity, global and per-destination rate limits, MIPv6 HAO source swapping, route/XFRM lookup, optional RFC4884/RFC5837 extensions, checksum construction, and pending-frame output. Notification parses inner extension headers, calls registered protocol error handlers, and reports to raw sockets.

## State and Persistence
Per-CPU raw control sockets carry outbound ICMP traffic and are temporarily rebound to the target net namespace under a socket spinlock. Per-net sysctls control ratelimit, echo ignore behavior, ratemask, anycast-as-unicast, and extension masks. Runtime stats are per-net/per-device ICMP/IP counters.

## Dependencies and Integration Points
Depends on IPv6 routing, XFRM, rawv6, ping, NDISC, MLD, SEG6 ICMP handling, netfilter conntrack attachment, l3mdev, sysctl, and socket/IP6 output APIs. Registers as final `IPPROTO_ICMPV6` inet6 protocol.

## Risks and Test Signals
Risks include recursive ICMP generation, rate-limit bypass or overdrop, wrong source/device selection for loopback/l3mdev/link-local traffic, extension object sizing, XFRM reverse-policy handling, and error notification for fragments/truncated packets. Test signals include checksum failures, echo sysctls, multicast/anycast echo behavior, PMTU and redirect delivery, RFC4884 extensions, protocol error callbacks, raw socket errors, per-net sysctl cloning, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/icmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/Makefile -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/Makefile

## Purpose
Builds the IPv6 Identifier Locator Addressing (ILA) module when `CONFIG_IPV6_ILA` is enabled.

## Important APIs, Types, and Functions
The Makefile declares `obj-$(CONFIG_IPV6_ILA) += ila.o` and composes `ila.o` from `ila_main.o`, `ila_common.o`, `ila_lwt.o`, and `ila_xlat.o`.

## Control Flow
Kbuild includes this directory's module objects only when the IPv6 ILA configuration symbol is selected. The linked object combines generic-netlink/pernet setup, checksum/address translation helpers, lwtunnel integration, and xlat mapping support.

## State and Persistence
The file itself has no runtime state. It determines whether ILA runtime state from the C sources is built and linkable.

## Dependencies and Integration Points
Depends on Kbuild and the `CONFIG_IPV6_ILA` symbol. It integrates ILA into the IPv6 networking build as a single module/object.

## Risks and Test Signals
Risks are limited to missing object membership or config mismatch. Test signals are successful builds with `CONFIG_IPV6_ILA=m/y`, module symbol availability, and link failures if any required object is omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila.h -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/ila.h

## Purpose
Defines shared ILA data structures and function declarations for locator/identifier address translation, lwtunnel support, per-network xlat state, and generic-netlink commands.

## Important APIs, Types, and Functions
Types include `struct ila_locator`, `struct ila_identifier`, `struct ila_addr`, `struct ila_params`, and `struct ila_net`. Inline helpers include `ila_a2i()`, `compute_csum_diff8()`, and `ila_csum_neutral_set()`. It declares `ila_update_ipv6_locator()`, `ila_init_saved_csum()`, lwt lifecycle functions, xlat pernet functions, xlat netlink command handlers, `ila_net_id`, and `ila_nl_family`.

## Control Flow
The header has no execution path but encodes the ILA address layout: IPv6 address high 64 bits are locator, low 64 bits are identifier, with bitfields for identifier type and checksum-neutral flag. `compute_csum_diff8()` constructs a checksum delta over two 64-bit locator values for later incremental checksum updates.

## State and Persistence
Defines per-translation parameters (`locator`, `locator_match`, precomputed checksum diff, checksum mode, identifier type) and per-net xlat hashtable/lock state. Actual allocation and lifecycle are in implementation files.

## Dependencies and Integration Points
Depends on kernel byte-order bitfield definitions, checksum APIs, genetlink, skbuff, IPv6 protocol headers, and UAPI `linux/ila.h`. It is shared by lwtunnel, xlat, common checksum, and module registration code.

## Risks and Test Signals
Risks include bitfield layout portability, aliasing `struct in6_addr` to `struct ila_addr`, checksum delta correctness, and keeping declarations synchronized with `ila_xlat.c`. Test signals include sparse/endian builds, formatted identifier parsing, checksum-neutral bit behavior, and genl/lwt users compiling against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_common.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_common.c

## Purpose
Provides common ILA locator update and checksum-adjustment logic shared by lwtunnel and xlat paths. It changes the destination locator portion of an IPv6 address while preserving or updating transport checksums according to the configured ILA checksum mode.

## Important APIs, Types, and Functions
Exports `ila_init_saved_csum()` and `ila_update_ipv6_locator()`. Internal helpers include `get_csum_diff_iaddr()`, `get_csum_diff()`, `ila_csum_do_neutral_fmt()`, `ila_csum_do_neutral_nofmt()`, and `ila_csum_adjust_transport()`.

## Control Flow
`ila_init_saved_csum()` precomputes a checksum delta when a fixed `locator_match` is known. `ila_update_ipv6_locator()` inspects `p->csum_mode`: it can update TCP/UDP/ICMPv6 checksums incrementally, apply formatted checksum-neutral mapping while toggling the C-bit, apply unformatted neutral mapping, or do nothing. After checksum handling, it writes the new locator into the IPv6 destination address.

## State and Persistence
State is carried in `struct ila_params`, especially precomputed `csum_diff`, locator values, and checksum mode. Packet mutation is in-place on the skb IPv6 destination and optional transport checksum field. No persistent storage exists.

## Dependencies and Integration Points
Depends on skb pull checks, TCP/UDP/ICMPv6 header definitions, incremental checksum helpers, and UAPI checksum mode constants. Called by `ila_lwt.c` and the xlat implementation.

## Risks and Test Signals
Risks include failing to parse extension headers before transport checksums, UDP zero checksum handling, checksum-neutral bit misuse, locator-match vs dynamic diff mistakes, and partial checksum state interactions. Test signals include TCP/UDP/ICMPv6 translations in each checksum mode, CHECKSUM_PARTIAL UDP packets, SIR-to-ILA and ILA-to-SIR neutral-map directions, malformed short transport headers, and checksum verification after locator replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_lwt.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_lwt.c

## Purpose
Implements ILA lightweight tunnel encapsulation for IPv6 routes. It lets routes translate destination locators on output or input, optionally cache the next dst for connected routes, and expose ILA parameters through lwtunnel netlink attributes.

## Important APIs, Types, and Functions
`struct ila_lwt` stores `struct ila_params`, a `dst_cache`, and flags for connected/output mode. Main callbacks are `ila_output()`, `ila_input()`, `ila_build_state()`, `ila_destroy_state()`, `ila_fill_encap_info()`, `ila_encap_nlsize()`, and `ila_encap_cmp()`. Registration uses `ila_lwt_init()` and `ila_lwt_fini()` with `LWTUNNEL_ENCAP_ILA`.

## Control Flow
Output validates IPv6, applies locator translation when configured for route output, then either calls the original route output for gateway/cache routes or looks up a route to the translated nexthop, applies XFRM lookup, optionally caches the dst, replaces skb dst, and sends via `dst_output()`. Input validates IPv6 and applies reverse translation for route-input hooks before calling original input. State build parses nested ILA attributes, validates IPv6 family, locator, identifier type, hook type, checksum mode, and checksum-neutral constraints, allocates lwtunnel state, initializes dst cache, precomputes checksum delta from route destination locator, sets redirect flags, and returns the new state.

## State and Persistence
Per-route lwtunnel state holds translation parameters and a dst cache. Connected routes may cache dsts if no reference loop is created. State is kernel route configuration, recreated from netlink route operations, not stored by this file.

## Dependencies and Integration Points
Depends on lwtunnel core, IPv6 route output, XFRM lookup, dst cache, netlink attributes from `linux/ila.h`, and `ila_update_ipv6_locator()`. It integrates with `ip -6 route encap ila ...` style route configuration.

## Risks and Test Signals
Risks include dst cache loops, route lookup after destination mutation, unsupported identifier formats, checksum-neutral invalid inputs, input/output hook confusion, and non-IPv6 skb drops. Test signals include route add/dump/delete with ILA encap, output and input hook translation, connected route cache hit/miss, XFRM interaction, invalid attr rejection, locator/checksum mode dump round-trip, and packet checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_lwt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_main.c -->
# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_main.c

## Purpose
Defines ILA module initialization, generic-netlink family operations, netlink attribute policy, and per-network namespace lifecycle. It wires the xlat mapping subsystem and lwtunnel support into a single module.

## Important APIs, Types, and Functions
Defines `ila_nl_policy`, `ila_nl_ops`, exported `ila_net_id`, and exported `struct genl_family ila_nl_family`. Netlink commands map to `ila_xlat_nl_cmd_add_mapping()`, delete, flush, get, and dump callbacks. Namespace functions are `ila_init_net()`, `ila_pre_exit_net()`, and `ila_exit_net()`. Module lifecycle is `ila_init()`/`ila_fini()`.

## Control Flow
Module init registers pernet device state first, then the generic-netlink family, then lwtunnel encap ops. Failure unwinds in reverse order. Netlink add/delete/flush require admin permission; get supports dump start/dump/done callbacks. Per-net init initializes xlat state; pre-exit and exit tear it down. Module exit unregisters lwtunnel ops, generic-netlink family, and pernet device state.

## State and Persistence
Per-net state size is `sizeof(struct ila_net)` and is referenced through `ila_net_id`. Generic-netlink family metadata is `__ro_after_init`. Xlat mappings are runtime netlink state owned by `ila_xlat.c`; this file manages lifecycle only.

## Dependencies and Integration Points
Depends on generic netlink, network namespace generic storage, ILA xlat implementation, ILA lwtunnel registration, and UAPI command/attribute constants. It is the module-level integration point for user-space ILA management.

## Risks and Test Signals
Risks include registration unwind leaks, net namespace teardown ordering, relaxed genl validation compatibility, admin permission enforcement, and lwt/xlat lifecycle ordering. Test signals include module load/unload, namespace creation/destruction, genl add/del/get/dump/flush commands, permission checks, and forced failure injection at each registration step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ipv6/ila/ila_main.c -->
