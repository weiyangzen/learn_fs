# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.h

Purpose: Declares get-dates task packet and dialog entry point.

Important APIs/types: `SVR_GETDATES_PARAMS` carries server identity and filename. `Server_GetDates(LPIDENT)` starts the workflow.

Control flow/state: Packet is passed from input dialog to results dialog and task.

Dependencies/integration: Used by server command menus for file maintenance.

Risks/test signals: `szFilename` uses `MAX_PATH`; remote server paths longer than that cannot be expressed.
