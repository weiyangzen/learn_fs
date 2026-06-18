# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystem.java

Purpose: latency-injecting local UFS for tests. It extends `LocalUnderFileSystem`, sleeps for configured durations before selected operations, and otherwise preserves local UFS behavior.

Important APIs and control flow: overrides lifecycle, connection, create/createDirect, delete, exists, status, location, fingerprint, space, type, directory/file checks, list, mkdirs, open, rename, setOwner, setMode, and supportsFlush. Each operation calls `sleepIfNecessary` with the matching option, strips the `sleep` scheme via `cleanPath`, and delegates to `super`. `renameFile` distinguishes temporary file names with `PathUtils.isTemporaryFileName`.

State, dependencies, integration, risks, tests: state is `SleepingUnderFileSystemOptions`. Persistence is local filesystem persistence inherited from `LocalUnderFileSystem`. Dependencies include `CommonUtils.sleepMs`, `PathUtils`, UFS options, and status classes. Risks include sleeps blocking test threads, negative durations meaning no sleep, and only overridden methods receiving latency injection; inherited methods not listed have normal timing.
