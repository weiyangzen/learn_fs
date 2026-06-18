# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SSLConnectionConfigurator.java

## Purpose

`SSLConnectionConfigurator` applies Hadoop SSL client configuration to HTTP connections and sets socket timeouts.

## Important APIs, Types, And Functions

It implements `ConnectionConfigurator`. The constructor builds and initializes an `SSLFactory`, obtains `SSLSocketFactory` and `HostnameVerifier`, and stores connect/read timeouts. `configure` applies SSL pieces to `HttpsURLConnection` and always sets timeouts. `destroy` releases the `SSLFactory`.

## Control Flow

Factories are initialized once at construction. Each connection configuration checks whether the connection is HTTPS; if so, it installs the SSL socket factory and hostname verifier before setting timeout values.

## State And Persistence

State is in-memory SSL factory material plus immutable timeout values. No persistence exists, though SSLFactory may read keystores/truststores from configuration.

## Dependencies And Integration Points

`URLConnectionFactory` uses this for normal and OAuth WebHDFS connection factories. It depends on Hadoop `SSLFactory`, Java `HttpsURLConnection`, and authentication client `ConnectionConfigurator`.

## Risks

Constructor failures force callers to fall back or fail depending on path. Forgetting `destroy` can leak SSLFactory resources. HTTP URLs still receive timeouts but no TLS protection, so callers must enforce scheme policy where required.

## Test Signals

Tests should verify configured HTTPS socket factory/hostname verifier, timeout propagation for HTTP and HTTPS, failure fallback in `URLConnectionFactory`, and `destroy` invocation.
