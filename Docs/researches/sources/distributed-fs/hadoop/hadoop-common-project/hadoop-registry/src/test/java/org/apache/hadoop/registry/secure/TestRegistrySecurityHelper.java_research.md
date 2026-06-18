# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestRegistrySecurityHelper.java

Purpose: unit tests registry security ACL parsing, default realm expansion, UGI ACL creation, and secure configuration validation.

Important APIs and functions: class setup initializes `RegistrySecurity` as secure with a configured realm. Tests cover `splitAclPairs()`, `buildACLs()`, default realm insertion for SASL ACLs, mixed SASL/digest ACLs, default system accounts, JVM realm lookup, `createACLForUser()`, and the requirement that secure registry implies Kerberos authentication.

Control flow: ACL strings are split and built into ZooKeeper `ACL` objects, then IDs and schemes are asserted. Null realm with short SASL principals is expected to fail during ACL building.

State and persistence: no persistent external state; it initializes a test `RegistrySecurity` instance and reads current UGI/JVM realm.

Dependencies and integration: ties registry constants, ZooKeeper ACL permissions, Hadoop UGI, and `RegistrySecurity` parsing rules together.

Risks and test signals: strong parser coverage for realmed and short ACL strings. It does not run against a live secure ZooKeeper, so enforcement is covered separately by secure registry integration tests.
