# File Research: sources/block-storage/mdadm/tests/00readonly

## Purpose
Regression test for switching arrays to readonly and back to read-write across metadata versions and RAID levels.

## Behavior
- Iterates metadata `0.9`, `1.0`, `1.1`, `1.2`.
- Iterates RAID levels `raid0`, `raid1`, `raid4`, `raid5`, `raid6`, `raid10`, and optionally `linear`.
- Skips RAID0 with metadata `0.9`.
- Creates a four-device clean array, verifies no sync, switches readonly with `mdadm -ro`, checks `/proc/mdstat` and sysfs `array_state`, switches back writable, and stops the array.

## Integration
Uses variables and helpers from `tests/func.sh` and the top-level `test` runner.
