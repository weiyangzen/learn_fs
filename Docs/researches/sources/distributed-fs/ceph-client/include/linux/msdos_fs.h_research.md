<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/msdos_fs.h

## Purpose
`msdos_fs.h` imports FAT/MS-DOS filesystem UAPI definitions and provides a kernel helper for validating FAT boot-sector media bytes.

## Important APIs, Types, and Functions
It includes `uapi/linux/msdos_fs.h` and defines `fat_valid_media(u8 media)`, accepting fixed-disk media values `>= 0xf8` and floppy marker `0xf0`.

## Control Flow and State
FAT code calls `fat_valid_media()` while parsing boot sectors or validating filesystem metadata.

## State and Persistence Behavior
No state is owned. The helper validates on-disk FAT metadata.

## Dependencies and Integration Points
It integrates with FAT filesystem parsing and UAPI FAT constants.

## Risks
Changing accepted media bytes could reject valid FAT volumes or accept corrupt metadata.

## Test Signals
Mount FAT images with common media bytes, reject invalid boot sectors, and compile FAT code using UAPI definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_fs.h -->
