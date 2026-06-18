# File Research: sources/cow-pools/nilfs-utils/lib/nilfs.c

Core `libnilfs` implementation. It defines the private `struct nilfs`, mount discovery through `/proc/mounts`, raw device opening, mounted ioctl directory opening, superblock reading, incompatible feature checks, cleaner semaphore setup, and close/accessor routines.

Most public operations are thin ioctl wrappers over the NILFS UAPI: checkpoint mode change, checkpoint info/stat, checkpoint delete, segment usage info/stat/update, vinfo, bdescs, clean segments, sync, resize, allocation range, freeze, and thaw.

Raw segment access computes segment offsets from the superblock, optionally mmap’s page-aligned device ranges, falls back to `pread()`, and returns a populated `nilfs_segment`. It also provides segment sequence reads and cached oldest checkpoint lookup.
