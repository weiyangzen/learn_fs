# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFileSystem.java

Purpose: `HarFileSystem` implements the read-only Hadoop Archive (`har`) filesystem. It maps logical paths inside a `.har` archive to byte ranges inside underlying `part-*` files using `_masterindex` and `_index` metadata.

Important APIs: `initialize`, `getScheme`, `getHarVersion`, URI/path helpers, `makeQualified`, `getFileBlockLocations`, `getFileStatus`, `open`, `listStatus`, read-only mutator overrides, `hasPathCapability`, `HarFSDataInputStream`, `HarMetaData`, and metadata cache configuration constants.

Control flow and state: initialization decodes `har://underlying-scheme-host/path` into an underlying filesystem URI, finds the archive path ending in `.har`, validates `_masterindex` and `_index`, and loads or refreshes static LRU metadata keyed by archive URI based on index modification timestamps. Metadata parsing reads hash ranges from `_masterindex`, seeks ranges in `_index`, builds a map of internal paths to `HarStatus`, and caches part-file statuses. `getFileStatus` and `listStatus` synthesize statuses from index entries plus underlying part/index file metadata. `open` wraps the underlying part file stream in a bounded stream that fakes EOF at the archived file's byte range and adjusts positioned reads/seeks. Mutations throw `IOException`; path-handle opens are unsupported.

Dependencies and integration: depends on underlying `FileSystem`, `LineReader`, `Text`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FsPermission`, path capability validation, and `FileUtil.copy` for local extraction.

Risks: metadata cache is static and synchronized only around map creation; individual metadata objects can be shared. Index parsing assumes well-formed space-separated lines and uses decoded fields. Permissions/owner/group from HAR v3 metadata are parsed but not applied; synthesized statuses use underlying file metadata. `createFile` and `appendFile` delegate to underlying fs despite the connector being read-only, a surprising inherited-builder surface. `checkPath` delegates to the underlying filesystem and may not fully validate `har` URI semantics.

Test signals: valid/invalid HAR URI decoding, missing index files, metadata cache invalidation on index timestamp change, v1/v2/v3 filename decoding and modification times, file vs directory status/listing, bounded sequential and positioned reads including EOF, block location offset fixing, read-only mutator failures, and `FS_READ_ONLY_CONNECTOR` capability.
