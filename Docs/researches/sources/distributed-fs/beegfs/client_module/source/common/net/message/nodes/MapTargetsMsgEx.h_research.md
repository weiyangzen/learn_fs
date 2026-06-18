# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.h

## Research
`MapTargetsMsgEx.h` declares the receive-only map-targets message. It embeds `NetMessage`, stores a `NumNodeID`, ack ID pointer/length, and a list of `TargetPoolMapping` entries. Initialization sets `NETMSGTYPE_MapTargets` and initializes the list head.

Control flow is init and accessor use; receive processing and release are in the `.c` file. State includes owned deserialized list entries and receive-buffer-backed ack string. Dependencies are `NetMessage.h`, `Common.h`, and `StoragePoolId.h`. Integration points are management-driven target mapping updates into the client `TargetMapper`. Risks are serialization intentionally unimplemented, list lifetime, and consumer assumptions that all mappings refer to the same node ID. Test signals are deserialization of multiple target mappings and release cleanup.
