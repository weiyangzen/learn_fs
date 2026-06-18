# File Research: sources/block-storage/vdo/utils/vdo/blockMapUtils.h

Declares the block-map inspection API used by VDO diagnostic utilities.

Key details:
- Defines `MappingExaminer`, a callback over block-map slot, tree height, PBN, and mapping state.
- Exposes whole-map traversal via `examineBlockMapEntries()`.
- Exposes targeted lookup helpers `findLBNPage()` and `findLBNMapping()`.
- Exposes `readBlockMapPage()` for direct page reads with nonce/PBN validation.

Dependencies:
- Pulls in `encodings.h`, `physicalLayer.h`, and `userVDO.h`, so callers operate on decoded VDO state and abstract physical I/O.
