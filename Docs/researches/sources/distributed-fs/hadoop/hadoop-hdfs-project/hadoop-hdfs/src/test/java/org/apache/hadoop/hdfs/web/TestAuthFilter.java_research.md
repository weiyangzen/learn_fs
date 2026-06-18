# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestAuthFilter.java

Purpose: verifies WebHDFS HTTP authentication filter initialization from Hadoop configuration.

Important APIs/types/functions: `AuthFilterInitializer.initFilter`, `FilterContainer.addFilter`, `AuthFilter`, `PseudoAuthenticationHandler.ANONYMOUS_ALLOWED`, Mockito `doAnswer`.

Control flow: the test creates a configuration with `hadoop.http.authentication.*` Kerberos settings. A mocked `FilterContainer` intercepts `addFilter`; the answer asserts filter name/class and inspects the generated parameter map for cookie path, auth type, absent cookie domain, Kerberos principal/keytab, and anonymous allowed flag. Finally, `AuthFilterInitializer` is invoked.

State and persistence behavior: no persistence; all state is config and mocked call arguments.

Dependencies and integration points: connects HDFS Web auth initialization to Hadoop HTTP server filter registration and authentication-server constants.

Risks: raw Mockito `Answer` and unchecked map cast suppress type safety. It covers default cookie path/domain and anonymous flag but not alternate cookie domain or simple auth configurations.

Test signals: one filter registration with expected name/class and a correctly translated auth parameter map.
