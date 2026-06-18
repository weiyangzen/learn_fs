# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.h

Purpose: Defines the `SUBSET` model and exports subset filtering, UI, persistence, copy, and cleanup functions.

Important APIs/types: `SUBSET` holds subset name, dirty flag, and allocated monitored/unmonitored multistrings. Exports include `Subsets_fMonitorServer`, `Subsets_SetMonitor`, `ShowSubsetsDialog`, save/load/enumerate helpers, and memory management.

Control flow/state: A subset can represent "only these servers" via `pszMonitored`, "all except these servers" via `pszUnmonitored`, or no filter via null pointers.

Dependencies/integration: Consumed by display/dispatch code to decide monitored servers and by UI code to edit/save subsets.

Risks/test signals: All code that copies or frees subsets must preserve multistring double-null termination and use `Subsets_FreeSubset` rather than raw delete.
