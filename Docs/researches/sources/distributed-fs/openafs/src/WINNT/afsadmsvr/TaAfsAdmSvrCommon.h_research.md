<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h

Purpose: declares common list-management APIs used by server RPC handlers and client-side support code.

Important APIs/types/functions: declarations cover `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST` create/copy/add/remove/test/free functions. Default arguments allow optional `LPARAM`, `LPASOBJPROP`, and `LPASACTION` outputs.

Control flow: included by code that needs to build RPC-returnable lists or inspect list contents. It exposes semantic operations while hiding the flexible-array reallocator.

State and persistence: no state. The implementation allocates heap-backed contiguous structures that callers must free explicitly.

Dependencies/integration: depends on admin-server public types (`ASID`, `LPASIDLIST`, `LPASOBJPROP`, `LPASACTIONLIST`) from `TaAfsAdmSvr.h`.

Risks and test signals: the prototype for `AfsAdmSvr_AddToActionList` names `pLispt`, a harmless typo but a signal that compile coverage should include this header. ABI tests should ensure C++ default arguments do not leak into C-facing RPC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.h -->
