# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/httpfs-default.xml

## Purpose
`httpfs-default.xml` provides default HttpFS server configuration: listener address, SSL, Hadoop HTTP server settings, service list, authentication, proxy-user examples, delegation-token timing, Hadoop backend authentication, filesystem cache purge, and access-mode defaults.

## Important APIs, Types, and Functions
Key properties include `httpfs.http.port` (`14000`), `httpfs.http.hostname` (`0.0.0.0`), `httpfs.http.administrators`, `httpfs.ssl.enabled`, Hadoop HTTP thread/header/temp settings, `httpfs.buffer.size`, `httpfs.services`, Kerberos principal/keytab properties, proxy-user property examples, delegation token intervals, `httpfs.hadoop.authentication.*`, filesystem cache purge frequency/timeout, and `httpfs.access.mode`.

## Control Flow
The file is loaded into Hadoop `Configuration` during HttpFS startup. Variable interpolation links properties such as `httpfs.hostname` to `httpfs.http.hostname`, Kerberos principals to realm/host values, and secret/temp paths to config/tmp directories.

## State and Persistence
This is static configuration shipped with the application. Runtime state is created by services that consume the settings, such as secret files, Kerberos logins, filesystem cache entries, and delegation token managers.

## Dependencies and Integration Points
`ServerWebApp` and `HttpFSServerWebServer` consume listener and SSL properties. `HttpFSAuthenticationFilter` consumes Hadoop HTTP authentication settings. `FileSystemAccessService` consumes backend auth/cache settings. `TestHttpFSAccessControlled` mutates `httpfs.access.mode` at runtime to verify read-write, write-only, and read-only behavior.

## Risks
Defaults are simple-auth and non-SSL, which are suitable for test/dev but insecure for production unless overridden. The typo `FORBIDDED` appears in the description only. Default wildcard examples for proxy users are comments, not active settings. Secret-file handling must be secured by deployment permissions.

## Test Signals
`TestHttpFSAccessControlled` directly verifies `httpfs.access.mode` semantics. `BaseTestHttpFSWith` writes `httpfs-site.xml` with proxy-user and signature-secret overrides and runs the full operation matrix through the server.
