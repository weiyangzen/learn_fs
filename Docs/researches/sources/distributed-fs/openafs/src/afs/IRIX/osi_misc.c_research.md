# sources/distributed-fs/openafs/src/afs/IRIX/osi_misc.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_misc.c

Purpose: miscellaneous IRIX support for OpenAFS, including semaphore-name formatting, optional vnode glue NUMA detection, and platform identifier export.

Important APIs/types/functions: `afs_mpservice`, `makesname`, optional `afs_init_kernel_config`, and global `afs_ipno`. Uses IRIX inventory APIs under `AFS_SGI_VNODE_GLUE`.

Control flow: `makesname` truncates prefix and decimal vnode number into `METER_NAMSZ` without relying on unavailable kernel `snprintf`. `afs_init_kernel_config` initializes once under `afs_init_kern_lock`, optionally probes CPU board inventory for IP27/IP35 NUMA systems, and sets `afs_is_numa_arch`.

State/persistence: stores one-time vnode glue initialization state, NUMA flag, and compile-time IP platform number. Semaphore names are transient initialization data.

Dependencies/integration: used by `osi_vcache.c` for named semaphores and by `osi_vfs.h` vnode-shape shims when SGI vnode glue is enabled.

Risks/test signals: semaphore names may not be unique due to length truncation; NUMA detection depends on inventory data and compile-time platform macros. Test vcache allocation on many vnode numbers, NUMA/non-NUMA IRIX systems, and repeated init calls.
