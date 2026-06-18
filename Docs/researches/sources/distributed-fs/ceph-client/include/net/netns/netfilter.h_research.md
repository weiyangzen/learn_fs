# sources/distributed-fs/ceph-client/include/net/netns/netfilter.h

Purpose: Defines per-network-namespace core netfilter state, including logger bindings, hook entry arrays by protocol family, sysctl/proc entries, and defragmentation users.

Important APIs/types/functions: `struct netns_nf` stores optional `proc_netfilter`, RCU `nf_loggers[NFPROTO_NUMPROTO]`, sysctl headers for logging and lwtunnel hooks, RCU hook arrays for IPv4/IPv6 and optional ARP/bridge families, plus IPv4/IPv6 defrag user counters when enabled.

Control flow: Netfilter hook registration updates the relevant family/hook RCU array; packet traversal reads hook entries under RCU. Logging paths pick per-net protocol-family loggers. Sysctl/proc expose logging and lwtunnel hook controls. Defrag modules increment/decrement per-net users.

State and persistence: Runtime per-net hook arrays, logger pointers, proc/sysctl headers, and defrag counters. No durable persistence; RCU and namespace teardown ordering are central.

Dependencies/integration: Depends on netfilter core, nfnetlink, logging, queueing, bridge netfilter, procfs/sysctl, and namespace teardown ordering.

Risks/test signals: Test hook registration/unregistration races, namespace-specific logger binding, ARP/bridge config matrices, lwtunnel sysctl registration, defrag user reference counts, proc/sysctl cleanup, and packet traversal during hook-array replacement.
