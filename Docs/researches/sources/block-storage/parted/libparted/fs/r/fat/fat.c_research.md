# File Research: sources/block-storage/parted/libparted/fs/r/fat/fat.c

Core FAT filesystem lifecycle and libparted operations: allocate, open, create, close, check, copy, and resize/create constraints.

Key behavior:
- `fat_alloc()` creates `PedFileSystem`, `FatSpecific`, and duplicate geometry.
- `fat_alloc_buffers()` allocates the shared 512 KiB sector buffer and one-byte-per-cluster info table.
- `fat_open()` reads/analyzes boot sector, opens FAT32 info sector, reads FAT table, allocates buffers, and collects cluster info.
- `fat_create()` computes FAT sizing, initializes geometry fields, creates FAT16 or FAT32 metadata, writes boot/info sectors and FAT tables, and clears root directory for FAT16.
- `fat_check()` recomputes expected sizes, compares duplicate FATs, checks FAT32 free-cluster info-sector value, and marks the filesystem checked.
- `fat_get_copy_constraint()` and resize/create constraints derive minimum sizes from used clusters plus directory relocation needs.
- `fat_copy()` is implemented as open then resize into the target geometry.

Important dependencies:
- Boot sector and info-sector helpers from other FAT files.
- Size math from `calc.c`.
- Table operations from `table.c`.
- Cluster classification from `count.c`.

Notable constraints:
- Only FAT16 and FAT32 are created through public helpers here.
- Resize minimum is found by binary search because FAT sizing is not directly invertible.
