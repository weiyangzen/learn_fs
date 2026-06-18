# File Research: sources/block-storage/parted/libparted/labels/fdasd.c

This file is the IBM s390 DASD/VTOC helper implementation used by libparted’s DASD support, adapted from Linux `fdasd`.

Key responsibilities:
- Maintains an `fdasd_anchor_t` with geometry, VTOC labels, volume label, partition list, free-space state, and DASD metadata.
- Reads, validates, recreates, prepares, and writes VOL1/VTOC labels.
- Creates and updates format 1, 4, 5, 7, 8, and 9 labels.
- Handles DASD-specific geometry, device type, API version, volume serial, and partition data set names.

Core behavior:
- `fdasd_initialize_anchor()` zeroes the anchor, initializes partition-number mappings, allocates label buffers, initializes the format 9 template, and creates a linked list of `partition_info_t` nodes.
- `fdasd_cleanup()` frees label buffers and partition-info nodes.
- `fdasd_error()` maps local failure enums to translated libparted exceptions.
- `fdasd_get_geometry()` uses regular-file simulation for tests, otherwise uses `BLKGETSIZE64`, `HDIO_GETGEO`, `BLKSSZGET`, and `BIODASDINFO`; it also supports fallback validation as DASD 3390 geometry.
- `fdasd_check_api_version()` checks the DASD kernel driver API unless operating on a regular file.
- `fdasd_check_volume()` reads the volume label, validates `VOL1`, `LNX1`, or `CMS1`, follows the VTOC pointer, initializes missing labels for unlabeled non-file devices, and handles FBA layout.
- `fdasd_valid_vtoc_pointer()` reads format 4 and processes valid or invalid VTOC cases.
- `fdasd_process_valid_vtoc()` scans VTOC records, loads FMT1/FMT8 partition labels, initializes missing FMT5/FMT7 labels, handles old partition-name numbering, reorganizes labels, and updates partition info.
- `fdasd_recreate_vtoc()` and `fdasd_reuse_vtoc()` rebuild free-space and partition labels while preserving relevant partition extents/name fields.
- `fdasd_add_partition()` allocates an unused FMT1/FMT8 label, computes track extents, inserts the partition in sorted order, updates FMT4 and free-space labels, and marks VTOC changed.
- `fdasd_prepare_labels()` and `fdasd_write_vtoc_labels()` generate or preserve EBCDIC data set names, emit VTOC labels, write FMT9 companions for FMT8 labels, and clear leftover label slots.
- `fdasd_write_labels()` writes volume and VTOC labels only when marked changed.
- `fdasd_check_volser()`, `fdasd_get_volser()`, and `fdasd_change_volser()` validate, read, and update six-character volume serials.

Integration:
- Depends heavily on `parted/vtoc.h`, `parted/fdasd.h`, `parted/device.h`, Linux DASD ioctls, and libparted exception handling.
- Track/cylinder conversions are delegated to VTOC helpers such as `cchh2trk()`, `cchhb2blk()`, `vtoc_set_extent()`, and EBCDIC conversion helpers.
- Unlike the disk-label backend files, this file does not register a `PedDiskType`; it is a helper layer for DASD label code elsewhere.

Risk notes:
- Several string operations use fixed VTOC field lengths and `sprintf`/`strncpy`; the surrounding buffers are fixed-size by format contract, so correctness depends on the hard-coded field sizes.
- Regular-file geometry simulation is explicitly for testing and may not model all DASD layout edge cases.
- `fdasd_error()` throws exceptions but returns `void`; callers rely on libparted exception semantics rather than direct error propagation in several paths.
