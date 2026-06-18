# sources/distributed-fs/ceph-client/include/net/dst_metadata.h

Read `sources/distributed-fs/ceph-client/include/net/dst_metadata.h` completely for this pass (280 lines, 6779 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_metadata.h_research.md`.

Purpose: defines metadata destinations used to attach non-routing metadata to skbs, especially tunnel receive/transmit metadata, hardware port mux information, MACsec SCI data, and XFRM lwtunnel metadata.

Important APIs/types/functions: `enum metadata_type` distinguishes IP tunnel, hardware port mux, MACsec, and XFRM metadata. `struct metadata_dst` embeds a `dst_entry` flagged with `DST_METADATA` and a union of `ip_tunnel_info`, `hw_port_info`, `macsec_info`, or `xfrm_md_info`. Helpers include `skb_metadata_dst()`, `skb_tunnel_info()`, `lwt_xfrm_info()`, `skb_xfrm_md_info()`, `skb_valid_dst()`, `skb_metadata_dst_cmp()`, `metadata_dst_alloc/free`, per-CPU alloc/free, `tun_rx_dst()`, `tun_dst_unclone()`, `skb_tunnel_info_unclone()`, IPv4 `__ip_tun_set_dst()`/`ip_tun_rx_dst()`, and IPv6 `__ipv6_tun_set_dst()`/`ipv6_tun_rx_dst()`.

Control flow: tunnel receive paths allocate a metadata dst, initialize tunnel key fields from the outer IPv4/IPv6 header and tunnel flags/id, attach it to the skb, and pass the decapsulated packet onward. Transmit/external-mode tunnel paths retrieve metadata via `skb_tunnel_info()`. If a metadata dst must be modified, `tun_dst_unclone()` copies tunnel info, reinitializes embedded dst cache if present, replaces skb dst, and drops the old dst. Comparison helpers let flow paths decide whether two skbs carry identical metadata.

State and persistence: metadata dsts are per-skb transient dst objects. They may include embedded `dst_cache` state inside `ip_tunnel_info`, tunnel options of variable length, XFRM original dst pointers, or device pointers. They persist only while referenced by the skb or per-CPU metadata allocation.

Dependencies and integration points: depends on skbuff dst handling, IP/IPv6 header helpers, tunnel key APIs, MACsec SCI types, `dst.h`, optional `CONFIG_DST_CACHE`, and lwtunnel state. It is central to collect-metadata tunnels, OVS/TC tunnel offloads, MACsec, and XFRM lwtunnel paths.

Risks: `skb_valid_dst()` deliberately rejects metadata dsts as real routes. `skb_metadata_dst_cmp()` assumes both skb dsts are metadata when present and compares variable tunnel options by `options_len`. Unclone must preserve and reinitialize embedded dst cache correctly. Tunnel allocation is GFP_ATOMIC and can fail under pressure. Metadata dsts are not route dsts; passing them to normal output as routes is wrong.

Test signals: IPv4/IPv6 tunnel metadata allocation from outer headers, DF flag propagation, tunnel option compare, unclone with and without dst cache, external-mode tunnel transmit requiring metadata, MACsec/XFRM metadata retrieval, invalid metadata type compare, skb dst replacement/refcount tests, and allocation failure handling.
