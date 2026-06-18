# File Research: sources/block-storage/linux-dm/drivers/md/bcache/bcache_ondisk.h

## Purpose
Defines bcache user-visible/on-disk metadata formats and bit encodings for btree keys, pointers, superblocks, journal entries, priority sets, UUID records, and btree bsets.

## Main Interfaces
- `struct bkey` plus bitfield helpers for pointer count, checksum type, dirty flag, size, inode, offset, device, pointer offset, and generation.
- Superblock versions, constants, `cache_sb_disk`, and in-memory `cache_sb`.
- Cache/backing-device flags for sync, discard, replacement policy, cache mode, and backing-device state.
- Magic helpers for journal, priority set, and bset structures.
- On-disk `jset`, `prio_set`, `uuid_entry`, `bset`, and obsolete `uuid_entry_v0`.

## Control Flow
The file is mostly static encoding logic. Inline helpers compute key size/bytes, move to the next variable-length key, copy key headers, identify backing-device superblocks, and compose pointer words.

## State And Synchronization
No locking. It defines persistent state consumed by mount, journal replay, btree IO, priority writing, feature negotiation, and userspace format tools.

## Integration Points
Included by both kernel implementation and UAPI-adjacent code. `bcache.h`, `bset.h`, `btree.c`, `extents.c`, and feature code depend on these field definitions.

## Notable Behaviors
- Btree keys are inode:end-offset:size records, where offset is the extent end.
- Pointers encode cache device id, sector offset, and 8-bit generation.
- Superblock disk and in-memory structs intentionally do not have identical layout.
- Feature-bearing superblock versions extend older cache/backing-device versions.

## Risks And Review Focus
- Any encoding change is an on-disk format change requiring compatibility handling.
- Bitfield macros are used for both validation and mutation, so offset/width mistakes are severe.
- Comments note future limits such as 64-bit `KEY_OFFSET()` and Y2106 time overflow fields.
