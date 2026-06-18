# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/KerberosSecurityTestcase.java

## Purpose
`KerberosSecurityTestcase` is a JUnit base class that starts a `MiniKdc` before each test and stops it afterward, giving Kerberos-enabled tests a default embedded KDC.

## Important APIs, Types, and Functions
- Fields store `MiniKdc kdc`, `File workDir`, and `Properties conf`.
- `startMiniKdc()` is annotated `@BeforeEach`; it calls overridable `createTestDir()` and `createMiniKdcConf()`, constructs `MiniKdc`, and starts it.
- `createTestDir()` defaults the work directory to `System.getProperty("test.dir", "target")`.
- `createMiniKdcConf()` defaults to `MiniKdc.createConf()`.
- `stopMiniKdc()` is annotated `@AfterEach` and stops the KDC if present.
- Getters expose KDC, work directory, and properties to subclasses.

## Control Flow and State
Subclasses can override the setup hooks before `MiniKdc` construction. Runtime state includes a generated MiniKdc work subdirectory and system Kerberos properties modified by `MiniKdc`.

## Dependencies and Integration Points
It integrates JUnit 5 lifecycle annotations with `MiniKdc`. `TestMiniKdc` and `TestChangeOrgNameAndDomain` use it directly.

## Risks and Edge Cases
Because `MiniKdc` mutates JVM-wide Kerberos properties, tests inheriting this class should not run multiple KDC instances in parallel in the same JVM. Cleanup relies on `MiniKdc.stop()`.

## Test Signals
Subclasses validate that the base lifecycle successfully starts a KDC, creates keytabs, and supports JAAS login.
