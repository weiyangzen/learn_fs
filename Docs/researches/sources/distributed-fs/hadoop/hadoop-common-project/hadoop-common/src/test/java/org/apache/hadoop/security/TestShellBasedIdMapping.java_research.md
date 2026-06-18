# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestShellBasedIdMapping.java

Purpose: validates `ShellBasedIdMapping` behavior for Unix/NFS user and group ID mapping, including static map parsing, shell command parsing, duplicate resolution, unsigned 32-bit overflow handling, refresh intervals, and incremental lookup updates.

Important APIs and types: `ShellBasedIdMapping`, `ShellBasedIdMapping.StaticMapping`, `ShellBasedIdMapping.PassThroughMap`, `parseStaticMap`, `updateMapInternal`, `getUidNameMap`, `getGidNameMap`, `getUid`, `getGid`, `getUserName`, `getGroupName`, `clearNameMaps`, `IdMappingConstant`, Guava `BiMap`/`HashBiMap`, and `Configuration`.

Control flow: tests create temporary static map files, parse `uid`/`gid` lines with comments, tabs, empty lines, and large unsigned values, then assert pass-through behavior for unmapped IDs. Shell parser tests feed synthetic `echo | cut` commands into `updateMapInternal` to build user/group maps. Refresh tests compare a reference mapper against an incremental mapper, repeatedly clearing maps and changing the static mapping file before `getUid`/`getGid` calls. Duplicate tests verify first/last retained names in the bidirectional map. Update interval tests verify defaults, minimum clamp, and custom timeout.

State and persistence: writes temp static map files and depends on their modification time for refresh behavior; one loop sleeps briefly to avoid same-mtime ambiguity. It also shells out or emulates shell commands and can read real local account/group maps in incremental tests.

Dependencies and integration points: integrates Hadoop NFS ID mapping constants, platform assumptions (`assumeNotWindows`), shell command execution, local OS passwd/group sources, and Guava bidirectional maps.

Risks: non-Windows tests depend on host account database stability. Static map refresh is mtime-sensitive. Duplicate resolution depends on `HashBiMap` replacement semantics and the order of command output. Unsigned ID overflow mapping to signed Java `int` values is intentional but easy to regress.

Test signals: good coverage for parser robustness, static remap precedence, duplicate filtering, 32-bit boundary IDs, timeout configuration, and incremental cache population through individual lookup APIs.
