## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileContext.java

Purpose: tests `FileContext` initialization with invalid default URIs and the interaction between configuration-driven and API-driven umask settings.

Important APIs/types/functions: `FileContext.getFileContext`, `FileSystem.FS_DEFAULT_NAME_KEY`, `CommonConfigurationKeys.FS_PERMISSIONS_UMASK_KEY`, `FileContext.getUMask`, `FileContext.setUMask`, `FsPermission.createImmutable`, and `UnsupportedFileSystemException`.

Control flow: `testDefaultURIWithoutScheme` sets the default FS to `/` and expects `UnsupportedFileSystemException`. `testConfBasedAndAPIBasedSetUMask` creates two file contexts from different file URIs, verifies default `022`, mutates the config to `011` and observes both contexts, then explicitly sets each context's umask and verifies later config changes no longer affect that context.

State and persistence: no files are created. State is held in shared `Configuration` and in per-`FileContext` umask override fields.

Dependencies/integration points: covers config propagation in `FileContext`, URI-based context selection, and permission defaults used by file creation across FileContext users.

Risks and test signals: the important regression signal is whether explicit `setUMask` freezes a context's setting while contexts without explicit settings continue reflecting configuration. URI parsing behavior overlaps with default-FS tests.
