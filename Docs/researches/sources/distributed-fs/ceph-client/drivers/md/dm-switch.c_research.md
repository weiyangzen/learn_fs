# sources/distributed-fs/ceph-client/drivers/md/dm-switch.c

## Purpose
Implements the `switch` DM target, which maps many fixed-size regions to one of many paths using a compact in-memory table and supports runtime remapping through target messages.

## Important APIs, Types, And Functions
`struct switch_path` stores an underlying device and start sector. `struct switch_ctx` stores path count, region size, number of regions, bit-packing geometry, vmalloc-backed region table, and path array. Key functions are `switch_ctr()`, `switch_map()`, `process_set_region_mappings()`, `switch_message()`, `switch_prepare_ioctl()`, and `switch_iterate_devices()`.

## Control Flow
Constructor parses path count, region size, zero optional args, and device/offset pairs; sets max IO length to region size; allocates a packed region table; initializes mappings round-robin; and sets one discard bio. Mapping divides offset by region size, reads the packed path number with `READ_ONCE()`, falls back to path 0 if invalid, and remaps to the selected path. `set_region_mappings` messages update entries using compact hex assignments and repeat syntax.

## State And Persistence
The region table is volatile memory. Runtime remaps are not persisted. Updates are in-place and serialized per message, while IO can concurrently read table slots.

## Dependencies And Integration Points
Depends on DM target APIs, message dispatch, vmalloc, bit packing, and device iteration. Registered with `module_dm(switch)`.

## Risks
Concurrent readers may observe torn slot updates on weak architectures, hence invalid path fallback. Message parsing must reject malformed input and avoid overflow. Very large region tables require careful sizing.

## Test Signals
Test initial round-robin mapping, explicit and repeat `set_region_mappings`, invalid messages, concurrent IO during remap, discard routing, ioctl forwarding for sector-0 path, and table/status output.
