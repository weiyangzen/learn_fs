# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_verbs.c

## Purpose
`ipoib_verbs.c` wraps the low-level RDMA verbs setup for the default IPoIB UD transport. It attaches/detaches multicast groups, transitions the UD QP through INIT/RTR/RTS, creates CQs and the QP, initializes send/receive work-request templates, tears resources down, and maps IB asynchronous events to IPoIB flush levels.

## Important APIs, Types, And Functions
`ipoib_mcast_attach()` checks/refreshes P_Key assignment, optionally sets Q_Key on the QP, and calls `ib_attach_mcast()`. `ipoib_mcast_detach()` calls `ib_detach_mcast()`. `ipoib_init_qp()` moves the QP through INIT, RTR, and RTS with Q_Key, port, P_Key index, and PSN fields, resetting on failure. `ipoib_transport_dev_init()` initializes CM support, sizes receive/send CQs, creates CQs on alternating completion vectors, creates the UD QP with capability-driven flags, arms CQs, initializes SGE/WR templates, and enables SG features. `ipoib_transport_dev_cleanup()` destroys QP and CQs. `ipoib_event()` routes RDMA events to light, normal, or heavy flush work.

## Control Flow And State
Transport init first tries `ipoib_cm_dev_init()`, and if CM is available expands receive CQ sizing for CM send and receive completions. It chooses completion vectors with a static atomic counter, creates the receive CQ then send CQ, requests notifications, and creates a UD QP with flags such as IPoIB UD LSO, block multicast loopback, netif QP, and OPA netdev use based on device/kernel capabilities cached in `priv`. It then sets DMA lkeys and WR defaults used by the datapath.

Event handling is intentionally coarse grained: client reregister and GID changes without a user-controlled address trigger light flushes; port error/active/LID changes trigger normal flushes; P_Key changes trigger heavy flushes that may restart QPs and update parent/child P_Key state.

## Dependencies And Integration Points
The file depends on RDMA verbs and multicast APIs, `ipoib_cm.c` for connected-mode initialization/cleanup, `ipoib_ib.c` for flush work, and `ipoib_multicast.c` for attach/detach callers. It is invoked from default netdev init/uninit in `ipoib_main.c`, and its `ipoib_event()` handler is registered per parent port.

## Risks And Test Signals
Risks include CQ size calculations when CM is enabled with or without SRQ, failure unwinding that must destroy only created resources, capability flag mismatches on older HCAs, QP state transition failures leaving stale state, and event storms causing repeated flushes. Test signals include devices with/without CM, SRQ, TSO, checksum offload, managed flow steering, OPA support, multicast attach failures, P_Key absence/change, and IB async events for port state, LID, GID, and client reregister.
