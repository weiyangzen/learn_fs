# sources/distributed-fs/ceph-client/security/ipe/ipe.h

Purpose: Shared IPE top-level declarations and logging prefix.

Important APIs/types/functions: Defines `pr_fmt`, declares `ipe_sb()`, `ipe_enabled`, optional `ipe_bdev()`/`ipe_inode()`, and `ipe_init_securityfs()`.

Control flow: Header-only interface.

State and persistence: Exposes global enablement and blob accessors for persistent LSM blob storage.

Dependencies and integration: Included across IPE source files and depends on LSM hook types.

Risks and test signals: Interface risks are config guard mismatch and accessor misuse before blob allocation. Build matrix validates most issues.
