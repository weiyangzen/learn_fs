# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/RetrieveInodesMsg.h

## Purpose
Defines `RetrieveInodesMsg`, a BeeGFS fsck repair and audit query/request message using `NETMSGTYPE_RetrieveInodes`. It packages selectors, offsets, target identifiers, or entry metadata for transport through the common binary `NetMessage` format.

## Important APIs, Types, And Functions
`RetrieveInodesMsg` derives from `public NetMessageSerdes<RetrieveInodesMsg>` and uses `BaseType(NETMSGTYPE_RetrieveInodes)` or an equivalent base constructor. Constructors include `RetrieveInodesMsg(unsigned hashDirNum, int64_t lastOffset, unsigned maxOutInodes, bool isBuddyMirrored): BaseType(NETMSGTYPE_RetrieveInodes), hashDirNum(hashDirNum), lastOffset(lastOffset), maxOutInodes(maxOutInodes), isBuddyMirrored(isBuddyMirrored)`; `RetrieveInodesMsg() : BaseType(NETMSGTYPE_RetrieveInodes)`. Serialization writes `hashDirNum`, `lastOffset`, `maxOutInodes`, `isBuddyMirrored`. Notable accessors/helpers include `isBuddyMirrored()`, `getHashDirNum()`, `getLastOffset()`, `getMaxOutInodes()`, `getIsBuddyMirrored()`. Declared payload/backing members include `uint32_t hashDirNum`, `int64_t lastOffset`, `uint32_t maxOutInodes`, `bool isBuddyMirrored`.

## Control Flow
Sender-side code builds `RetrieveInodesMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler.

## Dependencies And Integration Points
Includes `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_RetrieveInodes`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Offset cursors can repeat or skip records if callers mishandle continuation; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_RetrieveInodes`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering. Check empty result, boundary, and continuation cursor behavior.
