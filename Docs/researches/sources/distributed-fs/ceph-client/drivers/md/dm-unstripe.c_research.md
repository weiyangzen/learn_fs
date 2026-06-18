# sources/distributed-fs/ceph-client/drivers/md/dm-unstripe.c

## Purpose
`dm-unstripe.c` implements the `unstriped` device-mapper target. It exposes one selected stripe from an already-striped layout as a linear virtual device by translating virtual sectors to the corresponding sectors on a backing striped device.

## Important APIs, Types, And Functions
- `struct unstripe_c` stores the backing `dm_dev`, physical start offset, total stripes, selected stripe, computed unstripe width/offset, chunk size, and optional power-of-two chunk shift.
- `unstripe_ctr()` parses target arguments: `<number of stripes> <chunk size> <stripe #> <dev_path> <offset>`.
- `map_to_core()` computes the backing sector by finding the stripe row and adding skipped stripe widths plus selected-stripe offset.
- `unstripe_map()` sets the bio device and translated sector.
- `unstripe_status()`, `unstripe_iterate_devices()`, and `unstripe_io_hints()` provide table output, underlying-device reporting, and chunk hints.

## Control Flow
Constructor validation checks argument count, stripe count, chunk size, stripe number, backing device open, offset parse, target length divisibility by chunk size, and max I/O length setup. It precomputes `unstripe_offset = unstripe * chunk_size`, `unstripe_width = (stripes - 1) * chunk_size`, and `chunk_shift` for power-of-two chunk sizes. Mapping gets the target-relative sector, divides by chunk size to get the row, adds the width skipped for other stripes in prior rows, then adds selected stripe offset and physical start.

## State And Persistence Behavior
The target has only table/runtime state in `struct unstripe_c`; it persists no metadata. Status table output reconstructs constructor arguments.

## Dependencies And Integration Points
It integrates with DM target registration through `module_dm(unstripe)`, uses `dm_get_device()`/`dm_put_device()`, `dm_target_offset()`, `dm_set_target_max_io_len()`, and queue limits. It depends on block-layer bio remapping and DM table modes.

## Risks
- The stripe number validation allows `uc->unstripe == uc->stripes` when `stripes > 1` because it checks `>` rather than `>=`; valid stripe indexes appear to be zero-based from the offset formula.
- Arithmetic overflow should be considered for very large target lengths, chunk sizes, or stripe counts.
- The target requires length divisible by chunk size but does not require the selected stripe to be within a stricter zero-based range.

## Test Signals
Test constructor reject paths, non-power-of-two and power-of-two chunk mapping equivalence, boundary sectors at chunk transitions, table status roundtrip, iterate-devices range, queue chunk hints, and stripe index equal to stripe count behavior.
