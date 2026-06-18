# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/MiniKMS.java

## Purpose
`MiniKMS.java` is a test utility that starts an embedded KMS web server with generated/default configuration for integration tests.

## Important APIs, Types, and Functions
`MiniKMS.Builder` configures KMS conf directory, log4j file, port, and optional SSL keystore/password. `MiniKMS.start` creates missing `kms-acls.xml`, `core-site.xml`, and `kms-site.xml`, sets required system properties, configures host/port and optional SSL, starts `KMSWebServer`, and records the resulting URL. `getKMSUrl` and `stop` expose lifecycle control.

## Control Flow
Builder validation ensures required directories/files exist. `start` sets `kms.config.dir`, copies `mini-kms-acls-default.xml` if needed, writes minimal core-site and kms-site files when absent, sets simple authentication and a JCEKS provider under the conf dir, then starts the server on localhost at the requested port.

## State and Persistence
MiniKMS writes test configuration XML files and a provider URI pointing to `kms.keystore` under the chosen conf directory. Runtime state includes the embedded `KMSWebServer` and URL.

## Dependencies and Integration Points
It depends on `KMSWebServer`, `KMSConfiguration`, Hadoop `Configuration`, `Path`, `SSLFactory`, resource loading via `ThreadUtil`, and Commons IO. Tests can use it to exercise the same servlet/server stack as production.

## Risks
It mutates JVM-wide system properties, which can leak between tests if not isolated. Existing config files are respected rather than overwritten, so tests depend on directory cleanliness. `stop` wraps server stop failures in runtime exceptions.

## Test Signals
Tests should cover default file generation, custom config dir validation, custom port, SSL setup, URL availability, cleanup/stop behavior, and isolation of global system properties across test cases.
