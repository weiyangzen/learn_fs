# sources/distributed-fs/ceph-client/drivers/infiniband/core/multicast.c

## Purpose
`multicast.c` implements RDMA SA multicast join and leave management for InfiniBand-capable ports. It serializes joins for the same MGID, tracks membership by join-state bit, sends SA `MCMemberRecord` SET and DELETE requests, exposes joined records to callers, builds AH attributes from multicast records, and reacts to port, LID, pkey, and client-reregister events.

## Important APIs, types, and functions
- Exported APIs are `ib_sa_join_multicast()`, `ib_sa_free_multicast()`, `ib_sa_get_mcmember_rec()`, and `ib_init_ah_from_mcmember()`.
- `struct mcast_device` is per RDMA device and contains an event handler plus a flexible array of `mcast_port` objects.
- `struct mcast_port` owns an RB tree of groups keyed by MGID and a refcount/completion used during device removal.
- `struct mcast_group` stores the current SA member record, pending and active member lists, membership counters by join-state type, group state, active SA query, pkey index, leave state, and retry count.
- `struct mcast_member` wraps the public `ib_sa_multicast`, caller client, current state, group pointer, list entry, and lifetime completion.
- `mcast_work_handler()` is the serialized group worker that processes pending joins, SA joins, leaves, and event recovery.
- `join_handler()` and `leave_handler()` are SA query callbacks.

## Control flow
`mcast_init()` creates an ordered workqueue, registers an SA client, and registers the `ib_multicast` client. Device add allocates a `mcast_device`, initializes multicast-capable ports, stores client data, and registers an event handler. Device remove unregisters events, flushes multicast work, drops each port's base reference, waits for groups to drain, and frees the device wrapper.

`ib_sa_join_multicast()` allocates a member, takes a reference on the caller's SA client, acquires or creates the MGID group, and queues the member. The group worker processes one logical action at a time. If the group already has the requested join-state bits and the supplied record is compatible, the member joins locally and the caller callback runs immediately. Otherwise the worker sends an SA SET request and returns until `join_handler()` updates the group record and restarts the worker. After members leave, `get_leave_state()` identifies SA join-state bits with no remaining active members and sends SA DELETE requests.

`ib_sa_free_multicast()` removes a member from pending or active lists. If an active member was the last user of a join-state bit, the group is made busy and work is queued so a leave can be sent. Event handling marks groups for full error recovery or pkey-specific recovery. Group error processing reports `-ENETRESET` to active members and clears membership so callers can rejoin.

## State and persistence
All state is in memory. The RB tree is protected by `mcast_port.lock`; group lists, counters, and state are protected by `mcast_group.lock`. Group references combine an atomic group refcount with a port refcount so device removal waits until active groups finish. Member lifetime uses a refcount and completion so callbacks can safely free multicast objects after the core drops its references.

The SA maintains actual fabric membership; this file mirrors it in `group->rec.join_state` and `members[]`. It does not persist membership across driver unload, port reset, or process restart.

## Dependencies and integration points
The implementation depends on `sa.h` query helpers, RDMA device client registration, IB event handlers, GID cache helpers, pkey lookup, AH attribute helpers, netdevice-aware RoCE GID lookup, ordered workqueues, RB trees, and exported SA multicast ABI used by ULPs such as IPoIB.

## Risks
- Join serialization is deliberate. Bypassing it can race two different records for the same MGID, producing incompatible SA state.
- MGID zero permits duplicates during insertion, which is special-case behavior that must be preserved.
- Callback return values can trigger `ib_sa_free_multicast()` from inside worker or callback context; refcounts are critical.
- PKey events compare cached pkey index with a fresh lookup. Incorrect handling can either miss required resets or reset healthy groups.
- `rdma_find_gid_by_port()` in `ib_init_ah_from_mcmember()` returns a GID attribute that is moved into AH attributes; callers must later destroy AH attributes as documented.

## Test signals
- Test multiple simultaneous joins to one MGID with compatible and incompatible records.
- Verify each join-state bit type increments and decrements correctly and that SA DELETE is sent only when the last active member of a state leaves.
- Inject SA join and leave failures, including leave retry exhaustion.
- Trigger port error, LID change, client reregister, and pkey change events and verify callbacks and rejoin behavior.
- Build and runtime tests should include both IB and RoCE AH initialization paths, with net namespace filtering for netdevices.
