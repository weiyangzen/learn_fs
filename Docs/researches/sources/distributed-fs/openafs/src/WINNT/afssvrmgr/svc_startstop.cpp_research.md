# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.cpp

Purpose: Provides service running check and start/restart/stop workflows with permanent/temporary mode selection.

Important APIs/functions: `Services_fRunning` queries live status through `LPSERVICE::GetStatus`. `Services_Restart` directly starts `taskSVC_RESTART`. `Services_Start` and `Services_Stop` show a modal start/stop dialog, then dispatch `taskSVC_START` or `taskSVC_STOP` with temporary flag. Dialog helpers format text and capture the selected mode.

Control flow: Start/stop use a local `SERVICE_STARTSTOP_PARAMS` stack struct for modal UI, then allocate the public task packet only after OK. The dialog title and radio labels are selected based on `fStart`.

State and persistence: Temporary/permanent affects remote BOS service state via task packets. No local preferences.

Dependencies/integration: Depends on service status APIs, task dispatch, resource strings, and help IDs.

Risks: `Services_StartStop_DlgProc` keeps a static pointer that is not explicitly cleared on destroy, though the modal lifetime limits exposure. Restart bypasses confirmation and temporary mode entirely.

Test signals: Start/stop cancel, temporary vs permanent selection, service status query failure, BOS restart from property tab, and help routing for start vs stop dialog.
