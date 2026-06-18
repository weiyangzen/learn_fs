# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/servlet/TestHostnameFilter.java

Purpose: Unit tests for `HostnameFilter` thread-local remote hostname capture and cleanup.

Important APIs/types/functions: tests `hostname` and `testMissingHostname`; `HostnameFilter.get`, `doFilter`, and servlet `FilterChain`.

Control flow: mocked requests supply either `localhost` or null remote address. During the downstream chain, the test asserts the thread-local hostname resolves to a localhost representation or placeholder `???`; after `doFilter`, it asserts the thread-local is cleared.

State and persistence: uses a thread-local in `HostnameFilter`; no external persistence.

Dependencies/integration: Mockito, servlet API, and JUnit.

Risks and test signals: important cleanup signal for request-scoped logging context. Hostname resolution can vary by OS, so the test accepts `localhost` or `127.0.0.1`.
