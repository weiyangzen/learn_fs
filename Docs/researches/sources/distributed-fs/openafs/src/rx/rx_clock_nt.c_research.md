# Research: sources/distributed-fs/openafs/src/rx/rx_clock_nt.c

## sources/distributed-fs/openafs/src/rx/rx_clock_nt.c

### Purpose
`rx_clock_nt.c` implements the Windows NT RX clock backend using high-resolution performance counters.

### Important Functions and State
- `clock_Init` obtains `QueryPerformanceFrequency`, marks initialization, and updates current time.
- `clock_UnInit` clears initialization state for non-kernel builds.
- `clock_UpdateTime` reads `QueryPerformanceCounter`, subtracts `rxi_clock0`, converts ticks to seconds/useconds, and updates `clock_now`, `clock_haveCurrentTime`, and `clock_nUpdates`.
- Globals: `clock_now`, `clock_haveCurrentTime`, `clock_nUpdates`, `rxi_clock0`, and `rxi_clockFreq`.

### Control Flow and Integration
This file is compiled only for `AFS_NT40_ENV`. `rx_clock.h` undefines or maps clock macros so these functions provide the concrete implementation. RX event and timeout code consume the same `struct clock` API.

### State and Persistence
State is in-memory only and process-local. The epoch is the captured performance counter baseline in `rxi_clock0`.

### Risks and Edge Cases
- The file shown initializes frequency but does not set `rxi_clock0` in `clock_Init`; callers must ensure it has a meaningful baseline elsewhere or elapsed time starts from zero-initialized process state.
- If no high-performance counter is available, the process exits.
- Double conversion may lose precision for very long runtimes.

### Test Signals
Windows-specific tests should validate monotonic increases, correct usec normalization, initialization of `rxi_clock0`, and event scheduling after long-running uptime.
