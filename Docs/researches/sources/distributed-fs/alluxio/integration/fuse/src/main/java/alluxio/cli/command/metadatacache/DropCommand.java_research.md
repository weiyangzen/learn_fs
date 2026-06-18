# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropCommand.java

Purpose: FUSE metadata-cache subcommand that clears cached metadata for the target path and related entries.

Important APIs and helpers: `getCommandName()` returns `drop`; `getUsage()` includes a path placeholder before `.alluxiocli.metadatacache.drop`; `runSubCommand` calls `MetadataCachingFileSystem.dropMetadataCache(path)` and returns a completed `URIStatus`; `getDescription()` explains path/children invalidation.

Control flow and state: the path supplied by `FuseShell` is the parent path of the special command suffix. Cache mutation is delegated to the metadata-caching filesystem.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `AlluxioURI`, `URIStatus`, `FileInfo`, and `Constants`.

Risks and test signals: no extra args are validated, so all path targeting depends on `FuseShell` parent-path parsing. Description contains a grammatical typo but documents recursive directory behavior.
