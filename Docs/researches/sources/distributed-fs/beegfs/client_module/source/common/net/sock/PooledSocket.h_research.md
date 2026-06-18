# sources/distributed-fs/beegfs/client_module/source/common/net/sock/PooledSocket.h

Purpose: Extends the abstract `Socket` with pool membership, availability, activity, expiration timer, and NIC type metadata.

Important APIs/types/functions: `_PooledSocket_init`, `_PooledSocket_uninit`, `PooledSocket_getHasExpired`, availability/activity getters and setters, expiration timer helpers, `PooledSocket_getNicType`, `getPool`, `getPoolElem`, and `setPool` manage `PooledSocket` state.

Control flow: Socket implementations embed `PooledSocket`; connection pools toggle availability and activity, set expiration start times, and link sockets into `ConnectionList` nodes. Expiration is checked from `Time_elapsedSinceMS`.

State and persistence behavior: In-memory only. The socket records its containing pool and list element, so list operations and socket teardown must stay coordinated.

Dependencies and integration points: Used by `StandardSocket`, `RDMASocket`, connection lists, and node connection pools.

Risks: Incorrect pool/element bookkeeping can leave dangling list references. Expiration starts only when explicitly set, so callers must manage idle lifecycle consistently.

Test signals: Pool insert/remove, availability transitions, activity reset, expiration timer behavior, and virtual destruction through embedded `Socket`.
