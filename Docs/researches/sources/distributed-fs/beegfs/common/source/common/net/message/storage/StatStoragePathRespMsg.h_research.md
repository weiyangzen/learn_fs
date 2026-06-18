# sources/distributed-fs/beegfs/common/source/common/net/message/storage/StatStoragePathRespMsg.h

## Purpose
Defines `StatStoragePathRespMsg`, the response payload wrapper for BeeGFS storage target operation RPCs using `NETMSGTYPE_StatStoragePathResp`. It records server results, returned records, or continuation state while leaving request handling to daemon-specific processors.

## Important APIs, Types, And Functions
`StatStoragePathRespMsg` derives from `public NetMessageSerdes<StatStoragePathRespMsg>` and uses `BaseType(NETMSGTYPE_StatStoragePathResp)` or an equivalent base constructor. Constructors include `StatStoragePathRespMsg(int result, int64_t sizeTotal, int64_t sizeFree, int64_t inodesTotal, int64_t inodesFree) : BaseType(NETMSGTYPE_StatStoragePathResp)`; `StatStoragePathRespMsg() : BaseType(NETMSGTYPE_StatStoragePathResp)`. Serialization writes `result`, `sizeTotal`, `sizeFree`, `inodesTotal`, `inodesFree`. Notable accessors/helpers include `getResult()`, `getSizeTotal()`, `getSizeFree()`, `getInodesTotal()`, `getInodesFree()`. Declared payload/backing members include `int32_t result`, `int64_t sizeTotal`, `int64_t sizeFree`, `int64_t inodesTotal`, `int64_t inodesFree`.

## Control Flow
Sender-side code builds `StatStoragePathRespMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/Common.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the storage target operation code path that handles `NETMSGTYPE_StatStoragePathResp`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Wire-format drift between serialize order, constructor defaults, and handlers is the main risk.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_StatStoragePathResp`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
