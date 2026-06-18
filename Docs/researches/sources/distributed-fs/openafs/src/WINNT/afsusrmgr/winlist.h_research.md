# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.h

Purpose: declares the process-local modeless property-window registry.

Important APIs/types: `WINDOWLISTTYPE` differentiates user, group, and cell property windows. `ASID_ANY` is a wildcard for searches. Exports are `WindowList_Add`, `WindowList_Search`, and `WindowList_Remove`.

State and dependencies: no state in the header; implementation stores registry entries in a static array.

Risks and test signals: object ID `0` has semantic use for multi-selection windows, while `ASID_ANY` is `-1`; tests should verify callers do not confuse those cases.
