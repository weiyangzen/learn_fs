<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.h -->
## sources/distributed-fs/ceph/src/mds/flock.h

`flock.h` declares the MDS file-lock state container and ordering helpers around `ceph_filelock`. It defines owner equality and ordering semantics that preserve compatibility with old clients: modern owners are identified by `client` plus high-bit-set `owner`, while old clients also require `pid`.

The public API exposes waiter inspection/removal, lock acquisition, conflict lookup, range unlock, client-wide cleanup, Ceph encoding/decoding, formatter dumping, and generated test instances. `held_locks` and `waiting_locks` are both multimaps keyed by starting offset; client count maps are maintained for fast empty/client cleanup checks. Private helpers cover recursive deadlock detection, waiter insertion, range normalization, lower-bound lookup, overlap discovery, self-neighbor coalescing, owner partitioning, and exclusive-lock discovery.

State behavior is explicitly mixed durable/runtime. The header exposes all four maps, but the implementation persists only held locks and held counts. `type` and `cct` are constructor/runtime values, and waiting state is a transient scheduling aid. The API also returns activated locks from `remove_lock`, although this implementation currently only mutates held state and leaves activation policy to higher layers.

Dependencies are lightweight but important: `ceph_filelock` from `include/ceph_fs.h`, `client_t`, Ceph buffer/formatter forward declarations through used signatures, and standard maps/lists. Integration points are MDS locker code, session reconnect (`cap_reconnect_t` carries flock blobs), and journal/recovery code that expects durable state to round-trip.

Risks: external code can mutate public maps without preserving counts, comparator behavior affects multimap lookup and global wait graph keys, and old/new client owner compatibility must remain stable. Test signals should focus on comparator ordering, old-client pid semantics, public encode/decode compatibility, empty-state behavior, and acquisition/removal paths through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/flock.h -->
