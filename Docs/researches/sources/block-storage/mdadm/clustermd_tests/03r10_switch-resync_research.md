# File Research: sources/block-storage/mdadm/clustermd_tests/03r10_switch-resync

## Purpose
Tests clustered RAID10 resync ownership transfer between nodes.

## Behavior
The script creates a non-assume-clean clustered RAID10 array, confirms resync on `NODE1` and PENDING on `NODE2`, stops `NODE1`, verifies resync continues on `NODE2`, waits, reassembles on `NODE1`, and verifies clean RAID10 bitmap state.

## Integration Notes
This covers initial resync failover rather than replacement recovery.
