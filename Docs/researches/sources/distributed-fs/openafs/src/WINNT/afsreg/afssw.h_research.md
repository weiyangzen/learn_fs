# sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.h

## Purpose
Declares the public registry accessors for OpenAFS software configuration.

## Important APIs, Types, And Functions
The header declares `afssw_GetServerInstallDir`, `afssw_GetClientCellServDBDir`, `afssw_GetClientCellName`, `afssw_SetClientCellName`, `afssw_GetServerVersion`, and `afssw_GetClientVersion`, all under C linkage for C++ callers.

## Control Flow
Callers use these functions to read allocated strings or version triples, and to write the client cell name. Return convention is `0` on success and `-1` with `errno` set for failures.

## State And Persistence
The declarations represent access to persistent registry configuration under the keys defined in `afsreg.h`; the header itself stores no state.

## Dependencies And Integration Points
It is consumed by installer/configuration tools and pairs with `afssw.c`. Consumers must free returned strings from the getter functions.

## Risks And Test Signals
The implementation contains `afssw_GetClientInstallDir`, but this header does not declare it, so callers relying on the header cannot use that accessor without an external declaration. Compile coverage for all intended consumers is the main signal.
