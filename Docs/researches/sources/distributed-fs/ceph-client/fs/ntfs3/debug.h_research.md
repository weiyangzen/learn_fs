# sources/distributed-fs/ceph-client/fs/ntfs3/debug.h

## Purpose
Provides small pointer arithmetic helpers and NTFS3 logging macros that wrap driver-specific printk functions.

## Important APIs, Types, And Functions
`Add2Ptr()` and `PtrOffset()` compute byte offsets for packed NTFS records. `ntfs_printk()` and `ntfs_inode_printk()` are declared when `CONFIG_PRINTK` is enabled and stubbed otherwise. Logging macros include `ntfs_err`, `ntfs_warn`, `ntfs_info`, `ntfs_notice`, `ntfs_inode_err`, and `ntfs_inode_warn`.

## Control Flow
Callers use macros throughout NTFS3 source files. With printk disabled, calls compile to empty inline functions while retaining format checking annotations.

## State And Persistence
No persistent state. The macros emit kernel logs only when printing is configured.

## Dependencies And Integration Points
Included by most NTFS3 files. The pointer helpers are used for packed MFT/attribute/index structures, so they are part of record parsing and mutation mechanics.

## Risks And Edge Cases
`PtrOffset()` casts pointers through `size_t`, so it assumes both pointers are within the same mapped object and addressable as integer offsets. Misuse can hide bounds errors in record parsing. Logging macros depend on callers including appropriate kernel severity prefixes.

## Test Signals
Build with and without `CONFIG_PRINTK`; compile format-checking warnings; exercise corrupted-record paths that use `Add2Ptr()`/`PtrOffset()` under KASAN/UBSAN.
