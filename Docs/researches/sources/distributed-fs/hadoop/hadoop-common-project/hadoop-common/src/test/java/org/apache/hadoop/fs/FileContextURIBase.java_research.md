# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextURIBase.java

## Purpose
`FileContextURIBase` is an abstract cross-URI test suite for `FileContext`. It verifies that one `FileContext` can operate on paths qualified for another context or filesystem and that both contexts observe the same created, deleted, listed, and status-queried resources.

## Important APIs, Types, And Functions
The fixture exposes `protected FileContext fc1` and `fc2`. `qualifiedPath(String, FileContext)` creates a path under a static temp base and qualifies it with the provided context. `isTestableFileNameOnPlatform()` filters filenames invalid on Windows, using a pattern that rejects reserved characters and trailing space/dot. Tests use `FileContextTestHelper` static helpers, `FsPermission`, `LambdaTestUtils`, `Shell.WINDOWS`, and `RemoteIterator<FileStatus>`.

## Control Flow
The suite creates files and directories through one context using paths qualified by another, then checks visibility through the other context. It covers unusual filenames, null names, duplicate create failure, parent auto-creation, directory creation, mkdir under files, directory predicates, delete idempotence for files and directories, modification time equality, filesystem status, expected `FileNotFoundException` behavior, and array/iterator listing.

## State And Persistence Behavior
All test state lives under the static `BASE` path from `GenericTestUtils.getTempPath("testContextURI")`. `tearDown()` deletes `BASE` through `fc2`, relying on the comment that `fc1` and `fc2` point to the same location in concrete subclasses. File and directory names intentionally include spaces and punctuation when platform-valid.

## Dependencies And Integration Points
Concrete subclasses initialize `fc1` and `fc2`, commonly to localfs or viewfs combinations. The suite tests integration between `FileContext` path qualification, URI routing, filesystem status, and `FileContext.Util` listing APIs.

## Risks
The assumption that `fc1` and `fc2` share cleanup location is important; if a subclass points them to different backends, cleanup may leak state. Some assertions require positive capacity/remaining/used values, which can be unsuitable for mock or virtual filesystems. Windows filename filtering intentionally narrows coverage on that platform.

## Test Signals
Passing tests indicate correct cross-context URI dispatch, path qualification, create/delete/list/status coherence, error behavior for missing paths, and platform-aware handling of special filenames.
