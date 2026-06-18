# sources/distributed-fs/beegfs/common/source/common/net/message/session/AckNotifyMsg.h

## Purpose
Defines `AckNotifiyMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_AckNotify`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`AckNotifiyMsg` derives from `public MirroredMessageBase<AckNotifiyMsg>` and uses `BaseType(NETMSGTYPE_AckNotify)` or an equivalent base constructor. Constructors include `AckNotifiyMsg(): BaseType(NETMSGTYPE_AckNotify)`. Payload serialization is empty or delegated to an inherited helper type. Notable accessors/helpers include `supportsMirroring()`. No standalone payload members are declared in this class; payload storage is inherited or empty.

## Control Flow
Sender-side code builds `AckNotifiyMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_AckNotify`. Buddy mirroring is part of the contract, with primary/secondary payload differences guarded by `Flag_BuddyMirrorSecond` where used.

## Risks And Edge Cases
Buddy-mirror forwarding requires the primary to fill replay-only fields correctly.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_AckNotify`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Cover primary and secondary buddy-mirror layouts, including replay IDs and mirrored timestamps.
