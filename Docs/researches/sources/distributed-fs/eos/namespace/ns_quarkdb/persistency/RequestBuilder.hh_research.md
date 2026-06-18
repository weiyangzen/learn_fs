# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.hh

Purpose: Declares `RequestBuilder`, the central stateless command-construction API for QuarkDB namespace metadata.
Important APIs/types/functions: `RedisRequest` is `std::vector<std::string>`; static methods cover container/file protobuf writes, reads, deletes, metadata counts, cache invalidation publish messages, and filesystem accounting set keys.
Control flow: callers assemble a request locally and pass it to qclient/backends; this header intentionally exposes no execution or retry behavior.
State/persistence: no mutable state; persistence is represented by the target QDB command/key layout.
Dependencies/integration: includes namespace interface types and identifier wrappers; source implementation binds it to constants such as `sContainerKey`, `sFileKey`, and cache invalidation channels.
Risks: because commands are plain string vectors, there is no type-level distinction between command name, key, field, hint, and blob; adding new command formats requires test coverage for exact argument ordering.
Test signals: direct coverage exists for filesystem key helpers; broader service tests and metadata flush paths depend on stable command construction.
