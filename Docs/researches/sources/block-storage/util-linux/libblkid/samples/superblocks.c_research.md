# File Research: sources/block-storage/util-linux/libblkid/samples/superblocks.c

## Purpose
Sample program that probes a device for superblock metadata and prints all collected NAME=value results.

## Main Components
- Creates a probe from a device filename.
- Enables superblock probing.
- Requests broad superblock flags: labels, raw labels, UUIDs, raw UUIDs, type, secondary type, usage, version, magic, and filesystem info.
- Runs `blkid_do_safeprobe()`.
- Iterates all values with `blkid_probe_numof_values()` and `blkid_probe_get_value()`.

## Behavior
Safe probing returns an error on hard failure, warns when no superblock information can be gathered, and otherwise prints every collected result.

## Dependencies and Interactions
Uses public superblock flags from `blkid.h.in`. It exercises the superblock chain built into libblkid but does not touch partition or topology APIs.

## Research Notes
This is a compact example of the NAME=value interface for superblocks, as opposed to binary partition/topology objects.
