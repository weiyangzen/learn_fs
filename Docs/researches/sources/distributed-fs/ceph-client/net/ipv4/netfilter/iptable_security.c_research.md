# sources/distributed-fs/ceph-client/net/ipv4/netfilter/iptable_security.c

## Purpose
`iptable_security.c` instantiates the legacy IPv4 `security` table for MAC policy hooks after normal DAC-style filtering.

## Important APIs, Types, And Functions
Key objects are `security_table`, `sectbl_ops`, `iptable_security_table_init()`, pernet pre-exit/exit handlers, and module init/exit.

## Control Flow
The module allocates hook ops using `ipt_do_table()`, registers pernet cleanup, and registers a template that creates a default security table per namespace. It hooks local input, forward, and local output at `NF_IP_PRI_SECURITY`.

## State And Persistence
State is the per-net xt table plus static hook ops. Rules are in-memory and namespace-scoped.

## Dependencies And Integration Points
It depends on `SECURITY` Kconfig, `ip_tables.c`, xtables templates, and IPv4 netfilter hook priority ordering.

## Risks
Risks include priority/order regressions relative to LSM/MAC expectations, init cleanup mistakes, and table absence in configurations without legacy iptables support.

## Test Signals
Test module load/unload, default table creation, local-in/forward/local-out hooks, ordering relative to filter/mangle tables, namespace teardown, and failure cleanup.
