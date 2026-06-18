# File Research: sources/block-storage/linux-dm/drivers/md/bcache/debug.h

## Purpose
Declares bcache debug/verification functions and debug-controlled macros.

## Main Interfaces
- With `CONFIG_BCACHE_DEBUG`: declares `bch_btree_verify()` and `bch_data_verify()`, and exposes `expensive_debug_checks(c)`, `key_merging_disabled(c)`, and `bypass_torture_test(d)` as runtime fields.
- Without debug: verification functions are no-ops and the macros are constants.
- With `CONFIG_DEBUG_FS`: declares `bch_debug_init_cache_set()`; otherwise provides a no-op.

## Integration Points
Included by btree, extents, request, and debug code to compile the same call sites across debug and non-debug builds.

## Risks And Review Focus
- Behavior differs materially by configuration: expensive checks, key merging disable, and bypass torture flags are unavailable in non-debug builds.
- Function prototypes mention `struct btree` without a local forward declaration, relying on include ordering in users.
