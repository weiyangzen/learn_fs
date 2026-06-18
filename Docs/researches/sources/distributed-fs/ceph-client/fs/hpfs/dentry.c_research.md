# sources/distributed-fs/ceph-client/fs/hpfs/dentry.c

Purpose: this file implements HPFS dcache name hashing and comparison. It gives the VFS case-insensitive, HPFS-specific filename semantics.

Important APIs and functions: `hpfs_hash_dentry()` adjusts trailing dots/spaces, uppercases through the mounted HPFS code page, and sets the qstr hash. `hpfs_compare_dentry()` validates lookup names with `hpfs_chk_name()` and compares existing and candidate names through `hpfs_compare_names()`. `hpfs_dentry_operations` exports these as `.d_hash` and `.d_compare`.

Control flow: hash generation preserves `.` and `..` special cases but otherwise trims OS/2-cleared suffix characters before hashing. Comparison trims the existing dentry string, validates the incoming name, and returns mismatch on invalid or non-equal names.

State and persistence: no persistent state is changed. The code reads the superblock code-page table and mutates the transient qstr hash.

Dependencies and integration: it depends on `name.c` for adjustment, validation, upcase, and comparison. Superblock setup installs these dentry operations so lookups match HPFS on-disk ordering and case behavior.

Risks: hashing and comparison must stay aligned; otherwise dentries can be missed or aliased incorrectly. The code intentionally does not reject too-long names during hashing, leaving validation to compare/lookup paths.

Test signals: lookup names differing only by case, trailing dots/spaces, long-name flags, invalid characters, `.`/`..`, and non-ASCII bytes mapped through the HPFS code page table.
