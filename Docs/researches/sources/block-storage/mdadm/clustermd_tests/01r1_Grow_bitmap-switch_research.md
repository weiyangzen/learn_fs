# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_bitmap-switch

## Purpose
Tests bitmap policy transitions for clustered RAID1.

## Behavior
The script creates an assume-clean clustered RAID1 array, switches clustered bitmap to none, none to internal, internal to none, and none back to clustered. It verifies bitmap disappearance/creation with `mdadm -X`, checks `/proc/mdstat` bitmap state, reassembles on `NODE2`, confirms `Cluster name` in bitmap output on all nodes, and verifies final state.

## Integration Notes
This is the RAID1 counterpart of the RAID10 bitmap-switch test.
