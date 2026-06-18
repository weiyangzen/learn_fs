# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.h

Purpose: Declares server property task packets and UI entry point.

Important APIs/types: `SVR_SETAUTH_PARAMS` carries server identity and auth-enable flag. `SVR_SCOUT_APPLY_PACKET` carries warning toggles, warning percentages, and auto-refresh settings. `Server_ShowProperties` opens the property sheet.

Control flow/state: Packets are filled by property tabs and consumed by async tasks.

Dependencies/integration: Used by server property implementation and task dispatcher.

Risks/test signals: Confirm `WORD` percentage fields and `size_t` minute field map correctly to stored preference types.
