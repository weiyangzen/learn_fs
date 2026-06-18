# sources/distributed-fs/ceph-client/fs/ntfs/iomap.h

## Purpose
`iomap.h` is the public NTFS header for iomap integration. It declares the operation tables implemented in `iomap.c` and the direct-I/O zeroing helper used by NTFS write and allocation paths.

## Important APIs, Types, and Functions
The header exports `ntfs_write_iomap_ops`, `ntfs_read_iomap_ops`, `ntfs_seek_iomap_ops`, `ntfs_page_mkwrite_iomap_ops`, `ntfs_dio_iomap_ops`, `ntfs_writeback_ops`, and `ntfs_iomap_folio_ops`. It also declares `ntfs_dio_zero_range(struct inode *inode, loff_t offset, loff_t length)`, which zeros block-device sectors for direct-I/O allocation edge handling.

## Control Flow and State
The header does not implement control flow; it makes the NTFS iomap dispatch points visible to VFS/address-space setup code. Callers select an operation table based on read, write, seek, page-mkwrite, direct-I/O, or writeback context, and `iomap.c` owns the actual mapping and state mutation.

## State and Persistence Behavior
No state is stored here. The declared operation tables mutate persistent-related state indirectly through runlist allocation, initialized-size updates, dirty MFT records, and block zeroing in `iomap.c`.

## Dependencies and Integration Points
It includes Linux `pagemap.h` and `iomap.h`, then NTFS `volume.h` and `inode.h`. It is the narrow integration contract between NTFS inode setup and Linux iomap helpers.

## Risks
Risk is mostly API drift: changes in Linux iomap callback signatures or NTFS operation table names must be reflected here and in all users. Including both `volume.h` and `inode.h` can increase coupling; any circular include change should be checked carefully.

## Test Signals
Compile coverage from address-space operation setup is the primary signal. Runtime signals come from any NTFS read/write/direct-I/O/mmap/writeback test that exercises these exported tables.
