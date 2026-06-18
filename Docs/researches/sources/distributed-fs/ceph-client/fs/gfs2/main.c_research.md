<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/main.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/main.c

## Purpose
`main.c` is the GFS2 module entry and exit file. It initializes global caches, workqueues, debugfs, quota hash/shrinker state, page pools, and filesystem type registrations, and tears them down in reverse order on module unload.

## Important APIs, types, and functions
The entry points are `init_gfs2_fs` and `exit_gfs2_fs`, wired through `module_init` and `module_exit`. Object constructors are `gfs2_init_inode_once`, `gfs2_init_glock_once`, and `gfs2_init_gl_aspace_once`. The file defines the global `struct workqueue_struct *gfs2_control_wq`; `gfs2_recovery_wq` is defined in `recovery.c` but allocated here. It initializes caches for glocks, glock address spaces, inodes, bufdata, resource groups, quota data, qadata, and transactions.

## Control Flow
Initialization sets up qstrs for `.` and `..`, initializes the quota hash table and sysfs, creates the quota LRU and glock subsystem, allocates all slab caches, registers the quota-data shrinker, creates recovery/control/freeze workqueues, creates the page mempool, registers debugfs, and registers both `gfs2` and `gfs2meta` filesystem types. Each failure label unwinds only the resources already created. Exit unregisters filesystems and debugfs, stops global workqueues, destroys the LRU, waits for pending RCU callbacks with `rcu_barrier`, destroys the page pool and caches, and uninitializes sysfs.

## State and Persistence
The file owns process-wide kernel resources, not on-disk state. Persistent filesystem state is unaffected except through registration availability. The slab constructors initialize per-object list heads, lock state, quota pointers, reservation trees, and address-space objects so later mount-time code can rely on clean invariants.

## Dependencies and Integration Points
It integrates with sysfs (`gfs2_sys_init`), glock subsystem initialization, quota shrinker setup, recovery and control workqueues used by `recovery.c` and `lock_dlm.c`, freeze workqueue used by superblock code, debugfs, the shared page mempool used by log writes, and VFS filesystem registration through `gfs2_fs_type` and `gfs2meta_fs_type`.

## Risks
Initialization order matters because later caches and workqueues depend on earlier global subsystems. Exit must wait for RCU before freeing quota-data cache objects. Workqueues must be destroyed after filesystems are unregistered and mounts have gone away. Constructor omissions can surface as list corruption or stale lock state in reused slab objects.

## Test Signals
Signals include module load/unload, failure injection at each cache/workqueue/mempool/registration step, lockdep and KASAN coverage of slab constructors, mounting after repeated module reloads, quota shrinker registration, and ensuring no global workqueue work remains after filesystem unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/main.c -->
