<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackdepot.h -->
# sources/distributed-fs/ceph-client/include/linux/stackdepot.h

Purpose: Declares Stack Depot, a deduplicating storage service for stack traces used by sanitizers and debugging subsystems to avoid storing repeated stack arrays per object.

Important APIs/types/functions: `depot_stack_handle_t`, handle layout constants, `union handle_parts`, `struct stack_record`, `depot_flags_t`, `STACK_DEPOT_FLAG_CAN_ALLOC`, `STACK_DEPOT_FLAG_GET`, initialization APIs, `stack_depot_save_flags()`, `stack_depot_save()`, `__stack_depot_get_stack_record()`, `stack_depot_fetch()`, `stack_depot_print()`, `stack_depot_snprint()`, `stack_depot_put()`, `stack_depot_set_extra_bits()`, and `stack_depot_get_extra_bits()`.

Control flow: Users initialize Stack Depot early or at runtime, save stack entries to receive compact handles, later fetch or print entries by handle, optionally hold/release references with `STACK_DEPOT_FLAG_GET`, and may use spare handle bits for caller metadata.

State and persistence behavior: When enabled, stack records live in depot pools and hash lists, with handle fields encoding pool index, offset, and extra bits. Reference-counted records can be freed through an RCU-safe freelist path. No on-disk persistence exists.

Dependencies: GFP allocation, page sizing, list heads, refcounts, RCU cookies, and `CONFIG_STACKDEPOT`/frame-count configuration.

Integration points: KASAN, SLUB debugging, leak detection, and any subsystem storing many repeated stack traces.

Risks: Saving without allocation permission in contexts that need new pools can fail. Users of `STACK_DEPOT_FLAG_GET` must call `stack_depot_put()` or refcounts can overflow/leak. Extra bits must fit `STACK_DEPOT_EXTRA_BITS`.

Test signals: Stack depot initialization modes, save/fetch deduplication tests, no-allocation context tests, refcount put/evict tests, snprint output tests, and extra-bit encode/decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackdepot.h -->
