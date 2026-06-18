# sources/distributed-fs/ceph-client/drivers/net/ovpn/skb.h

Purpose: Defines ovpn-specific skbuff control-block state and an IP-version validation helper.

Important APIs, types, and functions: `struct ovpn_cb` overlays `skb->cb` with `peer`, `ks`, `crypto_tmp`, `payload_offset`, and TCP `nosignal` metadata. `ovpn_skb_cb()` returns the overlay and enforces size at build time. `ovpn_ip_check_protocol()` pulls enough network header data and returns `ETH_P_IP`, `ETH_P_IPV6`, or zero.

Control flow: Crypto and transport paths stash peer/key/temp state in the skb control block while packets move asynchronously through encryption/decryption and TCP send. TX/RX logic uses `ovpn_ip_check_protocol()` before routing or accepting inner packets.

State and persistence behavior: Control-block data is per skb and transient. It must be cleared or not assumed once packets are handed to userspace or foreign networking layers.

Dependencies and integration points: It depends on skbuff, IPv4/IPv6 header helpers, socket types, and ovpn peer/crypto types through pointers. TCP receive explicitly clears `skb->cb` before queuing non-data packets to userspace.

Risks and edge cases: Any other subsystem reusing `skb->cb` can clobber ovpn metadata; handoff boundaries must be clear. Non-linear skbs require the pull checks in `ovpn_ip_check_protocol()`. The helper checks `ip_hdr(skb)->version`, so callers must have set the network header first.

Test signals: Check nonlinear IPv4/IPv6 skbs, too-short headers, unknown IP versions, control-block size build checks, async crypto completion preserving metadata, and userspace-forwarded TCP control packets not leaking ovpn private cb contents.
