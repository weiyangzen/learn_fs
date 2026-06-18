# File Research: sources/cow-pools/nilfs-utils/include/nilfs_feature.h

Declares feature flag conversion and editing helpers. It defines compatibility feature classes: compat, read-only compat, and incompat, plus a negate marker used when reporting invalid clear operations.

Used by feature-management code to convert between names like `block_count` or generated `FEATURE_R0` style names and bit masks.
