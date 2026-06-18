# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestMetaDataRespMsg.h

## Purpose
Defines `RequestMetaDataRespMsg`, the response payload wrapper for BeeGFS monitoring RPCs using `NETMSGTYPE_RequestMetaDataResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RequestMetaDataRespMsg` derives from `public NetMessageSerdes<RequestMetaDataRespMsg>` and uses `BaseType(NETMSGTYPE_RequestMetaDataResp)` or an equivalent base constructor. Constructors include `RequestMetaDataRespMsg(const std::string& nodeID, const std::string& hostnameid, NumNodeID nodeNumID, NicAddressList *nicList, bool isRoot, unsigned IndirectWorkListSize, unsigned DirectWorkListSize, unsigned sessionCount, HighResStatsList* statsList) : BaseType(NETMSGTYPE_RequestMetaDataResp)`; `RequestMetaDataRespMsg() : BaseType(NETMSGTYPE_RequestMetaDataResp)`. Serialization writes `nodeID`, `hostnameid`, `nodeNumID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `isRoot`, `indirectWorkListSize`, `directWorkListSize`, `sessionCount`, `backedPtr(obj->statsList, obj->parsed.statsList)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getNicList()`, `getStatsList()`, `getNodeID()`, `gethostnameid()`, `getNodeNumID()`, `getIsRoot()`, `getIndirectWorkListSize()`, `getDirectWorkListSize()`, `getSessionCount()`. Declared payload/backing members include `static const unsigned USE_CLIENT_STATS_V2`, `std::string nodeID`, `std::string hostnameid`, `NumNodeID nodeNumID`, `bool isRoot`, `uint32_t indirectWorkListSize`, `uint32_t directWorkListSize`, `uint32_t sessionCount`, `NicAddressList* nicList`, `HighResStatsList* statsList`, `HighResStatsList statsList`, `NicAddressList nicList`.

## Control Flow
Sender-side code builds `RequestMetaDataRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestMetaDataResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestMetaDataResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
