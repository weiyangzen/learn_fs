# File Research: sources/block-storage/util-linux/libblkid/src/topology/dm.c

## Scope

Provides legacy device-mapper topology probing via `dmsetup`.

## Behavior

- Detects device-mapper devices by major number/driver name.
- Finds `dmsetup` in standard sbin paths, forks it as `dmsetup table -j <maj> -m <min>`, and parses striped table output.
- Exports minimum I/O size as stripe size and optimal I/O size as stripe width.

## Dependencies And Risks

- Used as a fallback for systems lacking sysfs topology.
- Drops permissions before executing external helper.
- Only recognizes the simple `striped` table format parsed by `fscanf()`.
