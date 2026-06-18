# sources/distributed-fs/ceph-client/net/ipv6/ipcomp6.c

## Purpose
This file registers IPv6 IP Payload Compression Protocol support with XFRM. It wires generic IPComp compression/decompression into the IPv6 stack, initializes IPComp XFRM state for transport or tunnel mode, creates/attaches associated IPv6 tunnel states for tunnel-mode IPComp, and handles ICMPv6 PMTU/redirect errors for compressed packets.

## Important APIs, Types, And Functions
Main functions are `ipcomp6_err()`, `ipcomp6_tunnel_create()`, `ipcomp6_tunnel_attach()`, `ipcomp6_init_state()`, and `ipcomp6_rcv_cb()`. The protocol registration objects are `ipcomp6_type` (`struct xfrm_type`) and `ipcomp6_protocol` (`struct xfrm6_protocol`). Module lifecycle is `ipcomp6_init()` and `ipcomp6_fini()`.

The file uses generic IPComp helpers `ipcomp_init_state()`, `ipcomp_destroy()`, `ipcomp_input()`, and `ipcomp_output()`, plus IPv6 tunnel SPI allocation/lookup helpers `xfrm6_tunnel_alloc_spi()` and `xfrm6_tunnel_spi_lookup()`.

## Control Flow
When an IPComp XFRM state is created, `ipcomp6_init_state()` accepts transport and tunnel modes, sets header length to zero or one IPv6 header, delegates compression-algorithm initialization to generic IPComp, and for tunnel mode attaches an associated IPv6 tunnel state. Attachment first looks up an existing tunnel SPI for the source address and matching XFRM state; if none exists it allocates a new state, fills IPv6 tunnel identity, selector, family, mode, source, mark, and if_id, initializes it, inserts it into XFRM state tables, and increments tunnel user counts.

Inbound IPComp packets are received through `xfrm6_protocol_register()` with `xfrm6_rcv` and `xfrm_input`, then generic IPComp input handles decompression. ICMPv6 errors handled by `ipcomp6_err()` only process packet-too-big and redirect. It derives the IPComp CPI as an XFRM SPI, looks up the matching state by destination, mark, protocol COMP, and AF_INET6, then applies `ip6_redirect()` or `ip6_update_pmtu()`.

## State And Persistence
This file owns only static registration objects and a lock-class key. Runtime state lives in XFRM states. Tunnel-mode IPComp creates or references an associated XFRM tunnel state and increments `tunnel_users`. No state is persisted outside XFRM's in-kernel security association lifetime.

## Dependencies And Integration Points
The file depends on the XFRM type/protocol registry, generic IPComp implementation, IPv6 route/PMTU/redirect helpers, PF_KEY/IPComp UAPI definitions, and IPv6 tunnel SPI allocation. It registers protocol `IPPROTO_COMP` for AF_INET6 and declares `MODULE_ALIAS_XFRM_TYPE(AF_INET6, XFRM_PROTO_COMP)`.

## Risks And Edge Cases
Tunnel-mode attach is sensitive to reference counts: newly created tunnel states are inserted and held, then assigned to `x->tunnel` and counted with `tunnel_users`. Error paths must mark failed states dead and drop references. `ipcomp6_err()` assumes enough quoted bytes exist at the IPComp header offset; callers in the IPv6 protocol error path are expected to enforce that. Unsupported modes return `-EINVAL` with extack text.

## Test Signals
Coverage should include transport-mode and tunnel-mode IPComp SA creation, unsupported mode rejection, compression/decompression of IPv6 packets through XFRM, associated tunnel state reuse and creation, teardown reference counts, ICMPv6 packet-too-big updating PMTU for COMP states, redirect handling, malformed or unrelated ICMP errors being ignored, and module load/unload registration rollback on failure.
