# File Research: sources/block-storage/linux-dm/drivers/md/dm-dust.c

## Role
Implements the `dust` test target, which emulates bad blocks by failing reads for selected logical blocks and optionally failing a configured number of writes before a write clears a bad block.

## Data Model
- `struct dust_device` stores the lower device, start sector, block size, sectors-per-block mapping, rb-tree of bad blocks, count, lock, read-fail enable flag, and quiet/verbose mode.
- `struct badblock` is an rb-tree entry keyed by logical block number and stores an 8-bit remaining write-failure count.

## Target Interface
- Constructor syntax is `<device_path> <offset> <blksz>`.
- Block size must be at least 512 bytes, a power of two, and no larger than the target length or 1 GiB.
- The target maximum IO length is set to exactly one configured block.

## Runtime Messages
- `enable` and `disable` toggle failing reads/writes on listed bad blocks.
- `addbadblock <block> [write_fail_count]` inserts a bad block, with `write_fail_count` capped at 255.
- `removebadblock <block>` deletes one bad block.
- `queryblock <block>`, `countbadblocks`, `listbadblocks`, and `clearbadblocks` inspect or reset state.
- `quiet` toggles diagnostic logging.

## IO Behavior
- `dust_map()` always remaps the bio to the lower device and target-relative sector.
- When enabled, reads whose logical block appears in the rb-tree return `DM_MAPIO_KILL`.
- Writes to a listed block fail while `wr_fail_cnt` is nonzero, decrementing that count each time.
- Once the write-fail count reaches zero, a write removes the block from the badblock tree and is remapped normally.

## Important Invariants
- The rb-tree and badblock count are protected by `dust_lock`.
- Logical block conversion uses `sect_per_block_shift`, relying on the constructor’s power-of-two block size validation.
- IO splitting to a single dust block keeps read/write lookup semantics unambiguous.

## Filesystem/Storage Relevance
`dm-dust` is a deterministic media-error emulator. It is useful for testing filesystem read-error handling, repair paths, scrubbing, retries, and behavior when writes appear to repair sectors.

## Notable Risks
- The message API keeps all badblock state in memory; it is not persistent.
- Range validation compares selected block values against lower-device size after sector-to-block conversion and is intentionally simple for a test target.
