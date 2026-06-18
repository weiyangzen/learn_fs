<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c

## Purpose
`ipsec.c` adds NFD3 TX descriptor checksum flags for packets using XFRM/IPsec hardware offload when the offload device advertises ESP TX checksum support.

## Important APIs, Types, And Functions
The only function is `nfp_nfd3_ipsec_tx(struct nfp_nfd3_tx_desc *txd, struct sk_buff *skb)`. It reads `xfrm_input_state()`, `xfrm_offload()`, and the skb IP header, then sets `NFD3_DESC_TX_CSUM`, optional `NFD3_DESC_TX_IP4_CSUM`, and TCP/UDP checksum flags.

## Control Flow
The function first checks that the XFRM state has an offload device with `NETIF_F_HW_ESP_TX_CSUM`. It marks checksum offload, adds IPv4 checksum when the outer header is IPv4, chooses L4 protocol from `xo->proto` in transport mode or `xo->inner_ipproto` in tunnel mode, and sets either UDP or TCP checksum flags. Unsupported modes or protocols leave only the generic checksum/IP flags already set.

## State And Persistence
There is no persistent state. It mutates only the in-flight NFD3 TX descriptor for one skb.

## Dependencies And Integration Points
This file is compiled only when `CONFIG_NFP_NET_IPSEC` enables the real prototype in `nfd3.h`; otherwise an inline no-op is used. It is called from `nfp_nfd3_tx()` after IPsec metadata has been prepared and instead of the generic checksum helper.

## Risks
The function assumes XFRM state/offload pointers are valid because the caller checked `xfrm_offload(skb)` and IPsec preparation succeeded. Unsupported protocols silently skip TCP/UDP flagging. Header interpretation uses `ip_hdr(skb)`, so callers must ensure skb network headers still point at the expected outer header after metadata prepend.

## Test Signals
Test ESP TX checksum with IPv4 and IPv6, transport and tunnel modes, TCP and UDP inner protocols, unsupported XFRM modes, offload devices without `NETIF_F_HW_ESP_TX_CSUM`, and interaction with the metadata-prepend path in `nfp_nfd3_tx()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/ipsec.c -->
