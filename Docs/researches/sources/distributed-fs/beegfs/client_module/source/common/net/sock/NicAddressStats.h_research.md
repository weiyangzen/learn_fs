# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStats.h

Purpose: Tracks per-NIC connection availability, recency, last error, validity, and RDMA NUMA priority for BeeGFS connection selection.

Important APIs/types/functions: `NicAddressStats_init`, `invalidate`, `setValid`, `comparePriority`, `updateUsed`, `updateLastError`, `lastErrorExpired`, and `usable` operate on `NicAddressStats` fields `established`, `available`, `used`, `lastError`, and `nicValid`.

Control flow: Priority comparison prefers RDMA devices on the requested NUMA node, then more available connections, fewer established connections, and least-recently used NICs. Usability rejects RDMA stats without an `ibdev` and otherwise allows available slots or room below `maxConns`.

State and persistence behavior: Process-local mutable counters/timestamps; invalidation clears RDMA device pointers and validity.

Dependencies and integration points: Used by node connection pools, RDMA socket stats, `Time`, and optional kernel RDMA NUMA helpers.

Risks: Comments require owner `NodeConnPool` mutex for most access; unsynchronized mutation can mis-rank or race connection accounting. Error expiry uses elapsed wall time.

Test signals: NUMA preference, availability/established ordering, LRU ordering, invalid/offline NIC behavior, and error-expiration windows.
