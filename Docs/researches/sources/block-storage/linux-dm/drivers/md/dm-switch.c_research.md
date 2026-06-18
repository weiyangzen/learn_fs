# File Research: sources/block-storage/linux-dm/drivers/md/dm-switch.c

## Purpose
Implements the `switch` DM target: a dynamic region-to-path mapper intended for many fixed-size regions where the mapping is arbitrary and cannot be compactly represented by a simple stripe target.

## Main Objects
- `struct switch_path`: backing DM device and starting offset.
- `struct switch_ctx`: target context with path list, region size, region count, bit-packing metadata, and packed `region_table`.
- `region_table_slot_t`: machine-word storage for multiple region table entries.

## Target Surface
Registers target:
- Name: `switch`
- Version: `{1, 1, 0}`
- Feature: `DM_TARGET_NOWAIT`
- Supports map, message, status, prepare_ioctl, and iterate_devices.

## Control Flow
- `switch_ctr()` parses `<num_paths> <region_size> <num_optional_args> [optional_args] [<dev_path> <offset>]+`.
- `alloc_region_table()` calculates:
  - number of regions from target length and region size,
  - bits needed per path number,
  - entries per machine-word slot,
  - vmalloc-backed packed table storage.
- `initialise_region_table()` fills the table round-robin across paths.
- `switch_map()` converts a bio sector to a region, reads the path number, remaps the bio to that path plus offset, and returns `DM_MAPIO_REMAPPED`.
- `switch_message()` accepts only `set_region_mappings`, serialized by a static mutex.
- `process_set_region_mappings()` parses compact hex mapping updates:
  - `<region>:<path>`
  - `:<path>` for next region
  - `R<cycle_length>,<num_write>` to repeat previous mapping cycles.

## Data Structure Details
- Region entries are bit-packed into `unsigned long` slots.
- Reads use `READ_ONCE()`; writes update a full slot without explicit map-side locking.
- If a non-atomic torn read produces an invalid path number, mapping falls back to path 0.

## Dependencies
- DM argument parsing helpers.
- `vmalloc` for large region tables.
- Block bio remapping.
- Fast table-based hex parsing.

## Notable Behaviors
- Discards use one target bio because sending UNMAP down any path is considered sufficient.
- `prepare_ioctl()` passes ioctls through to the path for sector 0 only if the target exactly covers the underlying device size from that offset.
- Status table output prints only path definitions, not the current region table contents.

## Risk and Test Focus
- Packed table writes are not transactional across concurrent map reads; invalid torn reads are mitigated only by fallback to path 0.
- Message parser is performance-oriented and strict; malformed repeat/cycle updates should be covered.
- Very large region/path counts rely on overflow checks in `alloc_region_table()`.
