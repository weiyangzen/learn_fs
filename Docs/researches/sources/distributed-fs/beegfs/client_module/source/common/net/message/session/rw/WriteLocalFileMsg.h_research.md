# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.h

Purpose: Declares the BeeGFS kernel-client message type `WriteLocalFileMsg` and its in-memory fields for write offset/count/access flags, optional quota user/group IDs, file handle, client node ID, path info, and target ID.

Important APIs/types/functions: Key declarations are WriteLocalFileMsg_init, WriteLocalFileMsg_initFromSession, WriteLocalFileMsg_serializePayload, WriteLocalFileMsg_setUserdataForQuota. Structs in scope are WriteLocalFileMsg. Feature/compat flags: WRITELOCALFILEMSG_FLAG_SESSION_CHECK=1; WRITELOCALFILEMSG_FLAG_USE_QUOTA=2; WRITELOCALFILEMSG_FLAG_DISABLE_IO=4; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR=8; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND=16; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_FORWARD=32.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
