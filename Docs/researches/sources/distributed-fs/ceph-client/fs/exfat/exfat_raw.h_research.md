# sources/distributed-fs/ceph-client/fs/exfat/exfat_raw.h

## Purpose
`exfat_raw.h` defines exFAT on-disk constants and packed raw structures. It describes boot-sector layout, directory entry types, FAT special cluster values, allocation flags, file attributes, checksum modes, timestamp limits, and the union representation of every 32-byte exFAT dentry variant used by the driver.

## Important APIs, types, and functions
Key constants include boot signatures, `"EXFAT   "` filesystem name, volume flags (`VOLUME_DIRTY`, `MEDIA_FAILURE`), cluster sentinels (`EXFAT_EOF_CLUSTER`, `EXFAT_BAD_CLUSTER`, `EXFAT_FREE_CLUSTER`), first/reserved cluster constants, allocation flags (`ALLOC_POSSIBLE`, `ALLOC_FAT_CHAIN`, `ALLOC_NO_FAT_CHAIN`), dentry size and maximum directory entries, raw dentry type bytes, checksum modes, file attributes, sector/cluster limits, and timestamp bounds.

`struct boot_sector` is the packed main/backup boot sector format. `struct exfat_dentry` is a packed 32-byte dentry with union arms for file, stream, name, bitmap, upcase, volume label, vendor extension, vendor allocation, and generic secondary entries. `EXFAT_TZ_VALID` marks valid timezone offset fields.

## Control flow
There is no executable control flow. Runtime code reads these structures from buffer heads and converts little-endian fields with the kernel endian helpers. Entry classification in `dir.c`, boot validation in `super.c`, allocation in `fatent.c`/`balloc.c`, NLS upcase loading, and timestamp conversion in `misc.c` all depend on this exact raw layout.

## State and persistence behavior
Everything in this header describes persistent on-disk state. The packed layout must match the exFAT specification byte-for-byte. The driver persists file size and valid size in stream entries, timestamps and attributes in file entries, UTF-16 name fragments in name entries, allocation bitmap/upcase metadata in root-directory system entries, and volume flags in the boot sector.

## Dependencies and integration points
The header depends only on Linux integer types. It is included by all implementation files that parse or write disk data and by `exfat_fs.h` users indirectly through shared type references. It bridges block-buffer contents to higher-level exFAT in-memory structures.

## Risks and test signals
Risks are layout and interpretation bugs: missing `__packed`, incorrect little-endian conversion, raw type classification drift, timestamp range mishandling, treating reserved cluster values as valid, and incorrectly handling benign versus critical secondary entries. Tests should mount known-good images, fuzz boot sectors and dentries, verify structure sizes/offsets at build time, exercise vendor/benign secondary entries, validate timezone/timestamp bounds, and run cross-endian or sparse/static-analysis checks for endian annotations.
