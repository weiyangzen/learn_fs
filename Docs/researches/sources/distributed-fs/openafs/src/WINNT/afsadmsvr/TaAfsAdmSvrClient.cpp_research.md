# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.cpp

Purpose: implements the main client-side `asc_*` library wrappers for the admin-server RPC interface plus list allocation/free helpers and callback dispatch.

Important APIs/types/functions: `MIDL_user_allocate/free` bridge RPC allocation to OpenAFS `Allocate/Free`. `asc_AsidList*`, `asc_ObjPropList*`, and `asc_ActionList*` wrap common list helpers. `asc_AdminServerOpen/Close` manage sockets, binding, ping and callback threads. Credential, cell, object, action, notification, and random-key wrappers call corresponding `AfsAdmSvr_*` RPCs inside `RpcTryExcept`. Fast object getters read the local cache only. `AfsAdmSvrCallback_Action()` maps server callbacks to local notification listeners.

Control flow: opening initializes Winsock once, binds to an existing server or starts one when local and unavailable, starts ping and callback helper threads, and increments a request count. Cell open creates a local cache and fetches rudimentary cell properties. Object-property getters refresh server data only if local versions are stale, then copy cached properties. Refresh calls invalidate server cache and trigger listener requery. All RPC failures are normalized to `RPC_S_CALL_FAILED_DNE`.

State/persistence: static `l` tracks socket initialization and admin-server open reference count. Client-side caches and listeners live in other modules. No disk persistence, but calls can mutate remote AFS state.

Dependencies/integration: depends on generated RPC stubs, binding/cache/notify/ping internal headers, OpenAFS common list helpers, Windows RPC exception macros, Winsock, and AFS app allocation functions.

Risks/test signals: reference counting is not protected by `asc_Enter()` in open/close, and fixed `STRING` copies can overflow if callers provide long values. A TODO notes passwords are sent without encryption. Tests should cover bind failure and auto-fork paths, repeated open/close, ping/callback thread lifecycle, cache creation failure rollback, RPC exception handling, fast getters with missing/deleted properties, and listener notification delivery.
