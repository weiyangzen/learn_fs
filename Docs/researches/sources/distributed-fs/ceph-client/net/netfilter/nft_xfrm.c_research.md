# sources/distributed-fs/ceph-client/net/netfilter/nft_xfrm.c

Purpose: nftables `xfrm` expression extracts IPSec/XFRM state fields into nft registers.

Important APIs/types/functions: `struct nft_xfrm`, `nft_xfrm_get_init()`, `xfrm_state_addr_ok()`, `nft_xfrm_state_get_key()`, `nft_xfrm_get_eval_in()`, `nft_xfrm_get_eval_out()`, and `nft_xfrm_validate()`.

Control flow: init validates family, key, direction, transform depth, and destination register size. Eval reads inbound state from `skb_sec_path()` or outbound state by walking `xfrm_dst` children, then stores reqid, SPI, source, or destination address, breaking when state is absent or incompatible.

State and persistence: immutable expression metadata only. Dependencies include nf_tables, XFRM state, secpath, dst xfrm chains, and hook validation. Risks: address keys only valid for matching family and BEET/TUNNEL/IPTFS modes, missing dst/secpath, and register length mismatch. Test signals: inbound/outbound hooks, all keys, multiple `spnum` depths, transport mode address failures, unsupported families, and dump parity.
