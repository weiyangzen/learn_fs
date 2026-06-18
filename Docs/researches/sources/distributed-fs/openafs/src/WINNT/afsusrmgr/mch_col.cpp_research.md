## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_col.cpp

Purpose: defines default machine-list column layout and displayed values. Machine accounts are represented as PTS user objects with machine-specific filtering.

Important APIs/types/functions: `Machine_SetDefaultView` and `Machine_GetColumn`.

Control flow: default view uses small icons, shows name and UID, and sets status icon mode. `Machine_GetColumn` retrieves `ASOBJPROP`, then formats name, group quota, UID, owner, or creator from `UserProperties.PTSINFO` when available.

State and persistence behavior: writes first-run defaults into `gr.viewMch` and `gr.ivMch`; persisted user changes are stored elsewhere.

Dependencies and integration points: consumed by `display.cpp` lazy text and startup defaults. Depends on `MACHINECOLUMNS`, OpenAFS cached user/PTS properties, and resource IDs.

Risks: if `fHavePtsInfo` is false, most machine columns remain blank while still reporting numeric/alphabetic type. The file comment says user-view columns, a stale comment that can mislead maintenance.

Test signals: display machines with full/missing PTS info, sort each machine column, and verify default shown columns and icon mode after first-run initialization.
