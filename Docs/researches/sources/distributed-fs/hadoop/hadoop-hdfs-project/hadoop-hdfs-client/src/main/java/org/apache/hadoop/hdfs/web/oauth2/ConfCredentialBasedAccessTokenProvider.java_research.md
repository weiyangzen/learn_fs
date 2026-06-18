# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfCredentialBasedAccessTokenProvider.java

## Purpose

`ConfCredentialBasedAccessTokenProvider` supplies the client credential for the OAuth2 client-credentials grant from Hadoop configuration.

## Important APIs, Types, And Functions

It extends `CredentialBasedAccessTokenProvider`, stores `credential`, overrides `setConf`, and implements `getCredential`.

## Control Flow

`setConf` initializes common OAuth config in the superclass, then requires `dfs.webhdfs.oauth2.credential`. Token refresh is inherited; when a token is needed, superclass calls `getCredential`.

## State And Persistence

State is the configured credential string and inherited access-token/timer state. No durable persistence exists.

## Dependencies And Integration Points

It is the default OAuth token provider selected by `OAuth2ConnectionConfigurator` when a provider class is not explicitly set.

## Risks

Credentials live in configuration and memory. `getCredential` throws if called before proper configuration. Missing config keys fail at initialization.

## Test Signals

Tests should cover configured credential, missing credential, superclass config requirements, and token refresh body content.
