<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp

Purpose: manages cached `ASOBJPROP` data for cells, servers, services, partitions, volumes, users, and groups, and runs optional per-cell auto-refresh threads.

Important APIs/types/functions: `REFRESHTHREAD` tracks cell id, last refresh time, refresh rate, and handle. `AfsAdmSvr_SetCellRefreshRate()`, `StopCellRefreshThread()`, and `MarkRefreshThread()` manage refresh entries. `AfsAdmSvr_ObtainRudimentaryProperties()` maps an `IDENT` to common type/name/parent fields. `AfsAdmSvr_ObtainFullProperties()` opens the typed AfsClass object and fills status-specific union fields. `AfsAdmSvr_TestProperties()` refreshes cached properties and bumps `verProperties` on changes. `AfsAdmSvr_NotifyCallback()` reacts to AfsClass create/destroy/refresh events. `GetCurrentProperties()` and `InvalidateObjectProperties()` are typed access helpers.

Control flow: AfsClass notify create initializes an `ASOBJPROP` and stores it in `IDENT::SetUserParam()`. Refresh-end and mutation paths call `AfsAdmSvr_TestProperties()` to detect changes. Auto-refresh threads wake every minute, invalidate a cell, and run `RefreshAll()` when the configured interval has elapsed.

State and persistence: file-local static refresh-thread array and critical section. Object properties are stored as heap pointers in each `IDENT` user parameter. No durable persistence; the cache is rebuilt from AfsClass/admin calls.

Dependencies/integration: heavily integrated with AfsClass `CELL`, `SERVER`, `SERVICE`, `AGGREGATE`, `FILESET`, `USER`, and `PTSGROUP` objects, admin property structs, action refresh tracking, logging, and `GetAsidType()`.

Risks and test signals: refresh-thread entries are stopped by zeroing `idCell`; thread handles are not joined or closed. Full property collection copies sensitive user key material into `ASOBJPROP`. `AfsAdmSvr_GetCurrentProperties()` assumes `GetUserParam()` already exists after opening an object. Tests should cover each object type, missing objects setting `verPROP_NO_OBJECT`, version increment on property change, destroy of cell stopping refresh, and auto-refresh interval behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.cpp -->
