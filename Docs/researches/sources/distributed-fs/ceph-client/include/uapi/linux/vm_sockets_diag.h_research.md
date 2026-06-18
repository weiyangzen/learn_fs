<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h

Purpose: defines the sock_diag request and response structures for querying open AF_VSOCK sockets.

Important APIs and types: `struct vsock_diag_req` carries family, protocol, state bitmap, reserved inode/show fields, and cookie. `struct vsock_diag_msg` returns family, socket type, state, shutdown bits, source/destination CID and port, inode, and cookie.

Control flow, state, and persistence: userspace sends a netlink sock_diag request and receives one message per matching vsock. It snapshots kernel socket state but stores no persistent data.

Dependencies and integration points: integrates AF_VSOCK with sock_diag/netlink tooling such as `ss` and diagnostics libraries.

Risks and test signals: risks include state bitmap mismatch with TCP-style socket states, reserved field validation, cookie uniqueness, and missing socket types. Test listen/connected/closed sockets, stream and datagram if supported, shutdown flags, and filtered state queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vm_sockets_diag.h -->
