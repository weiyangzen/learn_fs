# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.c

## Purpose
Provides a small embedded CPU bitmask implementation used for cpupower CPU selection and online/offline CPU reporting.

## Important APIs, Types, and Functions
Public APIs are `bitmask_alloc`, `bitmask_free`, `bitmask_setbit`, `bitmask_setall`, `bitmask_clearall`, `bitmask_isallclear`, `bitmask_isbitset`, `bitmask_first`, `bitmask_last`, `bitmask_next`, `bitmask_parselist`, and `bitmask_displaylist`. Internal helpers implement word layout, token scanning, and range emission.

## Control Flow, State, and Persistence
Masks are heap allocated as arrays of unsigned long sized by bit count. Parsing clears the mask first, accepts comma-separated numbers/ranges with optional stride, rejects out-of-range and malformed terms, and leaves the mask clear on error. Display collapses consecutive set bits into ranges. State lives only in caller-owned heap objects.

## Dependencies and Integration Points
Used by `cpupower.c`, frequency/idle setters, monitor filtering, and helper CPU state routines. The layout intentionally follows kernel affinity bitmask word ordering rather than byte arrays.

## Risks and Test Signals
`while (p = q, q = nexttoken(...), p)` relies on assignment in condition and can trigger warnings. A stride of zero is not explicitly rejected and can create an infinite loop for input like `0-3:0`. Allocation users often do not handle NULL. Test parser success/failure cases, stride zero, max CPU boundary, display buffer truncation, and empty masks.
