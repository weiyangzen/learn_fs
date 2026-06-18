# sources/distributed-fs/ceph-client/net/lapb/lapb_timer.c

## Purpose
`lapb_timer.c` implements LAPB T1 and T2 timer management. T1 handles establishment, release, retransmission, and frame-reject retry. T2 delays receive acknowledgments so RR responses can be coalesced.

## Important APIs, Types, and Functions
Externally used helpers are `lapb_start_t1timer()`, `lapb_start_t2timer()`, `lapb_stop_t1timer()`, `lapb_stop_t2timer()`, and `lapb_t1timer_running()`. Internal callbacks are `lapb_t1timer_expiry()` and `lapb_t2timer_expiry()`.

## Control Flow
Start helpers delete any existing timer instance, install the callback, set expiry relative to `jiffies`, mark the running flag, and add the timer. T2 expiry checks that it is still the active timer and, if an ACK is pending, clears the flag and sends `lapb_timeout_response()`. T1 expiry switches on LAPB state: state 0 DCE may send DM before establishing; state 1 resends SABM(E) or times out; state 2 resends DISC or confirms timeout; state 3 requeues and retransmits I-frames or disconnects on retry exhaustion; state 4 retransmits FRMR or disconnects on retry exhaustion. Most non-terminal paths restart T1.

## State and Persistence
The file mutates timer running flags, retry count, state, queues, and condition flags indirectly through helper calls. All state is in-memory within `struct lapb_cb`.

## Dependencies and Integration Points
Timer callbacks lock `lapb->lock` with bottom halves disabled and call helpers from interface, output, and subroutine files. The unregister path synchronizes timer deletion to prevent callbacks from using freed control blocks.

## Risks and Edge Cases
Running flags are separate from kernel timer pending state; both are checked to avoid handling stale callbacks. Retry exhaustion semantics differ by state and must match LAPB expectations. Timer callbacks can race with stop/start paths and unregister, making lock and `timer_delete_sync()` usage important.

## Test Signals
Tests should simulate T1/T2 expiry in every LAPB state, verify N2 retry boundaries, assert correct indications/confirmations on timeout, check stale timer callbacks are ignored after stop/restart, and use lockdep/KASAN during unregister with timers active.
