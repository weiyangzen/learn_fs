# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_proto_gre.h

Purpose: Declares GRE conntrack state and keymap helpers used to associate PPTP/GRE flows with conntrack tuples.

Important APIs, types, and functions: Important pieces are `struct nf_ct_gre`, `struct nf_ct_gre_keymap`, `nf_ct_gre_keymap_add()`, `nf_ct_gre_keymap_destroy()`, and `gre_pkt_to_tuple()`. Detected source surface: 30 lines; includes `net/netfilter/nf_conntrack_tuple.h`; macros `_CONNTRACK_PROTO_GRE_H`; structs `list_head`, `net`, `nf_conn`, `nf_conntrack_tuple`, `nf_ct_gre`, `nf_ct_gre_keymap`, `rcu_head`; enums none; typedefs none; function-like declarations/helpers `gre_pkt_to_tuple`, `nf_ct_gre_keymap_add`, `nf_ct_gre_keymap_destroy`.

Control flow: GRE packet handling extracts tuple keys from skb data, maps packet keys to conntrack tuple endpoints, and tears keymaps down when the owning connection is destroyed.

State and persistence behavior: Per-connection GRE state stores original/reply keys, while keymap entries are hlist nodes linked into lookup tables. Persistence is limited to conntrack lifetime.

Dependencies and integration points: Depends on conntrack tuple types and generic skb parsing. PPTP conntrack/NAT is the main higher-level integration point.

Risks and test signals: Risks are key collisions, endian mistakes in GRE keys, and missing cleanup on conntrack destruction. Test simultaneous PPTP calls, NAT-rewritten call IDs, and no-key GRE packets.
