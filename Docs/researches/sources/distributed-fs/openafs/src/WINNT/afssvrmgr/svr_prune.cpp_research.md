# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.cpp

Purpose: Implements singleton dialog for pruning `.BAK`, `.OLD`, and/or core files from a selected server.

Important APIs/functions: `Server_Prune` opens/focuses the dialog with default checkbox choices. `Server_Prune_DlgProc` handles lifecycle. `Server_Prune_OnInitDialog` sets checkboxes and starts server enumeration. `Server_Prune_EnableOK` requires a selected server and at least one prune option. `Server_Prune_OnOK` dispatches `taskSVR_PRUNE`.

Control flow: The dialog is cached under `pcSVR_PRUNE`. Server combo is disabled until `taskSVR_ENUM_TO_COMBOBOX` completes. OK dispatches the prune task and closes by fallthrough.

State and persistence: `SVR_PRUNE_PARAMS` stores target server and option booleans. No local persistence.

Dependencies/integration: Uses prop cache, server enumeration, task dispatch, and maintenance command resources.

Risks: Destructive operation is gated only by the dialog options; no additional confirmation is shown here. Task failures must be reported elsewhere. Singleton cache prevents independent prune dialogs for different servers.

Test signals: Default option combinations, no option selected disables OK, server enum failure, selected server dispatch, duplicate dialog focus, and prune-task error handling outside this file.
