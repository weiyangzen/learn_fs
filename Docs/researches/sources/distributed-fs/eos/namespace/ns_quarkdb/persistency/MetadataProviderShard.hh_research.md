# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.hh

Purpose: Declares `MetadataProviderShard`, the asynchronous QDB metadata fetch/cache shard used by QuarkDB-backed file and container services.
Important APIs/types/functions: constructor wires non-owning `qclient::QClient`, `IContainerMDSvc`, `IFileMDSvc`, and `folly::Executor`; public fetch APIs are `retrieveContainerMD`, `retrieveFileMD`, and `hasFileMD`; cache controls include drop/insert/set-size/stats methods; private `processIncomingFileMdProto` and `processIncomingContainerMD` convert protobuf/backend tuples into service-owned metadata objects.
Control flow: callers request metadata by ID, in-flight maps deduplicate concurrent fetches through `folly::FutureSplitter`, and completion handlers materialize objects before caching.
State/persistence: persistent state lives in QDB and protobufs; this class owns only in-memory LRU caches and in-flight futures guarded by `mMutex`.
Dependencies/integration: depends on `LRU`, QuarkDB metadata classes, service interfaces, qclient, and Folly futures; it is a backend boundary for `FileMDSvc`/`ContainerMDSvc`.
Risks: stale cache entries require invalidation via explicit drop/insert paths; non-owning pointers require services/client/executor lifetime discipline; FutureSplitter maps must be erased reliably on failures.
Test signals: `FileMDSvcTest.LoadTest` checks repeated futures for the same fid coalesce to one in-memory object; locking tests assert metadata retrieval should not lock the returned object.
