# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add

## Purpose
Tests clustered RAID10 `--manage --add` behavior.

## Behavior
The first scenario fails and removes one RAID10 member, zeros a replacement disk, adds it, waits for recovery, and verifies restored `UU` state. The second scenario adds an extra disk to a healthy array and verifies it becomes a spare.

## Integration Notes
This validates both replacement-add and spare-add behavior through the generic `--add` path.
