<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h

Purpose: defines the AF_RXRPC socket ABI, including sockaddr layout, socket options, control messages, security levels/indices, abort codes, and challenge payloads.

Important APIs, types, and functions: `struct sockaddr_rxrpc` wraps an RxRPC service ID and an IPv4/IPv6 datagram transport address. Socket options include `RXRPC_SECURITY_KEY`, `RXRPC_SECURITY_KEYRING`, `RXRPC_MIN_SECURITY_LEVEL`, service upgrade, supported-cmsg discovery, and managed response. `enum rxrpc_cmsg_type` defines sendmsg/recvmsg control messages such as `RXRPC_USER_CALL_ID`, `RXRPC_ABORT`, `RXRPC_ACK`, `RXRPC_NEW_CALL`, exclusive call, timeouts, challenge/response, and appdata. Security constants cover plain/auth/encrypt levels and RXKAD/RXGK/RXK5/YFS indices. Abort codes cover local RxRPC, rxgen, RXKAD, and RXGK failures. `struct rxrpc_challenge` and `rxgk_challenge` describe challenge metadata.

Control flow: userspace binds or connects AF_RXRPC sockets with `sockaddr_rxrpc`, configures security material with socket options, uses control messages to identify calls and manage call lifecycle, receives terminal ACK/abort/error notifications, and may respond to security challenges when managed response is enabled.

State and persistence behavior: call, connection, key, timeout, and service-upgrade state lives in AF_RXRPC sockets and kernel keyrings. User call IDs are application-owned tags that can be recycled after terminal messages. This header only defines the ABI.

Dependencies and integration points: includes Linux types and IPv4/IPv6 address headers. It integrates with AF_RXRPC, keyrings, Kerberos/RXKAD/RXGK security, AFS/YFS filesystems, and sendmsg/recvmsg cmsg handling.

Risks and edge cases: control-message applicability differs for client/server and send/receive paths. Terminal messages affect user call ID reuse. Security abort code compatibility with OpenAFS/YFS matters. Variable security-class challenge data follows fixed challenge prefixes, so bounds validation is required.

Test signals: AF_RXRPC client/server calls with no security, RXKAD, and RXGK; cmsg parsing for user call IDs and aborts; service upgrade; managed challenge/response; timeout notifications; IPv4 and IPv6 transports; and malformed cmsg length tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rxrpc.h -->
