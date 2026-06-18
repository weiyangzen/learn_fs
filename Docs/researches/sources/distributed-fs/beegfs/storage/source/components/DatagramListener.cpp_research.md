## sources/distributed-fs/beegfs/storage/source/components/DatagramListener.cpp

Purpose: Handles UDP datagrams accepted by the storage daemon and dispatches only message types valid in this context.

Important APIs/types/functions: Constructor forwards network filters, NIC list, ack store, UDP port, and outbound-interface restriction to `AbstractDatagramListener`. `handleIncomingMsg()` resolves sender socket, builds `NetMessage::ResponseContext`, switches on message type, and invokes `processIncoming()` for allowed control/state messages.

Control flow: If no sender socket is found for the source IP, it logs and drops. Allowed messages include ack/dummy, heartbeat, target mapping/capacity/state refresh, remove node, storage pool refresh, and mirror buddy group changes. Disallowed message types are logged as invalid context.

State and persistence: No persistence. Uses inherited send buffer/socket state and ack machinery.

Dependencies and integration: Depends on common datagram listener, IP address handling, net message types, and BeeGFS logging. Created and owned by `App`; used by registration and internode sync operations.

Risks and test signals: Missing a valid UDP control message in the switch would cause runtime rejection. Tests should verify allowed/disallowed message dispatch and behavior when `findSenderSock()` returns null.
