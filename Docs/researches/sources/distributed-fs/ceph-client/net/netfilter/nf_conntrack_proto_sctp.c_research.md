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
