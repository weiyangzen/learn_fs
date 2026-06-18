## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-debugfs.h

### Purpose
This header exposes debugfs lifecycle and daemon-update hooks for OrangeFS.

### Important APIs, types, and functions
It declares `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`, `orangefs_prepare_debugfs_help_string()`, `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()`.

### Control flow
Module init prepares help, then calls init; module exit calls cleanup. Device ioctls call the `new_*` functions when the userspace daemon supplies debug settings.

### State and persistence behavior
No state is declared in the header. State lives in `orangefs-debugfs.c`.

### Dependencies and integration points
Includes user-pointer function signatures for ioctl paths and is included by `orangefs-mod.c` and `devorangefs-req.c`.

### Risks
The header has no include guard in this snapshot, so repeated inclusion relies on compatible duplicate declarations.

### Test signals
Build coverage should catch signature drift between device ioctl dispatch and debugfs implementation.
