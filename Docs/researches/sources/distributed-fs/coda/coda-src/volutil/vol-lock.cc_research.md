## sources/distributed-fs/coda/coda-src/volutil/vol-lock.cc

Purpose: `vol-lock.cc` provides volutil RPCs to lock and unlock a volume, primarily for backup coordination.

Important APIs/types/functions: `S_VolLock` attaches a volume, checks `V_VolLock(vol).IPAddress`, obtains the write lock, stamps the lock owner, copies the volume version vector to the caller, and releases the volume attachment. `S_VolUnlock` attaches the volume, verifies a nonzero lock owner, clears it, releases the write lock, and disconnects.

Control flow: both RPCs initialize volutil, get the volume, operate on `V_VolLock`, put the volume, and disconnect. Lock failure returns `EWOULDBLOCK`; unlocking an unlocked volume returns `EINVAL`.

State and persistence behavior: mutates in-memory volume lock state and lock primitive state. It does not appear to persist lock owner to disk. The returned `ViceVersionVector` is a snapshot used by backup clients.

Dependencies/integration points: used by backup tooling before `S_VolMakeBackups`; that code verifies owner `IPAddress == 5`. Depends on volume attach/put, LWP locks, and Coda logging.

Risks: lock owner identity is a magic constant (`5`) with comments saying it needs changing; RPC caller identity is not recorded. No timeout queue is active despite comments. `S_VolUnlock` releases any nonzero owner, not specifically the caller's lock. Error paths must avoid leaving locks held.

Test signals: lock/unlock success, double lock returns `EWOULDBLOCK`, unlock unlocked returns `EINVAL`, backup sees owner `5`, failure after `ObtainWriteLock`, and concurrent callers.
