# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.c

Purpose: transport-specific helper layer for usNIC custom RoCE port allocation and UDP socket inspection.

Important APIs/functions: `usnic_transport_to_str()`, `usnic_transport_sock_to_str()`, `usnic_transport_rsrv_port()`, `usnic_transport_unrsrv_port()`, `usnic_transport_get_socket()`, `usnic_transport_put_socket()`, `usnic_transport_sock_get_addr()`, `usnic_transport_init()`, and `usnic_transport_fini()`.

Control flow: module init allocates a bitmap and reserves port 0. QP group creation reserves a custom RoCE port or gets a referenced socket from a user FD, extracts AF_INET/protocol/address/port, and later releases the port/socket on flow teardown. Port 0 requests auto-allocate from `roce_next_port`.

State and persistence: global `roce_bitmap`, `roce_next_port`, and spinlock track reserved custom RoCE ports for the module lifetime. UDP socket references persist in QP group flow objects.

Dependencies and integration: depends on Linux bitmaps, socket fd lookup, inet socket access, and usNIC ABI transport enums. Integrated by QP group flow creation and debugfs formatting.

Risks: `ROCE_BITMAP_SZ` is expressed as bytes but passed as bit count to bitmap helpers, limiting allocation to 8192 bits rather than all 16-bit ports. Auto-allocation wraps through the low 4096 range via `(port_num & 4095) + 1`. Socket address extraction only supports AF_INET and trusts `sock->ops->getname()`.

Test signals: custom port reserve/free including collisions and port 0 auto-allocation, UDP socket fd reference/release, non-UDP and non-IPv4 rejection, transport debugfs string output, and module unload leak checks.
