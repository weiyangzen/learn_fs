# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/queue.c

Purpose: Provides the SMT event queue used to serialize hardware, timer, and management events into ECM, CFM, RMT, SMT, and PCM state machines.

Important APIs/types/functions: Exports `ev_init()`, `queue_event()`, `timer_event()`, `ev_dispatcher()`, and `smt_online()`. Concentrator debug builds also expose `do_smt_flag()`.

Control flow: `ev_init()` resets producer/consumer pointers. `queue_event()` stores class/event at `ev_put`, advances and wraps the ring pointer, and logs an overrun if producer catches consumer. `timer_event()` decodes a timer token into class/event and queues it. `ev_dispatcher()` drains queued events, dispatching by class to `ecm()`, `cfm()`, `rmt()`, `smt_event()`, or `pcm()` for PHY classes, and updates `ev_get` after each event so nested `queue_event()` calls can detect overflow. `smt_online()` queues ECM connect/disconnect and immediately dispatches.

State and persistence behavior: Mutates `smc->q.ev_put`, `smc->q.ev_get`, and `smc->q.ev_queue[]`. The queue is runtime-only, but it is the ordering mechanism for state-machine transitions that update persistent MIB state and hardware controls.

Dependencies and integration points: Integrates with the SMT timer package, ISR path in `hwmtm.c`, and all major SMT state machines. Event class constants and queue storage come from `smc.h`/FDDI headers. `smt_online()` is the public control path for connecting to or disconnecting from the ring.

Risks: On overflow it logs but does not stop insertion, so old unprocessed events may be overwritten. Dispatch is synchronous and can enqueue more events recursively, making ordering important. Unknown classes panic. There is no visible locking in this file; callers must provide serialization appropriate to ISR/task context.

Test signals: Queue wraparound; overrun logging; timer token decoding; connect/disconnect through `smt_online()`; dispatch to each state machine class; nested event production during dispatch; invalid class panic path.
