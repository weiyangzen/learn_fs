# sources/distributed-fs/beegfs/common/source/common/net/message/storage/attribs/GetChunkFileAttribsMsg.h

## Purpose
Defines `GetChunkFileAttribsMsg`, a BeeGFS metadata and storage attributes query/request message using `NETMSGTYPE_GetChunkFileAttribs`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`GetChunkFileAttribsMsg` derives from `public NetMessageSerdes<GetChunkFileAttribsMsg>` and uses `BaseType(NETMSGTYPE_GetChunkFileAttribs)` or an equivalent base constructor. Constructors include `GetChunkFileAttribsMsg(const std::string& entryID, uint16_t targetID, PathInfo* pathInfo) : BaseType(NETMSGTYPE_GetChunkFileAttribs)`; `GetChunkFileAttribsMsg() : BaseType(NETMSGTYPE_GetChunkFileAttribs)`. Serialization writes `rawString(obj->entryID, obj->entryIDLen, 4)`, `backedPtr(obj->pathInfoPtr, obj->pathInfo)`, `targetID`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getEntryID()`, `getTargetID()`, `getPathInfo()`. Declared payload/backing members include `unsigned entryIDLen`, `const char* entryID`, `uint16_t targetID`, `PathInfo* pathInfoPtr`, `PathInfo pathInfo`.

## Control Flow
Sender-side code builds `GetChunkFileAttribsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization. Feature flags become part of message state because they decide whether optional fields appear on the wire.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/PathInfo.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the metadata and storage attributes code path that handles `NETMSGTYPE_GetChunkFileAttribs`. Feature flags: `GETCHUNKFILEATTRSMSG_FLAG_BUDDYMIRROR`=1, `GETCHUNKFILEATTRSMSG_FLAG_BUDDYMIRROR_SECOND`=2.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; serialization pointers and deserialized backing storage have different ownership rules; feature flag mismatches change the expected wire layout; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_GetChunkFileAttribs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Exercise each local feature flag both absent and present, plus unsupported-flag rejection through `checkHeaderFeatureFlagsCompat()`. Check empty result, boundary, and continuation cursor behavior.
