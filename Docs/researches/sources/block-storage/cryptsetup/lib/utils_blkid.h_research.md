# File Research: sources/block-storage/cryptsetup/lib/utils_blkid.h

## Purpose
Declares the local blkid probe wrapper interface.

## Key Responsibilities
- Forward-declares `struct blkid_handle`.
- Defines `blk_probe_status` values: `PRB_OK`, `PRB_EMPTY`, `PRB_AMBIGUOUS`, `PRB_FAIL`.
- Declares initialization, chain selection, LUKS filtering, probing, type accessors, wipe, support detection, and block-size lookup functions.

## Important Details
- Documents that fd-based initialization resets the file description offset.
- Keeps libblkid dependency out of most callers by hiding the concrete handle type.
