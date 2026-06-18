# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.c

## Role

`io_misc.c` implements filesystem data-range operations that mutate extents but are not normal writeback: fallocate, punch hole, truncate, insert range, and collapse range.

## Major Functions

- `bch2_extent_fallocate()`: overwrites a range with reservation keys or unwritten extents, depending on nocow support.
- `bch2_fpunch_snapshot()`: fsck-oriented punch over a snapshot range.
- `bch2_fpunch_at()` / `bch2_fpunch()`: delete or trim extent coverage over a logical byte range.
- `bch2_truncate()`: creates and resumes a logged truncate operation.
- `bch2_resume_logged_op_truncate()`: replays truncate by setting inode size then punching extents past EOF.
- `bch2_fcollapse_finsert()`: starts logged insert/collapse-range operations.
- `bch2_resume_logged_op_finsert()`: replays extent shifting and inode size adjustment.

## Fallocate Behavior

For ordinary allocation, the file emits `KEY_TYPE_reservation` keys sized to the requested sector range and desired replica count. For nocow plus unwritten-extent support, it directly allocates physical sectors, appends pointers, and marks them unwritten.

The code reserves disk space before allocator interaction, tracks sectors actually allocated, and increments the write clock after successful physical allocation.

## Logged Operations

Truncate and finsert/fcollapse are represented as logged bkeys so they can resume after crash. Both hold `snapshots.create_lock` for snapshot consistency during operation start/resume/finish.

Finsert/fcollapse has a state machine:
- start
- shift extents
- finish

It shifts extents backward or forward through the extents btree, uses delete+copy insertions, handles snapshot divergence, and updates `op->v.pos` so replay can continue.

## Invariants

- Transaction restarts are expected and retried around btree mutations.
- Extent punch uses extent-update paths for correct trimming/accounting.
- Insert-range can split compressed extents and reserves enough space when snapshot copies or compressed splits require new allocation accounting.
- Logged operation resume treats missing subvolumes differently when running from recovery versus foreground paths.
