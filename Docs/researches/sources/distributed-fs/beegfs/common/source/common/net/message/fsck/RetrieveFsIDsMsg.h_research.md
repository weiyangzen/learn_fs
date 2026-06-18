# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveFsIDsMsg.h

## Purpose
Defines `RetrieveFsIDsMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveFsIDs`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveFsIDsMsg` derives from `public NetMessageSerdes<RetrieveFsIDsMsg>` and uses `BaseType(NETMSGTYPE_RetrieveFsIDs)` or an equivalent base constructor. Constructors include `RetrieveFsIDsMsg(unsigned hashDirNum, bool buddyMirrored, std::string& currentContDirID, unsigned maxOutIDs, int64_t lastHashDirOffset, int64_t lastContDirOffset) : BaseType(NETMSGTYPE_RetrieveFsIDs)`; `RetrieveFsIDsMsg() : BaseType(NETMSGTYPE_RetrieveFsIDs)`. Serialization writes `hashDirNum`, `buddyMirrored`, `rawString(obj->currentContDirID, obj->currentContDirIDLen)`, `maxOutIDs`, `lastHashDirOffset`, `lastContDirOffset`. Notable accessors/helpers include `getCurrentContDirID()`, `getHashDirNum()`, `getBuddyMirrored()`, `getLastContDirOffset()`, `getLastHashDirOffset()`, `getMaxOutIDs()`. Declared payload/backing members include `uint32_t hashDirNum`, `bool buddyMirrored`, `unsigned currentContDirIDLen`, `uint32_t maxOutIDs`, `int64_t lastHashDirOffset`, `int64_t lastContDirOffset`.

## Control Flow
Sender-side code builds `RetrieveFsIDsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`, `common/storage/Path.h`, `common/storage/StorageDefinitions.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveFsIDs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
String payloads are length/alignment-sensitive; offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveFsIDs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
