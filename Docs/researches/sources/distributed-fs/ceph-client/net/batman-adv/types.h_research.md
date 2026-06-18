# sources/distributed-fs/ceph-client/net/batman-adv/types.h

## Purpose
This header is the central private data model for batman-adv. It declares per-interface, per-originator, per-neighbor, TVLV, translation table, gateway, multicast, DAT, bridge-loop-avoidance, fragmentation, forwarding, throughput-meter, and algorithm callback structures.

## Important APIs, Types, And Functions
Key structures include `batadv_priv`, `batadv_hard_iface`, `batadv_orig_node`, `batadv_neigh_node`, `batadv_priv_tvlv`, `batadv_tvlv_container`, `batadv_tvlv_handler`, `batadv_priv_tt`, `batadv_tt_*` entries, `batadv_priv_gw`, optional `batadv_priv_mcast`, optional `batadv_priv_dat`, optional BLA types, `batadv_forw_packet`, and `batadv_algo_ops` with nested interface, neighbor, originator, and gateway operation tables. Important enums include DHCP direction, traffic counters, originator capabilities, throughput meter role, and TVLV handler flags.

## Control Flow
The file does not implement behavior, but it encodes control-flow contracts through callbacks and ownership fields. Routing algorithms plug in via `batadv_algo_ops`; TVLV callbacks are stored in `batadv_tvlv_handler`; delayed work fields drive OGM transmission, ELP transmission, translation-table purging, multicast updates, DAT purging, BLA work, originator purging, throughput-meter completion, and forwarding queues.

## State, Persistence, And Dependencies
Most state is runtime-only and tied to net_device lifetime. Lifetimes are governed by `kref`, RCU heads, spinlocks, mutexes, atomics, delayed work, hlist/list membership, and per-CPU counters. `batadv_priv` is the root per mesh interface object and embeds feature-private substructures. Conditional blocks depend on kernel config options such as `CONFIG_BATMAN_ADV_DAT`, `CONFIG_BATMAN_ADV_MCAST`, `CONFIG_BATMAN_ADV_BLA`, `CONFIG_BATMAN_ADV_BATMAN_V`, and `CONFIG_BATMAN_ADV_DEBUG`.

## Integration Points
All batman-adv modules include this indirectly through `main.h`. Packet formats come from `uapi/linux/batadv_packet.h` and netlink/user ABI from `uapi/linux/batman_adv.h`. `tvlv.c` specifically uses `batadv_priv_tvlv`, `batadv_tvlv_container`, `batadv_tvlv_handler`, and `batadv_tvlv_handler_flags`.

## Risks
This header concentrates cross-module concurrency contracts, so field misuse can produce races even if individual modules compile. Several comments specify locks that must protect list or metadata updates; bypassing those locks can corrupt routing, TT, TVLV, or multicast state. Conditional compilation changes structure layouts and available counters, which makes feature combinations important. Some comments in the BLA claim structure appear swapped between `refcount` and `rcu`, so maintainers should verify semantics from usage rather than relying only on the comment text.

## Test Signals
Useful signals include lockdep on all list mutations, RCU stall/KASAN coverage during teardown, feature matrix builds across optional configs, route/TT/multicast/gateway behavior under interface churn, and netlink/debugfs dumps that agree with the embedded counters and lists.
