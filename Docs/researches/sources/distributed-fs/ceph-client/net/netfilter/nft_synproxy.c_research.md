# sources/distributed-fs/ceph-client/net/netfilter/nft_synproxy.c

Purpose: nftables `synproxy` expression and `NFT_OBJECT_SYNPROXY` object for terminating client SYNs and validating SYN-cookie ACKs before traffic continues.

Important APIs/types/functions: `struct nft_synproxy`, `nft_synproxy_do_init()`, `nft_synproxy_do_eval()`, v4/v6 eval helpers, `nft_synproxy_obj_update()`, `nft_register_expr()`, and `nft_register_obj()`.

Control flow: init parses MSS/wscale/options, obtains conntrack support, and initializes per-net synproxy support for IPv4, IPv6, or inet. Eval requires TCP, verifies checksum, parses TCP options, replies to SYN with SYNACK, validates ACK, consumes handled skbs, and returns `NF_STOLEN`, `NF_DROP`, or `NFT_BREAK`.

State and persistence: per-rule/object `nf_synproxy_info`; per-net synproxy and conntrack references persist for rule lifetime; object update uses `WRITE_ONCE()`. Dependencies include nf_tables, nf_conntrack, nf_synproxy, TCP parsing, and IPv4/IPv6 support. Risks: packet ownership after `consume_skb()`, mixed-family init unwind, checksum/parser errors, and ref symmetry. Test signals: init/dump round trip, SYN/ACK paths, invalid flags/families, inet family cleanup, and module unload with objects.
