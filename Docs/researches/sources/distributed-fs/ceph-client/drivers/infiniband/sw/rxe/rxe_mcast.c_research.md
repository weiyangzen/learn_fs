# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mcast.c

## Purpose
`rxe_mcast.c` implements RXE multicast group management. It maps multicast GIDs to netdev multicast MAC addresses, stores multicast groups in an RB tree, and tracks QPs attached to each group for packet replication in receive paths.

## Important APIs, types, and functions
External functions are `rxe_lookup_mcg()`, `rxe_attach_mcast()`, `rxe_detach_mcast()`, and `rxe_cleanup_mcg()`. Internal helpers manage netdev multicast add/delete, RB tree insert/remove/lookup, multicast group allocation/destruction, and multicast attachment (`struct rxe_mcg`) and membership (`struct rxe_mca`) lifetime.

## Control flow
Attach calls `rxe_get_mcg()` to find or allocate a group. Allocation enforces `max_mcast_grp`, speculatively allocates without holding the lock, rechecks under `mcg_lock`, inserts the group, and then adds the netdev multicast address outside the lock. Then `rxe_attach_mcg()` avoids duplicate QP membership, allocates an MCA, enforces per-group and total attach limits, takes a QP reference, and appends it to the group list. Detach finds the group, removes the matching MCA, drops references/counters, and destroys the group when the last QP detaches.

## State and persistence
Per-device multicast state includes `mcg_tree`, `mcg_lock`, group count, total attachment count, per-QP membership count, group krefs, QP refs, and netdev multicast filter state. It persists until detach or device cleanup.

## Dependencies and integration points
The file uses Linux RB trees, krefs, netdev multicast APIs, IPv6 multicast-to-Ethernet mapping, RXE object refs, and RDMA attach/detach multicast verbs. Receive multicast replication uses the group membership list.

## Risks
If `rxe_mcast_add()` fails after inserting the group into the tree, `rxe_get_mcg()` currently frees `mcg` directly rather than removing the tree entry and dropping the inserted kref; that path should be reviewed carefully. Attach/detach counters and krefs must remain balanced under lock. Netdev disappearance can make add/delete return `-ENODEV`.

## Test signals
Test first attach, duplicate attach, multi-QP attach limits, detach last member, netdev multicast add/delete failure, lookup while attach/detach races, device teardown with non-empty group tree, and receive replication to all members.
