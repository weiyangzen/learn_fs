# File Research: sources/block-storage/util-linux/libblkid/samples/mkfs.c

## Purpose
Example for mkfs-like programs that must avoid overwriting existing filesystems or partition tables and should query block-device topology before formatting.

## Main Components
- Opens a probe with `blkid_new_probe_from_filename()`.
- Enables partition probing while superblock probing remains enabled by default.
- Runs `blkid_do_fullprobe()`.
- Checks result values `TYPE` and `PTTYPE` to reject devices containing an existing superblock or partition table.
- Retrieves topology with `blkid_probe_get_topology()`.
- Frees the probe before exit.

## Behavior
The program exits with failure if no device argument is provided, probe creation fails, full probing errors, an existing filesystem/RAID superblock is detected, a partition table is detected, or topology cannot be read.

## Dependencies and Interactions
Uses the public libblkid low-level probing API plus util-linux `err()`/`errx()` helpers from `c.h`.

## Research Notes
The topology usage is illustrative; the sample includes a commented placeholder showing where a formatter would use fields such as alignment offset.
