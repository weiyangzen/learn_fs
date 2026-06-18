# sources/distributed-fs/ceph-client/net/core/utils.c

## Purpose
This file provides generic networking utilities that are useful outside protocol-specific IPv4/IPv6 stacks: network printk rate limiting, IPv4/IPv6 literal parsing, address-with-scope parsing, wildcard address detection, and transport checksum update helpers.

## APIs, Types, and Functions
Exported APIs are `net_ratelimit()`, `in_aton()`, `in4_pton()`, `in6_pton()`, `inet_pton_with_scope()`, `inet_addr_is_any()`, `inet_proto_csum_replace4()`, `inet_proto_csum_replace16()`, and `inet_proto_csum_replace_by_diff()`. Internal helpers include `xdigit2bin()`, `inet4_pton()`, and `inet6_pton()`. The file defines global `net_ratelimit_state`.

## Control Flow, State, and Persistence
`net_ratelimit()` delegates to `__ratelimit()` with a 5-second, 10-message default. `in_aton()` performs a permissive dotted decimal parse into big-endian IPv4. `in4_pton()` strictly parses four decimal octets with delimiter handling and overflow rejection. `in6_pton()` implements a state machine for hex words, `::` compression, delimiters, and IPv4-embedded suffixes; when compression is used it backfills zero words into the destination. `inet_pton_with_scope()` parses optional ports and dispatches by address family, with AF_UNSPEC trying IPv4 then IPv6. IPv6 link-local scopes are resolved by device name in the given net namespace or numeric scope ID.

Checksum helpers update L4 checksum fields and, for `CHECKSUM_COMPLETE` IPv4 pseudoheader updates, adjust `skb->csum` consistently. IPv6 16-byte address replacement deliberately avoids changing `skb->csum` because address and L4 checksum changes cancel for complete checksums.

Persistent state is limited to the ratelimit token bucket. Parsing and checksum helpers are stateless.

## Dependencies and Integration
Depends on ratelimit infrastructure, hex conversion, socket address structures, IPv6 address type helpers, netdevice lookup for scope IDs, byte-order/checksum primitives, skb checksum state, and kernel string conversion helpers. It integrates with modules that need address parsing without pulling in full protocol-stack code and with NAT/tunnel/classifier paths that adjust checksums after address rewrites.

## Risks and Test Signals
Risks include permissive `in_aton()` accepting malformed values, parser delimiter edge cases, IPv6 compression/backfill mistakes, scope-name lookup races or netns mismatches, and checksum corruption for partial versus complete skb states. Test signals include IPv4/IPv6 parser unit vectors, embedded IPv4 IPv6 forms, link-local scope by name and number, wildcard address checks, checksum replacement tests across `CHECKSUM_NONE`, `CHECKSUM_COMPLETE`, and `CHECKSUM_PARTIAL`, and ratelimit behavior through sysctl-adjusted `message_cost`/`message_burst`.
