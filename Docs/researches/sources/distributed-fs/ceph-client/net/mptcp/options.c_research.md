<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/options.c -->
# sources/distributed-fs/ceph-client/net/mptcp/options.c

## Purpose
Implements MPTCP TCP-option parsing, outgoing option selection/writing, DSS mapping and ACK handling, ADD_ADDR/RM_ADDR/MP_PRIO/MP_FAIL/MP_FASTCLOSE/MP_RST processing, receive-window sharing, checksum generation, and subflow establishment transitions.

## Important APIs, Types, and Functions
`mptcp_get_options()` parses TCP options into `struct mptcp_options_received` through `mptcp_parse_option()`. Outgoing selection is handled by `mptcp_syn_options()`, `mptcp_synack_options()`, and `mptcp_established_options()`, with specialized helpers for MPC/MPJ, DSS, ADD_ADDR, RM_ADDR, PRIO, FASTCLOSE, FAIL, and RST. `mptcp_write_options()` serializes `struct mptcp_out_options` to the TCP header. Receive-side state updates use `check_fully_established()`, `ack_update_msk()`, `rwin_update()`, `mptcp_update_rcv_data_fin()`, and `mptcp_incoming_options()`. Exported `mptcp_get_reset_option()` returns an MP_RST option word for reset skb extensions.

## Control Flow
Parsing walks TCP options, dispatches on MPTCP subtype, validates strict lengths, version, flags, BOS-like option semantics, and stores decoded keys, HMACs, sequence numbers, address IDs, ports, checksums, and reset/fail fields. Outgoing SYN/SYNACK paths advertise MP_CAPABLE or MP_JOIN. Established-option selection prioritizes fallback, reset-bearing packets, third-ACK MPC/MPJ, DSS/data-fin, MP_FAIL, ADD_ADDR/RM_ADDR, and MP_PRIO while respecting option-space limits and documented mutual exclusions. Incoming options first handle fallback, then establish subflows or reset protocol violations, process control options, update MPTCP-level ACK/window state, attach `SKB_EXT_MPTCP` mapping data for payload skbs, and schedule PM/work items as needed.

## State and Persistence
The file mutates MPTCP socket state such as `snd_una`, `bytes_acked`, `wnd_end`, `last_ack_recv`, `rcv_data_fin`, receive-window sent state, subflow establishment flags, MP_FAIL/FASTCLOSE/RST flags, ADD_ADDR timers through PM callbacks, and skb MPTCP extensions. It stores no global state.

## Dependencies and Integration Points
Depends on TCP option layout, skb extensions, MPTCP protocol structs, crypto helpers, path manager APIs, MIB counters, TCP checksum/window helpers, and MPTCP tracepoints. It is central to subflow connect/listen code, data receive/transmit, PM signaling, fallback, and diagnostics.

## Risks
Option-space composition is dense and mutually exclusive; adding options can silently overrun or suppress critical DSS/handshake data. Length parsing intentionally accepts checksum-presence mismatches for later reset enforcement, so downstream checks must remain intact. Sequence expansion from 32-bit to 64-bit ACK/DSN values can acknowledge future data if conflict guards regress. ADD_ADDR HMAC depends on key direction and address/port bytes. Receive-window sharing uses atomics across subflows and is race-prone. MP_JOIN fully-established handling must reject early data and retransmit third-ACK acks correctly.

## Test Signals
MPTCP selftests should cover MP_CAPABLE handshake with/without data/checksum, MP_JOIN success and early-data reset, DSS ACK/map/data-fin variants, 32-bit wrap expansion, ADD_ADDR IPv4/IPv6/port echo/HMAC failure, RM_ADDR, MP_PRIO, MP_FAIL infinite-map fallback, MP_FASTCLOSE and MP_RST on reset packets, receive-window conflict counters, fallback paths, and packet captures verifying serialized option bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/options.c -->
