## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DF.java

Purpose: `DF` provides filesystem disk-space statistics for a local path. It uses Java `File` APIs for capacity, used, and available bytes, and the platform `df` command on Unix-like systems to identify filesystem and mount point.

Important APIs and types: constructors accept `File` plus either `Configuration` or refresh interval. Accessors include `getDirPath`, `getFilesystem`, `getCapacity`, `getUsed`, `getAvailable`, `getPercentUsed`, and `getMount`. It extends `Shell`, overrides `getExecString` and `parseExecResult`, and exposes `parseOutput` for tests.

Control flow, state, and persistence: construction stores the canonical path and initializes an output buffer. `getFilesystem` and `getMount` use Windows drive-letter logic on Windows and otherwise run `df -k -P`, verify exit code, and parse output. `parseOutput` handles long filesystem names split across lines. State is cached in fields but refreshed by `Shell.run()` according to the interval; no durable persistence exists.

Dependencies and integration: HDFS and MapReduce disk accounting use this class, and `DFCachingGetSpaceUsed` wraps it for cached usage estimates. It depends on `Shell`, `Configuration`, `CommonConfigurationKeys`, and `java.io.File`.

Risks and test signals: parsing is sensitive to locale/output shape, command availability, paths containing shell-sensitive characters, and zero-capacity percent math. Tests should cover Windows branches, missing paths, long filesystem lines, nonzero exit codes, malformed numeric fields, and consistency between Java `File` usage values and parsed mount identity.
