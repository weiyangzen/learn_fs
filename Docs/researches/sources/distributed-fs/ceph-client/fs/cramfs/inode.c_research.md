# sources/distributed-fs/ceph-client/fs/cramfs/inode.c

Purpose: implements Cramfs VFS integration: inode construction, block-device and MTD-backed image reading, direct physical mmap support for suitable MTD images, superblock validation, directory iteration/lookup, folio decompression, statfs, mount, and module registration.

Important APIs/functions: `cramino()` computes inode numbers from on-disk inode offsets. `get_cramfs_inode()` creates VFS inodes for regular files, directories, symlinks, and special files. `cramfs_read()` dispatches to `cramfs_blkdev_read()` or `cramfs_direct_read()`. `cramfs_get_block_range()` and `cramfs_physmem_mmap()` enable direct mapping of aligned uncompressed blocks. `cramfs_read_super()` validates magic, feature flags, root inode, size/fsid, and root offset. `cramfs_readdir()`, `cramfs_lookup()`, and `cramfs_read_folio()` provide directory and file data operations.

Control flow: mount tries MTD if enabled, then blockdev if enabled. Fill-super allocates `cramfs_sb_info`, maps/reads the image, validates the superblock, and creates the root. File reads locate the block pointer for the folio, interpret direct/uncompressed flags or end-pointer layout, read compressed bytes, call `cramfs_uncompress_block()` unless uncompressed, zero-fill the folio tail, and mark read completion.

State and persistence: `cramfs_sb_info` stores image size, block/file counts, flags, and MTD mapping details. A small global two-buffer block cache is protected by `read_mutex`. The filesystem is read-only and has no writeback state.

Dependencies/integration: VFS, block device page cache, MTD `point/unpoint`, zlib decompression wrapper, UAPI Cramfs on-disk structs, generic read-only file ops, symlink page ops, and mmap helpers.

Risks: `read_mutex` serializes decompression and shared block buffers. On-disk pointer validation is crucial; bad block sizes over `2*PAGE_SIZE` or uncompressed over `PAGE_SIZE` fail. MTD direct mmap must avoid mapping shared tail pages. Old mkcramfs quirks are handled in inode number logic and root permissions.

Test signals: valid and invalid magic/endian images, shifted root offsets, sorted directory lookup, malformed namelen/block pointers, compressed and uncompressed blocks, holes, symlinks, special files, blockdev cache reuse, MTD direct mapping and fallback mmap, remount read-only, and statfs counts.
