# sources/distributed-fs/ceph-client/net/llc/af_llc.c

## Purpose
`af_llc.c` implements the PF_LLC socket user interface. It supports connectionless LLC class 1 through `SOCK_DGRAM` and connection-oriented LLC2 through `SOCK_STREAM`, including bind, autobind, connect, listen, accept, send, receive, shutdown, and socket options.

## Important APIs, Types, and Functions
The file defines `llc_proto`, `llc_ui_family_ops`, and `llc_ui_ops`. Major functions include `llc_ui_create()`, `llc_ui_release()`, `llc_ui_bind()`, `llc_ui_autobind()`, `llc_ui_connect()`, `llc_ui_listen()`, `llc_ui_accept()`, `llc_ui_sendmsg()`, `llc_ui_recvmsg()`, `llc_ui_shutdown()`, `llc_ui_setsockopt()`, and `llc_ui_getsockopt()`. Helpers manage dynamic SAP allocation, link numbers, waits for connection/disconnect/busy conditions, packet-info control messages, and LLC header sizing.

## Control Flow
Create checks `CAP_NET_RAW`, rejects non-init network namespaces, and allocates an `llc_sock`. Bind resolves an Ethernet device and SAP, opens or finds the SAP, checks address conflicts, stores device/local address, and inserts the socket into the SAP. Connect requires stream sockets, autobinds if needed, stores destination address, sends SABME through `llc_establish_connection()`, and optionally waits for state to leave `TCP_SYN_SENT`. Listen marks a bound stream socket as `TCP_LISTEN`. Accept dequeues child sockets from the listener receive queue and grafts them to the new socket. Send builds an skb sized to device MTU and dispatches UI, TEST, XID, or LLC2 data. Receive implements stream-style byte consumption or datagram one-packet delivery with optional source address and packet-info cmsg.

## State and Persistence
State lives in `struct llc_sock` and `struct sock`: SAP pointer, device and netdev tracker, local/destination LLC addresses, copied receive sequence, LLC2 timers/options, socket state, and receive queues. Dynamic SAP and link counters are static process-wide kernel state.

## Dependencies and Integration Points
The file integrates with LLC SAP/connection handlers, PDU builders, netdevice lookup, socket core, proc/sysctl initialization, and packet dispatch registration through `llc_add_pack()`. It restricts operation to `init_net`.

## Risks and Edge Cases
Socket lifetime is complex: release may send DISC, wait, remove from SAP, hold SAP across `release_sock()`, drop netdev references, orphan, and free the LLC socket. Send temporarily drops the socket lock while allocating skb and revalidates device/header/MTU assumptions afterward. Autobind modifies the user-provided sockaddr. Namespace restriction and CAP_NET_RAW checks are intentional security boundaries.

## Test Signals
Exercise bind/autobind with fixed and dynamic SAPs, address conflict detection, datagram UI/TEST/XID send, stream connect/listen/accept/send/recv/shutdown, nonblocking connect and send-busy waits, cmsg packet-info, release during active connection, and init_net/CAP_NET_RAW rejection paths.
