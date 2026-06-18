# File Research: sources/block-storage/linux-dm/drivers/md/md-linear.h

## Purpose
Defines private data structures for the MD linear personality.

## Main Interfaces
- `struct dev_info`: component `md_rdev` pointer plus cumulative `end_sector`.
- `struct linear_conf`: RCU head, total `array_sectors`, copied `raid_disks`, and flexible `disks[]` array.

## Control Flow
No executable control flow. The layout supports fast binary-search mapping in `md-linear.c`.

## State And Synchronization
`linear_conf` includes `struct rcu_head` so old configurations can be freed after RCU grace periods when hot-add swaps in a new mapping.

## Integration Points
Included only by the linear personality implementation.

## Notable Behaviors
- `raid_disks` is intentionally copied into the configuration so readers can iterate the flexible array safely even if `mddev->raid_disks` changes during hot-add.

## Risks And Review Focus
- Any structure changes must preserve the flexible-array allocation pattern used by `struct_size(conf, disks, raid_disks)`.
