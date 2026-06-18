# File Research: sources/cow-pools/bcachefs-tools/include/linux/hash.h

This header provides Linux integer and pointer hash helpers. It defines `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `GOLDEN_RATIO_PRIME`, `hash_long()`, generic `__hash_32()`, `hash_32()`, `hash_64()`, `hash_ptr()`, and `hash32_ptr()`.

The hashing strategy multiplies by a golden-ratio-derived odd constant and uses high bits for the result. On 32-bit builds, 64-bit hashing folds through 32-bit operations; on 64-bit builds, it uses a 64-bit multiply.
