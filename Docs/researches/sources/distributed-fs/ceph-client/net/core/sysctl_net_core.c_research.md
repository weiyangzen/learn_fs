# sources/distributed-fs/ceph-client/net/core/sysctl_net_core.c

## Purpose
This file registers `/proc/sys/net/core` sysctls for global and per-network-namespace network core tuning. It exposes socket buffer limits, backlog and NAPI budgets, RPS/RFS controls, flow limiting, BPF JIT controls, busy polling, timestamp behavior, qdisc defaults, tunnel inheritance policy, and several static-key backed toggles.

## APIs, Types, and Functions
The main tables are `net_core_table[]` for global core sysctls and `netns_core_table[]` for per-netns sysctls. Custom handlers include `dump_cpumask()`, `rps_default_mask_sysctl()`, `rps_sock_flow_sysctl()`, `flow_limit_cpu_sysctl()`, `flow_limit_table_len_sysctl()`, `set_default_qdisc()`, `proc_do_dev_weight()`, `proc_do_rss_key()`, `proc_do_skb_defer_max()`, `proc_dointvec_minmax_bpf_enable()`, `proc_dointvec_minmax_bpf_restricted()`, and `proc_dolongvec_minmax_bpf_restricted()`. Netns registration is handled by `sysctl_core_net_init()`, `sysctl_core_net_exit()`, and `sysctl_core_init()`. Boot parameter parsing is in `fb_tunnels_only_for_init_net_sysctl_setup()`.

## Control Flow, State, and Persistence
At `fs_initcall`, the global table is registered for `init_net`, and a pernet subsystem registers per-net tables. Non-init netns receive a duplicated `netns_core_table`; early per-net entries are pointer-adjusted from `init_net` to the target `struct net`, while buffer limit/default entries are made read-only outside init net. RPS and flow-limit writes allocate or free CPU masks/tables under mutexes and publish via RCU or release stores. BPF JIT writes are capability-gated and enforce config-specific min/max behavior. Device weight writes recompute hotdata receive/transmit weights from base weight and biases.

Persistent state includes global exported `sysctl_fb_tunnels_only_for_init_net` and `sysctl_devconf_inherit_init_net`, `net_hotdata` tunables, per-net `net->core` sysctl fields, RPS masks/tables, flow-limit per-CPU objects, static keys for RPS/RFS and skb defer disabling, and sysctl header pointers stored in `net->core.sysctl_hdr`.

## Dependencies and Integration
Depends on proc sysctl infrastructure, net namespaces, RPS/RFS, flow limit, softnet data, BPF JIT globals, packet scheduler default qdisc helpers, netdevice RSS key, busy poll variables, socket buffer globals from `sock.c`, static key sysctl handling, and boot `__setup`. It directly influences send/receive buffer bounds, backlog processing, CPU steering, timestamp delivery, and BPF observability/security.

## Risks and Test Signals
Risks include unsafe pointer adjustment for netns table copies, missing cleanup of per-net masks, inconsistent static-key toggles after sysctl writes, insufficient capability checks for BPF JIT visibility, accepting invalid non-power-of-two flow tables, and race-prone replacement of RPS/flow-limit structures. Test signals include sysctl read/write tests under init and non-init netns, capability tests for BPF JIT knobs, RPS/RFS table resize under traffic, flow-limit CPU bitmap updates, qdisc default changes, netns create/destroy leak checks, and static-key state validation for `skb_defer_max` and high-order allocation toggles.
