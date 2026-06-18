# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.cpp

Purpose: Implements the fileset restore dialog. It lets users choose a dump file, target fileset name, target server/aggregate, and incremental mode before starting restore.

Important APIs/functions: `Filesets_Restore` opens the modal dialog and dispatches `taskSET_RESTORE` if required fields are present. `Filesets_Restore_DlgProc` coordinates async lookup and server/aggregate enumeration. `Filesets_Restore_OnSetName` starts `taskSET_LOOKUP`. `Filesets_Restore_OnEndTask_LookupFileset` decides create-vs-overwrite UI state. `Filesets_Restore_OnBrowse` uses `GetOpenFileName` for dump selection.

Control flow: Initialization subclasses the aggregate list, restores `gr.viewAggRestore` from related aggregate views when first used, sets defaults from an optional parent identity, runs lookup once, and starts `taskSVR_ENUM_TO_COMBOBOX`. Server selection triggers `taskAGG_ENUM_TO_LISTVIEW`. Fileset name edits start async lookup, which can change `psrp->lpi` from aggregate target to existing fileset target and disable server/aggregate choice for overwrite.

State and persistence: `SET_RESTORE_PARAMS` stores chosen target identity, fileset name, filename, and incremental flag. Column layout persists in `gr.viewAggRestore` on destroy. Actual restore changes occur in `taskSET_RESTORE`.

Dependencies/integration: Uses server and aggregate enumeration packets, `set_general.h` for lookup packet, `svr_window.h`, `display.h`, `columns.h`, and `FastList` helpers.

Risks: `Filesets_Restore_OnEndTask_EnumAggregates` is empty, so aggregate enumeration failure feedback depends on lower display behavior. Multiple rapid name changes can queue overlapping lookup tasks; late completion could update `psrp->lpi` for stale text if the task layer does not coalesce. OK enablement relies on `psrp->lpi` not being a server.

Test signals: Restore into existing fileset, restore creating new fileset, parent server/aggregate/fileset defaults, failed lookup, server switch, empty filename/name, browse filter, incremental checkbox, and column persistence.
