# sources/distributed-fs/ceph-client/tools/perf/util/sharded_mutex.c

`sharded_mutex.c` implements allocation and destruction for a hash-sharded mutex pool. The pool lets many logical objects share a fixed number of mutexes selected by hash, reducing per-object memory overhead at the cost of possible lock collisions.

`sharded_mutex__new(size_t num_shards)` rounds the requested shard count up to the next power of two by computing `cap_bits`, allocates one `struct sharded_mutex` plus `1 << cap_bits` flexible-array mutexes, stores `cap_bits`, initializes each mutex with `mutex_init()`, and returns the pool. Allocation failure returns `NULL`.

`sharded_mutex__delete(struct sharded_mutex *sm)` destroys each mutex with `mutex_destroy()` and frees the allocation. It assumes `sm` is non-null and that no thread still owns or waits on any shard.

State is entirely heap-local to the returned pool. There is no persistence. The power-of-two capacity is persisted in `cap_bits`, and callers use the inline getter from the header to map hashes to mutexes.

Dependencies are `sharded_mutex.h`, `mutex.h`, and standard allocation. Integration points are perf data structures that need low-overhead per-object locking with stable hashes.

Risks include undefined behavior for `num_shards == 0` if callers expect no mutexes, shift overflow for extremely large `num_shards`, no cleanup path if a later `mutex_init()` could fail on a platform where it returns errors, and null dereference if `sharded_mutex__delete(NULL)` is called. Lock contention depends on shard count and hash quality.

Test signals should cover creation with one, exact power-of-two, and non-power-of-two shard counts; hash-to-shard distribution through the header inline; multithreaded lock/unlock use; deletion after all locks are released; and boundary handling for zero or very large counts if the caller surface permits them.
