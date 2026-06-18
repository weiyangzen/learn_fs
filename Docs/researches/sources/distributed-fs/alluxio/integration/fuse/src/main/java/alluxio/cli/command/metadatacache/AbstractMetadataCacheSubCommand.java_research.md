# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/AbstractMetadataCacheSubCommand.java

Purpose: shared implementation for metadata-cache FUSE subcommands, enforcing configuration and locating the correct metadata-caching filesystem wrapper.

Important APIs and helpers: overrides `run(AlluxioURI, String[])` to require `USER_METADATA_CACHE_ENABLED`, then calls abstract `runSubCommand(AlluxioURI, String[], MetadataCachingFileSystem)`. `findMetadataCachingFileSystem()` accepts either direct `MetadataCachingFileSystem` or a `LocalCacheFileSystem` whose underlying filesystem is metadata-caching.

Control flow and state: command execution first checks configuration, then unwraps filesystem layers, throwing runtime/illegal-state errors when metadata cache support is disabled or the filesystem type is unexpected.

Dependencies and integration: depends on `MetadataCachingFileSystem`, `LocalCacheFileSystem`, `PropertyKey.USER_METADATA_CACHE_ENABLED`, `AlluxioURI`, and command base context.

Risks and test signals: failures are runtime exceptions and not typed `URIStatus` responses. The error message for bad underlying local-cache filesystem reports the outer class name, which may reduce diagnostics. It centralizes important guard behavior for all subcommands.
