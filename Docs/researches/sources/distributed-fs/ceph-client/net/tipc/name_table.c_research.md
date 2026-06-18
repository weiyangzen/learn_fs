# sources/distributed-fs/ceph-client/net/tipc/name_table.c

## Purpose
`name_table.c` implements TIPC service name publication storage, service-range lookup, subscription notification, multicast/group destination expansion, local publish/withdraw orchestration, netlink dumping of publications, and helper lists of destination socket/node pairs. It is the authoritative runtime table mapping service types/ranges to publishing sockets.

## Important APIs, Types, And Functions
Internal structures are `struct service_range`, an augmented RB-tree node keyed by lower/upper instance ranges with `max` for overlap search, and `struct tipc_service`, a hash-bucket entry for one service type with its range tree, subscriptions, publication counter, and spinlock. Important exported functions include `tipc_nametbl_lookup_anycast()`, `tipc_nametbl_lookup_group()`, `tipc_nametbl_lookup_mcast_sockets()`, `tipc_nametbl_lookup_mcast_nodes()`, `tipc_nametbl_build_group()`, `tipc_nametbl_publish()`, `tipc_nametbl_withdraw()`, `tipc_nametbl_insert_publ()`, `tipc_nametbl_remove_publ()`, `tipc_nametbl_subscribe()`, `tipc_nametbl_unsubscribe()`, `tipc_nametbl_init()`, `tipc_nametbl_stop()`, `tipc_nl_name_table_dump()`, and the `tipc_dest_*()` list helpers.

## Control Flow
Insertion allocates a `publication`, finds or creates the hash-bucket `tipc_service`, creates or finds an exact `service_range`, rejects duplicate key/socket/node publications, links local publications into `local_publ`, links all publications into `all_publ`, assigns a monotonic id, and reports `TIPC_PUBLISHED` to overlapping subscriptions. Removal finds the service and exact range, unlinks the publication, reports `TIPC_WITHDRAWN`, erases the range if empty, and deletes the service when it has neither ranges nor subscriptions.

Anycast lookup first checks whether a remote lookup should be deferred by scope. It then searches overlapping ranges for the requested instance and chooses local-only, legacy closest-first, or round-robin `all_publ` selection, moving the selected publication to the tail. Multicast and group lookup functions walk matching ranges to build destination lists, local socket lists, node lists, or communication-group members. Subscribe creates the service if needed, attaches a subscription, optionally reports existing matching publications in publication-id order, and holds a reference until unsubscribe.

`tipc_nametbl_publish()` enforces `TIPC_MAX_PUBL`, inserts the publication, delegates distribution message creation to `name_distr.c`, and broadcasts the returned skb after dropping the table lock. Withdraw mirrors this flow and frees the publication with RCU. Netlink dumping walks hash buckets, services, ranges, and publication lists with callback cursor state for service type, lower bound, key, and done status.

## State And Persistence
Persistent state is the per-net `struct name_table`: hash buckets, node/cluster scope publication lists, cluster-scope rwlock, local publication count, replicast destination count, and outgoing name-distribution sequence. Each `tipc_service` owns its RB tree and subscription list. Each `publication` is linked simultaneously into socket, node/scope, local-publication, all-publication, and temporary reporting lists, with RCU lifetime.

## Dependencies And Integration Points
The file depends on `netlink.h`, `name_distr.h`, subscription reporting, broadcast distribution, address/scope helpers, node subscription cleanup, and group membership construction. Socket bind/unbind paths publish and withdraw here; `msg.c` uses anycast lookup for named-message rerouting; broadcast and group code use multicast/group lookup helpers; legacy and modern netlink paths use the dump API.

## Risks And Edge Cases
The locking hierarchy combines the global per-net `nametbl_lock`, per-service spinlocks, RCU traversal, and the cluster-scope lock in `name_distr.c`; lock-order regressions can deadlock. Publication objects live on many lists, so partial unlinking can corrupt later cleanup. Overlap search depends on correct augmented RB-tree `max` maintenance. Round-robin list movement mutates lookup state. Netlink dump cursors can become stale if publications are removed mid-dump, and the code signals interrupted dumps via `prev_seq`.

## Test Signals
Tests should cover exact and overlapping ranges, duplicate publication rejection, max-publication enforcement, local/node/cluster scope semantics, anycast local-first/round-robin/legacy behavior, multicast socket and node expansion, group member construction, subscription initial reports and withdrawal reports, service/range deletion, netlink dump pagination under concurrent updates, destination list duplicate suppression, and lockdep/RCU/KASAN during bind/unbind/node-failure races.
