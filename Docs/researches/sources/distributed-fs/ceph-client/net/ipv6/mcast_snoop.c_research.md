# sources/distributed-fs/ceph-client/net/ipv6/mcast_snoop.c

Purpose: Provides a reusable validator for bridge or snooping code that needs to identify sane IPv6 MLD packets without running the full IPv6 input stack.

Important APIs/types/functions: The exported API is `ipv6_mc_check_mld(struct sk_buff *skb)`. Helpers validate the IPv6 header, hop-by-hop extension chain, ICMPv6 checksum, MLD message type, MLDv2 report length, and MLD query rules. It uses `struct mld_msg`, `struct mld2_query`, `struct mld2_report`, `ipv6_skip_exthdr`, `ipv6_mc_may_pull`, `skb_checksum_trimmed`, and `ip6_compute_pseudo`.

Control flow: `ipv6_mc_check_mld` first verifies the IPv6 header version, payload length, and transport offset. It then requires a hop-by-hop option chain whose terminal next header is ICMPv6, trims/validates the ICMPv6 checksum, and classifies the ICMPv6 body. Queries must have link-local source addresses; general queries must target link-local all-nodes; v2 queries must have enough bytes for their fixed header. Reports and reductions are accepted after minimum-length checks.

State and persistence: The file is stateless. It mutates only skb header offsets and may allocate/free a temporary checksum-trimmed skb.

Dependencies/integration: Integrates through `EXPORT_SYMBOL(ipv6_mc_check_mld)` for multicast snooping users. It depends on IPv6 header parsing, ICMPv6 checksum helpers, and MLD structure definitions.

Risks and test signals: Risks are off-by-one payload length checks, incorrectly accepting non-hop-by-hop ICMPv6, checksum handling on non-linear skbs, and mismatched return-code semantics. Test signals include malformed extension chains, truncated MLDv1/v2 packets, bad checksums, non-link-local query sources, general queries not sent to ff02::1, and non-MLD ICMPv6 packets returning `-ENODATA`/`-ENOMSG` rather than hard validation errors.
