# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_main.c

## Purpose
`ipoib_main.c` wires HFI1 accelerated IP-over-InfiniBand support into the RDMA netdev allocation path. It wraps the generic IPoIB netdev operations with HFI1-specific transmit, receive, multicast, queue, and QP bookkeeping so an `RDMA_NETDEV_IPOIB` device can use HFI1 SDMA and receive contexts.

## Important APIs, types, and functions
- `qpn_from_mac()` derives the local QPN from the IPoIB MAC address bytes 1..3.
- `hfi1_ipoib_dev_init()` and `hfi1_ipoib_dev_uninit()` delegate to the original netdev ops and register or remove the netdev in `dd->netdev_rx->dev_tbl` by QPN.
- `hfi1_ipoib_dev_open()` opens the underlying IPoIB device, looks up the matching rdmavt QP under RCU, pins it in `priv->qp`, then enables HFI1 RX queues and TX NAPI.
- `hfi1_ipoib_dev_stop()` disables TX NAPI and RX queues, drops the QP reference, and calls the original `ndo_stop`.
- `hfi1_ipoib_mcast_attach()` and `hfi1_ipoib_mcast_detach()` locate the QP and call `ib_attach_mcast()` or `ib_detach_mcast()`.
- `hfi1_ipoib_setup_rn()` fills `struct rdma_netdev` callbacks, initializes `struct hfi1_ipoib_dev_priv`, allocates TX and RX resources, and replaces `netdev->netdev_ops`.
- `hfi1_ipoib_rn_get_params()` is the exported capability hook used by the RDMA core to request HFI1 accelerated IPoIB parameters.

## Control flow
The RDMA core calls `hfi1_ipoib_rn_get_params()` for `RDMA_NETDEV_IPOIB`. The function rejects unsupported netdev types, disabled AIP capability, devices without netdev receive contexts, and invalid ports. It then reports private-data size, TX queue count from `dd->num_sdma`, RX queue count from `dd->num_netdev_contexts`, and `hfi1_ipoib_setup_rn()` as the initializer.

During netdev setup, the file preserves the original IPoIB `netdev_ops` in `priv->netdev_ops`, installs HFI1 send, multicast, timeout, and P_Key callbacks in `struct rdma_netdev`, initializes TX request rings first, initializes the accelerated RX path second, and finally substitutes a small HFI1 `net_device_ops` wrapper. Open and stop are symmetric around the QP reference and queue enable state: the original IPoIB open must succeed before HFI1 looks up the QP, and a failed QP lookup unwinds by stopping the original netdev.

## State and persistence
The main persistent in-memory state is `struct hfi1_ipoib_dev_priv`: original netdev ops, device/port pointers, P_Key state, Q_Key, QP reference, and TX/RX resources. The QPN-to-netdev xarray entry in `netdev_rx` is created at `ndo_init` and erased at `ndo_uninit`, so receive demultiplexing depends on the MAC-derived QPN remaining stable. No state is persisted across driver unload or reboot.

## Dependencies and integration points
This file integrates with RDMA netdev allocation, generic IPoIB netdev callbacks, rdmavt QP lookup/reference APIs, HFI1 netdev RX helpers, HFI1 IPoIB TX/RX helpers, multicast verbs, and P_Key queries. It assumes HFI1 AIP capability and receive contexts were configured by broader device initialization.

## Risks
- MAC-derived QPN mapping is central to RX demultiplexing; MAC address changes after registration would need careful synchronization with `dev_tbl`.
- `hfi1_ipoib_dev_stop()` returns early when `priv->qp` is NULL, so callers rely on the failed-open path having already stopped the original netdev.
- Multicast attach/detach and open independently look up the QP; races with QP teardown depend on correct RCU and rdmavt reference behavior.
- Setup changes `netdev->netdev_ops` only after TX/RX initialization; future initialization changes must preserve this unwind ordering.

## Test signals
- Build with HFI1 AIP/IPoIB enabled and verify `hfi1_ipoib_rn_get_params()` rejects non-IPoIB types, disabled AIP, zero netdev contexts, and invalid ports.
- Exercise interface open/close, including failed QP lookup, and confirm RX queues, TX NAPI, and QP references are balanced.
- Validate VLAN or child IPoIB devices that depend on QPN registration in `hfi1_netdev_add_data()`.
- Test multicast join/leave paths with valid and missing QPs.
