# File Research: sources/cow-pools/nilfs2-kmod10/include/uapi/linux/nilfs2_api.h

## Summary
Defines the NILFS2 user-space ABI: checkpoint, segment usage, cleaner, virtual block, disk block descriptor structures, flag helpers, and ioctl numbers.

## Main ABI Structures
- `struct nilfs_cpinfo`: checkpoint metadata returned to userspace.
- `struct nilfs_suinfo`: segment usage metadata.
- `struct nilfs_suinfo_update`: selective segment usage update descriptor.
- `struct nilfs_cpmode`: checkpoint/snapshot mode changes.
- `struct nilfs_argv`: generic pointer/count/size/index argument vector.
- `struct nilfs_period`: checkpoint-number interval.
- `struct nilfs_cpstat`: checkpoint totals.
- `struct nilfs_sustat`: segment usage totals and protection sequence.
- `struct nilfs_vinfo`: virtual block lookup result.
- `struct nilfs_vdesc`: virtual block descriptor for cleaner queries.
- `struct nilfs_bdesc`: disk block descriptor for cleaner block moves.

## Flags and Helpers
Checkpoint flags include snapshot, invalid, sketch, and minor. Segment usage flags include active, dirty, and error. Update flags select last modification time, block count, and flags fields inside `nilfs_suinfo_update`.

The header provides inline helper predicates and set/clear functions for these flag fields.

## Ioctls
Defines ioctl identity `'n'` and commands for:
- Changing checkpoint mode.
- Deleting checkpoints.
- Getting checkpoint info/statistics.
- Getting and setting segment usage info/statistics.
- Looking up virtual block info.
- Getting block descriptors.
- Cleaning segments.
- Syncing.
- Resizing.
- Setting segment allocation range.

## Important Details
`NILFS_IOCTL_CLEAN_SEGMENTS` takes an array of five `nilfs_argv` structures, matching the cleaner path that passes multiple vectors into kernel segment cleaning. `nilfs_argv.v_base` is a 64-bit userspace pointer value to keep the ABI fixed across architectures.

The active segment usage flag is exposed through `nilfs_suinfo` but is virtual in kernel state; sufile update code clears it before writing flags to disk.

## Risks
This is a stable UAPI header. Field sizes, alignment padding, ioctl numbers, and struct layouts must not be changed casually. Kernel internals must continue to validate sizes/counts from `nilfs_argv` before trusting userspace buffers.
