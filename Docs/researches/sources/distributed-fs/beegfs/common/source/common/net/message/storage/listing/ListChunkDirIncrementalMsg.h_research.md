# sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListChunkDirIncrementalMsg.h

## Purpose
Defines `ListChunkDirIncrementalMsg`, a BeeGFS directory and chunk listing query/request message using `NETMSGTYPE_ListChunkDirIncremental`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`ListChunkDirIncrementalMsg` derives from `public NetMessageSerdes<ListChunkDirIncrementalMsg>` and uses `BaseType(NETMSGTYPE_ListChunkDirIncremental)` or an equivalent base constructor. Constructors include `ListChunkDirIncrementalMsg(uint16_t targetID, bool isMirror, const std::string& relativeDir, int64_t offset, unsigned maxOutEntries, bool onlyFiles, bool ignoreNotExists) : BaseType(NETMSGTYPE_ListChunkDirIncremental), targetID(targetID), isMirror(isMirror), relativeDir(relativeDir), offset(offset), maxOutEntries(maxOutEntries), onlyFiles(onlyFiles), ignoreNotExists(ignoreNotExists)`; `ListChunkDirIncrementalMsg() : BaseType(NETMSGTYPE_ListChunkDirIncremental)`. Serialization writes `stringAlign4(obj->relativeDir)`, `targetID`, `isMirror`, `offset`, `maxOutEntries`, `onlyFiles`, `ignoreNotExists`. Notable accessors/helpers include `isMirror()`, `getTargetID()`, `getIsMirror()`, `getOffset()`, `getMaxOutEntries()`, `getRelativeDir()`, `getOnlyFiles()`, `getIgnoreNotExists()`. Declared payload/backing members include `uint16_t targetID`, `bool isMirror`, `std::string relativeDir`, `int64_t offset`, `uint32_t maxOutEntries`, `bool onlyFiles`, `bool ignoreNotExists`.

## Control Flow
Sender-side code builds `ListChunkDirIncrementalMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/net/message/storage/listing/ListChunkDirIncrementalRespMsg.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the directory and chunk listing code path that handles `NETMSGTYPE_ListChunkDirIncremental`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_ListChunkDirIncremental`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
