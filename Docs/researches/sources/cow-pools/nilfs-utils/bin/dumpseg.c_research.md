# File Research: sources/cow-pools/nilfs-utils/bin/dumpseg.c

Implements `dumpseg`, a raw segment inspection command. It accepts `[DEVICE|NODE] SEGNUM...`, opens NILFS raw storage with `NILFS_OPEN_RAW | NILFS_OPEN_SRCHDEV`, tries to enable mmap reads, then reads each requested segment with `nilfs_get_segment()`.

The file walks segment summaries through `nilfs_psegment`, `nilfs_file`, and `nilfs_block` iterators from `segment.h`. It prints segment sequence, next segment, partial segment creation time, file info records, and either virtual block descriptors or real DAT block descriptors.

It contains detailed diagnostics for malformed segment summaries: alignment, oversized partial segment, oversized header, oversized summary, file block count mismatch, and finfo/binfo overrun.
