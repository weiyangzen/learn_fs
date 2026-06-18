# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/TestDatanodeHttpServer.java

## Purpose

`TestDatanodeHttpServer` verifies that `DatanodeHttpServer` honors the configured HDFS HTTP policy by enabling HTTP, HTTPS, or both endpoints and leaving disabled endpoint addresses null.

## Important APIs and types

- JUnit parameterized class runs the same test for `HttpConfig.Policy.HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`.
- `KeyStoreTestUtil` creates temporary SSL configuration and keystores.
- `URLConnectionFactory` opens HTTP or HTTPS URLs with the generated SSL client configuration.
- `DatanodeHttpServer.start`, `getHttpAddress`, `getHttpsAddress`, and `close` are the direct server lifecycle APIs.

## Control flow

`@BeforeAll` creates a temp base directory, generates SSL config, creates a URL connection factory, and points DFS client/server keystore resource keys at the generated files. The parameterized test sets the HTTP policy and both DataNode HTTP/HTTPS bind addresses to `localhost:0`, starts a `DatanodeHttpServer`, and checks access for enabled schemes. `canAccess` opens the root URL, expects HTTP 200, reads the response, and requires the admin page text `Hadoop Administration`. Disabled schemes are expected to have null server addresses.

## State and persistence behavior

The test writes temporary keystores and SSL XML resources under a generated test path and cleans them in `@AfterAll`. Server sockets bind to ephemeral local ports. No DataNode dataset is required because the server is constructed with null DataNode dependencies for this policy check.

## Dependencies and integration points

It connects Hadoop HTTP policy configuration, SSL resource generation, DataNode HTTP server endpoint creation, URL connection behavior, and the common admin web UI response.

## Risks and edge cases

- `canAccess` catches all exceptions and returns false, so failure diagnostics are collapsed.
- The page-content assertion depends on the admin page text.
- It does not test WebHDFS endpoints, authentication filters, or TLS certificate details.
- Static configuration is shared across parameterized instances, so mutations must remain policy-local.

## Test signals

Strong signals are all three policy modes, real socket binding, real HTTP/HTTPS requests through Hadoop SSL config, null checks for disabled endpoints, and response-code plus admin-page validation for enabled endpoints.
