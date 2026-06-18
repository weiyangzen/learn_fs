<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_pptp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_pptp.c

## Purpose
Implements the PPTP TCP control-channel conntrack helper. It tracks PPTP session/call state, extracts call IDs, installs GRE expectations for the data channel, tears those expectations or sibling GRE connections down on disconnect, and delegates packet mangling to optional NAT PPTP hooks.

## Important APIs, Types, and Functions
Public surface is `pptp_msg_name()` under debug builds and exported `nf_nat_pptp_hook`. Internal core functions are `conntrack_pptp_help()`, `pptp_outbound_pkt()`, `pptp_inbound_pkt()`, `exp_gre()`, `pptp_expectfn()`, `pptp_destroy_siblings()`, and `destroy_sibling_or_exp()`. Persistent helper state is `struct nf_ct_pptp_master` from `nfct_help_data(ct)`, including session state, call state, PNS/PAC call IDs, and GRE keymap pointers.

## Control Flow
The helper only inspects established TCP control packets. It parses the TCP header, PPTP packet header, control header, and bounded control union. Original-direction packets are treated as PNS to PAC and update state for session start/stop, outgoing call requests, incoming call replies, and call clear. Reply-direction packets validate server replies, save PAC call IDs, and call `exp_gre()` on accepted calls. NAT callbacks run after state validation when `IPS_NAT_MASK` is present.

## State and Persistence
State is per master control connection and protected by `nf_pptp_lock`. GRE expectations create two directional related flows, attach `pptp_expectfn()`, and create GRE keymap entries. When the data flow materializes, `pptp_expectfn()` extends GRE timeouts and removes the opposite expectation in non-NAT mode. Destroy paths remove keymaps and kill existing GRE siblings or pending expectations.

## Dependencies and Integration Points
Depends on TCP conntrack helper registration, conntrack expectations, zones, GRE conntrack keymaps, PPTP protocol structs, and optional `nf_nat_pptp_hook`. The registered helper covers IPv4 TCP destination port 1723 and exposes a two-expectation policy.

## Risks
The implementation assumes PNS to PAC is the original direction and supports only one call per session. Malformed or reordered control messages are logged but accepted, which avoids breaking traffic but can leave helper state stale. GRE keymap lifecycle depends on balanced expectation creation and destroy paths. NAT hook RCU dereferences and call-id rewriting are high-risk integration points.

## Test Signals
Test full PPTP outbound call setup, incoming-call paths, teardown, repeated call setup in one control session, NAT and non-NAT GRE expectations, duplicate/retransmitted control packets, truncated PPTP headers, wrong call IDs, and module unload while expectations exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_pptp.c -->
