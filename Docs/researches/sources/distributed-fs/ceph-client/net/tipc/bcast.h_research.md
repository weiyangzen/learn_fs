# sources/distributed-fs/ceph-client/net/tipc/bcast.h

## Purpose
This header declares the public interface and shared data structures for TIPC broadcast and multicast handling.

## Important APIs, Types, And Functions
It defines broadcast method constants `BCLINK_MODE_BCAST`, `BCLINK_MODE_RCAST`, `BCLINK_MODE_SEL`, the method expiration interval, `struct tipc_nlist` for multicast destination tracking, and `struct tipc_mc_method` for socket-to-broadcast method state. It declares broadcast lifecycle, transmit, receive, ACK/sync, netlink, stat reset, mode query, ratio query, and filtering functions. Inline helpers lock/unlock the per-net broadcast spinlock and return the broadcast send link.

## Control Flow
The header does not implement complex control flow, but its API separates lifecycle, peer membership, transmit selection, receive feedback, and netlink property management. `tipc_mc_method` allows callers to cache a selected multicast method until expiration unless the user forces a method.

## State And Persistence
`tipc_nlist` instances hold temporary local/remote destination lists. `tipc_mc_method` holds per-socket or per-send method state and a deferred queue for ordering. Broadcast link state itself lives in `struct tipc_net`.

## Dependencies And Integration Points
The header depends on `core.h` and forward declarations for TIPC link, message, netlink message, and destination list types. It is consumed by socket, bearer, node, and link code.

## Risks And Test Signals
Risks include callers failing to purge destination lists, using broadcast lock helpers in the wrong context, or misusing `mandatory` method state. Test signals include compile coverage of all declarations, multicast socket tests that switch methods, and lockdep coverage around broadcast lock use.
