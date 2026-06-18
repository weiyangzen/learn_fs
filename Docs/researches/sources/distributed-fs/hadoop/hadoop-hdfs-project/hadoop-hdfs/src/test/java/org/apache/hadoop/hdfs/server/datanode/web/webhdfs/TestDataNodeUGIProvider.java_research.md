# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/TestDataNodeUGIProvider.java

## Purpose

`TestDataNodeUGIProvider` verifies WebHDFS DataNode-side `UserGroupInformation` construction and cache behavior for secure token-based requests and insecure user-parameter requests. It also checks the secure no-token path delegates to non-token UGI construction.

## Important APIs and types

- `DataNodeUGIProvider.init`, `ugi`, `clearCache`, `ugiCache`, and `nonTokenUGI` are under test.
- `ParameterParser` reads query parameters from Netty `QueryStringDecoder`.
- `DelegationTokenIdentifier`, `DelegationTokenSecretManager`, and `Token` synthesize WebHDFS delegation tokens.
- `SecurityUtil`, `UserGroupInformation`, and `WebHdfsFileSystem` configure secure or insecure identity context.
- `DFS_WEBHDFS_UGI_EXPIRE_AFTER_ACCESS_KEY` controls cache expiry.

## Control flow

Setup creates WebHDFS test configuration, sets cache expiry to five seconds, and initializes the provider. The secure-cache test enables Kerberos, creates a proxy login user, obtains a WebHDFS filesystem and two delegation tokens, builds two `OPEN` URIs that differ only by delegation token, and verifies repeated `ugi()` calls for the same token return equal UGI objects while different tokens produce distinct UGIs. It then clears one provider cache reference, waits for global cache expiration without touching entries, and verifies new calls produce different UGIs.

The insecure-cache test builds two URIs with different `user.name` values, verifies same-user cache hits and different-user cache separation, waits for expiry, and verifies new UGI instances are returned. The secure-null-token test enables Kerberos but supplies user parameters rather than a delegation token, spies the provider, invokes `ugi`, and verifies `nonTokenUGI` is called with parsed username, doAs user, and resolved remote user.

## State and persistence behavior

State is in the static UGI cache, global UGI security configuration, login user, and in-memory delegation token secret manager threads. The test intentionally waits for cache expiration and calls Guava-style `cleanUp` to avoid refreshing access times.

## Dependencies and integration points

It integrates DataNode WebHDFS parameter parsing, secure delegation-token identity, insecure pseudo-auth identity, UGI cache expiry, token service assignment, and default web user fallback logic.

## Risks and edge cases

- Security and login user configuration are global JVM state and may affect neighboring tests if not isolated by the harness.
- The token secret manager is started but not explicitly stopped in this file.
- Equality of UGI objects is used as the cache signal; object identity is not directly asserted.
- Expiration waits are time-based and can slow test execution.

## Test signals

Strong signals are token-keyed cache hits, token separation, user-keyed insecure cache hits, user separation, expiry-driven cache misses, explicit cache cleanup, and verification that secure no-token requests use the non-token UGI path.
