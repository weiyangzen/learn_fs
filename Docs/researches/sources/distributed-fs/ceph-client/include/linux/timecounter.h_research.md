<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timecounter.h -->
# sources/distributed-fs/ceph-client/include/linux/timecounter.h

## Purpose
declares cyclecounter/timecounter helpers for converting hardware cycles into monotonic nanoseconds.

## Important APIs, Types, and Functions
The file is 165 lines and exports these visible symbol families: types/enums `cyclecounter`, `timecounter`; macros/constants none; function-like macros `CYCLECOUNTER_MASK`; inline helpers `cyclecounter_cyc2ns`, `timecounter_adjtime`, `cc_cyc2ns_backwards`, `timecounter_cyc2time`; external prototypes `register`, `timecounter_read`.

## Control Flow
A driver provides a `cyclecounter` with read/mask/mult/shift/max_idle_ns. `timecounter_init()` seeds state, `timecounter_read()` accumulates cycle deltas, and inline conversion helpers translate forward and backward cycle timestamps.

## State and Persistence Behavior
`timecounter` stores the cyclecounter pointer, current nanoseconds, last cycle value, fractional remainder, and mask. Driver code owns serialization around reads and adjustments.

## Dependencies and Integration Points
It depends on fixed-width types and integrates with PTP hardware clocks, network timestamping, media devices, and other cycle-based clocks. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Cycle wrap, wrong mask/mult/shift, and reading less often than max idle time cause time jumps. `timecounter_adjtime()` changes accumulated time and must be synchronized with readers.

## Test Signals
Unit-test cycle wrap conversion, mult/shift scaling, backward timestamp conversion, adjtime, and compare hardware timestamp streams against PHC/PTP reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timecounter.h -->
