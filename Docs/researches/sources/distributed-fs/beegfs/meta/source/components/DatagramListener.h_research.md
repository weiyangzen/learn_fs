# sources/distributed-fs/beegfs/meta/source/components/DatagramListener.h

Purpose: The header declares the metadata-specific `DatagramListener`, a thin subclass of `AbstractDatagramListener`.

Important APIs/types: The constructor accepts `NetFilter*`, `NicAddressList&`, `AcknowledgmentStore*`, UDP port, and `restrictOutboundInterfaces`. The protected override `handleIncomingMsg(struct sockaddr*, NetMessage*)` provides metadata-server dispatch filtering.

Control flow and state: Most runtime behavior and state live in the abstract base class. This subclass exists to name the component and restrict/dispatch incoming message types according to metadata server context.

Dependencies/integration: `App` owns a `DatagramListener*`, exposes it via `getDatagramListener()`, updates its NIC list on interface changes, and stops it during shutdown with `sendDummyToSelfUDP()` to wake the receive loop. `InternodeSyncer` and `ModificationEventFlusher` use the datagram listener for UDP-with-ack communication.

Risks and test signals: The narrow header makes ownership and lifetime the main risk: consumers store raw pointers, so the listener must outlive users like the modification flusher. Behavioral coverage depends on tests for the `.cpp` dispatch and base listener.
