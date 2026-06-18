# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_createrep.cpp

## Purpose
`set_createrep.cpp` implements the Create Replica dialog, allowing a read-write fileset to be replicated onto a selected aggregate.

## Important APIs, Types, And Functions
The public entry point is `Filesets_CreateReplica`. Internal handlers include `Filesets_CreateReplica_DlgProc`, `Filesets_CreateReplica_OnInitDialog`, `Filesets_CreateReplica_OnSelectServer`, `Filesets_CreateReplica_StartDisplay_Aggregates`, `Filesets_CreateReplica_OnEndTask_EnumAggregates`, and `Filesets_CreateReplica_EnableOK`. A subclass procedure supports the aggregate-list columns menu.

## Control Flow
The entry point allocates `SET_CREATEREP_PARAMS`, shows `IDD_SET_CREATEREP`, validates that the target is an aggregate, and starts `taskSET_CREATEREP`. Initialization formats the source server/aggregate/fileset into the dialog title text, restores the aggregate view, disables OK/list/server controls, and asynchronously enumerates servers. When a server is selected, aggregate enumeration starts; selecting an aggregate enables OK.

## State And Persistence
Runtime state is the source and target identity pair. `gr.viewAggMove` is reused for the aggregate list layout and stored on destroy. No registry persistence is performed directly.

## Dependencies And Integration Points
Dependencies include columns UI, display text callbacks, server combobox enumeration, aggregate list enumeration, global aggregate view state, and task IDs `taskSVR_ENUM_TO_COMBOBOX`, `taskAGG_ENUM_TO_LISTVIEW`, and `taskSET_CREATEREP`. It is used by fileset drag/drop and "replicate here" workflows.

## Risks And Edge Cases
The dialog assumes the caller supplies a valid source fileset; it validates only target aggregate on OK. Static list subclass state limits simultaneous dialogs. Failed enumeration has little user-visible handling. Reusing `gr.viewAggMove` couples create-replica and move dialog column choices.

## Test Signals
Test default target selection, server-change target clearing, aggregate selection OK enablement, formatted source text, column menu behavior, cancel cleanup, and task parameter identity correctness.
