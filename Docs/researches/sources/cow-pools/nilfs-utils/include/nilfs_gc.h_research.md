# File Research: sources/cow-pools/nilfs-utils/include/nilfs_gc.h

Public NILFS garbage collection API. It defines reclaim parameters for protected sequence, protected checkpoint number, and minimum reclaimable blocks. It also defines reclaim stats for cleaned, protected, deferred, live, defunct, and freed blocks.

The API exposes legacy `nilfs_reclaim_segment()`, enhanced `nilfs_xreclaim_segment()`, protection testing, and an inline `nilfs_assess_segment()` dry-run wrapper.
