# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

## Research
`SetMirrorBuddyGroupMsgEx.h` declares the receive-only mirror buddy group update message. It embeds `NetMessage` and stores node type, primary/secondary target IDs, buddy group ID, allow-update flag, and ack ID. Inline getters expose each field, and initialization sets `NETMSGTYPE_SetMirrorBuddyGroup`.

Control flow is init/access plus `.c` deserialization/processing. State is fixed-size, with ack ID referencing the receive buffer. Dependencies are `NetMessage.h`. Integration points are storage and metadata mirror group mapper updates initiated by management. Risks include no outgoing serialization, invalid node-type handling, and lifetime of ack ID. Test signals are deserialization of all fields and correct mapper selection for storage versus metadata.
