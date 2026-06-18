# File Research: sources/block-storage/mdadm/clustermd_tests/03r10_switch-recovery

## Purpose
Tests clustered RAID10 recovery ownership transfer between nodes.

## Behavior
The script creates RAID10 with a spare, fails one active device to start remote recovery, stops the array on `NODE1`, verifies recovery continues on `NODE2`, waits for completion, checks `UU` state, checks dmesg, and stops the remaining node.

## Integration Notes
This targets clustered md failover during recovery.
