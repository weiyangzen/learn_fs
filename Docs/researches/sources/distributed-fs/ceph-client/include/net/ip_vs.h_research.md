# sources/distributed-fs/ceph-client/include/net/ip_vs.h

Purpose: Defines the IP Virtual Server in-kernel API: packet header parsing, connection/service/destination state, schedulers, persistence engines, protocol modules, applications, sync daemon, estimators, resizable hash tables, sysctls, transmit methods, and conntrack hooks.

Important APIs/types/functions: `ip_vs_iphdr` abstracts IPv4/IPv6 packet metadata and extension-header parsing. `ip_vs_rht` provides RCU/seqcount-protected resizable hash tables. Core structs include `ip_vs_conn`, `ip_vs_service`, `ip_vs_dest`, `ip_vs_scheduler`, `ip_vs_pe`, `ip_vs_app`, `ip_vs_protocol`, `ip_vs_proto_data`, and `netns_ipvs`. APIs cover connection lookup/new/put/expire, service/dest lookup, scheduler bind/unbind, app and persistence registration, protocol init/cleanup, estimator management, sync daemon control, transmit variants, netns init/cleanup, hooks registration, and conntrack integration.

Control flow: Packet hooks parse IP headers, find or schedule a connection using protocol handlers, bind destinations and apps, then transmit by forwarding method: NAT, tunnel, direct route, bypass, local, or null. Resizable tables are walked under RCU and seqcount retry while resize may expose old/new tables. Timers expire conns/dests and estimator kthreads process stats in tick buckets.

State and persistence: Per-net `netns_ipvs` holds service and connection tables, protocol/app tables, real-server tables, stats, delayed works, sysctls, sync daemon state, estimator kthreads, hook masks, trash lists, and counters. Connections have timers, refcounts, flags, state, seq deltas, app data, PE data, and destination refs. All is runtime/netns state configured through IPVS control plane.

Dependencies/integration: Integrates Linux netfilter, conntrack, IPv4/IPv6 headers, checksum helpers, namespace lifecycle, workqueues, timers, RCU, modules, sysctl, housekeeping CPU masks, and user UAPI `linux/ip_vs.h`.

Risks: Refcount, timer, RCU, and resize interactions are high risk; conntrack confirmation can prevent redirecting old flows; mixed IPv4/IPv6 destinations affect sync; sysctl defaults must match behavior without `CONFIG_SYSCTL`; checksum delta helpers must use correct address family. Test signals include IPv4/IPv6 services, each forwarding method, scheduler modules, persistence templates, FTP/app helpers, conn table resize, sync master/backup, estimator start/stop/reload, conntrack on/off, and netns teardown with live conns.
