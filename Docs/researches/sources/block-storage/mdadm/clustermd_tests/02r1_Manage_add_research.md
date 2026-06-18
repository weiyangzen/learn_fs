# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add

## Purpose
Tests clustered RAID1 `--manage --add` behavior.

## Behavior
The first scenario fails/removes a member, zeros a replacement, adds it, waits for recovery, and verifies restored state. The second scenario adds an extra disk to a healthy RAID1 and verifies it becomes a spare.

## Integration Notes
This is the RAID1 counterpart of the RAID10 manage-add test.
