# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas.c

Implements replica-set tracking, validation, superblock conversion, refcounting, GC cleanup, readability/writability checks, and device-data queries.

Main responsibilities:
- Represent on-disk replica entries as sorted in-memory `struct bch_replicas_cpu` entries with atomic refs.
- Convert bkeys and device lists into `bch_replicas_entry_v1` entries.
- Mark new replica entries, adding them to the CPU table and superblock when needed.
- Refcount journal replica entries and remove unused ones.
- Garbage-collect unreferenced or obsolete replica entries.
- Convert between superblock `replicas_v0`, `replicas`, and in-memory CPU form.
- Validate superblock replica fields, including invalid devices, bad required counts, and duplicates.
- Determine whether a filesystem can be read or written with a given device mask and force flags.
- Query whether the superblock has journal replicas or whether a device has any data types recorded.
- Verify replica refs are clean at shutdown.

Important data flow:
- `extent_to_replicas()` extracts non-cached extent pointers. EC pointers set `nr_required = 0` because stripe data is represented separately.
- `stripe_to_replicas()` records stripe devices and required block count as `nr_blocks - nr_redundant`.
- `bch2_bkey_to_replicas()` maps btree pointers to btree replicas, extents/reflink values to user replicas, and stripes to parity replicas.
- `cpu_replicas_add_entry()` grows the in-memory table, copies old entries, appends a variable-length new entry, and sorts in Eytzinger order.
- `bch2_mark_replicas_slowpath()` updates CPU state under `mark_lock` and `sb_lock`, converts it back to superblock form, then writes the superblock if changed.
- `bch2_replicas_gc_accounted()` compares replica entries against disk accounting keys and removes entries no longer accounted.

Compatibility behavior:
- `replicas_v0` entries have no `nr_required`; conversion sets `nr_required = 1`.
- If no entry requires `nr_required != 1`, CPU-to-superblock conversion writes the v0 field; otherwise it writes the v1 `replicas` field.
- For metadata version `no_sb_user_data_replicas` and later, user-data replica entries are considered obsolete and skipped/implicitly marked.

Read/write policy:
- `bch2_can_read_replicas_with_devs()` checks online devices against `nr_required`, distinguishing metadata/data lost and degraded force flags.
- Cached replicas are always readable for this check.
- `bch2_can_write_fs_with_devs()` requires online journal, btree, and user data writable durability and enforces metadata/data degraded force flags against desired replicas.

Concurrency:
- `c->capacity.mark_lock` protects the in-memory replica table.
- `c->sb_lock` protects superblock field updates.
- `PF_MEMALLOC_NOFS` is used around superblock/replica mutation paths.
