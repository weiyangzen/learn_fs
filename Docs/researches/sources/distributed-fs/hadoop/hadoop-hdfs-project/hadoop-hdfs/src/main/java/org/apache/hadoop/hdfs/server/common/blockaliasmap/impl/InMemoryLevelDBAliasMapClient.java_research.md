<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java

Purpose: this private client adapts the RPC protocol of `InMemoryAliasMapServer` to the `BlockAliasMap<FileRegion>` API. It is used by DataNodes and fs2img-like tools to read and write PROVIDED `FileRegion` records backed by the server-side in-memory/LevelDB alias map.

Important APIs and types: the outer class is `Configurable` and initializes protocol translators through `InMemoryAliasMapProtocolClientSideTranslatorPB.init(conf)`. `LevelDbReader.resolve` calls `aliasMap.read(block)` and maps a returned `ProvidedStorageLocation` into `FileRegion`. Its iterator pages through `aliasMap.list(marker)` using `InMemoryAliasMap.IterationResult`. `LevelDbWriter.store` writes block and provided location pairs through `aliasMap.write`.

Control flow and state: `setConf` replaces the local collection of alias-map proxies. `getAliasMap(blockPoolID)` requires a non-null block pool id, asks each proxy for `getBlockPoolId`, and returns the matching one or throws. Reader iteration is lazy and batch-oriented: first batch starts at an empty marker; when the current batch is exhausted and a next marker is present, it fetches the next batch and recurses to return the first item.

Persistence and dependencies: this class does not persist locally. It depends on RPC proxies and server-side alias map persistence. `close` stops every proxy with `RPC.stopProxy`; reader and writer close methods are no-ops because the proxy lifecycle belongs to the client.

Integration points: it bridges `BlockAliasMap` consumers with `InMemoryAliasMapProtocol`, `ProvidedStorageLocation`, and protobuf client translators.

Risks and test signals: `getAliasMap` logs and ignores IO failures while checking proxy block-pool ids, then throws if no match is found. Iterator IOExceptions are wrapped in `RuntimeException`, which can surprise callers expecting checked IO. Tests should cover multiple block pools, missing block-pool id, empty list batches, marker pagination, proxy shutdown, and failed protocol calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java -->
