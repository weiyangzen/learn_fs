<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_gre.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_gre.c

## Purpose
Tracks GRE and PPTP-GRE flows. It extracts PPTP call IDs into conntrack tuple keys, maintains PPTP GRE keymaps installed by the PPTP helper, refreshes GRE timeouts, and exposes GRE timeout policy support.

## Important APIs, Types, and Functions
Exports `nf_ct_gre_keymap_add()` and `nf_ct_gre_keymap_destroy()` for PPTP. Core functions are `gre_pkt_to_tuple()`, `gre_keymap_lookup()`, `nf_conntrack_gre_packet()`, `nf_conntrack_gre_init_net()`, and the descriptor `nf_conntrack_l4proto_gre`. Per-net state is `struct nf_gre_net`, including `keymap_list` and timeout array.

## Control Flow
Tuple extraction first reads a GRE base header. Non-PPTP or non-version-1 GRE is treated like generic zero-key tracking. PPTP GRE requires PPP protocol and uses the destination call ID plus a source key found in the RCU keymap. Packet handling initializes per-connection GRE timeouts on first sight, then refreshes unreplied or stream timeout based on `IPS_SEEN_REPLY` and sets `IPS_ASSURED` unless the flow is a NAT clash.

## State and Persistence
Keymap entries are allocated per PPTP master connection, linked into a per-net RCU list under `keymap_lock`, and freed with `kfree_rcu()`. Each GRE conntrack stores timeout and stream_timeout in `ct->proto.gre`.

## Dependencies and Integration Points
Depends on GRE/PPTP headers, conntrack timeout APIs, expectations via the PPTP helper, and ctnetlink port tuple encoding. `nf_conntrack_proto_pernet_init()` initializes per-net lists and defaults; sysctl exposes GRE timeout knobs when GRE tracking is built.

## Risks
Keymap lookup is linear per namespace and must remain RCU-safe. Incorrect source/destination call-id mapping breaks PPTP NAT/data tracking. Non-PPTP GRE is intentionally weakly distinguished, which can collide for multiple GRE sessions between the same peers.

## Test Signals
Test plain GRE, PPTP GRE with and without NAT, retransmitted expectations, call teardown keymap cleanup, GRE reply promotion to ASSURED, ctnetlink timeout policies, and concurrent PPTP sessions in separate net namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_gre.c -->
