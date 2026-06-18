# sources/distributed-fs/ceph-client/include/linux/trace_clock.h

## Purpose
Declares trace clock functions used by tracing infrastructure to timestamp events with different precision/scalability tradeoffs.

## Important APIs, Types, And Functions
Exports `trace_clock_local()`, `trace_clock()`, `trace_clock_jiffies()`, `trace_clock_global()`, and `trace_clock_counter()`, all returning `u64` and marked `notrace`.

## Control Flow
The header has no implementation. Runtime callers choose local, medium/default, jiffies, global monotonic, or counter clocks depending on ordering and overhead needs.

## State, Persistence, And Dependencies
No state is defined here. It includes compiler/types and architecture-specific `asm/trace_clock.h`, which may provide arch-optimized definitions or backing state.

## Integration Points
Used by ftrace, trace events, ring-buffer timestamping, and tracing UI clock selection. The functions must be safe from tracing recursion because they are `notrace`.

## Risks And Test Signals
Risks are non-monotonic timestamps when the wrong clock is selected, recursion if traced, and architecture implementation drift. Test signals include per-CPU and global ordering checks, tracing recursion tests, and build coverage across architectures.
