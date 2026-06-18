# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `GetXAttrRespMsg.c`, carrying xattr value buffer, returned size, and return code.

Important APIs/types/functions: Key declarations are GetXAttrRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if (!Serialization_deserializeCharArray(ctx, &thisCast->valueBufLen,; if (!Serialization_deserializeInt(ctx, &thisCast->size) ); if (!Serialization_deserializeInt(ctx, &thisCast->returnCode) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
