# sources/distributed-fs/ceph-client/net/tipc/subscr.h

## Purpose
Defines the topology subscription object and endian conversion helpers used by the topology server and name table. It also declares subscription lifecycle APIs and topology-server namespace lifecycle functions.

## Important APIs, Types, And Macros
`struct tipc_subscription` contains the host-endian subscription, event template, `kref`, namespace pointer, optional timer, list nodes for name-table and subscriber ownership, connection id, inactive flag, and spinlock. `TIPC_MAX_SUBSCR` and `TIPC_MAX_PUBL` define topology-service scale limits. `TIPC_FILTER_MASK`, `tipc_sub_read`, `tipc_sub_write`, and `tipc_evt_write` preserve compatibility with clients that signal endian mode through filter bits.

## Control Flow And State
The header models dual ownership: subscriptions live simultaneously in a service/name-table list and a per-connection list. Timers and publication callbacks mutate the event template under `sub->lock`, while `kref` controls final deallocation. The endian macros are part of runtime behavior because they decide whether fields are byte-swapped based on filter bits.

## Dependencies And Integration Points
Includes `topsrv.h`, bringing topology server event delivery into the subscription contract. It forward-declares `publication` and `tipc_conn`, while `subscr.c`, `topsrv.c`, and name-table code use the list nodes and lifecycle functions together.

## Risks And Test Signals
Risk centers on list ownership conventions and endian macro assumptions. Tests should cover little-endian and compatibility-form requests, cancellation equality against raw `evt.s`, timer cancellation, and publication overlap reporting after connection close. Build coverage should ensure all topology service users include this header without circular type exposure.
