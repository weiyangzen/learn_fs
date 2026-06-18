# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.cpp

Purpose: Implements fileset rename workflow, including an async preflight that resolves the read-write fileset for a possibly replica/clone request.

Important APIs/functions: `Filesets_ShowRename` allocates `SET_RENAME_INIT_PARAMS` and starts `taskSET_RENAME_INIT`. `Filesets_OnEndTask_ShowRename` handles lookup result, opens the modal rename dialog, and starts `taskSET_RENAME_APPLY` on success. `Filesets_Rename_DlgProc`, `Filesets_Rename_OnInitDialog`, and `Filesets_Rename_EnableOK` implement the modal UI.

Control flow: The preflight obtains `lpiRW`; failures show refresh or not-replicated errors. The dialog displays server/aggregate/current fileset name, initializes the new-name edit control to the current name, focuses it, and enables OK only when the new name is nonempty and differs case-insensitively.

State and persistence: The apply packet stores `lpiFileset` and `szNewName`. Persistent rename effects occur in `taskSET_RENAME_APPLY`.

Dependencies/integration: Relies on `svrmgr.h` tasks, identity name getters, resource strings, and help context.

Risks: `Filesets_Rename_DlgProc` uses a static packet pointer, acceptable for modal single-use but unsafe if reentered. It validates only nonempty/different names, leaving syntax/conflict validation to the task/server.

Test signals: Rename from RW and replica selections, failed lookup, unchanged-name disablement, empty-name disablement, and task error reporting by downstream handlers.
