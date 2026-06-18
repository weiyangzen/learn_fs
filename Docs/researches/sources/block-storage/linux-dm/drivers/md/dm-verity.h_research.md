# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity.h

## Purpose
Defines the shared dm-verity data structures, constants, enums, per-bio memory layout helpers, and helper prototypes used by the verity target and FEC implementation.

## Main Interfaces
- Constants and enums: `DM_VERITY_MAX_LEVELS`, `enum verity_mode`, and `enum verity_block_type`.
- Target state: `struct dm_verity`.
- Per-bio state: `struct dm_verity_io`.
- Variable-length per-bio accessors: `verity_io_hash_req()`, `verity_io_real_digest()`, `verity_io_want_digest()`, and `verity_io_digest_end()`.
- Helper prototypes: `verity_for_bv_block()`, `verity_hash()`, and `verity_hash_for_block()`.

## Control Flow
The header has no standalone runtime control flow. Its inline functions calculate addresses of variable-length fields stored immediately after `struct dm_verity_io`: ahash request, real digest, wanted digest, and the end pointer used by FEC to append its own per-bio state.

## State And Synchronization
`struct dm_verity` centralizes opened data/hash devices, dm-bufio state, crypto transform, root digest and salt, optional zero digest, block geometry, tree levels, corruption counters, error mode, verification workqueue, hash-level starts, optional FEC pointer, optional validated-block bitset, and optional signature key description.

`struct dm_verity_io` stores the parent target pointer, original bio endio, starting block, number of blocks, current bio iterator, and verification work item. Synchronization is handled by the implementation workqueue and lower-level APIs.

## Integration Points
Shared by `dm-verity-target.c`, `dm-verity-fec.c`, and signature/FEC headers. It pulls in dm-bufio, device-mapper, and crypto hash types.

## Notable Behaviors
- Per-bio layout is manual and depends on `ti->per_io_data_size` being computed by the constructor.
- `verity_io_digest_end()` is the extension point used by FEC for additional per-bio data.
- `DM_VERITY_MAX_LEVELS` is 63, matching the 64-bit hash-tree level arithmetic in the target.

## Risks And Review Focus
- Any change to `struct dm_verity_io` or the inline layout helpers must be coordinated with per-bio size and alignment calculations.
- `struct dm_verity` fields are read across IO completion/workqueue paths; lifecycle teardown must only occur after DM has stopped IO.
