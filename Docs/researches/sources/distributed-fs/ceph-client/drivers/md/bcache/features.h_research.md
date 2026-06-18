# sources/distributed-fs/ceph-client/drivers/md/bcache/features.h

Purpose: defines bcache on-disk feature classes, supported feature masks, feature-bit accessors, generated per-feature helpers, unknown-feature checks, and string-printing prototypes.

Important APIs/macros: feature classes are `BCH_FEATURE_COMPAT`, `BCH_FEATURE_RO_COMPAT`, and `BCH_FEATURE_INCOMPAT`. Incompat bits include obsolete large bucket and log-encoded large bucket size. `BCH_FEATURE_*_SUPP` masks define what this implementation supports. `BCH_HAS_*_FEATURE()` tests raw superblock fields. `BCH_FEATURE_*_FUNCS()` generates `bch_has_feature_*`, `bch_set_feature_*`, and `bch_clear_feature_*`; this file instantiates helpers for `obso_large_bucket` and `large_bucket`. Unknown-feature helpers detect unsupported bits.

Control flow: generated `has` functions return false for superblocks older than `BCACHE_SB_VERSION_CDEV_WITH_FEATURES`, preserving compatibility with legacy layouts. Set/clear functions directly mutate the relevant feature field in `struct cache_sb`.

State and persistence: feature bits live in the on-disk cache superblock. These macros control mount/registration compatibility decisions and superblock mutation for feature enable/disable operations.

Dependencies/integration: includes Linux kernel/types headers and `bcache_ondisk.h`; print functions are implemented in `features.c` and used by sysfs-style reporting.

Risks/test signals: unknown incompatible features must prevent unsafe use elsewhere in registration code; this header only provides detection. The macro names concatenate `BCH##_FEATURE...`, which depends on exact token construction. Tests should cover legacy-version false returns, unknown masks for all classes, setting/clearing each known bit, and large-bucket superblock compatibility.
