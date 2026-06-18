# File Research: sources/block-storage/mdadm/clustermd_tests/00r10_Create

## Purpose
Tests clustered RAID10 creation and assembly across two nodes.

## Behavior
The script creates clustered RAID10 arrays with normal sync, assume-clean, spare-device, and named-array variants. It assembles the array on `NODE2`, verifies resync/PENDING behavior when appropriate, checks RAID10 type, clustered bitmap presence, clean state, expected member state, spare count, name propagation, and dmesg cleanliness, then stops the array on all nodes.

## Integration Notes
It relies on `func.sh` helpers, shared variables such as `$md0`, `$dev0`-`$dev2`, `$NODE1`, `$NODE2`, and remote `ssh` execution.
