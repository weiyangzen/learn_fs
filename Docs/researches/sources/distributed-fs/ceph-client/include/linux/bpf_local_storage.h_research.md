# sources/distributed-fs/ceph-client/include/linux/bpf_local_storage.h

Purpose: Defines the generic object-local BPF storage infrastructure used by socket, task, inode, cgroup-related, or other local-storage maps. It lets BPF maps define storage value size while the target object owns the per-object mini-map/list of storage elements.

Important APIs/types/functions: `struct bpf_local_storage_map` embeds `struct bpf_map`, has per-bucket hash/list locks, element size, and cache index. `struct bpf_local_storage_elem` links one storage value into both the map bucket and owning object's `struct bpf_local_storage`; atomic state bits track map unlink, storage unlink, and deferred free. `struct bpf_local_storage` has a small RCU cache, element list, owner pointer, RCU head, raw/q spinlock, mem charge, and owner refcount. `bpf_local_storage_lookup()` performs an RCU cache lookup first, then scans the per-object list and optionally refreshes the cache. Allocation/update/free APIs manage map validation, element allocation/linking/unlinking, object storage allocation, BTF checks, and memory usage.

Control flow: Map creation validates attributes and allocates buckets/cache index. On update, storage elements are allocated, linked to the owner storage and map bucket, and charged to the owner. Lookup from BPF or syscall uses the owner storage and map pointer as key. Object teardown calls `bpf_local_storage_destroy()`; map teardown unlinks all elements.

State/persistence: Storage values persist for the lifetime of the owner object or map, whichever unlinks first. RCU protects lookups; bucket locks and object locks protect mutations. The cache is an optimization and can be stale until RCU-safe replacement.

Dependencies/integration: Depends on core BPF map definitions, filter/BTF support, RCU hlist, hash/list primitives, BPF memory allocator, and raw/q spinlocks. Integrates with concrete map ops through `map_local_storage_charge`, `map_local_storage_uncharge`, and `map_owner_storage_ptr`.

Risks/test signals: Risks include dual-owner unlink races, stale cache entries, mem-charge imbalance, owner refcount misuse, lock ordering between map buckets and object storage, and BTF value-size mistakes. Test signals include local storage selftests for sockets/tasks/inodes, concurrent update/delete/lookup, owner teardown under active lookup, map destruction with live owners, KCSAN/lockdep, and memory accounting assertions.
