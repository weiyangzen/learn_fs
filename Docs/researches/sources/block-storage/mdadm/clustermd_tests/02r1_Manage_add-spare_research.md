# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add-spare

## Purpose
Tests clustered RAID1 `--manage --add-spare`.

## Behavior
The script adds one spare to a healthy RAID1 array, then repeats with an array already containing one spare and adds a second. It verifies spare counts, RAID1 identity, clustered bitmap, `UU` member state, and dmesg cleanliness.

## Integration Notes
This validates explicit spare growth without failing members.
