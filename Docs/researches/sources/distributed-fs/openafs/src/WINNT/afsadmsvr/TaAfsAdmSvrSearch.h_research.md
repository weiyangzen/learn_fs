<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h

Purpose: declares the admin-server search helper surface used by object-find RPC handlers.

Important APIs/types/functions: prototypes cover refresh, multi-result searches by cell/server/partition and object type, exact lookup by scope/name, principal-only lookup, and advanced list filtering.

Control flow: object RPC code can compose these helpers to implement `ObjectFind` and `ObjectFindMultiple` without exposing enumeration internals.

State and persistence: no header state. Implementation maintains only the regex cache and returns heap `ASIDLIST`s.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` for `ASID`, `ASOBJTYPE`, `AFSADMSVR_SEARCH_REFRESH`, and `AFSADMSVR_SEARCH_PARAMS`.

Risks and test signals: many functions accept output pointers and optional status pointers; integration tests should check null/missing outputs and error code propagation from failed AfsClass opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrSearch.h -->
