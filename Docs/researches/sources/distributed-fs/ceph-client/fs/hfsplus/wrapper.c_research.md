# sources/distributed-fs/ceph-client/fs/hfsplus/wrapper.c

Purpose: this file finds and reads the real HFS+ volume header, including HFS wrappers, partition maps, and multisession CD media. It also provides `hfsplus_submit_bio()`, the low-level block I/O helper used by HFS+ code that needs sector-granular reads or writes against the mounted block device.

Important APIs and types: `struct hfsplus_wd` holds wrapper-derived allocation block size/start and embedded extent information. `hfsplus_submit_bio()` aligns the requested HFS+ sector to `hfsplus_min_io_size(sb)`, returns the in-buffer offset for reads, and delegates to `bdev_rw_virt()`. `hfsplus_read_wrapper()` initializes `HFSPLUS_SB(sb)` fields such as `min_io_size`, `s_vhdr`, `s_backup_vhdr`, `alloc_blksz`, `blockoffset`, `part_start`, `sect_count`, and `fs_shift`.

Control flow: mount setup starts with `sb_min_blocksize()`, asks `hfsplus_get_last_session()` for the partition/session window, allocates volume-header buffers, then repeatedly reads sector 2 relative to the current partition. If the signature is HFS+ or HFSX it proceeds; if it is an HFS wrapper it parses `HFSP_WRAPOFF_*` fields and jumps back with an adjusted embedded start/count; otherwise it calls `hfs_part_find()` and retries. It then reads the secondary volume header at `part_start + part_size - 2`, checks matching signatures, validates the allocation block size, and sets the final VFS block size with alignment against the partition offset.

State and persistence: this code mutates only superblock in-memory mount state and allocates buffers that later represent on-disk headers. Persistent writes are not performed here, but incorrect offsets would make all later metadata I/O target the wrong sectors.

Dependencies and integration: it depends on block-device helpers, CD-ROM TOC/multisession APIs, `hfsplus_fs.h`, `hfsplus_raw.h`, and partition-map discovery. `hfsplus_read_wrapper()` is an early mount prerequisite for the rest of HFS+ metadata parsing.

Risks: the reread loop depends on valid wrapper/partition metadata and has multiple `-EINVAL` exits for malformed media. The block-size power-of-two check is essential because `hfsplus_submit_bio()` uses bit masking for alignment. The function frees buffers on failure but leaves successful ownership to later superblock teardown.

Test signals: mount images with plain HFS+, HFSX, HFS-wrapped HFS+, partition-map-contained volumes, invalid secondary headers, non-power-of-two block sizes, and multisession CD options. I/O tests should include block devices whose logical block size exceeds `HFSPLUS_SECTOR_SIZE`.
