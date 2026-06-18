# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache.go

Purpose: Thread-safe in-memory bidirectional cache mapping NVMe devices to CSI staging paths.

Important APIs/types/functions: `MountCache` interface, concrete `mountCache`, `NewMountCache`, `Add`, `GetDevice`, `RemoveByDevice`, `RemoveByMountPoint`, and `GetCopyAllDevices`.

Control flow: `Add` refuses to overwrite an existing staging path or device mapping. Remove operations delete both map directions. `GetCopyAllDevices` returns a cloned device-to-path map so callers can make disconnect decisions without holding the cache lock.

State and persistence behavior: Runtime-only memory state. Node server rebuilds cache on startup from live mount information.

Dependencies and integration points: Used by node stage/unstage rollback and disconnect logic. Depends only on Go `sync` and `maps`.

Risks: The 1:1 constraint simplifies safety but may ignore legitimate cases where one device appears at multiple staging paths or aliases. `sync.Mutex` is used for read and write paths; performance is adequate for CSI operation volume but not optimized for high read concurrency.

Test signals: Dedicated tests cover add/get/remove, concurrency, non-existent removal, empty cache, and overwrite refusal.
