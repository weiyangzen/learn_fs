<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapfile.h -->
# sources/distributed-fs/ceph-client/include/linux/swapfile.h

## Purpose

`swapfile.h` exposes architecture and generic limits for swapfile sizing and a flag describing whether migration swap entries can preserve accessed/dirty bits. It is a narrow interface between generic swap code and architecture-specific swap encoding limits.

## Important APIs, types, and functions

It declares `generic_max_swapfile_size()`, `arch_max_swapfile_size()`, global `swapfile_maximum_size`, and global `swap_migration_ad_supported`.

## Control flow

Swap activation consults generic and architecture maximum size calculations to cap usable swap offsets. Migration-entry helpers in `swapops.h` query `swap_migration_ad_supported` to decide whether to encode A/D bits in swap offsets.

## State and persistence behavior

`swapfile_maximum_size` and `swap_migration_ad_supported` are global kernel state initialized by swap/architecture setup. They persist for the boot lifetime and govern later swapon and migration-entry behavior.

## Dependencies and integration points

It integrates with `swap.h`, `swapops.h`, architecture page-table/swap encoding, and `mm/swapfile.c`.

## Risks and test signals

Risks include overestimating maximum offsets on architectures with small PTE swap fields, inconsistent A/D-bit support versus actual encoding capacity, and regressions for 32-bit pgoff architectures. Tests should validate maximum swapfile sizes across page sizes and architectures, migration entries with and without A/D preservation, and swapon rejection/truncation around limit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapfile.h -->
