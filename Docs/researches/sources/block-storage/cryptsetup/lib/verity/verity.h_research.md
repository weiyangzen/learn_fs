# File Research: sources/block-storage/cryptsetup/lib/verity/verity.h

## Purpose
Declares internal dm-verity handling APIs and constants.

## Key Responsibilities
- Defines maximum hash type and block-size validation macro.
- Declares superblock read/write.
- Declares activation, parameter verification, userspace verification, and hash creation.
- Declares FEC processing and size calculations.
- Declares hash offset/block calculations, UUID generation, and dump function.

## Important Details
- `VERITY_BLOCK_SIZE_OK(x)` returns true for invalid block sizes: not 512-multiple, too small, too large, or not power-of-two.
