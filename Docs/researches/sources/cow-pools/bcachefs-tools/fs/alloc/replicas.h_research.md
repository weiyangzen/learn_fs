# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.h

Public replicas tracking header.

Exports:
- Replica entry sort, text, and validation helpers.
- CPU replica table text rendering.
- Device-list and bkey-to-replica conversion helpers.
- Marked/mark APIs for ensuring replica entries exist.
- Cached replica-entry constructor.
- Readability/writability checks for device masks.
- Superblock journal/data query helpers.
- Replica entry get/put/kill APIs for refcounted journal entries.
- Replica GC helpers.
- Superblock-to-CPU conversion.
- Superblock field ops for `replicas` and `replicas_v0`.
- Shutdown verification and cleanup helpers.

Defines:
- `bch2_replicas_entry_has_dev()`.
- `bch2_replicas_entry_eq()`.
- `replicas_entry_next()` and `for_each_replicas_entry()` for variable-length superblock fields.

Role:
- Shared by allocation, journal, mount/device checks, fsck/accounting, and superblock validation code.
