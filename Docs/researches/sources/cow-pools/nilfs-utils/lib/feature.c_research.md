# File Research: sources/cow-pools/nilfs-utils/lib/feature.c

Implements NILFS feature flag parsing and formatting. The known named feature is read-only compatible `block_count`; unknown feature bits are formatted as `FEATURE_Cn`, `FEATURE_Rn`, or `FEATURE_In`.

`nilfs_edit_feature()` parses comma/space-separated feature edits, supports `none`, supports `^feature` negation, validates set/clear operations against caller-provided masks, and returns the bad type/mask on failure.
