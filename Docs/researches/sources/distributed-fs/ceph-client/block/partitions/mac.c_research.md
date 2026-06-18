<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.c -->
# sources/distributed-fs/ceph-client/block/partitions/mac.c

## Purpose

`mac.c` parses Apple Partition Map disk labels. It verifies the driver descriptor in block 0, reads the partition map entries using the media block size recorded by the descriptor, publishes every valid map entry, and marks Linux RAID entries.

## Important APIs, Types, And Functions

The public entry point is `mac_partition(struct parsed_partitions *state)`. It uses `struct mac_driver_desc` and `struct mac_partition` from `mac.h`. On PowerMac builds, `mac_fix_string()` trims trailing spaces and `note_bootable_part()` is called to report the most plausible root partition.

## Control Flow

The parser reads sector 0 and requires `MAC_DRIVER_MAGIC`. It extracts the Apple block size, rejects non-power-of-two block sizes because entries could straddle unreadable sector boundaries, then reads the first partition entry. The first entry must have `MAC_PARTITION_MAGIC`; its `map_count` determines how many entries to scan, capped by `DISK_MAX_PARTS` and `state->limit`.

For each slot, the parser reads `slot * secsize`, checks the entry signature, emits start and size in 512-byte sectors, and flags `Linux_RAID` entries with `ADDPART_FLAG_RAID`. PowerMac-specific logic scores bootable PowerPC/Linux/root-like partitions and reports the best one.

## State And Persistence Behavior

No persistent kernel state is stored, except the optional PowerMac bootable partition note. The on-disk Apple Partition Map persists names, types, status bits, starts, and sizes. The parser emits transient `parsed_partitions` entries.

## Dependencies And Integration Points

It depends on `check.h`, `mac.h`, `linux/ctype.h`, endian conversion helpers, and optionally `asm/machdep.h`. Its integration is the Linux partition parser table and, on PowerMac, architecture setup code that consumes `note_bootable_part()`.

## Risks And Edge Cases

The block-size logic is the main edge case. Non-power-of-two block sizes are rejected, and entries whose structure would exceed the readable rounded-down data area return `-1`. `blocks_in_map` is unsigned in use, so the `blocks_in_map < 0` check is redundant, but the upper-bound check prevents impossible map counts. Strings from disk may not be NUL-terminated; PowerMac scoring trims before comparisons.

## Test Signals

Tests should cover absent driver magic, bad partition signature, non-power-of-two block sizes, valid maps with multiple entries, oversized map counts, RAID type detection, and PowerMac root scoring. Expected output includes ` [mac]`, correct 512-sector scaling, and a clean newline on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.c -->
