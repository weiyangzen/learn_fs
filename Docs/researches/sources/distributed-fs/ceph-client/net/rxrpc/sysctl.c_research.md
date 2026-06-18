# sources/distributed-fs/ceph-client/net/rxrpc/sysctl.c

Purpose: registers `/proc/sys/net/rxrpc` tunables for RxRPC timing, connection reap, backlog, receive window, receive MTU, jumbo packet, and optional receive-delay injection parameters.

Important APIs/functions: `rxrpc_sysctl_init()` registers the static table under `init_net`, and `rxrpc_sysctl_exit()` unregisters it. The `rxrpc_sysctl_table` maps proc names to global variables such as `rxrpc_soft_ack_delay`, `rxrpc_idle_ack_delay`, `rxrpc_conn_idle_client_expiry`, `rxrpc_max_backlog`, `rxrpc_rx_window_size`, `rxrpc_rx_mtu`, and `rxrpc_rx_jumbo_max`.

Control flow: initialization calls `register_net_sysctl()` and returns `-ENOMEM` on failure. Exit unregisters only when a table header was registered. Individual sysctls use kernel min/max handlers: millisecond values use `proc_doulongvec_minmax`, jiffy-backed expiry values use `proc_doulongvec_ms_jiffies_minmax`, and integer tunables use `proc_dointvec_minmax`.

State and persistence: sysctl writes mutate global RxRPC variables at runtime; values are not persisted by this file across reboot. Bounds constants enforce minimum Rx MTU 500, backlog range 4..`RXRPC_BACKLOG_MAX - 1`, receive window <= 255, jumbo max <= `RXRPC_MAX_NR_JUMBO`, and time delays within configured ranges.

Dependencies and integration: integrates Linux sysctl infrastructure and RxRPC global tunable definitions from `ar-internal.h`. Optional `CONFIG_AF_RXRPC_INJECT_RX_DELAY` exposes `inject_rx_delay` for fault/test behavior.

Risks: global tunables affect all RxRPC users in `init_net`; there is no per-net namespace registration here. Incorrect bounds could destabilize flow control, MTU handling, or connection expiry. Runtime changes can alter behavior under active calls.

Test signals: module init/exit sysctl registration tests, proc read/write validation at min/max/out-of-range values, conversion tests for ms-to-jiffies fields, and feature-gated presence of `inject_rx_delay`.
