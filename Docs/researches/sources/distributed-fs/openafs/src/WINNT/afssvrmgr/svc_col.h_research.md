# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.h

Purpose: Defines service list columns and declares formatting/default-view helpers.

Important APIs/types: `SERVICECOLUMN` enumerates ten service columns. `SERVICECOLUMNS` maps resource IDs to default widths. `nSERVICECOLUMNS` computes column count. Exports include `Services_SetDefaultView`, `Services_GetAlertCount`, and `Services_GetColumnText`.

Control flow/state: The enum order must match `SERVICECOLUMNS` and text buffers in `svc_col.cpp`.

Dependencies/integration: Used by FastList display code and column chooser logic.

Risks/test signals: Adding/reordering columns requires updating enum, table, and text switch together.
