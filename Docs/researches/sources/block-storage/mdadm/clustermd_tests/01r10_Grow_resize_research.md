# File Research: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_resize

## Purpose
Tests clustered RAID10 grow operations for size and chunk changes.

## Behavior
The first scenario creates RAID10 with a small explicit size, grows to max, waits for resync, shrinks back to the original size, and verifies state. The second scenario creates RAID10 with 64 KiB chunks, grows chunk size to 128 KiB, waits for reshape, then verifies chunk size, member state, and dmesg cleanliness.

## Integration Notes
The script validates grow behavior on `NODE1` while the clustered array is assembled on both nodes.
