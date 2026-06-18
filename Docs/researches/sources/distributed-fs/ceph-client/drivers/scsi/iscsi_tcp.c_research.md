# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.c

Purpose: implements the software iSCSI-over-TCP initiator transport data path, connecting libiscsi/libiscsi_tcp session and PDU machinery to a userspace-supplied TCP socket.

Important APIs and functions: socket callbacks are installed/restored by `iscsi_sw_tcp_conn_set_callbacks()` and `_restore_callbacks()`. Receive runs through `iscsi_sw_tcp_data_ready()`, optional `recvwork`, `tcp_read_sock()`, and `iscsi_tcp_recv_skb()`. Transmit is driven by `iscsi_sw_tcp_pdu_init()`, header/data prep helpers, `iscsi_sw_tcp_pdu_xmit()`, and `iscsi_sw_tcp_xmit_segment()`. Transport callbacks create/destroy sessions and connections, bind sockets, set/get params, gather stats, and register as `iscsi_transport` named `tcp`.

Control flow: userspace creates a session, creates a connection, and binds a TCP socket fd. Bind validates TCP, binds libiscsi connection state, stores the socket under `sock_lock`, tunes socket flags, installs callbacks, and primes header receive state. Data-ready either reads in softirq callback context or queues `recvwork`. Write-space chains to the old callback and queues iSCSI transmit. Stop suspends TX, shuts down the socket, restores callbacks, suspends RX, clears the pointer, and calls `iscsi_conn_stop()`.

State and persistence: runtime state is in `iscsi_sw_tcp_conn`: socket pointer, callback backups, mutex, work item, send segment, digest CRCs, and counters. Session state is linked through `iscsi_sw_tcp_host`. No on-disk persistence; parameters are exposed through transport sysfs/netlink.

Dependencies and integration: depends on TCP sockets, SCSI host/session lifecycle, libiscsi task management, libiscsi_tcp segment/digest helpers, tracepoints, and block queue limits. Data digest enables stable writes in `sdev_configure()`.

Risks and test signals: callback locking and socket lifetime are the main hazards, especially stop/destroy races with data-ready and param reads. Test digest on/off, queued versus softirq receive, partial sends/EAGAIN, socket close with pending receive memory, bind failure, local/peer address reads, module unload, and stable-write feature with data digests.
