# sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap.c

## Purpose
`fastmap.c` implements on-flash fastmap format sizing, attach-time fastmap parsing, pool scanning, debug self-checks, fastmap writing, invalidation, and fastmap update orchestration. Fastmap accelerates attach by persisting enough WL/EBA/volume state to avoid a full flash scan.

## Important APIs, Types, And Functions
Public functions are `ubi_calc_fm_size()`, `ubi_scan_fastmap()`, `ubi_fastmap_init_checkmap()`, `ubi_fastmap_destroy_checkmap()`, and `ubi_update_fastmap()`. Important helpers include `new_fm_vbuf()`, `add_aeb()`, `add_vol()`, `assign_aeb_to_av()`, `update_vol()`, `process_pool_aeb()`, `unmap_peb()`, `scan_pool()`, `count_fastmap_pebs()`, `ubi_attach_fastmap()`, `find_fm_anchor()`, `clone_aeb()`, `ubi_write_fastmap()`, `invalidate_fastmap()`, and `return_fm_pebs()`.

## Control Flow
Attach starts with a scan of early PEBs that populates `scan_ai->fastmap`; `find_fm_anchor()` chooses the newest fastmap superblock. `ubi_scan_fastmap()` clones candidate fastmap PEBs, reads the superblock, validates magic/version/used block count/size, reads EC and VID headers for all fastmap blocks, checks image sequence, reads fastmap payload blocks into `ubi->fm_buf`, validates CRC, then calls `ubi_attach_fastmap()`.

`ubi_attach_fastmap()` parses the serialized fastmap: free/used/scrub/erase lists, volume headers, and per-volume EBA tables. It then scans user and WL pools for changes after the fastmap was written, resolving newer duplicate LEBs with `ubi_compare_lebs()`, moving stale/unmapped PEBs to erase/free, and rejecting leaks where counted PEBs do not match expected device totals.

`ubi_update_fastmap()` refills pools and locks fastmap-related semaphores, allocates a new layout, obtains or reuses fastmap data PEBs and an anchor, writes the serialized fastmap, frees the old layout, and ensures a future anchor. On write failure it writes an invalid fastmap marker when possible; otherwise it switches UBI to read-only mode.

## State And Persistence
The on-flash format contains `ubi_fm_sb`, `ubi_fm_hdr`, two scan pools, EC entries for WL lists, volume headers, and EBA arrays. `ubi->fm_buf` is a full serialized image sized by `ubi_calc_fm_size()`. Runtime state includes `ubi->fm`, pool maximums, `fast_attach`, per-volume `checkmap` bitmaps for lazy stale-mapping validation, and debug `seen` bitmaps. Successful writes persist current WL/EBA state and pool contents; invalidation persists a fake fastmap superblock that forces next attach to full scan.

## Dependencies And Integration Points
Fastmap depends on UBI media format definitions, attach info allocators, EBA descriptors, WL pools and fastmap PEB allocation, UBI I/O helpers, CRC32, debug fastmap checks, and bad-block/image-sequence validation. `build.c` sets fastmap sizing and enables/disables it; `eba.c` uses checkmaps after fast attach; WL calls `ubi_update_fastmap()` on pool exhaustion.

## Risks
Fastmap correctness is data-safety critical because it can replace a full scan. The parser guards every serialized section against `fm_size` overflow and rejects bad magic, bad pool sizes, wrong image sequence, damaged pool PEBs, and PEB leaks. Pool scanning is required because pool PEBs may have changed after the fastmap was written. Failure to invalidate an obsolete fastmap can resurrect stale EBA/WL state, so update errors either invalidate or force read-only. Debug self-checks can be expensive but catch missed PEB accounting.

## Test Signals
Test no-fastmap fallback, bad magic/version/CRC/size handling, image sequence mismatch, pool PEB with all-FF VID becoming free, pool PEB with newer LEB replacing old mapping, stale pool mapping unmap, PEB leak detection, successful fast attach setting pool sizes and `fast_attach`, fastmap update under volume change, update failure invalidation, and read-only transition when invalidation fails.
