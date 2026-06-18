# File Research: sources/block-storage/lvm2/tools/lvmdiskscan.c

## Purpose
Implements `lvmdiskscan`, which scans block devices and reports disks, partitions, and LVM physical volumes.

## Main Flow
- Resets static counters for shell reuse.
- Warns when `--lvmpartition` limits output to LVM devices.
- Calls `label_scan(cmd)` before device iteration because filters may need bcache data.
- Computes maximum device-name width for aligned output.
- Iterates devices through `dev_iter_create(cmd->filter, 0)`.
- If `lvmcache_has_dev_info(dev)` is true, prints it as an LVM physical volume.
- Otherwise, unless only LVM partitions are requested, prints ordinary device details.
- Prints totals for disks, partitions, LVM PV whole disks, and LVM PV partitions.

## Helpers
- `_get_max_dev_name_len()` iterates devices to align output columns.
- `_count()` classifies a device as disk or partition by checking whether the last character of the device name is a digit.
- `_print()` formats device name, size, and annotation.
- `_check_device()` reads device size and prints ordinary devices.

## Important Details
- The partition/disk heuristic is simple and name-based.
- Failed size reads warn and continue with size `0`.
- Static counters are reset at command start to avoid interactive shell contamination.
