<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/hash.c research

Purpose: implements allocation, initialization, destruction, and lockdep class assignment for batman-adv's small generic hlist hashtable wrapper.

Important APIs and functions: `batadv_hash_new()` allocates the wrapper, bucket array, and per-bucket spinlock array with `GFP_ATOMIC`; `batadv_hash_destroy()` frees those allocations; `batadv_hash_set_lock_class()` assigns one lockdep class to all bucket locks in a table. Static `batadv_hash_init()` initializes each hlist and spinlock and resets the generation counter.

Control flow: allocation is staged so failures free earlier allocations. New hashes are returned empty with `size` set and `generation` zero. Destruction intentionally frees only the table structure and lock arrays; callers must purge contained entries before destroying. Lock class assignment is used by BLA when claim and backbone tables can be locked in nested contexts.

State and persistence: no global state. Each allocated `struct batadv_hashtable` owns arrays and a generation counter. Contents are managed by callers through inline add/remove helpers in `hash.h`.

Dependencies and integration: used by BLA claim/backbone tables, DAT cache, originator/translation-table style modules, and netlink dump consistency via `generation`. Depends on kernel hlist, spinlock, lockdep, and slab allocation.

Risks: `batadv_hash_destroy()` does not walk buckets, so failing to purge entries leaks caller-owned objects and may leave RCU callbacks unscheduled. `GFP_ATOMIC` allocation can fail under pressure. Size zero is not guarded here and would break choose callbacks via modulo, so callers must request positive sizes.

Test signals: allocation failure injection, destroy after caller purge, nested lockdep paths using `batadv_hash_set_lock_class()`, generation changes through add/remove, and users with large bucket counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/hash.c -->
