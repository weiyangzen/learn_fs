# sources/distributed-fs/ceph-client/include/linux/sunrpc/cache.h

Purpose: defines the generic SUNRPC cache framework used mainly for authentication, identity, and export-related upcall caches.

Important APIs and types: `struct cache_head` supplies hash linkage, expiry, refresh time, refcount, and flags `CACHE_VALID`, `CACHE_NEGATIVE`, `CACHE_PENDING`, and `CACHE_CLEANED`. `struct cache_detail` describes cache-specific operations, hash table, flush time, request/read queues, pipefs/procfs exposure, writer accounting, and network namespace. `struct cache_req` and `struct cache_deferred_req` support delaying requests until an upcall fills an entry. APIs include lookup/update, pipe upcalls, deferred cleanup, `cache_check*()`, purge/flush, per-net create/register/destroy, pipefs registration, sequence iteration, and qword parsing helpers.

Control flow: callers look up a key, check validity, possibly send an upcall over procfs/pipefs, defer the RPC request, then update or mark negative results when user space responds. Expiry uses seconds since boot and flush-time comparisons.

State and persistence: cache entries, queues, writer counts, and timestamps are in-memory and per-cache/per-net. User-space responses can refresh state but nothing here persists across reboot.

Dependencies and integration points: depends on kref, spinlocks, wait queues, procfs, pipefs, net namespaces, and string-to-integer parsing. It supports server auth domains, Unix group caches, and other SUNRPC identity caches.

Risks and test signals: risks include refcount races, expired-but-referenced entries, no-listener stalls, deferred request leaks, boot-time versus wall-clock conversion errors, and namespace unregister ordering. Test with cache upcall daemons, writer close/reopen, negative entries, flush/purge, RCU iteration, and request deferral under load.
