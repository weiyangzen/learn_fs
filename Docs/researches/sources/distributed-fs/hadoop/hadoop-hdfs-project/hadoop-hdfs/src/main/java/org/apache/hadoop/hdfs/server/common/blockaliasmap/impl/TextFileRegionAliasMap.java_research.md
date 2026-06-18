<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java

Purpose: `TextFileRegionAliasMap` stores and reads `FileRegion` aliases as delimited UTF-8 text files, optionally compressed, with one block-pool-specific file per block pool.

Important APIs and types: `ReaderOptions` configures read file path and delimiter from `DFS_PROVIDED_ALIASMAP_TEXT_READ_FILE` and delimiter keys. `WriterOptions` configures output directory, delimiter, and optional codec from the write-dir and codec keys. `createReader` converts `LocalFileSystem` to raw local FS, discovers compression by file extension, derives `blocks_<blockPoolID>.csv[.codec]`, and returns `TextReader`. `createWriter` creates the output stream and wraps it with the codec if configured. `TextReader.resolve` linearly scans the iterator for a matching `Block`. `TextWriter.store` writes `blockId,path,offset,length,generationStamp[,base64Nonce]`.

Control flow and state: readers keep a synchronized `IdentityHashMap` from iterators to open `BufferedReader`s so `close` can close all active iterators. Each iterator prefetches one pending `FileRegion`; EOF removes the reader from the map. Writer state is a single `Writer` and delimiter. `refresh` throws unsupported.

Persistence and dependencies: persistence is text files in Hadoop `FileSystem`, raw local FS when applicable, and optional Hadoop compression codecs. Nonces are Base64 encoded only when non-empty. The parsed block pool id is inferred from the filename prefix `blocks_`.

Integration points: this implementation is useful for import/export tooling and PROVIDED storage bootstrap where human-readable alias maps are easier than LevelDB. It relies on HDFS config keys, `Path`, `CompressionCodecFactory`, `FileRegion`, and `ProvidedStorageLocation`.

Risks and test signals: delimiter parsing uses `String.split(delim)`, so regex metacharacters and delimiters in paths are risky. `blockPoolIDFromFileName` assumes a `blocks_` prefix. `resolve` is O(n). `getWriter` falls back to the outer `conf` in one branch, which must be set. Tests should cover compressed and uncompressed files, nonce round trip, invalid line field counts, special delimiters, multiple live iterators, close error aggregation, and filename/block-pool mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java -->
