# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestChRootedFs.java

Purpose: Tests `ChRootedFs`, the `AbstractFileSystem`/`FileContext` chroot wrapper, for path translation, core operations, working directory behavior, name validation, resolve behavior, and snapshot delegation.

Important APIs/types/functions: `ChRootedFs`, `FileContext`, `AbstractFileSystem`, `FileContextTestHelper`, `CreateFlag`, `FileContext.DEFAULT_PERM`, `isValidName`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, and Mockito spies.

Control flow: `setUp` creates a local `FileContext` root and wraps the default `AbstractFileSystem` in a `ChRootedFs` exposed through `FileContext`. Tests mirror file-system operations from `TestChRootedFileSystem`: create/delete files recursively and non-recursively, mkdir/delete, rename files/dirs, cross-filesystem-looking rename, list root contents, working-directory relative/absolute/URI transitions, open/create relative to cwd, and resolve existing/non-existing paths. Name validation tests spy on the base FS to ensure `/test` is translated to `/chroot/test`. Snapshot tests spy on the base FS, translate the snap root by appending to chroot path without scheme/authority, and verify delegation/return value.

State/persistence: Uses real local `FileContext` test directories cleaned after each test. Spy-based tests avoid real snapshot implementation by stubbing base FS methods.

Dependencies/integration: Integrates chroot translation with the newer `FileContext`/`AbstractFileSystem` stack and base `FileContext*` helpers.

Risks: Similar URI/path qualification caveat as `ChRootedFileSystem`. Working-directory behavior differs from `FileSystem` version by expecting non-existing cwd to fail. Snapshot tests validate delegation but not actual snapshot persistence.

Test signals: Raw target existence checks, file status path expectations, qualified working directories, missing resolve exception, translated `isValidName` calls, and translated snapshot method invocations.
