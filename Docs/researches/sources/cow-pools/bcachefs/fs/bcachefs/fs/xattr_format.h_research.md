# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr_format.h

This header defines persistent xattr key/value layout and namespace ids.

Key elements:
- Namespace indexes:
  - user
  - POSIX ACL access
  - POSIX ACL default
  - trusted
  - security
- `struct bch_xattr` stores:
  - common `bch_val`
  - `x_type`
  - `x_name_len`
  - little-endian `x_val_len`
  - flexible `x_name_and_value[]` bytes

Important detail:
- Name and value are stored contiguously; helper macros in `xattr.h` compute the value pointer.
- The comment notes that `__counted_by(x_name_len)` previously caused a false out-of-bounds detection, so the flexible array is left without that annotation.
