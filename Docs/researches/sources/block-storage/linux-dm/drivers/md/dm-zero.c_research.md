# File Research: sources/block-storage/linux-dm/drivers/md/dm-zero.c

## Scope

This file implements the small Device Mapper `zero` target: a dummy mapping that returns zero-filled data for reads and silently drops writes/discards.

## Public And Internal APIs Covered

- DM target constructor: `zero_ctr()`.
- DM target mapper: `zero_map()`.
- Module lifecycle: `dm_zero_init()` and `dm_zero_exit()`.
- Target definition: `zero_target`.

## Control Flow And Behavior

- `zero_ctr()` rejects all table arguments and advertises one discard bio so discard requests are accepted and silently consumed instead of returning unsupported-operation errors.
- `zero_map()` zero-fills normal read bios and completes them immediately.
- Readahead reads are killed with `DM_MAPIO_KILL` to avoid wasting page cache on predictable zero data.
- Writes are silently accepted and completed without forwarding to any backing device.
- Any operation other than read/write is killed.
- The target has `DM_TARGET_NOWAIT` because it does not need to sleep on backing I/O.

## State And Data Structures

- No per-target private state is allocated.
- `zero_target` declares name `zero`, version `{1, 1, 0}`, constructor, mapper, and module owner.

## Dependencies

- Device Mapper target registration and bio completion APIs.
- Block-layer helpers `bio_op()`, `zero_fill_bio()`, `bio_endio()`, and request op/flag constants.

## Risks And Invariants

- The target intentionally discards writes and discards. It is useful for tests/sinks but must not be mistaken for persistent storage.
- Readahead bios are killed rather than completed with zeros, changing behavior from normal reads to avoid cache pollution.
- Since there is no backing device, every accepted bio must be completed in `zero_map()`.
