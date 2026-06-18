# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropAllCommand.java

Purpose: FUSE metadata-cache subcommand that clears all cached metadata entries.

Important APIs and helpers: `getCommandName()` returns `dropAll`; `getUsage()` builds the synthetic FUSE CLI path; `runSubCommand` calls `MetadataCachingFileSystem.dropMetadataCacheAll()` and returns a completed `URIStatus`; `getDescription()` describes the clear-all behavior.

Control flow and state: actual cache mutation is delegated to the metadata-caching filesystem. The command returns a mock `FileInfo` with `completed=true` so FUSE shell calls can surface success through file metadata.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `AlluxioURI`, `URIStatus`, `FileInfo`, and `Constants`.

Risks and test signals: no argument validation is implemented because no arguments are expected. It relies on the abstract base to enforce cache-enabled state and filesystem type.
