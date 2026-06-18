# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_execute.h

Purpose: Declares remote execute packet and UI entry point.

Important APIs/types: `SVR_EXECUTE_PARAMS` carries server identity and command path/string. `Server_Execute(LPIDENT)` opens the command dialog.

Control flow/state: Dialog fills packet and dispatches `taskSVR_EXECUTE`.

Dependencies/integration: Used by server context command routing.

Risks/test signals: `szCommand` is limited to `MAX_PATH`, which may be too short for complex command lines.
