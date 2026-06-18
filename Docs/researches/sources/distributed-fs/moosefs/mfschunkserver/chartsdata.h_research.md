# sources/distributed-fs/moosefs/mfschunkserver/chartsdata.h

## Purpose
`chartsdata.h` declares the initialization entry point for chunkserver chart collection.

## Important API
`int chartsdata_init(void)` initializes CPU usage tracking, registers periodic chart refresh and store callbacks, registers chart shutdown handling, and initializes the common charts subsystem through the implementation.

## Control Flow and Integration
The header is consumed by startup code that initializes chunkserver modules. After `chartsdata_init` succeeds, the module operates via callbacks registered with the common `main` loop. Callers do not drive refresh directly through this header.

## State and Persistence
No state is declared in the header. The implementation persists chart samples through the common chart store file named by `chartsdefs.h`.

## Dependencies
The header includes `<inttypes.h>`, although this particular declaration does not expose fixed-width integer arguments. The implementation depends on the chart schema and many counter providers.

## Risks
Because only init is public, failure handling at startup is important: if callers ignore a nonzero return, chart files may not be loaded or stored even though the daemon continues serving data. Direct refresh/store functions exist in the implementation but are intentionally not public.

## Test Signals
Compile-time inclusion from startup code and runtime startup logs or chart file creation are the primary signals. A test harness should call `chartsdata_init` in a configured main-loop environment and verify registered timed callbacks execute.
