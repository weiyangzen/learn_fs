# sources/distributed-fs/ceph-client/net/appletalk/sysctl_net_atalk.c

Purpose: exposes AppleTalk AARP timing and retry tunables through `/proc/sys/net/appletalk`.

Important APIs, types, and functions: `atalk_table` contains four `ctl_table` entries: `aarp-expiry-time`, `aarp-tick-time`, `aarp-retransmit-limit`, and `aarp-resolve-time`. Lifecycle functions are `atalk_register_sysctl` and `atalk_unregister_sysctl`.

Control flow: registration calls `register_net_sysctl(&init_net, "net/appletalk", atalk_table)` and stores the returned header. Unregistration passes that header to `unregister_net_sysctl_table`. Time values use `proc_dointvec_jiffies`; retransmit limit uses `proc_dointvec`.

State and persistence: the sysctl values point directly at global integers defined in `aarp.c`. They persist only while the module is loaded and are init-net sysctls, not per-network-namespace state.

Dependencies and integration points: depends on `CONFIG_SYSCTL`, the sysctl core, init_net, and AARP global tunables. DDP module init/exit calls these helpers when sysctl support is compiled.

Risks: no min/max validation is defined in the table, so unreasonable values can affect timer cadence, cache lifetime, and retransmission behavior. A missing registration header would make unregister unsafe if called after failed registration, though the normal init path only calls exit after success.

Test signals: sysctl directory creation/removal, read/write conversion for jiffies-based values, behavior with zero or very large timer values, and module init unwind when sysctl registration fails.
