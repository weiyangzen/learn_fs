# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/AbstractSecureRegistryTest.java

Purpose: shared fixture for Kerberos-secured registry and ZooKeeper tests. It provisions a MiniKdc, principals, keytabs, JAAS file, Hadoop security configuration, and secure `MicroZookeeperService` instances.

Important APIs and functions: class setup initializes `RegistrySecurity`, KDC, JAAS system properties, and Kerberos rules. `setupKDCAndPrincipals()` creates keytabs for ZooKeeper, Alice, and Bob and writes JAAS entries. `createSecureZKInstance()` configures a secure micro ZooKeeper. `login()` creates a JAAS `LoginContext`; `startSecureZK()` logs in the ZooKeeper server principal and starts the secure service.

Control flow: class lifecycle starts security once; instance lifecycle stops per-test services and secure ZooKeeper. Principal choice differs on Windows for localhost versus 127.0.0.1. Kerberos short-name mapping uses a fixed rule that strips the `EXAMPLE.COM` realm.

State and persistence: writes KDC work files, keytabs, and `jaas.txt` under `target/kdc` or `test.dir`. It mutates JVM JAAS and Hadoop security state.

Dependencies and integration: integrates MiniKdc, Hadoop UGI, KerberosName, registry security, ZooKeeper SASL options, service lifecycle, and test name extension.

Risks and test signals: expensive and environment-sensitive but necessary for secure registry coverage. Global JVM security properties and Kerberos rules can leak if teardown is incomplete; the fixture explicitly stops services and clears login state.
