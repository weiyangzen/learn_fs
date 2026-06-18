# File Research: sources/block-storage/bcache-tools/make.c

`make.c` implements bcache device formatting. It parses cache/backing mode, bucket size, block size, data offset, cset UUID, writeback, discard, wipe/force, label, and replacement policy. It validates power-of-two sizes, detects logical block size from block devices, rejects existing non-bcache signatures through blkid, optionally wipes existing bcache superblocks, and writes a new bcache superblock at `SB_START`.

For cache devices it computes bucket counts, first bucket, discard and replacement policy, and optionally issues whole-device `BLKDISCARD`. For backing devices it sets writethrough/writeback mode, handles non-default data offsets, integrates zoned-device offset checks, and forces zoned backing devices away from writeback. It writes zeroes to the start of the disk, writes the little-endian superblock plus CRC, fsyncs, and closes.

Notable risk: `opened` in the force/reopen path is not initialized before the retry loop.
