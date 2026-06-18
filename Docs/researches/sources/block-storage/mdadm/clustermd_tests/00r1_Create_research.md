# File Research: sources/block-storage/mdadm/clustermd_tests/00r1_Create

## Purpose
Tests clustered RAID1 creation and assembly across two nodes.

## Behavior
The script creates clustered RAID1 arrays in normal, assume-clean, spare-device, and named-array forms. It assembles on `NODE2`, verifies resync/PENDING behavior, RAID1 identity, clustered bitmap, no active sync after wait, member state, spare count, name visibility, and clean dmesg output.

## Integration Notes
It mirrors the RAID10 creation test but targets RAID1 behavior and two-way mirror semantics.
