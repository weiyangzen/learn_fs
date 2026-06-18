# sources/distributed-fs/ceph-client/include/linux/sunrpc/xprtsock.h

Purpose: declares the socket-backed SUNRPC client transport provider and its private transport state.

Important APIs and types: lifecycle APIs are `init_socket_xprt()` and `cleanup_socket_xprt()`. Reserved port bounds/defaults define privileged source port selection. `struct sock_xprt` embeds `rpc_xprt` and stores socket, sock, backing file, TCP receive fragment/XID/calldir/offset/length/copied state, transmit offset, socket state bits, connect/error/recv workers, receive mutex, handshake completion, source address/port, last transport error, owning client, UDP buffer sizes, TCP timeout, and saved socket callbacks. State bits include connecting, data ready, timeout update, wake error/write/pending/disconnect, connect sent, no space, and ignore receive.

Control flow: socket transports initialize and register, connect asynchronously, receive stream fragments into the RPC receive state machine, transmit partial records using offsets, handle socket callbacks through workers, and restore callbacks during teardown.

State and persistence: socket transport state is per-transport runtime state tied to sockets, workers, callbacks, and connection progress.

Dependencies and integration points: integrates with `rpc_xprt`, socket layer callbacks, workqueues, handshake support, RPC client, and TCP/UDP timeout behavior.

Risks and test signals: risks include callback races, receive worker reentrancy, fragment header parsing, partial-send offset bugs, reserved-port exhaustion, and handshake completion deadlocks. Test TCP and UDP RPC, reconnects, socket errors, TLS handshake paths, partial sends, and cleanup under active traffic.
