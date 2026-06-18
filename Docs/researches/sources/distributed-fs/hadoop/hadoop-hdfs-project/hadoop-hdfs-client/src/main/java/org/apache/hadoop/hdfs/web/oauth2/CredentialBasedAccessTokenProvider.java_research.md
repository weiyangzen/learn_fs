# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/CredentialBasedAccessTokenProvider.java

## Purpose

`CredentialBasedAccessTokenProvider` implements the OAuth2 client-credentials token flow for providers that can supply a client secret/credential.

## Important APIs, Types, And Functions

It defines `dfs.webhdfs.oauth2.credential`, stores timer, client ID, refresh URL, access token, and `initialCredentialObtained`, declares abstract `getCredential`, overrides `setConf`, synchronized `getAccessToken`, and package-visible `refresh`.

## Control Flow

`getAccessToken` refreshes if the token is near expiry or no token has been obtained. `refresh` posts `client_secret`, `grant_type=client_credentials`, and `client_id` to the configured token endpoint, requires HTTP 200, parses `expires_in`, and stores `access_token`.

## State And Persistence

OAuth token and timer are in memory only. The credential comes from subclasses.

## Dependencies And Integration Points

`ConfCredentialBasedAccessTokenProvider` supplies the credential. `OAuth2ConnectionConfigurator` calls this through the `AccessTokenProvider` base. Apache HttpClient performs token endpoint calls.

## Risks

Refresh failures are wrapped as `IOException`, losing some endpoint-specific structure. Missing or malformed JSON fields throw during refresh. Token endpoint timeout is fixed to the default socket timeout.

## Test Signals

Tests should verify first-call refresh, expiry refresh, credential inclusion, error wrapping, malformed endpoint responses, and thread synchronization.
