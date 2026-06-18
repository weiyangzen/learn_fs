# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InternalOperations.java

Purpose: `InternalOperations` exposes package-scoped `FileSystem` operations to implementation packages such as `org.apache.hadoop.fs.impl` without making them public API.

Important APIs: `rename(FileSystem, Path, Path, Options.Rename...)`.

Control flow and state: it simply calls the protected/deprecated `FileSystem.rename(src,dst,options)` method. It holds no state.

Dependencies and integration: used by Hadoop filesystem implementation code that needs access to rename-with-options behavior while preserving API boundaries.

Risks: this is intentionally not for applications; broader use would couple external code to internal compatibility shims. It suppresses deprecation because Hadoop still needs the protected API for selected flows.

Test signals: rename option propagation, overwrite behavior, exception propagation, and visibility/use from implementation packages.
