# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_startstop.h

Purpose: Declares public service control packets and helper functions.

Important APIs/types: `SVC_START_PARAMS` and `SVC_STOP_PARAMS` carry service identity and temporary flag. Functions include `Services_fRunning`, `Services_Start`, `Services_Restart`, and `Services_Stop`.

Control flow/state: Start/stop allocate these packets after confirmation and hand them to tasks.

Dependencies/integration: Used by service property and context command handlers.

Risks/test signals: Ensure restart task does not need the temporary flag that start/stop expose.
