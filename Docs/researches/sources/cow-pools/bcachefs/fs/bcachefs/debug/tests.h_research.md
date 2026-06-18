# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/tests.h

Declares the optional bcachefs debug test entry point.

Key declaration:
- Under `CONFIG_BCACHEFS_TESTS`, exposes `bch2_btree_perf_test(struct bch_fs *, const char *, u64, unsigned)`.

Core mechanics:
- Outside `CONFIG_BCACHEFS_TESTS`, the header provides no fallback implementation; callers are expected to guard use with the same config option.

Filesystem relevance:
- Connects sysfs debug test dispatch to the optional in-kernel btree test implementation.
