# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_syncvldb.h

Purpose: declares the task parameters and public UI entry point for VLDB synchronization.

Important API/types: `SVR_SYNCVLDB_PARAMS` contains `LPIDENT lpi`, which may identify a server or aggregate, and `BOOL fForce`, which controls forced synchronization. `Server_SyncVLDB(LPIDENT lpi)` opens the confirmation dialog.

Control flow contract: UI code creates this struct on OK and passes it to `taskSVR_SYNCVLDB`; `Task_Svr_SyncVLDB` deletes it after calling `AfsClass_SyncVLDB`.

State and persistence: transient task input only, no stored preferences.

Dependencies/integration: requires common Manager identity types from `svrmgr.h`; included by the dialog implementation and task implementation.

Risks/test signals: callers must pass a server or aggregate identity that remains valid across async dispatch. Tests should assert `fForce` defaults expected by the UI and task-side ownership is single-use.
