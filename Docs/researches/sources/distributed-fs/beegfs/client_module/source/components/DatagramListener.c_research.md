# sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.c

## Purpose
Implements the UDP datagram listener/sender thread for management heartbeats, node updates, locking notifications, target-state refresh, and other lightweight messages.

## Important APIs and control flow
`__DatagramListener_run` allocates NUMA-local buffers and enters `__DatagramListener_listenLoop`. The loop receives datagrams with timeout, ignores empty/timeout cases, rejects localhost-origin datagrams on the same UDP port, constructs a `NetMessage`, validates header length/sequence, and dispatches allowed message types through `processIncoming`. Ack messages are explicitly ignored to avoid noisy false errors. `__DatagramListener_initSock` creates a UDP socket, enables broadcast, sets receive buffer size, and binds. `DatagramListener_sendMsgToNode` serializes a message and sends it to every standard NIC of a node that passes `NetFilter`. Send calls are mutex-serialized through header inlines.

## State, dependencies, integration
State includes UDP socket, local node, net filter, send/receive buffers, UDP port, and send mutex. It integrates with `InternodeSyncer` for heartbeat send/receive and with message handlers for cluster updates.

## Risks and test signals
`NetMessageFactory_createFromBuf` is assumed to return a non-null message object. Localhost filtering depends on local NIC list and UDP port. Tests should cover invalid headers, ignored ack messages, allowed/disallowed message types, net-filtered sends, bind failure cleanup, and self-datagram suppression.
