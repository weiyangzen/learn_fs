## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.h

Purpose: this header declares the Libertas debugfs lifecycle entry points.

Important APIs: `lbs_debugfs_init()` and `lbs_debugfs_remove()` manage the global root. `lbs_debugfs_init_one()` and `lbs_debugfs_remove_one()` manage per-device files using `struct lbs_private` and `struct net_device`.

Control flow and integration: module/core init calls the global initializer; device add/remove paths call the per-device functions. Removal order should mirror creation to avoid stale dentries.

State and persistence: no state is defined here. Dentry pointers live in `lbs_private` and in `debugfs.c`'s global root.

Risks and tests: prototypes must remain aligned with `debugfs.c` and main/core callers. Test signals are build coverage with debugfs enabled and clean device/module teardown.
