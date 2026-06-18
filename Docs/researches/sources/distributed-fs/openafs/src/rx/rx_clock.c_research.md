# Research: sources/distributed-fs/openafs/src/rx/rx_clock.c

## sources/distributed-fs/openafs/src/rx/rx_clock.c

### Purpose
`rx_clock.c` implements the older non-pthread, non-gettimeofday user-space elapsed-time backend using `ITIMER_REAL`, while other builds mostly use inline macros from `rx_clock.h`.

### Important Functions and State
- `clock_Init` initializes the relative clock and calls `clock_UpdateTime`.
- `clock_UnInit` resets initialization state.
- `clock_UpdateTime` reads the remaining interval timer and computes elapsed time into global `clock_now`.
- `clock_Sync` resets the interval timer to a large `STARTVALUE` and advances `relclock_epoch` so elapsed time remains monotonic across timer resets.
- Globals include `clock_now`, `clock_haveCurrentTime`, `clock_nUpdates`, and static epoch/start values.

### Control Flow
On initialization, `clock_Sync` installs an ignored `SIGALRM` handler and calls `setitimer`. Later `clock_UpdateTime` computes elapsed offset from the decrementing timer; if the timer has counted below half the start value, it calls `clock_Sync` to avoid expiration. The `clock_GetTime` macro in `rx_clock.h` lazily calls `clock_UpdateTime` when `clock_haveCurrentTime` has been cleared by `clock_NewTime`.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_clock.h`, `setitimer`, `getitimer`, `signal`, and `osi_Panic`. RX event scheduling and retransmission timing depend on this time base when this backend is active.

### Risks and Edge Cases
- This backend monopolizes `ITIMER_REAL`; other code using it can break RX timing.
- The time base is elapsed time since `clock_Init`, not wall time, unlike gettimeofday/pthread paths.
- System timer rounding is handled, but signal/timer interactions remain platform-sensitive.
- Time moving backwards is mostly handled by `rx_event.c`, not this file.

### Test Signals
Tests should verify event scheduling under this backend, repeated timer resyncs, `clock_NewTime` caching behavior, and no timer expiration after long-running processes.
