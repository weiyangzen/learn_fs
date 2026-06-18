# sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.c

Purpose: Provides initialization for per-peer ovpn packet/byte counters.

Important APIs, types, and functions: `ovpn_peer_stats_init()` sets RX/TX byte and packet atomic64 counters to zero for a `struct ovpn_peer_stats`.

Control flow: Peer allocation calls this initializer for VPN and link stats before the peer becomes visible. Data paths later increment counters through inline helpers in `stats.h`; netlink serializes their current values in peer get/dump responses.

State and persistence behavior: The counters are per-peer runtime state and reset with peer recreation or key/session reconfiguration that allocates a new peer.

Dependencies and integration points: It depends on Linux atomic64 and the declarations in `stats.h`. It integrates with netlink telemetry and data-path accounting.

Risks and edge cases: Counters are atomic but not snapshot-consistent across multiple fields, so netlink can report bytes/packets from slightly different moments. Initialization must run before any packet path can increment.

Test signals: Create peers and verify zeroed stats; send/receive data and validate increments; dump stats during concurrent traffic; and run on 32-bit builds where atomic64 support is more sensitive.
