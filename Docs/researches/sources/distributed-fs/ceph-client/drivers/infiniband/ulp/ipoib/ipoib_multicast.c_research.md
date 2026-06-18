# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_multicast.c

## Purpose
`ipoib_multicast.c` manages InfiniBand multicast membership for IPoIB. It joins the mandatory broadcast group, synchronizes netdevice multicast addresses with IB multicast groups, supports send-only multicast groups for transmit-only traffic, attaches/detaches QPs, creates AHs for multicast sends, controls carrier-on after broadcast join, and flushes/restarts multicast state around device events.

## Important APIs, Types, And Functions
Scheduling and lifecycle helpers include `__ipoib_mcast_schedule_join_thread()`, `ipoib_mcast_join_task()`, `ipoib_mcast_start_thread()`, `ipoib_mcast_stop_thread()`, `ipoib_mcast_dev_flush()`, and `ipoib_mcast_restart_task()`. Membership operations include `ipoib_mcast_alloc()`, `__ipoib_mcast_find()`, `__ipoib_mcast_add()`, `ipoib_mcast_join()`, `ipoib_mcast_join_complete()`, `ipoib_mcast_join_finish()`, `ipoib_mcast_leave()`, `ipoib_mcast_remove_list()`, and `ipoib_check_and_add_mcast_sendonly()`. Transmit entry is `ipoib_mcast_send()`. Debug iterators are compiled when debug is enabled.

## Control Flow And State
The join task waits for `IPOIB_FLAG_OPER_UP`, active port state, and a valid device address. If no broadcast group exists, it allocates one keyed from `dev->broadcast + 4`; until that group is attached, all other joins are deferred. Successful broadcast join updates cached multicast MTU, admin MTU when appropriate, Q_Key, traffic class/rate/SL/flow/hop values, and `rn->mtu`, attaches the QP, creates an AH, schedules carrier-on work, and restarts the join task for non-broadcast memberships.

The multicast list mirrors the netdev multicast address list. Restart clears found flags, validates IPoIB multicast addresses against the broadcast template, ignores userspace-direct groups when `umcast` is enabled and SA records exist, replaces send-only entries with full entries when subscribed, and removes absent non-send-only groups. Send-only groups are created on transmit, queue packets up to `IPOIB_MAX_MCAST_QUEUE`, and retry joins with capped exponential backoff; repeated send-only failure drops queued packets but leaves the group cached for future sends.

Flush removes all multicast groups and broadcast state from rbtrees/lists under lock, waits for in-flight joins, detaches QPs, frees multicast SA handles, drops queued packets, releases AHs, and removes neighbour entries tied to MGIDs.

## Dependencies And Integration Points
The file depends on IB SA multicast APIs, RDMA AH construction, netdevice multicast address APIs, rtnl for carrier-on safety, and lower `rdma_netdev` `attach_mcast`/`detach_mcast`/`send` ops. It is called from `ipoib_ib.c` during up/down/flush, from `ipoib_main.c` transmit and set-rx-mode paths, and from neighbour GC to clean send-only groups.

## Risks And Test Signals
Risks include races between multicast restart/flush/join callbacks, carrier-on during stop/unregister, queued packet drops on join failure, correctness of broadcast-derived MTU/Q_Key values, send-only behavior with subnet managers that reject send-only joins, and userspace-direct multicast filtering. Test signals include broadcast join before carrier, IPv4/IPv6 multicast joins and leaves, send-only transmit to unsubscribed groups, `umcast` toggling, port inactive/active transitions, backoff/retry behavior, group flush during unregister, and debugfs multicast iterator output.
