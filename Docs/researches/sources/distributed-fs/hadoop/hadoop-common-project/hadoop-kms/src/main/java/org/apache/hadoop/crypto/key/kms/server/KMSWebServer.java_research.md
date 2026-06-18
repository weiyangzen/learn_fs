# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebServer.java

## Purpose
`KMSWebServer.java` builds and runs the Hadoop `HttpServer2` instance that hosts the KMS web application.

## Important APIs, Types, and Functions
The constructor configures HTTP/HTTPS endpoint, admin ACL, SSL config, auth filter prefix, deprecated environment-variable overrides, metrics identity, and JVM pause monitoring. Lifecycle methods are `start`, `isRunning`, `join`, `stop`, and `getKMSUrl`. `main` validates required system properties and runs the daemon.

## Control Flow
Construction maps deprecated `KMS_*` environment variables into configuration with warnings, chooses scheme from SSL enablement, initializes `JvmPauseMonitor`, removes generic Hadoop auth/proxy filter initializers to avoid duplication, and builds `HttpServer2`. `start` starts HTTP, initializes the default metrics system and JVM metrics, and starts pause monitoring. `stop` reverses these resources.

## State and Persistence
State is the running HTTP server, scheme, metrics process/session identifiers, and pause monitor. It writes no persistent data.

## Dependencies and Integration Points
It depends on Hadoop `HttpServer2`, metrics2, `SSLFactory`, admin `AccessControlList`, `KMSAuthenticationFilter`, and `KMSConfiguration`. Shell scripts launch this class with required system properties.

## Risks
Environment variables still override configuration even though deprecated, which can surprise deployments. The constructor receives `sslConf`; non-SSL embedded paths may pass null, so behavior depends on `HttpServer2.Builder` tolerance. Removing filter initializers relies on exact class names.

## Test Signals
Tests should verify endpoint URL construction, SSL and non-SSL startup, deprecated env override precedence, filter initializer pruning, admin ACL propagation, metrics/pause monitor lifecycle, and `main` property validation.
