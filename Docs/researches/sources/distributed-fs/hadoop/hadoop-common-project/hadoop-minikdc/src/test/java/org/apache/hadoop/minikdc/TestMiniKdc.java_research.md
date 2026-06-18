# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/test/java/org/apache/hadoop/minikdc/TestMiniKdc.java

## Purpose
`TestMiniKdc.java` validates the embedded MiniKdc lifecycle, keytab generation, and Kerberos login interoperability.

## Important APIs, Types, and Functions
- The class extends `KerberosSecurityTestcase`, so each test receives a running KDC.
- `shouldUseIbmPackages()` and `isSystemClassAvailable()` detect IBM Java JAAS module differences.
- `testMiniKdcStart()` asserts the KDC binds a nonzero port.
- `testKeytabGen()` creates principals `foo/bar` and `bar/foo`, loads the keytab with Kerby `Keytab`, and verifies realm-qualified principal names.
- Nested `KerberosConfiguration` builds JAAS `AppConfigurationEntry` options for client and server login, with IBM and non-IBM option sets.
- `testKerberosLogin()` creates a `foo` principal/keytab, logs in as client and server, validates the resulting `Subject` contains one `KerberosPrincipal` named `foo@REALM`, and logs out.

## Control Flow and State
MiniKdc is started by the base class. Tests create keytabs in the work directory, then use JAAS `LoginContext` to authenticate. `finally` cleanup logs out if credentials remain.

## Dependencies and Integration Points
The test integrates MiniKdc, Apache Kerby keytab parsing, Java JAAS, `Subject`, `KerberosPrincipal`, and JUnit assertions. It guards compatibility across standard Sun/Oracle/OpenJDK and IBM Java security modules.

## Risks and Edge Cases
JAAS option names differ between IBM and non-IBM runtimes. Environment variable `KRB5CCNAME` is optionally propagated as `ticketCache`, which can affect login behavior. The test assumes generated `krb5.conf` and keytabs are visible to JAAS after MiniKdc startup.

## Test Signals
It provides core smoke coverage that MiniKdc can start, issue principals, export usable keytabs, and authenticate both initiator and acceptor style logins.
