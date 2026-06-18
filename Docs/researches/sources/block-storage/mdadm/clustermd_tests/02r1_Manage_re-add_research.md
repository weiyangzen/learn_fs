# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_re-add

## Purpose
Tests clustered RAID1 re-add of a failed and removed member.

## Behavior
The script creates a clustered RAID1 array, fails and removes one member, re-adds the same device, waits for completion, verifies `UU` state, checks dmesg, and stops the array.

## Integration Notes
This exercises the optimized same-device re-add path for clustered mirrors.
