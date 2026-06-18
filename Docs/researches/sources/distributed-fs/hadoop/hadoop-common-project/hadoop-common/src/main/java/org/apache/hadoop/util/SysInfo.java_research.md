# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfo.java

Purpose: `SysInfo` defines the public evolving abstraction for querying host resource information across operating systems.

Important APIs/types/functions: `newInstance()` chooses `SysInfoLinux` when `Shell.LINUX` is true, `SysInfoWindows` when `Shell.WINDOWS` is true, and throws `UnsupportedOperationException` otherwise. Abstract methods expose total/available virtual and physical memory, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU percentage, vcores used, aggregate network bytes, and aggregate storage bytes.

Control flow: the class performs no measurement itself. It is a dispatch and contract layer; concrete implementations decide caching and refresh behavior.

State and persistence behavior: `SysInfo` has no fields. Concrete instances may cache OS readings.

Dependencies and integration points: depends on `Shell` platform detection and the Linux/Windows implementations. Yarn resource monitors and daemon metrics can use this interface without platform-specific branching.

Risks: unsupported platforms fail at instance creation. The API returns primitive values with implementation-specific sentinel values such as `-1` for unavailable data, so callers must not assume every metric is populated.

Test signals: tests should verify platform dispatch under mocked shell flags and caller handling of unavailable metrics.
