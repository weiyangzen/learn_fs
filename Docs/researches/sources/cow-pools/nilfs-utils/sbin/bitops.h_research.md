# File Research: sources/cow-pools/nilfs-utils/sbin/bitops.h

## Scope

Declares ext2-compatible bitmap helper functions.

## API Surface

The header exposes `ext2fs_set_bit()`, `ext2fs_clear_bit()`, and `ext2fs_test_bit()` for use by NILFS mkfs metadata initialization.

## Dependencies And Risks

It has a simple include guard and no external includes. Callers must match the implementation's byte-addressed bitmap assumptions and perform their own bounds validation.
