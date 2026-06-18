# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.h

Purpose: Declares the BeeGFS kernel-client message type `LookupIntentMsg` and its in-memory fields for lookup/revalidate/create/open/stat intent flags, parent entry, name, optional meta version and entry info, open access flags, quota/create fields, preferred targets, and optional file event.

Important APIs/types/functions: Key declarations are LookupIntentMsg_init, LookupIntentMsg_initFromName, LookupIntentMsg_initFromEntryInfo, LookupIntentMsg_serializePayload, LookupIntentMsg_addIntentCreate, LookupIntentMsg_addIntentCreateExclusive, LookupIntentMsg_addIntentOpen, LookupIntentMsg_addIntentStat. Structs in scope are LookupIntentMsg. Feature/compat flags: LOOKUPINTENTMSG_FLAG_REVALIDATE=1; LOOKUPINTENTMSG_FLAG_CREATE=2; LOOKUPINTENTMSG_FLAG_CREATEEXCLUSIVE=4; LOOKUPINTENTMSG_FLAG_OPEN=8; LOOKUPINTENTMSG_FLAG_STAT=16; LOOKUPINTENTMSG_FLAG_USE_QUOTA=1; LOOKUPINTENTMSG_FLAG_BUDDYMIRROR=2; LOOKUPINTENTMSG_FLAG_BUDDYMIRROR_SECOND=4.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
