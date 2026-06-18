# File Research: sources/block-storage/mdadm/clustermd_tests/03r1_switch-resync

## Purpose
Tests clustered RAID1 initial resync ownership transfer.

## Behavior
The script creates a non-assume-clean clustered RAID1 array, checks resync on `NODE1` and PENDING on `NODE2`, stops `NODE1`, verifies `NODE2` takes over resync, waits, reassembles on `NODE1`, and verifies RAID1 bitmap, no sync, `UU` state, and clean dmesg.

## Integration Notes
This validates clustered md resync failover for mirrors.
