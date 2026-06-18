# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.h

Purpose: Declares service property task packets and UI entry point.

Important APIs/types: `SVC_PROP_APPLY_PACKET` carries target service and warn-stop setting. `SVC_RESTARTTIMES_PARAMS` carries BOS general/new-binary restart flags and schedules. `Services_ShowProperties` opens the property sheet.

Control flow/state: Packets are allocated by tabs and consumed by task handlers.

Dependencies/integration: Used by service command routing and task implementation.

Risks/test signals: Ensure `SYSTEMTIME.wDayOfWeek == (WORD)-1` daily convention is honored by BOS restart task code.
