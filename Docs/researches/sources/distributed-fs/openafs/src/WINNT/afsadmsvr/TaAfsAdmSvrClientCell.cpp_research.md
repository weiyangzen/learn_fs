# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCell.cpp

Purpose: implements client-side wrappers for cell mutation and refresh-rate configuration.

Important APIs/types/functions: `asc_CellChange()` wraps `AfsAdmSvr_ChangeCell()` and refreshes cell properties on success. `asc_CellRefreshRateSet()` wraps `AfsAdmSvr_SetRefreshRate()`.

Control flow: both functions call server RPCs under `RpcTryExcept`, map exceptions to `RPC_S_CALL_FAILED_DNE`, and write `pStatus` on failure. `asc_CellChange()` requests all data for the cell after mutation to update local cache.

State/persistence: no local persistent state beyond cache refresh. Server-side calls can change AFS PTS cell properties or refresh-thread state.

Dependencies/integration: depends on client internal header, generated RPC calls, and `asc_ObjectPropertiesGet()` cache behavior.

Risks/test signals: cache refresh failure after a successful server mutation makes the wrapper report failure even though the cell changed. Tests should cover that partial-success behavior, RPC exceptions, invalid clients, and zero/nonzero refresh rates.
