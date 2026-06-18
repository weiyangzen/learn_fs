<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c

## Purpose
`xt_rateest.c` implements matching based on named netfilter rate estimators. It compares one estimator against constants or another estimator using bytes-per-second and packets-per-second rates.

## Important APIs, Types, and Functions
`xt_rateest_mt()` reads `struct xt_rateest_match_info`, fetches estimator rates, applies absolute or relative comparison modes, and supports delta calculations. `xt_rateest_mt_checkentry()` resolves and pins estimator objects; `xt_rateest_mt_destroy()` releases them.

## Control Flow, State, and Persistence
At rule insertion, named estimators are looked up and stored in match info. Packet evaluation snapshots current estimator values, optionally subtracts configured baselines, compares BPS/PPS fields according to mode, and returns the result with inversion as configured. Rate state is owned by the estimator subsystem.

## Dependencies and Integration Points
The module depends on x_tables and `xt_rateest` estimator objects created elsewhere. It is commonly used with the RATEEST target or traffic measurement rules.

## Risks and Test Signals
Risks include missing named estimators, refcount leaks, stale rate windows, signed/unsigned delta comparisons, and ambiguous combined BPS/PPS modes. Tests should cover constant threshold, estimator-vs-estimator, delta mode, less/greater/equal operators, BPS and PPS combinations, inversion, missing estimator rejection, and destroy release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_rateest.c -->
