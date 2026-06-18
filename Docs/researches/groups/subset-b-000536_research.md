# Research Group: subset-b-000536

This grouped report covers the requested BeeGFS client kernel-module message, socket, RDMA, NIC, and mirror-buddy files. Each section is wrapped with exact source-path markers for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `OpenFileRespMsg.c`, carrying open-file results, file handle ID, `PathInfo`, preprocessed stripe pattern bytes, file version, and file state.

Important APIs/types/functions: Key declarations are OpenFileRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeInt(ctx, &thisCast->result) ); if(!Serialization_deserializeStrAlign4(ctx, &thisCast->fileHandleIDLen,; if (!PathInfo_deserialize(ctx, &thisCast->pathInfo) ); if (!Serialization_deserializeUInt(ctx, &thisCast->fileVersion)); if (!Serialization_deserializeUInt8(ctx, &thisCast->fileState)). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `OpenFileRespMsg` and its in-memory fields for open-file results, file handle ID, `PathInfo`, preprocessed stripe pattern bytes, file version, and file state.

Important APIs/types/functions: Key declarations are OpenFileRespMsg_init, OpenFileRespMsg_deserializePayload, OpenFileRespMsg_createPattern, OpenFileRespMsg_getResult, OpenFileRespMsg_getFileHandleID. Structs in scope are OpenFileRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ReadLocalFileRDMAMsg.c`, carrying read offset/count/access flags, file handle, client node ID, path info, target ID, and `RdmaInfo` remote buffer metadata.

Important APIs/types/functions: Key declarations are ReadLocalFileRDMAMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->offset); Serialization_serializeInt64(ctx, thisCast->count); Serialization_serializeUInt(ctx, thisCast->accessFlags); Serialization_serializeStrAlign4(ctx, thisCast->fileHandleIDLen, thisCast->fileHandleID); NumNodeID_serialize(ctx, &thisCast->clientNumID); PathInfo_serialize(ctx, thisCast->pathInfoPtr); Serialization_serializeUShort(ctx, thisCast->targetID); RdmaInfo_serialize(ctx, thisCast->rdmap). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h

Purpose: Declares the BeeGFS kernel-client message type `ReadLocalFileRDMAMsg` and its in-memory fields for read offset/count/access flags, file handle, client node ID, path info, target ID, and `RdmaInfo` remote buffer metadata.

Important APIs/types/functions: Key declarations are ReadLocalFileRDMAMsg_init, ReadLocalFileRDMAMsg_initFromSession, ReadLocalFileRDMAMsg_serializePayload. Structs in scope are ReadLocalFileRDMAMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileRDMAMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ReadLocalFileV2Msg.c`, carrying read offset/count/access flags, file handle, client node ID, path info, and target ID.

Important APIs/types/functions: Key declarations are ReadLocalFileV2Msg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->offset); Serialization_serializeInt64(ctx, thisCast->count); Serialization_serializeUInt(ctx, thisCast->accessFlags); Serialization_serializeStrAlign4(ctx, thisCast->fileHandleIDLen, thisCast->fileHandleID); NumNodeID_serialize(ctx, &thisCast->clientNumID); PathInfo_serialize(ctx, thisCast->pathInfoPtr); Serialization_serializeUShort(ctx, thisCast->targetID). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.h

Purpose: Declares the BeeGFS kernel-client message type `ReadLocalFileV2Msg` and its in-memory fields for read offset/count/access flags, file handle, client node ID, path info, and target ID.

Important APIs/types/functions: Key declarations are ReadLocalFileV2Msg_init, ReadLocalFileV2Msg_initFromSession, ReadLocalFileV2Msg_serializePayload. Structs in scope are ReadLocalFileV2Msg. Feature/compat flags: READLOCALFILEMSG_FLAG_SESSION_CHECK=1; READLOCALFILEMSG_FLAG_DISABLE_IO=2; READLOCALFILEMSG_FLAG_BUDDYMIRROR=4; READLOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND=8.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/ReadLocalFileV2Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `WriteLocalFileMsg.c`, carrying write offset/count/access flags, optional quota user/group IDs, file handle, client node ID, path info, and target ID.

Important APIs/types/functions: Key declarations are WriteLocalFileMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->offset); Serialization_serializeInt64(ctx, thisCast->count); Serialization_serializeUInt(ctx, thisCast->accessFlags); Serialization_serializeUInt(ctx, thisCast->userID); Serialization_serializeUInt(ctx, thisCast->groupID); Serialization_serializeStrAlign4(ctx, thisCast->fileHandleIDLen, thisCast->fileHandleID); NumNodeID_serialize(ctx, &thisCast->clientNumID); PathInfo_serialize(ctx, thisCast->pathInfo). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.h

Purpose: Declares the BeeGFS kernel-client message type `WriteLocalFileMsg` and its in-memory fields for write offset/count/access flags, optional quota user/group IDs, file handle, client node ID, path info, and target ID.

Important APIs/types/functions: Key declarations are WriteLocalFileMsg_init, WriteLocalFileMsg_initFromSession, WriteLocalFileMsg_serializePayload, WriteLocalFileMsg_setUserdataForQuota. Structs in scope are WriteLocalFileMsg. Feature/compat flags: WRITELOCALFILEMSG_FLAG_SESSION_CHECK=1; WRITELOCALFILEMSG_FLAG_USE_QUOTA=2; WRITELOCALFILEMSG_FLAG_DISABLE_IO=4; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR=8; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_SECOND=16; WRITELOCALFILEMSG_FLAG_BUDDYMIRROR_FORWARD=32.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `WriteLocalFileRDMAMsg.c`, carrying write offset/count/access flags, optional quota user/group IDs, file handle, client node ID, path info, target ID, and `RdmaInfo`.

Important APIs/types/functions: Key declarations are WriteLocalFileRDMAMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->offset); Serialization_serializeInt64(ctx, thisCast->count); Serialization_serializeUInt(ctx, thisCast->accessFlags); Serialization_serializeUInt(ctx, thisCast->userID); Serialization_serializeUInt(ctx, thisCast->groupID); Serialization_serializeStrAlign4(ctx, thisCast->fileHandleIDLen, thisCast->fileHandleID); NumNodeID_serialize(ctx, &thisCast->clientNumID); PathInfo_serialize(ctx, thisCast->pathInfo). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h

Purpose: Declares the BeeGFS kernel-client message type `WriteLocalFileRDMAMsg` and its in-memory fields for write offset/count/access flags, optional quota user/group IDs, file handle, client node ID, path info, target ID, and `RdmaInfo`.

Important APIs/types/functions: Key declarations are WriteLocalFileRDMAMsg_init, WriteLocalFileRDMAMsg_initFromSession, WriteLocalFileRDMAMsg_serializePayload, WriteLocalFileRDMAMsg_setUserdataForQuota. Structs in scope are WriteLocalFileRDMAMsg. Feature/compat flags: WRITELOCALFILERDMAMSG_FLAG_SESSION_CHECK=1; WRITELOCALFILERDMAMSG_FLAG_USE_QUOTA=2; WRITELOCALFILERDMAMSG_FLAG_DISABLE_IO=4; WRITELOCALFILERDMAMSG_FLAG_BUDDYMIRROR=8; WRITELOCALFILERDMAMSG_FLAG_BUDDYMIRROR_SECOND=16; WRITELOCALFILERDMAMSG_FLAG_BUDDYMIRROR_FORWARD=32.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMAMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleInt64Msg` for `WriteLocalFileRDMARespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are WriteLocalFileRDMARespMsg_init. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRDMARespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleInt64Msg` for `WriteLocalFileRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are WriteLocalFileRespMsg_init. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/rw/WriteLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleUInt16Msg` for `StatStoragePathMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are StatStoragePathMsg_init, StatStoragePathMsg_initFromTarget. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `StatStoragePathRespMsg.c`, carrying storage-path status plus total/free bytes and inode counters.

Important APIs/types/functions: Key declarations are StatStoragePathRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeInt(ctx, &thisCast->result) ); if(!Serialization_deserializeInt64(ctx, &thisCast->sizeTotal) ); if(!Serialization_deserializeInt64(ctx, &thisCast->sizeFree) ); if(!Serialization_deserializeInt64(ctx, &thisCast->inodesTotal) ); if(!Serialization_deserializeInt64(ctx, &thisCast->inodesFree) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `StatStoragePathRespMsg` and its in-memory fields for storage-path status plus total/free bytes and inode counters.

Important APIs/types/functions: Key declarations are StatStoragePathRespMsg_init, StatStoragePathRespMsg_deserializePayload. Structs in scope are StatStoragePathRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/StatStoragePathRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `TruncFileMsg.c`, carrying new file size, target `EntryInfo`, optional quota feature flag, and optional file-event audit record.

Important APIs/types/functions: Key declarations are TruncFileMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->filesize); EntryInfo_serialize(ctx, thisCast->entryInfoPtr); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.h

Purpose: Declares the BeeGFS kernel-client message type `TruncFileMsg` and its in-memory fields for new file size, target `EntryInfo`, optional quota feature flag, and optional file-event audit record.

Important APIs/types/functions: Key declarations are TruncFileMsg_init, TruncFileMsg_initFromEntryInfo, TruncFileMsg_serializePayload. Structs in scope are TruncFileMsg. Feature/compat flags: TRUNCFILEMSG_FLAG_USE_QUOTA=1; TRUNCFILEMSG_FLAG_HAS_EVENT=2.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `TruncFileRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are TruncFileRespMsg_init, TruncFileRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/TruncFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `GetXAttrMsg.c`, carrying entry info, xattr name, and requested value buffer size.

Important APIs/types/functions: Key declarations are GetXAttrMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeStr(ctx, strlen(thisCast->name), thisCast->name); Serialization_serializeInt(ctx, thisCast->size). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.h

Purpose: Declares the BeeGFS kernel-client message type `GetXAttrMsg` and its in-memory fields for entry info, xattr name, and requested value buffer size.

Important APIs/types/functions: Key declarations are GetXAttrMsg_init, GetXAttrMsg_initFromEntryInfoNameAndSize, GetXAttrMsg_serializePayload. Structs in scope are GetXAttrMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `GetXAttrRespMsg.c`, carrying xattr value buffer, returned size, and return code.

Important APIs/types/functions: Key declarations are GetXAttrRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if (!Serialization_deserializeCharArray(ctx, &thisCast->valueBufLen,; if (!Serialization_deserializeInt(ctx, &thisCast->size) ); if (!Serialization_deserializeInt(ctx, &thisCast->returnCode) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `GetXAttrRespMsg` and its in-memory fields for xattr value buffer, returned size, and return code.

Important APIs/types/functions: Key declarations are GetXAttrRespMsg_init, GetXAttrRespMsg_deserializePayload, GetXAttrRespMsg_getValueBuf, GetXAttrRespMsg_getReturnCode, GetXAttrRespMsg_getSize. Structs in scope are GetXAttrRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/GetXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ListXAttrMsg.c`, carrying entry info and requested list buffer size.

Important APIs/types/functions: Key declarations are ListXAttrMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeInt(ctx, thisCast->size). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.h

Purpose: Declares the BeeGFS kernel-client message type `ListXAttrMsg` and its in-memory fields for entry info and requested list buffer size.

Important APIs/types/functions: Key declarations are ListXAttrMsg_init, ListXAttrMsg_initFromEntryInfoAndSize, ListXAttrMsg_serializePayload. Structs in scope are ListXAttrMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ListXAttrRespMsg.c`, carrying packed xattr-name list buffer, returned size, and return code.

Important APIs/types/functions: Key declarations are ListXAttrRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeStrCpyVecPreprocess(ctx, &valueField) ); if (!Serialization_deserializeInt(ctx, &thisCast->size) ); if (!Serialization_deserializeInt(ctx, &thisCast->returnCode) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `ListXAttrRespMsg` and its in-memory fields for packed xattr-name list buffer, returned size, and return code.

Important APIs/types/functions: Key declarations are ListXAttrRespMsg_init, ListXAttrRespMsg_deserializePayload, ListXAttrRespMsg_getValueBuf, ListXAttrRespMsg_getReturnCode, ListXAttrRespMsg_getSize. Structs in scope are ListXAttrRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/ListXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `RefreshEntryInfoMsg.c`, carrying entry info that asks metadata/storage to refresh entry placement metadata.

Important APIs/types/functions: Key declarations are RefreshEntryInfoMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h

Purpose: Declares the BeeGFS kernel-client message type `RefreshEntryInfoMsg` and its in-memory fields for entry info that asks metadata/storage to refresh entry placement metadata.

Important APIs/types/functions: Key declarations are RefreshEntryInfoMsg_init, RefreshEntryInfoMsg_initFromEntryInfo, RefreshEntryInfoMsg_serializePayload. Structs in scope are RefreshEntryInfoMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `RefreshEntryInfoRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are RefreshEntryInfoRespMsg_init, RefreshEntryInfoRespMsg_getResult. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `RemoveXAttrMsg.c`, carrying entry info and xattr name.

Important APIs/types/functions: Key declarations are RemoveXAttrMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeStr(ctx, strlen(thisCast->name), thisCast->name). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.h

Purpose: Declares the BeeGFS kernel-client message type `RemoveXAttrMsg` and its in-memory fields for entry info and xattr name.

Important APIs/types/functions: Key declarations are RemoveXAttrMsg_init, RemoveXAttrMsg_initFromEntryInfoAndName, RemoveXAttrMsg_serializePayload. Structs in scope are RemoveXAttrMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `RemoveXAttrRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are RemoveXAttrRespMsg_init, RemoveXAttrRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/RemoveXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `SetAttrMsg.c`, carrying valid attribute bitmask, mode, modification/access times, user/group IDs, entry info, quota flag, buddy mirror flag, and optional file event.

Important APIs/types/functions: Key declarations are SetAttrMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt(ctx, thisCast->validAttribs); Serialization_serializeInt(ctx, thisCast->attribs.mode); Serialization_serializeInt64(ctx, thisCast->attribs.modificationTimeSecs); Serialization_serializeInt64(ctx, thisCast->attribs.lastAccessTimeSecs); Serialization_serializeUInt(ctx, thisCast->attribs.userID); Serialization_serializeUInt(ctx, thisCast->attribs.groupID); EntryInfo_serialize(ctx, thisCast->entryInfoPtr); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.h

Purpose: Declares the BeeGFS kernel-client message type `SetAttrMsg` and its in-memory fields for valid attribute bitmask, mode, modification/access times, user/group IDs, entry info, quota flag, buddy mirror flag, and optional file event.

Important APIs/types/functions: Key declarations are SetAttrMsg_init, SetAttrMsg_initFromEntryInfo, SetAttrMsg_serializePayload. Structs in scope are SetAttrMsg. Feature/compat flags: SETATTRMSG_FLAG_USE_QUOTA=1; SETATTRMSG_FLAG_BUDDYMIRROR_SECOND=2; SETATTRMSG_FLAG_HAS_EVENT=4.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `SetAttrRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are SetAttrRespMsg_init, SetAttrRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `SetFileStateMsg.c`, carrying entry info and one-byte file-state value.

Important APIs/types/functions: Key declarations are SetFileStateMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeUInt8(ctx, thisCast->state). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.h

Purpose: Declares the BeeGFS kernel-client message type `SetFileStateMsg` and its in-memory fields for entry info and one-byte file-state value.

Important APIs/types/functions: Key declarations are SetFileStateMsg_init, SetFileStateMsg_initFromEntryInfoAndState, SetFileStateMsg_serializePayload. Structs in scope are SetFileStateMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `SetFileStateRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are SetFileStateRespMsg_init, SetFileStateRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetFileStateRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `SetXAttrMsg.c`, carrying entry info, xattr name, value byte array, value size, and setxattr flags.

Important APIs/types/functions: Key declarations are SetXAttrMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeStr(ctx, strlen(thisCast->name), thisCast->name); Serialization_serializeCharArray(ctx, thisCast->size, thisCast->value); Serialization_serializeInt(ctx, thisCast->flags). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.h

Purpose: Declares the BeeGFS kernel-client message type `SetXAttrMsg` and its in-memory fields for entry info, xattr name, value byte array, value size, and setxattr flags.

Important APIs/types/functions: Key declarations are SetXAttrMsg_init, SetXAttrMsg_initFromEntryInfoNameValueAndSize, SetXAttrMsg_serializePayload. Structs in scope are SetXAttrMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `SetXAttrRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are SetXAttrRespMsg_init, SetXAttrRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/SetXAttrRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `StatMsg.c`, carrying entry info with an optional parent-info request feature flag.

Important APIs/types/functions: Key declarations are StatMsg_serializePayload, StatMsg_getSupportedHeaderFeatureFlagsMask. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->entryInfoPtr). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.h

Purpose: Declares the BeeGFS kernel-client message type `StatMsg` and its in-memory fields for entry info with an optional parent-info request feature flag.

Important APIs/types/functions: Key declarations are StatMsg_init, StatMsg_initFromEntryInfo, StatMsg_addParentInfoRequest, StatMsg_serializePayload, StatMsg_getSupportedHeaderFeatureFlagsMask. Structs in scope are StatMsg. Feature/compat flags: STATMSG_FLAG_GET_PARENTINFO=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `StatRespMsg.c`, carrying stat result, `StatData`, and optional parent node/entry information.

Important APIs/types/functions: Key declarations are StatRespMsg_deserializePayload, StatRespMsg_getSupportedHeaderFeatureFlagsMask. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeInt(ctx, &thisCast->result) ); if(!StatData_deserialize(ctx, &thisCast->statData) ); if (!Serialization_deserializeStrAlign4(ctx, &strLen, &thisCast->parentEntryID) ); if(!NumNodeID_deserialize(ctx, &thisCast->parentNodeID) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `StatRespMsg` and its in-memory fields for stat result, `StatData`, and optional parent node/entry information.

Important APIs/types/functions: Key declarations are StatRespMsg_init, StatRespMsg_getParentInfo, StatRespMsg_deserializePayload, StatRespMsg_getSupportedHeaderFeatureFlagsMask, StatRespMsg_getResult, StatRespMsg_getStatData. Structs in scope are StatRespMsg. Feature/compat flags: STATRESPMSG_FLAG_HAS_PARENTINFO=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/attribs/StatRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `HardlinkMsg.c`, carrying source entry, destination directory, destination name, source directory/name compatibility fields, and optional file event.

Important APIs/types/functions: Key declarations are HardlinkMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->fromInfo); EntryInfo_serialize(ctx, thisCast->toDirInfo); Serialization_serializeStrAlign4(ctx, thisCast->toNameLen, thisCast->toName); EntryInfo_serialize(ctx, thisCast->fromDirInfo); Serialization_serializeStrAlign4(ctx, thisCast->fromNameLen, thisCast->fromName); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.h

Purpose: Declares the BeeGFS kernel-client message type `HardlinkMsg` and its in-memory fields for source entry, destination directory, destination name, source directory/name compatibility fields, and optional file event.

Important APIs/types/functions: Key declarations are HardlinkMsg_init, HardlinkMsg_initFromEntryInfo, HardlinkMsg_serializePayload. Structs in scope are HardlinkMsg. Feature/compat flags: HARDLINKMSG_FLAG_HAS_EVENT=2.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `HardlinkRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are HardlinkRespMsg_init, HardlinkRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/HardlinkRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `MkDirMsg.c`, carrying user/group/mode/umask, parent entry, directory name, preferred nodes, mirror flags, and optional file event.

Important APIs/types/functions: Key declarations are MkDirMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeUInt(ctx, thisCast->userID); Serialization_serializeUInt(ctx, thisCast->groupID); Serialization_serializeInt(ctx, thisCast->mode); Serialization_serializeInt(ctx, thisCast->umask); EntryInfo_serialize(ctx, thisCast->parentInfo); Serialization_serializeStrAlign4(ctx, thisCast->newDirNameLen, thisCast->newDirName); Serialization_serializeUInt16List(ctx, thisCast->preferredNodes); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.h

Purpose: Declares the BeeGFS kernel-client message type `MkDirMsg` and its in-memory fields for user/group/mode/umask, parent entry, directory name, preferred nodes, mirror flags, and optional file event.

Important APIs/types/functions: Key declarations are MkDirMsg_init, MkDirMsg_initFromEntryInfo, MkDirMsg_serializePayload. Structs in scope are MkDirMsg. Feature/compat flags: MKDIRMSG_FLAG_NOMIRROR=1; MKDIRMSG_FLAG_BUDDYMIRROR_SECOND=2; MKDIRMSG_FLAG_HAS_EVENT=4.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `MkDirRespMsg.c`, carrying mkdir result plus created directory `EntryInfo` on success.

Important APIs/types/functions: Key declarations are MkDirRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeUInt(ctx, &thisCast->result) ); if (!EntryInfo_deserialize(ctx, &thisCast->entryInfo) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `MkDirRespMsg` and its in-memory fields for mkdir result plus created directory `EntryInfo` on success.

Important APIs/types/functions: Key declarations are MkDirRespMsg_init, MkDirRespMsg_deserializePayload, MkDirRespMsg_getResult. Structs in scope are MkDirRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `MkFileMsg.c`, carrying create credentials, mode/umask, optional stripe hints, optional storage pool override, parent entry, new name, preferred targets, and optional file event.

Important APIs/types/functions: Key declarations are MkFileMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeUInt(ctx, thisCast->userID); Serialization_serializeUInt(ctx, thisCast->groupID); Serialization_serializeInt(ctx, thisCast->mode); Serialization_serializeInt(ctx, thisCast->umask); Serialization_serializeUInt(ctx, thisCast->numtargets); Serialization_serializeUInt(ctx, thisCast->chunksize); StoragePoolId_serialize(ctx, &thisCast->storagePoolId); EntryInfo_serialize(ctx, thisCast->parentInfoPtr). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.h

Purpose: Declares the BeeGFS kernel-client message type `MkFileMsg` and its in-memory fields for create credentials, mode/umask, optional stripe hints, optional storage pool override, parent entry, new name, preferred targets, and optional file event.

Important APIs/types/functions: Key declarations are MkFileMsg_init, MkFileMsg_initFromEntryInfo, MkFileMsg_serializePayload, MkFileMsg_setStripeHints, MkFileMsg_setStoragePoolId. Structs in scope are MkFileMsg. Feature/compat flags: MKFILEMSG_FLAG_STRIPEHINTS=1; MKFILEMSG_FLAG_STORAGEPOOLID=2; MKFILEMSG_FLAG_HAS_EVENT=4.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `MkFileRespMsg.c`, carrying mkfile result plus created file `EntryInfo` on success.

Important APIs/types/functions: Key declarations are MkFileRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeUInt(ctx, &thisCast->result) ); if (!EntryInfo_deserialize(ctx, &thisCast->entryInfo) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `MkFileRespMsg` and its in-memory fields for mkfile result plus created file `EntryInfo` on success.

Important APIs/types/functions: Key declarations are MkFileRespMsg_init, MkFileRespMsg_deserializePayload, MkFileRespMsg_getResult. Structs in scope are MkFileRespMsg. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/MkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `RmDirMsg.c`, carrying parent entry info, directory name to remove, and optional file event.

Important APIs/types/functions: Key declarations are RmDirMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->parentInfo); Serialization_serializeStrAlign4(ctx, thisCast->delDirNameLen, thisCast->delDirName); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.h

Purpose: Declares the BeeGFS kernel-client message type `RmDirMsg` and its in-memory fields for parent entry info, directory name to remove, and optional file event.

Important APIs/types/functions: Key declarations are RmDirMsg_init, RmDirMsg_initFromEntryInfo, RmDirMsg_serializePayload. Structs in scope are RmDirMsg. Feature/compat flags: RMDIRMSG_FLAG_HAS_EVENT=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `RmDirRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are RmDirRespMsg_init, RmDirRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/RmDirRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `UnlinkFileMsg.c`, carrying parent entry info, file name to unlink, and optional file event.

Important APIs/types/functions: Key declarations are UnlinkFileMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: EntryInfo_serialize(ctx, thisCast->parentInfoPtr); Serialization_serializeStrAlign4(ctx, thisCast->delFileNameLen, thisCast->delFileName); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.h

Purpose: Declares the BeeGFS kernel-client message type `UnlinkFileMsg` and its in-memory fields for parent entry info, file name to unlink, and optional file event.

Important APIs/types/functions: Key declarations are UnlinkFileMsg_init, UnlinkFileMsg_initFromEntryInfo, UnlinkFileMsg_serializePayload. Structs in scope are UnlinkFileMsg. Feature/compat flags: UNLINKFILEMSG_FLAG_HAS_EVENT=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `UnlinkFileRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are UnlinkFileRespMsg_init, UnlinkFileRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/creating/UnlinkFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ListDirFromOffsetMsg.c`, carrying server offset, list limit, directory entry info, dot-entry filter, and a compatibility flag for buffer-size support.

Important APIs/types/functions: Key declarations are ListDirFromOffsetMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt64(ctx, thisCast->serverOffset); Serialization_serializeUInt(ctx, thisCast->dirListLimit); EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeBool(ctx, thisCast->filterDots). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h

Purpose: Declares the BeeGFS kernel-client message type `ListDirFromOffsetMsg` and its in-memory fields for server offset, list limit, directory entry info, dot-entry filter, and a compatibility flag for buffer-size support.

Important APIs/types/functions: Key declarations are ListDirFromOffsetMsg_init, ListDirFromOffsetMsg_initFromEntryInfo, ListDirFromOffsetMsg_serializePayload. Structs in scope are ListDirFromOffsetMsg. Feature/compat flags: LISTDIROFFSETMSG_COMPATFLAG_CLIENT_SUPPORTS_BUFSIZE=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `ListDirFromOffsetRespMsg.c`, carrying new server offset, per-entry offsets, result code, entry types, entry IDs, and entry names.

Important APIs/types/functions: Key declarations are ListDirFromOffsetRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeInt64(ctx, &thisCast->newServerOffset) ); if(!Serialization_deserializeInt64CpyVecPreprocess(ctx, &thisCast->serverOffsetsList) ); if(!Serialization_deserializeInt(ctx, &thisCast->result) ); if(!Serialization_deserializeUInt8VecPreprocess(ctx, &thisCast->entryTypesList) ); if (!Serialization_deserializeStrCpyVecPreprocess(ctx, &thisCast->entryIDsList) ); if(!Serialization_deserializeStrCpyVecPreprocess(ctx, &thisCast->namesList) ). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `ListDirFromOffsetRespMsg` and its in-memory fields for new server offset, per-entry offsets, result code, entry types, entry IDs, and entry names.

Important APIs/types/functions: Key declarations are ListDirFromOffsetRespMsg_init, ListDirFromOffsetRespMsg_deserializePayload, ListDirFromOffsetRespMsg_parseNames, ListDirFromOffsetRespMsg_parseEntryIDs, ListDirFromOffsetRespMsg_parseEntryTypes, ListDirFromOffsetRespMsg_parseServerOffsets, ListDirFromOffsetRespMsg_getResult. Structs in scope are ListDirFromOffsetRespMsg. Feature/compat flags: LISTDIROFFSETRESPMSG_COMPATFLAG_SERVER_SUPPORTS_BUFSIZE=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_deserializeStrCpyVec(&this->entryIDsList, outEntryIDs); Serialization_deserializeStrCpyVec(&this->namesList, outNames); Serialization_deserializeUInt8Vec(&this->entryTypesList, outEntryTypes); Serialization_deserializeInt64CpyVec(&this->serverOffsetsList, outServerOffsets). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `LookupIntentMsg.c`, carrying lookup/revalidate/create/open/stat intent flags, parent entry, name, optional meta version and entry info, open access flags, quota/create fields, preferred targets, and optional file event.

Important APIs/types/functions: Key declarations are LookupIntentMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeInt(ctx, thisCast->intentFlags); EntryInfo_serialize(ctx, thisCast->parentInfoPtr); Serialization_serializeStrAlign4(ctx, thisCast->entryNameLen, thisCast->entryName); Serialization_serializeUInt(ctx, thisCast->metaVersion); EntryInfo_serialize(ctx, thisCast->entryInfoPtr); Serialization_serializeUInt(ctx, thisCast->accessFlags); NumNodeID_serialize(ctx, &thisCast->clientNumID); Serialization_serializeUInt(ctx, thisCast->userID). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.h

Purpose: Declares the BeeGFS kernel-client message type `LookupIntentMsg` and its in-memory fields for lookup/revalidate/create/open/stat intent flags, parent entry, name, optional meta version and entry info, open access flags, quota/create fields, preferred targets, and optional file event.

Important APIs/types/functions: Key declarations are LookupIntentMsg_init, LookupIntentMsg_initFromName, LookupIntentMsg_initFromEntryInfo, LookupIntentMsg_serializePayload, LookupIntentMsg_addIntentCreate, LookupIntentMsg_addIntentCreateExclusive, LookupIntentMsg_addIntentOpen, LookupIntentMsg_addIntentStat. Structs in scope are LookupIntentMsg. Feature/compat flags: LOOKUPINTENTMSG_FLAG_REVALIDATE=1; LOOKUPINTENTMSG_FLAG_CREATE=2; LOOKUPINTENTMSG_FLAG_CREATEEXCLUSIVE=4; LOOKUPINTENTMSG_FLAG_OPEN=8; LOOKUPINTENTMSG_FLAG_STAT=16; LOOKUPINTENTMSG_FLAG_USE_QUOTA=1; LOOKUPINTENTMSG_FLAG_BUDDYMIRROR=2; LOOKUPINTENTMSG_FLAG_BUDDYMIRROR_SECOND=4.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `LookupIntentRespMsg.c`, carrying lookup/create/open/stat/revalidate response flags, result codes, stat data, file handle, stripe pattern, path info, and conditional entry info.

Important APIs/types/functions: Key declarations are LookupIntentRespMsg_deserializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: if(!Serialization_deserializeInt(ctx, &thisCast->responseFlags) ); if(!Serialization_deserializeUInt(ctx, &thisCast->lookupResult) ); if(!Serialization_deserializeInt(ctx, &thisCast->statResult) ); if(!StatData_deserialize(ctx, &thisCast->statData) ); if(!Serialization_deserializeInt(ctx, &thisCast->revalidateResult) ); if(!Serialization_deserializeInt(ctx, &thisCast->createResult) ); if(!Serialization_deserializeInt(ctx, &thisCast->openResult) ); if(!Serialization_deserializeStrAlign4(ctx,. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.h

Purpose: Declares the BeeGFS kernel-client message type `LookupIntentRespMsg` and its in-memory fields for lookup/create/open/stat/revalidate response flags, result codes, stat data, file handle, stripe pattern, path info, and conditional entry info.

Important APIs/types/functions: Key declarations are LookupIntentRespMsg_init, LookupIntentRespMsg_deserializePayload. Structs in scope are LookupIntentRespMsg. Feature/compat flags: LOOKUPINTENTRESPMSG_FLAG_REVALIDATE=1; LOOKUPINTENTRESPMSG_FLAG_CREATE=2; LOOKUPINTENTRESPMSG_FLAG_OPEN=4; LOOKUPINTENTRESPMSG_FLAG_STAT=8.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/lookup/LookupIntentRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.c

Purpose: Implements the kernel-client BeeGFS wire-message contract for `RenameMsg.c`, carrying entry type, source and destination directory entries, old/new names, and optional file event.

Important APIs/types/functions: Key declarations are RenameMsg_serializePayload. Structs in scope are the single message struct. Feature/compat flags: no local feature flags beyond the bound message type.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: Serialization_serializeUInt(ctx, thisCast->entryType); EntryInfo_serialize(ctx, thisCast->fromDirInfo); EntryInfo_serialize(ctx, thisCast->toDirInfo); Serialization_serializeStrAlign4(ctx, thisCast->oldNameLen, thisCast->oldName); Serialization_serializeStrAlign4(ctx, thisCast->newNameLen, thisCast->newName); FileEvent_serialize(ctx, thisCast->fileEvent). Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.h

Purpose: Declares the BeeGFS kernel-client message type `RenameMsg` and its in-memory fields for entry type, source and destination directory entries, old/new names, and optional file event.

Important APIs/types/functions: Key declarations are RenameMsg_init, RenameMsg_initFromEntryInfo, RenameMsg_serializePayload. Structs in scope are RenameMsg. Feature/compat flags: RENAMEMSG_FLAG_HAS_EVENT=1.

Control flow: The message is initialized with `NetMessage_init`, caller-owned pointers such as `EntryInfo`, `PathInfo`, names, file events, lists, or RDMA descriptors are attached by the inline constructor, and payload code walks the fields in a fixed server-compatible order. Payload operations observed here: inline wrappers only; payload work is inherited or implemented in the matching C file. Conditional fields are governed by intent/header/compat flags, so sender and receiver must make the same flag decision before parsing optional data.

State and persistence behavior: These message objects are transient stack/heap carriers for one RPC. They do not own most string/list/storage-info inputs unless a deserializer explicitly borrows pointers into the receive buffer, and they persist nothing outside the message header and payload bytes.

Dependencies and integration points: Integrated with `NetMessage`, BeeGFS serialization helpers, storage metadata types such as `EntryInfo`, `PathInfo`, `StatData`, `StripePattern`, quota/user fields, file-event logging, buddy-mirror feature flags, and session/storage remoting code that must match the userspace/server protocol definitions.

Risks: Wire-order or flag drift can corrupt all following fields. Borrowed deserialized buffers must not outlive the receive buffer, success-only deserialization paths must leave failure cases untouched, and optional event/quota/RDMA fields require exact feature-flag synchronization with servers.

Test signals: High-value tests are kernel/userspace protocol round trips, malformed or truncated payload deserialization, feature-flag compatibility tests, and client remoting tests for success and error replies. Compile coverage also matters because most constructors are inline in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameRespMsg.h

Purpose: Defines a thin BeeGFS kernel-client response/request wrapper over `SimpleIntMsg` for `RenameRespMsg`. It provides type-specific initialization and value access while reusing the common simple-message payload layout.

Important APIs/types/functions: The exported inline entry points are RenameRespMsg_init, RenameRespMsg_getValue. The file intentionally keeps the wire contract in the shared simple message base and only binds the concrete `NETMSGTYPE_*` value.

Control flow: Callers initialize the wrapper, then either read the embedded integer result/value or send the inherited one-field message. There is no independent parser or state machine in this header.

State and persistence behavior: State is the embedded integer field owned by the `Simple*Msg` base. Nothing is persisted locally; the value reflects one server reply or target selector.

Dependencies and integration points: Integrates with BeeGFS `NetMessage` dispatch and the storage/session remoting code that expects typed names for protocol messages.

Risks: The main risk is semantic drift between the wrapper name and the simple base message type; wire compatibility depends on the chosen `NETMSGTYPE_*` and integer width staying synchronized with server code.

Test signals: Useful tests are protocol round-trip and negative-result checks in client remoting paths, plus compile coverage that all typed wrappers map to the expected simple base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/storage/moving/RenameRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/msghelpers/MsgHelperAck.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/msghelpers/MsgHelperAck.h

Purpose: Provides the inline helper that sends an `AckMsgEx` reply when an incoming request included an ack ID.

Important APIs/types/functions: `MsgHelperAck_respondToAckRequest` builds the ack message, computes its serialized length, serializes into a caller buffer, and sends either through `DatagramListener_sendto_kernel` for datagrams or `Socket_sendto_kernel` for stream sockets.

Control flow: Empty ack IDs return false without I/O. Non-empty IDs always return true after attempting serialization/send, logging serialization or send failures but not propagating them as a false ack-request result.

State and persistence behavior: The helper persists no state; it uses caller-provided buffers and the current socket/datagram listener.

Dependencies and integration points: Depends on `AckMsgEx`, `App`, `Logger`, `DatagramListener`, `Socket`, and `StringTk_hasLength`.

Risks: Send errors are logged but not reported through the boolean return, so callers must interpret true as ack-request-present rather than ack-delivered. Buffer sizing must match `NetMessage_getMsgLength`.

Test signals: Exercise empty ack IDs, serialization buffer too small, datagram versus stream send paths, and logged send failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/msghelpers/MsgHelperAck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/IpAddress.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/IpAddress.h

Purpose: Centralizes BeeGFS kernel helpers for IPv4-mapped IPv6 addresses and typed socket-address construction.

Important APIs/types/functions: `beegfs_mapped_ipv4`, `beegfs_make_sockaddr_in`, `beegfs_make_sockaddr_in6`, `beegfs_get_sockaddr`, `beegfs_get_port`, `Beegfs_Sockaddr`, `bsa_ptr`, `bsa_size`, `bsa_make`, and `bsa_make_for_recv` handle AF_INET/AF_INET6 conversion without unsafe casts at call sites.

Control flow: `bsa_make` emits IPv4 sockaddr data only for v4-mapped, any, or loopback IPv6 values when the requested domain is AF_INET; otherwise it returns false so callers can skip impossible IPv6-on-IPv4 connections.

State and persistence behavior: Pure value helpers; no persistent state.

Dependencies and integration points: Used by standard and RDMA sockets, NIC discovery, and `SocketTk` address formatting across IPv4/IPv6 compatibility paths.

Risks: The AF_INET fallback deliberately special-cases only common addresses; real IPv6 targets fail when IPv6 is disabled. `bsa_size` depends on a populated family and returns full union size for receive buffers.

Test signals: Cover v4-mapped, any, loopback, non-v4 IPv6 with AF_INET, normal AF_INET6, and receive-buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/IpAddress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.c

Purpose: Discovers usable TCP and RDMA NIC addresses for the BeeGFS client module.

Important APIs/types/functions: `NIC_findAll`, `__NIC_findAllTCP`, `__NIC_filterInterfacesForRDMA`, `NIC_nicTypeToString`, `NIC_nicAddrToString`, `NIC_supportsRDMA`, and `NIC_supportedCapabilities` populate `NicAddressList` entries after applying `NicAddressFilter`.

Control flow: The code walks kernel `net_device` entries, skips loopback devices, records IPv4 as mapped IPv6, records only acceptable global-ish IPv6 unicast addresses, then optionally probes RDMA capability by binding an `RDMASocket` to discovered TCP addresses. `onlyRDMA` removes non-RDMA entries afterward.

State and persistence behavior: Allocates `NicAddress` entries into caller-owned lists; no persistent global state. RDMA probe sockets are temporary.

Dependencies and integration points: Integrates Linux networking structures, BeeGFS address filters/lists, `RDMASocket`, and `SocketTk` formatting.

Risks: The device walk has a TODO about RTNL locking; interface churn can race discovery. RDMA probing depends on successful bind behavior and memory allocation. IPv6 filtering can exclude temporary/deprecated/link-local addresses intentionally.

Test signals: Validate filtering, IPv4 mapping, IPv6 exclusion rules, RDMA-only pruning, and no leaks on allocation/probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.h

Purpose: Declares BeeGFS NIC discovery and capability helpers used by connection-pool setup.

Important APIs/types/functions: `NIC_findAll`, `NIC_nicTypeToString`, `NIC_nicAddrToString`, `NIC_supportsRDMA`, and `NIC_supportedCapabilities` are the public surface around `NicAddressList` and `NicListCapabilities`.

Control flow: Consumers call `NIC_findAll` with filter/RDMA/domain parameters, then inspect the resulting list or derived capabilities. The header itself keeps implementation details in the `.c` file.

State and persistence behavior: No state is stored in the header; callers own discovered list contents.

Dependencies and integration points: Depends on `NicAddress`, `NicAddressList`, iterators, filters, and string/common helpers.

Risks: Callers must free allocated list elements with the matching BeeGFS list cleanup utilities and must understand that capability reporting reflects current discovery, not a persistent hardware registry.

Test signals: Compile/link coverage plus integration tests for standard-only, RDMA-capable, and RDMA-filtered discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddress.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddress.h

Purpose: Defines the BeeGFS network-address record and NIC capability enum.

Important APIs/types/functions: `NicAddrType_t` distinguishes standard TCP and RDMA addresses, `NicAddress` stores IPv6-form address, NIC type, interface name, and optional RDMA device pointer, `NicListCapabilities` reports RDMA support, and `NicAddress_equals` compares address/type/name.

Control flow: The equality helper is pure and is used by list comparison and discovery code. RDMA-specific `ibdev` data exists only under `BEEGFS_RDMA`.

State and persistence behavior: Values are copied into list nodes and stats records; no global persistence.

Dependencies and integration points: Used by NIC discovery, connection pools, RDMA sockets, address filters, and priority stats.

Risks: Equality ignores the RDMA `ibdev` pointer, so two otherwise identical RDMA entries compare equal even if device pointers differ. Interface names are fixed-size `IFNAMSIZ` arrays.

Test signals: Compare IPv4-mapped/IPv6 addresses, names, type mismatches, and RDMA builds with/without device pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.c

Purpose: Implements equality comparison for BeeGFS NIC address lists.

Important APIs/types/functions: `NicAddressList_equals` first compares list length, then walks both underlying `PointerList` instances in order and calls `NicAddress_equals` for each pair.

Control flow: The function returns false on different lengths, otherwise remains true only while every aligned element matches. Order is significant; it is not a set comparison.

State and persistence behavior: Read-only traversal of caller-owned lists; no allocations or persistence.

Dependencies and integration points: Depends on `PointerListIter`, `NicAddress_equals`, and the list wrapper declared in `NicAddressList.h`.

Risks: Because order matters, discovery-order changes can make equivalent address sets compare different. Null element handling is not defensive.

Test signals: Equal lists, length mismatch, same entries in different order, and entries differing by IP/type/name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.h

Purpose: Provides a typed BeeGFS wrapper around `PointerList` for NIC address/stat records.

Important APIs/types/functions: The inline surface is NicAddressList_init, NicAddressList_uninit, NicAddressList_append, NicAddressList_length, NicAddressList_equals. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressListIter.h

Purpose: Provides a typed BeeGFS wrapper around `PointerListIter` for NIC address/stat records.

Important APIs/types/functions: The inline surface is NicAddressListIter_init, NicAddressListIter_next, NicAddressListIter_value, NicAddressListIter_end. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStats.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStats.h

Purpose: Tracks per-NIC connection availability, recency, last error, validity, and RDMA NUMA priority for BeeGFS connection selection.

Important APIs/types/functions: `NicAddressStats_init`, `invalidate`, `setValid`, `comparePriority`, `updateUsed`, `updateLastError`, `lastErrorExpired`, and `usable` operate on `NicAddressStats` fields `established`, `available`, `used`, `lastError`, and `nicValid`.

Control flow: Priority comparison prefers RDMA devices on the requested NUMA node, then more available connections, fewer established connections, and least-recently used NICs. Usability rejects RDMA stats without an `ibdev` and otherwise allows available slots or room below `maxConns`.

State and persistence behavior: Process-local mutable counters/timestamps; invalidation clears RDMA device pointers and validity.

Dependencies and integration points: Used by node connection pools, RDMA socket stats, `Time`, and optional kernel RDMA NUMA helpers.

Risks: Comments require owner `NodeConnPool` mutex for most access; unsynchronized mutation can mis-rank or race connection accounting. Error expiry uses elapsed wall time.

Test signals: NUMA preference, availability/established ordering, LRU ordering, invalid/offline NIC behavior, and error-expiration windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsList.h

Purpose: Provides a typed BeeGFS wrapper around `PointerList` for NIC address/stat records.

Important APIs/types/functions: The inline surface is NicAddressStatsList_init, NicAddressStatsList_uninit, NicAddressStatsList_append, NicAddressStatsList_length. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsListIter.h

Purpose: Provides a typed BeeGFS wrapper around `PointerListIter` for NIC address/stat records.

Important APIs/types/functions: The inline surface is NicAddressStatsListIter_init, NicAddressStatsListIter_next, NicAddressStatsListIter_value, NicAddressStatsListIter_end. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/NicAddressStatsListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/PooledSocket.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/PooledSocket.h

Purpose: Extends the abstract `Socket` with pool membership, availability, activity, expiration timer, and NIC type metadata.

Important APIs/types/functions: `_PooledSocket_init`, `_PooledSocket_uninit`, `PooledSocket_getHasExpired`, availability/activity getters and setters, expiration timer helpers, `PooledSocket_getNicType`, `getPool`, `getPoolElem`, and `setPool` manage `PooledSocket` state.

Control flow: Socket implementations embed `PooledSocket`; connection pools toggle availability and activity, set expiration start times, and link sockets into `ConnectionList` nodes. Expiration is checked from `Time_elapsedSinceMS`.

State and persistence behavior: In-memory only. The socket records its containing pool and list element, so list operations and socket teardown must stay coordinated.

Dependencies and integration points: Used by `StandardSocket`, `RDMASocket`, connection lists, and node connection pools.

Risks: Incorrect pool/element bookkeeping can leave dangling list references. Expiration starts only when explicitly set, so callers must manage idle lifecycle consistently.

Test signals: Pool insert/remove, availability transitions, activity reset, expiration timer behavior, and virtual destruction through embedded `Socket`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/PooledSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.c

Purpose: Adapts the lower-level `IBVSocket` RDMA transport to the generic BeeGFS `Socket`/`PooledSocket` interface.

Important APIs/types/functions: `RDMASocket_init`, `_RDMASocket_uninit`, `RDMASocket_rdmaDevicesExist`, `_connectByIP`, `_bindToAddr`, `_listen`, `_shutdown`, `_shutdownAndRecvDisconnect`, `_recvT`, `_sendto`, and `RDMASocket_poll` delegate to `IBVSocket` while preserving socket peer/bound fields.

Control flow: Initialization sets RDMA defaults from client config and installs the RDMA `SocketOps`. Connect passes the configured buffer/key settings to `IBVSocket_connectByIP`; send ignores destination addresses because RDMA is connection-oriented.

State and persistence behavior: Owns an embedded `IBVSocket` and RDMA communication config for the socket lifetime. No durable persistence.

Dependencies and integration points: Bridges connection pools and message I/O to `IBVSocket`, `Config`, `SocketTk`, and `NicAddressStats`.

Risks: RDMA availability is compile/runtime dependent. The `RDMASocket_registerMr` inline in the header inverts the `IBVSocket_registerMr` return convention, so call sites must follow this wrapper’s semantics.

Test signals: RDMA-disabled builds, connection setup, send/receive delegation, config-derived buffers/timeouts, shutdown, and memory-registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.h

Purpose: Declares the RDMA socket wrapper that embeds `PooledSocket` plus `IBVSocket` and exposes it through the generic BeeGFS socket API.

Important APIs/types/functions: Construction/init/uninit, RDMA device discovery, virtual socket operations, polling, `RDMASocket_setBuffers`, timeout/TOS/failure-status setters, device/rkey getters, `RDMASocket_isRkeyGlobal`, key-type conversion, and memory-registration wrapper.

Control flow: Callers tune unconnected sockets with buffer count/size/fragment/key type, then connect through the socket vtable. Inline getters forward to `IBVSocket`.

State and persistence behavior: Stores `IBVCommConfig` and embedded IBV state for one RDMA connection/listener. No persistence beyond process memory.

Dependencies and integration points: Used by NIC RDMA probing, connection pools, and RDMA read/write messages. Depends on BeeGFS config and RDMA key-type policy.

Risks: Settings only affect unconnected sockets; late changes may be ignored. Global/unsafe DMA key modes carry security/isolation tradeoffs compared with registered memory keys.

Test signals: Key-type mapping, buffer config propagation, device/rkey getters, and both RDMA-enabled and disabled build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.c

Purpose: Implements the small base layer for the abstract BeeGFS kernel socket interface.

Important APIs/types/functions: `_Socket_init`, `_Socket_uninit`, `Socket_bind`, and `Socket_bindToAddr` initialize base fields and delegate binding to virtual operations.

Control flow: `Socket_bind` binds to `in6addr_any` on the requested port; `Socket_bindToAddr` dispatches through `this->ops->bindToAddr`. Concrete implementations provide connect/listen/shutdown/send/recv behavior.

State and persistence behavior: Base initialization resets peer/bound fields and poll/list bookkeeping; no persistence.

Dependencies and integration points: Used by `StandardSocket`, `RDMASocket`, pooled sockets, and client network code that consumes the `SocketOps` vtable.

Risks: The base type assumes `ops` is valid before virtual calls. Incorrect embedding or initialization order can dereference null operations.

Test signals: Construct concrete sockets, verify bind delegation and base field initialization through standard/RDMA wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.h

Purpose: Declares the abstract BeeGFS kernel socket API and common send/receive helpers.

Important APIs/types/functions: `SocketOps` defines virtual `connectByIP`, `bindToAddr`, `listen`, `shutdown`, `shutdownAndRecvDisconnect`, `sendto`, and `recvT`. Inline helpers include `Socket_virtualDestruct`, `Socket_recvT`, kernel-buffer wrappers, exact-receive loops, and send wrappers.

Control flow: Public helpers copy or construct `iov_iter` values, delegate to the concrete vtable, and advance iterators after successful reads. Exact receive loops continue until the requested byte count arrives or a timeout/error occurs.

State and persistence behavior: The base stores peer names/IP, bound port, and poll state. No durable persistence; activity is owned by concrete sockets.

Dependencies and integration points: Shared by standard TCP sockets, RDMA sockets, ack helper, message transport, and kernel `iov_iter` utilities.

Risks: The header notes iterator advancement issues, especially for `ITER_PIPE`; callers must avoid double-advancing or mutating external pipe state unexpectedly. Exact receive requires initialized `outNumReceivedBeforeError`.

Test signals: Partial reads, timeout/error handling, iterator advancement, kernel-buffer wrappers, and vtable dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.c

Purpose: Implements BeeGFS TCP/UDP kernel sockets on top of Linux `struct socket`, including callbacks, options, connect/bind/listen/shutdown, timed receive, and send/receive wrappers.

Important APIs/types/functions: `StandardSocket_init`, `_StandardSocket_initSock`, option setters for keepalive/broadcast/receive-buffer/TCP_NODELAY/TCP_CORK, `_StandardSocket_connectByIP`, `_bindToAddr`, `_listen`, `_shutdown`, `_shutdownAndRecvDisconnect`, `_recvT`, `_sendto`, `StandardSocket_recvfrom`, and `StandardSocket_recvfromT`.

Control flow: Initialization creates a kernel socket and installs callbacks that wake BeeGFS poll waiters. Connect and bind use `Beegfs_Sockaddr` helpers for IPv4/IPv6 compatibility. Timed receive uses socket wait state and returns timeout/error codes; send handles optional destination addresses.

State and persistence behavior: Owns a kernel socket pointer and restores/releases it on uninit. Poll wait queues and callback state live only while the socket exists.

Dependencies and integration points: Integrates Linux socket APIs, `IpAddress.h`, `SocketTk`, `Serialization`, `PooledSocket`, and BeeGFS transport code.

Risks: Kernel callback replacement/restoration, blocking waits, allocation mode, and IPv4/IPv6 fallback are sensitive to kernel-version behavior. Buffer-size tuning doubles requested values and may fail with kernel limits.

Test signals: Connect/bind/listen failure paths, callback wakeups, timeouts, UDP recvfrom, TCP options, IPv4-mapped and IPv6 addresses, and teardown under pending pollers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.h

Purpose: Declares the concrete standard TCP/UDP socket implementation for the BeeGFS `SocketOps` abstraction.

Important APIs/types/functions: Exports construction/init/uninit, socket option setters, virtual operations, `StandardSocket_recvfrom`, `StandardSocket_recvfromT`, low-level `setsockopt`, and the `StandardSocket` struct containing `PooledSocket`, `struct socket*`, and socket domain.

Control flow: Callers construct/init, optionally tune options, then use either typed methods or the embedded `Socket` vtable.

State and persistence behavior: Tracks the kernel socket and domain for one live connection/listener. State is released by `_StandardSocket_uninit`.

Dependencies and integration points: Used by connection pools, message transport, datagram handling, and NIC probing for standard interfaces.

Risks: Consumers must not bypass initialization before vtable use, and option setters require a live kernel socket.

Test signals: Compile coverage plus option-setting and transport integration tests through the abstract socket interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.c

Purpose: Manages DMA-mapped buffer fragments used by BeeGFS RDMA send/receive and RDMA READ/WRITE registration paths.

Important APIs/types/functions: `IBVBuffer_init`, `IBVBuffer_initRegistration`, `IBVBuffer_free`, and `IBVBuffer_fill` allocate fragment arrays, map them for DMA, optionally allocate/map an `ib_mr`, unmap/free resources, and copy data from `iov_iter` into fragments.

Control flow: Initialization computes fragment count, allocates buffer and SGE arrays, kmallocs each fragment, maps it with `ib_dma_map_single`, and unwinds through `IBVBuffer_free` on failure. Registration builds scatterlist entries and maps them into an MR.

State and persistence behavior: Owns kernel buffers, DMA addresses, optional MR, fragment counts, and DMA direction until freed.

Dependencies and integration points: Used by `IBVSocket` communication contexts and RDMA key registration. Depends on kernel RDMA verbs and `iov_iter`.

Risks: Any allocation/mapping failure must unwind fully. DMA direction/length mismatches can corrupt transfers; `IBVBuffer_fill` mutates SGE lengths and list length based on copied data.

Test signals: Fragmented allocation, map failure unwind, registration failure, fill across multiple fragments, and free idempotence under partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.h

Purpose: Declares the RDMA buffer object used by `IBVSocket` when `BEEGFS_RDMA` is enabled.

Important APIs/types/functions: Exposes `IBVBuffer_init`, `IBVBuffer_initRegistration`, `IBVBuffer_free`, `IBVBuffer_fill`, and struct fields for fragment pointers, `ib_sge` list, optional memory region, buffer size/count, active SGE length, and DMA direction.

Control flow: Consumers initialize buffers against an `IBVCommContext`, optionally prepare memory registration for RDMA READ/WRITE, fill send buffers from iterators, and free during context teardown.

State and persistence behavior: Header declares ownership of DMA-mapped memory for one communication context. No persistence.

Dependencies and integration points: Compiled only with RDMA support and used by `IBVSocket` queue-pair setup and data path.

Risks: The struct is unavailable without `BEEGFS_RDMA`; callers must compile-guard direct access. Buffer fields are low-level and require disciplined teardown.

Test signals: RDMA build compilation plus integration tests that allocate, register, send, receive, and free buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVBuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.c

Purpose: Implements BeeGFS RDMA transport over Linux RDMA CM and InfiniBand verbs, including connection management, queue pairs, completion queues, flow control, send/receive, memory registration, and event handling.

Important APIs/types/functions: Public entry points include `IBVSocket_init`, `uninit`, `rdmaDevicesExist`, `connectByIP`, `bindToAddr`, `listen`, `shutdown`, `recvT`, `send`, `checkConnection`, timeout/TOS/failure-status setters, `getDevice`, and `registerMr`. Internal helpers create CM IDs, communication contexts, destination private data, CQs/QPs, post send/recv work requests, wait for completion events, enforce flow control, and handle RDMA CM/CQ/QP callbacks.

Control flow: Connect resolves address/route, creates context/QP/CQs/buffers, exchanges private data, transitions to established state, posts receives, then data path alternates posted receives/sends with completion handling and flow-control counters. Shutdown/disconnect tears down CM and verbs resources.

State and persistence behavior: Maintains CM ID, connection state, timeout config, completion counters, wait queues, QP/CQ/PD/MR objects, send/recv buffers, incomplete receive/send trackers, and NIC stats pointer. All state is kernel-memory lifetime only.

Dependencies and integration points: Integrates RDMA CM, ib verbs, BeeGFS `IBVBuffer`, `IpAddress`, `Time`, `NicAddressStats`, `RDMASocket`, and RDMA-capable connection pools.

Risks: This is concurrency- and hardware-sensitive code. Event ordering, timeout handling, stale connection rejection, flow-control counters, CQ notification arming, DMA key mode, and resource cleanup can cause hangs, leaks, or data corruption if changed casually.

Test signals: RDMA hardware/integration tests for connect/listen, disconnect races, timeout paths, flow-control exhaustion, partial receives, nonblocking send completion, MR registration, and RDMA-disabled fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.h

Purpose: Declares the BeeGFS RDMA socket API, connection states, timeout/config structures, communication context, destination metadata, and internal helpers used by `IBVSocket.c`.

Important APIs/types/functions: Public APIs cover init/uninit, device discovery, connect/bind/listen/shutdown, send/recv, connection checks, polling, timeouts/TOS/failure status, NIC stats, rkey/device getters, and MR registration. Under `BEEGFS_RDMA`, it declares `IBVCommConfig`, `IBVTimeoutConfig`, `IBVCommContext`, incomplete send/recv state, connection states, CM/CQ handlers, posting and wait helpers, and private-data constants.

Control flow: The header defines the state machine names from unconnected through address/route resolved, established, failed, and rejected-stale, which the C file drives through RDMA CM events and completion handling.

State and persistence behavior: Struct declarations show all per-connection kernel resources and counters; none are durable.

Dependencies and integration points: Shared by `RDMASocket`, `IBVBuffer`, NIC probing, and RDMA build guards.

Risks: Internal structs are tightly coupled to verbs lifetimes and callback synchronization. Build guards mean non-RDMA consumers must avoid depending on RDMA-only fields.

Test signals: Compile both RDMA and non-RDMA builds, validate state transitions, context teardown, and public wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/No_IBVSocket.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/No_IBVSocket.c

Purpose: Provides non-RDMA stub implementations of the `IBVSocket` API when `BEEGFS_RDMA` is not enabled.

Important APIs/types/functions: All public `IBVSocket_*` functions are present; most log `no_ibvsocket_err()` and return failure values, while setters are no-ops, `rdmaDevicesExist` returns false, and `getDevice`/`getNicStats` return NULL.

Control flow: Any accidental use of RDMA operations in a non-RDMA build fails fast by return code and informational logging rather than linking missing symbols.

State and persistence behavior: No RDMA state is allocated or persisted.

Dependencies and integration points: Lets `RDMASocket` and NIC discovery compile while reporting no RDMA devices.

Risks: Return conventions vary by method (`false`, `-1`, `~0`, NULL), so callers must use the appropriate failure check. Unexpected log messages indicate a caller reached a path that should have been gated by RDMA availability.

Test signals: Non-RDMA build tests should confirm discovery reports no RDMA, RDMA socket init/connect fail cleanly, and standard TCP paths continue to work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/No_IBVSocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionList.h

Purpose: Provides a typed BeeGFS wrapper around `PointerList` for connection pooled sockets.

Important APIs/types/functions: The inline surface is ConnectionList_init, ConnectionList_uninit, ConnectionList_append, ConnectionList_prepend, ConnectionList_moveToHead, ConnectionList_moveToTail, ConnectionList_remove, ConnectionList_length. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionListIter.h

Purpose: Provides a typed BeeGFS wrapper around `PointerListIter` for connection pooled sockets.

Important APIs/types/functions: The inline surface is ConnectionListIter_init, ConnectionListIter_next, ConnectionListIter_value, ConnectionListIter_end. It preserves type names for callers while delegating storage and iteration mechanics to the common pointer-list implementation.

Control flow: Initialization prepares the embedded list/iterator, append/prepend/remove/move operations forward to `PointerList`, and iterator helpers advance or expose typed values. For connection lists, moving/removing also maintains `PooledSocket` pool metadata where required.

State and persistence behavior: State is in-memory list membership only. Ownership depends on the caller-supplied `owner` flag or external cleanup conventions; there is no persistence beyond the client process.

Dependencies and integration points: Used by NIC discovery/stats, connection pools, pooled sockets, and node connection selection.

Risks: Typed wrappers do not add deep validation; stale iterators, double removal, or wrong ownership cleanup can corrupt list state or leak sockets/address objects.

Test signals: List length, append/remove, iterator removal, owner cleanup, and socket pool metadata updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/ConnectionListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/DevicePriorityContext.h -->
# sources/distributed-fs/beegfs/client_module/source/common/nodes/DevicePriorityContext.h

Purpose: Defines the small context object used when ranking devices/NICs for connection priority.

Important APIs/types/functions: `DevicePriorityContext` contains `maxConns` and, under `BEEGFS_NVFS`, a GPU index associated with the first page.

Control flow: The header has no functions; selection code elsewhere passes this context into priority comparisons.

State and persistence behavior: Plain transient value object, not persisted.

Dependencies and integration points: Integrates connection/device selection with optional NVFS GPU locality hints.

Risks: Callers must initialize all fields for the active build configuration; otherwise priority logic can use stale stack values.

Test signals: Compile with and without `BEEGFS_NVFS`, and test device ranking with max connection limits and GPU locality where enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/DevicePriorityContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/MirrorBuddyGroup.c -->
# sources/distributed-fs/beegfs/client_module/source/common/nodes/MirrorBuddyGroup.c

Purpose: Manages sequence numbers for BeeGFS buddy-mirrored target groups, including in-flight tracking, acknowledgement selection, completion buffering, and object lifetime.

Important APIs/types/functions: `MirrorBuddyGroup_constructFromTargetIDs`, `MirrorBuddyGroup_put`, `MirrorBuddyGroup_acquireSequenceNumber`, `MirrorBuddyGroup_releaseSequenceNumber`, and `MirrorBuddyGroup_setSeqNoBase` manage group IDs, primary/secondary target IDs, krefs, a slot semaphore, mutex, in-flight min-heap, and finished ring buffer.

Control flow: Acquire waits or trylocks a slot, refs the group, increments the sequence, appends to the heap, and returns either a selective acknowledgement from the finished ring or the lowest in-flight predecessor. Release records the finished sequence, removes its heap slot by bubbling to root and heapifying down, wakes one slot, and drops the ref.

State and persistence behavior: All state is in-memory per group. Sequence base can only advance. Buffers are kmalloc/vmalloc-backed and freed on final kref.

Dependencies and integration points: Used by buddy-mirror write/metadata paths that require ordered sequence acknowledgements across mirrored targets.

Risks: Heap pointer self-references must be updated after every swap; mistakes can corrupt release handles. Semaphore capacity bounds in-flight operations, and `sequence==0` disables acquisition with `ENOENT`.

Test signals: Concurrent acquire/release, nonblocking acquire `EAGAIN`, interrupted waits, selective acknowledgement ring wrap, heap removal from arbitrary slots, and seq-base advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/nodes/MirrorBuddyGroup.c -->
