# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/counter.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard data packet anti-replay counter window implemented in `receive.c`.

Important APIs and functions: `wg_packet_counter_selftest()` allocates a `noise_replay_counter`, repeatedly initializes it, and uses macro `T(n, expected)` to assert `counter_validate()` behavior over duplicates, out-of-order counters, window boundaries, and reject-after limits.

Control flow: Test sequences first check simple increasing, duplicate, and near-window values, then fill entire windows in ascending and descending patterns, then checks boundary behavior near `REJECT_AFTER_MESSAGES`. It prints pass/fail and frees the counter.

State and persistence: Allocates one temporary replay counter and mutates its bitmap/counter state. No persistent state remains.

Dependencies and integration points: Included inside `receive.c` after `counter_validate()` so it can call the static function. Invoked from `main.c` in DEBUG builds.

Risks: Because it includes the static implementation, compile placement matters. It verifies algorithmic cases but not concurrent locking behavior under real RX load.

Test signals: DEBUG module load should print nonce counter self-tests pass; failure pinpoints anti-replay window or reject-limit regressions.
