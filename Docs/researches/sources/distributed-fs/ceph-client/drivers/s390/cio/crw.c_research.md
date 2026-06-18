# sources/distributed-fs/ceph-client/drivers/s390/cio/crw.c

## Purpose
This file implements Channel Report Word machine-check dispatch for s390 CIO. It registers per-reporting-source handlers, runs a kernel thread that drains CRWs, handles chained/overflow reports, and enables channel-report machine checks.

## Important APIs, Types, and Functions
Public APIs are `crw_register_handler()`, `crw_unregister_handler()`, `crw_handle_channel_report()`, and `crw_wait_for_channel_report()`. Internal state includes `crw_handler_mutex`, `crw_handlers[NR_RSCS]`, atomic request counter `crw_nr_req`, and wait queue `crw_handler_wait_q`. The collector thread is `crw_collect_info()`.

## Control Flow
Subsystem users register a handler for a CRW reporting source code. Machine-check notification calls `crw_handle_channel_report()`, incrementing `crw_nr_req` and waking `kmcheck`. The collector waits until work exists, repeatedly calls `stcrw()`, records up to two chained CRWs, calls all handlers on overflow, or dispatches the completed CRW/chained pair to the handler selected by `rsc`. When draining finishes, it decrements the request count and wakes waiters. Init starts `kmcheck` and sets the CR14 channel report submask bit.

## State and Persistence
All state is volatile. Handler registrations persist only while modules/subsystems remain loaded. CRWs are consumed from hardware or injection once read. There is no disk persistence.

## Dependencies and Integration Points
It depends on architecture control registers, `stcrw()`, kthreads, wait queues, and subsystem handlers registered by CSS/CHSC/channel-path code. When injection is enabled elsewhere, `stcrw()` retrieval may be substituted or augmented by synthetic CRW data.

## Risks and Test Signals
Risk areas include serialization under `crw_handler_mutex` while handlers run, only supporting two chained CRWs directly, overflow fanout to all handlers, signal handling in the collector, and handler registration races. Test signals include CRW injection for CSS/SCH/CPATH sources, overflow CRW handling, chained CRW pairs, unregister during idle, `crw_wait_for_channel_report()` draining, and boot verification that `kmcheck` starts and CR14 is enabled.
