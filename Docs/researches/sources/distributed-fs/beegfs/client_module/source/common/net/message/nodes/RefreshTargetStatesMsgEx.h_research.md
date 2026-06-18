# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.h

## Research
`RefreshTargetStatesMsgEx.h` declares the receive-only refresh-target-states message. It embeds `NetMessage`, stores an ack ID pointer/length, initializes with `NETMSGTYPE_RefreshTargetStates`, and exposes `RefreshTargetStatesMsgEx_getAckID`.

Control flow is init and accessor use; deserialization and processing are in the `.c` file. State is a receive-buffer-backed string with no owned resources. Dependencies are `NetMessage.h` and `Common.h`. Integration points are management-driven target state refresh notifications and `InternodeSyncer`. Risks are accidental serialization use, empty ack IDs, and no payload versioning beyond the message type. Test signals are deserialized ack IDs and forced syncer refresh after dispatch.
