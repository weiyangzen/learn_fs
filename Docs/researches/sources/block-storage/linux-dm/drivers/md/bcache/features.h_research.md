# File Research: sources/block-storage/linux-dm/drivers/md/bcache/features.h

`features.h` defines the superblock feature-bit contract used by bcache cache devices. It separates feature classes into compatible, read-only compatible, and incompatible spaces, with helper masks for direct bit testing. In this snapshot the only supported feature bits are incompatible bucket-size layout flags: the obsolete 32-bit large bucket encoding and the newer logarithmic large-bucket-size encoding.

The core generated helpers come from `BCH_FEATURE_*_FUNCS()`, which emit `bch_has_feature_*()`, `bch_set_feature_*()`, and `bch_clear_feature_*()` routines against `struct cache_sb`. The generated `has` helpers explicitly return false for superblocks older than `BCACHE_SB_VERSION_CDEV_WITH_FEATURES`, so callers can use the same helpers on old and feature-bearing superblocks.

Unknown-feature detection is centralized in `bch_has_unknown_compat_features()`, `bch_has_unknown_ro_compat_features()`, and `bch_has_unknown_incompat_features()`. `super.c` uses these checks while reading feature-bearing cache superblocks, rejecting devices with unsupported bits before interpreting bucket geometry. The file also declares the feature-printing functions consumed by `sysfs.c` for `feature_compat`, `feature_ro_compat`, and `feature_incompat`.

Important dependencies are `bcache_ondisk.h` for `struct cache_sb` layout and superblock version constants, plus `features.c` for the declared printers. The main invariant is that feature bits are meaningful only on cache-device superblocks at or above the feature-version threshold.
