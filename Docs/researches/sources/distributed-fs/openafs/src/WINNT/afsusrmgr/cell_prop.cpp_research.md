# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.cpp

Purpose: implements the Account Manager cell properties sheet, currently focused on general cell id allocation limits.

Important APIs/functions: `Cell_ShowProperties` opens/focuses the modeless property sheet and selects a requested tab. `CellProp_General_DlgProc` handles sheet lifetime, help, notifications, apply, and dirty marking. `CellProp_General_OnInitDialog` registers object listening and formats the cell name. `CellProp_General_UpdateDialog` reads cell properties and updates spinners. `CellProp_General_OnApply` dispatches `taskCELL_CHANGE`.

Control flow: if a sheet for `g.idCell` is already open, `WindowList_Search` focuses it and optionally changes tab. Otherwise a property sheet is created with the general tab. The tab starts an `OBJECT_LISTEN` task for the cell and reacts to `WM_ASC_NOTIFY_OBJECT` by reloading current values.

State and persistence: no direct settings persistence. The persisted cell limits live in the AFS admin server/cell and are changed asynchronously through `CELL_CHANGE_PARAMS`. Window de-duplication is held in `WindowList`.

Dependencies/integration: uses admin-server client fast property reads, object-listen task, property sheet helpers, spinner helpers, `winlist.h`, and localized resources.

Risks: `asc_ObjectPropertiesGet_Fast` return value is ignored in update; stale/uninitialized `Properties` could populate spinners on failure. Spinner ranges use negative max constants for signed id semantics and should be validated carefully. Tests should cover open/focus behavior, listener registration/unregistration, property refresh notification, apply packet fields, and failed property reads.
