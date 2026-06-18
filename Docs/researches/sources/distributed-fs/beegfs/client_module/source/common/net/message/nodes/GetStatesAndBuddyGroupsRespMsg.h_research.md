# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h

## Research
`GetStatesAndBuddyGroupsRespMsg.h` declares the receive-side response carrying two maps: buddy group ID to primary/secondary target IDs, and target ID to reachability/consistency state. It embeds `NetMessage` and owns two `struct list_head` containers for `BuddyGroupMapping` and `TargetStateMapping`.

Control flow initializes both lists and relies on the `.c` ops for deserialization and release. State is owned list elements allocated by serializers. Dependencies include `NetMessage.h`, `Common.h`, and `Types.h`. Integration points are management-sync logic, `MirrorBuddyGroupMapper`, and `TargetStateStore`. Risks are using the lists after message free, forgetting release, and keeping the structure wire-compatible with server common code. Test signals are list contents matching management state and cleanup under kmemleak or fault-injection tests.
