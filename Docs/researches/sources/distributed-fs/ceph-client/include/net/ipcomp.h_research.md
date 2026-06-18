# sources/distributed-fs/ceph-client/include/net/ipcomp.h

Purpose: Declares the IPComp transform interface used by XFRM/IPsec compression processing and provides a header accessor for sk_buffs.

Important APIs/types/functions: The file forward-declares `ip_comp_hdr`, `netlink_ext_ack`, and `xfrm_state`. `ipcomp_input`, `ipcomp_output`, `ipcomp_destroy`, and `ipcomp_init_state` form the transform lifecycle: initialize compression state from netlink/XFRM config, compress/decompress packets, and release state. `ip_comp_hdr()` returns the transport header cast as an IPComp header.

Control flow: XFRM input/output implementation calls these functions after policy/state lookup. The inline accessor assumes the skb transport header already points at the IPComp header; it performs no validation itself.

State and persistence: Persistent transform state is owned by `struct xfrm_state` and the implementation. This header only exposes lifecycle hooks and carries no global state.

Dependencies/integration: Depends on sk_buff, XFRM state, and netlink extended ack reporting. It integrates with IPv4/IPv6 IPsec paths through XFRM rather than direct route/tunnel code.

Risks: Header pointer correctness is essential; callers must ensure linear/pulled transport header before casting. Compression state initialization needs clear extack errors for bad algorithms or unsupported parameters. Test signals include XFRM IPComp SA creation failure/success, packet input/output compression, malformed/truncated IPComp headers, transform destroy paths, and IPv4/IPv6 policy integration.
