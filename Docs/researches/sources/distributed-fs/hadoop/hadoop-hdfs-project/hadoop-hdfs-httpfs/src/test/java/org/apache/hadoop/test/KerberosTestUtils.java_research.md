# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/KerberosTestUtils.java

Purpose: Kerberos test utility for constructing principals/keytab paths and running callables under JAAS-authenticated client or server subjects.

Important APIs/types/functions: property constants for realm/client/server/keytab, getters `getRealm`, `getClientPrincipal`, `getServerPrincipal`, `getKeytabFile`, nested `KerberosConfiguration`, and methods `doAs`, `doAsClient`, `doAsServer`.

Control flow: getters read system properties with defaults. `KerberosConfiguration` builds JAAS login-module options for keytab use, ticket cache, renewal, krb5 refresh, initiator mode, and debug. `doAs` creates a subject with a Kerberos principal, logs in via `LoginContext`, executes the callable through `Subject.doAs`, unwraps privileged exceptions, and logs out in `finally`.

State and persistence: depends on keytab and ticket cache files outside the repo; mutates JAAS login session only during invocation.

Dependencies/integration: Java security/JGSS/JAAS, Hadoop `KerberosUtil`, and test Kerberos system properties.

Risks and test signals: powerful but environment-sensitive. Defaults point to `${user.home}/${user.name}.keytab`, so tests require explicit properties or local credentials.
