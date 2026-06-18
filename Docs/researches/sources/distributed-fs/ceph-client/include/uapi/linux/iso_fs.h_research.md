# sources/distributed-fs/ceph-client/include/uapi/linux/iso_fs.h

## Purpose
`iso_fs.h` exports ISO-9660 and High Sierra filesystem on-disk structure layouts and constants.

## Important APIs, Types, and Functions
`ISODCL(from, to)` computes field widths from spec byte ranges. Structures include `iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, `hs_volume_descriptor`, `hs_primary_descriptor`, `iso_path_table`, and `iso_directory_record`. Constants identify descriptor types, standard IDs (`CD001`, `CDROM`), and block size (`ISOFS_BLOCK_SIZE` 2048).

## Control Flow
Filesystem parsers read sectors, match descriptor IDs/types, parse primary or supplementary descriptors, walk path tables, and interpret directory records. The kernel ISOFS driver uses these layouts for mount-time discovery and directory traversal.

## State and Persistence
The state represented is on-disk persistent media metadata. The header itself holds no runtime state.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/magic.h>`. It integrates with the ISOFS filesystem driver, image-building tools, forensic parsers, and boot/media tooling.

## Risks and Test Signals
Tests should cover exact packed field offsets, block-size assumptions, malformed descriptor lengths, endianness encoded in ISO fields, supplementary descriptor handling, and directory records with variable-length names.
