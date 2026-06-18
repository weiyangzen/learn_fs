# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc_tun_mplsoudp.c

Purpose: implements MPLS-over-UDP, via BareUDP, tunnel operations for mlx5 TC. It builds UDP plus MPLS shim encapsulation and parses MPLS-over-UDP decap keys when hardware can match them.

Important APIs and types: static ops cover capability check for `reformat_l3_tunnel_to_l2`, header length calculation, encap attr init with `MLX5_REFORMAT_TYPE_L2_TO_L3_TUNNEL`, IP tunnel header generation, UDP port parsing, and MPLS tunnel parsing. The exported object is `mplsoudp_tunnel` with L4 match level and generic encap equality.

Control flow: header generation sets outer IP protocol to UDP, writes tunnel destination port, and encodes MPLS label, TTL, traffic class, and BOS from parsed MPLS info. Decap parsing first requires stateless MPLS-over-UDP or CW MPLS UDP flex parser support, rejects encap keyid, and if MPLS key exists supports matching only the first label stack entry. It maps first LSE label, EXP/TC, BOS, and TTL masks/values into misc2 fields and enables misc2 matching.

State and persistence: no local persistent state. It relies on parse attributes to carry MPLS info for encap and common encap caching for object lifetime.

Dependencies and integration points: Linux BareUDP and MPLS helpers, common tunnel UDP parsing, mlx5 Ethernet and generic capabilities, flow dissector MPLS keys, and misc2 hardware match fields.

Risks and test signals: limitations include no encap keyid matching, first-LSE-only matching, and capability-dependent parser support. Test with simple MPLS-over-UDP encap, first-label decap match, multiple LSE rejection, keyid rejection, TTL/TC/BOS masks, and capability-negative hardware.
