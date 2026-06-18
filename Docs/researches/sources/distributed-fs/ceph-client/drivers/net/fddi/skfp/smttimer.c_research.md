# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/smttimer.c

## Purpose
`smttimer.c` implements the SMT timer queue used by the FDDI state machines and SMT agent. It multiplexes many logical `struct smt_timer` objects onto the hardware timer hooks `hwt_start()`, `hwt_stop()`, and `hwt_read()` using a delta-ordered linked list.

## Important APIs and Functions
The public timer API is `smt_timer_init()`, `smt_timer_stop()`, `smt_timer_start()`, `smt_force_irq()`, and `smt_timer_done()`. The internal engine is `timer_done(struct s_smc *smc, int restart)`. Expired timers are delivered through `timer_event(smc, token)`.

## Control Flow
Initialization clears the queue and fast timer state, then initializes the hardware timer. Starting a timer converts microseconds to 16 microsecond hardware ticks, clamps zero to one tick, removes any existing instance of the same timer, stores the token and owning SMC, then inserts it into the delta list. If the queue was empty, the hardware timer is started directly; otherwise `timer_done(..., restart=0)` first accounts for elapsed ticks so insertion is relative to current time.

Stopping a timer marks it inactive, unlinks it from the delta queue, repairs the next timer's delta by adding the removed delta, and stops the hardware timer if the removed timer was the only queued timer. `smt_force_irq()` schedules the special fast timer after 32 microseconds with an `SM_FAST` token. When the hardware timer expires, `smt_timer_done()` calls `timer_done(..., restart=1)`, which reads elapsed ticks, detaches all expired timers, delivers their tokens, and restarts the hardware timer for the next queued delta.

## State, Dependencies, and Integration
State lives in `smc->t.st_queue` and `smc->t.st_fast`, plus the per-timer `tm_active`, `tm_next`, `tm_delta`, `tm_token`, and `tm_smc` fields. The module integrates with SMT event dispatch, state-machine timers, and hardware-specific timer primitives.

## Risks and Test Signals
Risks are delta-list corruption, double-start/double-stop behavior, elapsed-time correction before insertion, and reentrant timer callbacks that mutate the queue. Tests should cover inserting before/middle/after existing timers, stopping head/middle/tail timers, stopping the only timer, forced fast IRQ delivery, multiple expirations in one hardware tick, and callback-driven timer restart.
