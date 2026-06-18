<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp

Purpose: implements object search helpers for admin-server RPC handlers, including regex-style name filtering, optional refresh before search, scoped enumeration, exact lookup, and advanced user-expiration filtering.

Important APIs/types/functions: `AfsAdmSvr_Search_Compare()` caches the last `REGEXP` and supports leading `!` negation. `AfsAdmSvr_SearchRefresh()` refreshes a cell or server depending on requested object type. `AfsAdmSvr_Search_*InCell`, `*InServer`, and `VolumesInPartition` build `ASIDLIST` results. `AfsAdmSvr_Search_*InCell/Server/Partition` exact functions resolve one object id. `AfsAdmSvr_Search_OneUser()` and `OneGroup()` search cell-scoped principals. `AfsAdmSvr_Search_Advanced()` filters a list by account-expiration or password-expiration thresholds.

Control flow: search handlers optionally refresh the scope, enumerate AfsClass objects or global `IDENT` registry, apply name matching, append ASIDs, and then advanced filtering may remove list entries in place. Exact searches open typed children directly where possible, or scan cached identifiers when no direct open helper exists.

State and persistence: the regex compare function keeps static last-pattern state and compiled expression. Search results are heap `ASIDLIST`s; object/property data comes from the in-memory AfsClass cache.

Dependencies/integration: depends on `REGEXP`, AfsClass enumeration APIs, `IDENT::FindFirst/Next`, list helpers, property helpers, Windows time conversion, and `ASOBJPROP` user/group metadata.

Risks and test signals: the static regex cache is not synchronized, so concurrent searches with different patterns can race. Several exact-search loops return `FALSE` immediately on a zero-refcount object without closing enumeration, which risks iterator cleanup. Advanced password expiration uses 100ns arithmetic and must handle invalid times. Tests should cover empty and negated patterns, all object scopes, refresh modes, exact lookup misses, advanced expiration filters, and concurrent pattern searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.cpp -->
