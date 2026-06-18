# sources/distributed-fs/beegfs/common/source/common/net/message/storage/creating/RmChunkPathsMsg.h

## Purpose
Defines `RmChunkPathsMsg`, a BeeGFS namespace mutation command message using `NETMSGTYPE_RmChunkPaths`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`RmChunkPathsMsg` derives from `public NetMessageSerdes<RmChunkPathsMsg>` and uses `BaseType(NETMSGTYPE_RmChunkPaths)` or an equivalent base constructor. Constructors include `RmChunkPathsMsg(uint16_t targetID, StringList* relativePaths) : BaseType(NETMSGTYPE_RmChunkPaths)`; `RmChunkPathsMsg() : BaseType(NETMSGTYPE_RmChunkPaths)`. Serialization writes `targetID`, `backedPtr(obj->relativePaths, obj->parsed.relativePaths)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getTargetID()`, `getRelativePaths()`. Declared payload/backing members include `uint16_t targetID`, `StringList* relativePaths`, `StringList relativePaths`.

## Control Flow
Sender-side code builds `RmChunkPathsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/toolkit/serialization/Serialization.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the namespace mutation code path that handles `NETMSGTYPE_RmChunkPaths`. Feature flags: `RMCHUNKPATHSMSG_FLAG_BUDDYMIRROR`=1.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RmChunkPaths`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
