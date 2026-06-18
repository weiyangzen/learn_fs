# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/aliasmap/InMemoryAliasMap.java

## Purpose
`InMemoryAliasMap` implements `InMemoryAliasMapProtocol` using LevelDB to map HDFS `Block` records to `ProvidedStorageLocation` records. It supports provided storage alias lookup plus snapshot/archive transfer for standby NameNode bootstrap.

## Important APIs and types
Main protocol methods are `list(Optional<Block>)`, `read(Block)`, `write(Block, ProvidedStorageLocation)`, and `getBlockPoolId`. Static helpers initialize the LevelDB store, convert blocks and locations to/from protobuf bytes, transfer a bootstrap archive, create a snapshot copy, compress the snapshot as tar.gz, recursively archive files while skipping LevelDB `LOCK`, and complete bootstrap extraction.

## Control flow
`init` reads the configured LevelDB directory, appends the block pool ID when present, creates missing directories, opens LevelDB, and returns a configured alias map. `list` seeks to the marker or first key, reads up to the configured batch size, converts each LevelDB key/value pair into `FileRegion`, and returns an optional next marker when more entries remain. `read` gets one key and converts the value if present. `write` serializes both sides and stores them in LevelDB. Bootstrap transfer creates a consistent snapshot DB using a LevelDB snapshot iterator, archives the block-pool directory, sets HTTP verification/file-name headers, streams the tarball, and deletes temporary artifacts.

## State and persistence
Persistent state is LevelDB data under the configured alias map directory, optionally scoped by block pool ID. Runtime state is the opened DB handle, URI, config, and block pool ID. Snapshot transfer creates temporary `aliasmap_snapshot` and `aliasmap.tar.gz` files and cleans them in a finally block.

## Dependencies and integration points
It depends on LevelDB JNI, HDFS protocol protobuf conversion, provided-storage `FileRegion`, NameNode `ImageServlet`/`TransferFsImage` bootstrap transfer utilities, compression/archive libraries, `DataTransferThrottler`, and Hadoop configuration keys for alias map directory and batch size.

## Risks and edge cases
The class name says in-memory, but persistence is LevelDB; operational expectations must account for local disk state. `list` uses the marker as an inclusive seek and then selects a next marker by consuming one additional iterator entry, so callers must follow protocol semantics carefully to avoid duplicates or skips. Snapshot creation copies all K/V pairs and can be expensive for large maps. Cleanup errors after transfer are aggregated and thrown, which may surface after a successful stream copy.

## Test signals
Tests should cover missing directory creation, missing config error, read/write round trips, ordered paginated list behavior with markers and batch sizes, protobuf conversion failures, snapshot consistency while writes occur, archive contents excluding `LOCK`, bootstrap extraction, HTTP transfer headers, throttling, and cleanup failure paths.
