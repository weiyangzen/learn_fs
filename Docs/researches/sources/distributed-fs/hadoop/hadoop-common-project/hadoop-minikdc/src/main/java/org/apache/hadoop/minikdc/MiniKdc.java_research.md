# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/src/main/java/org/apache/hadoop/minikdc/MiniKdc.java

## Purpose
`MiniKdc.java` implements an embeddable and command-line Mini KDC backed by Apache Kerby `SimpleKdcServer`. It is used by Hadoop tests that need real Kerberos principals, keytabs, and `krb5.conf` behavior.

## Important APIs, Types, and Functions
- Public configuration keys include `ORG_NAME`, `ORG_DOMAIN`, `KDC_BIND_ADDRESS`, `KDC_PORT`, `INSTANCE`, `MAX_TICKET_LIFETIME`, `MIN_TICKET_LIFETIME`, `MAX_RENEWABLE_LIFETIME`, `TRANSPORT`, and `DEBUG`.
- `createConf()` returns a clone of default properties: localhost, ephemeral port, realm `EXAMPLE.COM`, TCP transport, ticket lifetime defaults, and debug false.
- Constructor validates required properties, creates a timestamped working directory under the supplied build directory, logs config, parses port, and derives upper-case realm from organization name/domain.
- `start()` constructs `SimpleKdcServer`, calls `prepareKdcServer()`, initializes, rewrites default realm in generated `krb5.conf`, and starts the server.
- `prepareKdcServer()` sets work dir, host, realm, TCP/UDP port, transport flags, KDC service name, debug system property, and ticket lifetime config.
- `stop()` stops the Kerby server, restores debug system property, recursively deletes work dir, sleeps for a Kerby cleanup delay, and logs shutdown.
- `createPrincipal(String,password)` and `createPrincipal(File,String...)` create KDC principals and export keytabs.
- `main()` supports standalone usage: work dir, properties file, keytab file, and principals.

## Control Flow and State
MiniKdc owns server state (`SimpleKdcServer`), selected port, realm, work directory, generated `krb5.conf`, transport, and saved Kerberos debug flag. It mutates JVM system properties `java.security.krb5.conf` indirectly through Kerby and `sun.security.krb5.debug` directly. Keytab files are created externally at caller-specified paths; internal work directories are deleted on stop.

## Dependencies and Integration Points
The implementation depends on Apache Kerby `SimpleKdcServer`, `KdcConfigKey`, `NetworkUtil`, `IOUtil`, SLF4J, and Java properties/filesystem APIs. It is used by KMS security tests and MiniKdc tests as an embedded Kerberos authority.

## Risks and Edge Cases
Important risks include global JVM Kerberos property mutation, no parallel KDC safety in one JVM, recursive deletion of the generated work directory, TCP/UDP transport validation, port selection races when port is 0, and the synchronized `stop()` sleep suppressed by SpotBugs. The copy constructor for required property set appears to add `KDC_BIND_ADDRESS` twice and omits `MIN_TICKET_LIFETIME` from required properties, which is intentional or legacy because minimum lifetime is optional.

## Test Signals
`TestMiniKdc` verifies startup, nonzero port selection, keytab generation, and JAAS client/server login. `TestChangeOrgNameAndDomain` verifies realm customization via overridden config.
