# sources/distributed-fs/glusterfs/libglusterfs/src/event-epoll.c

## Purpose
This file implements the epoll backend for GlusterFS's event subsystem. It manages file descriptor registration, one-shot epoll delivery, poller worker threads, dynamic thread reconfiguration, poller-death notifications, and rearming after handlers complete.

## Important APIs, types, and functions
The backend exports `event_ops_epoll` with `event_pool_new_epoll`, `event_register_epoll`, `event_select_on_epoll`, unregister variants, `event_dispatch_epoll`, `event_reconfigure_threads_epoll`, `event_pool_destroy_epoll`, and `event_handled_epoll`. Internal state is organized into `event_slot_epoll`, `event_slot_epoll_table`, `event_thread_data`, slot generation counters, atomic slot refs, and the `poller_death` list.

## Control flow
Registration allocates a slot from table arrays, initializes handler/data/event flags, stores index and generation in `epoll_event.data`, and calls `epoll_ctl(ADD)`. Dispatch starts poller threads and joins the first one. Workers loop in `epoll_wait()`, validate slot generation, suppress duplicate in-handler delivery, invoke the registered handler, and rely on the handler path to call `gf_event_handled()`. `event_handled_epoll()` decrements `in_handler` and rearms the fd with `epoll_ctl(MOD)` if the slot generation still matches.

## State and persistence behavior
All state is in-memory in `struct event_pool`. Slot tables persist until event-pool destruction. Slot generation values detect stale events after unregister/reuse. `do_close` defers fd close until final slot unref. Poller-death notification temporarily splices registered slots to a local list while a shrinking worker notifies handlers with `event_thread_died = 1`.

## Dependencies and integration points
The file depends on Linux `sys/epoll.h`, GlusterFS event types from `glusterfs/gf-event.h`, threading through `gf_thread_create`, syscall wrappers, atomics, locks, lists, and structured logging. The public wrappers in `event.c` choose this backend when epoll is available.

## Risks and edge cases
The backend has complex concurrency: slot refs, slot locks, event-pool mutex, generation checks, unregister racing handler execution, and thread reconfiguration all interact. Failure to call `gf_event_handled()` after a handler can leave a one-shot fd disabled. `event_select_on_epoll()` skips `epoll_ctl(MOD)` while a handler is active, relying on later rearm. Destroy mode blocks new registrations but comments acknowledge races with concurrent registration. Poller-death list slicing must avoid use-after-free and missed notifications.

## Test signals
Tests should cover register/select/unregister/close, stale generation delivery, handler rearm, missing handled behavior, concurrent unregister during handler, error/hup single handling, dynamic thread increase/decrease, destroy-mode shutdown, poller-death notifications, slot-table expansion and exhaustion, and fd close deferral until final unref.
