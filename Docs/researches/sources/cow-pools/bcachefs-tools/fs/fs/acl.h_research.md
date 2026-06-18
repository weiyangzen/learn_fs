# File Research: sources/cow-pools/bcachefs-tools/fs/fs/acl.h

## Purpose

Defines bcachefs on-disk ACL structures and declares ACL helper APIs.

## Main Interfaces

- `BCH_ACL_VERSION`.
- On-disk structs: `bch_acl_entry`, `bch_acl_entry_short`, `bch_acl_header`.
- `bch2_acl_to_text()`.
- Under `!NO_BCACHEFS_FS`: get/set/chmod ACL APIs.
- Under `NO_BCACHEFS_FS`: no-op stubs for transactional set/chmod helpers.

## Notes

The header separates portable ACL format handling from VFS-only behavior, allowing tools/userspace builds to compile without Linux VFS ACL operations.
