# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.cc

Purpose: Implements stateless factories for Redis/QuarkDB requests used by metadata services and filesystem accounting.
Important APIs/types/functions: `writeContainerProto` and `writeFileProto` serialize metadata objects into `eos::Buffer` and emit `LHSET`; low-level overloads accept ID, locality hint, and serialized blob; read/delete/count APIs emit `LHGET`, `LHDEL`, and `LHLEN`; invalidation APIs emit `PUBLISH`; filesystem-key helpers build `fsview:<location>:files` and `fsview:<location>:unlinked`.
Control flow: object overloads serialize through interface virtuals, convert identifiers with `stringify`/`SSTR`, and return vector<string> command payloads for qclient execution.
State/persistence: no state is stored here; commands target persistent keys from `namespace/ns_quarkdb/Constants.hh`.
Dependencies/integration: integrates `IFileMD`, `IContainerMD`, `Buffer`, EOS string conversion, and constants used by `FileSystemView`, services, and tests.
Risks: read APIs currently omit locality hints; command construction depends on exact key/channel constants; serialized blobs are opaque and must match `Serialization`/metadata object formats.
Test signals: `FileSystemView.FileSetKey` asserts filesystem key formats; service integration tests indirectly exercise read/write/delete/count command paths.
