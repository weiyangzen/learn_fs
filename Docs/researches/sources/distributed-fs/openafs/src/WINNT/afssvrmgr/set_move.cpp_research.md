# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_move.cpp

## Purpose
`set_move.cpp` implements the Move Fileset dialog, choosing a destination aggregate for an existing fileset and starting the move task.

## Important APIs, Types, And Functions
The public entry point is `Filesets_ShowMoveTo`. Internal handlers include `Filesets_MoveTo_DlgProc`, `Filesets_MoveTo_OnInitDialog`, `Filesets_MoveTo_OnEndTask_InitDialog`, `Filesets_MoveTo_OnSelectServer`, `Filesets_MoveTo_StartDisplay_Aggregates`, `Filesets_MoveTo_OnEndTask_EnumAggregates`, and `Filesets_MoveTo_EnableOK`. A list subclass procedure supports the columns context menu.

## Control Flow
The entry point allocates `SET_MOVE_PARAMS`, shows `IDD_SET_MOVETO`, validates a target aggregate, and starts `taskSET_MOVE`. Initialization restores `gr.viewAggMove`, disables controls, and starts `taskSET_MOVETO_INIT` to fetch source status. The end-task handler formats a read-write/read-only description or shows an error, then enumerates servers. Server selection clears invalid targets and starts aggregate enumeration. Aggregate selection enables OK.

## State And Persistence
Runtime state is the source/target identity pair and the selected server stored in `DWLP_USER`. Aggregate list layout is stored in `gr.viewAggMove` through FastList view helpers. No direct registry writes occur.

## Dependencies And Integration Points
Dependencies include columns UI, display text callbacks, server/aggregate enumeration tasks, source-status task `taskSET_MOVETO_INIT`, move task `taskSET_MOVE`, resource strings, and global aggregate view state. Drag/drop code calls this entry point for move-here actions.

## Risks And Edge Cases
`Filesets_MoveTo_StartDisplay_Aggregates` sets `lpp->lpiServer = NULL`, so despite storing selected server in `DWLP_USER`, aggregate enumeration may not be server-filtered here unless the task infers it from dialog state. That is worth regression testing. Static subclass state limits simultaneous dialogs. Source-status failure cancels the dialog.

## Test Signals
Test read-write/read-only source descriptions, server selection filtering, target clearing when server changes, aggregate selection OK enablement, column chooser persistence, source-status error path, drag/drop default target, and task parameter identities.
