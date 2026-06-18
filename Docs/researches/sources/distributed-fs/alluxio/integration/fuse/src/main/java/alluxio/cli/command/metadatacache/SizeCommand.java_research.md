# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/SizeCommand.java

Purpose: FUSE metadata-cache subcommand that exposes current metadata-cache size through returned file metadata.

Important APIs and helpers: `getCommandName()` returns `size`; `getUsage()` builds the synthetic `.alluxiocli.metadatacache.size` path; `runSubCommand` calls `MetadataCachingFileSystem.getMetadataCacheSize()` and returns a completed `URIStatus` with `FileInfo.length` set to that value.

Control flow and state: no cache mutation occurs. The command uses the `ls -l` file-size field as the user-visible transport for cache size.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `URIStatus`, `FileInfo`, `AlluxioURI`, and `Constants`.

Risks and test signals: size semantics depend on the underlying metadata-cache implementation. Like other subcommands, validation and filesystem-type checks are centralized in the abstract base.
