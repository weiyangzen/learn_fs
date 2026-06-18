# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/trace.h

## Purpose
This tiny umbrella header connects the IRDMA trace translation unit to the connection-management tracepoint definitions.

## Important APIs, Types, And Functions
- It contains only the SPDX/copyright header and `#include "trace_cm.h"`.
- Its role is to give `trace.c` a stable include target while keeping actual trace event definitions in `trace_cm.h`.

## Control Flow
There is no runtime flow. At compile time, including this header includes all `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` declarations from `trace_cm.h`.

## State And Persistence
No state is declared here. Generated tracepoint state comes from `trace_cm.h` when included with `CREATE_TRACE_POINTS`.

## Dependencies And Integration Points
It depends directly on `trace_cm.h` and indirectly on Linux tracepoint headers and `main.h`. It integrates the single-instantiation pattern used by kernel tracepoints.

## Risks And Edge Cases
Because it is only an include shim, the main risk is accidental addition of unrelated declarations or include ordering that breaks `CREATE_TRACE_POINTS`. If future trace categories are added, this header may need to include more trace headers.

## Test Signals
Successful compilation of `trace.c` and availability of `irdma_cm` trace events are the relevant signals.
