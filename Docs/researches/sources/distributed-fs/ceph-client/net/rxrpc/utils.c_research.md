# sources/distributed-fs/ceph-client/net/rxrpc/utils.c

Purpose: contains a small RxRPC utility for deriving a `sockaddr_rxrpc` peer address from an incoming skb.

Important APIs/functions: `rxrpc_extract_addr_from_skb()` zeroes the destination address and fills the UDP source endpoint for IPv4 or, when enabled, IPv6. It sets `transport_type`, `transport_len`, family, port, and address fields.

Control flow: the function switches on `skb->protocol`. For `ETH_P_IP`, it reads `udp_hdr(skb)->source` and `ip_hdr(skb)->saddr`; for `ETH_P_IPV6` under `CONFIG_AF_RXRPC_IPV6`, it reads `ipv6_hdr(skb)->saddr`; unsupported protocols log a rate-limited warning and return `-EAFNOSUPPORT`.

State and persistence: no persistent state. The caller-provided `sockaddr_rxrpc` is overwritten; skb contents are read only.

Dependencies and integration: used by RxRPC receive paths that need to identify or create peers from UDP packets. Depends on network header pointers already being valid and on Linux IPv4/IPv6/UDP header helpers.

Risks: it assumes the skb is already parsed far enough that IP and UDP header accessors are valid. Unsupported L2 protocol values are not recoverable here. IPv6 support is compile-time gated.

Test signals: IPv4 receive path address extraction, IPv6 builds with `CONFIG_AF_RXRPC_IPV6`, malformed or unexpected protocol skbs, and rate-limited warning coverage.
