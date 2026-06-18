# File Research: sources/block-storage/kvdo/vdo/vdo-resume.c

## Purpose
Implements VDO preresume behavior: commits any new table configuration, transitions metadata state to dirty when needed, and resumes subsystems in dependency order.

## Resume Phases
- Start resuming and write dirty superblock if needed.
- Allow read-only mode entry.
- Resume dedupe/hash zones.
- Resume slab depot.
- Resume recovery journal.
- Resume block map.
- Resume logical zones.
- Apply compression setting and resume packer.
- Resume flusher.
- Resume data VIO pool.
- Finish resuming.

## Key Functions
- `vdo_preresume_internal()` is the external entry point used during device-mapper preresume.
- `apply_new_vdo_configuration()` commits logical and physical growth requested by the new table.
- `resume_callback()` drives the admin operation across phase-specific threads.
- `write_super_block()` changes `VDO_CLEAN` or `VDO_NEW` to `VDO_DIRTY` before normal operation.

## Important Behavior
- The new `device_config` is installed after attempted configuration changes, whether they succeed or fail.
- Commit failures enter in-memory read-only mode because the device is suspended and disk state is not updated.
- `VDO_READ_ONLY` during resume is treated as successful resume.
- Compression is enabled/disabled from `device_config->compression` during packer resume.
- `VDO_REPLAYING` is invalid for resume superblock transition.
