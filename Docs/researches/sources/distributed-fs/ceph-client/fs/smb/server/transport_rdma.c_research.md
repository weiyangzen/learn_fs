## sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.c

Purpose: adapts the common `smbdirect` RDMA socket implementation to ksmbd's server transport interface. It starts SMB Direct listeners, accepts RDMA clients, creates ksmbd connections, and implements read/write/RDMA read/RDMA write transport operations.

Important APIs and functions: exported functions include `init_smbd_max_io_size`, `get_smbd_max_read_write_size`, `ksmbd_rdma_init`, `ksmbd_rdma_stop_listening`, and `ksmbd_rdma_capable_netdev`. Internal functions allocate/free transports, wrap `smbdirect_connection_recvmsg`, `smbdirect_connection_send_iter`, and `smbdirect_connection_rdma_xmit`, manage listener kthreads, configure SMB Direct socket parameters, and translate debug logging.

Control flow: `ksmbd_rdma_init` initializes two listeners: port 445 for InfiniBand/RoCE and port 5445 for iWARP. Each listener creates a kernel SMBDirect socket, sets negotiation, credit, send/receive, read/write, keepalive, polling, and logging parameters, binds and listens, then starts an accept kthread. Accepted sockets are wrapped in `struct smb_direct_transport`, a ksmbd connection is allocated and inserted into the connection hash, and a per-connection handler thread is launched. Transport ops pass normal SMB messages or RDMA payloads through the SMBDirect socket.

State and persistence behavior: runtime state consists of listener sockets/threads, per-connection `smb_direct_transport` objects, negotiated SMBDirect socket parameters, and a configurable max read/write size clamped between 512 KiB and 16 MiB. No persistent storage is written.

Dependencies and integration points: depends on `linux/smbdirect.h`, RDMA/InfiniBand availability, ksmbd connection allocation/handler loop, global connection list locking, SMB common sizing setup via IPC startup, and netdev RDMA capability reporting for SMB2 network-interface info.

Risks: listener startup is all-or-nothing and must destroy both listeners on partial failure. Port flags intentionally split iWARP and IB/RoCE behavior. Accepted transport cleanup must release both SMBDirect socket and ksmbd connection exactly once. The transport only reports max RDMA I/O size for its own ops table, so callers must handle TCP returning zero.

Test signals: `CONFIG_SMB_SERVER_SMBDIRECT` builds, listener startup/teardown on systems with and without RDMA devices, port 445 and 5445 binding failures, accepted client connection thread launch, negotiated max read/write size clamp, RDMA read/write success and failure paths, keepalive timeout, and network-interface capability reporting.
