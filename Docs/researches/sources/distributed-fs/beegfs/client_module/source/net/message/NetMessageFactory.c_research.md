## sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.c

**Purpose:** Implements deserialization and factory construction for network messages received by the BeeGFS kernel client. It maps wire message type IDs to concrete client-side message structs and validates headers/payloads.

**Important APIs/types/functions:** `NetMessageFactory_createFromBuf` decodes a raw buffer into an allocated message. `NetMessageFactory_deserializeFromBuf` deserializes into a caller-provided expected message object. `NetMessageFactory_createFromMsgType` maps `NETMSGTYPE_*` IDs to `NETMESSAGE_CONSTRUCT(TYPE)` calls. Static `__NetMessageFactory_deserializeRaw` copies the header, checks feature-flag compatibility, and invokes the message-specific `deserializePayload`.

**Control flow:** A raw receive buffer is wrapped in `DeserializeCtx`, the generic header is decoded, a concrete message object is created by switch, and the payload is decoded only if the type is recognized and compatible. Incompatible feature flags or payload decode failures mark the message invalid. Preallocated deserialization first checks that the wire type equals the expected type.

**State and persistence behavior:** No durable state is stored here. The factory allocates message objects that callers must later destruct/free. Wire compatibility is enforced through message header feature flags and typed payload deserializers.

**Dependencies and integration points:** Includes all response/control/node/storage/session messages that the client can receive, plus optional NVFS RDMA response support. It is used by messaging/commkit receive paths and must stay synchronized with the protocol enum and message constructors.

**Risks:** Missing a new message type turns a valid server response into `NETMSGTYPE_Invalid`. Header deserialization appears unconditional; callers must ensure buffer length is large enough for the header. The default invalid path still allocates a `SimpleMsg`, so allocation failure behavior depends on `os_kmalloc`. Feature-flag compatibility is checked before payload decode, which is correct but requires each message class to declare supported flags accurately.

**Test signals:** Test creation for every mapped message type, invalid/unknown types, expected-type mismatch, incompatible feature flags, malformed payloads, optional `BEEGFS_NVFS` mappings, and memory ownership/destruction of both typed and invalid messages.
