# sources/distributed-fs/ceph-client/security/selinux/avc.c

## Purpose
`avc.c` implements SELinux's Access Vector Cache (AVC), the hot-path cache for policy decisions keyed by source SID, target SID, and target class. It avoids repeated security-server lookups, supports extended permissions such as ioctl command sets, audits grants/denials according to policy, and flushes or updates cached decisions when policy changes.

## Important APIs, Types, and Data
Core structures:

- `struct avc_entry`: cache payload: source SID, target SID, class, `struct av_decision`, and optional extended-permission node.
- `struct avc_node`: RCU-protected hlist node wrapping an `avc_entry`.
- `struct avc_xperms_node`: extended permission metadata plus a list of decisions.
- `struct avc_xperms_decision_node`: one extended permission decision, including allowed/auditallow/dontaudit bitmaps.
- `struct avc_cache`: hash slots, per-slot spinlocks for writers, LRU hint, active node count, and latest policy notification sequence.
- `struct selinux_avc`: top-level cache threshold plus `avc_cache`.

Public or externally used functions:

- `selinux_avc_init()`: initializes slots, locks, threshold, and counters.
- `avc_get_cache_threshold()` / `avc_set_cache_threshold()`: expose runtime cache threshold control.
- `avc_init()`: creates slab caches for AVC nodes and extended permission structures.
- `avc_get_hash_stats()`: formats cache occupancy and chain-length stats.
- `avc_add_callback()`: registers policy-change callbacks during init.
- `avc_ss_reset()`: flushes cache, runs reset callbacks, and records latest policy sequence.
- `avc_has_perm_noaudit()`: checks ordinary permissions without audit.
- `avc_has_perm()`: checks ordinary permissions and performs policy-directed audit.
- `avc_has_extended_perms()`: checks base access plus extended permission bitmaps.
- `avc_policy_seqno()`: returns latest policy sequence notification.

## Control Flow
Ordinary permission checking:

1. `avc_has_perm()` calls `avc_has_perm_noaudit()`.
2. `avc_has_perm_noaudit()` looks up `(ssid, tsid, tclass)` under RCU.
3. On hit, it copies `av_decision`, computes denied bits, drops RCU, and calls `avc_denied()` if needed.
4. On miss, it drops RCU and calls `avc_perm_nonode()`, which computes a decision through `security_compute_av()`, inserts it with `avc_insert()`, and evaluates denied bits.
5. `avc_has_perm()` then calls `avc_audit()` to emit audit records when policy says auditallow or auditdeny applies.

Extended permission checking:

1. `avc_has_extended_perms()` looks up or computes the base decision and associated `extended_perms`.
2. If no extended permissions apply, it falls back to the base decision.
3. If a requested driver/base permission decision is absent but the driver and base are known, it computes the extended decision via `security_compute_xperms_decision()`.
4. The computed extended decision is added to the cache with `avc_update_node(AVC_CALLBACK_ADD_XPERMS, ...)`.
5. The requested xperm bit is checked against allowed/dontaudit/auditallow bitmaps before denial and audit.

Cache mutation:

- `avc_insert()` rejects stale decisions with `avc_latest_notif_update()`, allocates a node, deep-copies extended permissions, then inserts or replaces under the per-bucket spinlock.
- `avc_update_node()` allocates a replacement node, finds an existing node with matching seqno, copies the old decision, mutates grant/revoke/audit bits or extended permissions, and replaces the old node with RCU.
- `avc_flush()` walks every bucket under locks and deletes nodes with RCU callbacks.
- `avc_reclaim_node()` scans buckets using `lru_hint` and trylocks, reclaiming up to `AVC_CACHE_RECLAIM` nodes when the active count exceeds the threshold.

Audit flow:

- `avc_xperms_audit_required()` combines requested, allowed, auditallow, auditdeny, dontaudit, result, and extended permission information to decide whether to audit.
- `slow_avc_audit()` builds `selinux_audit_data`, then calls generic `common_lsm_audit()` with SELinux pre/post callbacks.
- Pre-callback prints permission names from `secclass_map`; post-callback translates SIDs to contexts, emits class and permissive status, traces `selinux_audited`, and includes raw invalid contexts when available.

## State and Persistence Behavior
The AVC is a volatile in-kernel cache. It persists only until cache reclaim, policy reset, or system shutdown. Policy sequence numbers prevent old decisions from being inserted after a newer revocation notification. Cache nodes are RCU-freed to allow lockless readers. Extended permission payloads are separately slab-allocated and deep-copied because they can be chained and selectively added after a base AVC entry exists.

The cache threshold defaults to the number of hash slots, `1 << CONFIG_SECURITY_SELINUX_AVC_HASH_BITS`, and can be changed at runtime by SELinux filesystem control paths. When `CONFIG_SECURITY_SELINUX_AVC_STATS` is enabled, per-CPU counters record lookups, misses, allocations, frees, and reclaims.

## Dependencies and Integration Points
`avc.c` depends on SELinux security-server APIs such as `security_compute_av()`, `security_compute_xperms_decision()`, SID-to-context translation, enforcing/permissive state, class/permission maps, and xperm bit helpers. It integrates with generic LSM audit via `common_lsm_audit()`, Linux audit buffers, tracepoints in `trace/events/avc.h`, RCU, hlist, spinlocks, slab caches, and selinuxfs status/stat display paths.

## Risks and Edge Cases
- RCU readers and per-bucket writers require strict copy-replace discipline; in-place mutation of visible nodes would race readers.
- `avc_update_node()` requires a matching decision seqno, so stale update notifications fail with `-ENOENT`.
- Extended permission allocation uses `GFP_NOWAIT`; memory pressure can skip caching or fail xperm update paths.
- `avc_denied()` grants denied permissions into the cache in permissive mode unless `AVC_STRICT` is set, which is intentional but must not leak into enforcing decisions after policy changes.
- Class index use in audit callbacks assumes valid nonzero `tclass`; `slow_avc_audit()` warns and returns `-EINVAL` for invalid classes.
- Reclaim is approximate and trylock-based, so active node count can remain above threshold transiently.

## Test Signals
Validation should cover cache hits and misses, policy reload flushing, revocation sequence ordering, permissive vs enforcing denial results, `AVC_STRICT`, extended ioctl-style permissions, auditallow/auditdeny/dontaudit combinations, selinuxfs cache stats/hash stats, tracepoint emission, and fault injection for slab allocation failures. Concurrency tests should stress RCU readers while policy reloads, grants/revokes, and threshold-driven reclaim occur.
