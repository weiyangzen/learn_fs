# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2ConnectionConfigurator.java

## Purpose

`OAuth2ConnectionConfigurator` applies OAuth2 bearer-token authentication to WebHDFS HTTP connections, optionally after SSL configuration.

## Important APIs, Types, And Functions

Important members are `HEADER = "Bearer "`, `AccessTokenProvider accessTokenProvider`, optional `ConnectionConfigurator sslConfigurator`, constructors, and `configure`.

## Control Flow

Construction requires the access-token-provider config key, resolves the provider class with `conf.getClass`, instantiates it with `ReflectionUtils`, and calls `setConf`. `configure` first delegates to SSL if present, then requests an access token and sets request property `AUTHORIZATION` to `Bearer <token>`.

## State And Persistence

It stores provider and optional SSL configurator. Token state lives in the provider. No persistence exists.

## Dependencies And Integration Points

Created by `URLConnectionFactory.newOAuth2URLConnectionFactory` and used for all OAuth-enabled WebHDFS connections.

## Risks

Header name casing is literal `AUTHORIZATION`; HTTP is case-insensitive, but tests/proxies may expect `Authorization`. Provider reflection/config failures occur at construction. SSL configurator lifecycle is not exposed through this class.

## Test Signals

Tests should verify provider selection, missing config failures, Authorization header content, SSL delegation order, and exception propagation from provider refresh.
