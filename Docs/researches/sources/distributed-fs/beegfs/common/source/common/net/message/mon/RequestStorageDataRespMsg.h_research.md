# sources/distributed-fs/beegfs/common/source/common/net/message/mon/RequestStorageDataRespMsg.h

## Purpose
Defines `RequestStorageDataRespMsg`, the response payload wrapper for BeeGFS monitoring RPCs using `NETMSGTYPE_RequestStorageDataResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`RequestStorageDataRespMsg` derives from `public NetMessageSerdes<RequestStorageDataRespMsg>` and uses `BaseType(NETMSGTYPE_RequestStorageDataResp)` or an equivalent base constructor. Constructors include `RequestStorageDataRespMsg(const std::string& nodeID, const std::string& hostnameid, NumNodeID nodeNumID, NicAddressList *nicList, unsigned indirectWorkListSize, unsigned directWorkListSize, int64_t diskSpaceTotal, int64_t diskSpaceFree, unsigned sessionCount, HighResStatsList* statsList, StorageTargetInfoList *storageTargets) : BaseType(NETMSGTYPE_RequestStorageDataResp)`; `RequestStorageDataRespMsg() : BaseType(NETMSGTYPE_RequestStorageDataResp)`. Serialization writes `nodeID`, `hostnameid`, `nodeNumID`, `serdesNicAddressList(obj->nicList, obj->parsed.nicList)`, `indirectWorkListSize`, `directWorkListSize`, `diskSpaceTotalMiB`, `diskSpaceFreeMiB`, `sessionCount`, `backedPtr(obj->statsList, obj->parsed.statsList)`, `backedPtr(obj->storageTargets, obj->parsed.storageTargets)`. Notable accessors/helpers include `getSupportedHeaderFeatureFlagsMask()`, `getNicList()`, `getStatsList()`, `getStorageTargets()`, `getNodeID()`, `gethostnameid()`, `getNodeNumID()`, `getIndirectWorkListSize()`, `getDirectWorkListSize()`, `getDiskSpaceTotalMiB()`, `getDiskSpaceFreeMiB()`, `getSessionCount()`. Declared payload/backing members include `static const unsigned NODE_SUPPORTS_IPV6`, `std::string nodeID`, `std::string hostnameid`, `NumNodeID nodeNumID`, `NicAddressList* nicList`, `uint32_t indirectWorkListSize`, `uint32_t directWorkListSize`, `int64_t diskSpaceTotalMiB`, `int64_t diskSpaceFreeMiB`, `uint32_t sessionCount`, `StorageTargetInfoList storageTargets`, `HighResStatsList statsList`, `NicAddressList nicList`, `HighResStatsList* statsList`.

## Control Flow
Sender-side code builds `RequestStorageDataRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/nodes/Node.h`, `common/storage/StorageDefinitions.h`, `common/storage/StorageTargetInfo.h`, `common/toolkit/HighResolutionStats.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the monitoring code path that handles `NETMSGTYPE_RequestStorageDataResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RequestStorageDataResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
