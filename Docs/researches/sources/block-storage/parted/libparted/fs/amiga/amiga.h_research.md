# File Research: sources/block-storage/parted/libparted/fs/amiga/amiga.h

Defines the Amiga `PartitionBlock` layout and shared helper declarations. `PartitionBlock` mirrors Amiga RDB partition metadata: block ID, checksum fields, linked-list pointer, flags, BSTR drive name, environment vector fields, geometry fields, DOS type, boot priority, and reserved words.

Macros include `PART(pos)` for casting, bootable/nomount flag bit definitions, and declarations for `amiga_find_part()` plus the `AmigaIds` linked-list helpers used to filter expected RDB block kinds. Fields are stored in Amiga big-endian order and are converted by callers with `PED_BE*_TO_CPU`.

This header is consumed by AFFS, ASFS, APFS/PFS, and the RDB helper implementation. It does not include an include guard, so it relies on conventional single inclusion in these small C files.
