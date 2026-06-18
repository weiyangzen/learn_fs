# `sources/distributed-fs/ceph-client/include/linux/if_tunnel.h`

Purpose: small internal tunnel helper header that includes IP tunnel UAPI definitions and provides an RCU iteration macro for tunnel hash/list traversal.

Important APIs/types/functions: `for_each_ip_tunnel_rcu(pos, start)`.

Control flow and state: macro follows `pos->next` with `rcu_dereference` until null. The tunnel list/hash state is owned by tunnel drivers.

Dependencies/integration: depends on IPv4/IPv6 headers, UAPI `if_tunnel.h`, `u64_stats_sync`, and RCU conventions.

Risks: caller must hold appropriate RCU read lock or RTNL as documented; `pos` type must have `next`; mutation outside the documented locking model risks races.

Test signals: tunnel lookup/list traversal under concurrent add/delete with RCU, lockdep coverage, and build coverage for IP tunnel drivers.
