# File Research: sources/cow-pools/nilfs-utils/sbin/bitops.c

## Scope

Provides portable C bitmap bit operations for mkfs-style metadata allocation.

## APIs And Behavior

When `_EXT2_HAVE_ASM_BITOPS_` is not defined:

- `ext2fs_set_bit()` sets a bit in a byte-addressed bitmap and returns the previous bit value.
- `ext2fs_clear_bit()` clears a bit and returns the previous bit value.
- `ext2fs_test_bit()` returns the current bit value.

## State And Dependencies

The code is extracted from e2fsprogs and treats bit zero as the low bit of the first byte. `mkfs.h` aliases these functions as `nilfs_set_bit`, `nilfs_clear_bit`, and `nilfs_test_bit`.

## Risks And Invariants

No bounds are checked; callers must provide a bitmap large enough for `nr`. Return values are masks, not normalized booleans.
