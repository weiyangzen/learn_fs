# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.c

## Research
`BumpFileVersion.c` implements outgoing serialization for file-version bump requests. The payload always serializes `EntryInfo`; if `BUMPFILEVERSIONMSG_FLAG_HASEVENT` is set, it also serializes a `FileEvent`. The ops mark the message as supporting sequence numbers and use dummy deserialization.

Control flow is feature-flag gated around the optional event payload. State is non-owned `EntryInfo` and optional `FileEvent` pointers from the header. Dependencies include `BumpFileVersion.h`, `EntryInfo`, `FileEvent`, and `NetMessage`. Integration points are metadata/session paths that update cache invalidation or persistent file version counters after file events. Risks include feature flag mismatch with payload presence, non-owned pointer lifetime, and sequence-number retry semantics causing duplicate persistent bumps if server handling is not idempotent. Test signals are serialized payload with/without event, response handling through `BumpFileVersionRespMsg`, and retry behavior.
