# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCell.cpp

Purpose: implements server-side RPC operations for cell-level administration.

Important APIs/types/functions: `AfsAdmSvr_ChangeCell()` changes PTS cell properties from `AFSADMSVR_CHANGECELL_PARAMS`; `AfsAdmSvr_SetRefreshRate()` starts/stops or adjusts the periodic refresh thread for a cell.

Control flow: `ChangeCell` creates an `ACTION_CELL_CHANGE`, begins an operation, validates client, maps IDL parameters to `PTSPROPERTIES`, calls `AfsClass_SetPtsProperties()`, then refreshes/tests cached properties for the cell. `SetRefreshRate` validates client and calls `AfsAdmSvr_StopCellRefreshThread()` when rate is zero or `AfsAdmSvr_SetCellRefreshRate()` otherwise.

State/persistence: mutates the AFS cell's PTS properties through AFS class APIs and server refresh-thread state. No local file persistence.

Dependencies/integration: depends on `TaAfsAdmSvrInternal.h`, AfsClass PTS APIs, operation/action tracking, and cell refresh helpers.

Risks/test signals: property changes must be reflected in cache and notifications after success. Tests should cover invalid clients, invalid cell IDs, AFS class failures, action lifecycle, zero/nonzero refresh rates, and cache update after mutation.
