# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGIWithExternalKdc.java

Purpose: verifies UGI keytab login against a user-provided external KDC when explicitly enabled. It is a guarded integration test for deployments that want to validate real Kerberos infrastructure rather than MiniKdc.

Important APIs and types: `SecurityUtilTestHelper.isExternalKdcRunning`, JUnit `assumeTrue`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, `AuthenticationMethod.KERBEROS`, `Configuration`, and `CommonConfigurationKeys.HADOOP_SECURITY_AUTHENTICATION`.

Control flow: `@BeforeEach` skips the test unless external KDC support is enabled. The test reads `user.principal` and `user.keytab` system properties, configures Hadoop security authentication to Kerberos, logs in through UGI, and asserts the returned UGI uses Kerberos. It then attempts to log in as a bogus principal using the same keytab and expects failure.

State and persistence: reads JVM system properties for principal, keytab, and external KDC enablement; mutates static UGI configuration. It does not create files and depends entirely on externally provisioned Kerberos files/config.

Dependencies and integration points: integrates with real `java.security.krb5.conf`, real KDC service, external keytab material, and Hadoop UGI Kerberos login. It is intentionally skipped in normal unit-test environments.

Risks: unavailable or misconfigured external KDC causes skip or failure. Printing caught exception stack traces can create noisy logs. Because the keytab is external, failures may indicate environmental drift rather than code regression.

Test signals: when enabled, provides high-value end-to-end proof that UGI can authenticate with real Kerberos and rejects mismatched principals.
