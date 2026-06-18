<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ao.h -->
# sources/distributed-fs/ceph-client/include/net/tcp_ao.h

Purpose: Defines TCP Authentication Option internal state, key layout, counters, option parsing hooks, hash/key derivation APIs, and no-op stubs for builds without TCP-AO.

Important APIs/types/functions: `union tcp_ao_addr` stores IPv4 or IPv6 address. `struct tcp_ao_hdr` maps TCP option fields and `tcp_ao_hdr_maclen()` derives MAC length. `struct tcp_ao_counters` tracks good/bad packets, key misses, required-AO drops, and dropped ICMPs. `struct tcp_ao_key` stores hlist node, address/prefix/family/l3index, raw master key, sigpool id, digest and MAC sizes, send/receive ids, RCU head, per-key counters, and two traffic keys. `struct tcp_ao_info` stores key list, cached current/rnext keys, counters, required/ICMP policy, initial sequence numbers, send/receive SNE, and refcount. IPv4/IPv6 context structs define pseudoheader key inputs. APIs cover transmit hashing, inbound hash validation, key lookup, established-key caching, key copy to child sockets, traffic-key calculation, SNE computation, reset preparation, socket option parsing/get/repair, timewait transfer, connect/established transitions, syncookie integration, and common parsing of AO/MD5 options.

Control flow: Userspace installs master keys through TCP-AO sockopts. During connect/listen/accept, AO initializes traffic keys from addresses, ports, and ISNs. Transmit paths choose current key, compute SNE, hash TCP header/payload, and write AO MAC. Receive paths parse auth options, lookup matching key by l3index/address/family/sndid/rcvid, compute expected hash, update counters, and drop or accept. Timewait and reset paths carry enough AO state to authenticate late packets or resets.

State and persistence behavior: AO state is per socket and RCU-managed. `current_key` and `rnext_key` are cached only for established states and require READ_ONCE/WRITE_ONCE if accessed without socket lock. SNE tracks upper sequence number extension to prevent replay across 32-bit sequence wrap. Static keys `tcp_ao_needed` and `tcp_md5_needed` gate overhead when unused.

Dependencies/integration points: Integrated from `tcp.h`, TCP option parser, MD5 compatibility paths, TCP syncookies, request/timewait sockets, IPv4/IPv6 pseudoheader hashing, sigpool crypto helpers, and sockopt get/set/repair paths.

Risks: Key lifetime, RCU, and refcounting are security-critical. Incorrect SNE basis can accept replayed segments or reject valid wraparound traffic. AO and MD5 option coexistence parsing must be unambiguous. Stubs must return `-ENOPROTOOPT` or neutral values consistently when AO is disabled.

Test signals: TCP-AO selftests for IPv4/IPv6, key rotation, current/rnext behavior, listener-to-child copy, timewait, reset, syncookie, ICMP ignore policy, SNE wraparound, repair sockopts, AO-required drops, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tcp_ao.h -->
