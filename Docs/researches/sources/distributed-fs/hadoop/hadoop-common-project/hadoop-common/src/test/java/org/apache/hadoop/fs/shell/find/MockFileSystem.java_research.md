# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/MockFileSystem.java

Purpose: Test-only `FilterFileSystem` implementation that lets `PathData` and `Find` resolve the URI scheme `mockfs:///` while delegating operations to a Mockito `FileSystem`.

Important APIs/types/functions: static `setup()`, constructor `MockFileSystem()`, overrides `initialize`, `makeQualified`, `globStatus`, `getWorkingDirectory`, and `resolvePath`.

Control flow: `setup` lazily creates and resets a static mock filesystem, constructs a `Configuration` with `fs.defaultFS=mockfs:///` and `fs.mockfs.impl=MockFileSystem`, stubs `getConf`, and returns the mock for tests to program. The wrapper constructor passes the static mock into `FilterFileSystem`. Overrides keep qualification and resolution identity-based and return `/` as working directory.

State/persistence: Holds a static Mockito mock across tests but resets it on each setup. No real filesystem state is used.

Dependencies/integration: Bridges Hadoop filesystem service loading with Mockito-driven unit tests for `find` expressions and traversal. It is essential because `PathData` asks Hadoop to instantiate a `FileSystem` from configuration.

Risks: Static state requires strict reset discipline. The wrapper deliberately simplifies qualification and resolution, so it does not model all real filesystem behavior. Tests using it must explicitly stub every operation they expect.

Test signals: Indirect; downstream find tests validate that `PathData` and `Find` interact with the mock as configured.
