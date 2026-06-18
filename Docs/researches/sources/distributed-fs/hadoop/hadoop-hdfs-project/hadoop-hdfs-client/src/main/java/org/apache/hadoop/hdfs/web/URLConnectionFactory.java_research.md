# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/URLConnectionFactory.java

## Purpose

`URLConnectionFactory` constructs and configures URL connections for WebHDFS clients, including timeouts, SSL, OAuth2, and optional SPNEGO authentication.

## Important APIs, Types, And Functions

Key APIs are `DEFAULT_SOCKET_TIMEOUT`, `DEFAULT_SYSTEM_CONNECTION_FACTORY`, `newDefaultURLConnectionFactory`, `newOAuth2URLConnectionFactory`, `openConnection(URL)`, `openConnection(URL, boolean isSpnego)`, private `getSSLConnectionConfiguration`, `setTimeouts`, and `destroy`.

## Control Flow

Factory methods attempt to create `SSLConnectionConfigurator`; default factories fall back to timeout-only configuration on SSL setup failure, while OAuth factory treats setup failure as fatal. `openConnection` either opens a plain URL and applies the configurator or opens an `AuthenticatedURL` with `KerberosUgiAuthenticator` after refreshing the current user's TGT.

## State And Persistence

The factory stores one `ConnectionConfigurator`. No persistent state exists. `destroy` tears down the SSL configurator if the direct configurator is an `SSLConnectionConfigurator`.

## Dependencies And Integration Points

It integrates with WebHDFS initialization, OAuth2 connection configuration, SSL factory setup, Hadoop UGI, `AuthenticatedURL`, and Kerberos fallback auth.

## Risks

The OAuth path requires SSL configurator construction and wraps all failures as `IOException`. `destroy` does not reach an SSL configurator nested inside `OAuth2ConnectionConfigurator`, so lifecycle coverage differs by mode. Returning null from the unreachable `AuthenticationException` path in `openConnection(URL)` would be hazardous if assumptions change.

## Test Signals

Tests should cover default timeout-only fallback, SSL configuration success, OAuth factory failure, SPNEGO open path with TGT refresh, non-HTTP URL behavior, and destroy lifecycle.
