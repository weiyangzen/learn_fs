# File Research: sources/block-storage/mdadm/clustermd_tests/03r1_switch-recovery

## Purpose
Tests clustered RAID1 recovery ownership transfer between nodes.

## Behavior
The script creates RAID1 with a spare, fails one active device, waits for remote recovery visibility, stops `NODE1`, verifies recovery continues on `NODE2`, waits for completion, verifies `UU` state, checks dmesg, and stops `NODE2`.

## Integration Notes
This is the RAID1 counterpart of the RAID10 recovery-switch test.
