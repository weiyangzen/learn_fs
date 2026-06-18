# sources/distributed-fs/ceph-client/net/tipc/bearer.h

## Purpose
This header defines the generic TIPC bearer/media abstraction shared by media drivers and the TIPC core.

## Important APIs, Types, And Functions
It defines media constants, media address layout constants, supported media type IDs, minimum bearer MTU, broadcast/replicast support markers, `struct tipc_media_addr`, `struct tipc_media`, `struct tipc_bearer`, and `struct tipc_bearer_names`. It declares media objects, bearer netlink APIs, media netlink APIs, L2 media helpers, bearer lookup/lifecycle helpers, transmit functions, loopback helpers, and `tipc_mtu_bad()`.

## Control Flow
The function pointer table in `struct tipc_media` is the key dispatch point: generic bearer code calls media-specific send, enable, disable, and address conversion functions. Inline `tipc_loopback_trace()` clones packets to loopback only when packet taps are active, and `tipc_mtu_bad()` rejects devices too small for TIPC headers.

## State And Persistence
The header defines state stored in each bearer: media-private pointer, MTU, addresses, packet type, RCU head, priority/window/tolerance/domain, identity, discovery pointer, network plane, encapsulation header length, up bit, and refcount. State persists only while the bearer is enabled.

## Dependencies And Integration Points
Dependencies include TIPC core/message/netlink headers, generic netlink, netdevice packet handling, and optional media implementations selected by Kconfig. It is the contract between generic bearer management and `eth_media`, `ib_media`, and `udp_media`.

## Risks And Test Signals
Risks include media implementations not fully initializing required bearer fields, inconsistent media address conversion, and callers using transmit helpers without valid RCU/RTNL context. Test signals include compile coverage for all configured media, MTU boundary tests, netlink bearer/media property reporting, and packet capture via loopback trace.
