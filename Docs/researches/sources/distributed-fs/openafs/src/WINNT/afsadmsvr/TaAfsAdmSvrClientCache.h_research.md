# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientCache.h

Purpose: internal header for client-side admin-server object cache operations.

Important APIs/types/functions: declares cache lifecycle (`CreateCellCache`, `DestroyCellCache`), lookup (`GetCachedProperties`), and single/multiple `RefreshCachedProperties()` overloads.

Control flow: higher-level client wrappers use these functions during cell open/close and property retrieval.

State/persistence: no header state; implementation keeps process-global in-memory cache.

Dependencies/integration: requires IDL types such as `ASID`, `LPASOBJPROP`, `LPASIDLIST`, and `AFSADMSVR_GET_LEVEL`.

Risks/test signals: callers must not free or persist `GetCachedProperties()` pointers. Compile tests should verify overloads are only consumed from C++.
