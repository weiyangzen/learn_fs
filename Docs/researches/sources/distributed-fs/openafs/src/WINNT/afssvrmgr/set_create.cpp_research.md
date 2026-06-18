# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_create.cpp

## Purpose
`set_create.cpp` implements the Create Fileset dialog. It collects a fileset name, target aggregate, quota, quota units, and optional clone creation flag, then starts the asynchronous fileset creation task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_Create`. Internal handlers include `Filesets_Create_DlgProc`, `Filesets_Create_OnInitDialog`, `Filesets_Create_OnSelectServer`, `Filesets_Create_StartDisplay_Aggregates`, `Filesets_Create_OnEndTask_EnumAggregates`, `Filesets_Create_EnableOK`, and `Filesets_Create_OnEndTask_FindQuotaLimits`. A subclass procedure handles the columns context menu for the aggregate list.

## Control Flow
`Filesets_Create` allocates `SET_CREATE_PARAMS`, sets defaults (`ckQUOTA_DEFAULT`, no clone), displays `IDD_SET_CREATE`, validates the aggregate and name, and starts `taskSET_CREATE`. The dialog asynchronously enumerates servers to a combobox, enumerates aggregates to a FastList, and finds quota limits for the selected aggregate. Selection and column changes refresh the aggregate list. Quota unit changes recalculate spinner limits. OK is enabled only when a target aggregate and nonempty fileset name exist.

## State And Persistence
Runtime state is in `SET_CREATE_PARAMS` plus global view state `gr.viewAggCreate` and `gr.cbQuotaUnits`. The aggregate list view layout is restored/stored through `FL_RestoreView` and `FL_StoreView`; global settings persistence happens elsewhere. The task owns the params after a successful OK.

## Dependencies And Integration Points
Dependencies include `set_general.h` quota constants, columns UI, server-window helpers, display text callbacks, task packets `SVR_ENUM_TO_COMBOBOX_PACKET` and `AGG_ENUM_TO_LISTVIEW_PACKET`, and task IDs `taskSET_CREATE`, `taskAGG_FIND_QUOTA_LIMITS`, `taskSVR_ENUM_TO_COMBOBOX`, and `taskAGG_ENUM_TO_LISTVIEW`.

## Risks And Edge Cases
Name validation is limited to nonempty text in this UI; deeper validation must occur in the task layer. Quota conversions can lose precision when switching to MB units. The list subclass procedure uses a static original WNDPROC, so multiple simultaneous create dialogs would share it. Server/aggregate enumeration failure handling is minimal.

## Test Signals
Test initial parent aggregate selection, empty-name OK disable, quota spinner range and unit conversion, aggregate selection updates quota limits, server change clears invalid aggregate target, column chooser persistence, cancel cleanup, and task parameter correctness on OK.
