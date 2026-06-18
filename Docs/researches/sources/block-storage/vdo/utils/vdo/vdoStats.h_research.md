# File Research: sources/block-storage/vdo/utils/vdo/vdoStats.h

Declares the VDO stats read/write API.

Key details:
- `read_vdo_stats()` parses a buffer into `struct vdo_statistics`.
- `vdo_write_stats()` writes a stats structure to stdout.
- Includes `types.h`; the concrete stats structure is declared in `statistics.h`.

Research relevance:
- `messageStatsReader.c` implements the read side; the write side is provided elsewhere in the utility tree.
