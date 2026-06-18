# sources/distributed-fs/ceph-client/fs/ntfs/ntfs.h

## Purpose
`ntfs.h` is a central include for common NTFS constants, conversion macros, inline helpers, external operation tables, global slab caches, and cross-module function declarations.

## Important APIs and Types
The header defines default preallocation and compression constants, byte/cluster/MFT/page/sector conversion macros and inline equivalents, filesystem constants such as `NTFS_BLOCK_SIZE`, `NTFS_SB_MAGIC`, and maximum name/label lengths, case-sensitivity constants, `NTFS_SB()`, `struct option_t`, external operation tables, slab caches, and declarations for compression, superblock flags, MST, Unicode, ioctl, upcase, and block-device I/O functions. It also defines `ntfs_ffs()`.

## Control Flow and State
There is no runtime state machine in this header, but the conversion helpers encode important layout assumptions: cluster size bits/masks, MFT record size bits, page size, and superblock block size drive mapping between logical NTFS objects and Linux page or block addresses.

## Dependencies and Integration
Most NTFS source files include this header to reach `volume.h`, `layout.h`, `inode.h`, logging format, VFS operation exports, and common conversions. MFT, runlist, namei, MST, object-id, quota, and reparse code all depend on declarations or constants here.

## Risks
The macro and inline conversion helpers overlap; drift between them would be dangerous. Several conversions assume bit-shiftable power-of-two sizes configured in `ntfs_volume`. Invalid volume geometry can cascade into wrong folio, cluster, and sector calculations. Central external declarations can hide stale APIs until link time.

## Test Signals
Geometry tests should validate conversions for small and large cluster sizes, MFT records smaller/equal/larger than a page, block sizes different from 512 bytes, and compression cluster constraints. Build tests should catch declaration drift against implementations.
