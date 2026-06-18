# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfRefreshTokenBasedAccessTokenProvider.java

## Purpose

`ConfRefreshTokenBasedAccessTokenProvider` obtains WebHDFS OAuth2 access tokens from a configured refresh token using the authorization-code refresh-token flow.

## Important APIs, Types, And Functions

It defines config keys `dfs.webhdfs.oauth2.refresh.token` and `dfs.webhdfs.oauth2.refresh.token.expires.ms.since.epoch`. Important methods are constructors, `setConf`, synchronized `getAccessToken`, package-visible `refresh`, and `getRefreshToken`.

## Control Flow

`setConf` loads refresh token, expiry epoch, client ID, and refresh URL. `getAccessToken` refreshes when the timer says the token is expired or near expiry. `refresh` posts URL-encoded `grant_type=refresh_token`, refresh token, and client ID, requires HTTP 200, parses JSON `expires_in` and `access_token`, and updates timer/token.

## State And Persistence

State is in-memory access token, refresh token, client ID, refresh URL, and timer. No refreshed token is written back to configuration.

## Dependencies And Integration Points

It uses Apache HttpClient, `JsonSerialization`, OAuth constants, `URLConnectionFactory.DEFAULT_SOCKET_TIMEOUT`, and WebHDFS OAuth config keys.

## Risks

The initial access token is null until the first successful refresh, so bad expiry config can produce immediate network failure. Response entity is converted to string multiple times in error/success paths. Secrets remain in memory and may appear in test/log diagnostics if not careful.

## Test Signals

Tests should mock token endpoint success/failure, missing config, expiry-triggered refresh, JSON parse failures, non-200 responses, and synchronized concurrent calls.
