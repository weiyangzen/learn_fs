# sources/distributed-fs/ceph-client/drivers/md/bcache/features.c

Purpose: converts cache-set feature bits into human-readable sysfs strings. The current feature table exposes the incompatible `large_bucket` feature for log-encoded large bucket sizes.

Important APIs/functions: `bch_print_cache_set_feature_compat()`, `bch_print_cache_set_feature_ro_compat()`, and `bch_print_cache_set_feature_incompat()` each build a feature list into a caller-provided buffer. The local `feature_list` maps feature class, bit mask, and printable name. `compose_feature_string()` marks enabled features by wrapping their names in brackets.

Control flow: each print function initializes `out = buf`, invokes the macro for its feature class, and returns the byte count. The macro iterates the feature table, filters by class, tests the corresponding feature bits in `c->cache->sb`, and appends a newline if at least one feature in that class exists in the table.

State and persistence: reads persistent superblock feature fields through `cache_set->cache->sb`; it does not modify them. Output reflects only entries present in `feature_list`, so supported but unlisted bits would not print by name.

Dependencies/integration: includes `bcache_ondisk.h`, `bcache.h`, and `features.h`. These functions are intended for cache-set sysfs display paths.

Risks/test signals: `snprintf(out, buf + size - out, ...)` relies on pointer arithmetic for remaining length; tests should use small buffers and all feature classes. The feature table sentinel uses `compat == 0`, so a future compatible feature with class value zero cannot be represented without changing the sentinel scheme. Test with enabled and disabled large-bucket incompat bits and legacy superblock versions.
