## sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.hh

Purpose: declares the query-prepare result object. It packages completion status, response payload, and XRootD return code.

Important APIs: public constructor, `hasQueryPrepareFinished()`, `getResponse()`, and `getReturnCode()`. Private `setQueryPrepareFinished()` and `setReturnCode()` are accessible to `PrepareManager` via friendship.

Integration: returned to `XrdMgmOfs` query handling, then serialized using `QueryPrepareResponseJson`. Risks include friend-only mutation and uninitialized return code if a caller constructs directly. Tests should validate lifecycle through `PrepareManager::queryPrepare()`.
