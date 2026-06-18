# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/FuseShellTest.java

Purpose: isolation tests for the FUSE special command shell, particularly metadata-cache commands addressed through `.alluxiocli` paths. The fixture builds a `MetadataCachingFileSystem` around a mocked `FileSystemContext` and a custom `GetStatusFileSystemMasterClient`, primes two cached statuses, then removes backing map entries so later hits prove cache behavior.

Important APIs and control flow: `isSpecialCommand` distinguishes reserved `.alluxiocli.metadatacache.*` paths from normal user paths. `runCommand` rejects disabled metadata cache, unknown command groups, and unknown subcommands with `InvalidArgumentRuntimeException`. Valid commands return cache size, drop one path cache entry, or drop all entries.

State, dependencies, integration, risks, tests: the main state is the metadata cache inside `MetadataCachingFileSystem`, with `mFileStatusMap` acting as the master source. Dependencies include PowerMock, Mockito, `BaseFileSystem`, `CloseableResource`, and `GetStatusPOptions`. Risks include reliance on cache internals and equality of `URIStatus`; tests do not exercise concurrent cache mutation or command paths outside metadata cache.
