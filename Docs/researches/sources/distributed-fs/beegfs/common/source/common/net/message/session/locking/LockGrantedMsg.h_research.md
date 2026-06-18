# sources/distributed-fs/beegfs/common/source/common/net/message/session/locking/LockGrantedMsg.h

## Purpose
Defines `LockGrantedMsg`, a BeeGFS session locking command message using `NETMSGTYPE_LockGranted`. It serializes operation parameters and identifiers for the receiving management, metadata, or storage daemon.

## Important APIs, Types, And Functions
`LockGrantedMsg` derives from `public AcknowledgeableMsgSerdes<LockGrantedMsg>` and uses `BaseType(NETMSGTYPE_LockGranted)` or an equivalent base constructor. Constructors include `LockGrantedMsg(const std::string& lockAckID, const std::string& ackID, NumNodeID granterNodeID) : BaseType(NETMSGTYPE_LockGranted, ackID.c_str())`; `LockGrantedMsg() : BaseType(NETMSGTYPE_LockGranted)`. Serialization writes `rawString(obj->lockAckID, obj->lockAckIDLen, 4)`, `granterNodeID`. Notable accessors/helpers include `serializeAckID()`, `getLockAckID()`, `getGranterNodeID()`. Declared payload/backing members include `unsigned lockAckIDLen`, `const char* lockAckID`, `NumNodeID granterNodeID`.

## Control Flow
Sender-side code builds `LockGrantedMsg` with operation parameters or result values, then BeeGFS serializes the static `serialize(This, Ctx&)` payload after the common `NetMessageHeader`. Receiver-side code constructs the default/deserialization form and dispatches the message type through the BeeGFS factory to daemon handlers outside this header. Conditional fields, when present, are selected by message feature flags, acknowledgement helpers, or buddy-mirror header state.

## State And Persistence
The header itself performs no persistence; durable state is the serialized BeeGFS wire payload and any state changes later made by the handler. String fields serialize explicit lengths/alignment and must remain valid for the lifetime of send-side serialization.

## Dependencies And Integration Points
Includes `common/net/message/AcknowledgeableMsg.h`, `common/nodes/NumNodeID.h`. Integrates with BeeGFS `NetMessage`/serdes dispatch and the session locking code path that handles `NETMSGTYPE_LockGranted`. Acknowledgement IDs can be carried through `AcknowledgeableMsgSerdes`.

## Risks And Edge Cases
String payloads are length/alignment-sensitive.

## Test Signals
Compile a target that includes this header and registers or uses `NETMSGTYPE_LockGranted`. Round-trip serialize/deserialize populated payloads and verify accessor-visible values, result codes, and list ordering.
