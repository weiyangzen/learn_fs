# sources/distributed-fs/ceph-client/include/rdma/lag.h

Purpose: Declares RDMA LAG helpers for choosing and releasing RoCE transmit slave netdevices for address handles.

Important APIs/types/functions: `enum rdma_lag_flags` with `RDMA_LAG_FLAGS_HASH_ALL_SLAVES`, `rdma_lag_get_ah_roce_slave`, and `rdma_lag_put_ah_roce_slave`.

Control flow: AH creation or transmit setup asks for a RoCE slave based on device and AH attributes, then later releases the returned netdevice through the put helper.

State and persistence behavior: The header owns no state, but the get/put contract implies referenced runtime `net_device` objects. Policy flags are stored on the RDMA device.

Dependencies and integration points: Depends on Linux LAG support, `ib_device`, and `rdma_ah_attr`. Integrates with RoCE address-handle and send paths.

Risks: Missing put leaks netdevice references. Bond membership changes require correct reference/RCU handling. Hash policy can affect packet ordering and path distribution.

Test signals: Reference balance, no-slave handling, bond membership changes, and hash-all-slaves policy behavior.
