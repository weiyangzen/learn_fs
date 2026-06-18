# sources/distributed-fs/lizardfs/src/common/connection_pool.cc

Purpose: implements a thread-safe connection reuse pool keyed by `NetworkAddress`.

Important APIs/types/functions: `ConnectionPool::putConnection` stores a file descriptor with timeout; `getConnection` returns a valid descriptor or `-1`; `cleanup` removes timed-out connections and closes their descriptors.

Control flow: `getConnection` loops while stale descriptors are found. It locks, pops the oldest connection for an address, unlocks, then either returns the descriptor if still valid or closes it and retries. `cleanup` walks all address lists under lock, records stale fds, erases empty map entries, unlocks, and closes descriptors outside the mutex.

State and persistence: state is in-memory `std::map<NetworkAddress, std::list<Connection>>` guarded by `mutex_`. There is no persistence; fd ownership transfers to the pool on `putConnection` and back to the caller on successful `getConnection`.

Dependencies and integration: depends on `connection_pool.h`, `massert` assertions, and `tcpclose` from sockets. It integrates with network clients that want short-lived TCP connection reuse.

Risks: `putConnection` asserts `fd > 0`, excluding descriptor `0`; normal sockets usually satisfy this but the API is stricter than POSIX fd validity. `getConnection` leaves empty address entries in the map until `cleanup`. No maximum pool size is enforced, so repeated puts can accumulate until timeouts.

Test signals: no direct unittest in this subset. Behavior is mostly validated indirectly by networking users and would benefit from fake-clock/fake-close tests for timeout and concurrency paths.
