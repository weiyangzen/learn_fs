# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_resize

## Purpose
Tests clustered RAID1 size grow and shrink.

## Behavior
The script creates a clustered RAID1 array with an explicit small size, grows it to max, waits for resync, shrinks it back to the original size, verifies no sync is active, checks final state and dmesg, and stops the array.

## Integration Notes
This focuses on size changes only; RAID1 has no chunk reshape path here.
