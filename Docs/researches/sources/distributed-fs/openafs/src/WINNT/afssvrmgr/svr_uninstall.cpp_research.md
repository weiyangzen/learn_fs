# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_uninstall.cpp

Purpose: implements the "Uninstall File" dialog for removing a named file from a selected AFS server.

Important APIs/functions: `Server_Uninstall` is the public entry point and enforces a single global uninstall dialog via `PropCache_Search(pcSVR_UNINSTALL, NULL)`. `Server_Uninstall_DlgProc` manages help, task completions, commands, and cleanup. `Server_Uninstall_OnInitDialog` starts `taskSVR_ENUM_TO_COMBOBOX`. `Server_Uninstall_EnableOK` validates that a server and file name are present. `Server_Uninstall_OnOK` builds `SVR_UNINSTALL_PARAMS` and starts `taskSVR_UNINSTALL`.

Control flow: opening allocates a params struct with optional initial server and empty filename. The dialog disables server selection and OK while server enumeration runs. Once enumeration completes, the dialog enables server selection and reevaluates OK. OK dispatches without a reply window and closes the dialog.

State and persistence: selected server and file path are transient. `DWLP_USER` owns the init params until `WM_DESTROY`, where it is deleted. No registry/preferences are written.

Dependencies/integration: uses AfsAppLib help/dialog helpers, `StartTask`, `SVR_ENUM_TO_COMBOBOX_PACKET`, `PropCache`, and `Task_Svr_Uninstall`, which calls `AfsClass_UninstallFile`.

Risks/test signals: the dialog is global rather than per-server, so a second request focuses the existing instance even if a different server was intended. The init enum packet is not zeroed, though both fields are set. Failures happen after dialog close via task-side `ErrorDialog`. Tests should cover initial-server selection, empty filename disabling, server enum failures, and error text containing the base filename.
