# sources/distributed-fs/ceph-client/include/uapi/linux/ip_vs.h

## Purpose
`ip_vs.h` exports the Linux IP Virtual Server ABI for configuring services, real-server destinations, synchronization daemons, timeouts, connection flags, statistics, and the generic netlink family.

## Important APIs, Types, and Functions
Legacy socket-option commands are defined under `IP_VS_SO_SET_*` and `IP_VS_SO_GET_*`. Structures include `ip_vs_service_user`, `ip_vs_dest_user`, `ip_vs_stats_user`, `ip_vs_getinfo`, `ip_vs_service_entry`, `ip_vs_dest_entry`, `ip_vs_get_dests`, `ip_vs_get_services`, `ip_vs_timeout_user`, and `ip_vs_daemon_user`. The generic netlink family is `IPVS_GENL_NAME` with commands for service/destination CRUD, daemon control, config, info, zero, and flush. Attribute enums describe nested service, destination, daemon, stats, and info payloads.

## Control Flow
Userspace load-balancer tools create services, add destinations, tune scheduling flags and persistence, start sync daemons, and fetch stats. The kernel IPVS tables then classify packets, choose destinations, update connection state, and optionally synchronize connection entries to backup nodes.

## State and Persistence
IPVS services, destinations, connection tables, stats, timeouts, and daemon status live in kernel networking state and network namespaces. The header defines only request and response layouts. Counters are mutable until zeroed or flushed.

## Dependencies and Integration Points
It depends on `<linux/types.h>`. It integrates with netfilter/IPVS, generic netlink, legacy sockopt control paths, keepalived/ipvsadm, tunneling modes, conntrack, and multicast sync.

## Risks and Test Signals
Tests should cover struct layout for legacy sockopts, flexible-array response sizing, nested netlink attribute validation, stats32/stats64 compatibility, sync flag masks, tunnel type/flags, and namespace isolation. Risk is high for compatibility because both old sockopt and netlink ABIs coexist.
