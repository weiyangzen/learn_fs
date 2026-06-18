<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h -->
# sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h

## Purpose
Defines the RDMA userspace connection manager ABI for `/dev/infiniband/rdma_cm`: command IDs, port spaces, command payloads, connection parameters, multicast, events, options, migration, IB service resolution, and event injection structures.

## Important APIs, Types, and Functions
Read coverage: 381 lines and 7961 bytes. Visible type families include enum rdma_ucm_port_space, struct rdma_ucm_cmd_hdr, struct rdma_ucm_create_id, struct rdma_ucm_create_id_resp, struct rdma_ucm_destroy_id, struct rdma_ucm_destroy_id_resp, struct rdma_ucm_bind_ip, struct sockaddr_in6, struct rdma_ucm_bind, struct __kernel_sockaddr_storage, struct rdma_ucm_resolve_ip, struct rdma_ucm_resolve_addr, struct rdma_ucm_resolve_route, struct rdma_ucm_query, struct rdma_ucm_query_route_resp, struct ib_user_path_rec, struct rdma_ucm_query_addr_resp, struct rdma_ucm_query_path_resp, struct ib_path_rec_data, struct rdma_ucm_query_ib_service_resp, struct ib_user_service_rec, struct rdma_ucm_conn_param, struct rdma_ucm_ud_param, struct ib_uverbs_ah_attr, struct rdma_ucm_ece, struct rdma_ucm_connect, struct rdma_ucm_listen, struct rdma_ucm_accept, ... (+14 more). Important macros/constants include RDMA_USER_CM_H, RDMA_USER_CM_ABI_VERSION, RDMA_MAX_PRIVATE_DATA, RDMA_USER_CM_IB_SERVICE_NAME_SIZE. Explicit ioctl-style command names include none.

## Control Flow
Userspace creates an ID, binds or resolves addresses/routes, queries route/address/path data, listens or connects, accepts/rejects/disconnects, initializes QP attributes, joins/leaves multicast, reads events, sets options, migrates IDs between fds, and handles IB service resolution or written CM events.

## State and Persistence Behavior
Kernel state includes CM IDs, route resolution, event queues, QP association, private data, multicast memberships, ECE data, options, and file ownership. Events report asynchronous state transitions and carry response payloads.

## Dependencies and Integration Points
It depends on Linux integer and socket storage types. It integrates with rdma_cm, cma, ib_cm/iw_cm, RDMA providers, multicast, and rdma-core/librdmacm. Direct includes are #include <linux/types.h>, #include <linux/socket.h>, #include <linux/in6.h>, #include <rdma/ib_user_verbs.h>, #include <rdma/ib_user_sa.h>.

## Risks and Edge Cases
Private data is capped at 256 bytes, sockaddr storage layouts must remain compatible, event ordering and ACK semantics are critical, and ID migration changes ownership/lifetime. Port-space and option enums must remain stable.

## Test Signals
Run librdmacm tests for resolve/connect/listen/accept/reject/disconnect, multicast join/leave, event read/ack ordering, ID migration, ECE/private-data limits, IPv4/IPv6/IB service resolution, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/rdma/rdma_user_cm.h -->
