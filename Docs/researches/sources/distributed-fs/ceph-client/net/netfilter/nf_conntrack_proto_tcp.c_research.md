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
