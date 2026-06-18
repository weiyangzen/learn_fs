<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h

Purpose: defines the Qualcomm IPC Router userspace socket address and control-packet ABI.

Important APIs and types: `QRTR_NODE_BCAST` and `QRTR_PORT_CTRL` define broadcast/control endpoints. `struct sockaddr_qrtr` carries address family, node, and port. `enum qrtr_pkt_type` identifies data, hello/bye, server/client add/delete, resume, exit, ping, and lookup messages. `struct qrtr_ctrl_pkt` carries little-endian command plus server or client endpoint payload.

Control flow: userspace binds/connects QRTR sockets using `sockaddr_qrtr`; control messages announce services and clients through the control port. Kernel QRTR routes data/control packets between local clients, remote nodes, and transports.

State and persistence: QRTR node/port mappings, service lookup registrations, and transport state are runtime IPC state. No persistent state is defined.

Dependencies and integration points: depends on socket and Linux type headers. Integrates with Qualcomm modem/remoteproc services, AF_QIPCRTR sockets, service discovery, and QRTR transports.

Risks and test signals: risks include endpoint spoofing, stale service records, endian mistakes in control packets, and broadcast storms. Test service registration/lookup, remote node connect/disconnect, malformed control packets, and socket address validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qrtr.h -->
