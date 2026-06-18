<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java

Purpose: `BlockAliasMap<T extends BlockAlias>` defines the unstable public abstraction used by PROVIDED storage to map HDFS `Block` identifiers to external storage aliases such as `FileRegion`.

Important APIs and types: `Reader<U>` is an `Iterable` and `Closeable` with a `resolve(Block)` lookup method and marker `Options`. `Writer<U>` is a `Closeable` with `store(U)` and marker `Options`. `ImmutableIterator` supplies a base iterator that always rejects `remove`. The top-level API exposes `getReader(opts, blockPoolID)`, `getWriter(opts, blockPoolID)`, `refresh()`, and `close()`.

Control flow and state: this file has no concrete storage state. Implementations decide how to bind a reader or writer to a block pool and whether `refresh` has meaning. The abstract contract allows `getReader` to return null when no reader can be created, although concrete implementations often throw instead.

Persistence and dependencies: the contract depends on `Block`, `BlockAlias`, and Java `Optional`/`Iterator`/`Closeable`. Persistence semantics are left to implementations such as LevelDB, text files, or RPC-backed alias maps.

Integration points: DataNode PROVIDED storage, fsimage-generation utilities, and alias-map service clients use this contract to resolve block IDs to external file offsets.

Risks and test signals: because the API is marked unstable, callers should not assume a common option type or refresh behavior. Tests should verify implementation-specific close semantics, unsupported remove behavior, empty lookups, and block-pool scoping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java -->
