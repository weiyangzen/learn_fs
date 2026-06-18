<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h

### Purpose
`PooledSocket` extends `Socket` with connection-pool bookkeeping: availability, close-on-release, and optional expiration timing.

### Important APIs, Types, And Functions
It derives from `Socket`. Methods include `isAvailable()`, `setAvailable()`, `setExpireTimeStart()`, `getHasExpirationTimer()`, `isCloseOnRelease()`, `setCloseOnRelease()`, and `getHasExpired(expireSecs)`.

### Control Flow
Connection pools mark sockets unavailable on acquire and available on release. Expiration is inactive when `expireTimeStart` is zero; otherwise elapsed time is compared with `expireSecs`.

### State, Persistence, And Dependencies
State is in-memory per pooled connection. It depends on `Socket` and `Time`.

### Integration Points
`NodeConnPool`, `LocalNodeConnPool`, `StandardSocket`, and `RDMASocket` use this as the common pooled socket base.

### Risks
No internal locking is present, so pool code must synchronize access. Expiration uses seconds converted to milliseconds and can overflow if huge values are passed. Tests should cover availability transitions, close-on-release behavior, expiration disabled/enabled, and pool synchronization around these flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h -->
