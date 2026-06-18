# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenProvider.java

## Purpose

`AccessTokenProvider` is the base SPI for supplying OAuth2 bearer tokens to WebHDFS HTTP connections.

## Important APIs, Types, And Functions

It implements Hadoop `Configurable`, stores `Configuration`, and declares abstract `getAccessToken()`.

## Control Flow

Connection configurators call `getAccessToken` for each connection. Subclasses own caching and refresh behavior.

## State And Persistence

Only the Hadoop configuration reference is stored. No token state is held in the base class.

## Dependencies And Integration Points

`OAuth2ConnectionConfigurator` instantiates subclasses by configuration and calls `setConf`. Implementations use WebHDFS OAuth configuration keys.

## Risks

Implementations must be performant and thread-safe because tokens are requested per connection. Misconfigured providers fail during reflection or first token request.

## Test Signals

Tests should cover configuration injection, subclass selection, exception propagation, and repeated connection calls.
