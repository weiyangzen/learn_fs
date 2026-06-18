# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/StatUtils.java

Purpose: test helper for querying and changing filesystem permissions by shelling out to platform-specific commands.

Important APIs/types/functions: nested `Permission` value class, `getPermissionFromProcess`, `setPermissionFromProcess`, `removeDomain`, and `getPermissionStringFromProcess`.

Control flow: query builds `Shell.getGetPermissionCommand`, appends target path, starts a process, reads the first stdout line, tokenizes symbolic permissions, link count, owner, and group, strips Windows domains, and returns `FsPermission`. Set builds `Shell.getSetPermissionCommand` and executes it similarly.

State and persistence behavior: `setPermissionFromProcess` mutates real filesystem permissions. Query has no durable state beyond process execution.

Dependencies and integration points: integrates Hadoop `Shell`, `FsPermission`, Java `ProcessBuilder`, and a single-thread executor for stdout reading.

Risks and test signals: process handling is platform-sensitive and reads only first stdout line. The code starts an executor then calls `awaitTermination` before submitting, which is unusual but harmless for simple commands. Tests using it depend on shell command availability and permissions.
