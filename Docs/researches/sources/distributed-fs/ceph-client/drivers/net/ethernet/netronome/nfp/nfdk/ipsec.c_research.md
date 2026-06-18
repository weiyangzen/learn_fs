# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/ipsec.c

## Purpose
Adds a small NFDK TX helper for IPsec checksum flagging when `CONFIG_NFP_NET_IPSEC` is enabled. It adjusts descriptor metadata flags after IPsec preparation has identified an offloaded packet.

## Important APIs, Types, and Functions
- `nfp_nfdk_ipsec_tx(u64 flags, struct sk_buff *skb)` checks `xfrm_input_state(skb)` and the skb IP header, then ORs `NFDK_DESC_TX_L3_CSUM` for IPv4 and `NFDK_DESC_TX_L4_CSUM` when the offload device advertises `NETIF_F_HW_ESP_TX_CSUM`.

## Control Flow
`nfp_nfdk_tx()` in `nfdk/dp.c` calls this helper only after IPsec metadata was prepared. The helper reads XFRM state and IP version, modifies the existing NFDK metadata flags, and returns the updated flags used in the TX metadata descriptor.

## State and Persistence Behavior
No persistent or owned state. It reads skb/XFRM state and device feature bits and returns a modified flag word.

## Dependencies and Integration Points
Depends on Linux XFRM state, SKB IP header helpers, NFDK descriptor flag definitions in `nfdk.h`, and `nfp_net` IPsec feature negotiation. It is declared conditionally in `nfdk.h`; when IPsec is disabled, the inline stub returns flags unchanged.

## Risks
The helper assumes `xfrm_input_state(skb)` is valid on the offloaded TX path and that `ip_hdr(skb)` is meaningful for the packet. Incorrect call ordering or malformed skb headers could set wrong checksum flags.

## Test Signals
Exercise ESP TX checksum offload for IPv4 and IPv6, compare descriptor flags, and verify fallback behavior when `NETIF_F_HW_ESP_TX_CSUM` is absent. Build coverage should include both `CONFIG_NFP_NET_IPSEC=y` and disabled configurations.
