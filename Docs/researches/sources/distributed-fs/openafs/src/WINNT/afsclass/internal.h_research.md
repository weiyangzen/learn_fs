# sources/distributed-fs/openafs/src/WINNT/afsclass/internal.h

## Purpose
`internal.h` is the private header tying `afsclass` implementation files to the worker dispatch layer and common internal utilities. It exposes allocation growth constants, shared globals, and helper prototypes used by class objects that manage servers, services, aggregates, filesets, and BOS restart schedules.

## Important APIs, types, and functions
The header defines growth increments `cREALLOC_SERVERS`, `cREALLOC_SERVICES`, `cREALLOC_AGGREGATES`, and `cREALLOC_FILESETS`. It declares the globals `cRefreshAllReq`, `fLongServerNames`, and `dwWant`. It exposes `AfsClass_GetCriticalSection`, time helpers, recurring-time helpers, `AfsClass_FileTimeToDouble`, `AfsClass_SplitFilename`, BOS restart conversion helpers, and `AfsClass_GenFullUserName`.

## Control flow
There is no executable control flow in the header. It enforces include ordering by including `worker.h`, making the private helper layer aware of all worker task and packet definitions. Implementation files include this header to reach the shared lock and helper conversions before calling admin DLL wrappers.

## State and persistence behavior
The header declares process-global state that is defined in `internal.cpp`. These globals are not persisted directly; they coordinate in-memory refresh behavior, display/name preferences, and refresh-domain selection for the `afsclass` process.

## Dependencies and integration points
`internal.h` depends on `worker.h`, which pulls in the AFS admin client, vos, bos, kas, pts, and utility admin headers. That makes this header an integration point between higher-level C++ class code and C-style AFS admin APIs. The BOS restart prototypes require `bos_RestartTime_t` and related masks from the admin headers.

## Risks and edge cases
Any file including `internal.h` inherits the large `worker.h` dependency surface and its Windows/AFS type requirements, increasing rebuild coupling. The fixed reallocation constants encode growth policy globally and may be inefficient for unusually large cells. Since globals are externally mutable, refresh and display behavior can change from any implementation file that includes this header.

## Test signals
Build tests should compile all `afsclass` users with this header under the supported Windows toolchain. Integration tests should verify that server/service/aggregate/fileset collections grow correctly at the declared increments and that callers see consistent `dwWant`, `fLongServerNames`, and `cRefreshAllReq` behavior across translation units.
