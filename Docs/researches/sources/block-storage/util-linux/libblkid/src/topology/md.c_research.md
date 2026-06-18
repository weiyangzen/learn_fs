# File Research: sources/block-storage/util-linux/libblkid/src/topology/md.c

## Scope

Provides Linux md RAID topology probing through md ioctls.

## Behavior

- Detects md devices by major number or driver name.
- Opens the whole disk if the probed device is a partition.
- Uses `GET_ARRAY_INFO` to read RAID level, chunk size, and disk counts.
- Adjusts effective data-disk count for RAID4/5/6 parity and exports minimum/optimal I/O sizes.

## Dependencies And Risks

- Ignores RAID levels that should not be stripe-aligned.
- Must close any auxiliary whole-disk fd.
- Optimal I/O size calculation depends on correct parity-disk deduction.
