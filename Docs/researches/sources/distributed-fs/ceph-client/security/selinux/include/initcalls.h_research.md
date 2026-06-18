## sources/distributed-fs/ceph-client/security/selinux/include/initcalls.h

### Purpose
`initcalls.h` centralizes SELinux initcall declarations so individual SELinux subsystems can be initialized in the correct boot sequence.

### Important APIs, types, and functions
It declares `init_sel_fs`, `sel_netport_init`, `sel_netnode_init`, `sel_netif_init`, `sel_netlink_init`, `sel_ib_pkey_init`, `selinux_nf_ip_init`, and `selinux_initcall`.

### Control flow
SELinux's LSM initialization references `selinux_initcall` through `.initcall_device`; subsystem init implementations can be linked without circular declarations. Individual cache init functions generally check `selinux_enabled_boot` before allocating or initializing state.

### State and persistence
This header stores no state. It coordinates initialization of selinuxfs, network caches, netlink tables, Infiniband P_Key cache, and netfilter hooks.

### Dependencies and integration points
It is included by `hooks.c`, `ibpkey.c`, and other SELinux subsystem sources that participate in boot-time setup.

### Risks
Missing or misordered init declarations can leave caches or hooks uninitialized while hook code assumes they are available.

### Test signals
Boot SELinux-enabled and disabled kernels, inspect init logs, and verify selinuxfs, netfilter hooks, net caches, netlink, and Infiniband cache setup paths execute or skip as expected.
