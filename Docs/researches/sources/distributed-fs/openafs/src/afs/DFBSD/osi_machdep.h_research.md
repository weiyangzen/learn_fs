# sources/distributed-fs/openafs/src/afs/DFBSD/osi_machdep.h

## Purpose
Defines the minimal DragonFly BSD OSI machine-dependent time helper for OpenAFS.

## Important APIs, Types, And Functions
The header provides inline `osi_GetTime(osi_timeval32_t *atv)`, which calls `microtime` and copies seconds and microseconds.

## Control Flow
Callers pass an output timeval; the inline helper fetches current kernel time and assigns fields.

## State And Persistence
No local state is maintained.

## Dependencies And Integration Points
Depends on DragonFly `microtime` and OpenAFS `osi_timeval32_t`. It is included through `afs_osi.h`.

## Risks
Only time retrieval is defined here; other platform macros must be defined by common BSD headers or elsewhere. Time truncation into 32-bit fields may matter on long-lived systems.

## Test Signals
DragonFly builds and runtime timestamping in cache manager events should validate the helper.
