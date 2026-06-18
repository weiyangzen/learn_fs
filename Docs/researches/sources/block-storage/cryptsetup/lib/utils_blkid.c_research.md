# File Research: sources/block-storage/cryptsetup/lib/utils_blkid.c

## Purpose
Provides an abstraction over libblkid probing and wiping so cryptsetup can detect and optionally erase filesystem, partition, and LUKS signatures.

## Key Responsibilities
- Creates blkid probe handles from paths or file descriptors.
- Configures probe chains for wipe detection, full printing, superblock-only detection, and fast detection.
- Filters LUKS superblocks in or out.
- Wraps normal and safe blkid probes into local `PRB_*` status values.
- Exposes detected partition/superblock type and superblock block size.
- Wipes detected magic signatures with libblkid wipe support or a manual fallback.

## Important Details
- The manual wipe fallback reads magic offsets/lengths from blkid values and writes zeros using aligned blockwise I/O.
- `blk_init_by_fd()` warns in the header that the file description offset is reset.
- When libblkid is unavailable, every API has a stub returning failure/unsupported values.
- Compatibility macros cover older blkid versions lacking wipe or bad-checksum flags.

## Dependencies
Depends on `utils_blkid.h`, `utils_io.h`, optional `<blkid/blkid.h>`, and blockwise write helpers.
