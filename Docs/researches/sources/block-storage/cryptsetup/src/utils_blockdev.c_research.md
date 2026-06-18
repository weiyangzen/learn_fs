# File Research: sources/block-storage/cryptsetup/src/utils_blockdev.c

## Purpose
Linux block-device helper functions for dm device lookup, blkid signature detection/wiping, superblock block-size probing, and blkid availability checks.

## Device Mapper Lookup
- `dm_prepare_uuid()` constructs a device-mapper UUID prefix from a crypt type and libcryptsetup UUID, removing UUID dashes.
- `lookup_holder_dm_name()` scans `/sys/dev/block/<major>:<minor>/holders`, inspects holder `dm/uuid` and `dm/name`, counts holders, and returns a matching dm name.
- `tools_lookup_crypt_device()` prepares a dm UUID prefix, stats the data device, requires a block device, and searches holders for a crypt mapping.

## Signature Detection
- `tools_detect_signatures()` initializes a blkid probe, applies a filter mode (`none`, filter LUKS, or only LUKS), prints warnings for partition and superblock signatures, and returns count/status.
- Batch mode downgrades signature warnings to debug logs.

## Signature Wiping
- `tools_wipe_all_signatures()` opens the target read-write, optionally exclusive for block devices, initializes blkid wipe probes, optionally restricts to LUKS superblocks, wipes detected signatures, and fsyncs after each wipe.

## Superblock Size
`tools_superblock_block_size()` probes the first superblock, returns the detected block size and superblock name when available, and treats empty probes as non-errors.

## Notes
- All blkid functionality is skipped when compiled without blkid support.
- Sysfs scanning intentionally handles symlinked `dm` entries and validates regular `uuid`/`name` files before reading.
