# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUGILoginFromKeytab.java

Purpose: integration-tests `UserGroupInformation` keytab login and relogin semantics with `MiniKdc`, including renewal executor configuration, subject-derived UGI behavior, failed relogin recovery, and concurrent relogin synchronization.

Important APIs and types: `MiniKdc`, `UserGroupInformation.loginUserFromKeytab`, `loginUserFromKeytabAndReturnUGI`, `getUGIFromSubject`, `loginUserFromSubject`, `reloginFromKeytab`, `forceReloginFromKeytab`, `isFromKeytab`, `KerberosTicket`, `KerberosPrincipal`, `LoginContext`, `Subject`, `User`, renewal config keys, `CyclicBarrier`, `CountDownLatch`, and executor services.

Control flow: `@BeforeEach` enables Kerberos auth, resets immediate-renew behavior, starts a MiniKdc, and creates a thread pool; `@AfterEach` stops both. Basic tests create principals/keytabs, log in, assert `isFromKeytab`, last-login time, and new `LoginContext` on relogin. Subject tests remove or modify Hadoop `User` principals to distinguish managed keytab logins from external subjects. Renewal tests toggle `HADOOP_KERBEROS_KEYTAB_LOGIN_AUTORENEWAL_ENABLED`. Relogin tests compare ticket identity/auth time across login users and external subject users. Failure recovery renames the keytab to force `KerberosAuthException`, then restores it. The concurrency test blocks logout on a barrier to prove relogins serialize while `getCurrentUser` remains nonblocking.

State and persistence: creates MiniKdc work directories and keytab files under JUnit temp dirs, mutates static UGI configuration/login user, toggles renewal test flags, and starts executor threads. Cleanup shuts down KDC and executor but relies on JUnit temp cleanup for files.

Dependencies and integration points: integrates JAAS login, Java Kerberos credentials, Hadoop UGI internals, MiniKdc, Mockito spies, and concurrent Java primitives.

Risks: Kerberos integration and timing sleeps can be slow/flaky. Static UGI state and global Kerberos config can leak. Concurrency assertions rely on barriers and timeouts. Keytab rename behavior depends on local filesystem semantics.

Test signals: strong integration signal for keytab login, managed versus external subject relogin isolation, renewal executor activation, failure recovery, and credential corruption prevention under concurrent relogin.
