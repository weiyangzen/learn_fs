## sources/distributed-fs/beegfs/client_module/source/net/message/NetMessageFactory.h

**Purpose:** Declares the kernel-client message factory interface for creating or deserializing `NetMessage` objects from receive buffers or message type IDs.

**Important APIs/types/functions:** Exposes `NetMessageFactory_createFromBuf`, `NetMessageFactory_deserializeFromBuf`, and `NetMessageFactory_createFromMsgType`.

**Control flow:** Callers provide an `App`, buffer pointer, buffer length, and optionally a preallocated output message plus expected type. Implementations in the `.c` file handle header decode, type dispatch, compatibility checks, and payload decode.

**State and persistence behavior:** The header owns no state. It defines allocation/ownership expectations: `createFromBuf` and `createFromMsgType` return heap-allocated messages owned by the caller; `deserializeFromBuf` fills a caller-owned object.

**Dependencies and integration points:** Depends on `common/Common.h` and the generic `NetMessage` declaration. It is included by networking receive code and RPC helpers that need protocol message construction.

**Risks:** The interface does not encode buffer mutability or ownership beyond raw `char*`, so callers must ensure the buffer remains valid during deserialization. Expected message type is an unsigned short protocol constant; mismatches fail without richer diagnostics.

**Test signals:** Compile users against the header, validate caller cleanup of allocated messages, and test that preallocated response deserialization fails cleanly for wrong message types.
