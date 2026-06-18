# subset-b-006240 netfilter ipset/IPVS research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmark.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmark.c

## Purpose

`ip_set_hash_ipmark.c` implements the `hash:ip,mark` ipset type. It stores a packet IP address paired with the skb mark, with an optional create-time mark mask. The type is usable from both packet path lookups and netlink userspace add/delete/test operations, and it delegates generic hash-table creation, lookup, timeout, extension, resize, and listing mechanics to `ip_set_hash_gen.h`.

## Important APIs, types, and functions

The file defines `struct hash_ipmark4_elem` with `ip` and `mark`, and `struct hash_ipmark6_elem` with an IPv6 `union nf_inet_addr` and `mark`. `hash_ipmark{4,6}_data_equal()` compares stored keys; `hash_ipmark{4,6}_data_list()` serializes elements as `IPSET_ATTR_IP` plus `IPSET_ATTR_MARK`; and `hash_ipmark{4,6}_data_next()` records restart state for bounded IPv4 range expansion. The generated variants expose `hash_ipmark_create` through the `ip_set_type` record. Packet path functions `hash_ipmark{4,6}_kadt()` read `skb->mark`, apply `h->markmask`, read source or destination IP according to `IPSET_DIM_ONE_SRC`, and call the generated ADT function. Userspace functions `hash_ipmark{4,6}_uadt()` validate netlink attributes, parse extensions, apply the mark mask, and run add/delete/test operations.

## Control flow

Module initialization registers `hash_ipmark_type` with family `NFPROTO_UNSPEC`, dimension two, and features `IPSET_TYPE_IP | IPSET_TYPE_MARK`. The generic hash include creates IPv4 and IPv6 implementations based on `HTYPE`, `MTYPE`, `HOST_MASK`, and `IP_SET_HASH_WITH_MARKMASK`. Packet lookups are direct: construct an element from packet fields, mask the mark, then dispatch through `set->variant->adt[adt]`. Userspace IPv4 operations optionally expand `IPSET_ATTR_IP_TO` or `IPSET_ATTR_CIDR`; when the operation exceeds `IPSET_MAX_RANGE`, the current element is copied into `h->next` and `-ERANGE` signals retry. IPv6 deliberately rejects IP ranges and accepts only `/128` CIDR.

## State and persistence behavior

Persistent state lives in the generic hash set allocation: the table, element extensions, timeout metadata, bucket size, init value, resize policy, and the `next` cursor used across retried range additions. The module itself keeps no global mutable state beyond registration. Mark masking is create-time set state and is applied both to packet lookups and userspace entries, so stored keys match runtime packet interpretation.

## Dependencies and integration points

This file depends on the ipset core, `ip_set_hash.h`, `pfxlen.h`, netlink attribute helpers, skb IP address helpers, and the generic hash generator. It integrates with xtables/nftables match/set paths through `kadt`, with userspace `ipset` netlink commands through `uadt`, and with kernel module loading through `MODULE_ALIAS("ip_set_hash:ip,mark")`.

## Risks

The special invalid element check rejects only the all-zero IP plus all-zero masked mark case, so callers must understand that a zero mark can still be valid with a nonzero IP. IPv4 range expansion is bounded by `IPSET_MAX_RANGE`; large ranges depend on retry correctness and `h->next`. IPv6 range support is intentionally absent. Any mismatch between markmask creation policy and userspace expectations can make rules appear not to match because marks are normalized before storage and lookup.

## Test signals

Useful tests create IPv4 and IPv6 `hash:ip,mark` sets with and without `markmask`, add/test/delete exact entries, exercise IPv4 `IP_TO` and `CIDR` expansion including retry-sized ranges, verify `/128`-only IPv6 behavior, check zero IP/zero mark rejection, list elements and confirm netlink mark serialization, and run packet-path tests where `skb->mark` is masked before matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipport.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipport.c

## Purpose

`ip_set_hash_ipport.c` implements the `hash:ip,port` ipset type. It matches an IP address plus transport protocol/port, with create-time netmask and bitmask support. The module handles packet decoding for IPv4 and IPv6 and userspace netlink add/delete/test operations, while generic hash mechanics come from `ip_set_hash_gen.h`.

## Important APIs, types, and functions

`struct hash_ipport4_elem` stores IPv4 address, port, protocol, and padding. `struct hash_ipport6_elem` stores IPv6 address, port, and protocol. `hash_ipport{4,6}_data_equal()` compares IP, port, and protocol; `data_list()` emits `IPSET_ATTR_IP`, `IPSET_ATTR_PORT`, and `IPSET_ATTR_PROTO`; and `data_next()` captures IP/port progress for range retries. `hash_ipport{4,6}_kadt()` extracts packet ports with `ip_set_get_ip{4,6}_port()`, extracts the configured packet address dimension, applies `h->bitmask`, rejects all-zero masked IPs, and dispatches the operation. `hash_ipport{4,6}_uadt()` validates netlink protocol/port/IP attributes, parses optional IP and port ranges, and handles protocols without ports by zeroing the port unless the protocol is ICMP/ICMPv6.

## Control flow

The file sets `IP_SET_HASH_WITH_NETMASK` and `IP_SET_HASH_WITH_BITMASK` before including the hash generator for IPv4 and IPv6. Userspace IPv4 control flow validates required IP and port attributes, gets extensions, masks the IP, parses `IPSET_ATTR_PROTO`, decides whether port ranges are meaningful, and either performs a single ADT call or nests IP and port loops. `IPSET_ATTR_CIDR` converts the IPv4 IP dimension into a host-order range; `IPSET_ATTR_PORT_TO` expands only for protocols with ports. IPv6 rejects IP ranges and non-host CIDR, but supports port range expansion for port protocols. The registered type advertises dimension two and features `IPSET_TYPE_IP | IPSET_TYPE_PORT`.

## State and persistence behavior

Stored elements are normalized by protocol and address bitmask. Generic hash state persists table allocation, timeouts, comments/counters/skbinfo extensions, bucket size, initval, resize policy, and range retry cursor. No file-local persistent data exists after registration.

## Dependencies and integration points

The module depends on `ip_set_getport.h` to parse packet ports, ipset netlink helpers for userspace attributes, `pfxlen.h` for CIDR/range conversion, and generic hash infrastructure. It is loaded via `MODULE_ALIAS("ip_set_hash:ip,port")` and used by iptables/nftables set match/target paths.

## Risks

The port field becomes zero for protocols without ports, which is correct but can surprise users who supply a port with AH/ESP-like protocols. ICMP and ICMPv6 use the port field to hold type/code style data and are special-cased. All-zero masked IPs are rejected, so broad bitmasks can make entries invalid. Large IPv4 IP x port products are bounded and require retry handling.

## Test signals

Tests should cover TCP/UDP/SCTP/UDPLITE port matching, ICMP and ICMPv6 behavior, non-port protocol normalization to port zero, IPv4 IP and port range expansion, IPv6 port range with rejected IP ranges, bitmask/netmask create options, all-zero masked IP rejection, extension preservation during list output, and packet-path source/destination dimension selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportip.c

## Purpose

`ip_set_hash_ipportip.c` implements `hash:ip,port,ip`, a three-dimensional ipset type for an address, transport protocol/port, and a second address. It is used when rules need to match tuples such as client address, service port, and peer address without the second address being interpreted as a network.

## Important APIs, types, and functions

`struct hash_ipportip4_elem` contains `ip`, `ip2`, `port`, and `proto`; the IPv6 variant uses two `union nf_inet_addr` fields. `hash_ipportip{4,6}_data_equal()` compares both addresses, port, and protocol. `data_list()` emits `IPSET_ATTR_IP`, `IPSET_ATTR_IP2`, `IPSET_ATTR_PORT`, and `IPSET_ATTR_PROTO`. Packet path `kadt` functions extract the port from dimension two and IP addresses from dimensions one and three. Userspace `uadt` functions require `IP`, `IP2`, `PORT`, and `PROTO`, support extension parsing, normalize non-port protocols to port zero, and expand first-address and port ranges where supported.

## Control flow

The module includes `ip_set_hash_gen.h` twice, once for IPv4 and once for IPv6. IPv4 userspace operations can expand `IPSET_ATTR_IP_TO` or `CIDR` for the first address and can expand `PORT_TO` for protocols with ports. The second address is parsed as a single address, not a range. IPv6 operations reject IP ranges and require any CIDR to equal `/128`, but still allow port range expansion. Single operations and `IPSET_TEST` go straight to the generated ADT path.

## State and persistence behavior

The generic hash layer stores normalized tuple elements and all enabled ipset extensions. IPv4 retry state stores the next first-address and port in `h->next`; IPv6 retry state stores only the next port. There is no global state beyond the registered `ip_set_type`.

## Dependencies and integration points

The file integrates with ipset core APIs, netlink attribute policies, packet port extraction helpers, and the generic hash implementation. Its type registration advertises `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_IP2`, dimension three, and `NFPROTO_UNSPEC`, allowing both address families under one module alias.

## Risks

Only the first IP dimension is range-expanded; users expecting `IP2_TO` support will not get it because the policy does not include it. Protocol handling mirrors `hash:ip,port`, so non-port protocols collapse the port to zero. Very large IPv4 IP/port expansions are capped by `IPSET_MAX_RANGE` and depend on retry cursor correctness.

## Test signals

Tests should add/test/delete IPv4 and IPv6 tuples, verify source/destination flag mapping for all three dimensions, exercise IPv4 first-IP CIDR/range plus port ranges, confirm IPv6 IP range rejection and port range acceptance, validate missing/zero protocol errors, and check list output for both IP attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportnet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportnet.c

## Purpose

`ip_set_hash_ipportnet.c` implements `hash:ip,port,net`, a three-dimensional ipset type matching an address, protocol/port, and a second address interpreted as a network. It supports `nomatch` entries and range expansion for IPv4 inputs, and it packs the `nomatch` flag into CIDR storage through the generic hash net support.

## Important APIs, types, and functions

IPv4 and IPv6 elements hold first IP, second network IP, port, CIDR, `nomatch`, and protocol. `hash_ipportnet{4,6}_data_equal()` compares IPs, CIDR, port, and protocol. `do_data_match()` returns `-ENOTEMPTY` for `nomatch` elements so the generic matcher can invert the result. `data_set_flags()` and `data_reset_flags()` translate `IPSET_FLAG_NOMATCH` between command flags and element state. `data_netmask()` normalizes `ip2` by CIDR and stores `cidr - 1`; `data_list()` emits `CIDR2`, `CADT_FLAGS`, protocol, port, and both IPs. The `kadt` functions build packet tuples from dimensions one, two, and three. The `uadt` functions parse IP, IP2, CIDR/CIDR2, port/proto, flags, ranges, and extensions.

## Control flow

For packet tests, the selected `ip2` address is masked by the default or lookup CIDR before calling the generated ADT operation; tests use host-width CIDR to allow generic net lookup across stored prefixes. Userspace single operations normalize `ip2` with `ip_set_hostmask(e.cidr + 1)` and apply `ip_set_enomatch()` so `nomatch` entries return the expected negative match. IPv4 range operations can expand the first IP range, port range, and second-IP range; the second range is converted to CIDR blocks with `ip_set_range_to_cidr()`. IPv6 rejects IP ranges and supports only port range expansion plus explicit `CIDR2` masking.

## State and persistence behavior

Generic hash state tracks per-CIDR network lookup metadata through `IP_SET_HASH_WITH_NETS` and packed CIDR layout. IPv4 retry state records first IP, port, and second IP in `h->next` for large Cartesian expansions. The stored `nomatch` bit is persistent element state and is serialized back through `CADT_FLAGS`.

## Dependencies and integration points

The file depends on `ip_set_getport.h`, `pfxlen.h`, ipset core netlink helpers, `ip_set_hash.h`, and generic hash macros `IP_SET_HASH_WITH_NETS_PACKED`, `IP_SET_HASH_WITH_PROTO`, and `IP_SET_HASH_WITH_NETS`. It registers the `hash:ip,port,net` module with `IPSET_TYPE_NOMATCH` so callers know negative entries are supported.

## Risks

The `cidr - 1` representation forbids CIDR zero for this packed type, so input validation is critical. IPv4 range products can grow quickly across first IP, port, and second network ranges; `IPSET_MAX_RANGE` only bounds per operation, not user surprise. `nomatch` handling depends on the caller passing and interpreting flags correctly. Protocols without ports force port zero except ICMP.

## Test signals

Tests should cover exact and network matches, `nomatch` behavior for add/test/list, IPv4 first-IP and second-IP range conversion into CIDR blocks, port range expansion and retry, IPv6 range rejection, `CIDR2` masking, ICMP/ICMPv6 and non-port protocol normalization, timeout/counter/comment/skbinfo listing, and packet-path dimension direction flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_ipportnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_mac.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_mac.c

## Purpose

`ip_set_hash_mac.c` implements the `hash:mac` ipset type. It stores one Ethernet MAC address per element and supports packet-path matching on source or destination Ethernet addresses plus userspace netlink management.

## Important APIs, types, and functions

`struct hash_mac4_elem` stores `ETH_ALEN` bytes in a union padded to two `__be32` words because generic hash code assumes zero-valued IP-like storage cannot represent a valid element. `hash_mac4_data_equal()` compares addresses with `ether_addr_equal()`, and `hash_mac4_data_list()` emits `IPSET_ATTR_ETHER`. `hash_mac4_kadt()` validates that the skb is on an Ethernet device with a usable MAC header, copies source or destination Ethernet address based on `IPSET_DIM_ONE_SRC`, rejects the all-zero address, and dispatches the generated ADT operation. `hash_mac4_uadt()` validates a six-byte netlink `ETHER` attribute, parses extensions, rejects the all-zero address, and calls the generated ADT function.

## Control flow

The module defines only one generated variant, with `NFPROTO_UNSPEC`, `IP_SET_PROTO_UNDEF`, and `IP_SET_EMIT_CREATE`; address family is irrelevant because matching happens at layer two. Create and ADT policies support generic hash options, timeouts, counters, comments, and skbinfo. Module init/fini register and unregister the type with an RCU barrier before unregister on unload.

## State and persistence behavior

Stored state is the generic hash table plus optional per-element extensions. The file keeps no file-local mutable state. Timeout, resize, bucket size, and init value behavior are inherited from the generated hash implementation.

## Dependencies and integration points

The file depends on Ethernet device/header helpers, ipset core, and the generic hash generator. It integrates with packet rules that can access `skb_mac_header`, and with userspace `ipset` commands through `IPSET_ATTR_ETHER`.

## Risks

Packet-path matching fails for non-Ethernet devices, skbs without a MAC header, short MAC headers, or zero MAC addresses. There is no IPv4/IPv6 split, so tests should not expect address-family filtering. Any caller using this on bridged or tunneled paths must ensure the skb still carries the intended Ethernet header.

## Test signals

Tests should create `hash:mac` sets, add/list/delete MAC addresses, reject zero and wrong-length addresses, match source and destination MACs from Ethernet skbs, verify non-Ethernet skb rejection, and exercise timeout/counter/comment/skbinfo extension behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_net.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_net.c

## Purpose

`ip_set_hash_net.c` implements `hash:net`, an ipset type whose element is one IP network prefix. It supports IPv4 range input, IPv6 exact-prefix input, and `nomatch` entries for negative matches.

## Important APIs, types, and functions

`struct hash_net4_elem` and `struct hash_net6_elem` store IP, CIDR, and `nomatch`. `hash_net{4,6}_data_equal()` compares normalized network address and CIDR. `do_data_match()`, `data_set_flags()`, and `data_reset_flags()` implement `IPSET_FLAG_NOMATCH`. `data_netmask()` masks the stored address to the requested prefix. `data_list()` serializes the address, `IPSET_ATTR_CIDR`, and optional `CADT_FLAGS`. `hash_net{4,6}_kadt()` extracts source or destination packet IP and masks it by the current lookup CIDR. `hash_net{4,6}_uadt()` parses userspace attributes, extensions, CIDR, flags, and optional IPv4 ranges.

## Control flow

The generic hash include is configured with `IP_SET_HASH_WITH_NETS`, so the generated lookup code can search stored prefixes. Packet tests use host-width CIDR to let generic net lookup iterate candidate prefixes. IPv4 userspace `uadt` converts a single entry into network form with `ip_set_hostmask(e.cidr)`, or expands `IP_TO` ranges by repeatedly selecting the largest CIDR block via `ip_set_range_to_cidr()`. IPv6 rejects `IP_TO` and only accepts explicit CIDR values from 1 to 128. Results pass through `ip_set_enomatch()` and `ip_set_eexist()` handling for consistent `nomatch` and `-exist` semantics.

## State and persistence behavior

The set stores normalized prefix entries, `nomatch` bits, and generic extensions. The IPv4 retry cursor stores the next IP in `h->next.ip`. Timed entries are handled by generic hash timeout machinery. The module does not persist state outside the ipset object.

## Dependencies and integration points

Dependencies include ipset core, generic hash, prefix length helpers, netlink address parsers, and packet IP address accessors. The registered type advertises `IPSET_TYPE_IP | IPSET_TYPE_NOMATCH`, dimension one, and supports revision features up to bucketsize/initval.

## Risks

CIDR zero is rejected for this type, so it cannot represent `/0` here. IPv4 `IP_TO` covering the entire 32-bit space is rejected by the overflow guard. `nomatch` behavior can invert tests unexpectedly if callers ignore `CADT_FLAGS`. Prefix normalization means listing may show masked network addresses rather than the exact input host.

## Test signals

Tests should cover IPv4 and IPv6 prefix add/test/delete, IPv4 range-to-CIDR decomposition, CIDR validation including zero rejection, `nomatch` outcomes, timeout cleanup, extension list output, packet source/destination lookups, and retry behavior for large IPv4 ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netiface.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netiface.c

## Purpose

`ip_set_hash_netiface.c` implements `hash:net,iface`, an ipset type matching an IP network plus network interface name. It supports physical bridge device matching, wildcard interface prefixes, `nomatch`, `/0` support, and generic ipset extensions.

## Important APIs, types, and functions

The hashed key structs omit the variable interface string from the key length used by the generated hash, while full element structs store `ip`, `physdev`, `cidr`, `nomatch`, `elem`, `wildcard`, and `iface[IFNAMSIZ]`. `hash_netiface{4,6}_data_equal()` first compares IP/CIDR, increments the `multi` counter for same-network multi-element checks, then compares physical-device bit and either exact interface name or wildcard prefix. `data_list()` emits IP, CIDR, interface name, and flags for physdev, wildcard, and nomatch. `get_physindev_name()` and `get_physoutdev_name()` integrate with bridge netfilter when configured. `kadt` functions read packet IP and either logical in/out interface or bridge physical interface. `uadt` functions parse IP, interface name, flags, CIDR, ranges, and extensions.

## Control flow

The file configures `IP_SET_HASH_WITH_NETS`, `IP_SET_HASH_WITH_MULTI`, and `IP_SET_HASH_WITH_NET0`; the last allows `/0` entries. Packet operations mask the packet IP by default CIDR and copy the selected interface name. Userspace IPv4 can add/delete/test exact entries or expand `IP_TO` into CIDR blocks. IPv6 rejects IP ranges. `IPSET_FLAG_PHYSDEV` switches packet-path interface selection to bridge physical devices if `CONFIG_BRIDGE_NETFILTER` is enabled; otherwise physdev requests cannot populate an interface and fail. `IPSET_FLAG_IFACE_WILDCARD` changes equality to prefix matching.

## State and persistence behavior

The set stores interface names in each element plus generic extensions and timeout state. The `multi` mechanism lets multiple interface entries share the same network hash key. Timed entries are handled by generic hash cleanup. Retry state for IPv4 stores the next IP block. The registered type carries no independent global state.

## Dependencies and integration points

Dependencies include bridge netfilter APIs, ipset net/hash infrastructure, IFNAMSIZ string handling, netlink parsers, and packet path `xt_action_param` interface state. The type exposes `IPSET_TYPE_IP | IPSET_TYPE_IFACE | IPSET_TYPE_NOMATCH`.

## Risks

Interface wildcard matching uses prefix comparison with the stored name length, so malformed or unintended prefixes can match broad device sets. Physdev behavior depends on `CONFIG_BRIDGE_NETFILTER`; without it, physdev packet matching can fail. Empty interface names are rejected on packet path. `/0` support is deliberate here and must be tested because many other hash net types reject CIDR zero.

## Test signals

Tests should cover exact interface matches, wildcard prefix matches, logical input/output dimension flags, bridge physdev matching when enabled, `/0` entries, IPv4 range expansion, IPv6 range rejection, `nomatch`, timeout cleanup, and list serialization of physdev/wildcard flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netiface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netnet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netnet.c

## Purpose

`ip_set_hash_netnet.c` implements `hash:net,net`, a two-dimensional ipset type storing two network prefixes. It supports `nomatch`, IPv4 range expansion on either network dimension, and create-time netmask/bitmask handling.

## Important APIs, types, and functions

IPv4 elements store two addresses in a union with a combined comparison field, plus two CIDRs and `nomatch`; IPv6 elements store two `union nf_inet_addr` values and combined CIDR comparison. `hash_netnet{4,6}_data_equal()` compares both normalized networks and both CIDRs. `data_reset_elem()` restores the inner network during generic multi-network matching. `data_netmask()` masks either outer or inner network based on the `inner` flag. `hash_netnet{4,6}_init()` sets both CIDRs to host width. `kadt` functions extract two packet address dimensions and apply netmask plus bitmask. `uadt` functions parse `IP`, `IP2`, `CIDR`, `CIDR2`, optional ranges, flags, and extensions.

## Control flow

The file sets `IPSET_NET_COUNT 2`, `IP_SET_HASH_WITH_NETS`, `IP_SET_HASH_WITH_NETMASK`, and `IP_SET_HASH_WITH_BITMASK` before including the generic hash code. Packet tests use host-width CIDRs for lookup and normalize both packet addresses. IPv4 userspace operations either perform a single normalized ADT call or expand outer and inner ranges by repeatedly converting ranges to CIDR blocks. IPv6 rejects `IP_TO` and `IP2_TO`; it masks both addresses by CIDR and bitmask, rejects all-zero host-width first addresses, and dispatches one operation.

## State and persistence behavior

Persistent set state includes two-prefix elements, bitmask/netmask configuration, `nomatch` bits, generic extensions, and hash network metadata for two network dimensions. Retry state stores both IP dimensions in `h->next`. There is no separate module-level mutable state after registration.

## Dependencies and integration points

The module integrates with generic ipset hash code for multi-network lookup and create policies. It depends on prefix/range helpers, IPv4/IPv6 masking helpers, and netlink attribute parsing. It registers features `IPSET_TYPE_IP | IPSET_TYPE_IP2 | IPSET_TYPE_NOMATCH`.

## Risks

Range expansion across two dimensions can generate many CIDR blocks and hit `IPSET_MAX_RANGE`. IPv6 does not support range input. Bitmask normalization can reject or alter user-provided host-width IPv6 addresses, especially all-zero first addresses. Because two CIDRs participate in equality, tests must verify both prefix lengths, not only addresses.

## Test signals

Tests should add/test/delete IPv4 and IPv6 network pairs, list both CIDRs, verify `nomatch`, exercise IPv4 `IP_TO` and `IP2_TO` expansion including retries, validate IPv6 range rejection, cover netmask/bitmask create options, and run packet-path tests selecting source/destination dimensions independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netport.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netport.c

## Purpose

`ip_set_hash_netport.c` implements `hash:net,port`, matching an IP network with protocol/port. It supports `nomatch`, IPv4 network and port ranges, IPv6 port ranges, and packed CIDR storage.

## Important APIs, types, and functions

Elements contain IP, port, protocol, packed CIDR, and `nomatch`. `hash_netport{4,6}_data_equal()` compares normalized network, port, protocol, and CIDR. `do_data_match()`, `data_set_flags()`, and `data_reset_flags()` implement `nomatch`. `data_netmask()` masks IP and stores `cidr - 1`. `data_list()` emits IP, port, `CIDR`, protocol, and optional flags. Packet-path `kadt` functions read packet port/protocol from dimension two, read the selected packet IP from dimension one, mask by current CIDR, and dispatch. Userspace `uadt` functions parse network, port, protocol, flags, optional ranges, and extensions.

## Control flow

The module enables `IP_SET_HASH_WITH_PROTO`, `IP_SET_HASH_WITH_NETS`, and `IP_SET_HASH_WITH_NETS_PACKED`. IPv4 single operations normalize `ip` by `ip_set_hostmask(e.cidr + 1)` and handle `nomatch` result translation. Range operations expand the IP range into CIDR blocks and loop through a port range when the protocol has ports. IPv6 rejects IP ranges, masks by CIDR, and only loops over ports. Non-port protocols store port zero except ICMP/ICMPv6.

## State and persistence behavior

State is in the generic hash table and per-element extensions. The packed CIDR representation is persistent on elements but serialized as `cidr + 1`. IPv4 retry state stores next IP and port. The module has no standalone mutable state.

## Dependencies and integration points

Dependencies include ipset core, generic hash code, transport port extraction helpers, prefix helpers, and netlink policies. The registered type advertises `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_NOMATCH`.

## Risks

CIDR zero is not supported because `cidr - 1` is stored. Large IPv4 network x port expansions can hit `IPSET_MAX_RANGE`. Non-port protocols silently normalize port to zero after validation. Correct `nomatch` behavior requires `CADT_FLAGS` to be preserved through add/test/list.

## Test signals

Tests should cover IPv4 and IPv6 network/port matches, protocol handling for TCP/UDP/SCTP/UDPLITE/ICMP, port range expansion, IPv4 network range expansion and retry, IPv6 IP range rejection, `nomatch`, CIDR validation, timeout and extension listing, and packet direction flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netportnet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netportnet.c

## Purpose

`ip_set_hash_netportnet.c` implements `hash:net,port,net`, matching an outer network, protocol/port, and inner network. It supports two network dimensions, `nomatch`, IPv4 range expansion including `/0`, and IPv6 exact-prefix operations.

## Important APIs, types, and functions

IPv4 and IPv6 elements contain two IP addresses, port, two CIDRs, `nomatch`, and protocol. `hash_netportnet{4,6}_data_equal()` compares both networks, both CIDRs, port, and protocol. `data_reset_elem()` restores the inner network during generated multi-network matching. `data_netmask()` masks either network depending on the `inner` flag. `hash_netportnet4_range_to_cidr()` special-cases the full IPv4 range as CIDR zero, unlike the standard range helper. `kadt` functions extract packet network dimensions one and three plus port dimension two. `uadt` functions parse two IPs, two CIDRs, optional two IP ranges, port/proto, flags, and extensions.

## Control flow

The module configures `IP_SET_HASH_WITH_PROTO`, `IP_SET_HASH_WITH_NETS`, `IPSET_NET_COUNT 2`, and `IP_SET_HASH_WITH_NET0`. Packet operations initialize both CIDRs from the set net metadata, use host-width CIDRs during tests, mask both packet IPs, and dispatch. IPv4 userspace single operations normalize both networks and translate `nomatch` results. Range operations nest outer network blocks, port values, and inner network blocks, storing retry progress in `h->next`. IPv6 rejects both IP range attributes and can only expand ports for port-bearing protocols.

## State and persistence behavior

The set stores two-prefix tuple elements, generic extensions, timeout state, and `nomatch`. IPv4 retry state includes outer IP, port, and inner IP. `/0` support is part of state semantics through `IP_SET_HASH_WITH_NET0` and the local range helper. There is no module-global runtime state beyond type registration.

## Dependencies and integration points

The file depends on the ipset generic hash/multi-network implementation, port extraction, prefix helpers, and netlink attribute policy. It registers as `hash:net,port,net` with features `IPSET_TYPE_IP | IPSET_TYPE_PORT | IPSET_TYPE_IP2 | IPSET_TYPE_NOMATCH`.

## Risks

IPv4 Cartesian expansion can be large because it combines two network ranges and a port range. `/0` support means full-range inputs are valid here and need special handling. Protocols without ports collapse port to zero. IPv6 users cannot use range attributes. `nomatch` and two-CIDR equality make regressions easy if list/test paths drop flags or prefix lengths.

## Test signals

Tests should cover exact tuple add/test/delete, outer and inner `/0`, IPv4 `IP_TO` and `IP2_TO` expansion, port ranges, retry after `IPSET_MAX_RANGE`, IPv6 range rejection, `nomatch`, list output for both CIDRs and flags, and packet-path dimension selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_netportnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_list_set.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_list_set.c

## Purpose

`ip_set_list_set.c` implements `list:set`, an ipset type whose elements are references to other ipsets. Packet operations walk the member sets in order and delegate add/delete/test to them. Userspace operations manage ordered membership, optional before/after placement, timeouts, and per-element extensions.

## Important APIs, types, and functions

`struct set_elem` is the RCU-protected list node storing the referenced set pointer, referenced set id, list head, and RCU head. `struct set_adt_elem` carries userspace add/delete/test input: target id, reference id, and before/after mode. `struct list_set` stores configured size, timeout GC timer, owning set, net namespace, and `members` list. Packet functions `list_set_ktest()`, `list_set_kadd()`, and `list_set_kdel()` iterate member sets and call `ip_set_test/add/del`. Userspace helpers `list_set_uadd()`, `list_set_udel()`, and `list_set_utest()` implement ordered membership semantics. `list_set_del()`, `list_set_replace()`, and `__list_set_del_rcu()` manage RCU deletion and reference release. `list_set_gc()` periodically removes expired elements.

## Control flow

Packet `kadt` takes an RCU read lock, builds kernel extensions, and dispatches by ADT. Test clears sub-counter matching flags to avoid unwanted nested counter lookup, then returns success only if a member set matches and the list element's own extensions match. Add/delete walk members until a sub-operation succeeds. Userspace `uadt` resolves `IPSET_ATTR_NAME` and optional `NAMEREF` to set ids, rejects loops by refusing member sets whose type has `IPSET_TYPE_NAME`, performs timeout cleanup before mutating timed lists, calls the variant ADT function, then drops references on error or non-add paths. Create initializes the list object, sets lockdep class, computes element size with extensions, and starts GC when timeout is configured.

## State and persistence behavior

Persistent state is the ordered RCU list of referenced set ids, per-element extensions, references held on member sets, optional timeout values, and the GC timer. Deletion and replacement release referenced set ids and free nodes after an RCU grace period. `flush` removes all members and extension size accounting. `cancel_gc` stops the timer and flushes references before destroy.

## Dependencies and integration points

The file depends on ipset core reference management, list extension helpers, RCU lists, net namespace lookup, timers, and netlink policies. It integrates deeply with other ipset types because every member operation delegates to `ip_set_test/add/del` by id. The registered type advertises `IPSET_TYPE_NAME | IPSET_DUMP_LAST`.

## Risks

Ordered before/after semantics are subtle, especially with expired entries skipped during lookup and possible replacement of timed-out slots. Reference management must pair every `ip_set_get_byname()` with `ip_set_put_byindex()` on all error paths. Packet add/delete semantics stop after the first successful member operation, which may hide later member failures. Loop detection prevents nested `list:set`, but only by checking `IPSET_TYPE_NAME`.

## Test signals

Tests should cover append, before, after, delete with reference constraints, duplicate add with and without `-exist`, timeout expiration and GC, flush/destroy reference release, packet test/add/delete delegation order, loop rejection, list dump pagination, counter/comment/skbinfo extensions on list elements, and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_list_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/pfxlen.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipset/pfxlen.c

## Purpose

`pfxlen.c` provides shared prefix-length helper data for ipset code. It exports precomputed IPv4/IPv6 netmask and hostmask maps and a helper that converts an IPv4 address range into the largest CIDR block starting at the range's left edge.

## Important APIs, types, and functions

`PREFIXES_MAP` is a macro-generated table of 129 four-word masks. `ip_set_netmask_map[]` exports network-order masks using `htonl()` for each word. `ip_set_hostmask_map[]` exports the same bit patterns as forced big-endian words for hostmask helper use. Both arrays are `union nf_inet_addr` and are exported with `EXPORT_SYMBOL_GPL`. `ip_set_range_to_cidr(u32 from, u32 to, u8 *cidr)` scans prefix lengths from 1 to 31, finds the largest aligned block whose last address does not exceed `to`, writes the CIDR, and returns the block's last address; if no broader block fits, it returns the single address with CIDR 32.

## Control flow

Consumers index the maps by prefix length for IPv4 or IPv6 masking. Range conversion is host-order IPv4 only: the loop checks alignment using `ip_set_hostmask(i)`, computes `last = from | ~ip_set_hostmask(i)`, and uses `after(last, to)` to avoid selecting a block beyond the requested range. The exported function is repeatedly called by hash set userspace add paths to decompose ranges into CIDR entries.

## State and persistence behavior

The file contains immutable exported tables and no runtime mutable state. The arrays persist for the lifetime of the module/kernel and are shared by ipset modules.

## Dependencies and integration points

Dependencies are limited to `linux/export.h` and `linux/netfilter/ipset/pfxlen.h`. Integration points include all ipset hash types that need `ip_set_netmask()`, `ip_set_hostmask()`, `ip6_netmask()`, or `ip_set_range_to_cidr()` for prefix normalization and range expansion.

## Risks

The maps must remain exactly aligned to prefix length indexes 0 through 128; any missing or reordered entry would corrupt every prefix match. `ip_set_range_to_cidr()` does not special-case the full IPv4 range as `/0`; callers that allow `/0` need their own wrapper, as `hash:net,port,net` does. The function assumes host-order IPv4 inputs.

## Test signals

Tests should validate masks at representative prefix lengths 0, 1, 31, 32, 33, 64, 96, 127, and 128; verify range-to-CIDR decomposition for aligned and unaligned ranges; confirm single-address `/32`; and include a caller-level test for full-range behavior where `/0` is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipset/pfxlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/Kconfig -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/Kconfig

## Purpose

`Kconfig` defines the build-time configuration surface for IP Virtual Server support. It gates the core IPVS module, protocol support, scheduler modules, application helpers, netfilter conntrack integration, persistence engines, debug support, IPv6 support, and hash-table sizing options.

## Important APIs, types, and functions

The central symbol is `IP_VS`, a tristate depending on `INET`, `NETFILTER`, and compatible `NF_CONNTRACK` state. `IP_VS_IPV6` adds IPv6 support and selects `NF_DEFRAG_IPV6`. `IP_VS_DEBUG` enables debug logging controlled at runtime by the IPVS sysctl. `IP_VS_TAB_BITS` configures the connection table size exponent, with architecture-dependent ranges. Protocol symbols include TCP, UDP, ESP/AH, and SCTP. Scheduler symbols include RR, WRR, LC, WLC, FO, OVF, LBLC, LBLCR, DH, SH, MH, SED, NQ, and TWOS. Helper symbols include `IP_VS_FTP`, `IP_VS_NFCT`, and `IP_VS_PE_SIP`.

## Control flow

Kconfig presents `IP_VS` as a menu. When disabled, all nested options are hidden. Enabling it exposes transport protocol choices, scheduler choices, SH/MH table sizing, application helper selection, connection tracking export, and SIP persistence. Dependencies enforce that FTP helper support is only available with TCP, conntrack, NAT, and FTP conntrack support; SIP persistence depends on UDP and SIP conntrack.

## State and persistence behavior

This file has no runtime state. Its selected symbols become compile-time configuration that controls which object files are built, which code branches compile, default connection table size, and which dependencies are selected.

## Dependencies and integration points

It integrates with the kernel Kconfig system and the adjacent IPVS Makefile. Runtime files such as `ip_vs_conn.c` read `CONFIG_IP_VS_TAB_BITS`, `CONFIG_IP_VS_IPV6`, `CONFIG_SYSCTL`, and protocol/helper symbols to include or exclude functionality.

## Risks

Incorrect dependencies can build modules without required protocol, NAT, conntrack, or defragmentation support. `IP_VS_TAB_BITS` has memory and performance implications; too small increases collision cost, too large wastes memory. Some scheduler/help text is user-facing, so symbol naming and dependency clarity affect configuration usability.

## Test signals

Tests are mostly build-matrix checks: core built-in/module/disabled, IPv6 enabled/disabled, each protocol and scheduler as module, FTP helper dependency failures, SIP persistence dependencies, conntrack export, and boundary values for `IP_VS_TAB_BITS`, `IP_VS_SH_TAB_BITS`, and `IP_VS_MH_TAB_INDEX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/Makefile -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/Makefile

## Purpose

`Makefile` maps IPVS Kconfig symbols to kernel object files. It defines the core `ip_vs` composite object, optional protocol objects, optional conntrack integration, scheduler modules, application helpers, and persistence engines.

## Important APIs, types, and functions

`ip_vs_proto-objs-y` is built from protocol-specific objects selected by `CONFIG_IP_VS_PROTO_TCP`, `UDP`, `AH_ESP`, and `SCTP`. `ip_vs-extra_objs-y` adds `ip_vs_nfct.o` when `CONFIG_IP_VS_NFCT` is enabled. `ip_vs-objs` combines connection management, core packet handling, control plane, scheduler framework, transmitters, app helpers, sync, estimator, protocol and persistence framework, plus selected protocol/extra objects. `obj-$(CONFIG_IP_VS)` builds the core composite. Individual `obj-$(CONFIG_IP_VS_*)` entries build scheduler and helper modules.

## Control flow

Kbuild evaluates the selected configuration symbols and expands the composite object lists. Core IPVS always includes common framework files when `IP_VS` is enabled, then appends enabled transport protocol and conntrack objects. Scheduler, FTP helper, and SIP persistence files are built as separate objects/modules according to their tristate symbols.

## State and persistence behavior

The file has no runtime state. It determines which code exists in the built kernel or modules and therefore which runtime features can register themselves.

## Dependencies and integration points

It integrates directly with the adjacent `Kconfig` symbols and the kernel Kbuild system. Runtime dependencies appear as link-time inclusion of files such as `ip_vs_conn.o`, `ip_vs_app.o`, `ip_vs_proto_tcp.o`, `ip_vs_rr.o`, `ip_vs_ftp.o`, and `ip_vs_pe_sip.o`.

## Risks

Missing an object in `ip_vs-objs` can produce unresolved symbols or silently remove core runtime behavior. Scheduler/helper entries must match Kconfig symbol names. Optional protocol object aggregation must stay synchronized with protocol registration expectations in IPVS core.

## Test signals

Build tests should enable each protocol, scheduler, helper, and persistence engine as built-in and module where allowed; verify `ip_vs.o` links with and without `IP_VS_NFCT`; and ensure module aliases/load paths work for scheduler and helper modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_app.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_app.c

## Purpose

`ip_vs_app.c` provides IPVS application-helper infrastructure. It lets protocol helpers such as FTP register application instances, bind helpers to IPVS connections, rewrite payload-related TCP sequence/ack numbers after packet mangling, expose helper state through procfs, and clean helper registrations per network namespace.

## Important APIs, types, and functions

Exported registration APIs are `register_ip_vs_app()`, `unregister_ip_vs_app()`, and `register_ip_vs_app_inc()`. `ip_vs_app_inc_new()` clones an app into a protocol/port incarnation, creates timeout tables if provided, and calls the protocol's `register_app` hook. `ip_vs_app_inc_release()` unregisters the incarnation and frees it through RCU. `ip_vs_app_inc_get()` and `ip_vs_app_inc_put()` pair module references with incarnation use counts. `ip_vs_bind_app()` delegates to protocol app binding, while `ip_vs_unbind_app()` calls helper unbind/done hooks and drops the incarnation reference. Packet hooks `ip_vs_app_pkt_in()` and `ip_vs_app_pkt_out()` call helper `pkt_in`/`pkt_out` callbacks and use `vs_fix_seq()`, `vs_fix_ack_seq()`, and `vs_seq_update()` for TCP sequence delta tracking.

## Control flow

Registration is serialized by `__ip_vs_app_mutex`. A base app is copied into `ipvs->app_list`, and incarnations are copied from that base and inserted into both protocol app state and the app's incarnation list. Packet processing checks `cp->app`; non-TCP helpers call callbacks directly, while TCP paths first ensure the TCP header is writable, adjust sequence/ack numbers based on prior payload length changes, invoke the helper callback, then update connection sequence delta state if the helper changed packet length. Procfs iteration locks the same mutex and walks all apps and incarnations.

## State and persistence behavior

Per-netns app state lives in `ipvs->app_list`. Each incarnation stores protocol, port, timeout table, use count, callback pointers, and parent app pointer. Connection-specific state lives in `cp->app`, `cp->app_data`, `cp->in_seq`, `cp->out_seq`, and sequence flags. Incarnations are RCU-freed after unregister, and module use counts prevent unloading while incarnations are active.

## Dependencies and integration points

The file depends on IPVS protocol hooks, module reference counting, RCU, procfs seq_file support, TCP header manipulation, skb writeability, and net namespace lifecycle. It integrates with `ip_vs_conn.c` connection creation/destruction, protocol modules that register helper ports, and helper modules such as FTP.

## Risks

Sequence delta logic is sensitive: incorrect `diff` handling can corrupt TCP streams after payload mangling. Helper callbacks run on packet paths and must handle writable skb failures. Registration and proc iteration share a mutex, while active packet users rely on module refs and RCU; lifetime regressions can lead to use-after-free or unload races. Per-netns cleanup must unregister all helpers before proc removal.

## Test signals

Tests should register duplicate and distinct apps, register incarnations for supported/unsupported protocols, bind/unbind helpers to connections, mangle TCP payload lengths and validate sequence/ack correction in both directions, exercise non-TCP callbacks, read `/proc/net/ip_vs_app`, and clean up network namespaces with active helper registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_app.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_conn.c -->
# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_conn.c

## Purpose

`ip_vs_conn.c` owns IPVS connection table management. It creates, hashes, looks up, rehashes, expires, flushes, lists, and frees `struct ip_vs_conn` objects. It also binds connections to destinations, transmit methods, application helpers, persistence engines, conntrack behavior, sync behavior, and per-netns resize/cleanup state.

## Important APIs, types, and functions

Hashing and lookup are built around `struct ip_vs_rht`, bucket bit locks, seqcounts, and dual hash nodes `hn0`/`hn1`. `ip_vs_conn_hashkey()`, `ip_vs_conn_hashkey_param()`, and `ip_vs_conn_hashkey_conn()` compute siphash keys. `ip_vs_conn_hash()` inserts new connections into the current table and schedules resizing. `ip_vs_conn_unlink()` removes only when the reference count shows no other users. Lookup APIs include `ip_vs_conn_in_get()`, `ip_vs_conn_in_get_proto()`, `ip_vs_ct_in_get()`, `ip_vs_conn_out_get()`, and `ip_vs_conn_out_get_proto()`. `ip_vs_conn_fill_cport()` safely rehashes no-client-port entries after the real client port is learned. `ip_vs_conn_new()` constructs and hashes new connections. Lifecycle functions include `ip_vs_conn_put()`, `ip_vs_conn_expire()`, `ip_vs_conn_expire_now()`, `ip_vs_conn_del()`, `ip_vs_conn_del_put()`, `ip_vs_conn_flush()`, and `ip_vs_conn_cleanup()`.

## Control flow

Initialization clamps `conn_tab_bits` to memory and architecture limits, computes `ip_vs_conn_tab_size`, and creates the connection slab cache. Per-netns init initializes counters, delayed resize work, conn table pointer, proc files, and default load factor. A new connection is allocated from the slab, initialized with client/virtual/destination tuple, flags, optional persistence data, timer, locks, destination binding, transmit function, app binding, conntrack flag, and finally inserted into the hash table. Incoming and outgoing packet lookup compute the appropriate tuple hash, walk current and transitional resize tables under RCU, compare tuple fields, and take a reference before returning.

Hash table resizing runs from `conn_resize_work_handler()`: it allocates a new table at the desired size/load factor, links it as `new_tbl`, waits for readers, migrates bucket chains under seqcount and bucket locks, publishes the new table, increments `conn_tab_changes`, waits for RCU readers, frees the old table, and reschedules shrink monitoring. No-client-port rehashing uses a similar seqcount-protected move so early fragments or protocols without initial client ports can later become normally keyed.

Expiration starts from timers or forced deletes. `ip_vs_conn_expire()` refuses to unlink while the connection controls children, otherwise unhashes when the refcount permits, handles control-chain release, drops conntrack if enabled and namespace is still active, unbinds app and destination, updates no-client-port counters, RCU-frees or directly frees one-packet connections, and decrements `conn_count`. If busy, it extends timeout and may sync the connection from master state. Flush loops over all buckets under RCU, expires un-controlled entries, waits until `conn_count` reaches zero, then unregisters and RCU-frees all resize-chain tables.

## State and persistence behavior

Per-connection state includes address/port tuples, protocol, forwarding flags, destination pointer, app pointer/data, persistence engine data, timer, refcount, control-chain counters, packet counters, sequence adjustment state, sync end time, and hash keys. Per-netns state includes the resizeable hash table, connection count, no-client-port counters, resize work item, table generation counter, dropentry counters, sysctls, and proc entries. State is in-memory only; synchronization code can mirror connection state to peer IPVS nodes, but this file does not persist it to disk.

## Dependencies and integration points

The file depends on IPVS core headers, RCU, hlist_bl locks, timers, delayed work, siphash/jhash/randomness, procfs, slab caches, protocol modules, destination/service lookup, transmit functions, app helpers, persistence engines, netfilter conntrack integration, sync, sysctl, and net namespace lifecycle. It exports lookup functions used by packet handling and flush/drop functions used by control/sysctl paths.

## Risks

Concurrency is the main risk. Resizing, no-client-port rehashing, lookup, and deletion rely on correct hash-key generation, table-id checks, seqcount retry, bucket lock ordering, RCU grace periods, and refcount transitions. Any mismatch can cause missed lookups, stale pointers, or double unlink. Destination counter updates must stay paired with bind/unbind, including templates and sync-created connections. Timer expiration cannot access conntrack after namespace cleanup disables IPVS. Random drop and flush paths must avoid deleting controlled connections prematurely.

## Test signals

Tests should cover incoming/outgoing lookup for NAT, DR, tunnel, localnode, bypass, IPv4 and IPv6, templates and persistence engines, no-client-port fill and rehash, resize growth/shrink under concurrent lookups, timer expiration of normal/template/controlled/one-packet connections, destination overload counter transitions, app binding/unbinding, conntrack drop behavior during namespace cleanup, proc listing across resize generations, random drop sysctl behavior, and full per-netns cleanup with active connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_conn.c -->
