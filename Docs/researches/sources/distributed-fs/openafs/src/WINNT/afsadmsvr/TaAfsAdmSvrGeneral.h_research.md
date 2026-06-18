<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h

Purpose: declares the core internal admin-server lifecycle, synchronization, client, action, and utility APIs.

Important APIs/types/functions: exposes lock helpers, startup/shutdown, auto-shutdown, operation begin/end/query helpers, client attach/detach/ping helpers, common Boolean/null return wrappers, `GetAsidType()`, `AfsAdmSvr_ResolveName()`, auto-open/min-scope functions, callback manager declaration, and `AfsAdmSvr_GetCurrentTime()`.

Control flow: server RPC implementation files include this header to validate clients, bracket operations, update action callbacks, and share common error-return idioms.

State and persistence: no state is exposed. State is implementation-private static memory in `TaAfsAdmSvrGeneral.cpp`.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` and is part of `TaAfsAdmSvrInternal.h`.

Risks and test signals: the helper wrappers combine status propagation with operation completion, so misuse can double-end or leak an operation. Tests should verify each RPC handler path pairs begin/end exactly once and that default `iOp = (size_t)-2` leaves operations untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGeneral.h -->
