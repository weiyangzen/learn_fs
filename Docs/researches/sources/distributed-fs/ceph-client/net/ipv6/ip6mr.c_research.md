# sources/distributed-fs/ceph-client/net/ipv6/ip6mr.c

## Purpose
This file implements IPv6 multicast routing: multicast virtual interfaces, multicast forwarding cache entries, unresolved cache queries to a routing daemon, PIM-SM register handling, `/proc` visibility, rtnetlink route dump/get support, multicast-routing socket options/ioctls, per-net table initialization, and multicast packet forwarding from input and output paths.

## Important APIs, Types, And Functions
Central state lives in `struct mr_table`, `struct vif_device`, and `struct mfc6_cache`. IPv6-specific rule/result wrappers are `struct ip6mr_rule` and `struct ip6mr_result`. Global locks are `mrt_lock` for VIF/MFC/mroute socket state and `mfc_unres_lock` for unresolved queues. `mrt_cachep` allocates MFC entries.

Initialization and teardown are `ip6_mr_init()` and `ip6_mr_cleanup()`. Socket-facing APIs are `ip6_mroute_setsockopt()`, `ip6_mroute_getsockopt()`, `ip6mr_ioctl()`, `ip6mr_compat_ioctl()`, `ip6mr_sk_done()`, and `mroute6_is_socket()`. Packet paths are `ip6_mr_input()`, `ip6_mr_output()`, `ip6_mr_forward()`, `ip6_mr_output_finish()`, `ip6mr_forward2()`, `ip6mr_output2()`, and `ip6mr_prepare_xmit()`.

Control-plane helpers include `mif6_add()`, `mif6_delete()`, `ip6mr_mfc_add()`, `ip6mr_mfc_delete()`, `mroute_clean_tables()`, `ip6mr_cache_unresolved()`, `ip6mr_cache_resolve()`, `ip6mr_cache_report()`, `mr6_netlink_event()`, `mrt6msg_netlink_event()`, `ip6mr_rtm_getroute()`, and `ip6mr_rtm_dumproute()`.

## Control Flow
Per-network initialization registers fib notifier ops, creates multicast route tables and default rules, and optionally creates `/proc/net/ip6_mr_vif` and `/proc/net/ip6_mr_cache`. Module init creates the MFC slab cache, registers pernet ops, a netdevice notifier, optional PIM protocol handler, and rtnetlink route handlers.

Userspace enables a multicast routing socket with `MRT6_INIT` on a raw ICMPv6 socket. `MRT6_ADD_MIF` adds normal VIFs or PIM register VIFs, enabling all-multicast and incrementing IPv6 `mc_forwarding` counters. `MRT6_ADD_MFC` and proxy variants create or update forwarding cache entries, insert them into the rhashtable and cache list, notify fib/rtnetlink listeners, and replay any queued unresolved packets. Delete/flush paths remove VIFs and MFCs, notify listeners, drop or unregister PIM register devices, and destroy unresolved queues.

Incoming multicast packets enter `ip6_mr_input()`. It selects the multicast route table through rules, finds an exact `(S,G)` cache or fallback `(*,G)`/parent entry, queues unresolved packets and reports `MRT6MSG_NOCACHE` to the mroute socket if needed, or forwards via `ip6_mr_forward()`. Forwarding validates the incoming VIF, sends PIM assert reports on wrong-interface conditions, updates counters, clones skbs for all but one outgoing VIF, decrements hop limit, and transmits through netfilter forward hooks.

Local output with `IP6SKB_MCROUTE` enters `ip6_mr_output()`. If the skb was not already forwarded and cache lookup succeeds with the expected parent VIF, `ip6_mr_output_finish()` replicates to outgoing VIFs through `ip6_output()`; otherwise it falls back to normal IPv6 output or queues an unresolved query. PIM register handling decapsulates inbound PIM register packets to a virtual `pim6reg` device and sends whole-packet reports from that device back to the routing daemon.

## State And Persistence
All state is in memory per net namespace: multicast route tables, VIF arrays, MFC rhashtable/list, unresolved queue, mroute socket pointer, PIM flags, register VIF number, fib notifier sequence, and `/proc` entries. Cache entries track parent VIF, TTL thresholds, packet/byte/wrong-if counters, last-use/assert timestamps, flags, origin, and multicast group. Unresolved entries hold queued packets and expire after a timer-driven timeout.

There is no disk persistence. Static entries are flagged `VIFF_STATIC` or `MFC_STATIC` so selective flush commands can preserve or remove them, but they still disappear on namespace/module teardown.

## Dependencies And Integration Points
This file integrates with raw IPv6 sockets, multicast daemon APIs from `<linux/mroute6.h>`, rtnetlink route families `RTNL_FAMILY_IP6MR`, fib rules/notifiers, netdevice unregister notifications, IPv6 route output, netfilter IPv6 forward hooks, PIM protocol dispatch, procfs/seq_file, RCU, rhashtable, and generic multicast routing helpers shared with IPv4. `ip6_output.c` calls `mroute6_is_socket()` for multicast loopback behavior.

## Risks And Edge Cases
Concurrency is the major risk: data path is mostly RCU, table mutation is RTNL plus `mrt_lock`, unresolved queues use `mfc_unres_lock`, and socket lifetime relies on `SOCK_RCU_FREE`. VIF deletion must update all-multicast, `mc_forwarding`, register-device state, netdevice trackers, and maxvif consistently. Unresolved queues are capped to a few packets per entry but can still produce daemon backpressure or timeout netlink replies.

Forwarding behavior for `(*,*)`, `(*,G)`, proxy parent entries, wrong-interface asserts, PIM whole-packet reports, and local-output multicast routing is subtle. Rtnetlink strict getroute validation requires full 128-bit source/destination lengths when attributes are present. Compatibility ioctls must avoid speculative out-of-bounds VIF access with `array_index_nospec()`.

## Test Signals
Strong coverage includes raw ICMPv6 `MRT6_INIT/DONE`, add/delete normal and PIM register MIFs, add/delete/update exact and proxy MFCs, unresolved queue creation/report/replay/timeout, multicast forwarding across multiple VIFs with hop-limit thresholds, wrong-interface assert generation, `MRT6_FLUSH` static/non-static behavior, netdevice unregister cleanup, `/proc/net/ip6_mr_vif` and `ip6_mr_cache` output, rtnetlink `RTM_GETROUTE` and dumps, multiple multicast tables/rules when enabled, PIM register encapsulation/decapsulation, and netns teardown under active traffic.
