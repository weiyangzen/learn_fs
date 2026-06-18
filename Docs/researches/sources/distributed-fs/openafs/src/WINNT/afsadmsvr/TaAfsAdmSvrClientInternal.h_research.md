# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientInternal.h

Purpose: umbrella internal header for the admin-server client library implementation.

Important APIs/types/functions: includes the public client API plus binding, cache, notification, and ping internal headers.

Control flow: implementation `.cpp` files include this to get all client-library internals and shared type declarations.

State/persistence: no state in the header. Included modules manage binding handles, caches, listeners, ping threads, and callback threads.

Dependencies/integration: depends on `TaAfsAdmSvrClient.h`, `TaAfsAdmSvrClientBind.h`, `TaAfsAdmSvrClientCache.h`, `TaAfsAdmSvrClientNotify.h`, and `TaAfsAdmSvrClientPing.h`.

Risks/test signals: broad inclusion can hide dependency cycles and increase rebuild blast radius. Compile tests should ensure all included headers remain self-consistent and no public/internal macro conflict appears.
