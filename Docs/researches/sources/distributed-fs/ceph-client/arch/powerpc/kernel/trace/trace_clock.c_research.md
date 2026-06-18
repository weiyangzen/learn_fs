# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/trace_clock.c

## Purpose
Provides a PowerPC trace clock backed directly by the architecture timebase.

## Important APIs, Types, and Functions
- `trace_clock_ppc_tb()` returns `get_tb()` and is marked `notrace`.

## Control Flow and State
The function is a single read of the timebase register through `get_tb()`.

## State and Persistence Behavior
No mutable state. It exposes raw monotonically increasing timebase ticks to tracing.

## Dependencies and Integration Points
Depends on `asm/trace_clock.h` declarations and `asm/time.h` timebase access. Used by tracing clock selection.

## Risks
The value is not nanoseconds and assumes synchronized, valid timebase behavior. It must remain `notrace` to avoid tracing recursion.

## Test Signals
Select the PowerPC trace clock, verify monotonically increasing trace timestamps across CPUs, and test with timebase synchronization/error scenarios.
