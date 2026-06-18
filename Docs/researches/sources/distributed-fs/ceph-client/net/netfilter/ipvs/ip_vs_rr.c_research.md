# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_rr.c

## Purpose
Implements the basic IPVS round-robin scheduler `rr`, selecting the next eligible destination in service list order.

## Important APIs, Types, and Functions
`ip_vs_rr_init_svc()` stores the current list position in `svc->sched_data`. `ip_vs_rr_del_dest()` repairs that pointer when the current destination is deleted. `ip_vs_rr_schedule()` advances through destinations and picks the next non-overloaded positive-weight server. `ip_vs_rr_scheduler` registers callbacks for service init, destination deletion, and scheduling.

## Control Flow
Scheduling takes `svc->sched_lock`, starts from the saved position, scans forward with RCU list continuation, and wraps at most once to avoid looping forever if the previous destination was unlinked. On success it updates `svc->sched_data` to the selected destination's list node. If no eligible server is found, it releases the lock and logs a scheduler error.

## State and Persistence
The only private state is the current list pointer stored in `svc->sched_data`; it persists for the service scheduler binding and is adjusted on destination deletion. It does not store weights or counters.

## Dependencies and Integration Points
Uses IPVS service destination lists, service scheduler lock, destination flags and weights, scheduler registry, and RCU. It is used by services configured with scheduler `rr`.

## Risks
Correct pointer repair on deletion is critical because `sched_data` can point at a destination already unlinked from the active list. Selection ignores weights except zero-weight quiescing. List order controls distribution.

## Test Signals
Verify cyclic distribution across eligible destinations, skip of zero-weight and overloaded servers, deletion of the current destination, service with no destinations, and module unregister RCU synchronization.
