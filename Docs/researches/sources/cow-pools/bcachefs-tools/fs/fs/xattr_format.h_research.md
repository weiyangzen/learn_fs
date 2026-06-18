# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr_format.h

## Purpose
Defines persistent xattr namespace indexes and the packed on-disk xattr value format.

## Main Contents
- Xattr type indexes:
  - user
  - POSIX ACL access
  - POSIX ACL default
  - trusted
  - security
- `struct bch_xattr`, containing value header, xattr type, name length, little-endian value length, and a flexible byte array containing name followed by value.
- Comment documenting that adding `__counted_by(x_name_len)` previously caused a false positive out-of-bounds write detection, so the flexible array remains unannotated.

## Integration Notes
`xattr.h` provides helpers for computing value sizes and locating the value portion. `xattr.c` validates type/name/value lengths and maps type indexes to VFS xattr handlers.

## Risks and Edge Cases
- Name and value share one flexible byte array; all size validation must account for both.
- The type index namespace is persistent and must remain stable for disk compatibility.
