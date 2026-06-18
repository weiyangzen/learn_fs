# sources/distributed-fs/ceph-client/net/ipv4/tcp_sigpool.c

## Purpose

`tcp_sigpool.c` provides a small shared pool of asynchronous hash transforms and per-CPU scratch buffers for TCP signing users such as TCP authentication mechanisms. It avoids each user permanently owning a full set of crypto resources while still allowing atomic/BH-safe hash request setup around packet processing.

## Important APIs, Types, and Functions

Exported APIs are `tcp_sigpool_alloc_ahash()`, `tcp_sigpool_release()`, `tcp_sigpool_get()`, `tcp_sigpool_start()`, `tcp_sigpool_end()`, `tcp_sigpool_algo()`, and `tcp_sigpool_hash_skb_data()`. `struct sigpool_entry` stores a base `crypto_ahash`, algorithm name, `kref`, and flags. `struct sigpool_scratch` is per-CPU and contains a `local_lock_t` plus an RCU-protected scratch pointer. `struct scratches_to_free` batches old scratch buffers for deferred RCU freeing.

## Control Flow

`tcp_sigpool_alloc_ahash()` is the slow path. Under `cpool_mutex`, it reserves per-CPU scratch space at least as large as requested, searches for an existing matching algorithm and increments or reinitializes its kref, or allocates a new pool slot. Allocation duplicates the algorithm string, creates a base ahash with `crypto_alloc_ahash()`, records whether a key is needed, and verifies the transform can be cloned.

Scratch growth in `sigpool_reserve_scratch()` allocates a new buffer per possible CPU, RCU-swaps it into the per-CPU pointer, frees offline/no-old buffers immediately, and defers online old buffers through `call_rcu()`. Cleanup is asynchronous: `tcp_sigpool_release()` drops a kref and schedules work when it reaches zero; `cpool_cleanup_work_cb()` frees zero-ref entries and releases scratch buffers if no entries remain active.

`tcp_sigpool_start()` enters `rcu_read_lock_bh()`, validates the pool id, clones the base ahash, allocates an atomic ahash request, locks the current CPU scratch with `local_lock_nested_bh()`, and returns the request and scratch in `struct tcp_sigpool`. `tcp_sigpool_end()` unlocks scratch, exits RCU BH, frees the request, and frees the cloned hash. `tcp_sigpool_hash_skb_data()` hashes TCP payload bytes after the header, page frags, and nested skb frags recursively using one-entry scatterlists and `crypto_ahash_update()`.

## State and Persistence Behavior

Pool state is process-global within the module: `cpool[]`, `cpool_populated`, `__scratch_size`, per-CPU scratch pointers, and the cleanup work item. References persist across TCP users until released. Scratch buffers persist while at least one pool entry is active and can grow but not shrink until all entries are unused.

## Dependencies and Integration Points

The module depends on the kernel crypto ahash API, RCU, CPU hotplug read locking, per-CPU local locks, workqueues, krefs, skbuff fragment traversal, and TCP header helpers. Signing code integrates by allocating a pool id, starting a per-packet hash context, hashing skb data, then ending and releasing references.

## Risks and Edge Cases

The most sensitive areas are refcount lifetime, RCU scratch replacement, and BH/local lock pairing. A caller must always pair successful `tcp_sigpool_start()` with `tcp_sigpool_end()`. Pool ids become invalid after release and cleanup, so users need their own lifetime discipline. Scratch reallocation can partially fail; the code updates `__scratch_size` only on success but still schedules old scratch freeing. Hashing recursive skb frags must avoid missing payload or hashing header bytes twice.

## Test Signals

Tests should cover duplicate algorithm allocation, reference get/release, cleanup after last release, scratch growth, allocation failure paths, invalid id warnings, start/end lock pairing under BH, algorithms that require keys, hash equivalence for linear skb data, paged frags, and nested frag lists. KASAN/KCSAN/lockdep and crypto selftests are important signals.
