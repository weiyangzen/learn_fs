# sources/distributed-fs/glusterfs/libglusterfs/src/event.c

## Purpose
This file is the backend-neutral public facade for GlusterFS event handling. It chooses epoll or poll, forwards registration and dispatch operations through `event_ops`, and coordinates event-poller shutdown.

## Important APIs, types, and functions
Public APIs include `gf_event_pool_new`, `gf_event_register`, `gf_event_unregister`, `gf_event_unregister_close`, `gf_event_select_on`, `gf_event_dispatch`, `gf_event_reconfigure_threads`, `gf_event_dispatch_destroy`, `gf_event_pool_destroy`, and `gf_event_handled`. The shutdown helper uses `struct event_destroy_data` and `poller_destroy_handler`.

## Control flow
`gf_event_pool_new()` tries `event_ops_epoll.new()` when epoll is compiled in and falls back to `event_ops_poll.new()` on failure. Other wrapper APIs validate the pool and call the selected backend. `gf_event_dispatch_destroy()` creates a nonblocking pipe, registers the read end, marks the pool as destroy mode, reconfigures event threads to zero, writes wakeups to the pipe while waiting on `event_pool->cond`, unregisters the pipe, and closes both fds.

## State and persistence behavior
The facade mutates backend event-pool state: selected `ops`, destroy flag, active thread count, and registered destroy pipe. No persistent storage occurs. `gf_event_pool_destroy()` only destroys the pool if destroy mode is set and active thread count is zero.

## Dependencies and integration points
It depends on `glusterfs/gf-event.h`, `timespec_now_realtime`, syscall wrappers, pthread condition waits, and the backend symbols from `event-epoll.c` and `event-poll.c`. RPC transports and other async subsystems call this facade instead of backend-specific APIs.

## Risks and edge cases
Shutdown is timing-sensitive: the destroy pipe must wake all pollers, handlers must drain it and call `gf_event_handled()`, and the retry count is bounded by the prior thread count plus ten. If pipe registration fails, cleanup closes fds but may leave destroy not set. `gf_event_pool_destroy()` silently refuses destruction if called before dispatch destroy completes. The parameter names in `poller_destroy_handler()` swap `poll_out` and `poll_in`, though only handled cleanup matters there.

## Test signals
Tests should cover epoll selection, poll fallback, wrapper validation failures, dispatch destroy with active pollers, timeout/retry behavior, destroy pipe cleanup, refusal to destroy before shutdown, `gf_event_handled()` delegation on epoll and no-op behavior on poll, and failure injection for pipe/register/write paths.
