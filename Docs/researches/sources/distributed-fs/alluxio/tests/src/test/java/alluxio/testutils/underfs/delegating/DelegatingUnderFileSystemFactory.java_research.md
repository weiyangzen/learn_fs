# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/delegating/DelegatingUnderFileSystemFactory.java

Purpose: simple test factory that returns a preconstructed `UnderFileSystem` for paths beginning with the `delegating` scheme.

Important APIs and control flow: `DELEGATING_SCHEME` is `"delegating"`. The constructor stores the UFS. `create` ignores path and configuration and returns `mUfs`. `supportsPath` checks `path.startsWith(DELEGATING_SCHEME)`.

State, dependencies, integration, risks, tests: state is a single UFS instance shared across all creates, so tests can install a controlled delegate or spy. Dependencies are minimal: `UnderFileSystem`, `UnderFileSystemConfiguration`, and factory interface. Risk: `supportsPath` does not null-check and accepts strings like `delegatingBad`, so callers must pass validated paths or tests may match more broadly than intended.
