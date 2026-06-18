# File Research: sources/cow-pools/nilfs-utils/include/nilfs.h

Public NILFS library API. It defines checkpoint number type, open flags, superblock update masks, layout reporting structure, option and lock helper macros, raw segment structure, and wrappers for core NILFS operations.

The API covers opening/closing a mounted or raw NILFS instance, querying mount/device/layout data, cleaner locking, reading/writing superblocks, raw segment reads, checkpoint mode changes, checkpoint and segment usage queries, GC ioctl arguments, sync, resize, allocation range, freeze/thaw, and oldest checkpoint lookup.
