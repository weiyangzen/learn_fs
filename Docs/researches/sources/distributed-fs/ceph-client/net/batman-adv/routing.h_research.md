# sources/distributed-fs/ceph-client/net/batman-adv/routing.h

## Purpose
Declares the receive-side routing API shared by batman-adv packet dispatchers and related modules. It exposes management-packet validation, route updates, packet receive handlers for major batman-adv packet classes, router lookup, and sequence-window restart protection.

## Important APIs And Types
The header exports `batadv_check_management_packet`, `batadv_update_route`, `batadv_recv_icmp_packet`, `batadv_recv_unicast_packet`, `batadv_recv_frag_packet`, `batadv_recv_bcast_packet`, `batadv_recv_unicast_tvlv`, `batadv_recv_unhandled_unicast_packet`, `batadv_find_router`, and `batadv_window_protected`. `batadv_recv_mcast_packet` is either the real multicast handler when `CONFIG_BATMAN_ADV_MCAST` is enabled or an inline stub that frees the skb and returns `NET_RX_DROP`.

## Control Flow
There is no executable control flow beyond the multicast-disabled inline. The declarations define the ownership contract that receive handlers consume or free skbs and return `NET_RX_*` status. Callers use `batadv_find_router` before send-side forwarding and `batadv_window_protected` when validating sequence-number windows.

## State And Persistence
The header owns no state. Its inline multicast fallback consumes the skb immediately when multicast support is absent.

## Dependencies And Integration Points
Includes `main.h`, `linux/skbuff.h`, and `linux/types.h`, tying the API to core batman-adv private structures and kernel skb handling. It is included by packet dispatch code, send logic needing router lookup, and modules that validate management packets or sequence restart windows.

## Risks
The main risk is API contract drift: receive handlers must preserve skb ownership expectations, and the multicast stub means code paths must not assume multicast packets survive when the feature is disabled. Changes to function signatures ripple broadly through packet dispatch and send-side routing.

## Test Signals
Compilation with and without `CONFIG_BATMAN_ADV_MCAST` is the primary direct signal. Integration tests should verify unsupported multicast packets are dropped cleanly in non-mcast builds and handled by the implementation in mcast builds.
