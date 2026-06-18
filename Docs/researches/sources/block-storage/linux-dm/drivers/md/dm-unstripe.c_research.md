# File Research: sources/block-storage/linux-dm/drivers/md/dm-unstripe.c

## Purpose
Implements the `unstriped` device-mapper target. It exposes one logical stripe from an already striped layout by remapping linear logical sectors onto the selected stripe's physical sectors.

## Main Interfaces
- Target lifecycle: `unstripe_ctr()` and `unstripe_dtr()`.
- IO mapping: `unstripe_map()` and `map_to_core()`.
- Reporting and limits: `unstripe_status()`, `unstripe_iterate_devices()`, and `unstripe_io_hints()`.
- Module registration: `dm_unstripe_init()` and `dm_unstripe_exit()`.

## Control Flow
The constructor parses five arguments: stripe count, chunk size, stripe number, backing device path, and physical offset. It validates nonzero stripe/chunk values, opens the backing striped device, records the selected stripe offset and row width, checks that target length is chunk-aligned, and sets maximum IO length to one chunk.

For each bio, `unstripe_map()` switches the bio to the backing device and computes the backing sector. `map_to_core()` calculates the row number by dividing the logical sector by chunk size, skips over the sectors belonging to the other stripes in previous rows, adds the selected stripe's offset inside the row, then adds the physical start.

## State And Synchronization
`struct unstripe_c` stores only immutable mapping parameters and a DM device reference. No locks are needed because target configuration is fixed after construction.

## Integration Points
Registered as the `unstriped` DM target with `DM_TARGET_NOWAIT`. It uses DM device acquisition/release, target max IO length, device iteration callbacks, queue limit hints, and standard DM status output.

## Notable Behaviors
- `chunk_shift` is cached for power-of-two chunk sizes to avoid division in the map path.
- The target emits the original table arguments in `STATUSTYPE_TABLE`; info status is empty and IMA status is an empty string.
- `limits->chunk_sectors` is set to the configured chunk size.

## Risks And Review Focus
- The stripe-number validation permits the edge case `unstripe == stripes` when `stripes <= 1`; callers should be checked if changing this validation.
- `iterate_devices()` reports the target length from the physical start, although the target maps over a sparse set of sectors in the striped device.
- All arithmetic is sector-based; overflow or off-by-one changes would directly corrupt remapping.
