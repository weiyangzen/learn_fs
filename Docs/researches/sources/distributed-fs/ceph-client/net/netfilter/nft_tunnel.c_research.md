# sources/distributed-fs/ceph-client/net/netfilter/nft_tunnel.c

Purpose: nftables tunnel support: a netdev `tunnel` expression reads skb tunnel metadata, and a `NFT_OBJECT_TUNNEL` object attaches transmit tunnel metadata.

Important APIs/types/functions: `struct nft_tunnel`, `struct nft_tunnel_obj`, `nft_tunnel_get_eval()`, `nft_tunnel_obj_init()`, option parsers for IPv4/IPv6/VXLAN/ERSPAN/GENEVE, `nft_tunnel_obj_eval()`, and dump helpers.

Control flow: expression init validates key/dreg/mode and stores path or tunnel id from `skb_tunnel_info()` when mode matches. Object init builds `ip_tunnel_info`, requires tunnel id plus IP/IP6 endpoint, parses ports, flags, TOS/TTL, and options, allocates `metadata_dst`, then eval replaces skb dst metadata.

State and persistence: objects persist `metadata_dst` and option bytes until destroy; expressions only store register metadata. Dependencies include nf_tables netdev, dst metadata, ip_tunnels, vxlan, erspan, and geneve. Risks: option length/type validation, dst-cache failure unwind, unconditional dump fields, and RX/TX mode semantics. Test signals: no metadata, mode mismatch, IPv4/IPv6 objects, each option family, invalid mixed options, and dump/init round trip.
