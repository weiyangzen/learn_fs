# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSWithKerberos.java

Purpose: Kerberos/SPNEGO integration tests for HTTPFS access and delegation tokens.

Important APIs/types/functions: `createHttpFSServer`, `resetUGI`, `testValidHttpFSAccess`, `testInvalidadHttpFSAccess`, `testDelegationTokenHttpFSAccess`, `testDelegationTokenWithFS`, and `testDelegationTokenWithinDoAs`. It uses `KerberosTestUtils`, `AuthenticatedURL`, `DelegationTokenAuthenticator`, `UserGroupInformation`, `HttpFSFileSystem`, and `WebHdfsFileSystem`.

Control flow: setup writes HTTPFS/HDFS config with `httpfs.authentication.type=kerberos`, configures proxyuser entries, starts Jetty, and sets HTTPFS authority. Valid access runs inside a Kerberos client subject and expects OK; invalid unauthenticated access expects unauthorized. Delegation-token tests obtain tokens via SPNEGO, use them for HTTPFS access, require SPNEGO for renew, allow cancel, and verify canceled-token denial. FileSystem tests login or create proxy users, obtain delegation tokens through filesystem implementations, set the token on a renewable filesystem, and list `/`.

State and persistence: global UGI configuration is reset after each test. The helper relies on system properties/keytab defaults for realm, principals, and keytab path; local configs and secrets are written in the test directory.

Dependencies/integration: integrates JAAS/Kerberos, Hadoop UGI, HTTPFS authentication, delegation token JSON, and both HTTPFS and WebHDFS filesystem clients.

Risks and test signals: high-value auth coverage but environment-sensitive because it assumes usable Kerberos test credentials/keytabs. The hard-coded `loginUserFromKeytab("client", "/Users/tucu/tucu.keytab")` path in the doAs helper path is especially brittle unless the test harness intercepts or configures it.
