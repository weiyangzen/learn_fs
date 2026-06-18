# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureRegistry.java

Purpose: integration tests secure `MicroZookeeperService` startup and Curator client behavior against SASL-enabled ZooKeeper.

Important APIs and functions: tests cover creating secure ZooKeeper, connecting with an insecure client after root creation, ZooKeeper principal write access, and SASL system property overwrite semantics. Helper `startCuratorServiceInstance()` configures a Curator client against `secureZK`; `userZookeeperToCreateRoot()` logs in as ZooKeeper and creates `/`.

Control flow: tests enable Kerberos debugging before each run and clear ZooKeeper SASL properties afterward. Secure paths log in through `LoginContext`, set SASL client properties, start Curator, create paths, and clean up login/client state in finally blocks.

State and persistence: mutates secure ZooKeeper state, JVM SASL system properties, and login contexts. Root ACLs are world read/write for test accessibility.

Dependencies and integration: integrates secure fixture, `CuratorService`, `RegistrySecurity`, ZooKeeper SASL option constants, and path dumping diagnostics.

Risks and test signals: covers secure startup and client property behavior. The insecure-client test is deliberately permissive after root creation, so it should not be interpreted as full ACL enforcement coverage.
