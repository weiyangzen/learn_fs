# Research: sources/distributed-fs/openafs/src/rx/rx_event.c

## sources/distributed-fs/openafs/src/rx/rx_event.c

### Purpose
`rx_event.c` implements RX's timer event scheduler using a red-black tree keyed by event time, with a per-time queue for events that share the same timestamp.

### Important Types and Functions
- Private `struct rxevent` holds queue node, rb-tree node, scheduled time, refcount, handled flag, callback, and three callback arguments.
- `rxevent_Init` initializes clock, locks, event tree, free list, allocation unit, and optional scheduler callback.
- `rxevent_Post` allocates and inserts an event; if it becomes the earliest event, it invokes the scheduler callback.
- `rxevent_Cancel` removes a pending event and releases references.
- `rxevent_RaiseEvents` fires all expired events and returns the wait interval for the next event.
- `rxevent_Get`, `rxevent_Put`, and `rxevent_Put`'s internal refcount logic manage event references.
- `shutdown_rxevent` frees allocated event blocks.

### Control Flow
Events are allocated from a free list in batches. Posting compares the target time with existing tree nodes: earlier/later goes left/right; exact-time events are queued on the existing node. If the new event is earlier than the current first event, the scheduler callback wakes the event loop. Raising events gets current time, adjusts all event times if the clock moved backwards, repeatedly removes the first expired event or a same-time queued event, drops the tree lock, calls the callback, and releases the event. Cancellation handles both rb-tree head nodes and same-time queue elements, replacing tree nodes when necessary.

### State and Persistence Behavior
State is in-memory only: `freeEvents`, `eventTree`, `eventSchedule`, `allocUnit`, and `initialised`. `rxevent` has atomic references for tree and caller ownership. No events persist across process/kernel lifetime.

### Dependencies and Integration Points
Depends on `opr_queue`, `opr_rbtree`, `rx_atomic`, RX locks, `clock_*`, and allocation wrappers. Used by retransmission timers, keepalives, delayed ACKs, delayed aborts, challenge retries, reachability checks, NAT keepalives, and kernel/user event loops.

### Risks and Edge Cases
- Cancellation of same-time queued events and rb-tree node replacement is subtle and vulnerable to list/tree invariant bugs.
- The event comparison in `rxevent_RaiseEvents` fires events when `eventTime < now`; exactly equal timestamps wait until time advances.
- Backward clock adjustment walks the whole tree and assumes event-thread context.
- `shutdown_rxevent` destroys locks and frees allocation blocks but does not explicitly cancel outstanding logical events first.

### Test Signals
Unit tests should cover insertion ordering, equal-time queues, canceling head/list/tail events, refcount release, scheduler callback wakeups, backward-time adjustment, shutdown after many batch allocations, and stress with concurrent post/cancel/raise under pthread locks.
