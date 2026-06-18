# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestMDCFilter.java

Purpose: Unit tests for `MDCFilter`, which populates and clears SLF4J MDC fields for request logging.

Important APIs/types/functions: test `mdc`, mocked `HttpServletRequest`, `HostnameFilter.HOSTNAME_TL`, SLF4J `MDC`, and servlet `FilterChain`.

Control flow: first request has no principal and no hostname; chain sees method/path only. Second request adds a principal and chain sees user/method/path. Third sets `HostnameFilter` thread-local and chain sees hostname/user/method/path. After each filter call, key fields are expected to be cleared where checked.

State and persistence: thread-local MDC and hostname state only; `MDC.clear` starts the test.

Dependencies/integration: servlet API, Mockito, SLF4J MDC, and `HostnameFilter`.

Risks and test signals: good request-context cleanup signal. The final hostname thread-local is removed manually, and the test mainly validates in-chain values rather than every post-chain cleanup path after later invocations.
