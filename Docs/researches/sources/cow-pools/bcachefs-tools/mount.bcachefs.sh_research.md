# File Research: sources/cow-pools/bcachefs-tools/mount.bcachefs.sh

## Purpose
Mount helper wrapper for bcachefs that expands a filesystem UUID into device paths.

## Behavior
- Parses mount options with `getopt`.
- Locates the first non-option positional argument as `UUID`.
- If the argument looks like a 32-hex UUID with optional dashes, scans `/proc/partitions`.
- Runs `bcachefs show-super /dev/$part` with a timeout and collects devices whose superblock output matches the UUID.
- Replaces the UUID argument with a colon-separated device list.
- Executes `mount -i -t bcachefs` with the rewritten arguments.

## Failure Modes
- Exits if UUID scan finds no matching devices.
- Prints a generic argument error when `getopt` fails.

## Dependencies
Requires bash, getopt, awk, timeout, bcachefs, and mount.
