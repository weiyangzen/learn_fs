# File Research: sources/block-storage/bcache-tools/features.h

This header declares `print_cache_set_supported_feature_sets(struct cache_sb *sb)` behind `_BCACHE_FEATURES_H`. It does not include `bcache.h`, so includers must have `struct cache_sb` visible or accept an incomplete type declaration context.
