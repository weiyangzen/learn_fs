## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/errdata.h

Purpose: declares the operation-error aggregation structure and API.

Important APIs/types/functions: `ERRORDATA` stores `cFailures`, `pAsidList`, `status`, and resource IDs for single and multiple error text. Public functions create, free, register per-object status, fetch final status, and show the dialog.

Control flow: batch task code can accumulate results independently of UI presentation, then show one summary.

State and persistence behavior: heap-owned transient state; no registry or global persistence.

Dependencies and integration points: depends on `LPASIDLIST`, `ASID`, and `ULONG` status conventions used by the OpenAFS admin client.

Risks: callers must call `ED_Free` exactly once and must not retain `pAsidList` entries after freeing. Message IDs must match format expectations used by `ED_ShowErrorDialog`.

Test signals: validate allocation/free with no registered failures and with failed ASIDs; check leak tooling around early returns in batch operations.
