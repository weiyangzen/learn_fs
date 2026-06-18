# File Research: sources/block-storage/linux-dm/drivers/md/dm-stripe.c

## Purpose
Implements the `striped` DM target, mapping logical sectors across multiple underlying devices using fixed-size stripes.

## Main Objects
- `struct stripe`: one backing device, its physical start sector, and error counter.
- `struct stripe_c`: target context with stripe count, stripe width, chunk size, shift optimizations, event work, and flexible stripe array.

## Target Surface
Registers target:
- Name: `striped`
- Version: `{1, 6, 0}`
- Features: `DM_TARGET_PASSES_INTEGRITY | DM_TARGET_NOWAIT`
- Supports map, end_io, status, iterate_devices, io_hints, and DAX direct access/zero-page when enabled.

## Control Flow
- `stripe_ctr()` parses `<number of stripes> <chunk size> [<dev_path> <offset>]+`, validates divisibility of target length by stripe count and chunk size, opens each device, configures split length and multi-bio counts for flush/discard/secure erase/write-same/write-zeroes.
- `stripe_map_sector()` computes target stripe and per-device sector from a logical sector, using shifts when stripe count or chunk size is power-of-two.
- `stripe_map()` handles:
  - flush fan-out by `target_bio_nr`,
  - discard/secure erase/write zeroes/write same by remapping only the range that hits the selected stripe,
  - normal I/O by direct stripe-sector calculation.
- `stripe_end_io()` increments per-device error counters and schedules a table event until a threshold is reached.
- `stripe_dtr()` releases devices, flushes event work, and frees context.

## DAX Path
When `CONFIG_FS_DAX` is enabled:
- `stripe_dax_pgoff()` maps page offsets to the correct stripe device and page offset.
- `stripe_dax_direct_access()` and `stripe_dax_zero_page_range()` pass through to the selected DAX device.

## Dependencies
- DM target/device APIs.
- Block bio operations and queue limits.
- Optional DAX APIs.
- Workqueue event notification via `dm_table_event()`.

## Notable Behaviors
- `iterate_devices()` reports each stripe over `stripe_width`.
- `io_hints()` sets `io_min` to chunk size and `io_opt` to chunk size multiplied by number of stripes.
- Error status marks stripes as `A` or `D` based on error count.

## Risk and Test Focus
- Sector math differs for power-of-two and non-power-of-two parameters; both need coverage.
- Range-remapping operations must correctly return empty subranges for stripes not touched by a discard-like bio.
- Error accounting identifies devices by major:minor string; test stacked or aliased devices carefully.
