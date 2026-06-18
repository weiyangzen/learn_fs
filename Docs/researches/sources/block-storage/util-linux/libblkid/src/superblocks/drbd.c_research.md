# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbd.c

DRBD metadata detector for v08/v8.4 and v09. It defines compact on-disk metadata structures, recognizes clean and unclean v08 magics and v09 magic near the end of the device, and dispatches by a magic-table hint.

Both version-specific probes validate the bitmap bytes-per-bit field against DRBD’s 4 KiB bitmap block size and require the aligned padding region to be zero. They then format DRBD’s 64-bit device UUID as a hex UUID-like value and set version `v08` or `v09`.

The detector reports RAID usage because DRBD is a replicated block layer. It avoids parsing the full DRBD metadata state and focuses on robust identification from magic, geometry, padding, and device UUID fields.
