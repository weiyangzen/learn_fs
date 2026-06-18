# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.h

Purpose: declares the uninstall-file task packet and public dialog entry point.

Important API/types: `SVR_UNINSTALL_PARAMS` carries the target `LPIDENT lpiServer` and remote filename/path in `szUninstall[MAX_PATH]`. `Server_Uninstall(LPIDENT lpiServer = NULL)` starts the UI, optionally preselecting a server.

Control flow contract: the dialog and task code allocate this struct for different lifetimes: one instance is dialog state during initialization, and another is task input on OK. `Task_Svr_Uninstall` owns deletion for task input.

State and persistence: transient only; no persistent preferences or cached file lists.

Dependencies/integration: depends on Manager identity and path constants; included by UI and task code.

Risks/test signals: remote filenames longer than `MAX_PATH - 1` are truncated by UI reads. Tests should check default argument callers and that an empty `szUninstall` is never dispatched.
