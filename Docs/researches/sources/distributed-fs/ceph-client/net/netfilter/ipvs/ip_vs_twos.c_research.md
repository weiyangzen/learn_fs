# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_twos.c

## Purpose
Implements the IPVS power-of-two-random-choices scheduler `twos`. It randomly samples two weighted destinations and returns the one with lower connection overhead normalized by weight.

## Important APIs, Types, and Functions
`ip_vs_twos_schedule()` performs all scheduling. It uses `get_random_u32_below()` for random weighted picks, `ip_vs_dest_conn_overhead()` for load, and `ip_vs_twos_scheduler` for module registration.

## Control Flow
The scheduler first sums positive weights for non-overloaded destinations and records whether any eligible destination exists. It draws two random numbers in the inclusive weight range, walks the destinations again subtracting weights until each draw selects a destination, then compares `overhead / weight` via cross multiplication. If the second choice is better, it returns it; otherwise it returns the first choice.

## State and Persistence
No private state exists. Randomness and current destination counters drive each decision.

## Dependencies and Integration Points
Depends on IPVS destination counters and weights, RCU destination traversal, Linux random APIs, and scheduler registration. It is useful for large pools where full least-connection scans are more expensive than randomized sampling.

## Risks
The code adds one to `total_weight` before drawing, making boundary behavior important; if a draw remains beyond all cumulative weights, the initialized fallback choice can survive. Randomness makes exact distribution tests probabilistic. The comparison uses integer multiplication and assumes selected weights are positive.

## Test Signals
Use deterministic random stubbing or statistical tests to confirm weighted sampling and lower normalized overhead selection. Cover single-destination pools, all zero/overloaded destinations, large weights, and repeated scheduling distribution compared with WLC.
