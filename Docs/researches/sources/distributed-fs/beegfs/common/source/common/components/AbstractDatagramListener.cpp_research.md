<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp

### Purpose
`AbstractDatagramListener.cpp` implements the shared UDP datagram listener for BeeGFS messages, including socket binding, interface-restricted sending, receive parsing, ack retry helpers, and self-wakeup.

### Important APIs, Types, And Functions
Core methods are `configSocket`, `initSocks`, `initBuffers`, `findSenderSock`, `findSenderSockUnlocked`, `setLocalNicList`, `run`, `listenLoop`, `sendToNodesUDP`, `sendToNodesUDPwithAck`, `sendToNodeUDPwithAck`, `sendBufToNode`, `sendMsgToNode`, `sendDummyToSelfUDP`, `incAckCounter`, and `isDGramFromSelf`.

### Control Flow
Construction initializes sockets immediately and throws on failure. Runtime allocates aligned send/receive buffers, then loops on `recvfromT`. Incoming datagrams from local addresses/port are ignored; remaining buffers are parsed by the app net message factory, validated for type, length, and sequence fields, then dispatched to subclass `handleIncomingMsg`. Sending selects either a wildcard UDP socket or a per-interface socket based on routing-table matches when outbound restriction is enabled. Ack sends register wait IDs, send to remaining nodes, wait, retry, and unregister.

### State, Persistence, And Dependencies
State includes UDP socket group, per-interface sockets, destination-to-source cache, routing table, local NIC list, net filter, ack store, aligned buffers, receive timeout, mutex, and ack counter. No durable state is written. Dependencies include `PThread`, `AbstractApp`, `MessagingTk`, serialization, `DummyMsg`, `StandardSocket`, node stores, and routing.

### Integration Points
Derived listeners such as `RegistrationDatagramListener` implement message policy. Nodes and management flows use UDP multicast-style sends and ack tracking for control-plane messages.

### Risks
The listener uses a single mutex for intertwined send/routing/socket state; long socket operations under this lock can affect concurrency. `sendto` wrappers return positive errno constants like `ENETUNREACH` rather than negative error returns, so callers treat only `>0` as sent in some paths. `initBuffers` ignores allocation failures and could leave null buffers. Cached route choices must be cleared when local NICs change, which `initSocks` does only in restricted mode.

### Test Signals
Tests should cover unrestricted and restricted binding, route cache invalidation on NIC updates, self-datagram filtering, invalid message rejection, ack retry/unregister behavior, net filter exclusion, dummy self-wakeup, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp -->
