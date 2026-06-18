# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.c

## Research
`GetStatesAndBuddyGroupsRespMsg.c` implements receive-only deserialization and cleanup for combined buddy group and target state responses. The release hook frees deserialized `BuddyGroupMapping` and `TargetStateMapping` list elements with `BEEGFS_KFREE_LIST`. Payload deserialization reads a buddy group mapping list followed by a target state mapping list.

Control flow is list-deserialize then list-deserialize; failure leaves any already allocated list entries to be cleaned by message release. State is two Linux list heads owned by the message after deserialization. Dependencies are `GetStatesAndBuddyGroupsRespMsg.h`, `Types.h` list serializers, and `Common.h` cleanup macros. Integration points are mirror buddy group mapper and target state store updates. Risks are memory leaks if the release hook is bypassed, partial-deserialization cleanup, and wire-order drift. Test signals are `NETMESSAGE_FREE` releasing both lists, correct mapper/state-store updates, and malformed list failure without leaks.
