# File Research: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_bitmap-switch

## Purpose
Tests bitmap policy transitions for clustered RAID10.

## Behavior
The script creates an assume-clean clustered RAID10 array, stops it on `NODE2`, switches bitmap mode from clustered to none, verifies member bitmaps disappear, switches none to internal, verifies internal bitmap creation, switches internal to none, then switches none back to clustered and reassembles on `NODE2`.

It verifies clustered bitmap metadata by checking `mdadm -X` output for `Cluster name` on all nodes.

## Integration Notes
This exercises `mdadm --grow --bitmap=` transitions and clustered bitmap visibility across nodes.
