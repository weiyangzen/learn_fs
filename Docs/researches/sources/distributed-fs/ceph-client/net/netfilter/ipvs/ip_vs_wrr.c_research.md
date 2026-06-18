# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wrr.c

## Purpose
Implements the IPVS weighted round-robin scheduler `wrr`. It cycles through destinations in list order while using maximum weight and GCD-derived weight steps to approximate weighted distribution.

## Important APIs, Types, and Functions
`struct ip_vs_wrr_mark` stores current list position `cl`, current required weight `cw`, maximum effective weight `mw`, and decrement interval `di`. `ip_vs_wrr_gcd_weight()` and `ip_vs_wrr_max_weight()` compute weight parameters. `ip_vs_wrr_init_svc()`, `ip_vs_wrr_dest_changed()`, and `ip_vs_wrr_done_svc()` manage per-service state. `ip_vs_wrr_schedule()` performs selection. `ip_vs_wrr_scheduler` registers init, done, add, delete, update, and schedule callbacks.

## Control Flow
Service initialization sets the current pointer to the list head and computes GCD, max effective weight, and current weight. Destination changes reset the pointer and recompute parameters under `svc->sched_lock`, adjusting `cw` to remain valid. Scheduling locks the service, scans forward from the current pointer for a destination with weight at least `cw` and not overloaded, then decrements `cw` by `di` and wraps as needed. It performs a final pass at weight threshold one to catch destinations whose weights changed below the old GCD.

## State and Persistence
Per-service state is the WRR mark stored in `svc->sched_data` and freed with RCU on unbind. It persists across scheduling calls to maintain position and current weight phase. Destination weights remain externally configured state.

## Dependencies and Integration Points
Depends on IPVS service locks, destination list traversal, GCD helper, RCU cleanup, scheduler registry, and atomic weights. Destination add/delete/update callbacks keep scheduler state aligned with the service pool.

## Risks
The algorithm is sensitive to concurrent weight changes, which the code partly mitigates with an effective max weight and final threshold-one pass. Pointer state can reference list head or destinations, so deletion and reassignment paths must reset it correctly. Overloaded destinations can cause the scan to wrap and eventually fail even if weights are positive.

## Test Signals
Validate weighted distribution ratios, GCD and max-weight recalculation after destination updates, zero and all-zero weights, overloaded destinations, deletion of current destination, dynamic weight reduction below GCD, and no-destination error messages.
