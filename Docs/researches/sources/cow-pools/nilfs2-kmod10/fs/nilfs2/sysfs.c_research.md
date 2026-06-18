# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.c

## Summary
Implements NILFS2 sysfs exposure under `/sys/fs/nilfs2`. It creates global feature attributes, per-device groups, mounted snapshot groups, and read/write controls for selected runtime tunables.

## Main Responsibilities
- Creates the top-level NILFS kset and `features` group.
- Creates per-device kobjects named by `sb->s_id`.
- Creates per-device subgroups: `mounted_snapshots`, `checkpoints`, `segments`, `superblock`, and `segctor`.
- Creates snapshot kobjects for current checkpoint and mounted read-only snapshots.
- Exposes checkpoint, segment, segctor, superblock, and device statistics.
- Provides a writable `superblock/sb_update_frequency` attribute.
- Performs kobject cleanup on group creation failure and device teardown.

## Exposed Data
Snapshot attributes:
- `inodes_count`, `blocks_count`, `README`.

Checkpoint attributes:
- `checkpoints_number`, `snapshots_number`, `last_seg_checkpoint`, `next_checkpoint`, `README`.

Segment attributes:
- `segments_number`, `blocks_per_segment`, `clean_segments`, `dirty_segments`, `README`.

Segctor attributes:
- Last/current segment block, sequence, checkpoint, next segment, partial segment offset, write times, non-GC write times, dirty data block count, and `README`.

Superblock attributes:
- `sb_write_time`, `sb_write_time_secs`, `sb_write_count`, `sb_update_frequency`, `README`.

Device attributes:
- `revision`, `blocksize`, `device_size`, `free_blocks`, `uuid`, `volume_name`, `README`.

Feature attributes:
- Driver revision and `README`.

## Important Behavior
Most attributes are read-only and use `sysfs_emit()`. `sb_update_frequency` parses an unsigned integer, clamps values below `NILFS_SB_FREQ` to the minimum, and updates `ns_sb_update_freq` under `ns_sem`.

The helper macros generate sysfs ops, kobj types, create functions, and delete functions for internal per-device subgroups. Snapshot kobjects are parented either directly under the device as `current_checkpoint` or under `mounted_snapshots/<checkpoint>`.

## State and Synchronization
Reads use the relevant NILFS locks: `ns_sem` for superblock fields, `ns_segctor_sem` for segment-constructor state, `ns_last_segment_lock` for latest segment cursor fields, and metadata semaphores where sufile/cpfile stats are queried.

## Risks
Kobject lifetime must be paired correctly with group creation failure paths and device deletion. Some sysfs reads call into metadata stat functions and can return kernel errors directly. `volume_name` formatting uses the raw fixed-size superblock field and truncation semantics should be treated carefully.
