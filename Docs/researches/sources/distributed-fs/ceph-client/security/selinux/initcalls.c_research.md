<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/initcalls.c -->
# sources/distributed-fs/ceph-client/security/selinux/initcalls.c

## Purpose
Provides the device-initcall style SELinux initialization aggregator used by the LSM definition. It centralizes selinuxfs, network label caches, netlink notifications, optional InfiniBand, and optional netfilter setup.

## Important APIs, Types, and Functions
The single exported initialization routine is `selinux_initcall()`. It invokes `init_sel_fs()`, `sel_netport_init()`, `sel_netnode_init()`, `sel_netif_init()`, `sel_netlink_init()`, optional `sel_ib_pkey_init()`, and optional `selinux_nf_ip_init()`.

## Control Flow
Initialization is sequential. Each sub-init return is captured in `rc_tmp`; the first nonzero error is preserved in `rc`, but later init routines still run. Compile-time feature guards include InfiniBand and netfilter only when configured.

## State and Persistence
The file itself owns no state. It causes persistent state to be created in subordinate modules: selinuxfs registration and kernel mount, network SID caches, netdevice notifier registration, netlink socket creation, and feature-specific hook state.

## Dependencies and Integration Points
Depends on `initcalls.h` declarations and Linux initcall ordering. This is the bridge between SELinux LSM registration and the separate subsystems that cannot be initialized solely from policy load.

## Risks
Because initialization continues after failures, later modules may start even if earlier interfaces like selinuxfs failed. There is no rollback for partially initialized subsystems in this file. Panic behavior is delegated to sub-inits such as netlink creation.

## Test Signals
Boot with SELinux enabled and disabled, verify `/sys/fs/selinux` and selinuxfs mount availability, netlink event socket creation, network cache initialization, and configs with InfiniBand or netfilter toggled. Fault-injection tests should confirm the first error is returned while later init attempts still run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/initcalls.c -->
