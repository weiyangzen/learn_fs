# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveDirEntriesMsg.h

## Purpose
Defines `RetrieveDirEntriesMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveDirEntries`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveDirEntriesMsg` derives from `public NetMessageSerdes<RetrieveDirEntriesMsg>` and uses `BaseType(NETMSGTYPE_RetrieveDirEntries)` or an equivalent base constructor. Constructors include `RetrieveDirEntriesMsg(unsigned hashDirNum, std::string& currentContDirID, unsigned maxOutEntries, int64_t lastHashDirOffset, int64_t lastContDirOffset, bool isBuddyMirrored) : BaseType(NETMSGTYPE_RetrieveDirEntries)`; `RetrieveDirEntriesMsg() : BaseType(NETMSGTYPE_RetrieveDirEntries)`. Serialization writes `hashDirNum`, `rawString(obj->currentContDirID, obj->currentContDirIDLen)`, `maxOutEntries`, `lastHashDirOffset`, `lastContDirOffset`, `isBuddyMirrored`. Notable accessors/helpers include `getCurrentContDirID()`, `getHashDirNum()`, `getLastContDirOffset()`, `getLastHashDirOffset()`, `getMaxOutEntries()`, `getIsBuddyMirrored()`. Declared payload/backing members include `uint32_t hashDirNum`, `unsigned currentContDirIDLen`, `uint32_t maxOutEntries`, `int64_t lastHashDirOffset`, `int64_t lastContDirOffset`, `bool isBuddyMirrored`.

## Control Flow
Sender-side code builds `RetrieveDirEntriesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveDirEntries`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveDirEntries`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
