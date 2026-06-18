# File Research: sources/cow-pools/nilfs-utils/sbin/mount/libmount_compat.h

## Scope

Provides compatibility definitions for libmount exit-status macros.

## API Surface

Includes `<libmount.h>` and defines `MNT_EX_SUCCESS`, `MNT_EX_USAGE`, `MNT_EX_SYSERR`, `MNT_EX_SOFTWARE`, `MNT_EX_USER`, `MNT_EX_FILEIO`, `MNT_EX_FAIL`, and `MNT_EX_SOMEOK` when absent.

## Dependencies And Risks

This keeps source compatible with older libmount headers. Values mirror traditional mount helper exit bit meanings; mismatches with a platform libmount would affect process exit semantics.
