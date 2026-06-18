# File Research: sources/block-storage/linux-dm/drivers/md/raid0.c

## Purpose
Implements the Linux MD RAID0 personality: striped request mapping, uneven-device multi-zone layout construction, discard splitting, metadata-free array sizing/status, and takeover from selected redundant personalities.

## Main Interfaces
- Personality registration: `raid0_personality`, `raid0_init()`, `raid0_exit()`.
- Configuration/lifetime: `create_strip_zones()`, `raid0_run()`, `raid0_free()`, `free_conf()`, `dump_zones()`.
- Request mapping: `raid0_make_request()`, `raid0_handle_discard()`, `find_zone()`, `map_sector()`.
- Array properties: `raid0_size()`, `raid0_status()`, `raid0_quiesce()`.
- Takeover paths: `raid0_takeover()`, `raid0_takeover_raid45()`, `raid0_takeover_raid10()`, `raid0_takeover_raid1()`.

## Control Flow
`raid0_run()` validates that a chunk size exists and no bitmap is configured, initializes MD accounting biosets, builds or reuses `mddev->private`, configures queue limits around chunk-sized requests, stacks component queue limits, sets array sectors from rounded component sizes, dumps the zone map for debugging, and registers integrity metadata.

`create_strip_zones()` rounds each component size down to a chunk boundary, counts unique post-rounding sizes as strip zones, selects the RAID0 multi-zone layout, validates slot coverage, allocates `strip_zone[]` and the flattened per-zone `devlist`, then builds zone boundaries. Zone 0 contains all devices up to the smallest device size; later zones contain only devices that extend beyond the previous zone's device offset.

`raid0_make_request()` handles flushes through the MD core, routes discards to RAID0-specific discard expansion, splits normal bios at chunk boundaries, accounts non-md bios, locates the logical strip zone, maps the sector using either original or alternate multi-zone semantics, checks for a broken target, remaps the bio to the component device plus `data_offset`, applies write-same/write-zeroes validation, and submits it.

`raid0_handle_discard()` first splits a discard that crosses a strip zone. It then converts the logical range into per-disk ranges for each device participating in the zone and calls `md_submit_discard_bio()` for each non-empty component span before completing the original bio.

Takeover helpers validate source-specific preconditions, rewrite `mddev` level/layout/chunk/disk-count fields, force a clean recovery checkpoint, clear unsupported RAID0 flags, and create a new RAID0 strip-zone configuration.

## State And Synchronization
`mddev->private` points to `struct r0conf`, which owns `strip_zone[]`, `devlist`, zone count, and selected layout. RAID0 has no private thread and `raid0_quiesce()` is empty; normal suspension and lifecycle coordination is handled by the MD core. Request-side state is read without additional RAID0-local locking, so configuration must be stable while the personality is active.

## Integration Points
Depends on MD core APIs for personality registration, bitmap rejection, accounting biosets, flush handling, write-same/write-zeroes checks, broken-device detection, queue/integrity setup, and capacity updates. Uses Linux block APIs for bio splitting/chaining, remap tracing, discard capability checks, and queue limit stacking. Includes `raid5.h` for RAID4/5 layout constants used by takeover validation.

## Notable Behaviors
- Multi-zone RAID0 assembly requires an explicit layout when component sizes differ; otherwise it refuses assembly and asks for `raid0.default_layout` 1 or 2.
- The original and alternate layouts differ only for multi-zone arrays; single-zone arrays force `RAID0_ORIG_LAYOUT`.
- `raid0_size()` sums each component size rounded down to a chunk multiple and warns if called as a generic reshape size function.
- Queue discard is enabled if any member supports discard, while per-target discard behavior is delegated to `md_submit_discard_bio()`.
- Takeover from RAID1 collapses to one active disk and chooses the largest chunk size up to 64 KiB that evenly divides the array and is at least `PAGE_SIZE`.

## Risks And Review Focus
- Multi-zone layout selection is compatibility-sensitive because Linux 3.14 changed mapping behavior for uneven RAID0 arrays; wrong layout selection silently changes data placement.
- `create_strip_zones()` mutates `rdev->sectors` by rounding down to chunk size, so callers must not expect the original component sector count afterwards.
- Normal I/O is split only at chunk boundaries before zone mapping; zone-boundary correctness depends on the relationship between chunk-aligned zone construction and `find_zone()`.
- Discard mapping fans out one logical discard into per-disk discards and manually adjusts zone-relative offsets; off-by-one errors here would discard wrong component sectors.
- Takeover paths alter live `mddev` geometry and unsupported flags before returning the private config, so failed or partial takeover paths require careful MD-core cleanup.
