# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add-spare

## Purpose
Tests clustered RAID10 `--manage --add-spare`.

## Behavior
The script creates a healthy clustered RAID10 array, adds one spare, verifies spare count, then repeats with an initial spare and adds a second spare. Each scenario checks RAID10 identity, bitmap state, member state, spare count, and dmesg.

## Integration Notes
This isolates explicit spare addition from replacement recovery.
