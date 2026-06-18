# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-event.h

## Purpose
Defines the low-level event loop abstraction used to register file descriptors, dispatch readiness notifications, manage poller threads, and support epoll-backed event processing.

## APIs, Types, and Functions
`event_handler_t` callbacks receive fd, slot index, generation, user data, readiness flags, error flag, and thread-exit notification. `event_pool` stores ops, epoll/poll fd data, breaker pipe, registration arrays, epoll slot tables, poller-death list, event cache, configured and active thread counts, auto-thread count, synchronization primitives, destroy flag, and poller thread IDs. `event_slot_epoll` tracks fd, events, generation, slot index, refs, close/handler/error state, data, handler, poller-death link, and lock. Public wrappers include `gf_event_pool_new()`, register/unregister/close, select-on, dispatch, reconfigure threads, destroy, dispatch-destroy, and handled notification.

## Control Flow, State, and Persistence
Callers create a pool, register fds with handlers, dispatch from one or more poller threads, modify interest masks with `select_on`, and unregister or unregister-close when done. Generation fields protect against stale fd events after slot reuse. State persists for the process lifetime of the event pool.

## Dependencies and Integration
Depends on pthreads, atomics/locks, list primitives, and `common-utils.h`. Used by RPC transports, sockets, management listeners, and client/server event processing.

## Risks and Test Signals
Risks include stale event delivery, fd close races, thread reconfiguration races, poller death notification ordering, and fallback differences between poll and epoll. Test signals include register/unregister stress, generation mismatch tests, multi-thread dispatch, unregister-close race tests, and clean shutdown with active handlers.
