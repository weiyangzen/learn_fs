# sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.h

## Purpose
`chartsdata.h` exposes the chunkserver chart subsystem initialization entry point.

## Important APIs, Types, And Functions
- `int chartsdata_init(void)` initializes timers, event-loop hooks, and chart storage for chunkserver metrics.

## Control Flow
Callers invoke `chartsdata_init` during chunkserver startup. Refresh, store, and termination are registered internally by the implementation.

## State And Persistence
The header owns no state. The implementation persists samples through the chart subsystem.

## Dependencies And Integration Points
It includes `common/platform.h` and integer types, and it is consumed by chunkserver startup code.

## Risks
The narrow API hides initialization side effects. Callers must know that cleanup is registered with the event loop rather than manually exposed.

## Test Signals
No direct tests are listed for this header.
