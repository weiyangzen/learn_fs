# sources/distributed-fs/beegfs/common/source/common/net/message/fsck/UpdateDirAttribsMsg.h

## Purpose
Defines `UpdateDirAttribsMsg`, a BeeGFS fsck repair and audit command message using `NETMSGTYPE_UpdateDirAttribs`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`UpdateDirAttribsMsg` derives from `public NetMessageSerdes<UpdateDirAttribsMsg>` and uses `BaseType(NETMSGTYPE_UpdateDirAttribs)` or an equivalent base constructor. Constructors include `UpdateDirAttribsMsg(FsckDirInodeList* inodes) : BaseType(NETMSGTYPE_UpdateDirAttribs)`; `UpdateDirAttribsMsg() : BaseType(NETMSGTYPE_UpdateDirAttribs)`. Serialization writes `backedPtr(obj->inodes, obj->parsed.inodes)`. Notable accessors/helpers include `getInodes()`. Declared payload/backing members include `FsckDirInodeList* inodes`, `FsckDirInodeList inodes`.

## Control Flow
Sender-side code builds `UpdateDirAttribsMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. Send-side pointer members are aliases, while deserialization fills owned parsed/backing members.

## Dependencies And Integration Points
Includes `common/fsck/FsckDirInode.h`, `common/net/message/NetMessage.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the fsck repair and audit code path that handles `NETMSGTYPE_UpdateDirAttribs`. No local feature flags are declared; the payload layout is fixed for this message type.

## Risks And Edge Cases
Serialization pointers and deserialized backing storage have different ownership rules; handlers may mutate cluster metadata, target state, or filesystem namespace.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_UpdateDirAttribs`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
