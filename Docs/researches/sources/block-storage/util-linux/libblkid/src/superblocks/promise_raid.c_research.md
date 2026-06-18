# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/promise_raid.c

## Scope

Detects Promise FastTrak RAID member metadata.

## Behavior

- Scans a fixed list of historical sector offsets from the end of the device.
- Requires whole-disk or regular-file probing.
- Matches the `Promise Technology, Inc.` signature and records it as the magic.

## Dependencies And Risks

- Stops when the device has fewer sectors than the next candidate offset.
- No checksum is available, so the offset list and whole-disk restriction are the main false-positive controls.
