# sources/distributed-fs/ceph-client/drivers/md/bcache/debug.h

Purpose: exposes debug-only verification hooks and debug-mode feature macros while compiling them out cleanly for normal builds. It is the switch point between expensive debug instrumentation and zero-cost stubs.

Important APIs/macros: with `CONFIG_BCACHE_DEBUG`, declares `bch_btree_verify()` and `bch_data_verify()` and maps `expensive_debug_checks(c)`, `key_merging_disabled(c)`, and `bypass_torture_test(d)` to runtime cache-set/device fields. Without it, the functions become empty inline stubs and the macros return zero. With `CONFIG_DEBUG_FS`, declares `bch_debug_init_cache_set()`; otherwise that cache-set hook is an empty inline stub.

Control flow: callers can unconditionally invoke verification or query debug knobs. Preprocessor branches decide whether those calls do real work, so request, B-tree, and extent code avoid scattered `#ifdef` blocks.

State and persistence: no persistent state is declared here. The macros expose flags stored in `cache_set` or cached device structures, influencing runtime decisions such as expensive pointer validation, key merging, and randomized bypass torture.

Dependencies/integration: forward-declares `bio`, `cached_dev`, and `cache_set`; `btree.h` includes this header, and `debug.c`, `extents.c`, `request.c`, and B-tree write paths rely on the macros.

Risks: because debug macros alter behavior, tests should cover both debug and non-debug configurations. In particular, `key_merging_disabled()` changes extent merge decisions and `bypass_torture_test()` changes request bypass behavior, so debug-enabled test failures may not reproduce in production builds.
