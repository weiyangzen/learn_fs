# sources/distributed-fs/ceph-client/drivers/net/ovpn/stats.h

Purpose: Defines per-peer ovpn statistics structures and inline counter update helpers.

Important APIs, types, and functions: `struct ovpn_peer_stat` stores atomic64 `bytes` and `packets`. `struct ovpn_peer_stats` groups RX and TX stats. `ovpn_peer_stats_increment()`, `ovpn_peer_stats_increment_rx()`, and `ovpn_peer_stats_increment_tx()` update byte and packet counters.

Control flow: Data paths call the inline helpers after successful VPN or link RX/TX operations. Netlink reads counters for peer reports.

State and persistence behavior: Stats are in-memory per-peer counters. They are monotonic for the peer lifetime and reset on peer recreation.

Dependencies and integration points: It relies on atomic64 operations and is embedded in `struct ovpn_peer` for both inner VPN accounting and outer transport accounting.

Risks and edge cases: Packet and byte increments are not a single atomic transaction. Callers must pass the correct length category to avoid mixing encrypted transport bytes with decrypted VPN bytes. Drops are accounted through netdev dstats elsewhere, not here.

Test signals: Validate RX/TX counters under UDP/TCP traffic, confirm no increment on failed decrypt or failed transmit, and compare netlink stats with expected packet sizes in both VPN and link layers.
