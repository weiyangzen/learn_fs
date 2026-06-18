# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_general.h

## Purpose
`set_general.h` declares common fileset helper APIs and quota/list constants.

## Important APIs, Types, And Functions
Constants include `ckQUOTA_DEFAULT`, `ckQUOTA_MINIMUM`, `ckQUOTA_MAXIMUM`, and `LVIS_ALL`. Functions declare fileset preference load/save, selected/focused identity lookup, focused tree item lookup, and lock-state detection.

## Control Flow
No logic exists in the header. Callers use these helpers from fileset tabs, display code, and fileset operation dialogs.

## State And Persistence
The declared preference helpers persist fileset preferences through the registry-backed preference layer. Other helpers are runtime UI state accessors.

## Dependencies And Integration Points
It depends on fileset identities/status, Win32 list/tree types, quota constants such as `ck1TB`, and `FILESET_PREF` definitions from broader `svrmgr.h`.

## Risks And Test Signals
`Filesets_GetFocusedItem` is declared but not visible in the paired implementation read here, so link or dead-code checks are important. Quota max is near signed 32-bit KB limits and must match task/server expectations.
