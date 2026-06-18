# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_pptp.c

## Purpose
IPv4 NAT side of the PPTP conntrack helper. PPTP uses a TCP control channel plus GRE data flows whose call IDs must be translated consistently when the control session is NATed. The file installs `nf_nat_pptp_hook` callbacks so the PPTP parser can mangle control messages, rewrite GRE expectations, and NAT expected GRE connections.

## Important APIs, types, and functions
Key types are `struct nf_nat_pptp_hook`, `struct nf_conntrack_expect`, `struct nf_ct_pptp_master`, and NAT extension `struct nf_nat_pptp`. `pptp_outbound_pkt()` rewrites PNS-to-PAC call IDs with `nf_nat_mangle_tcp_packet()`. `pptp_inbound_pkt()` rewrites PAC-to-PNS peer call IDs. `pptp_exp_gre()` adjusts original and reply GRE expectations. `pptp_nat_expected()` applies NAT setup to child GRE connections. Init/fini publish and clear `nf_nat_pptp_hook` with RCU.

## Control flow
The conntrack PPTP helper calls inbound/outbound hooks after parsing TCP control packets. Outbound `PPTP_OUT_CALL_REQUEST` stores the original PNS call ID, derives the NATed ID from the reply tuple destination TCP port, updates conntrack PPTP state, and rewrites the payload. Other selected control messages rewrite fixed call ID fields or pass unchanged. GRE expectation setup patches tuple keys and directions. When an expected GRE connection appears, `pptp_nat_expected()` removes the opposite expectation if present and applies source/destination NAT ranges from the master control tuple and saved GRE key.

## State and persistence
All state is per conntrack entry: original and translated call IDs are stored in helper/NAT extension data, and GRE expectations live in conntrack expectation tables. The only global state is the RCU hook pointer for module lifetime.

## Dependencies and integration points
Depends on conntrack helper data, GRE conntrack tuple fields, NAT helper mangle support, expectation lookup, conntrack zones, and `nf_nat_setup_info()`. Integrates with the PPTP conntrack parser through `nf_nat_pptp_hook` and module autoloading through `MODULE_ALIAS_NF_NAT_HELPER("pptp")`.

## Risks
The file documents a limitation: translated call IDs are derived from the TCP source port instead of reserved as unique GRE tuples, so multiple calls inside one control session can break. Payload mangling failures drop packets. Direction and saved protocol handling must remain exact, and RCU unload must synchronize before module text disappears.

## Test signals
Test PPTP through SNAT/DNAT, GRE expectation creation in both directions, repeated calls in one control connection, packet mangle failures, and module load/unload while control traffic is active.
