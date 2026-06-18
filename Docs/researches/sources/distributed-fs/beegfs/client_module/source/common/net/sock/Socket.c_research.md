# sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.c

Purpose: Implements the small base layer for the abstract BeeGFS kernel socket interface.

Important APIs/types/functions: `_Socket_init`, `_Socket_uninit`, `Socket_bind`, and `Socket_bindToAddr` initialize base fields and delegate binding to virtual operations.

Control flow: `Socket_bind` binds to `in6addr_any` on the requested port; `Socket_bindToAddr` dispatches through `this->ops->bindToAddr`. Concrete implementations provide connect/listen/shutdown/send/recv behavior.

State and persistence behavior: Base initialization resets peer/bound fields and poll/list bookkeeping; no persistence.

Dependencies and integration points: Used by `StandardSocket`, `RDMASocket`, pooled sockets, and client network code that consumes the `SocketOps` vtable.

Risks: The base type assumes `ops` is valid before virtual calls. Incorrect embedding or initialization order can dereference null operations.

Test signals: Construct concrete sockets, verify bind delegation and base field initialization through standard/RDMA wrappers.
