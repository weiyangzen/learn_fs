# Research: sources/distributed-fs/openafs/src/rx/rx_event.h

## sources/distributed-fs/openafs/src/rx/rx_event.h

### Purpose
`rx_event.h` exposes the RX timer event API while keeping `struct rxevent` opaque to callers.

### Important APIs
- `rxevent_Init(int nEvents, void (*scheduler)(void))`
- `rxevent_Post(struct clock *when, struct clock *now, callback, arg, arg1, arg2)`
- `rxevent_Cancel(struct rxevent **)`
- `rxevent_RaiseEvents(struct clock *wait)`
- `rxevent_Get(struct rxevent *)`, `rxevent_Put(struct rxevent **)`
- `shutdown_rxevent(void)`

### Control Flow and State
Callers initialize the package, post callbacks for absolute `struct clock` times, optionally hold references to events, cancel by pointer-to-pointer, and periodically call `rxevent_RaiseEvents` from the listener/event thread to execute due callbacks and obtain the next wait interval.

### Dependencies and Integration Points
Forward-declares `struct clock` and `struct rxevent`; actual scheduling is implemented in `rx_event.c`. Integrated by user LWP/pthread listeners and kernel event daemons.

### Risks and Edge Cases
- `rxevent_Cancel` requires a pending event pointer; a currently executing event may not cancel itself.
- Callers must use pointer-to-pointer APIs correctly because cancellation and put clear caller references.
- `when` uses RX's clock time base, which differs by platform backend.

### Test Signals
API-level tests should verify post/cancel semantics, reference get/put ownership, scheduler wakeups, and listener integration.
