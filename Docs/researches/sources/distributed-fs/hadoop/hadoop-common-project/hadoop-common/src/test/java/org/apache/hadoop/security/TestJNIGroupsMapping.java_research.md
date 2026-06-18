# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestJNIGroupsMapping.java

Purpose: Compares JNI and shell-based Unix group lookup implementations.

Important APIs/types/functions: `NativeCodeLoader.isNativeCodeLoaded`, `JniBasedUnixGroupsMapping`, `ShellBasedUnixGroupsMapping`, `UserGroupInformation.getCurrentUser`, and helper `testForUser`.

Control flow: `@BeforeEach` skips unless native code is loaded. The test compares sorted group arrays for the current user and a deliberately nonexistent user.

State and persistence: reads OS user/group database through shell and JNI paths.

Dependencies/integration points: native Hadoop library, Unix group APIs, shell group command implementation.

Risks: environment-dependent; group database changes during test can fail parity; skipped without native code, leaving JNI path untested.

Test signals: validates native group lookup returns the same groups as shell fallback for existing and missing users.
