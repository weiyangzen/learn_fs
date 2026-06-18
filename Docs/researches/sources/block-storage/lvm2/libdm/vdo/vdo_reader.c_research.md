# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_reader.c

Purpose: reads enough VDO on-disk metadata from a backend device or file to discover the VDO logical block count.

Read coverage: complete file read, 302 lines.

Key responsibilities:
- Defines packed VDO metadata structures for geometry blocks, headers, version numbers, volume geometry, region records, index config, and physical-volume component config.
- Decodes little-endian metadata fields into host order.
- Opens a VDO backend path, determines its size via `BLKGETSIZE64` or file `stat`, and reads the first 4 KiB metadata block.
- Validates the VDO magic string `dmvdo001`, geometry header id, and supported geometry major versions 4 and 5.
- Computes the VDO data-region offset from region start and bio offset, then seeks to the physical-volume component block.
- Reads component version/config data, rejects unknown major versions above 41, verifies nonce consistency, and returns logical block count.

Important entry point:
- `dm_vdo_parse_logical_size(const char *vdo_path, uint64_t *logical_blocks)`

Dependencies:
- Uses libdm logging helpers and endian conversion from `lib/mm/xlate.h`.
- Uses POSIX file APIs plus Linux `BLKGETSIZE64`.

Risk and edge cases:
- The parser is deliberately simplified and only extracts selected structure members.
- It assumes 4 KiB metadata block reads and packed layout compatibility with supported VDO versions.
- Short reads, invalid magic, unsupported versions, region offsets beyond file/device size, seek errors, and nonce mismatches all fail.
- On failure, `*logical_blocks` remains zero and the function returns `0`.
- Comments indicate it was based on VDO sources and may eventually be replaced by a library.
