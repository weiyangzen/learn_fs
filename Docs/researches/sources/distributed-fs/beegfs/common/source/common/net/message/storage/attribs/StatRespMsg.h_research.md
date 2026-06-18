# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/StatRespMsg.h

## Purpose
Defines `StatRespMsg`, the response payload wrapper for BeeGFS metadata and storage attributes RPCs using `NETMSGTYPE_StatResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StatRespMsg` derives from `public NetMessageSerdes<StatRespMsg>` and uses `BaseType(NETMSGTYPE_StatResp)` or an equivalent base constructor. Constructors include `StatRespMsg(int result, StatData statData) : BaseType(NETMSGTYPE_StatResp)`; `StatRespMsg() : BaseType(NETMSGTYPE_StatResp)`. Serialization writes `result`, `statData`, `stringAlign4(obj->parentEntryID)`, `parentNodeID`. Notable accessors/helpers include `isMsgHeaderFeatureFlagSet()`, `getSupportedHeaderFeatureFlagsMask()`, `getResult()`, `getStatData()`, `getParentNodeID()`. Declared payload/backing members include `int32_t result`, `StatData statData`, `NumNodeID parentNodeID`, `std::string parentEntryID`.

## Control Flow
Sender-side code builds `StatRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/NumNodeID.h`, `common/storage/Metadata.h`, `common/storage/StatData.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_StatResp`. Feature flags: `STATRESPMSG_FLAG_HAS_PARENTINFO`=1.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StatResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`.
