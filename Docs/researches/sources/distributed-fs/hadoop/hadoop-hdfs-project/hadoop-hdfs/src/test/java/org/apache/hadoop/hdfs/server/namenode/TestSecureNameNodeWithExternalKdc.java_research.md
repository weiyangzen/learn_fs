# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNodeWithExternalKdc.java

Purpose: Optional integration test for running a secure NameNode against an externally supplied KDC, principals, and keytabs. It verifies non-superuser Kerberos access semantics in an environment closer to deployment than the in-process test KDC.

Important APIs and functions: `testExternalKdcRunning()` uses `assumeTrue(isExternalKdcRunning())` to skip when not configured. `testSecureNameNode()` reads system properties for NameNode Kerberos/SPNEGO principals, keytab, user principal, and user keytab; configures `HADOOP_SECURITY_AUTHENTICATION`, NameNode principal keys, and keytab path; then uses UGI keytab login.

Control flow: The test starts a secure zero-DN cluster, uses the current/superuser filesystem to create writable `/tmp`, logs in the specified non-superuser, verifies writing `/users` fails, then creates and lists `/tmp/alpha` and checks Kerberos authentication.

State and persistence behavior: Runtime state includes external Kerberos credentials, NameNode security configuration, filesystem permissions, and UGI authentication method. No persistent NameNode restart is involved.

Dependencies and integration points: Integrates external KDC availability, system properties, HDFS security config, MiniDFSCluster, permissions, and UGI.

Risks: The test is intentionally environment-dependent and skipped unless the external KDC flag/helper says it is available. Misconfigured principals or accidentally superuser credentials invalidate the scenario.

Test signals: Passing requires all required system properties, successful secure cluster startup, denied root-level user write, successful write in `/tmp`, and `AuthenticationMethod.KERBEROS`.
