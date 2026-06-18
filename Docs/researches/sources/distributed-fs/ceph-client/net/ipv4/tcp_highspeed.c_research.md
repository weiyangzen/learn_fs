# sources/distributed-fs/ceph-client/net/ipv4/tcp_highspeed.c

## Purpose
`tcp_highspeed.c` implements Sally Floyd's HighSpeed TCP congestion-control module named `highspeed`, based on RFC 3649. It uses a cwnd-indexed AIMD table to increase more aggressively and decrease less sharply at large windows.

## Important APIs, Types, And Functions
The fixed table `hstcp_aimd_vals[]` maps cwnd thresholds to multiplicative-decrease factors scaled by 256; the index is stored per socket in `struct hstcp { u32 ai; }`. The registered callbacks are `hstcp_init()`, `hstcp_cong_avoid()`, `hstcp_ssthresh()`, Reno undo, and the module register/unregister functions.

## Control Flow
`hstcp_init()` resets the table index and clamps `snd_cwnd_clamp` so multiplicative-decrease arithmetic cannot overflow. `hstcp_cong_avoid()` exits unless cwnd-limited. Slow start delegates to `tcp_slow_start()`. In congestion avoidance it adjusts `ca->ai` until the current cwnd lies within the table interval, then accumulates `ca->ai + 1` credits into `snd_cwnd_cnt`; when credits reach cwnd, it increases cwnd by one. On congestion, `hstcp_ssthresh()` subtracts `(cwnd * md) >> 8` using the table value for the current index and floors the threshold at two packets.

## State, Persistence, Dependencies, And Integration
State is per-socket and minimal: only the table index. The AIMD table is static read-only module data. The module depends on core TCP congestion helpers and registers with the common congestion-control list.

## Risks And Test Signals
Risks include off-by-one table index movement at thresholds, overflow despite clamp changes, incorrect slow-start leftover ACK handling, and poor behavior if `ai` is stale after cwnd drops. Tests should select `highspeed`, sweep cwnd across table thresholds in both directions, confirm additive increase scales with `ai`, validate ssthresh values for representative table rows, and exercise module registration and fallback to Reno undo.
