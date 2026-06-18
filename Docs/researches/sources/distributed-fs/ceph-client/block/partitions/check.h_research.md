<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/check.h -->
# sources/distributed-fs/ceph-client/block/partitions/check.h

## Purpose
`check.h` declares the shared partition-parser interface and `struct parsed_partitions`, the intermediate container used by all partition table parsers before the core creates block-device partition objects.

## Important APIs, Types, and Functions
- `struct parsed_partitions` contains the disk, printable name, per-slot parsed range/flags/meta-info array, next/limit fields, beyond-end flag, and `seq_buf` for diagnostic output.
- `Sector` wraps a folio reference returned by `read_part_sector()`.
- `put_dev_sector()` releases the folio.
- `put_partition()` records a partition slot and appends a printable partition name.
- Parser prototypes cover Acorn, AIX, Amiga, Atari, cmdline, EFI, IBM, Karma, LDM, Mac, MSDOS, OF, OSF, SGI, Sun, SYSV68, and Ultrix.

## Control Flow
Parser implementations call `read_part_sector()` to map sector data, inspect on-disk structures, call `put_partition()` for discovered ranges, optionally fill `state->parts[n].info`, and return `1` for recognized, `0` for not recognized, or negative for read errors.

## State and Persistence Behavior
The header describes transient state. `state->access_beyond_eod` informs `core.c` whether native capacity unlock/retry may be needed. Per-partition metadata can become persistent kernel-visible sysfs/uevent state after `add_partition()` duplicates it into `bd_meta_info`.

## Dependencies and Integration Points
It depends on block device, page cache, seq_buf, and internal block definitions. It is the contract between parser files and `partitions/core.c`.

## Risks and Edge Cases
`put_partition()` silently ignores slots beyond `state->limit`, so parsers must still avoid overrunning their own local counters. Parsers must always call `put_dev_sector()` for successful reads. `state->name` is modified by `core.c` to include `p` suffix rules for disk names ending in digits.

## Test Signals
Compile all parser combinations, sector read error injection, partition-limit tests, metadata propagation tests, and folio reference leak checks validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/check.h -->
