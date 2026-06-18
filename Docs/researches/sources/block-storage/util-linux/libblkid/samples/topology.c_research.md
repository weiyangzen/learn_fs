# File Research: sources/block-storage/util-linux/libblkid/samples/topology.c

## Purpose
Sample program that prints block-device topology through both libblkid’s binary topology object and NAME=value probing interface.

## Main Components
- Opens a filename-backed probe.
- Calls `blkid_probe_get_topology()` and prints alignment offset, minimum/optimal I/O size, logical/physical sector size, DAX support, and disk sequence.
- Enables topology probing and disables superblock probing.
- Runs `blkid_do_fullprobe()`.
- Prints all returned NAME=value topology values.

## Behavior
The sample uses binary topology first, then the generic value interface. Missing NAME=value topology information is reported as a warning rather than fatal failure.

## Dependencies and Interactions
Uses public topology accessors from `blkid.h.in` and the topology chain wired into libblkid’s build.

## Research Notes
The binary topology accessor can return useful data without first running `blkid_do_fullprobe()`, matching the style of the binary partition sample.
