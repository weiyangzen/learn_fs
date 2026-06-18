# sources/distributed-fs/ceph-client/fs/btrfs/bio.h

## Purpose
`bio.h` defines the high-level Btrfs bio wrapper and the public I/O submission/repair API implemented by `bio.c`. It extends the Linux `struct bio` with Btrfs inode/offset context, checksum and ordered-extent state, completion aggregation, mirror tracking, scrub/remap/async flags, and parent-check metadata for btree reads.

## Important APIs, types, and functions
- `BTRFS_BIO_INLINE_CSUM_SIZE` is the inline checksum buffer size used for small read checksum arrays.
- `btrfs_bio_end_io_t` is the high-level completion callback type.
- `struct btrfs_bio` embeds `struct bio` as its last member and stores `inode`, `file_offset`, unioned read/write/metadata state, `end_io_work`, caller `end_io` and `private`, `pending_ios`, `mirror_num`, first error `status`, and flags for commit-root checksum search, scrub, remap, async checksum, and zone append.
- The read union stores checksum pointer/inline storage and saved iterator.
- The write union stores an ordered extent, ordered sums, checksum work/completion state, checksum iterator, original physical address, and original logical address.
- The metadata union stores `struct btrfs_tree_parent_check`.
- `btrfs_bio()` converts a Linux `bio *` to its containing `struct btrfs_bio *`.
- `btrfs_bio_init()` and `btrfs_bio_alloc()` initialize or allocate high-level bios.
- `btrfs_bio_end_io()`, `btrfs_submit_bbio()`, `btrfs_submit_repair_write()`, and `btrfs_repair_io_failure()` are the exported completion/submission/repair functions.
- `REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` to mark bios that should be submitted through `blkcg_punt_bio_submit()`.
- `btrfs_bioset_init()` and `btrfs_bioset_exit()` manage module-level allocation pools.

## Control flow
Callers allocate a `struct btrfs_bio` with `btrfs_bio_alloc()` or provide an embedded one that has an already-initialized block `bio`, then call `btrfs_bio_init()` to set Btrfs-owned fields. They fill the embedded `bio` vectors and operation flags, optionally populate operation-specific fields such as `ordered`, `parent_check`, `csum_search_commit_root`, `is_scrub`, or `is_remap`, and submit with `btrfs_submit_bbio()`.

The implementation may split a high-level bio into clone bios. The original `pending_ios` tracks all outstanding pieces, `status` records the first error, and the caller's `end_io` callback fires only once through `btrfs_bio_end_io()`. Repair callers use `btrfs_repair_io_failure()` for synchronous targeted data repair writes or `btrfs_submit_repair_write()` for scrub/dev-replace style metadata repair writes to one mirror.

## State and persistence behavior
The structure is per-I/O runtime state. It does not persist independently, but it carries enough metadata for `bio.c` to update persistent device contents, checksum items via ordered extents, zoned physical addresses, and repair writes. The embedded `bio` must remain last because bioset allocation sizes depend on `offsetof(struct btrfs_bio, bio)`.

Unioned fields are operation-specific and must not be interpreted across paths: data reads use checksum fields, data writes use ordered/checksum fields, and metadata reads use parent-check fields. Flags further specialize behavior for commit-root checksum lookup, scrub, remapped data I/O, async checksum generation, and zone append.

## Dependencies and integration points
The header depends on Linux block I/O types, workqueues, Btrfs tree-checker parent verification, and forward declarations for Btrfs fs/inode types. It is included by Btrfs data, metadata, scrub, repair, checksum, and volume-mapping code that submits logical I/O through the central Btrfs bio path.

## Risks and test signals
Key risks are misuse of the union fields, failing to set `inode` for data I/O that needs checksum/repair, incorrect `file_offset` when splitting or repairing, forgetting to hold ordered extent references, callback assumptions before all split bios finish, and breaking the "embedded bio last" allocation contract. Tests should cover normal allocation/init, stack or embedded initialization, data reads with checksum lookup, metadata reads with parent checks, data writes with ordered extents and async checksums, split completion aggregation, repair submissions, scrub/remap flags, zone append state, and bioset init/exit under fault injection.
