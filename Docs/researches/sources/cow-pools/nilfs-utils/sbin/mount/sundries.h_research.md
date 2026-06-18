# File Research: sources/cow-pools/nilfs-utils/sbin/mount/sundries.h

## Scope

Declares legacy helper support functions and traditional mount exit status bits.

## API Surface

Exposes signal blocking, canonicalization, diagnostics, type/option matching, fatal allocation/string helpers, `die()`, optional NFS mount prototype, and exit bit constants such as `EX_USAGE`, `EX_SYSERR`, `EX_FILEIO`, `EX_FAIL`, and `EX_SOMEOK`.

## Dependencies And Risks

The header assumes users include string functions for the `streq` macro. Exit constants are shared behavior for legacy mount and umount helpers.
