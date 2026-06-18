## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debug.h

### Purpose
This header defines OrangeFS gossip debug mask bits.

### Important APIs, types, and functions
It declares `GOSSIP_*_DEBUG` bits for superblock, inode, file, directory, utility, wait, ACL, dcache, device, namei, bufmap, cache, debugfs, xattr, init, and sysfs logging, plus `GOSSIP_NO_DEBUG`, `GOSSIP_MAX_NR`, and `GOSSIP_MAX_DEBUG`.

### Control flow
Logging call sites pass these masks to `gossip_debug()`. Debugfs and module parameters convert between strings and these bitmasks.

### State and persistence behavior
No state is stored here. The bit definitions affect runtime debug state held in `orangefs_gossip_debug_mask`.

### Dependencies and integration points
Usable from kernel and non-kernel contexts, with conditional includes and an `ARRAY_SIZE` fallback. Integrated by `orangefs-debugfs.c` and all OrangeFS logging call sites.

### Risks
Mask collisions would make debug controls misleading; the header centralizes bits to avoid that. `GOSSIP_MAX_NR` must match the highest defined bit count.

### Test signals
Debugfs `kernel-debug` writes for each keyword should toggle the corresponding mask and `debug-help` should list all keywords.
