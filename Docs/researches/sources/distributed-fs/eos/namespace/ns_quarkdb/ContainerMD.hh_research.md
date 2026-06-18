# sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.hh

Purpose: declares `QuarkContainerMD`, the QuarkDB implementation of `IContainerMD`.

Important APIs/types/functions: exposes container/file child management, async and sync lookup, metadata getters/setters for ids, ownership, modes, flags, clone data, xattrs, tree counters, access checks, serialization/deserialization, initialization, environment formatting, iterators, and map-copy helpers. Private members include `ContainerMdProto`, service/flusher/qclient pointers, child-map keys, `mClock`, and lazy child maps.

Control flow: most inline getters/setters wrap protobuf access with `runReadOp` or `runWriteOp` inherited from `LockableNSObjMD`. Iterator begin/end methods intentionally skip locking because iterator wrappers lock around use. Generation methods derive values from dense hash map bucket state and end iterator address to detect invalidation.

State and persistence: declares all state for container protobuf metadata and child maps. Persistent representation is the protobuf plus QuarkDB hashes for child ids.

Dependencies and integration: implements `IContainerMD`, depends on `IFileMD`, `MetadataFlusher`, protobuf, qclient, and `FutureWrapper`. Services inject dependencies through constructor or `setServices`.

Risks: many inline methods return protobuf-derived values while hiding lock acquisition, but reference-returning APIs need careful caller lifetime handling. The default constructor leaves services null for tests/dumps, so methods that touch flusher/qclient are invalid in standalone mode. Iterator generation relies on implementation details of the underlying map.

Test signals: mock/test constructors are used in QuarkDB namespace tests; `FRIEND_TEST(VariousTests, EtagFormattingContainer)` targets formatting behavior.
