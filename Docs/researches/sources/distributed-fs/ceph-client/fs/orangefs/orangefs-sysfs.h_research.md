## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-sysfs.h

### Purpose
This header declares the OrangeFS sysfs lifecycle functions.

### Important APIs, types, and functions
- `orangefs_sysfs_init()` creates the `/sys/fs/orangefs` hierarchy.
- `orangefs_sysfs_exit()` releases it.

### Control flow
`orangefs-mod.c` calls init during module load after debugfs setup and calls exit during failure unwind and module unload.

### State and persistence behavior
No state is stored in the header. Sysfs kobject state is private to `orangefs-sysfs.c`.

### Dependencies and integration points
Included by `orangefs-mod.c`; paired directly with `orangefs-sysfs.c`.

### Risks
There is no include guard in this two-line header, but duplicate extern declarations are harmless in normal C compilation.

### Test signals
Build coverage and module load/unload should confirm the declarations match the implementation and no sysfs symbols are missing.
