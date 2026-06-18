# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.c

## Research
`OpenFileMsg.c` serializes outgoing metadata open-file requests. The payload contains client numeric ID, access flags, serialized entry info, and optional file-event information when `OPENFILEMSG_FLAG_HAS_EVENT` is set. The ops support sequence numbers and use dummy deserialization.

Control flow is fixed field order with feature-flag gated event serialization. State is non-owned `EntryInfo` and optional `FileEvent`, plus access flags and client ID. Dependencies are `OpenFileMsg.h`, `EntryInfo`, `FileEvent`, and serialization helpers. Integration points are VFS open paths, quota/access-check flags, event logging, and metadata session establishment. Risks include access flag mismatch with Linux open flags, optional event flag/payload mismatch, non-owned lifetime, and sequence-number idempotency under retries. Test signals are open responses with file handle/path/pattern, bypass-access-check flag behavior, and event logging.
