# sources/distributed-fs/beegfs/meta/source/components/DatagramListener.cpp

Purpose: This file implements the metadata server UDP/datagram listener's message dispatch policy.

Important APIs/functions: The constructor forwards listener name, network filter, local NIC list, acknowledgment store, UDP port, and outbound-interface restriction to `AbstractDatagramListener`. `handleIncomingMsg()` resolves a sender socket, builds a `NetMessage::ResponseContext`, and dispatches only message types valid for metadata datagram handling.

Control flow: Incoming messages are rejected if no sender socket exists. Valid message types include Ack, Dummy, heartbeat request/response, target mapping, capacity publish/refresh, node removal, storage pool refresh, target state refresh, and mirror buddy group updates. For valid types, `processIncoming()` is called and failures are logged. All other message types are logged as invalid in this context.

State and persistence behavior: The listener maintains inherited socket/send-buffer state and uses `AcknowledgmentStore` for UDP acknowledgments. It does not persist data directly; processed messages can mutate node stores, mappings, capacity pools, or target states through their handlers.

Dependencies/integration: It depends on `AbstractDatagramListener`, `NetMessage` dispatch, IP address handling, and message type definitions. `App` creates it before `InternodeSyncer` and `ModificationEventFlusher`; the flusher uses it to send fsck modification-event messages.

Risks and test signals: The allowlist is a security and correctness boundary. New UDP control messages must be added intentionally, otherwise they will be rejected. There is no local unit test in this subset for dispatch allowlisting or missing socket behavior.
