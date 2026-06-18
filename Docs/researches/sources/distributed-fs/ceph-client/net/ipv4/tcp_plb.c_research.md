# sources/distributed-fs/ceph-client/net/ipv4/tcp_plb.c

## Purpose

`tcp_plb.c` implements TCP Protective Load Balancing state updates. PLB is a host-side datacenter load-balancing optimization that uses persistent transport congestion signals to trigger a transmit hash change, allowing ECMP/WCMP fabrics to place later packets on a different path. The implementation deliberately favors rehashing after idle periods or sustained congestion, and suppresses rehashing for a randomized interval after RTO to avoid returning traffic to a suspected black-holed path.

## Important APIs, Types, and Functions

The exported API is `tcp_plb_update_state()`, `tcp_plb_check_rehash()`, and `tcp_plb_update_state_upon_rto()`. All operate on `struct tcp_plb_state`, whose important fields here are `consec_cong_rounds` and `pause_until`. The functions use per-network-namespace sysctls: `sysctl_tcp_plb_enabled`, `sysctl_tcp_plb_cong_thresh`, `sysctl_tcp_plb_rehash_rounds`, `sysctl_tcp_plb_idle_rehash_rounds`, and `sysctl_tcp_plb_suspend_rto_sec`.

## Control Flow

`tcp_plb_update_state()` is called once per RTT with a congestion ratio. If PLB is disabled it returns. Nonnegative ratios below the threshold clear `consec_cong_rounds`; ratios at or above the threshold increment the counter up to the configured forced-rehash threshold.

`tcp_plb_check_rehash()` evaluates whether the counter reached the forced threshold or the lower idle threshold while `packets_out` is zero. It then validates `pause_until`, clearing stale or wrapped pause windows. If not paused, it calls `sk_rethink_txhash()`, clears the congestion-round counter, increments `tcp_sk(sk)->plb_rehash`, and updates `LINUX_MIB_TCPPLBREHASH`.

`tcp_plb_update_state_upon_rto()` is called on RTO. It chooses a randomized pause between one and two configured suspension intervals, stores `pause_until`, and resets congestion rounds because RTO itself may already have caused a path/hash rethink.

## State and Persistence Behavior

State is per connection in `struct tcp_plb_state` and `tcp_sock::plb_rehash`. It persists for the socket lifetime and is driven by RTT rounds and RTO events. No durable state exists. The jiffies-based `pause_until` explicitly handles wraparound and stale long pauses.

## Dependencies and Integration Points

The module depends on TCP congestion accounting elsewhere to supply `cong_ratio`, on `tcp_jiffies32`, `tcp_sk(sk)->packets_out`, `sk_rethink_txhash()`, per-net IPv4 sysctls, random number generation, and Linux TCP MIB counters. It is intended for TCP flows whose transmit hash affects underlay path choice.

## Risks and Edge Cases

Too aggressive thresholds can cause reordering from path changes, while too conservative thresholds hide persistent imbalance. RTO suspension must be long enough to avoid oscillating back to bad paths. Because this code uses jiffies arithmetic, wrap handling in `tcp_plb_check_rehash()` is important. Rehashing while packets are in flight is allowed for forced rehash but may increase reordering risk.

## Test Signals

Tests should exercise disabled PLB, below-threshold reset, threshold accumulation, forced rehash, idle rehash with no packets out, RTO suspension suppression, pause expiry, and jiffies wrap simulations. Runtime signals include `tcp_sk(sk)->plb_rehash`, `LINUX_MIB_TCPPLBREHASH`, txhash changes, and packet reordering/loss metrics after rehash.
