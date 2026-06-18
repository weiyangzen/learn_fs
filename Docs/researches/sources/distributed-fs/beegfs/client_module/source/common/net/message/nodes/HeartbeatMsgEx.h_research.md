# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.h

## Research
`HeartbeatMsgEx.h` declares the concrete heartbeat message. It stores node identity, type, numeric IDs, root information, versions, ports, ack ID, machine UUID, a non-owned outgoing NIC list, and a raw deserialized NIC list. Inline helpers initialize node-data heartbeats, parse NIC lists, get identity fields, and set/get ports.

Control flow is construction and accessor logic; complex receive behavior is in the `.c` file. State is mixed ownership: outgoing strings/NIC lists are caller-owned, deserialized strings/raw lists are receive-buffer backed. Dependencies are `NetMessage.h` and `NetworkInterfaceCard.h`. Integration points are heartbeat request responses, node discovery, datagram listener processing, and internode sync. Risks include lifetime of aliases/NIC lists during serialization, zero/undefined ports, root fields being meaningful only for metadata nodes, and typo-prone reserved version fields. Test signals are serialized heartbeat payload order, NIC list parse correctness, and node-store updates after receive.
