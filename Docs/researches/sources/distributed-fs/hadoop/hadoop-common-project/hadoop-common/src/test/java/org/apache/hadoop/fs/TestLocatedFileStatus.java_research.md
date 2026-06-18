# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocatedFileStatus.java

Purpose: verifies deprecated `LocatedFileStatus` constructors remain usable with null and non-null permissions.

Important APIs/types/functions: `LocatedFileStatus`, `BlockLocation`, `FsPermission`, `Path`, and Mockito `mock`.

Control flow/state/persistence: creates a mocked block-location array, constructs one status with a null permission, and constructs another with a mocked permission. No assertions are needed beyond successful construction.

Dependencies/integration points: protects binary/source compatibility for legacy callers constructing located statuses directly.

Risks/test signals: catches constructor nullability regressions or accidental removal/behavior changes in deprecated status construction paths.
