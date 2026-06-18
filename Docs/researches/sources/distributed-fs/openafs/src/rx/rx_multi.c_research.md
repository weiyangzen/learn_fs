# Research: sources/distributed-fs/openafs/src/rx/rx_multi.c

## sources/distributed-fs/openafs/src/rx/rx_multi.c

### Purpose
`rx_multi.c` implements the runtime support for multi-RX calls, allowing similar RPC calls to be issued concurrently over multiple connections and processed as replies arrive.

### Important Functions
- `multi_Init` allocates call and ready arrays plus a `multi_handle`, initializes lock/cv, creates one `rx_NewCall` per connection, and installs `multi_Ready` as each call's arrival procedure.
- `multi_Select` waits until a call index is ready or all calls are ready, then returns the next ready index or `-1`.
- `multi_Ready` is the RX arrival callback that appends an index to the ready list and wakes waiters.
- `multi_Finalize` aborts any unfinished calls with `RX_USER_ABORT`, destroys synchronization primitives, and frees allocated arrays/handle.

### Control Flow
Callers use the macros in `rx_multi.h` to start all calls, flush writes, and then repeatedly select ready replies. The arrival callback is invoked when the first reply packet or abort arrives. `multi_Select` blocks on a condition variable or LWP sleep until new ready entries exist. Finalization ensures outstanding calls are ended.

### State and Persistence
`multi_handle` state is allocated per multi-call block and freed at the end. No durable persistence.

### Dependencies and Integration Points
Depends on `rx_NewCall`, `rx_SetArrivalProc`, `rx_FlushWrite`, `rx_EndCall`, RX sleep/wakeup or locks, and allocation wrappers. It is designed for rxgen-generated multi-call macros.

### Risks and Edge Cases
- Allocation failure calls `osi_Panic`, not a recoverable error.
- Complex work inside a multi body can keep call channels occupied and cause deadlocks; `rx_multi.h` documents this risk.
- Concurrent `multi_Rx` over the same connections must use consistent connection ordering.
- Arrival callback ordering and ready array bounds depend on exactly one first-ready event per call.

### Test Signals
Tests should cover multiple successful replies, aborts/errors, finalization aborting unfinished calls, ready ordering, sleep/wakeup behavior, and concurrent calls with consistent connection order.
