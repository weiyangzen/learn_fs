<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh

### Purpose
Prints a compact status table for AoE block devices from sysfs.

### Important APIs, Types, And Functions
Uses sysfs_dir environment override defaulting to /sys, validates $sysd/block, loops over $sysd/block/etherd* excluding partitions, reads netif and state files, prints formatted device/netif/state rows, and sorts output.

### Control Flow
It exits if sysfs is unavailable and otherwise tolerates no devices via a sentinel end word.

### State, Persistence, And Dependencies
No persistent state is changed; it reads sysfs device attributes. Depends on /bin/sh, basename, ls, grep, sed, cat, printf, sort, and AoE sysfs layout.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include backtick word splitting, unquoted paths in the for list, and limited fields compared with aoe-stat.

### Test Signals
Test signals include no sysfs, empty device list, custom sysfs_dir fixture, devices with ! in names, and partition filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh -->
