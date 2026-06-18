# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.cpp

Purpose: implements the confirmation dialog for synchronizing VLDB entries with a selected server or aggregate.

Important APIs/functions: `Server_SyncVLDB` opens/focuses the modeless dialog using `PropCache`. `Server_SyncVLDB_DlgProc` handles initialization, ghost-status task completion, OK/cancel, and cleanup. `Server_SyncVLDB_OnInitDialog` formats warning text for server or aggregate scope. `Server_SyncVLDB_OnOK` creates `SVR_SYNCVLDB_PARAMS` with `fForce = TRUE` and dispatches `taskSVR_SYNCVLDB`.

Control flow: server-scoped sync shows immediately. Aggregate-scoped sync first starts `taskAGG_FIND_GHOST`; if the aggregate lacks a server entry, the dialog shows an error and closes, because syncing an unexported/offline aggregate would be unsafe. Otherwise it shows the confirmation UI.

State and persistence: state is transient in `DWLP_USER` and the task packet. There are no preference writes. `PropCache` ensures a single sync dialog per identity.

Dependencies/integration: depends on `svrmgr.h`, `svr_syncvldb.h`, `propcache.h`, string resources, `StartTask`, and `Task_Svr_SyncVLDB` in `task.cpp`, which calls `AfsClass_SyncVLDB`.

Risks/test signals: OK destroys the dialog immediately after dispatch and uses no reply window, so task failures surface through global error dialogs rather than inline UI. Aggregate ghost detection relies on `GHOST_HAS_SERVER_ENTRY`; tests should cover server path, valid aggregate path, ghost aggregate rejection, forced flag mapping, and task failure error behavior.
