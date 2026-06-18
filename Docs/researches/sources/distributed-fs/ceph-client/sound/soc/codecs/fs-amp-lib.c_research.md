# sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.c

## Purpose

This file is the shared firmware parser for FourSemi audio amplifier drivers. It loads a binary firmware package, verifies CRC and target device ID, parses table indexes, constructs scene descriptors, and exposes the result through `struct fs_amp_lib`.

## Important APIs, types, and functions

The exported API is `fs_amp_load_firmware()`. Internal helpers include `fs_verify_firmware()`, `fs_parse_all_tables()`, `fs_parse_scene_tables()`, `fs_get_scene_count()`, and table-specific pointer resolvers for strings, register tables, model blobs, and effect blobs. `fs_print_firmware_info()` logs project, device, and date metadata after successful parse.

## Control flow

`fs_amp_load_firmware()` validates arguments, requests the named firmware, copies it into devm memory, stores `amp_lib->hdr`, verifies the CRC over the header's `crc_size` region starting at `crc_size`, checks that the low byte of `chip_type` matches `amp_lib->devid`, parses the root index table into `amp_lib->table[]`, parses scene entries from `FS_INDEX_SCENE`, and logs metadata. Parse failures clear `amp_lib->hdr` before returning.

## State and persistence behavior

The loaded firmware copy, table pointers, scene array, scene names, and fallback scene names are devm-managed and persist for the device lifetime. The parser does not deep-copy model/effect/register tables; scene entries point into the copied firmware image. No reload or cleanup path is provided beyond devm release.

## Dependencies and integration points

It depends on Linux firmware loading, CRC16, devm allocation, and `fs-amp-lib.h` packed firmware structures. `fs210x.c` consumes the parsed scene, register, effect, and woofer tables to initialize and switch DSP scenes.

## Risks and test signals

Risks include limited bounds checking of nested offsets, trusting the root index table size, CRC range assumptions, malformed string offsets that can produce unterminated strings, and device-ID matching only against the low byte. Test with valid firmware, wrong-device firmware, corrupted CRC, out-of-range index types, zero/too-many scenes, missing optional tables, and fuzzed offsets under KASAN/KMSAN.
