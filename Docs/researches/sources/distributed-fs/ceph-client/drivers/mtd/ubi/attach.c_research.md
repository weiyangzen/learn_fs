# sources/distributed-fs/ceph-client/drivers/mtd/ubi/attach.c

## Purpose
Implements UBI attach-time media scanning and attach information construction. It classifies every PEB, reconstructs volume/LEB mappings, handles corruptions and power-cut cases, supports Fastmap fallback, computes erase-counter statistics, and hands the result to volume table, wear-leveling, and EBA initialization.

## Important APIs, Types, and Functions
Externally used functions include `ubi_alloc_aeb()`, `ubi_free_aeb()`, `ubi_compare_lebs()`, `ubi_add_to_av()`, `ubi_add_av()`, `ubi_find_av()`, `ubi_remove_av()`, `ubi_early_get_peb()`, and `ubi_attach()`. Internal helpers include `find_or_add_av()`, `add_to_list()`, `add_corrupted()`, `add_fastmap()`, `validate_vid_hdr()`, `check_corruption()`, `scan_peb()`, `late_analysis()`, `scan_all()`, optional `scan_fast()`, `destroy_ai()`, and `self_check_ai()`.

## Control Flow
Attach allocates `struct ubi_attach_info`, optionally tries Fastmap, and otherwise scans all PEBs. `scan_peb()` skips bad blocks, reads EC headers, classifies empty/corrupt/bitflip states, validates version and image sequence, reads VID headers, handles unsupported internal volumes by compatibility policy, classifies VID corruption using data-area checks, and either adds PEBs to free/erase/corrupt/alien/fastmap lists or into per-volume RB trees. Duplicate LEBs are resolved by `ubi_compare_lebs()`, which uses sequence numbers and copy-flag data CRCs to choose the newest valid copy. After scan, `late_analysis()` rejects excessive unexpected corruption or non-UBI-looking media, unknown ECs are normalized to mean EC, self-checks may run, and `ubi_attach()` initializes volume table, WL, and EBA subsystems.

## State and Persistence
Persistent state read from flash includes EC headers, VID headers, sequence numbers, image sequence, copy flags, data CRCs, and volume metadata. Runtime attach state consists of RB trees of volumes and LEBs plus lists for free, erase, corrupted, alien, and fastmap PEBs. The path may erase PEBs early through `ubi_early_get_peb()` and `early_erase_peb()` before WL is initialized.

## Dependencies and Integration Points
The file depends on UBI I/O helpers, CRC32, RB trees, slab caches, Fastmap when enabled, volume table reading, wear-leveling init, EBA init, debug self-checks, and MTD error classification including ECC errors/bitflips.

## Risks
Attach correctness is critical: misclassifying corruption can erase recoverable data or preserve unusable PEBs. Duplicate LEB selection relies on sequence numbers and copy CRCs. Fastmap fallback must avoid attaching stale/bad maps; bad VID headers during fast scan force full scan. Erase-counter overflow and inconsistent VID headers correctly abort attach. Resource cleanup across many error paths must preserve no leaks or stale pointers.

## Test Signals
Test clean media, empty media, power-cut interrupted erase/write, duplicate LEBs, corrupted EC/VID headers, image sequence mismatches, internal volume compatibility policies, excessive corruption rejection, Fastmap valid/invalid fallback, and debug self-check paths.
