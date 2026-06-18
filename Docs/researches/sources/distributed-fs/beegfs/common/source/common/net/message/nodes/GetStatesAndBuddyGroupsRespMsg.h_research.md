# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h

## Purpose
Defines `GetStatesAndBuddyGroupsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetStatesAndBuddyGroupsRespMsg` derives from `public NetMessageSerdes<GetStatesAndBuddyGroupsRespMsg>` and uses `BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp)` or an equivalent base constructor. Constructors include `GetStatesAndBuddyGroupsRespMsg(const MirrorBuddyGroupMap& groups, const TargetStateMap& states) : BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp), groups(&groups), states(&states)`; `GetStatesAndBuddyGroupsRespMsg() : BaseType(NETMSGTYPE_GetStatesAndBuddyGroupsResp)`. Serialization writes `backedPtr(obj->groups, obj->parsed.groups)`, `backedPtr(obj->states, obj->parsed.states)`. Notable accessors/helpers include `getGroups()`, `getStates()`. Declared payload/backing members include `const MirrorBuddyGroupMap* groups`, `const TargetStateMap* states`, `MirrorBuddyGroupMap groups`, `TargetStateMap states`.

## Control Flow
Sender-side code builds `GetStatesAndBuddyGroupsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`, `common/nodes/MirrorBuddyGroup.h`, `common/nodes/TargetStateInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetStatesAndBuddyGroupsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
