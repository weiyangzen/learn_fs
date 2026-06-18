# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_add

## Purpose
Tests adding RAID1 clustered mirror members through grow operations.

## Behavior
The script covers three RAID1 grow cases:
- Grow from two to three raid devices while adding a new disk.
- Grow from two active plus one spare to three active while adding another disk.
- Grow from two active plus one spare to three active without an explicit add disk, consuming the spare.

Each case waits for recovery on whichever node reports it, verifies final `UUU` state, checks dmesg, and stops the array.

## Integration Notes
The recovery may appear on either local or remote node, so the script probes `/proc/mdstat` and checks the appropriate node.
