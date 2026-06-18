# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_re-add

## Purpose
Tests clustered RAID10 re-add of a recently failed and removed member.

## Behavior
The script creates a clustered RAID10 array, fails and removes one device, re-adds the same device, waits, verifies final `UU` state, checks dmesg, and stops the array. A comment notes that even non-clustered arrays may avoid a visible sync job for this re-add path.

## Integration Notes
This targets mdadm's re-add optimization and clustered metadata handling.
