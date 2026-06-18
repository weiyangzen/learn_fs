# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.c

Implements replica-entry tracking in memory and on disk, plus read/write availability checks.

Main responsibilities:
- Convert bkeys, extents, stripes, and device lists into normalized `bch_replicas_entry_v1` entries.
- Keep in-memory replicas sorted in Eytzinger layout for fast lookup.
- Add newly observed replica entries to `c->replicas` and persist them into the superblock.
- Maintain atomic refcounts for journal replica entries.
- Garbage collect unreferenced or no-longer-accounted replica entries.
- Convert superblock replica fields between legacy v0 and current v1 encodings.
- Validate replica fields during superblock validation.
- Check if a filesystem can be read or written with a given device mask and force flags.
- Query whether a superblock/device has journal/data by replica entries.

Important behavior:
- User-data replica entries are treated as obsolete in superblocks when metadata version is at least `no_sb_user_data_replicas`; metadata and journal entries remain relevant.
- `extent_to_replicas()` ignores cached pointers and sets `nr_required = 0` when EC is present so stripe accounting supplies requirements.
- `stripe_to_replicas()` sets `nr_required` to data blocks (`nr_blocks - nr_redundant`) and lists stripe devices.
- Slow-path marking takes `sb_lock` and `capacity.mark_lock`, updates CPU replicas, converts to superblock format, and writes the superblock after dropping mark lock.
- v0 superblock output is used when no entry needs `nr_required != 1`; v1 is used when required count matters.

Read/write policy:
- `bch2_can_read_replicas_with_devs()` distinguishes metadata vs user data and maps missing/degraded states to force flags.
- `bch2_can_write_fs_with_devs()` checks online durable devices by data type, enforcing journal, btree, and user-data availability plus replica count thresholds unless degraded force flags allow it.

Concurrency:
- `capacity.mark_lock` protects `c->replicas`.
- `sb_lock` protects persisted superblock updates.
- Journal replica entry refcounts use atomics.

Dependencies:
- Accounting memory GC, bucket/device helpers, superblock IO, journal data type constants, sort/Eytzinger helpers.
