<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c

## Purpose
`eeh_event.c` decouples EEH error detection from recovery. It queues failure events that may be produced in interrupt context and processes them in the `eehd` kernel thread.

## Important APIs, Types, And Functions
State includes `eeh_eventlist_lock`, `eeh_eventlist_event`, and `eeh_eventlist`. Functions are private `eeh_event_handler()`, `eeh_event_init()`, `__eeh_send_failure_event()`, `eeh_send_failure_event()`, and `eeh_remove_event()`.

## Control Flow
The handler waits for completions, pops one event under the spinlock, calls `eeh_handle_normal_event(pe)` when the event has a PE or `eeh_handle_special_event()` otherwise, then frees the event. Send allocates with `GFP_ATOMIC`, optionally saves a stack trace, marks the PE recovering before queueing, appends to the list, and completes the event. The public send wrapper drops events when debugfs no-recover is enabled. Remove walks the queue and removes matching PE, PHB, or all events, with special handling to avoid dropping isolated events unless forced.

## State And Persistence
The event queue is in-memory only. PE recovery bits are set before queue insertion to protect PEs from being freed while pending.

## Dependencies And Integration Points
It integrates with the EEH core detector, EEH driver recovery functions, kthread/completion APIs, stack trace support, and debugfs no-recover flag from `eeh.c`.

## Risks
Allocation failure drops recovery and logs an error. Marking a PE recovering before event processing must be cleared by recovery paths. Event removal rules can lose or duplicate recovery if force usage is wrong.

## Test Signals
Signals include `eehd` thread startup, forced debugfs recovery, async recovery after interrupt-context detection, no-recover drops, duplicate event purging, and stack traces printed during normal recovery when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_event.c -->
