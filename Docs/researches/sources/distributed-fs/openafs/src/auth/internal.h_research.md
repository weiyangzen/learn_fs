# sources/distributed-fs/openafs/src/auth/internal.h

## Purpose
`internal.h` declares private auth/cellconfig helper functions shared between implementation files in `src/auth`.

## Important APIs, types, and functions
It declares `_afsconf_Check`, `_afsconf_Touch`, `_afsconf_IntGetKeys`, `_afsconf_IsClientConfigDirectory`, `_afsconf_LoadKeys`, `_afsconf_InitKeys`, `_afsconf_FreeAllKeys`, `_afsconf_GetLocalCell`, `_afsconf_LoadRealms`, and `_afsconf_FreeRealms`.

## Control flow
No runtime control flow is present. The declarations enable `cellconfig.c`, `keys.c`, and `realms.c` to call each other's internal routines.

## State and persistence
The declared functions operate on `struct afsconf_dir`, especially config reload state, CellServDB mtimes, key queues, and realm lists.

## Dependencies and integration points
It is included by `cellconfig.c` and related auth implementation files. It intentionally avoids being a public installed API.

## Risks
Because these helpers are private, external code should not depend on them. Callers must respect locking expectations, especially `_afsconf_Check` and `_afsconf_GetLocalCell`, which are used under the global afsconf lock in `cellconfig.c`.

## Test signals
Compile all auth objects together, exercise reload/touch/key/realm lifecycle through public APIs, and use static analysis for lock-order assumptions around internal calls.
