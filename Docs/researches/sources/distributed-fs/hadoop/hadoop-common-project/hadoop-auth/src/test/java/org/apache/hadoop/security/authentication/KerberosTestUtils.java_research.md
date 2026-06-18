<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java

## Purpose
Provides shared test utilities for MiniKDC-backed Kerberos authentication tests, including canonical test principals, keytab path generation, and helper methods that run callables as client or server subjects.

## Important APIs, types, and functions
`getRealm()`, `getClientPrincipal()`, `getServerPrincipal()`, and `getKeytabFile()` centralize test identity values. Inner `KerberosConfiguration` builds JAAS login options for IBM and non-IBM JVMs, including keytab, ticket cache, and debug options. `doAs()`, `doAsClient()`, and `doAsServer()` create a `LoginContext`, login with the test principal, run a callable through `Subject.doAs()`, and logout.

## Control flow
Tests create principals in the shared keytab, then wrap authenticated work in `doAsClient()` or `doAsServer()`. The helper preserves checked exceptions from the callable by unwrapping `PrivilegedActionException`.

## State and persistence
The generated keytab path is static and lives under `test.dir` or `target`. Login state is transient per helper invocation. It may interact with `KRB5CCNAME` environment/system properties.

## Dependencies and integration points
Used by Kerberos client/server tests and MiniKDC setup. Depends on JAAS, Kerberos principals, `KerberosUtil`, `PlatformName.IBM_JAVA`, and test keytab files.

## Risks and test signals
The static keytab path can leak across tests in the same JVM. Debug mode is always enabled. Tests using this helper are sensitive to local Kerberos/JDK behavior, ticket caches, and IBM option names. Signals include successful MiniKDC principal creation, login/logout cleanup, and both client/server principal execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/KerberosTestUtils.java -->
