# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestChangeOrgNameAndDomain.java

## Purpose
`TestChangeOrgNameAndDomain.java` verifies that MiniKdc tests still pass when the generated Kerberos realm is changed from the default.

## Important APIs, Types, and Functions
- The class extends `TestMiniKdc`, inheriting all startup, keytab, and login tests.
- It overrides `createMiniKdcConf()`, calls `super`, then sets `MiniKdc.ORG_NAME=APACHE` and `MiniKdc.ORG_DOMAIN=COM`.

## Control Flow and State
The overridden config hook runs before the inherited `KerberosSecurityTestcase.startMiniKdc()` constructs the KDC. This changes the realm to `APACHE.COM` for all inherited tests.

## Dependencies and Integration Points
The file depends on `TestMiniKdc`, `MiniKdc` property keys, and `Properties`. It is a reuse-based test rather than a standalone assertion class.

## Risks and Edge Cases
Because all inherited tests run under the custom realm, failures can indicate realm generation, keytab export, or JAAS login code has hard-coded `EXAMPLE.COM`.

## Test Signals
The inherited `testMiniKdcStart`, `testKeytabGen`, and `testKerberosLogin` provide the actual behavior signal under the customized realm.
