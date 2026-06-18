<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Caps.hh

Purpose: Declares `FuseServer::Caps`, the in-memory authority for FUSE client capabilities, lease expiry, and recipient selection for metadata/dentry broadcasts.

Important APIs/types/functions: Nested `capx` wraps an `eos::fusex::cap` protobuf plus the issuing `VirtualIdentity`. Type aliases define auth IDs, client IDs, UUID maps, inode-to-auth sets, and client-to-inode views. Public methods include `Store()`, `Imply()`, `Remove()/RemoveTS()`, `Delete()`, `Get()/GetTS()/GetRaw()`, broadcast methods, `Print()`, `Dump()`, and query helpers such as `HasInodeId()` and `GetInodeCapAuthIds()`.

Control flow: The class uses a single `std::mutex mtx` to protect all maps. Thread-safe wrappers (`GetTS`, `RemoveTS`) acquire the mutex; lower-level methods assume the caller already holds the lock. `expire()` checks the oldest time-ordered entry and removes it when its cap lease has expired; otherwise it signals whether stale time entries should be popped. `dropCaps()` gathers matching caps for a UUID, removes them, then clears client-id views for that UUID.

State and persistence behavior: All capability state is volatile. The primary map is `authid -> shared_cap`; secondary views are maintained for client and inode operations. `mTimeOrderedCap` is a multimap of lease time to auth id used by periodic expiry. Client UUID to client-id tracking supports multi-mount cleanup.

Dependencies and integration points: Includes `mgm/fusex.pb.h`, `common/Mapping.hh`, `common/Timing.hh`, logging, and `common/RWMutex.hh`. It is owned by `FuseServer`, called by the FUSE server command processor, heartbeat client monitor, and external MGM operations that need to invalidate eosxd caches.

Risks: Correctness depends on every mutation keeping all secondary indexes synchronized. Some accessors expose non-const references to internal maps, which can bypass locking and invariants. `Remove()` assumes the cap is present in all secondary maps and uses `operator[]`, potentially creating empty entries during cleanup. `Get()` returns a default empty cap by default, so callers must check `id()` to distinguish misses. Test signals should validate invariant preservation across store, imply, remove, delete, drop-by-UUID, and expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.hh -->
