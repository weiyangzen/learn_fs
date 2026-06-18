# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.h

Purpose: Defines server list columns and declares server view/text helper APIs.

Important APIs/types: `SERVERCOLUMN` enumerates name, address, and status. `SERVERCOLUMNS` maps columns to resource IDs and widths. Exports include default view setup and `Server_GetColumnText`.

Control flow/state: Enum/table order must remain synchronized with implementation switch logic.

Dependencies/integration: Used by server display and column chooser.

Risks/test signals: Adding columns requires updating `nSERVERCOLUMNS` consumers and text formatting.
