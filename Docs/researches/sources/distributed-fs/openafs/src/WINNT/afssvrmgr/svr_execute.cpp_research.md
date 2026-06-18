# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.cpp

Purpose: Implements a singleton modeless dialog for executing a command on a selected server.

Important APIs/functions: `Server_Execute` opens/focuses the dialog. `Server_Execute_DlgProc` handles lifecycle. `Server_Execute_OnInitDialog` enumerates servers. `Server_Execute_EnableOK` validates selected server and command text. `Server_Execute_OnOK` sends `SVR_EXECUTE_PARAMS` to `taskSVR_EXECUTE`.

Control flow: The dialog is cached under `pcSVR_EXECUTE` with no identity key. Server combo is disabled until `taskSVR_ENUM_TO_COMBOBOX` completes. OK destroys the dialog after dispatching the task.

State and persistence: Dialog packet stores default server and command buffer. No persisted state.

Dependencies/integration: Uses server enumeration packet, prop cache, task dispatcher, and Win32 dialog controls.

Risks: No confirmation or command validation beyond nonempty text; security and quoting rules must be enforced by task/server layer. Singleton prevents multiple simultaneous command dialogs across servers.

Test signals: Default server selection, server enum failure, empty command validation, duplicate dialog focus, and task dispatch contents.
