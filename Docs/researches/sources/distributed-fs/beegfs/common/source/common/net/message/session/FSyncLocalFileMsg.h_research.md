# sources/distributed-fs/beegfs/common/source/common/net/message/session/FSyncLocalFileMsg.h

## Purpose
Defines `FSyncLocalFileMsg`, a BeeGFS session lifecycle command message using `NETMSGTYPE_FSyncLocalFile`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`FSyncLocalFileMsg` derives from `public NetMessageSerdes<FSyncLocalFileMsg>` and uses `BaseType(NETMSGTYPE_FSyncLocalFile)` or an equivalent base constructor. Constructors include `FSyncLocalFileMsg(const NumNodeID sessionID, const char* fileHandleID, const uint16_t targetID) : BaseType(NETMSGTYPE_FSyncLocalFile)`; `FSyncLocalFileMsg() : BaseType(NETMSGTYPE_FSyncLocalFile)`. Serialization writes `sessionID`, `rawString(obj->fileHandleID, obj->fileHandleIDLen, 4)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getSessionID()`, `getFileHandleID()`, `getTargetID()`. Declared payload/backing members include `NumNodeID sessionID`, `const char* fileHandleID`, `unsigned fileHandleIDLen`, `uint16_t targetID`.

## Control Flow
Sender-side code builds `FSyncLocalFileMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session lifecycle code path that handles `NETMSGTYPE_FSyncLocalFile`. Feature flags: `FSYNCLOCALFILEMSG_FLAG_NO_SYNC`=1, `FSYNCLOCALFILEMSG_FLAG_SESSION_CHECK`=2, `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR`=4, `FSYNCLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND`=8.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; feature flag mismatches change the expected wire layout.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_FSyncLocalFile`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
