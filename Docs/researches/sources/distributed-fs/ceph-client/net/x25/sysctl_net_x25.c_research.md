# sources/distributed-fs/ceph-client/net/x25/sysctl_net_x25.c

Purpose: registers `/proc/sys/net/x25` runtime tunables for X.25 packet-layer timers and forwarding.

Important APIs/functions: `x25_register_sysctl()` registers the table under `init_net`; `x25_unregister_sysctl()` unregisters it. Table entries back `sysctl_x25_restart_request_timeout`, call/reset/clear request timeouts, ack holdback timeout, and `sysctl_x25_forward`.

Control flow: module init calls registration after netdevice notifier setup; module exit unregisters. Timer entries use `proc_dointvec_minmax` with 1 second to 300 second jiffy bounds; forwarding uses `proc_dointvec` without min/max.

State and persistence: sysctl writes mutate global integers used by new sockets/neighbours and forwarding decisions. Values are runtime-only and not persisted by this file.

Dependencies and integration: depends on Linux sysctl infrastructure and globals defined in `af_x25.c`. The forwarding flag gates `x25_forward_call()` use in incoming call handling.

Risks and test signals: `x25_forward` accepts any integer, so callers treat nonzero as enabled. Tests should cover table presence with `CONFIG_SYSCTL`, boundary rejection for timer values, module unload cleanup, and behavior changes for new sockets after sysctl writes.
