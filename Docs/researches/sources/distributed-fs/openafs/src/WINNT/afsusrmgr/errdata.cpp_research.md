## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.cpp

Purpose: aggregates per-object operation failures and presents a single final error dialog.

Important APIs/types/functions: implements `ED_Create`, `ED_Free`, `ED_RegisterStatus`, `ED_GetFinalStatus`, and `ED_ShowErrorDialog`. The visible snippet shows freeing, registering failed ASIDs and status, and choosing single vs multiple error messages.

Control flow: callers create an `ERRORDATA` with message IDs, register each operation result, and finally show the aggregated dialog. `ED_RegisterStatus` ignores successes, increments failure count on failures, stores the last status, and appends the failed object ASID to an internal list.

State and persistence behavior: state is in the heap `ERRORDATA` object and its `LPASIDLIST`; there is no persisted state. `ED_GetFinalStatus` returns the aggregate status for caller decisions.

Dependencies and integration points: uses `asc_AsidListCreate/AddEntry/Free`, `CreateNameList`, localized error strings, and `ErrorDialog`. It is intended for batch operations such as multi-delete/change tasks.

Risks: only the last failure status is retained, so mixed failure causes can be collapsed. Dialog text depends on being able to resolve ASID names after an operation, which can fail after deletes or cache invalidation.

Test signals: register zero failures, one failure, and multiple failures; verify status return, name-list formatting, and object list cleanup.
