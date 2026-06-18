# Research: sources/distributed-fs/ceph-client/net/llc/sysctl_net_llc.c

## sources/distributed-fs/ceph-client/net/llc/sysctl_net_llc.c

Purpose: Registers sysctl entries for LLC2 timeout tuning and an LLC station sysctl directory.

Important APIs/types/functions: Provides `llc_sysctl_init()` and `llc_sysctl_exit()`. The `llc2_timeout_table` exposes `ack`, `busy`, `p`, and `rej` entries backed by the global timeout integers defined in `llc_conn.c`, using `proc_dointvec_jiffies`.

Control flow: Init registers `net/llc/llc2/timeout` with the timeout table and `net/llc/station` as an empty table. If either registration fails, init calls exit to unregister any partial state. Exit unregisters non-NULL headers and clears them.

State and persistence behavior: Persistent state is the two `ctl_table_header *` handles and the global timeout variables modified through sysctl. These values affect future timer setup and expiration lengths used by LLC connection sockets.

Dependencies and integration points: Depends on init_net sysctl registration, LLC timeout globals from `<net/llc.h>`, and the connection initialization path that copies sysctl values into per-socket timer `expire` fields.

Risks and test signals: The sysctls are global to `init_net` rather than per network namespace in this file. Tests should cover registration failure unwind, read/write of jiffies-backed values, module unload cleanup, and confirming new sockets inherit updated timeout values while existing timer structures keep their configured expires unless reset.
