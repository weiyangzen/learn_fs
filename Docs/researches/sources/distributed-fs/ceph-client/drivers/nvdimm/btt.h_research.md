# sources/distributed-fs/ceph-client/drivers/nvdimm/btt.h

## Purpose
`btt.h` defines the on-media and in-memory data structures for the NVDIMM Block Translation Table implementation. It captures the BTT arena superblock layout, log entry format, map-entry bit encoding, free-list entries, and the `struct btt` / `struct arena_info` runtime handles consumed by `btt.c` and validated by `btt_devs.c`.

## Important APIs, Types, And Constants
Key constants include `BTT_SIG`, `MAP_TRIM_MASK`, `MAP_ERR_MASK`, `MAP_LBA_MASK`, `MAP_ENT_NORMAL`, arena min/max sizes, `BTT_DEFAULT_NFREE`, and `LOG_SEQ_INIT`. Macros `ent_lba()`, `ent_e_flag()`, `ent_z_flag()`, `set_e_flag()`, and `ent_normal()` abstract map-entry encoding.

`struct log_entry` and `struct log_group` define four 16-byte log slots per lane, with two real entries and two padding entries. The header documents both legacy and corrected padding layouts. `struct btt_sb` is the 4 KiB arena info block persisted twice per arena. `struct free_entry` tracks the volatile lane free block, sub-slot, sequence, and error state.

`struct arena_info` records arena geometry, offsets, free-list/RTT/map-lock pointers, flags, and valid log indices. `struct btt` records the gendisk, arena list, namespace/device references, LBA geometry, region, initialization state, arena count, and badblocks source.

The exported declarations are `nd_btt_arena_is_valid()` and `nd_btt_version()`.

## Control Flow
This header does not execute logic, but its layout drives BTT control flow. `btt.c` uses `struct btt_sb` to discover or create arenas, `struct log_group` to recover interrupted writes, `struct free_entry` to select per-lane replacement blocks, and `arena_info` offsets to translate logical LBAs to namespace byte offsets.

The log-format comment is operational: startup scans log groups to infer whether slots `(0,1)` or `(0,2)` contain active entries, then all subsequent log reads/writes use the detected `arena->log_index[]`.

## State And Persistence Behavior
`struct btt_sb` is persistent media state. It includes BTT UUID, parent namespace UUID, geometry, flags, arena-relative offsets to data/map/log/backup info block, and a checksum. `struct log_entry` persists transaction state for map updates. `struct arena_info` and `struct btt` are volatile state reconstructed from those media structures at attach time.

The map-entry bit convention is easy to misread: normal initialized entries are represented with both top bits set, while all-zero means initial identity. Error and trim flags are encoded inversely through helper logic in `btt.c`.

## Dependencies And Integration Points
The header depends only on Linux basic types but semantically depends on `ND_MAX_LANES` from `nd.h` through `BTT_DEFAULT_NFREE` once included in implementation context. It is included by BTT core code, BTT device code, and claim code for checksum size assertions and BTT personality operations.

## Risks And Edge Cases
Any change to `struct btt_sb`, `struct log_entry`, or flag constants is an on-media format change. The 4 KiB size and checksum position are asserted elsewhere, so padding must remain stable. The legacy log padding compatibility note is essential: removing it would strand old BTT layouts. The `MAP_LBA_MASK` and top-bit flags assume 32-bit map entries and constrain maximum internal LBAs.

## Test Signals
Compile-time assertions in `claim.c` cover 4 KiB generic superblock compatibility. Runtime tests should validate checksum compatibility, old/new log padding detection, arena size boundaries, parent UUID matching, and correct interpretation of normal, trim, error, and initial map states.
