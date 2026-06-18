# File Research: sources/block-storage/parted/libparted/fs/r/fat/fatio.c

Thin I/O adapter over `PedGeometry` for FAT fragments and clusters.

Key behavior:
- Converts fragment or cluster numbers to filesystem-relative sectors.
- Reads/writes one or more fragments.
- Reads/writes one or more clusters.
- Provides sync-write variants that call `ped_geometry_sync()` after the write.

Important dependencies:
- Mapping helpers from `calc.c`.
- FAT geometry fields from `FatSpecific`.

Constraints:
- Asserts fragment/cluster ranges before I/O.
- All sector math assumes the FAT implementation’s 512-byte sector model.
