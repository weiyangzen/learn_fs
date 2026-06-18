# sources/distributed-fs/ceph-client/drivers/scsi/iscsi_tcp.h

Purpose: declares private data structures for the software iSCSI TCP transport.

Important APIs and types: `struct iscsi_sw_tcp_send` contains the current outgoing header pointer, active segment, and data segment. `struct iscsi_sw_tcp_conn` stores the bound socket, `sock_lock`, receive work and queuing flag, outgoing send state, original socket callbacks, TX/RX CRC accumulators, and custom stats counters. `struct iscsi_sw_tcp_host` links a SCSI host to its iSCSI session. `struct iscsi_sw_tcp_hdrbuf` reserves a base iSCSI header plus AHS and digest space for task headers.

Control flow role: `iscsi_tcp.c` allocates these as per-connection, per-host, and per-task private areas through libiscsi setup calls. Send prep writes into `out.segment`/`out.data_segment`; callback installation uses the saved function pointers to restore the socket later.

State and persistence: all structures are in-memory lifecycle state tied to sessions, connections, and tasks. The socket pointer is guarded for netlink/sysfs access by `sock_lock`.

Dependencies and integration: includes `libiscsi.h` and `libiscsi_tcp.h`, and relies on kernel socket, workqueue, mutex, and CRC types.

Risks and test signals: structure sizing must match allocations in `iscsi_tcp_conn_setup()` and task `dd_data`; header max calculations reserve digest space. Validate that every successful callback install has a restore path and that stats fields remain coherent across reconnects.
