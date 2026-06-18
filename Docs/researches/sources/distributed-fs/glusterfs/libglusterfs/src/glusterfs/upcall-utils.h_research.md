# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/upcall-utils.h

Purpose: `upcall-utils.h` defines shared event and payload structures for server-to-client upcalls such as cache invalidation, lease recall, and lock contention notifications.

Important APIs and types: flag macros describe invalidated attributes/xattrs/dentries and fop-specific bundles such as `UP_WRITE_FLAGS`, `UP_ATTR_FLAGS`, and `UP_NLINK_FLAGS`. `gf_upcall_event_t` enumerates cache invalidation, recall lease, inode lock contention, and entry lock contention. `gf_upcall` carries client UID, GFID, event type, and event data. Specific payload structs carry iatt snapshots, parent stats, xattr dicts, lease type/tid, lock flock/pid/domain, and contention entry names.

Control flow and state: no logic. Producers allocate/populate payloads and consumers interpret based on `event_type` and flags.

Dependencies and integration: depends on iatt, UUID, compat, dict, and lock types. Translators and protocol layers use it to invalidate client caches and coordinate leases/locks.

Risks: flag combinations must be precise or clients may keep stale metadata. Dict and string pointers require clear ownership/lifetime across async delivery. Event type is `uint32_t` in `gf_upcall`, so enum mismatches must be avoided.

Test signals: cache invalidation tests for each fop class, lease recall delivery, lock contention payloads, xattr add/remove flags, parent stat invalidation on rename/unlink/mkdir/create, and serialization/deserialization compatibility are key.
