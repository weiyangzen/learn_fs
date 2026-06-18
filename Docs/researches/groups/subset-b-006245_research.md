<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c

## Purpose
Provides conntrack support routines used outside the normal netfilter hook path, specifically by Open vSwitch and TC conntrack actions. It centralizes helper invocation, TCP sequence adjustment after helper/NAT mangling, network-length trimming, and IPv4/IPv6 fragment reassembly for these callers.

## Important APIs, Types, and Functions
The exported APIs are `nf_ct_helper()`, `nf_ct_add_helper()`, `nf_ct_skb_network_trim()`, and `nf_ct_handle_fragments()`. `nf_ct_helper()` finds the `nf_conn_help` extension, validates helper family and L4 protocol, calls `helper->help()`, then applies `nf_ct_seq_adjust()` when `IPS_SEQ_ADJUST_BIT` is set. `nf_ct_add_helper()` attaches helper state and optionally loads the matching NAT helper. `nf_ct_skb_network_trim()` trims padding based on IPv4 total length or IPv6 payload/HBH length. `nf_ct_handle_fragments()` wraps `ip_defrag()` and `nf_ct_frag6_gather()`.

## Control Flow
OVS/TC callers pass an skb already positioned at the network header. Helper execution skips related replies, connections without helpers, nonmatching families, and nonmatching L4 protocols. IPv4 uses `ip_hdrlen()`; IPv6 skips extension headers and refuses non-first fragments. Fragment handling chooses the per-zone defrag user, clears IP control blocks, gathers fragments, records MRU/next header, clears packet hashes, and sets `ignore_df`.

## State and Persistence
The file stores no durable state. It mutates per-connection helper and sequence-adjust extensions, skb length/hash/control-block fields, and fragment-derived MRU state returned to callers. Helper and NAT helper module references acquired by `nf_ct_add_helper()` persist through the connection helper extension.

## Dependencies and Integration Points
Depends on conntrack helper and seqadj APIs, IPv4/IPv6 defrag, IPv6 extension parsing, and NAT helper loading when enabled. Direct callers include `net/openvswitch/conntrack.c` and `net/sched/act_ct.c`.

## Risks
Incorrect protocol-offset calculation breaks helpers and sequence adjustment. IPv6 extension parsing deliberately ignores later fragments, so callers must defragment before helper inspection where needed. `nf_ct_handle_fragments()` may steal or free skbs, making return-code handling critical. NAT helper loading must stay paired with conntrack helper references.

## Test Signals
Exercise OVS and TC CT actions with FTP/SIP-style helpers, NAT payload mangling, IPv4 fragments, IPv6 fragments, IPv6 HBH padding, unsupported families, and helper module load failures. Packet counters should show drops only on helper failures, seqadj failures, or defrag errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c

## Purpose
Provides the protocol-family glue for core conntrack: L4 protocol lookup, IPv4/IPv6 hook registration, confirmation-time helper/seqadj execution, original-destination sockopts, per-net hook reference counting, bridge conntrack registration, and per-net protocol timeout initialization.

## Important APIs, Types, and Functions
Exports `nf_l4proto_log_invalid()`, `nf_ct_l4proto_log_invalid()`, `nf_ct_l4proto_find()`, `nf_confirm()`, `nf_ct_netns_get()`, `nf_ct_netns_put()`, `nf_ct_bridge_register()`, and `nf_ct_bridge_unregister()`. Lifecycle functions are `nf_conntrack_proto_init()`, `nf_conntrack_proto_fini()`, and `nf_conntrack_proto_pernet_init()`. `getorigdst()` and `ipv6_getorigdst()` back `SO_ORIGINAL_DST` and `IP6T_SO_ORIGINAL_DST`.

## Control Flow
`nf_ct_l4proto_find()` maps TCP, UDP, ICMP, ICMPv6, SCTP, GRE, or generic trackers. `nf_confirm()` retrieves the skb conntrack, skips VRF postrouting and related replies, computes the L4 offset, invokes any helper, applies seqadj when needed, and confirms the entry. `nf_ct_netns_get()` enables defrag and registers PRE_ROUTING/LOCAL_OUT/confirm hooks per family; `nf_ct_netns_put()` unregisters them when per-net users drop to zero.

## State and Persistence
State is global `nf_ct_proto_mutex`, global `nf_ct_bridge_info`, per-net `nf_conntrack_net` users for IPv4/IPv6/bridge, and per-net protocol timeout structures initialized here. Hook registration persists while namespace user counts are nonzero. TCP fixup resets max window tracking when hooks are newly enabled for existing established entries.

## Dependencies and Integration Points
Depends on netfilter hooks, IPv4/IPv6 defrag, conntrack core, helpers, seqadj, NAT helper declarations, bridge conntrack, sockopt registration, route/IP headers, and per-protocol init functions. It is the entry point used by nftables, iptables, OVS, bridge, and flow-table paths to enable conntrack in a namespace.

## Risks
Hook user counts and bridge module references must remain balanced. Confirmation ordering matters because helpers may mangle packets before seqadj and final confirmation. `SO_ORIGINAL_DST` tuple reconstruction only supports TCP/SCTP and depends on socket locking. IPv6 extension parsing in `nf_confirm()` must avoid handing helpers non-first fragments.

## Test Signals
Validate IPv4/IPv6 conntrack enable/disable cycles, bridge autoload, `SO_ORIGINAL_DST` for redirected TCP/SCTP, helper execution before confirmation, seqadj after NAT helper mangling, VRF postrouting skip, and sysctl-driven invalid packet logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c

## Purpose
Implements the fallback L4 protocol descriptor for protocols without a dedicated conntrack tracker. Its main behavior is default timeout storage and optional ctnetlink timeout-policy serialization.

## Important APIs, Types, and Functions
Defines `nf_conntrack_l4proto_generic` with `.l4proto = 255` and `.allow_clash = true`. `nf_conntrack_generic_init_net()` initializes `nf_generic_pernet(net)->timeout` to `600*HZ`. Timeout netlink support is implemented by `generic_timeout_nlattr_to_obj()`, `generic_timeout_obj_to_nlattr()`, and `generic_timeout_nla_policy`.

## Control Flow
There is no packet-specific state machine in this file. Core conntrack uses the generic descriptor when `nf_ct_l4proto_find()` does not match a known protocol. Timeout policy parsing either updates the supplied object or the per-net default from `CTA_TIMEOUT_GENERIC_TIMEOUT`.

## State and Persistence
The only persistent state is the per-network-namespace generic timeout value and optional timeout-policy objects maintained by the timeout subsystem. The descriptor itself is static read-only protocol metadata.

## Dependencies and Integration Points
Depends on `nf_conntrack_l4proto.h`, timeout extensions, and ctnetlink timeout attributes when enabled. It integrates with `nf_conntrack_proto_pernet_init()` and the standalone sysctl entry `nf_conntrack_generic_timeout`.

## Risks
Generic tracking lacks protocol validation, so it can retain ambiguous flows for the configured timeout. Timeout netlink conversion must consistently use seconds in netlink and jiffies internally.

## Test Signals
Create conntrack entries for unsupported protocols, tune `nf_conntrack_generic_timeout`, configure ctnetlink timeout policies, and verify expiration uses the per-net or policy-specific value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c

## Purpose
Implements IPv4 ICMP conntrack tuple handling, echo-like flow tracking, ICMP error correlation to existing connections, netlink tuple encoding, and timeout policy support.

## Important APIs, Types, and Functions
Key functions are `icmp_pkt_to_tuple()`, `nf_conntrack_invert_icmp_tuple()`, `nf_conntrack_icmp_packet()`, `nf_conntrack_inet_error()`, and `nf_conntrack_icmpv4_error()`. Descriptor `nf_conntrack_l4proto_icmp` provides netlink tuple policy and timeout policy operations. Default timeout is `30*HZ`.

## Control Flow
Tuple extraction records ICMP type, code, and echo ID. New ICMP flows are allowed only for request-like types in `valid_new`; replies share the inverted tuple via `invmap`. ICMP errors validate header length, checksum on PREROUTING when enabled, known type range, and whether the type is an error. Error packets parse the embedded inner tuple, invert it, find the related conntrack in the right zone, and ensure the outer destination matches the found tuple destination before setting skb conntrack to RELATED.

## State and Persistence
State is limited to per-net ICMP timeout and skb conntrack association for RELATED errors. ICMP entries keep normal core conntrack state and accounting, but no extra protocol-private mutable fields are stored.

## Dependencies and Integration Points
Depends on IPv4 header/checksum helpers, conntrack tuple/core/zone APIs, timeout extension, netlink conntrack attributes, and invalid logging. It shares `nf_conntrack_inet_error()` with ICMPv6-style error correlation.

## Risks
Incorrect outer/inner destination validation can mark unrelated errors as RELATED. ICMP type inversion tables must cover only request/reply pairs. Accepting non-error ICMP in the error path avoids overtracking but makes tests sensitive to type selection.

## Test Signals
Verify echo, timestamp, info, and address request/reply tracking; invalid new ICMP types; bad checksums; short packets; related errors for TCP/UDP flows; forged outer-destination mismatch logs; and ctnetlink ICMP tuple filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c

## Purpose
Implements IPv6 ICMPv6 conntrack tuple handling, echo and node-information tracking, ICMPv6 error/redirect correlation, untracked handling for local control messages, and timeout/netlink support.

## Important APIs, Types, and Functions
Important functions are `icmpv6_pkt_to_tuple()`, `nf_conntrack_invert_icmpv6_tuple()`, `nf_conntrack_icmpv6_packet()`, `nf_conntrack_icmpv6_error()`, and `nf_conntrack_icmpv6_redirect()`. `nf_conntrack_l4proto_icmpv6` provides tuple netlink and timeout policy callbacks.

## Control Flow
New tracked ICMPv6 flows require echo request or NI query. The error path validates header length and checksum, marks selected neighbor discovery/MLD/router discovery control messages as `IP_CT_UNTRACKED`, handles redirects with hop-limit/link-local/options validation, and correlates true errors to embedded tuples using `nf_conntrack_inet_error()`.

## State and Persistence
Persistent state is the per-net ICMPv6 timeout. Packets can be explicitly marked untracked for control message types that should not create conntrack entries. No extra per-connection ICMPv6 private state is kept.

## Dependencies and Integration Points
Depends on IPv6/ICMPv6 headers, IPv6 checksum, neighbor discovery redirect structures, conntrack zones/core, netlink attributes, and timeout extension. Initialized from `nf_conntrack_proto_pernet_init()` and exposed through standalone sysctls.

## Risks
Redirect validation is subtle because only redirects with a redirect-header option should be correlated to an inner connection. Type index arithmetic subtracts 128 or 130 and must guard bounds. The descriptor uses timeout max constants that must match ICMPv6 userspace ABI expectations.

## Test Signals
Test echo/NI request flows, invalid new reply-only types, MLD/ND messages becoming untracked, bad checksum logs, valid and invalid redirects, related destination-unreachable/time-exceeded errors, and ctnetlink ICMPv6 tuple filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_icmpv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_sctp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_sctp.c

## Purpose
Implements SCTP conntrack state tracking. It validates SCTP chunks and CRCs, tracks association state and verification tags, handles heartbeat/new-flow edge cases, refreshes per-state timeouts, exposes protocol info through netlink/proc, and supports ctnetlink timeout policies.

## Important APIs, Types, and Functions
The core is `nf_conntrack_sctp_packet()`, with helpers `do_basic_checks()`, `sctp_new_state()`, `sctp_new()`, `sctp_error()`, and `sctp_can_early_drop()`. It defines `sctp_conntracks` transition tables, `sctp_timeouts`, netlink functions `sctp_to_nlattr()` and `nlattr_to_sctp()`, timeout converters, and descriptor `nf_conntrack_l4proto_sctp`.

## Control Flow
The packet path validates basic header length and CRC on PREROUTING when checksum checking is enabled. It walks chunks, rejects invalid ordering/zero lengths, records chunk-type bitmap, initializes new entries only for allowed OOTB packets, enforces verification tag rules, then under `ct->lock` advances state per chunk. INIT/INIT_ACK copy peer verification tags; COOKIE_ACK clears init collision flags; heartbeat mismatches have special two-step recovery. Accepted packets refresh the timeout for the resulting state unless marked `ignore`.

## State and Persistence
Each SCTP conntrack stores state, per-direction verification tags, init flags, heartbeat mismatch flags, and last mismatch direction in `ct->proto.sctp`. Per-net timeouts persist in `nf_sctp_pernet(net)->timeouts`. Netlink may restore state and vtags.

## Dependencies and Integration Points
Depends on SCTP headers/checksum code, conntrack events, L4 protocol descriptor callbacks, procfs printing, ctnetlink protoinfo, timeout policies, and standalone sysctls for SCTP timeouts.

## Risks
SCTP multihoming and stale-cookie handling are acknowledged incomplete areas. Verification-tag exceptions for INIT, ABORT, SHUTDOWN_COMPLETE, COOKIE_ECHO, and heartbeat are easy to regress. Timeout refresh suppression for retransmitted INITs prevents NAT pinning and should be preserved. Chunk walk relies on `do_basic_checks()` guaranteeing nonzero lengths.

## Test Signals
Exercise INIT/INIT_ACK/COOKIE_ECHO/COOKIE_ACK establishment, shutdown transitions, ABORT, heartbeat vtag recovery, CRC failure, malformed chunk order, OOTB packet rejection, netlink dump/restore of state/vtags, early-drop eligibility, and custom timeout policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_sctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_tcp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_tcp.c

## Purpose
Implements the TCP conntrack state machine, sequence/window validation, retransmission and timeout selection, netlink protocol-state export/import, sysctl-backed defaults, and early-drop policy for closed/closing flows.

## Important APIs, Types, and Functions
Main entry points are `nf_conntrack_tcp_packet()` and exported `nf_conntrack_tcp_set_closing()`. Important helpers include `get_conntrack_index()`, `segment_seq_plus_len()`, `tcp_options()`, `tcp_sack()`, `tcp_init_sender()`, `tcp_in_window()`, `tcp_error()`, `tcp_new()`, `nf_tcp_handle_invalid()`, and `nf_ct_tcp_state_reset()`. Static tables `tcp_conntracks` and `tcp_timeouts` define state transitions and per-state expiration defaults.

## Control Flow
Packets are parsed with `skb_header_pointer()`, rejected for short headers, bad checksums, or invalid flag combinations, and initialized through `tcp_new()` for unconfirmed entries. Under `ct->lock`, the state table chooses a new state based on direction and flags. Special paths handle TIME_WAIT reopening, ignored SYN/SYNACK resync, SYNPROXY keepalives, RFC5961 challenge ACKs, simultaneous open, and careful RST validation. `tcp_in_window()` validates sequence, ACK, SACK, receive-window, NAT seqadj offsets, and retransmission state before the packet refreshes an appropriate timeout and maybe emits `IPCT_PROTOINFO` or `IPCT_ASSURED`.

## State and Persistence
Each TCP conntrack stores state, per-direction `ip_ct_tcp_state` windows/options/flags, last packet metadata, retransmission count, and flags such as close initiator, SACK permitted, window scale, liberal pickup, and simultaneous open. Per-net `nf_tcp_net` stores timeouts, `tcp_loose`, `tcp_be_liberal`, `tcp_ignore_invalid_rst`, `tcp_max_retrans`, and flow offload timeout.

## Dependencies and Integration Points
Depends on TCP/IP checksum helpers, conntrack seqadj, SYNPROXY extension, events, timeout policies, ctnetlink protoinfo, procfs state printing, standalone sysctls, and flow table timeout configuration. The descriptor `nf_conntrack_l4proto_tcp` is selected by `nf_ct_l4proto_find()`.

## Risks
The sequence/window checks are the highest-risk logic: NAT sequence offsets, SACK upper bounds, window scaling, zero-window probes, liberal mode, and midstream pickup all interact. Invalid FIN/RST timeout shortening prevents stale established entries. Changing ignored-packet handling can break resynchronization after firewall state loss or challenge ACKs. Timeout indexes must align with userspace CTA timeout constants.

## Test Signals
Cover normal three-way open/close, simultaneous open, SYN retransmits without timeout renewal, loose midstream pickup, strict `tcp_loose=0`, bad checksums/flags, out-of-window data, SACK handling with NAT seqadj, invalid RST handling, challenge ACKs, retransmission timeout shortening, ASSURED transitions, netlink state dump/restore, and all TCP sysctl timeout knobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c

## Purpose
Implements UDP conntrack validation, stream promotion, timeout refresh, ctnetlink timeout policy support, and UDP tuple netlink integration.

## Important APIs, Types, and Functions
Main function is `nf_conntrack_udp_packet()`, supported by `udp_error()`, `udp_error_log()`, `udp_get_timeouts()`, `nf_conntrack_udp_init_net()`, and descriptor `nf_conntrack_l4proto_udp`. Default timeouts are 30 seconds unreplied and 120 seconds replied.

## Control Flow
`udp_error()` validates the UDP header, length field, and optional checksum on PREROUTING when checksum checking is enabled. The packet path initializes `ct->proto.udp.stream_ts` for new entries, refreshes the short timeout until reply traffic is seen and at least two seconds pass, then refreshes the stream timeout and sets `IPS_ASSURED` unless `IPS_NAT_CLASH` is present.

## State and Persistence
Per-connection UDP state is `stream_ts`, used to avoid promoting immediate bidirectional probes to long-lived streams. Per-net state is timeout array plus optional flow offload timeout.

## Dependencies and Integration Points
Depends on UDP headers, checksum helpers, conntrack events, timeout extension, port tuple netlink helpers, flow-table configuration, and standalone UDP sysctls.

## Risks
UDP has no handshake, so the two-second promotion threshold is the main heuristic. Bad length or checksum handling must avoid dropping valid checksum-offloaded traffic. NAT clash flows intentionally never become ASSURED.

## Test Signals
Validate one-way UDP expiration, bidirectional promotion after two seconds, immediate reply before stream threshold, zero checksum IPv4 packets, malformed lengths, bad checksums, NAT clash behavior, ctnetlink timeout policies, and flow offload timeout sysctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c

## Purpose
Implements a TCP helper for the SANE network scanner protocol. It watches for `SANE_NET_START` requests and successful replies, then installs an expectation for the data connection advertised by the server.

## Important APIs, Types, and Functions
The helper entry point is `help()`. Module registration uses `nf_conntrack_sane_init()`, `nf_conntrack_sane_fini()`, `nf_ct_helper_init()`, and `nf_conntrack_helpers_register()`. Wire structs `sane_request` and `sane_reply_net_start` describe the fields inspected. Helper state is `struct nf_ct_sane_master` with `SANE_STATE_START_REQUESTED`/normal state.

## Control Flow
Only established TCP packets are inspected. Original-direction payloads must exactly match `struct sane_request`; if the RPC code is `SANE_NET_START`, the helper marks the next reply interesting. Reply-direction packets are ignored unless that state is set. A successful reply with zero reserved field yields an expectation from client to server on the returned TCP port; expectation failure drops the packet.

## State and Persistence
Per-connection helper state records whether a start reply is pending, using `READ_ONCE()`/`WRITE_ONCE()`. Expectations persist for up to five minutes with one expected data connection. Module parameters select up to eight server ports, defaulting to `SANE_PORT`.

## Dependencies and Integration Points
Depends on conntrack helper and expectation APIs plus SANE helper header definitions. Registers IPv4 and IPv6 TCP helpers for each configured port.

## Risks
The helper expects exact request length and minimal reply fields, so protocol extensions or segmentation can be missed. It does not perform NAT mangling locally. Dropping on expectation failure can affect scanner setup when expectation limits are exhausted.

## Test Signals
Test default and custom ports, IPv4/IPv6, valid `SANE_NET_START` request/reply, refused status, nonzero reserved field, split TCP payloads, expectation exhaustion, and successful data connection classification as RELATED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c

## Purpose
Maintains and applies TCP sequence-number adjustments for conntrack helpers/NAT modules that change payload length. It rewrites sequence numbers, ACK numbers, and SACK blocks while updating TCP checksums.

## Important APIs, Types, and Functions
Exports `nf_ct_seqadj_init()`, `nf_ct_seqadj_set()`, `nf_ct_tcp_seqadj_set()`, `nf_ct_seq_adjust()`, and `nf_ct_seq_offset()`. Internal helpers are `nf_ct_sack_adjust()` and `nf_ct_sack_block_adjust()`. State lives in `struct nf_conn_seqadj` with per-direction `struct nf_ct_seqadj`.

## Control Flow
NAT/helper code calls init or set when payload length changes. `nf_ct_seqadj_set()` records a correction position and before/after offsets under `ct->lock`. `nf_ct_seq_adjust()` makes the TCP header writable, adjusts sequence by this direction's offset, adjusts ACK by the opposite direction's offset, and rewrites any SACK block sequence ranges. `nf_ct_seq_offset()` returns the offset relevant to a given sequence.

## State and Persistence
Per-direction offsets and correction positions persist in the conntrack extension for the connection lifetime. `IPS_SEQ_ADJUST_BIT` signals confirmation/helper paths to invoke adjustment. No global state is kept.

## Dependencies and Integration Points
Depends on conntrack extension storage, TCP header layout, checksum replacement helpers, TCP option parsing, and callers in helpers/NAT code plus `nf_confirm()` and `nf_ct_helper()`.

## Risks
Missing `nfct_seqadj_ext_add()` setup triggers a warning and skips updating, which can corrupt application data flows after NAT mangling. SACK parsing must reject partial options and keep checksum updates consistent. Locking spans packet mutation, so all callers must use writable skbs.

## Test Signals
Test FTP/SIP NAT payload expansion/shrink, sequence and ACK rewrite in both directions, SACK block rewrite, malformed TCP options, zero offset no-op, missing extension warning, and checksum validation after mangling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_seqadj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c

## Purpose
Implements the SIP conntrack helper for UDP and TCP. It parses SIP headers and SDP bodies, maintains SIP master state, creates expectations for signalling and RTP/RTCP media flows, refreshes registration expectations, and delegates SIP/SDP mangling to optional NAT hooks.

## Important APIs, Types, and Functions
Exports SIP parser helpers used by NAT: `ct_sip_parse_request()`, `ct_sip_get_header()`, `ct_sip_parse_header_uri()`, `ct_sip_parse_address_param()`, `ct_sip_parse_numerical_param()`, and `ct_sip_get_sdp_header()`. Main runtime functions are `sip_help_udp()`, `sip_help_tcp()`, `process_sip_msg()`, `process_sip_request()`, `process_sip_response()`, `process_sdp()`, `set_expected_rtp_rtcp()`, `process_register_request()`, and `process_register_response()`. `nf_nat_sip_hooks` is the exported RCU NAT hook table.

## Control Flow
UDP helper linearizes one datagram and processes one SIP message. TCP helper linearizes the skb and walks one or more SIP messages using `Content-Length`, tracking total payload-size changes for NAT seqadj. Request/response dispatch uses method handlers for INVITE, UPDATE, ACK, PRACK, BYE, and REGISTER. SDP processing locates session/media connection addresses and media ports, creates RTP/RTCP expectations, and asks NAT hooks to rewrite media/session addresses when required.

## State and Persistence
Per-flow `struct nf_ct_sip_master` stores invite/register CSeq and forced destination port learned from Via headers. Expectations persist for signalling, audio, video, and image classes with separate policies. Permanent inactive REGISTER expectations are activated/refreshed by successful registrar responses. Module parameters control helper ports, SIP master timeout, direct signalling/media restrictions, and external media behavior.

## Dependencies and Integration Points
Depends on conntrack helper/expectation APIs, routing lookups for external media decisions, SIP header definitions, IPv4/IPv6 address parsers, zones, and optional NAT SIP hooks for message, SDP, expectation, and sequence adjustment rewrites. Registers IPv4/IPv6 UDP/TCP helpers per configured port.

## Risks
Text parsing is complex: folded headers, comma-separated contacts, URI userinfo, IPv6 delimiters, malformed ports, and TCP message framing all affect correctness. Expectation conflicts across calls are handled with `-EALREADY`, but media reuse can still be surprising. NAT hooks mutate buffers and lengths, making TCP seqadj essential. Third-party registrations and external media are intentionally constrained by module parameters.

## Test Signals
Test UDP/TCP SIP, multiple TCP messages per skb, INVITE/UPDATE/PRACK/ACK SDP media expectations, failed responses flushing media expectations, BYE cleanup, REGISTER success/expiry/flush, IPv4/IPv6 Contact/Via/SDP parsing, direct/external media modes, NAT SIP rewrites, malformed headers, invalid ports, and RELATED RTP/RTCP flow creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c

## Purpose
Implements a small IPv4 SNMP broadcast helper. It uses the generic broadcast helper to expect replies to SNMP requests and optionally delegates SNMP NAT handling.

## Important APIs, Types, and Functions
The helper entry point is `snmp_conntrack_help()`. Module lifecycle is `nf_conntrack_snmp_init()` and `nf_conntrack_snmp_fini()`. The exported RCU hook pointer is `nf_nat_snmp_hook`. The helper registers for IPv4 UDP source port 161 with one expected reply.

## Control Flow
Every helper invocation calls `nf_conntrack_broadcast_help()` with the configured timeout. If NAT is active and a NAT SNMP hook is installed, the hook processes the skb; otherwise the packet is accepted.

## State and Persistence
No per-connection private state is defined here. The expectation policy timeout is initialized from the module parameter `timeout`, defaulting to 30 seconds. NAT hook state is external and RCU-protected.

## Dependencies and Integration Points
Depends on conntrack helper/expectation APIs, broadcast helper support, and optional NAT SNMP code. It is IPv4-only by tuple registration.

## Risks
The helper is intentionally broad for broadcast semantics and does not parse SNMP payloads itself. NAT hook dereference must remain under RCU protection supplied by netfilter hook context.

## Test Signals
Test broadcast SNMP requests, expected replies from agents, timeout parameter behavior, NAT enabled/disabled, missing NAT hook, and helper registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_snmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c

## Purpose
Provides the standalone conntrack module lifecycle and user-facing observability/configuration. It registers per-net conntrack state, `/proc` sequence files, per-CPU stats, sysctl tables, optional eager hook enablement, and global module initialization/cleanup.

## Important APIs, Types, and Functions
Exports `nf_conntrack_net_id`, `print_tuple()`, and `nf_conntrack_count()`. Procfs logic centers on `ct_seq_start()`, `ct_get_next()`, `ct_seq_show()`, and CPU stat seq ops. Sysctl setup uses `nf_conntrack_standalone_init_sysctl()` plus protocol-specific assignment helpers for TCP/SCTP/GRE. Per-net lifecycle is `nf_conntrack_pernet_init()`, `nf_conntrack_pernet_exit()`, and module lifecycle is `nf_conntrack_standalone_init()`/`fini()`.

## Control Flow
Module init starts core conntrack initialization, registers global sysctl `net/nf_conntrack_max`, finalizes core init, and registers a per-net subsystem. Per-net init sets checksum validation on, installs per-net sysctls and proc entries, initializes core conntrack net state, and optionally enables IPv4/IPv6 hooks when `enable_hooks=1`. Proc iteration walks the conntrack hash under RCU, handles nulls-list restarts, skips reply tuples, kills GC-eligible entries, and prints tuple/state/accounting/status metadata.

## State and Persistence
Persistent state includes module parameter `enable_hooks`, `nf_conntrack_net_id`, global sysctl header, per-net `nf_conntrack_net`, proc entries, sysctl table copies, conntrack hash/count/stat state owned by core, and per-net protocol timeout pointers. Non-init namespaces get read-only global sizing sysctls.

## Dependencies and Integration Points
Depends on conntrack core, L4 descriptors, helper/expect/acct/timestamp/zone APIs, procfs, seq_file, sysctl, LSM secctx, pernet subsystem, and net namespace userns ownership. It wires sysctl data pointers into the per-net protocol structs initialized elsewhere.

## Risks
Proc iteration over RCU nulls hash must preserve bucket/skip state during concurrent mutation. Sysctl table copies must be freed after unregister. Per-net failure paths must unwind proc/sysctl/core/hook setup in the right order. User-facing proc output is ABI-like and sensitive to field order.

## Test Signals
Load/unload conntrack, create/delete net namespaces, read `/proc/net/nf_conntrack` and `/proc/net/stat/nf_conntrack`, tune global and per-net sysctls, verify non-init namespace read-only sizing knobs, enable eager hooks, exercise acct/timestamp/zone/secmark output, and resize hash buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c

## Purpose
Implements a UDP helper for TFTP. It watches read/write requests on configured server ports and creates an expectation for the server's subsequent data connection from its chosen transfer ID port.

## Important APIs, Types, and Functions
The helper entry point is `tftp_help()`. Module lifecycle is `nf_conntrack_tftp_init()`/`fini()`. `nf_nat_tftp_hook` is an exported RCU hook pointer for NAT-specific expectation setup. Helpers are registered for IPv4 and IPv6 UDP per configured port.

## Control Flow
The helper reads a TFTP header after the UDP header. RRQ and WRQ allocate an expectation using the reply tuple source/destination addresses and original destination UDP port, then call NAT hook if needed or `nf_ct_expect_related()`. DATA, ACK, ERROR, and unknown opcodes only log debug messages and are accepted.

## State and Persistence
The file has no per-connection private state. Each request can create one expectation with a five-minute timeout. Module parameter `ports` allows up to eight server ports, defaulting to `TFTP_PORT`.

## Dependencies and Integration Points
Depends on UDP/TFTP headers, conntrack helper/expectation/event APIs, and optional NAT TFTP module. It integrates with helper assignment from rulesets or automatic helper configuration.

## Risks
Only the initial RRQ/WRQ packet is meaningful; fragmented or malformed requests are skipped. Expectation failure drops the request to avoid creating an untracked transfer. NAT hook behavior must match expectation tuple rewrite.

## Test Signals
Test RRQ and WRQ over IPv4/IPv6, custom ports, NAT and non-NAT transfers, expectation exhaustion, malformed/short TFTP headers, DATA/ACK/ERROR no-op paths, and RELATED classification of the server transfer flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_tftp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c

## Purpose
Provides the runtime glue for named conntrack timeout policies. It attaches timeout policy objects to conntracks, removes references when policies are deleted or connections die, and exposes an RCU hook table implemented by the timeout subsystem.

## Important APIs, Types, and Functions
Exports `nf_ct_timeout_hook`, `nf_ct_untimeout()`, `nf_ct_set_timeout()`, and `nf_ct_destroy_timeout()`. Internal helpers are `untimeout()` and `__nf_ct_timeout_put()`. State is stored in the `struct nf_conn_timeout` extension with an RCU pointer to `struct nf_ct_timeout`.

## Control Flow
`nf_ct_set_timeout()` enters RCU, finds the hook table, looks up a named policy, validates L3 and L4 protocol match, attaches a timeout extension with `nf_ct_timeout_ext_add()`, and returns errors for missing hooks/policies, protocol mismatch, or allocation failure. `nf_ct_untimeout()` iterates conntracks in a net namespace and clears matching timeout pointers. Destroy releases the referenced policy through `timeout_put()`.

## State and Persistence
The global hook pointer is RCU-published by another module. Per-connection timeout policy references persist until cleared by policy deletion, connection destruction, or explicit replacement. Reference counts are owned by hook callbacks.

## Dependencies and Integration Points
Depends on conntrack core iteration, extension storage, L4 protocol descriptors, timeout policy hooks, and callers such as `xt_CT`, conntrack netlink, OVS conntrack, and BPF conntrack helpers.

## Risks
RCU and policy reference lifetimes must stay balanced, especially on validation failure after `timeout_find_get()`. Protocol mismatch checks prevent attaching an incompatible timeout array. Iterating all conntracks for policy deletion can be expensive but avoids stale pointers.

## Test Signals
Configure named timeout policies, attach through CT target/OVS/netlink, verify L3/L4 mismatch errors, delete a policy and confirm existing conntracks clear references, destroy conntracks with policies, and test no-hook/no-policy error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c

## Purpose
Initializes the per-network-namespace default for conntrack flow timestamping from a module parameter.

## Important APIs, Types, and Functions
Defines module parameter `tstamp` backed by `nf_ct_tstamp` and function `nf_conntrack_tstamp_pernet_init(struct net *net)`, which copies that default into `net->ct.sysctl_tstamp`.

## Control Flow
During conntrack per-net initialization, core code calls `nf_conntrack_tstamp_pernet_init()`. The function performs a direct assignment; runtime changes are then controlled by the per-net sysctl when timestamp support is enabled.

## State and Persistence
Global `nf_ct_tstamp` stores the module default. Each namespace stores its mutable runtime setting in `net->ct.sysctl_tstamp`. Actual per-connection timestamp extensions are managed elsewhere.

## Dependencies and Integration Points
Depends on conntrack timestamp extension headers and module parameter infrastructure. Integrates with `nf_conntrack_core.c` per-net initialization and `nf_conntrack_standalone.c` sysctl/proc delta-time output.

## Risks
The file is intentionally small; the main risk is assuming module parameter changes automatically rewrite existing net namespaces. They do not: this function only seeds per-net defaults at init.

## Test Signals
Load conntrack with `tstamp=0` and `tstamp=1`, create new namespaces, check `nf_conntrack_timestamp` sysctl defaults, and verify `/proc/net/nf_conntrack` shows `delta-time` only when timestamping is enabled and timestamp extensions exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c

## Purpose
Implements netdev-family packet forwarding and duplication helpers for nftables, plus flow-offload action construction for fwd/dup netdev expressions.

## Important APIs, Types, and Functions
Exports `nf_fwd_netdev_egress()`, `nf_dup_netdev_egress()`, and `nft_fwd_dup_netdev_offload()`. Internal `nf_do_netdev_egress()` handles recursion limiting, optional MAC header push for ingress-origin packets, device assignment, timestamp clearing, and `dev_queue_xmit()`.

## Control Flow
Forwarding looks up the output interface by index under RCU; missing devices consume/free the original skb. Duplication looks up the device, clones the skb with `GFP_ATOMIC`, and transmits only the clone. Egress preparation pushes the MAC header back when duplicating/forwarding from netdev ingress and a MAC header is available. Offload obtains a device reference and appends a flow action entry with the requested action ID.

## State and Persistence
No persistent module state is stored. It mutates skb device/header/timestamp state and uses per-CPU netfilter duplicate recursion state. Offload entries hold device references later released by flow-rule destruction.

## Dependencies and Integration Points
Depends on nftables netdev packet info, nf_tables offload, flow action entries, netdevice lookup/transmit, and `nf_get_nf_dup_skb_recursion()`. Called by `nft_dup_netdev.c` and `nft_fwd_netdev.c`.

## Risks
Recursion limit enforcement prevents loops but drops skbs when exceeded. Forward consumes the original skb, while dup must not. MAC header push requires headroom and may fail. Offload must not leak device references on later failure paths.

## Test Signals
Test nft netdev dup and fwd rules on ingress and egress hooks, missing output interface behavior, recursive dup/fwd loops, insufficient headroom, cloned skb delivery, hardware/software offload setup, and device ref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c

## Purpose
Exposes an unstable BPF kfunc for XDP programs to look up netfilter flow table entries by a `bpf_fib_lookup` tuple and refresh matching flow offloads.

## Important APIs, Types, and Functions
The BPF-visible kfunc is `bpf_xdp_flow_lookup()`. Internal helper `bpf_xdp_flow_tuple_lookup()` finds a flow table for a device, does `flow_offload_lookup()`, derives the owning `struct flow_offload`, and refreshes it. `nf_flow_register_bpf()` registers the BTF kfunc set for `BPF_PROG_TYPE_XDP`. `struct bpf_flowtable_opts` currently contains only `error`.

## Control Flow
The kfunc validates `opts_len`, builds a `struct flow_offload_tuple` from `bpf_fib_lookup`, copies IPv4 or IPv6 addresses depending on family, and rejects unsupported families. Lookup uses the XDP RX device to find an attached nf flowtable. Errors are returned as NULL with `opts->error`; successful lookups return a `flow_offload_tuple_rhash *` and refresh the flow.

## State and Persistence
This file owns no flow state. It reads flow tables attached to devices and refreshes existing `struct flow_offload` timeout/accounting state through flow table core. The BTF kfunc registration persists after `nf_flow_register_bpf()` succeeds.

## Dependencies and Integration Points
Depends on BPF kfunc/BTF registration, XDP context casting, `bpf_fib_lookup` layout, netfilter flow table core, and `nf_flow_table_core.c`, which calls `nf_flow_register_bpf()`.

## Risks
The interface is explicitly unstable, but verifier-visible struct sizes and return annotations still must match the kernel BTF contract. `opts` is assumed valid when `opts_len` is checked. Flow tuple construction must match flowtable lookup keys exactly, including interface index, family, L4 protocol, ports, and addresses.

## Test Signals
Load XDP programs using the kfunc, test IPv4 and IPv6 flowtable hits/misses, unsupported family, wrong options length, no flowtable on device, timeout refresh on hit, BTF registration failure handling, and verifier behavior around nullable return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_flow_table_bpf.c -->
