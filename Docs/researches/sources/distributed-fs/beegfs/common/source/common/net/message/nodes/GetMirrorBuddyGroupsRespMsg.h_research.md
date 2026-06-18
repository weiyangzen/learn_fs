# sources/distributed-fs/beegfs/common/source/common/net/message/nodes/GetMirrorBuddyGroupsRespMsg.h

## Purpose
Defines `GetMirrorBuddyGroupsRespMsg`, the response payload wrapper for BeeGFS node and target management RPCs using `NETMSGTYPE_GetMirrorBuddyGroupsResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`GetMirrorBuddyGroupsRespMsg` derives from `public NetMessageSerdes<GetMirrorBuddyGroupsRespMsg>` and uses `BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)` or an equivalent base constructor. Constructors include `GetMirrorBuddyGroupsRespMsg(UInt16List* buddyGroupIDs, UInt16List* primaryTargetIDs, UInt16List* secondaryTargetIDs) : BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)`; `GetMirrorBuddyGroupsRespMsg() : BaseType(NETMSGTYPE_GetMirrorBuddyGroupsResp)`. Serialization writes `backedPtr(obj->buddyGroupIDs, obj->parsed.buddyGroupIDs)`, `backedPtr(obj->primaryTargetIDs, obj->parsed.primaryTargetIDs)`, `backedPtr(obj->secondaryTargetIDs, obj->parsed.secondaryTargetIDs)`. Notable accessors/helpers include `getBuddyGroupIDs()`, `getPrimaryTargetIDs()`, `getSecondaryTargetIDs()`. Declared payload/backing members include `UInt16List* buddyGroupIDs`, `UInt16List* primaryTargetIDs`, `UInt16List* secondaryTargetIDs`, `UInt16List buddyGroupIDs`, `UInt16List primaryTargetIDs`, `UInt16List secondaryTargetIDs`.

## Control Flow
Sender-side code builds `GetMirrorBuddyGroupsRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/Common.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the node and target management code path that handles `NETMSGTYPE_GetMirrorBuddyGroupsResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetMirrorBuddyGroupsResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
